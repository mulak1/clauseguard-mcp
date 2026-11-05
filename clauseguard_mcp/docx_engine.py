"""Pure-Python OpenXML (.docx) parser and native Word Track Changes (<w:del>/<w:ins>) generator."""

from __future__ import annotations

import base64
from datetime import datetime, timezone
import io
import re
import uuid
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET
import zipfile

from clauseguard_mcp.models import PlaybookType, RedlineFinding


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# In-memory store mapping doc_id -> (filename, docx_bytes) and sanitized filename -> (filename, docx_bytes)
_DOCX_STORE: dict[str, tuple[str, bytes]] = {}
_FILENAME_STORE: dict[str, tuple[str, bytes]] = {}


def sanitize_docx_filename(filename: str) -> str:
    """Return a URL-safe .docx filename."""
    clean = re.sub(r"[^A-Za-z0-9._-]", "_", (filename or "Contract_Redlined.docx").strip())
    if not clean.lower().endswith(".docx"):
        clean = f"{clean}.docx"
    return clean


def store_docx_artifact(filename: str, docx_bytes: bytes) -> str:
    """Store generated .docx bytes and return an immutable doc_id."""
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    safe_name = sanitize_docx_filename(filename)
    _DOCX_STORE[doc_id] = (safe_name, docx_bytes)
    if len(_DOCX_STORE) > 60:
        oldest_doc = next(iter(_DOCX_STORE))
        _DOCX_STORE.pop(oldest_doc, None)
    _FILENAME_STORE[safe_name] = (safe_name, docx_bytes)
    _FILENAME_STORE[f"{doc_id}_{safe_name}"] = (safe_name, docx_bytes)
    if len(_FILENAME_STORE) > 60:
        oldest_key = next(iter(_FILENAME_STORE))
        _FILENAME_STORE.pop(oldest_key, None)
    return doc_id


def get_docx_artifact(doc_id: str) -> tuple[str, bytes] | None:
    """Retrieve stored (filename, docx_bytes) by doc_id."""
    return _DOCX_STORE.get(doc_id)


def get_docx_by_filename(filename: str) -> tuple[str, bytes] | None:
    """Retrieve stored (filename, docx_bytes) by filename or doc_id."""
    if filename in _FILENAME_STORE:
        return _FILENAME_STORE[filename]
    safe = sanitize_docx_filename(filename)
    if safe in _FILENAME_STORE:
        return _FILENAME_STORE[safe]
    if filename in _DOCX_STORE:
        return _DOCX_STORE[filename]
    return None


def extract_text_from_docx_bytes(docx_bytes: bytes) -> str:
    """Extract paragraph text safely from a .docx ZIP payload."""
    if len(docx_bytes) > 5_000_000:
        raise ValueError("Invalid .docx payload: exceeds 5 MB size limit")
    try:
        with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as zf:
            if "word/document.xml" not in zf.namelist():
                raise ValueError("Invalid .docx archive: missing word/document.xml")
            info = zf.getinfo("word/document.xml")
            if info.file_size > 10_000_000:
                raise ValueError("Invalid .docx archive: uncompressed XML exceeds 10 MB limit")
            xml_bytes = zf.read("word/document.xml")
    except zipfile.BadZipFile as exc:
        raise ValueError("Invalid .docx payload: not a valid ZIP archive") from exc

    lower_xml = xml_bytes.lower()
    if b"<!doctype" in lower_xml or b"<!entity" in lower_xml:
        raise ValueError("Invalid .docx XML: external entities or DOCTYPE declarations are forbidden")

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError("Invalid .docx XML inside word/document.xml") from exc

    paragraphs: list[str] = []
    for p_elem in root.findall(f".//{{{W_NS}}}p"):
        texts = [t.text for t in p_elem.findall(f".//{{{W_NS}}}t") if t.text]
        joined = "".join(texts).strip()
        if joined:
            paragraphs.append(joined)
    return "\n\n".join(paragraphs)


def extract_text_from_b64_docx(docx_b64: str) -> str:
    """Decode base64 .docx string and extract text."""
    try:
        raw_bytes = base64.b64decode(docx_b64, validate=True)
    except Exception as exc:
        raise ValueError("Invalid base64 encoding for docx_base64") from exc
    return extract_text_from_docx_bytes(raw_bytes)


def create_sample_docx_bytes(paragraphs: list[str]) -> bytes:
    """Create a clean baseline OpenXML .docx binary from a list of paragraphs."""
    body_xml = "".join(
        f"<w:p><w:r><w:t xml:space=\"preserve\">{escape(p)}</w:t></w:r></w:p>"
        for p in paragraphs
    )
    return _package_openxml_zip(body_xml, track_revisions=False)


