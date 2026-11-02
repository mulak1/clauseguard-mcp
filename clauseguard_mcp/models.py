"""Immutable Pydantic v2 boundary schemas for ClauseGuard MCP."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class PlaybookType(str, Enum):
    FOUNDER_FRIENDLY = "founder_friendly"
    SAAS_VENDOR = "saas_vendor"
    GDPR_DPA = "gdpr_dpa"
    HIPAA_BAA = "hipaa_baa"


class AuditContractRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    contract_text: str | None = Field(
        default=None,
        max_length=250_000,
        description="Plain text of the agreement to review and redline.",
    )
    docx_base64: str | None = Field(
        default=None,
        max_length=5_000_000,
        description="Base64-encoded Microsoft Word (.docx) file to review and redline.",
    )
    playbook: PlaybookType = Field(
        default=PlaybookType.FOUNDER_FRIENDLY,
        description="Negotiation standard to apply during review.",
    )
    contract_name: str = Field(
        default="Agreement_Reviewed.docx",
        min_length=1,
        max_length=200,
        description="Filename for the exported Word (.docx) document.",
    )
    author: str = Field(
        default="ClauseGuard Legal Desk",
        min_length=1,
        max_length=100,
        description="Reviewer name shown in Microsoft Word Track Changes.",
    )

    @model_validator(mode="after")
    def validate_source_present(self) -> "AuditContractRequest":
        has_text = bool(self.contract_text and self.contract_text.strip())
        has_docx = bool(self.docx_base64 and self.docx_base64.strip())
        if not has_text and not has_docx:
            raise ValueError("Please provide either agreement text or a Word (.docx) file.")
        return self


class RedlineFinding(BaseModel):
    model_config = ConfigDict(frozen=True)

    clause_id: str
    category: str
    title: str
    plain_english_summary: str = ""
    severity: Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]
    risk_points: int
    original_excerpt: str
    proposed_redline: str
    compromise_redline: str = ""
    rationale: str
    counterparty_note: str = ""
    playbook_reference: str


class MissingClauseWarning(BaseModel):
    model_config = ConfigDict(frozen=True)

    clause_name: str
    importance: Literal["RECOMMENDED", "ESSENTIAL"]
    why_it_matters: str
    suggested_language: str


class AuditContractResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    doc_id: str
    contract_name: str
    playbook: PlaybookType
    playbook_label: str = "Balanced Commercial Standard"
    risk_score: int = Field(ge=0, le=100)
    risk_level: Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]
    sign_off_recommendation: str = ""
    executive_summary: str
    counterparty_email_draft: str = ""
    findings: tuple[RedlineFinding, ...]
    missing_clauses: tuple[MissingClauseWarning, ...] = ()
    redlined_docx_b64: str
    download_url: str
    track_changes_summary: dict[str, Any]


class CustomDocxItem(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    clause_id: str
    title: str
    severity: Literal["LOW", "MODERATE", "HIGH", "CRITICAL"] = "HIGH"
    original_excerpt: str
    replacement_text: str
    rationale: str = ""
    playbook_reference: str = "Standard Playbook"


class CustomDocxRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    contract_name: str = Field(default="Agreement_Redlined.docx", min_length=1, max_length=200)
    playbook: PlaybookType = PlaybookType.FOUNDER_FRIENDLY
    risk_score: int = Field(default=25, ge=0, le=100)
    risk_level: str = "MODERATE"
    contract_text: str = Field(min_length=5, max_length=250_000)
    accepted_redlines: tuple[CustomDocxItem, ...] = ()
    author: str = Field(default="ClauseGuard Legal Desk", max_length=100)


class SecurityProfile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    company_name: str = Field(default="Our Organization", max_length=120)
    soc2_status: str = Field(
        default="Independent SOC 2 Type II examination completed annually with continuous control monitoring",
        max_length=300,
    )
    iso27001_status: str = Field(
        default="ISO/IEC 27001:2022 certified Information Security Management System with annual external audits",
        max_length=300,
    )
    gdpr_status: str = Field(
        default="Full compliance with GDPR Articles 28 and 32, supported by Standard Contractual Clauses",
        max_length=300,
    )
    hipaa_status: str = Field(
        default="Compliant with HIPAA Security and Privacy Rules; standard Business Associate Agreements available",
        max_length=300,
    )
    encryption_at_rest: str = Field(
        default="AES-256 encryption at rest with hardware-backed key management and automatic 90-day key rotation",
        max_length=300,
    )
    encryption_in_transit: str = Field(
        default="TLS 1.3 (minimum TLS 1.2) encryption in transit with strict transport security across all connections",
        max_length=300,
    )
    breach_notification_hours: int = Field(default=24, ge=1, le=72)
    subprocessor_notice_days: int = Field(default=30, ge=7, le=90)
    access_control: str = Field(
        default="Single Sign-On (SAML 2.0 / OIDC), mandatory multi-factor authentication, role-based access, and quarterly reviews",
        max_length=300,
    )
    dr_rpo_rto: str = Field(
        default="Recovery Point Objective (RPO) under 15 minutes and Recovery Time Objective (RTO) under 2 hours, tested twice yearly",
        max_length=300,
    )


class QuestionnaireItem(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1, max_length=64)
    question: str = Field(min_length=3, max_length=2000)
    category_hint: str | None = Field(default=None, max_length=80)


class QuestionnaireRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    items: tuple[QuestionnaireItem, ...] = Field(min_length=1, max_length=100)
    profile: SecurityProfile = Field(default_factory=SecurityProfile)


class QuestionnaireAnswer(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    question: str
    domain: str
    compliance_status: Literal["COMPLIANT", "PARTIAL_REVIEW", "MANUAL_REQUIRED"]
    answer: str
    evidence_refs: tuple[str, ...]
    confidence: float = Field(ge=0.0, le=1.0)
    needs_human_review: bool


class QuestionnaireResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    company_name: str
    total_items: int
    auto_completed_count: int
    average_confidence: float
    answers: tuple[QuestionnaireAnswer, ...]


class CompareVersionsRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    version_a_text: str = Field(min_length=5, max_length=250_000)
    version_b_text: str = Field(min_length=5, max_length=250_000)
    version_a_name: str = Field(default="Initial_Agreement_Draft.docx", max_length=120)
    version_b_name: str = Field(default="Counterparty_Returned_Markup.docx", max_length=120)


class ClauseDiffItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    clause_index: int
    change_type: Literal["UNCHANGED", "MODIFIED", "ADDED", "REMOVED"]
    version_a_clause: str
    version_b_clause: str
    is_material_shift: bool
    risk_shift_type: str
    plain_title: str = ""
    severity: Literal["NONE", "LOW", "MODERATE", "HIGH", "CRITICAL"]
    risk_delta: int
    legal_impact: str


class CompareVersionsResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    version_a_name: str
    version_b_name: str
    total_clauses_compared: int
    material_risk_shifts: int
    net_risk_delta: int
    summary: str
    diffs: tuple[ClauseDiffItem, ...]
