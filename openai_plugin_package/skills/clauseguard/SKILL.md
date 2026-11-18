---
name: clauseguard
description: Use when the user pastes or uploads commercial contracts or clauses for commercial checklist comparison or Word (.docx) Track Changes formatting, compares two contract drafts, or shares customer security or privacy questionnaire items.
---

# ClauseGuard: Contract Redlines Workflow

1. **Important Usage Policy Rule (Informational Checklist Only — Not Legal Advice):**
   - ClauseGuard is an automated commercial playbook comparison and Microsoft Word (`.docx`) Track Changes formatting utility. It is **not a law firm** and **does not provide legal advice, formal legal opinions, or attorney representation**.
   - Never tell a user definitively whether to sign an agreement without counsel; always include the returned `disclaimer` reminding the user to review all commercial checklist variances and Track Changes drafts with a qualified attorney.
2. When the user wants a commercial contract (MSA, Mutual NDA, SaaS Subscription, DPA, or BAA) compared against a commercial playbook or formatted with Track Changes, call `audit_and_redline_contract`.
   - Present the Playbook Alignment Summary, 0-100 Checklist Variance Score, Missing Clause Checklist Items, Preferred vs. Middle-Ground Compromise Wording, Draft Counterparty Discussion Note, the downloadable Microsoft Word (`.docx`) Track Changes link (`download_docx_url`), and the non-legal-advice disclaimer.
3. When the user wants to compare two contract versions, call `compare_contract_versions` and highlight commercial text shifts between Draft A and Draft B.
4. When the user wants to complete a customer security or privacy questionnaire, call `autofill_security_questionnaire`.
