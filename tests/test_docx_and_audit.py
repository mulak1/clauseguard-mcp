"""Unit and integration tests for contract auditing and OpenXML Word Track Changes (.docx)."""

from __future__ import annotations

import base64
import io
import zipfile
import xml.etree.ElementTree as ET
import pytest
from pydantic import ValidationError

from clauseguard_mcp.models import AuditContractRequest, PlaybookType
from clauseguard_mcp.audit_engine import audit_and_redline_contract
from clauseguard_mcp.docx_engine import (
    create_sample_docx_bytes,
    extract_text_from_docx_bytes,
    generate_redlined_docx_bytes,
)


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def test_audit_predatory_msa_identifies_high_risk_clauses_and_track_changes() -> None:
    """As a founder, I want predatory MSA clauses flagged and redlined in a native .docx."""
    contract_text = (
        "1. LIMITATION OF LIABILITY. Customer's liability shall be uncapped and unlimited "
        "for any and all claims arising under this Agreement.\n\n"
        "2. INDEMNIFICATION. Customer shall indemnify, defend, and hold harmless Vendor "
        "from any and all claims unilaterally without reciprocal obligation.\n\n"
        "3. TERM AND RENEWAL. This Agreement shall automatically renew for successive "
        "3-year terms unless Customer provides written notice at least 120 days prior.\n\n"
        "4. INTELLECTUAL PROPERTY. Customer hereby irrevocably assigns all right, title, "
        "and interest in all Customer pre-existing IP and background technology to Vendor.\n\n"
        "5. NON-SOLICITATION. Customer shall not solicit or hire any employee or former "
        "contractor of Vendor anywhere in the world for a period of 5 years."
    )
    req = AuditContractRequest(
        contract_text=contract_text,
        playbook=PlaybookType.FOUNDER_FRIENDLY,
        contract_name="Predatory_Enterprise_MSA.docx",
        author="ClauseGuard Legal AI",
    )
    res = audit_and_redline_contract(req)

    assert res.risk_score >= 70
    assert res.risk_level in ("HIGH", "CRITICAL")
    assert len(res.findings) >= 5

    categories = {f.category for f in res.findings}
    assert "uncapped_liability" in categories
    assert "unilateral_indemnification" in categories
    assert "sneaky_auto_renewal" in categories
    assert "broad_ip_assignment" in categories
    assert "non_solicit_overreach" in categories

    # Validate the generated .docx is a real ZIP archive with native Word Track Changes
    raw_docx = base64.b64decode(res.redlined_docx_b64)
    with zipfile.ZipFile(io.BytesIO(raw_docx), "r") as zf:
        names = set(zf.namelist())
        assert "[Content_Types].xml" in names
        assert "word/document.xml" in names
        assert "word/settings.xml" in names

        doc_xml = zf.read("word/document.xml").decode("utf-8")
        settings_xml = zf.read("word/settings.xml").decode("utf-8")

        assert "<w:del " in doc_xml
        assert "<w:delText" in doc_xml
        assert "<w:ins " in doc_xml
        assert "trackRevisions" in settings_xml

        # Parse XML to ensure well-formedness
        root = ET.fromstring(doc_xml)
        dels = root.findall(f".//{{{W_NS}}}del")
        ins_nodes = root.findall(f".//{{{W_NS}}}ins")
        assert len(dels) >= 5
        assert len(ins_nodes) >= 5


def test_audit_gdpr_dpa_and_hipaa_playbooks() -> None:
    """As a DPO, I want GDPR DPA and HIPAA BAA missing subprocessor/breach clauses flagged."""
    dpa_text = (
        "DATA PROCESSING ADDENDUM\n"
        "Processor may engage any new subprocessors without prior notice or consent from Controller.\n"
        "In the event of a Personal Data Breach, Processor shall notify Controller within 30 days."
    )
    gdpr_res = audit_and_redline_contract(
        AuditContractRequest(
            contract_text=dpa_text,
            playbook=PlaybookType.GDPR_DPA,
            contract_name="Vendor_DPA.docx",
        )
    )
    assert gdpr_res.risk_score >= 35
    cats = {f.category for f in gdpr_res.findings}
    assert "missing_gdpr_subprocessor_notice" in cats or "delayed_breach_notification" in cats

    hipaa_text = (
        "BUSINESS ASSOCIATE AGREEMENT\n"
        "Business Associate liability shall be uncapped. Business Associate may use PHI without "
        "subprocessor flow-down restrictions and report breaches within 90 days."
    )
    hipaa_res = audit_and_redline_contract(
        AuditContractRequest(
            contract_text=hipaa_text,
            playbook=PlaybookType.HIPAA_BAA,
            contract_name="HIPAA_BAA.docx",
        )
    )
    assert hipaa_res.risk_score >= 35
    assert len(hipaa_res.findings) >= 2


def test_audit_accepts_base64_docx_payload() -> None:
    """As a user, I can upload a base64 .docx file directly to audit_and_redline_contract."""
    sample_bytes = create_sample_docx_bytes(
        [
            "MASTER SAAS AGREEMENT",
            "Customer liability shall be uncapped and unlimited for all damages.",
            "This Agreement shall automatically renew for 2-year periods unless given 90 days notice.",
        ]
    )
    extracted = extract_text_from_docx_bytes(sample_bytes)
    assert "uncapped and unlimited" in extracted

    b64_payload = base64.b64encode(sample_bytes).decode("ascii")
    res = audit_and_redline_contract(
        AuditContractRequest(
            docx_base64=b64_payload,
            playbook=PlaybookType.SAAS_VENDOR,
            contract_name="Uploaded_MSA.docx",
        )
    )
    assert res.risk_score > 0
    assert len(res.findings) >= 2
    assert res.doc_id.startswith("doc_")


def test_clean_contract_returns_low_risk_score() -> None:
    """As a reviewer, a balanced mutual contract should receive a low risk score."""
    clean_text = (
        "1. MUTUAL CONFIDENTIALITY. Each party agrees to protect the other party's Confidential "
        "Information using reasonable care for a period of three (3) years.\n"
        "2. MUTUAL LIMITATION OF LIABILITY. Neither party's aggregate liability shall exceed "
        "twelve (12) months of fees paid preceding the claim."
    )
    res = audit_and_redline_contract(
        AuditContractRequest(
            contract_text=clean_text,
            playbook=PlaybookType.FOUNDER_FRIENDLY,
        )
    )
    assert res.risk_score <= 20
    assert res.risk_level == "LOW"
    assert len(res.findings) == 0


def test_audit_rejects_empty_or_invalid_inputs() -> None:
    """Boundary validation rejects empty text/docx or invalid base64."""
    with pytest.raises(ValidationError):
        AuditContractRequest(contract_text="   ", docx_base64=None)

    with pytest.raises(ValueError, match="Invalid .docx"):
        extract_text_from_docx_bytes(b"not-a-valid-zip-file")
