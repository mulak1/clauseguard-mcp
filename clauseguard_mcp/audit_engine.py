"""Contract review & redline engine producing Risk Scores, Missing Clause Checks, and Word Track Changes."""

from __future__ import annotations

import base64
import re
from typing import Literal

from clauseguard_mcp.docx_engine import (
    extract_text_from_b64_docx,
    generate_redlined_docx_bytes,
    store_docx_artifact,
)
from clauseguard_mcp.models import (
    AuditContractRequest,
    AuditContractResponse,
    CustomDocxRequest,
    MissingClauseWarning,
    PlaybookType,
    RedlineFinding,
)
from clauseguard_mcp.playbooks import CLAUSE_RULES, PLAYBOOK_LABELS, ClauseRule


def audit_and_redline_contract(request: AuditContractRequest) -> AuditContractResponse:
    """Review agreement text or base64 .docx against the chosen playbook and emit a Track Changes .docx."""
    source_text = _resolve_contract_text(request)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\r\n\s*\r\n", source_text) if p.strip()]
    if len(paragraphs) <= 1:
        paragraphs = [p.strip() for p in source_text.splitlines() if p.strip()]

    findings = _evaluate_clauses(paragraphs, source_text, request.playbook)
    missing_clauses = _detect_missing_protections(source_text, request.playbook)
    risk_score = _compute_risk_score(findings, request.playbook)
    risk_level = _classify_risk_level(risk_score)
    playbook_label = PLAYBOOK_LABELS.get(request.playbook, "Balanced Commercial Standard")

    docx_bytes = generate_redlined_docx_bytes(
        contract_name=request.contract_name,
        playbook=request.playbook,
        risk_score=risk_score,
        risk_level=risk_level,
        paragraphs=paragraphs,
        findings=findings,
        author=request.author,
    )
    doc_id = store_docx_artifact(request.contract_name, docx_bytes)
    docx_b64 = base64.b64encode(docx_bytes).decode("ascii")

    summary = _build_executive_summary(
        request.contract_name,
        playbook_label,
        risk_score,
        risk_level,
        findings,
    )
    sign_off = _build_sign_off_recommendation(risk_level, findings)
    email_draft = _build_counterparty_email(request.contract_name, findings)

    return AuditContractResponse(
        doc_id=doc_id,
        contract_name=request.contract_name,
        playbook=request.playbook,
        playbook_label=playbook_label,
        risk_score=risk_score,
        risk_level=risk_level,
        sign_off_recommendation=sign_off,
        executive_summary=summary,
        counterparty_email_draft=email_draft,
        findings=findings,
        missing_clauses=missing_clauses,
        redlined_docx_b64=docx_b64,
        download_url=f"/api/docx/{doc_id}",
        track_changes_summary={
            "format": "Microsoft Word (.docx) with Track Changes",
            "track_revisions_enabled": True,
            "w_del_count": len(findings),
            "w_ins_count": len(findings),
            "author": request.author,
        },
    )


