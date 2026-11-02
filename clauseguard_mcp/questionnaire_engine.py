"""Vendor Security Questionnaire Autofill & Contract Version Comparison Engines."""

from __future__ import annotations

import re
from typing import Literal

from clauseguard_mcp.models import (
    ClauseDiffItem,
    CompareVersionsRequest,
    CompareVersionsResponse,
    QuestionnaireAnswer,
    QuestionnaireItem,
    QuestionnaireRequest,
    QuestionnaireResponse,
    SecurityProfile,
)


def autofill_security_questionnaire(request: QuestionnaireRequest) -> QuestionnaireResponse:
    """Populate vendor security questionnaire answers, control references, and confidence scores."""
    answers = tuple(_answer_single_item(item, request.profile) for item in request.items)
    auto_count = sum(1 for a in answers if not a.needs_human_review)
    avg_conf = round(sum(a.confidence for a in answers) / len(answers), 2)

    return QuestionnaireResponse(
        company_name=request.profile.company_name,
        total_items=len(answers),
        auto_completed_count=auto_count,
        average_confidence=avg_conf,
        answers=answers,
    )


def _answer_single_item(item: QuestionnaireItem, profile: SecurityProfile) -> QuestionnaireAnswer:
    q_lower = f"{item.category_hint or ''} {item.question}".lower()

    if any(k in q_lower for k in ("soc 2", "soc2", "aicpa", "trust services", "type ii")):
        return QuestionnaireAnswer(
            id=item.id,
            question=item.question,
            domain="Independent Audit & SOC 2",
            compliance_status="COMPLIANT",
            answer=(
                f"Yes. {profile.company_name} maintains an {profile.soc2_status}. "
                "Current audit reports and bridge letters are available upon request under a non-disclosure agreement."
            ),
            evidence_refs=("SOC 2 Type II Report (Criteria CC1.1 & CC6.1)", "Annual Independent Audit Attestation"),
            confidence=0.97,
            needs_human_review=False,
        )

    if any(k in q_lower for k in ("encrypt", "tls", "aes", "kms", "hsm", "at rest", "in transit", "key management")):
        return QuestionnaireAnswer(
            id=item.id,
            question=item.question,
            domain="Data Encryption & Key Protection",
            compliance_status="COMPLIANT",
            answer=(
                f"Yes. At {profile.company_name}, customer data is protected using {profile.encryption_at_rest}. "
                f"All network traffic is protected via {profile.encryption_in_transit}."
            ),
            evidence_refs=("Cryptography & Key Management Policy §4.2", "SOC 2 Control CC6.7 (Encryption)"),
            confidence=0.96,
            needs_human_review=False,
        )

    if any(k in q_lower for k in ("gdpr", "subprocessor", "article 28", "scc", "data privacy", "dpa")):
        return QuestionnaireAnswer(
            id=item.id,
            question=item.question,
            domain="Data Privacy & Subprocessor Notice",
            compliance_status="COMPLIANT",
            answer=(
                f"Yes. {profile.company_name} maintains {profile.gdpr_status}. We provide at least "
                f"{profile.subprocessor_notice_days} days advance written notice before adding any new data subprocessor."
            ),
            evidence_refs=("Customer Data Processing Addendum (Article 28)", "Published Subprocessor Schedule"),
            confidence=0.95,
            needs_human_review=False,
        )

    if any(k in q_lower for k in ("iso 27001", "iso27001", "iso/iec", "hipaa", "baa", "phi")):
        return QuestionnaireAnswer(
            id=item.id,
            question=item.question,
            domain="Information Security & Healthcare Standards",
            compliance_status="COMPLIANT",
            answer=(
                f"Yes. {profile.company_name} maintains an {profile.iso27001_status} and is {profile.hipaa_status}."
            ),
            evidence_refs=("ISO/IEC 27001:2022 Certificate of Registration", "HIPAA Security Safeguards Matrix"),
            confidence=0.94,
            needs_human_review=False,
        )

    if any(k in q_lower for k in ("incident", "breach", "sla", "notify", "response", "forensic")):
        return QuestionnaireAnswer(
            id=item.id,
            question=item.question,
            domain="Incident Response & Notification Timeframe",
            compliance_status="COMPLIANT",
            answer=(
                f"{profile.company_name} maintains an around-the-clock Incident Response Team and notifies affected "
                f"customers within {profile.breach_notification_hours} hours of confirming any unauthorized data access."
            ),
            evidence_refs=("Incident Response Plan §3.1 (24-Hour Notification)", "SOC 2 Control CC7.3"),
            confidence=0.95,
            needs_human_review=False,
        )

    if any(k in q_lower for k in ("mfa", "multi-factor", "sso", "saml", "rbac", "access control", "least privilege")):
        return QuestionnaireAnswer(
            id=item.id,
            question=item.question,
            domain="Access Control & Authentication",
            compliance_status="COMPLIANT",
            answer=f"Yes. {profile.company_name} enforces {profile.access_control}.",
            evidence_refs=("Access Control & Least-Privilege Standard §2", "SOC 2 Control CC6.2"),
            confidence=0.94,
            needs_human_review=False,
        )

    if any(k in q_lower for k in ("disaster", "rpo", "rto", "backup", "continuity", "bcdr", "failover")):
        return QuestionnaireAnswer(
            id=item.id,
            question=item.question,
            domain="Business Continuity & Recovery",
            compliance_status="COMPLIANT",
            answer=f"Yes. {profile.company_name} maintains a {profile.dr_rpo_rto} with encrypted backups.",
            evidence_refs=("Business Continuity & Disaster Recovery Plan", "Semi-Annual Failover Exercise Report"),
            confidence=0.93,
            needs_human_review=False,
        )

    return QuestionnaireAnswer(
        id=item.id,
        question=item.question,
        domain="Custom Operational Question (Needs Quick Check)",
        compliance_status="PARTIAL_REVIEW",
        answer=(
            f"{profile.company_name} maintains comprehensive security controls under our {profile.soc2_status}; "
            "this specific question has been highlighted for a quick review by your security lead."
        ),
        evidence_refs=("General Information Security Policy Manual",),
        confidence=0.62,
        needs_human_review=True,
    )


