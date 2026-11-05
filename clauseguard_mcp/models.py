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


def _coerce_playbook(val: Any) -> PlaybookType:
    if isinstance(val, PlaybookType):
        return val
    raw = str(val or "").strip().lower().replace("-", "_").replace(" ", "_")
    if raw in ("founder_friendly", "saas_vendor", "gdpr_dpa", "hipaa_baa"):
        return PlaybookType(raw)
    if "hipaa" in raw or "baa" in raw or "health" in raw:
        return PlaybookType.HIPAA_BAA
    if "gdpr" in raw or "dpa" in raw or "privacy" in raw:
        return PlaybookType.GDPR_DPA
    if "vendor" in raw or "provider" in raw or "seller" in raw:
        return PlaybookType.SAAS_VENDOR
    return PlaybookType.FOUNDER_FRIENDLY


class AuditContractRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

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

    @model_validator(mode="before")
    @classmethod
    def coerce_aliases(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"contract_text": data}
        if not isinstance(data, dict):
            return data
        out = dict(data)
        if not out.get("contract_text"):
            for alias in ("text", "contract", "document_text", "agreement_text", "content", "body"):
                if out.get(alias):
                    out["contract_text"] = str(out[alias])
                    break
        if "playbook" in out:
            out["playbook"] = _coerce_playbook(out["playbook"])
        if not out.get("contract_name"):
            out["contract_name"] = str(out.get("filename") or out.get("document_name") or "Agreement_Reviewed.docx")
        return out

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
    model_config = ConfigDict(frozen=True, extra="ignore")

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

    @model_validator(mode="before")
    @classmethod
    def coerce_profile_aliases(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return {}
        out = dict(data)
        if not out.get("company_name"):
            for alias in ("organization", "vendor_name", "org_name", "name", "company"):
                if out.get(alias):
                    out["company_name"] = str(out[alias])
                    break
        return out


class QuestionnaireItem(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    id: str = Field(default="Q-01", min_length=1, max_length=64)
    question: str = Field(min_length=1, max_length=2000)
    category_hint: str | None = Field(default=None, max_length=80)

    @model_validator(mode="before")
    @classmethod
    def coerce_item(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"id": "Q-01", "question": data.strip()}
        if not isinstance(data, dict):
            return data
        out = dict(data)
        raw_id = out.get("id")
        if raw_id is None or str(raw_id).strip() == "":
            for id_alias in ("question_id", "q_id", "number", "index", "item_id", "key"):
                if out.get(id_alias) is not None and str(out.get(id_alias)).strip() != "":
                    raw_id = out[id_alias]
                    break
        out["id"] = str(raw_id).strip() if raw_id is not None and str(raw_id).strip() else "Q-01"

        raw_q = out.get("question")
        if not raw_q or not str(raw_q).strip():
            for q_alias in ("question_text", "text", "prompt", "query", "control", "requirement", "item", "title"):
                if out.get(q_alias) and str(out.get(q_alias)).strip():
                    raw_q = out[q_alias]
                    break
        if raw_q is not None:
            out["question"] = str(raw_q).strip()

        if not out.get("category_hint"):
            for c_alias in ("category", "domain", "topic", "section"):
                if out.get(c_alias):
                    out["category_hint"] = str(out[c_alias]).strip()
                    break
        return out


class QuestionnaireRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    items: tuple[QuestionnaireItem, ...] = Field(min_length=1, max_length=100)
    profile: SecurityProfile = Field(default_factory=SecurityProfile)

    @model_validator(mode="before")
    @classmethod
    def coerce_request(cls, data: Any) -> Any:
        if isinstance(data, list):
            data = {"items": data}
        elif isinstance(data, str):
            lines = [ln.strip() for ln in data.splitlines() if ln.strip()]
            data = {"items": lines or [data]}
        if not isinstance(data, dict):
            return data
        out = dict(data)
        raw_items = out.get("items")
        if not raw_items:
            for alias in ("questions", "questionnaire", "security_questions", "queries", "controls"):
                if out.get(alias):
                    raw_items = out[alias]
                    break
        if isinstance(raw_items, str):
            raw_items = [ln.strip() for ln in raw_items.splitlines() if ln.strip()] or [raw_items]
        if isinstance(raw_items, (list, tuple)):
            normalized_items: list[dict[str, Any]] = []
            for idx, entry in enumerate(raw_items, start=1):
                default_id = f"Q-{idx:02d}"
                if isinstance(entry, str):
                    normalized_items.append({"id": default_id, "question": entry.strip()})
                elif isinstance(entry, dict):
                    item_copy = dict(entry)
                    has_any_id = any(
                        item_copy.get(k) is not None and str(item_copy.get(k)).strip() != ""
                        for k in ("id", "question_id", "q_id", "number", "index", "item_id", "key")
                    )
                    if not has_any_id:
                        item_copy["id"] = default_id
                    normalized_items.append(item_copy)
                else:
                    normalized_items.append({"id": default_id, "question": str(entry)})
            out["items"] = normalized_items

        if not out.get("profile"):
            for p_alias in ("vendor_profile", "company_profile", "organization_profile", "security_profile"):
                if isinstance(out.get(p_alias), dict):
                    out["profile"] = out[p_alias]
                    break
            else:
                if out.get("company_name") or out.get("organization"):
                    out["profile"] = {"company_name": str(out.get("company_name") or out.get("organization"))}
        return out


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
    model_config = ConfigDict(frozen=True, extra="ignore")

    version_a_text: str = Field(min_length=1, max_length=250_000)
    version_b_text: str = Field(min_length=1, max_length=250_000)
    version_a_name: str = Field(default="Initial_Agreement_Draft.docx", max_length=120)
    version_b_name: str = Field(default="Counterparty_Returned_Markup.docx", max_length=120)

    @model_validator(mode="before")
    @classmethod
    def coerce_diff_aliases(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        out = dict(data)
        if not out.get("version_a_text"):
            for a_alias in ("draft_a", "original_text", "original", "v1", "baseline", "text_a", "contract_a"):
                if out.get(a_alias):
                    out["version_a_text"] = str(out[a_alias])
                    break
        if not out.get("version_b_text"):
            for b_alias in ("draft_b", "revised_text", "revised", "markup", "counterparty_text", "v2", "text_b", "contract_b"):
                if out.get(b_alias):
                    out["version_b_text"] = str(out[b_alias])
                    break
        return out


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