def build_custom_redlined_docx(request: CustomDocxRequest) -> dict[str, str | int]:
    """Generate a custom .docx containing only the user's accepted and edited redlines."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\r\n\s*\r\n", request.contract_text) if p.strip()]
    if len(paragraphs) <= 1:
        paragraphs = [p.strip() for p in request.contract_text.splitlines() if p.strip()]

    custom_findings = tuple(
        RedlineFinding(
            clause_id=item.clause_id,
            category="custom",
            title=item.title,
            plain_english_summary=item.title,
            severity=item.severity,
            risk_points=15,
            original_excerpt=item.original_excerpt,
            proposed_redline=item.replacement_text,
            compromise_redline=item.replacement_text,
            rationale=item.rationale or "Custom reviewer revision.",
            counterparty_note="",
            playbook_reference=item.playbook_reference,
        )
        for item in request.accepted_redlines
    )

    docx_bytes = generate_redlined_docx_bytes(
        contract_name=request.contract_name,
        playbook=request.playbook,
        risk_score=request.risk_score,
        risk_level=request.risk_level,
        paragraphs=paragraphs,
        findings=custom_findings,
        author=request.author,
    )
    doc_id = store_docx_artifact(request.contract_name, docx_bytes)
    return {
        "doc_id": doc_id,
        "download_url": f"/api/docx/{doc_id}",
        "accepted_count": len(custom_findings),
    }


def _resolve_contract_text(request: AuditContractRequest) -> str:
    if request.contract_text and request.contract_text.strip():
        return request.contract_text.strip()
    if request.docx_base64 and request.docx_base64.strip():
        extracted = extract_text_from_b64_docx(request.docx_base64.strip())
        if not extracted.strip():
            raise ValueError("The uploaded Word document contained no readable text.")
        return extracted
    raise ValueError("No agreement text or Word file available.")


def _evaluate_clauses(
    paragraphs: list[str],
    full_text: str,
    playbook: PlaybookType,
) -> tuple[RedlineFinding, ...]:
    findings: list[RedlineFinding] = []
    idx = 1
    for rule in CLAUSE_RULES:
        matched_excerpt = _find_rule_match(paragraphs, full_text, rule)
        if matched_excerpt is not None:
            points = _adjusted_points(rule, playbook)
            findings.append(
                RedlineFinding(
                    clause_id=f"CL-{idx:02d}",
                    category=rule.category,
                    title=rule.title,
                    plain_english_summary=rule.plain_summary,
                    severity=rule.severity,
                    risk_points=points,
                    original_excerpt=matched_excerpt,
                    proposed_redline=rule.replacements[playbook],
                    compromise_redline=rule.compromise,
                    rationale=rule.rationale,
                    counterparty_note=rule.counterparty_note,
                    playbook_reference=rule.playbook_ref,
                )
            )
            idx += 1
    return tuple(findings)


def _detect_missing_protections(
    full_text: str,
    playbook: PlaybookType,
) -> tuple[MissingClauseWarning, ...]:
    lower = full_text.lower()
    warnings: list[MissingClauseWarning] = []

    if "terminate for material breach" not in lower and "termination for cause" not in lower and "cure period" not in lower:
        warnings.append(
            MissingClauseWarning(
                clause_name="Right to Terminate for Uncured Breach",
                importance="ESSENTIAL",
                why_it_matters="Without a termination-for-cause clause, you cannot exit the contract early even if the other side stops performing.",
                suggested_language="TERMINATION FOR CAUSE. Either party may terminate this Agreement upon thirty (30) days written notice if the other party materially breaches its obligations and fails to cure such breach within the notice period.",
            )
        )

    if playbook in (PlaybookType.GDPR_DPA, PlaybookType.HIPAA_BAA) and "return or delete" not in lower and "destroy" not in lower:
        warnings.append(
            MissingClauseWarning(
                clause_name="Data Return or Deletion Upon Termination",
                importance="ESSENTIAL",
                why_it_matters="Privacy laws require vendors to delete or return all customer records when the contract ends.",
                suggested_language="RETURN OR DELETION OF DATA. Within thirty (30) days after termination of this Agreement, Provider shall securely delete or return all Customer Data and certify deletion in writing.",
            )
        )

    if "force majeure" not in lower and len(full_text) > 350:
        warnings.append(
            MissingClauseWarning(
                clause_name="Mutual Force Majeure Protection",
                importance="RECOMMENDED",
                why_it_matters="Protects both sides if extraordinary events outside their control temporarily prevent performance.",
                suggested_language="FORCE MAJEURE. Neither party shall be liable for delays caused by events beyond its reasonable control, provided the affected party gives prompt notice and uses reasonable efforts to resume performance.",
            )
        )

    return tuple(warnings)


def _find_rule_match(paragraphs: list[str], full_text: str, rule: ClauseRule) -> str | None:
    for para in paragraphs:
        for pat in rule.patterns:
            if re.search(pat, para, flags=re.IGNORECASE):
                return para
    for pat in rule.patterns:
        match = re.search(pat, full_text, flags=re.IGNORECASE)
        if match:
            start = max(0, match.start() - 40)
            end = min(len(full_text), match.end() + 80)
            return full_text[start:end].strip()
    return None


def _adjusted_points(rule: ClauseRule, playbook: PlaybookType) -> int:
    if playbook in (PlaybookType.GDPR_DPA, PlaybookType.HIPAA_BAA) and rule.category in (
        "missing_gdpr_subprocessor_notice",
        "delayed_breach_notification",
    ):
        return rule.base_points + 6
    return rule.base_points


def _compute_risk_score(findings: tuple[RedlineFinding, ...], playbook: PlaybookType) -> int:
    if not findings:
        return 8 if playbook == PlaybookType.FOUNDER_FRIENDLY else 10
    total = sum(f.risk_points for f in findings)
    return min(100, max(15, total))


def _classify_risk_level(score: int) -> Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]:
    if score >= 75:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MODERATE"
    return "LOW"


def _build_sign_off_recommendation(
    risk_level: str,
    findings: tuple[RedlineFinding, ...],
) -> str:
    if not findings:
        return "Ready to sign — terms are balanced and match standard commercial expectations."
    crit_count = sum(1 for f in findings if f.severity in ("CRITICAL", "HIGH"))
    if crit_count > 0:
        return f"Do not sign as-is — {crit_count} high-impact clause(s) should be revised before signature."
    return "Negotiate minor commercial adjustments before signing."


def _build_executive_summary(
    contract_name: str,
    playbook_label: str,
    risk_score: int,
    risk_level: str,
    findings: tuple[RedlineFinding, ...],
) -> str:
    if not findings:
        return (
            f"We reviewed {contract_name} against the {playbook_label}. "
            f"The agreement carries a low risk score ({risk_score}/100) with no unusual terms requiring revision."
        )
    titles = ", ".join(f.title for f in findings[:3])
    more = f" and {len(findings) - 3} more" if len(findings) > 3 else ""
    return (
        f"We reviewed {contract_name} against the {playbook_label}. "
        f"We flagged {len(findings)} clause(s) outside standard commercial practice — {titles}{more} — "
        "and prepared a clean Word document with Track Changes ready for review."
    )


def _build_counterparty_email(
    contract_name: str,
    findings: tuple[RedlineFinding, ...],
) -> str:
    if not findings:
        return (
            f"Hi team,\n\nThank you for sending over {contract_name}. We completed our review and "
            "have no requested revisions—we are ready to proceed to signature.\n\nBest regards,"
        )
    bullets = "\n".join(f"• {f.title}: {f.counterparty_note}" for f in findings)
    return (
        f"Hi team,\n\nThank you for sharing {contract_name}. We reviewed the draft and attached a "
        "Word version with a few standard, balanced revisions in Track Changes so we can move "
        "quickly toward signature:\n\n"
        f"{bullets}\n\n"
        "Please let us know if these adjustments work on your end or if a quick call would be helpful.\n\n"
        "Best regards,"
    )
