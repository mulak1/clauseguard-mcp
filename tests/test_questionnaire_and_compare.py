"""Unit tests for vendor security questionnaire autofill and contract version comparison."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from clauseguard_mcp.models import (
    CompareVersionsRequest,
    QuestionnaireItem,
    QuestionnaireRequest,
    SecurityProfile,
)
from clauseguard_mcp.questionnaire_engine import (
    autofill_security_questionnaire,
    compare_contract_versions,
)


def test_autofill_security_questionnaire_populates_all_domains() -> None:
    """As a security lead, I want SOC2/GDPR/HIPAA/ISO27001/Encryption questions auto-answered."""
    items = [
        QuestionnaireItem(id="Q1", question="Do you maintain a current SOC 2 Type II report?"),
        QuestionnaireItem(
            id="Q2",
            question="How is customer data encrypted at rest and in transit (TLS/AES)?",
        ),
        QuestionnaireItem(
            id="Q3",
            question="Do you comply with GDPR Article 28 and maintain a list of subprocessors?",
        ),
        QuestionnaireItem(
            id="Q4",
            question="Are you certified under ISO/IEC 27001 and do you support HIPAA BAA?",
        ),
        QuestionnaireItem(
            id="Q5",
            question="What is your incident response SLA for notifying customers of a security breach?",
        ),
        QuestionnaireItem(
            id="Q6",
            question="Do you enforce multi-factor authentication (MFA), SSO/SAML, and RBAC?",
        ),
        QuestionnaireItem(
            id="Q7",
            question="What is your disaster recovery RPO/RTO and backup testing cadence?",
        ),
    ]
    req = QuestionnaireRequest(items=items)
    res = autofill_security_questionnaire(req)

    assert len(res.answers) == 7
    assert res.average_confidence >= 0.85
    for ans in res.answers:
        assert len(ans.answer) > 20
        assert len(ans.evidence_refs) >= 1
        assert 0.5 <= ans.confidence <= 1.0


def test_autofill_custom_profile_and_unrecognized_question() -> None:
    """Custom security profile values appear in answers and vague questions get calibrated confidence."""
    profile = SecurityProfile(
        company_name="AcmeCloud Inc.",
        soc2_status="SOC 2 Type II Certified (Deloitte, 2025)",
        encryption_at_rest="AES-256-GCM via AWS KMS HSM",
        encryption_in_transit="TLS 1.3 Strict",
        breach_notification_hours=24,
    )
    req = QuestionnaireRequest(
        items=[
            QuestionnaireItem(id="Q-ENC", question="Describe your encryption key management."),
            QuestionnaireItem(
                id="Q-MISC",
                question="What is your office cafeteria menu policy on Fridays?",
            ),
        ],
        profile=profile,
    )
    res = autofill_security_questionnaire(req)
    assert "AcmeCloud Inc." in res.answers[0].answer
    assert "AES-256-GCM" in res.answers[0].answer
    assert res.answers[0].confidence >= 0.90
    assert res.answers[1].confidence < 0.80
    assert res.answers[1].needs_human_review is True


def test_compare_contract_versions_detects_material_risk_shifts() -> None:
    """As legal counsel, I want material risk shifts between Draft v1 and Counterparty v2 flagged."""
    v1_text = (
        "1. LIMITATION OF LIABILITY. Neither party's aggregate liability shall exceed 12 months of fees.\n"
        "2. PAYMENT TERMS. Customer shall pay all undisputed invoices within Net 30 days.\n"
        "3. GOVERNING LAW. This Agreement shall be governed by the laws of the State of Delaware.\n"
        "4. RENEWAL. This Agreement renews upon mutual written agreement of both parties.\n"
        "5. INDEMNIFICATION. Each party shall mutually indemnify the other for third-party IP claims."
    )
    v2_text = (
        "1. LIMITATION OF LIABILITY. Customer's liability shall be uncapped and unlimited, whereas Vendor liability is capped at $1,000.\n"
        "2. PAYMENT TERMS. Customer shall pay all invoices within Net 90 days with no right of offset.\n"
        "3. GOVERNING LAW. This Agreement shall be governed by the laws of England and Wales in London.\n"
        "4. RENEWAL. This Agreement shall automatically renew for 3-year terms unless given 120 days notice.\n"
        "5. INDEMNIFICATION. Customer shall unilaterally indemnify Vendor for any claim whatsoever."
    )
    req = CompareVersionsRequest(
        version_a_text=v1_text,
        version_b_text=v2_text,
        version_a_name="v1_Founder_Draft.docx",
        version_b_name="v2_Counterparty_Redline.docx",
    )
    res = compare_contract_versions(req)

    assert res.total_clauses_compared >= 5
    assert res.material_risk_shifts >= 4
    assert res.net_risk_delta > 0
    shift_types = {d.risk_shift_type for d in res.diffs if d.is_material_shift}
    assert "liability_cap_weakened" in shift_types
    assert "payment_terms_extended" in shift_types
    assert "governing_law_changed" in shift_types
    assert "auto_renewal_added" in shift_types


def test_compare_identical_versions_has_zero_risk_delta() -> None:
    """Comparing identical drafts reports zero material risk shifts."""
    text = "1. TERM. The initial term of this Agreement is twelve (12) months."
    res = compare_contract_versions(
        CompareVersionsRequest(version_a_text=text, version_b_text=text)
    )
    assert res.material_risk_shifts == 0
    assert res.net_risk_delta == 0


def test_questionnaire_and_compare_boundary_validation() -> None:
    """Reject empty questionnaire list or empty version texts."""
    with pytest.raises(ValidationError):
        QuestionnaireRequest(items=[])

    with pytest.raises(ValidationError):
        CompareVersionsRequest(version_a_text="", version_b_text="Valid text")
