# ClauseGuard: Contract Redlines (MCP Connector & Legal Review Desk)

Plain-English commercial contract review, clause-by-clause risk scoring, negotiation email drafting, security questionnaire completion, and downloadable Microsoft Word (`.docx`) Track Changes.

- **Live Legal Review Desk:** https://clauseguard-mcp-production.up.railway.app
- **Remote MCP Endpoint (Claude & ChatGPT):** `https://clauseguard-mcp-production.up.railway.app/mcp`
- **ChatGPT Action OpenAPI Spec:** `https://clauseguard-mcp-production.up.railway.app/chatgpt-openapi.json`
- **Privacy & Confidentiality Policy:** https://clauseguard-mcp-production.up.railway.app/privacy
- **Terms of Service:** https://clauseguard-mcp-production.up.railway.app/terms

---

## Included MCP Tools (All Read-Only & Idempotent)

1. **`audit_and_redline_contract` (`Review & Redline Contract`)**
   - Reviews commercial agreements (MSA, Mutual NDA, SaaS Subscription, Data Processing Agreement, or Business Associate Agreement) against a plain-English legal playbook (`founder_friendly`, `saas_vendor`, `gdpr_dpa`, `hipaa_baa`).
   - Returns a `0–100` risk score, executive sign-off recommendation, missing-clause warnings, preferred & middle-ground fallback clauses, a ready-to-send counterparty negotiation email, and a downloadable `.docx` file with native Microsoft Word Track Changes.

2. **`autofill_security_questionnaire` (`Complete Security Questionnaire`)**
   - Drafts plain-English security and privacy responses, control evidence citations, and confidence ratings across SOC 2 Type II, GDPR, HIPAA, ISO 27001, encryption, incident response, access control, and resilience.

3. **`compare_contract_versions` (`Compare Two Contract Drafts`)**
   - Compares an earlier contract draft against a counterparty markup clause-by-clause and flags material business or legal shifts.

---

## Connect to Claude

1. Open **Claude Settings → Connectors → Add custom connector**.
2. Name: `ClauseGuard: Contract Redlines`
3. Remote MCP Server URL: `https://clauseguard-mcp-production.up.railway.app/mcp`

## Local Development

```bash
pip install -r requirements.txt
pytest
python main.py
```
