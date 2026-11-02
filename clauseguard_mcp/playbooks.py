"""Plain-English commercial negotiation playbooks and realistic agreement templates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from clauseguard_mcp.models import PlaybookType


PLAYBOOK_LABELS: dict[PlaybookType, str] = {
    PlaybookType.FOUNDER_FRIENDLY: "Balanced Buyer & Founder Standard",
    PlaybookType.SAAS_VENDOR: "Software Provider Commercial Standard",
    PlaybookType.GDPR_DPA: "Data Privacy & Subprocessor Standard",
    PlaybookType.HIPAA_BAA: "Healthcare Privacy (BAA) Standard",
}


@dataclass(frozen=True)
class ClauseRule:
    category: str
    title: str
    plain_summary: str
    severity: Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]
    base_points: int
    patterns: tuple[str, ...]
    rationale: str
    counterparty_note: str
    compromise: str
    replacements: dict[PlaybookType, str]
    playbook_ref: str


CLAUSE_RULES: tuple[ClauseRule, ...] = (
    ClauseRule(
        category="uncapped_liability",
        title="Unlimited Financial Liability Exposure",
        plain_summary="Removes the financial cap on what you could owe if a dispute arises.",
        severity="CRITICAL",
        base_points=26,
        patterns=(
            r"liability\s+shall\s+be\s+uncapped",
            r"unlimited\s+liability",
            r"uncapped\s+and\s+unlimited",
            r"liable\s+for\s+all\s+direct,\s+indirect,\s+consequential",
        ),
        rationale=(
            "Signing an agreement without a clear financial cap exposes your business to claims "
            "that far exceed the value of the contract itself."
        ),
        counterparty_note=(
            "We propose a standard mutual cap equal to 12 months of fees paid so both sides have "
            "predictable, insurable risk."
        ),
        compromise=(
            "MUTUAL LIMITATION OF LIABILITY. Each party's aggregate liability shall be capped at "
            "twelve (12) months of fees paid, with a two times (2x) super-cap solely for breaches "
            "of confidentiality or data protection obligations."
        ),
        replacements={
            PlaybookType.FOUNDER_FRIENDLY: (
                "MUTUAL LIMITATION OF LIABILITY. Except for breaches of confidentiality or gross negligence, "
                "neither party's total liability shall exceed the fees paid or payable in the twelve (12) "
                "months immediately preceding the claim, and neither party shall be liable for indirect "
                "or consequential damages."
            ),
            PlaybookType.SAAS_VENDOR: (
                "LIMITATION OF LIABILITY. Provider's cumulative liability arising out of or relating to this "
                "Agreement shall not exceed the subscription fees paid by Customer in the twelve (12) months "
                "preceding the event giving rise to the claim."
            ),
            PlaybookType.GDPR_DPA: (
                "DATA PROTECTION LIABILITY CAP. Each party's total liability under this Addendum shall be "
                "capped at two times (2x) the annual fees paid under the main agreement."
            ),
            PlaybookType.HIPAA_BAA: (
                "LIABILITY LIMITATION. Business Associate's aggregate liability for regulatory or remediation "
                "costs under this Addendum shall not exceed two times (2x) the twelve-month contract value."
            ),
        },
        playbook_ref="Standard §1.1 — Mutual 12-Month Fee Cap",
    ),
    ClauseRule(
        category="unilateral_indemnification",
        title="One-Sided Legal Defense Obligation",
        plain_summary="Requires you to pay the other side's legal bills without mutual protection.",
        severity="HIGH",
        base_points=20,
        patterns=(
            r"indemnify,\s*defend,\s*and\s+hold\s+harmless\s+vendor[\s\S]{0,80}unilaterally",
            r"customer\s+shall\s+unilaterally\s+indemnify",
            r"without\s+reciprocal\s+obligation",
            r"indemnify\s+disclosing\s+party\s+against\s+any\s+and\s+all\s+losses\s+whatsoever",
        ),
        rationale=(
            "A one-way defense clause makes you responsible for their legal costs while leaving you "
            "unprotected if their product or service infringes someone else's rights."
        ),
        counterparty_note=(
            "We updated the indemnification section so both parties mutually cover third-party IP "
            "infringement and gross negligence."
        ),
        compromise=(
            "MUTUAL THIRD-PARTY INDEMNIFICATION. Each party shall defend and indemnify the other against "
            "third-party claims arising from its own intellectual property infringement, gross negligence, "
            "or willful misconduct, subject to prompt written notice."
        ),
        replacements={
            PlaybookType.FOUNDER_FRIENDLY: (
                "MUTUAL INDEMNIFICATION. Each party shall defend and indemnify the other party against "
                "third-party claims arising from (a) its infringement of third-party intellectual property "
                "rights, or (b) its gross negligence or willful misconduct."
            ),
            PlaybookType.SAAS_VENDOR: (
                "MUTUAL INDEMNIFICATION. Provider shall defend Customer against third-party claims that the "
                "Service infringes intellectual property rights; Customer shall defend Provider against "
                "third-party claims arising from unlawful Customer content."
            ),
            PlaybookType.GDPR_DPA: (
                "PROPORTIONAL PRIVACY RESPONSIBILITY. Each party shall be responsible only for that portion "
                "of regulatory fines or damages directly caused by its breach of allocated privacy duties."
            ),
            PlaybookType.HIPAA_BAA: (
                "PROPORTIONAL BAA INDEMNITY. Each party shall indemnify the other solely to the extent an "
                "unauthorized disclosure of protected health information was caused by its breach."
            ),
        },
        playbook_ref="Standard §2.3 — Mutual Third-Party Defense",
    ),
    ClauseRule(
        category="sneaky_auto_renewal",
        title="Multi-Year Lock-In & Early Cancellation Deadline",
        plain_summary="Locks you into a 2-to-3 year renewal unless you cancel 90–120 days early.",
        severity="HIGH",
        base_points=16,
        patterns=(
            r"automatically\s+renew\s+for\s+(?:successive\s+)?[2-5]-year",
            r"(?:90|120|180)\s+days\s+prior(?:\s+written)?\s+notice",
            r"auto-renew\s+with\s+a\s+mandatory\s+15%\s+annual\s+uplift",
        ),
        rationale=(
            "A 90-to-120 day notice window on a multi-year renewal is easy to miss on the calendar "
            "and locks teams into unwanted multi-year commitments."
        ),
        counterparty_note=(
            "We adjusted renewals to standard 12-month periods with a 30-day cancellation notice window "
            "and a 5% cap on annual price increases."
        ),
        compromise=(
            "TERM AND RENEWAL. This Agreement renews for 12-month periods unless either party gives "
            "forty-five (45) days prior written notice, with Provider sending a renewal reminder at least "
            "60 days before expiration."
        ),
        replacements={
            PlaybookType.FOUNDER_FRIENDLY: (
                "TERM AND RENEWAL. This Agreement shall renew for twelve (12) month periods unless either "
                "party gives written notice of non-renewal at least thirty (30) days before the end of the "
                "current term. Any renewal price adjustment shall not exceed 5% per year."
            ),
            PlaybookType.SAAS_VENDOR: (
                "RENEWAL TERM. Subscriptions renew annually for 12-month periods unless Customer provides "
                "thirty (30) days written notice prior to renewal."
            ),
            PlaybookType.GDPR_DPA: (
                "COTERMINOUS TERM. This Data Processing Addendum stays in effect only for the duration of "
                "the main agreement and ends automatically when data processing ceases."
            ),
            PlaybookType.HIPAA_BAA: (
                "TERM AND RETURN OF RECORDS. This Addendum ends together with the main agreement, whereupon "
                "all protected health records shall be securely returned or destroyed within 30 days."
            ),
        },
        playbook_ref="Standard §3.2 — Annual Renewal & 30-Day Notice",
    ),
    ClauseRule(
        category="broad_ip_assignment",
        title="Overbroad Transfer of Your Pre-Existing Intellectual Property",
        plain_summary="Transfers ownership of your existing technology, tools, or product improvements.",
        severity="CRITICAL",
        base_points=22,
        patterns=(
            r"irrevocably\s+assigns\s+all\s+right,\s*title,\s*and\s+interest\s+in\s+all\s+customer\s+pre-existing\s+ip",
            r"background\s+technology\s+to\s+vendor",
            r"assigns\s+all\s+pre-existing\s+intellectual\s+property",
            r"derivatives\s+of\s+recipient's\s+independent\s+products\s+shall\s+belong\s+exclusively",
        ),
        rationale=(
            "Giving away ownership of your pre-existing intellectual property or independent product "
            "improvements clouds ownership of your core business assets."
        ),
        counterparty_note=(
            "We clarified that each party keeps 100% ownership of its existing intellectual property, "
            "data, and independent product developments."
        ),
        compromise=(
            "BACKGROUND IP RETENTION. Each party retains exclusive ownership of its pre-existing "
            "intellectual property and independent developments, granting only a limited, non-exclusive "
            "license strictly necessary to perform this Agreement during the Term."
        ),
        replacements={
            PlaybookType.FOUNDER_FRIENDLY: (
                "INTELLECTUAL PROPERTY OWNERSHIP. Each party retains sole and exclusive ownership of its "
                "pre-existing intellectual property, background technology, and confidential information. "
                "No ownership rights are transferred under this Agreement."
            ),
            PlaybookType.SAAS_VENDOR: (
                "OWNERSHIP OF PLATFORM AND DATA. Customer retains all ownership rights in Customer Data "
                "and pre-existing materials; Provider retains all ownership rights in the Software Service."
            ),
            PlaybookType.GDPR_DPA: (
                "OWNERSHIP OF PERSONAL DATA. Customer retains sole ownership and control of all Personal "
                "Data; Provider processes data solely on Customer's documented instructions."
            ),
            PlaybookType.HIPAA_BAA: (
                "OWNERSHIP OF HEALTH INFORMATION. Covered Entity retains exclusive ownership of all Protected "
                "Health Information; Business Associate may not sell or commercialize such data."
            ),
        },
        playbook_ref="Standard §4.1 — Pre-Existing IP & Data Retention",
    ),
    ClauseRule(
        category="non_solicit_overreach",
        title="Overbroad Global Hiring & Recruiting Restriction",
        plain_summary="Blocks your company from hiring for 3–5 years worldwide, even via public job ads.",
        severity="MODERATE",
        base_points=14,
        patterns=(
            r"not\s+solicit\s+or\s+hire\s+any\s+employee[\s\S]{0,80}(?:3|4|5)\s+years",
            r"anywhere\s+in\s+the\s+world\s+for\s+a\s+period\s+of\s+[3-9]\s+years",
            r"prohibited\s+from\s+hiring\s+even\s+via\s+general\s+public\s+job\s+postings",
        ),
        rationale=(
            "Multi-year global hiring bans that prohibit applicants from answering public job postings "
            "create unnecessary HR compliance traps."
        ),
        counterparty_note=(
            "We narrowed the non-solicitation clause to 12 months for personnel directly working on the "
            "project, with the standard carveout for public job postings."
        ),
        compromise=(
            "SCOPED NON-SOLICITATION. For twelve (12) months following the Term, neither party shall "
            "directly target for solicitation personnel with whom it had material contact under this "
            "Agreement, excluding candidates who respond to general public job listings."
        ),
        replacements={
            PlaybookType.FOUNDER_FRIENDLY: (
                "LIMITED NON-SOLICITATION. During the Term and for twelve (12) months thereafter, neither "
                "party shall knowingly solicit for employment personnel directly involved in this Agreement; "
                "general public job postings shall not be restricted."
            ),
            PlaybookType.SAAS_VENDOR: (
                "MUTUAL 12-MONTH NON-SOLICITATION. Neither party shall targeted-solicit employees directly "
                "engaged in the relationship for 12 months, excluding general recruiting advertisements."
            ),
            PlaybookType.GDPR_DPA: (
                "PERSONNEL CONFIDENTIALITY. Provider ensures all staff authorized to handle Personal Data "
                "are bound by written confidentiality obligations."
            ),
            PlaybookType.HIPAA_BAA: (
                "WORKFORCE SAFEGUARDS. Business Associate ensures all workforce members complete privacy "
                "training and comply with administrative safeguards."
            ),
        },
        playbook_ref="Standard §5.4 — 12-Month Scoped Non-Solicit",
    ),
    ClauseRule(
        category="missing_gdpr_subprocessor_notice",
        title="Adding Third-Party Data Vendors Without Advance Notice",
        plain_summary="Allows the vendor to share your customer data with new subcontractors without telling you.",
        severity="HIGH",
        base_points=20,
        patterns=(
            r"engage\s+any\s+new\s+subprocessors\s+without\s+prior\s+notice",
            r"without\s+prior\s+notice\s+or\s+consent\s+from\s+controller",
            r"without\s+subprocessor\s+flow-down\s+restrictions",
        ),
        rationale=(
            "Privacy regulations require vendors to give you advance written notice before sharing "
            "your customer data with new third-party subprocessors."
        ),
        counterparty_note=(
            "We added a 30-day advance written notice requirement before new subprocessors are given "
            "access to customer data, along with equivalent privacy flow-down terms."
        ),
        compromise=(
            "SUBPROCESSOR NOTICE. Provider shall maintain an up-to-date list of subprocessors and provide "
            "at least fifteen (15) days advance written notice before engaging any new subprocessor."
        ),
        replacements={
            PlaybookType.FOUNDER_FRIENDLY: (
                "SUBPROCESSOR ADVANCE NOTICE. Provider shall give at least thirty (30) days prior written "
                "notice before authorizing any new subprocessor and allow Customer to object on reasonable "
                "data-protection grounds."
            ),
            PlaybookType.SAAS_VENDOR: (
                "SUBPROCESSOR LIST & 30-DAY NOTICE. Provider maintains a current subprocessor list and "
                "notifies subscribed Customers at least thirty (30) days prior to adding a new subprocessor."
            ),
            PlaybookType.GDPR_DPA: (
                "SUBPROCESSOR CONTROLS (ARTICLE 28). Processor shall notify Controller in writing at least "
                "thirty (30) days before engaging any new Subprocessor and bind each Subprocessor to "
                "equivalent written data protection obligations."
            ),
            PlaybookType.HIPAA_BAA: (
                "SUBCONTRACTOR FLOW-DOWN. Business Associate shall ensure any subcontractor handling "
                "protected health information signs a written agreement with equivalent privacy safeguards."
            ),
        },
        playbook_ref="Standard §6.1 — 30-Day Advance Subprocessor Notice",
    ),
    ClauseRule(
        category="delayed_breach_notification",
        title="Delayed Security Incident Reporting Window (30–90 Days)",
        plain_summary="Lets the vendor wait 30 to 90 days before telling you about a data breach.",
        severity="HIGH",
        base_points=18,
        patterns=(
            r"notify\s+controller\s+within\s+(?:14|30|60|90)\s+days",
            r"report\s+breaches\s+within\s+(?:30|60|90)\s+days",
        ),
        rationale=(
            "Data protection laws require you to report breaches within 72 hours. If a vendor waits "
            "30 days to tell you, your company cannot meet its own legal deadline."
        ),
        counterparty_note=(
            "We updated the security incident reporting window from 30 days to within 24–48 hours "
            "so we can meet statutory 72-hour reporting timelines."
        ),
        compromise=(
            "BREACH NOTIFICATION TIMELINE. Provider shall notify Customer without undue delay and within "
            "forty-eight (48) hours of confirming any unauthorized disclosure of Customer Data."
        ),
        replacements={
            PlaybookType.FOUNDER_FRIENDLY: (
                "SECURITY INCIDENT NOTIFICATION. Provider shall notify Customer without undue delay, and "
                "no later than forty-eight (48) hours after confirming a security incident affecting Customer Data."
            ),
            PlaybookType.SAAS_VENDOR: (
                "INCIDENT REPORTING WINDOW. Provider shall notify Customer within forty-eight (48) hours "
                "of confirming any unauthorized access to Customer Data."
            ),
            PlaybookType.GDPR_DPA: (
                "PERSONAL DATA BREACH NOTIFICATION. Processor shall notify Controller without undue delay "
                "and no later than twenty-four (24) hours after becoming aware of a Personal Data Breach."
            ),
            PlaybookType.HIPAA_BAA: (
                "BREACH NOTIFICATION. Business Associate shall notify Covered Entity without unreasonable "
                "delay and within forty-eight (48) hours of discovering any breach of unsecured health data."
            ),
        },
        playbook_ref="Standard §6.4 — 24–48 Hour Incident Notification",
    ),
)


SAMPLE_CONTRACTS: dict[str, dict[str, str]] = {
    "predatory_msa": {
        "name": "Enterprise_Master_Services_Agreement.docx",
        "label": "Enterprise Master Services Agreement",
        "subtitle": "Vendor-drafted software agreement (5 high-risk clauses)",
        "playbook": "founder_friendly",
        "text": (
            "MASTER SERVICES AGREEMENT\n\n"
            "1. LIMITATION OF LIABILITY. Customer's liability shall be uncapped and unlimited for any and all "
            "claims arising under this Agreement, whereas Vendor's total liability is capped at $500.\n\n"
            "2. INDEMNIFICATION. Customer shall indemnify, defend, and hold harmless Vendor from any and all "
            "claims unilaterally without reciprocal obligation.\n\n"
            "3. TERM AND RENEWAL. This Agreement shall automatically renew for successive 3-year terms unless "
            "Customer provides written notice at least 120 days prior to expiration.\n\n"
            "4. INTELLECTUAL PROPERTY. Customer hereby irrevocably assigns all right, title, and interest in all "
            "Customer pre-existing IP and background technology to Vendor upon upload.\n\n"
            "5. NON-SOLICITATION. Customer shall not solicit or hire any employee or former contractor of Vendor "
            "anywhere in the world for a period of 5 years."
        ),
    },
    "unbalanced_nda": {
        "name": "Mutual_Non_Disclosure_Agreement.docx",
        "label": "Mutual Non-Disclosure Agreement",
        "subtitle": "Partnership evaluation NDA with hidden IP & hiring traps",
        "playbook": "founder_friendly",
        "text": (
            "NON-DISCLOSURE AND EVALUATION AGREEMENT\n\n"
            "1. INDEMNIFICATION & LIABILITY. Recipient's liability shall be uncapped and unlimited, and Recipient "
            "shall indemnify Disclosing Party against any and all losses whatsoever without reciprocal obligation.\n\n"
            "2. INTELLECTUAL PROPERTY RESIDUALS. Any improvements or derivatives of Recipient's independent products "
            "shall belong exclusively to Disclosing Party and Customer assigns all pre-existing intellectual property.\n\n"
            "3. NON-SOLICITATION OVERREACH. Recipient shall not solicit or hire any employee of Disclosing Party "
            "anywhere in the world for a period of 4 years, and is prohibited from hiring even via general public job postings."
        ),
    },
    "gdpr_dpa": {
        "name": "Customer_Data_Processing_Addendum.docx",
        "label": "Customer Data Processing Addendum",
        "subtitle": "Privacy addendum missing subprocessor notice & fast breach reporting",
        "playbook": "gdpr_dpa",
        "text": (
            "DATA PROCESSING ADDENDUM\n\n"
            "1. SUBPROCESSORS. Processor may engage any new subprocessors without prior notice or consent from Controller.\n\n"
            "2. PERSONAL DATA BREACH. In the event of a Personal Data Breach, Processor shall notify Controller within 30 days.\n\n"
            "3. LIABILITY. Customer's liability shall be uncapped and unlimited under this Data Processing Addendum."
        ),
    },
}

SAMPLE_QUESTIONNAIRE: tuple[dict[str, str], ...] = (
    {"id": "SEC-01", "question": "Does your organization maintain an independent SOC 2 Type II audit report?"},
    {"id": "SEC-02", "question": "How is customer data encrypted at rest and in transit across your infrastructure?"},
    {"id": "SEC-03", "question": "How do you handle GDPR Article 28 compliance and advance notice for new subprocessors?"},
    {"id": "SEC-04", "question": "What is your committed timeframe for notifying customers of a confirmed security incident?"},
    {"id": "SEC-05", "question": "Do you support Single Sign-On (SAML 2.0), multi-factor authentication, and role-based access?"},
    {"id": "SEC-06", "question": "What are your documented recovery objectives (RPO and RTO) and backup testing practices?"},
)

SAMPLE_DIFF_VERSIONS: dict[str, str] = {
    "version_a_name": "Initial_Agreement_Draft.docx",
    "version_b_name": "Counterparty_Returned_Markup.docx",
    "version_a_text": (
        "1. LIMITATION OF LIABILITY. Neither party's aggregate liability shall exceed 12 months of fees paid.\n"
        "2. PAYMENT TERMS. Customer shall pay undisputed invoices within Net 30 days of receipt.\n"
        "3. GOVERNING LAW. This Agreement is governed by the laws of the State of Delaware.\n"
        "4. RENEWAL. This Agreement renews only upon mutual written agreement for 12-month periods.\n"
        "5. INDEMNIFICATION. Each party shall mutually indemnify the other for third-party IP infringement claims."
    ),
    "version_b_text": (
        "1. LIMITATION OF LIABILITY. Customer's liability shall be uncapped and unlimited, while Vendor is capped at $1,000.\n"
        "2. PAYMENT TERMS. Customer shall pay all invoices within Net 90 days with 2% monthly late interest.\n"
        "3. GOVERNING LAW. This Agreement is governed by the laws of England and Wales in London.\n"
        "4. RENEWAL. This Agreement shall automatically renew for 3-year terms unless given 120 days notice.\n"
        "5. INDEMNIFICATION. Customer shall unilaterally indemnify Vendor for any and all claims whatsoever."
    ),
}