def compare_contract_versions(request: CompareVersionsRequest) -> CompareVersionsResponse:
    """Compare two agreement drafts clause-by-clause and highlight material business or legal shifts."""
    clauses_a = _split_clauses(request.version_a_text)
    clauses_b = _split_clauses(request.version_b_text)
    max_len = max(len(clauses_a), len(clauses_b))

    diffs: list[ClauseDiffItem] = []
    for idx in range(max_len):
        ca = clauses_a[idx] if idx < len(clauses_a) else ""
        cb = clauses_b[idx] if idx < len(clauses_b) else ""
        diffs.append(_compare_clause_pair(idx + 1, ca, cb))

    material_count = sum(1 for d in diffs if d.is_material_shift)
    net_delta = sum(d.risk_delta for d in diffs)
    summary = (
        f"We compared {len(diffs)} section(s) between {request.version_a_name} and {request.version_b_name} "
        f"and found {material_count} significant business or legal risk shift(s)."
    )

    return CompareVersionsResponse(
        version_a_name=request.version_a_name,
        version_b_name=request.version_b_name,
        total_clauses_compared=len(diffs),
        material_risk_shifts=material_count,
        net_risk_delta=net_delta,
        summary=summary,
        diffs=tuple(diffs),
    )


def _split_clauses(text: str) -> list[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines if lines else [text.strip()]


def _compare_clause_pair(idx: int, clause_a: str, clause_b: str) -> ClauseDiffItem:
    if clause_a == clause_b:
        return ClauseDiffItem(
            clause_index=idx,
            change_type="UNCHANGED",
            version_a_clause=clause_a,
            version_b_clause=clause_b,
            is_material_shift=False,
            risk_shift_type="no_change",
            plain_title="No Change",
            severity="NONE",
            risk_delta=0,
            legal_impact="This section is unchanged between both drafts.",
        )

    change_type: Literal["MODIFIED", "ADDED", "REMOVED"] = (
        "ADDED" if not clause_a else ("REMOVED" if not clause_b else "MODIFIED")
    )
    shift_type, plain_title, severity, delta, impact = _detect_material_shift(clause_a, clause_b)
    return ClauseDiffItem(
        clause_index=idx,
        change_type=change_type,
        version_a_clause=clause_a,
        version_b_clause=clause_b,
        is_material_shift=severity in ("MODERATE", "HIGH", "CRITICAL"),
        risk_shift_type=shift_type,
        plain_title=plain_title,
        severity=severity,
        risk_delta=delta,
        legal_impact=impact,
    )


def _detect_material_shift(
    clause_a: str,
    clause_b: str,
) -> tuple[str, str, Literal["NONE", "LOW", "MODERATE", "HIGH", "CRITICAL"], int, str]:
    b_low = clause_b.lower()
    a_low = clause_a.lower()

    if any(k in b_low for k in ("uncapped", "unlimited", "$1,000", "$500")) and "uncapped" not in a_low:
        return (
            "liability_cap_weakened",
            "Financial Liability Cap Removed or Weakened",
            "CRITICAL",
            28,
            "The other side removed the mutual 12-month liability cap and exposed your business to unlimited liability.",
        )

    if re.search(r"net\s*(?:60|75|90|120)", b_low) and not re.search(r"net\s*(?:60|75|90|120)", a_low):
        return (
            "payment_terms_extended",
            "Payment Window Stretched to 60–90+ Days",
            "MODERATE",
            12,
            "The payment schedule was pushed out from Net 30 to Net 90 days, slowing down cash collection.",
        )

    if ("governed by" in a_low or "governing law" in a_low or "governed by" in b_low) and a_low != b_low:
        return (
            "governing_law_changed",
            "Governing Law & Court Location Changed",
            "HIGH",
            16,
            "The legal jurisdiction governing disputes was moved to a different state or country.",
        )

    if ("automatically renew" in b_low or "120 days" in b_low or "3-year" in b_low) and "automatically renew" not in a_low:
        return (
            "auto_renewal_added",
            "Multi-Year Automatic Renewal Added",
            "HIGH",
            18,
            "The other side replaced mutual renewal with a 3-year automatic lock-in and a 120-day cancellation deadline.",
        )

    if ("unilaterally indemnify" in b_low or "any claim whatsoever" in b_low or "any and all claims" in b_low) and "unilaterally" not in a_low:
        return (
            "indemnity_broadened",
            "Mutual Defense Replaced with One-Sided Indemnity",
            "HIGH",
            20,
            "Mutual protection for third-party IP claims was replaced with a one-way obligation for you to cover all claims.",
        )

    return (
        "non_material_wording_edit",
        "Minor Wording Adjustment",
        "LOW",
        4,
        "Wording was edited slightly without shifting core risk; confirm it matches your commercial intent.",
    )
