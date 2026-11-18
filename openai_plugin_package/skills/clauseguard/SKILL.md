---
name: clauseguard
description: Use when the user pastes or uploads commercial agreement drafts or clauses for commercial checklist comparison or Microsoft Word (.docx) Track Changes formatting, compares two draft versions, or shares customer security questionnaire items.
---

# ClauseGuard: Commercial Checklist & Word Track Changes Workflow

1. **Important Usage Policy Rule (Informational Utility Only — Not Legal Advice):**
   - ClauseGuard is an automated commercial template checklist comparison and Microsoft Word (`.docx`) Track Changes formatting utility. It does **not** provide legal advice, regulatory compliance opinions, or legal representation.
   - Always include the returned `disclaimer` reminding the user to review all commercial checklist differences and Track Changes drafts with their team and legal counsel.
2. When the user wants an agreement draft compared against a commercial template checklist or formatted with Microsoft Word (`.docx`) Track Changes, call `audit_and_redline_contract`.
   - Present the Playbook Alignment Summary, 0-100 Checklist Variance Score, Missing Clause Checklist Items, Preferred vs. Middle-Ground Compromise Wording, Draft Counterparty Discussion Note, the downloadable Microsoft Word (`.docx`) Track Changes link (`download_docx_url`), and the informational disclaimer.
3. When the user wants to compare two agreement drafts, call `compare_contract_versions` and highlight commercial text differences between Draft A and Draft B.
4. When the user wants to complete a customer security questionnaire, call `autofill_security_questionnaire`.
