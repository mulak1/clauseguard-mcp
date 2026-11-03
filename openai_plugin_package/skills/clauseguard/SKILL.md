---
name: clauseguard
description: Use when the user pastes or uploads commercial contracts or clauses for review or redlining, compares two contract drafts, or shares customer security or privacy questionnaire items.
---

# ClauseGuard: Contract Redlines Workflow

1. When the user wants a commercial contract (MSA, Mutual NDA, SaaS Subscription, DPA, or HIPAA BAA) reviewed or redlined, call `audit_and_redline_contract`.
   - Present the 0-100 Risk Score, Executive Sign-Off Recommendation, Missing Clause Warnings, Preferred vs. Middle-Ground Compromise Redlines, Ready-to-Send Negotiation Email, and the downloadable Microsoft Word (`.docx`) Track Changes link (`public_download_url`).
2. When the user wants to compare two contract versions, call `compare_contract_versions` and highlight material risk shifts.
3. When the user wants to complete a customer security or privacy questionnaire, call `autofill_security_questionnaire`.