def generate_redlined_docx_bytes(
    contract_name: str,
    playbook: PlaybookType,
    risk_score: int,
    risk_level: str,
    paragraphs: list[str],
    findings: tuple[RedlineFinding, ...],
    author: str = "ClauseGuard MCP",
) -> bytes:
    """Generate a real Microsoft Word .docx containing native <w:del> and <w:ins> Track Changes."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    safe_author = escape(author)
    rev_id = 1

    xml_parts: list[str] = [
        _build_header_xml(contract_name, playbook.value, risk_score, risk_level, len(findings))
    ]

    used_findings: set[str] = set()
    for para in paragraphs:
        matched_finding = _match_finding_for_paragraph(para, findings, used_findings)
        if matched_finding is None:
            xml_parts.append(
                f'<w:p><w:r><w:t xml:space="preserve">{escape(para)}</w:t></w:r></w:p>'
            )
        else:
            used_findings.add(matched_finding.clause_id)
            del_id = rev_id
            ins_id = rev_id + 1
            rev_id += 2
            xml_parts.append(
                _build_tracked_change_paragraph(
                    original_text=para,
                    replacement_text=matched_finding.proposed_redline,
                    rationale=matched_finding.rationale,
                    severity=matched_finding.severity,
                    playbook_ref=matched_finding.playbook_reference,
                    author=safe_author,
                    timestamp=timestamp,
                    del_id=del_id,
                    ins_id=ins_id,
                )
            )

    # Append any remaining findings that matched across multi-line spans
    for finding in findings:
        if finding.clause_id not in used_findings:
            del_id = rev_id
            ins_id = rev_id + 1
            rev_id += 2
            xml_parts.append(
                _build_tracked_change_paragraph(
                    original_text=finding.original_excerpt,
                    replacement_text=finding.proposed_redline,
                    rationale=finding.rationale,
                    severity=finding.severity,
                    playbook_ref=finding.playbook_reference,
                    author=safe_author,
                    timestamp=timestamp,
                    del_id=del_id,
                    ins_id=ins_id,
                )
            )

    return _package_openxml_zip("".join(xml_parts), track_revisions=True)


def _match_finding_for_paragraph(
    para: str,
    findings: tuple[RedlineFinding, ...],
    used_findings: set[str],
) -> RedlineFinding | None:
    para_lower = para.lower()
    for finding in findings:
        if finding.clause_id in used_findings:
            continue
        excerpt_lower = finding.original_excerpt.lower()
        if excerpt_lower in para_lower or para_lower in excerpt_lower:
            return finding
    return None


def _build_header_xml(
    contract_name: str,
    playbook_name: str,
    risk_score: int,
    risk_level: str,
    finding_count: int,
) -> str:
    header_line = escape(
        f"CLAUSEGUARD MCP LEGAL AUDIT & REDLINE — {contract_name} | "
        f"Playbook: {playbook_name} | Risk Score: {risk_score}/100 ({risk_level}) | "
        f"Tracked Redlines: {finding_count}"
    )
    return (
        '<w:p><w:r><w:rPr><w:b/><w:color w:val="1E293B"/></w:rPr>'
        f'<w:t xml:space="preserve">{header_line}</w:t></w:r></w:p>'
    )


def _build_tracked_change_paragraph(
    *,
    original_text: str,
    replacement_text: str,
    rationale: str,
    severity: str,
    playbook_ref: str,
    author: str,
    timestamp: str,
    del_id: int,
    ins_id: int,
) -> str:
    note = f" [ClauseGuard {severity} Redline ({playbook_ref}): {rationale}]"
    return (
        "<w:p>"
        f'<w:del w:id="{del_id}" w:author="{author}" w:date="{timestamp}">'
        '<w:r><w:rPr><w:strike/><w:color w:val="DC2626"/></w:rPr>'
        f'<w:delText xml:space="preserve">{escape(original_text)}</w:delText>'
        "</w:r></w:del>"
        '<w:r><w:t xml:space="preserve"> </w:t></w:r>'
        f'<w:ins w:id="{ins_id}" w:author="{author}" w:date="{timestamp}">'
        '<w:r><w:rPr><w:b/><w:color w:val="15803D"/></w:rPr>'
        f'<w:t xml:space="preserve">{escape(replacement_text)}</w:t>'
        "</w:r></w:ins>"
        '<w:r><w:rPr><w:i/><w:color w:val="64748B"/></w:rPr>'
        f'<w:t xml:space="preserve">{escape(note)}</w:t></w:r>'
        "</w:p>"
    )


def _package_openxml_zip(body_paragraphs_xml: str, track_revisions: bool) -> bytes:
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/settings.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
        "</Types>"
    )
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        "</Relationships>"
    )
    doc_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rIdSettings" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" '
        'Target="settings.xml"/>'
        "</Relationships>"
    )
    track_tag = "<w:trackRevisions/>" if track_revisions else ""
    settings_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:settings xmlns:w="{W_NS}">{track_tag}</w:settings>'
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}">'
        f"<w:body>{body_paragraphs_xml}<w:sectPr/></w:body>"
        "</w:document>"
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", rels_xml)
        zf.writestr("word/_rels/document.xml.rels", doc_rels_xml)
        zf.writestr("word/settings.xml", settings_xml)
        zf.writestr("word/document.xml", document_xml)
    return buf.getvalue()
