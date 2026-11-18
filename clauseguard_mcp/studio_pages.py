"""Public HTML Pages (/privacy, /docs, /about, /terms) for ClauseGuard MCP."""

from __future__ import annotations

from clauseguard_mcp.studio_client_js import STUDIO_CLIENT_JS

__all__ = [
    "STUDIO_CLIENT_JS",
    "render_about_html",
    "render_docs_html",
    "render_privacy_html",
    "render_terms_html",
]


def _static_page_shell(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="icon" type="image/png" href="/icon.png" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif:wght@400&display=swap" rel="stylesheet">
  <style>
    body {{ font-family:'Instrument Sans',system-ui,sans-serif; background:#f9f9f9; color:#1f201d; margin:0; padding:3rem 1.5rem; line-height:1.65; font-size:16px; }}
    main {{ max-width:860px; margin:0 auto; background:#ffffff; border-radius:22px; padding:2.5rem; }}
    h1 {{ font-family:'Instrument Serif',Georgia,serif; font-size:2.4rem; font-weight:400; margin:0 0 0.5rem; }}
    h2 {{ font-size:1.15rem; margin:1.85rem 0 0.5rem; color:#1b6e66; }}
    p, li {{ font-size:1rem; color:#1f201d; max-width:68ch; }}
    code {{ background:#f3f3f2; padding:0.15rem 0.4rem; border-radius:6px; font-size:0.9rem; }}
    .table-wrapper {{ overflow:auto; max-inline-size:100%; container-type:inline-size; margin:1rem 0; border:1px solid #e7e7e5; border-radius:10px; }}
    table {{ width:100%; border-collapse:separate; border-spacing:0; font-size:0.94rem; }}
    caption {{ text-align:left; font-weight:600; padding:0.65rem 0.75rem; background:#f3f8f7; color:#1b6e66; border-bottom:1px solid #e7e7e5; }}
    thead {{ position:sticky; inset-block-start:0; z-index:1; }}
    th, td {{ text-align:left; padding:0.65rem 0.75rem; border-bottom:1px solid #e7e7e5; vertical-align:top; }}
    th {{ font-weight:600; color:#1b6e66; background:#f9f9f9; }}
    tbody th {{ position:sticky; inset-inline-start:0; background:#ffffff; font-weight:600; color:#1f201d; }}
    a {{ color:#1b6e66; text-decoration:none; font-weight:500; }}
    a:focus-visible, .table-wrapper:focus-visible {{ outline:3px solid #1b6e66; outline-offset:3px; }}
    .disclaimer-box {{ background:#f3f8f7; border-left:4px solid #1b6e66; padding:0.85rem 1.1rem; border-radius:8px; margin:1rem 0; font-size:0.95rem; }}
  </style>
</head>
<body>
  <main>{body_html}</main>
</body>
</html>"""


def render_privacy_html() -> str:
    """Return the complete Privacy & Confidentiality Policy page covering data collected, tool inputs/outputs, purposes, recipients, retention, and user controls."""
    return _static_page_shell(
        "Privacy &amp; Confidentiality Policy — ClauseGuard",
        """<p><a href="/">← Return to ClauseGuard Review Desk</a></p>
    <h1>Privacy &amp; Confidentiality Policy</h1>
    <p><strong>Effective Date:</strong> November 17, 2026 · <strong>Controller:</strong> Kader Mula (ClauseGuard) · <strong>Contact:</strong> <a href="mailto:mulak1@gmail.com">mulak1@gmail.com</a></p>
    <div class="disclaimer-box">
      <strong>Informational Commercial Checklist Only — Not Legal Advice:</strong> ClauseGuard is an automated commercial document comparison and Microsoft Word (<code>.docx</code>) Track Changes formatting utility. It is not a law firm and does not provide legal advice or substitute for review by a licensed attorney.
    </div>

    <h2>1. Zero Training on Your Agreements</h2>
    <p>Agreements, clauses, and security questionnaires submitted through the ClauseGuard Review Desk or via the Claude and ChatGPT MCP connectors are processed strictly in ephemeral memory to generate your requested checklist comparison and Word Track Changes document. Your content is never used to train, fine-tune, or improve any artificial intelligence or foundation models (<code>trains_on_customer_data: false</code>).</p>

    <h2>2. Data Collected &amp; Current MCP Tool Inputs and Outputs</h2>
    <p>ClauseGuard collects only the minimum data required to execute the specific tool you invoke:</p>
    <div tabindex="0" role="region" aria-labelledby="cg-privacy-tools-caption" class="table-wrapper">
      <table>
        <caption id="cg-privacy-tools-caption">ClauseGuard MCP Tool Inputs, Outputs, and Data Handling</caption>
        <thead>
          <tr><th scope="col">Tool Name</th><th scope="col">Tool Inputs Collected</th><th scope="col">Tool Outputs Returned</th><th scope="col">Retention &amp; Storage</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row"><code>audit_and_redline_contract</code></th><td><code>contract_text</code> (or <code>docx_base64</code>), <code>playbook</code> (<code>founder_friendly</code>, <code>saas_vendor</code>, <code>gdpr_dpa</code>, <code>hipaa_baa</code>), optional <code>contract_name</code>, <code>author</code>, and optional <code>api_key</code>.</td><td>0–100 commercial checklist variance score, clause-by-clause suggested Track Changes wording, counterparty email draft, non-legal-advice disclaimer, and ephemeral <code>.docx</code> download URL.</td><td>Input text processed statelessly in RAM; generated <code>.docx</code> held in a bounded in-memory LRU cache (max 60 files) for immediate download and cleared automatically.</td></tr>
          <tr><th scope="row"><code>autofill_security_questionnaire</code></th><td><code>items</code> (list of security/privacy question IDs and question strings), optional <code>profile</code> posture overrides, and optional <code>api_key</code>.</td><td>Plain-English draft security answers, control evidence citations, confidence scores, and informational disclaimer.</td><td>100% stateless in-memory execution; zero database persistence after HTTP response completes.</td></tr>
          <tr><th scope="row"><code>compare_contract_versions</code></th><td><code>version_a_text</code> (baseline draft), <code>version_b_text</code> (revised draft), optional draft labels, and optional <code>api_key</code>.</td><td>Clause-by-clause text diff summary highlighting commercial shifts (liability, payment terms, renewal, governing law) and informational disclaimer.</td><td>100% stateless in-memory execution; zero database persistence after HTTP response completes.</td></tr>
        </tbody>
      </table>
    </div>
    <p><strong>Technical Metadata:</strong> Standard HTTP request headers (caller IP address or <code>X-Client-Id</code>, user-agent, and optional Pro API key) are processed in memory to enforce monthly free/paid quota limits and protect against abuse.</p>

    <h2>3. Purposes of Data Processing</h2>
    <ul>
      <li><strong>Tool Execution:</strong> Comparing submitted agreement text against your selected commercial checklist, formatting OpenXML Microsoft Word (<code>.docx</code>) Track Changes files, comparing draft versions, and drafting security questionnaire responses.</li>
      <li><strong>Quota &amp; Abuse Prevention:</strong> Metering the complimentary tier (1 agreement comparison/month per client) versus the Professional Plan.</li>
      <li><strong>Security &amp; Reliability:</strong> Enforcing payload size limits (5 MB max), blocking malformed archives, and maintaining service uptime.</li>
    </ul>

    <h2>4. Recipients &amp; Third-Party Subprocessors</h2>
    <p>We never sell, rent, or share your agreements or tool inputs with advertisers or data brokers. Infrastructure subprocessors are limited to:</p>
    <ul>
      <li><strong>Railway Corp. (United States):</strong> Encrypted cloud container hosting where the stateless FastAPI MCP server executes in memory.</li>
      <li><strong>Stripe, Inc. (United States):</strong> Payment processing only if you voluntarily purchase a Professional Plan subscription via Stripe Checkout. ClauseGuard never sees or stores raw payment card numbers.</li>
    </ul>

    <h2>5. Data Retention &amp; Ephemeral Document Handling</h2>
    <p>Submitted contract text, draft comparisons, and questionnaire items are processed in volatile memory (RAM) for the duration of the HTTP request and are not written to disk or persistent databases. Generated Microsoft Word (<code>.docx</code>) files with Track Changes are held temporarily in a bounded in-memory ring buffer (capped at 60 artifacts) solely so you can click the download link during your active session, and are automatically evicted as new files are generated or when the container restarts.</p>

    <h2>6. User Controls, Deletion &amp; Privacy Rights (GDPR / CCPA)</h2>
    <ul>
      <li><strong>Input Redaction Control:</strong> You may anonymize party names, addresses, or financial figures before submitting text to any tool.</li>
      <li><strong>Local Browser Controls:</strong> Web Desk users can clear saved workspace preferences or API keys at any time using the <em>Clear</em> button or by clearing browser <code>localStorage</code>.</li>
      <li><strong>Access, Deletion &amp; Opt-Out Requests:</strong> To request immediate eviction of an in-memory <code>.docx</code> artifact, deletion of billing metadata, or exercise GDPR/CCPA data rights, email <strong>Kader Mula</strong> at <a href="mailto:mulak1@gmail.com">mulak1@gmail.com</a>. Requests are fulfilled within 24 hours.</li>
    </ul>

    <h2>7. Security &amp; Encryption</h2>
    <p>All connections use HTTPS (TLS 1.3) encryption in transit with HSTS, Content-Security-Policy, and XXE/zip-bomb protections, and OAuth 2.1 with S256 PKCE verification.</p>""",
    )


def render_docs_html() -> str:
    """Return the Public User & IT Administrator Documentation page for Claude/ChatGPT MCP review."""
    return _static_page_shell(
        "User &amp; IT Admin Documentation — ClauseGuard: Contract Redlines",
        """<p><a href="/">← Return to ClauseGuard Review Desk</a></p>
    <h1>User &amp; IT Administrator Documentation</h1>
    <p><strong>Connector Name:</strong> ClauseGuard: Contract Redlines<br/>
    <strong>Remote MCP Endpoint:</strong> <code>https://clauseguard-mcp-production.up.railway.app/mcp</code><br/>
    <strong>Support Contact:</strong> <a href="mailto:mulak1@gmail.com">mulak1@gmail.com</a></p>
    <div class="disclaimer-box">
      <strong>Informational Commercial Checklist Only — Not Legal Advice:</strong> ClauseGuard is an automated commercial document comparison and Microsoft Word (<code>.docx</code>) Track Changes formatting utility. It is not a law firm and does not provide legal advice or substitute for review by a licensed attorney.
    </div>
    <h2>1. Overview for End Users &amp; Commercial Operations Teams</h2>
    <p>ClauseGuard connects directly to Claude and ChatGPT to compare commercial agreement drafts (MSAs, Mutual NDAs, SaaS Subscriptions, Data Processing Addendums, and HIPAA BAAs) against plain-English commercial checklists. It returns clause-by-clause checklist variance scores, suggested balanced replacement wording, a draft counterparty discussion note, and a downloadable Microsoft Word (<code>.docx</code>) file with native Track Changes for review with your qualified legal counsel.</p>
    <h2>2. Security &amp; IT Administrator Review Summary</h2>
    <ul>
      <li><strong>100% Read-Only &amp; Idempotent Tools:</strong> All three exposed MCP tools (<code>audit_and_redline_contract</code>, <code>autofill_security_questionnaire</code>, and <code>compare_contract_versions</code>) are strictly stateless, read-only (<code>readOnlyHint: true</code>), and non-destructive (<code>destructiveHint: false</code>). The connector cannot mutate, delete, or modify any external systems or user records.</li>
      <li><strong>Zero Model Training &amp; Ephemeral Memory:</strong> Submitted contract text and generated <code>.docx</code> Track Changes artifacts are processed in ephemeral memory solely to fulfill the immediate request. No customer contracts or questionnaires are stored in persistent databases or used to train AI models.</li>
      <li><strong>Transport &amp; Authentication Security:</strong> All traffic is encrypted over HTTPS (TLS 1.3). The server supports open read-only evaluation as well as OAuth 2.1 with S256 PKCE discovery at <code>/.well-known/oauth-authorization-server</code>.</li>
    </ul>
    <h2>3. Included MCP Tools &amp; Scope</h2>
    <div tabindex="0" role="region" aria-labelledby="cg-docs-tools-caption" class="table-wrapper">
      <table>
        <caption id="cg-docs-tools-caption">ClauseGuard MCP Tools and Read-Only Permission Scope</caption>
        <thead><tr><th scope="col">Tool Name</th><th scope="col">Permission Scope</th><th scope="col">Description</th></tr></thead>
        <tbody>
          <tr><th scope="row"><code>audit_and_redline_contract</code></th><td>Read-Only · Idempotent</td><td>Compares commercial contract drafts against a checklist (<code>founder_friendly</code>, <code>saas_vendor</code>, <code>gdpr_dpa</code>, or <code>hipaa_baa</code>), calculates a 0–100 checklist variance score, drafts a counterparty note, and formats a downloadable Microsoft Word (<code>.docx</code>) file with Track Changes (informational checklist only — not legal advice).</td></tr>
          <tr><th scope="row"><code>autofill_security_questionnaire</code></th><td>Read-Only · Idempotent</td><td>Drafts plain-English security and privacy responses and evidence citations across SOC 2 Type II, GDPR, HIPAA, ISO 27001, encryption, incident response, and access control.</td></tr>
          <tr><th scope="row"><code>compare_contract_versions</code></th><td>Read-Only · Idempotent</td><td>Compares two contract drafts clause-by-clause and highlights commercial changes in liability caps, payment windows, governing law, auto-renewal, and indemnity.</td></tr>
        </tbody>
      </table>
    </div>
    <h2>4. Example Prompts in Claude &amp; ChatGPT</h2>
    <ul>
      <li><em>"Use ClauseGuard to compare this vendor MSA against the founder_friendly checklist and give me the download link for the redlined Word (.docx) file."</em></li>
      <li><em>"Compare our original draft against the vendor's returned markup using ClauseGuard and flag any changes to liability or payment terms."</em></li>
      <li><em>"Use ClauseGuard to complete these 5 customer security questionnaire items."</em></li>
    </ul>
    <h2>5. Policies &amp; Support</h2>
    <ul>
      <li><strong>About ClauseGuard:</strong> <a href="/about">https://clauseguard-mcp-production.up.railway.app/about</a></li>
      <li><strong>Privacy &amp; Confidentiality Policy:</strong> <a href="/privacy">https://clauseguard-mcp-production.up.railway.app/privacy</a></li>
      <li><strong>Terms of Service:</strong> <a href="/terms">https://clauseguard-mcp-production.up.railway.app/terms</a></li>
      <li><strong>GitHub Repository:</strong> <a href="https://github.com/mulak1/clauseguard-mcp">https://github.com/mulak1/clauseguard-mcp</a></li>
      <li><strong>Support Email:</strong> <a href="mailto:mulak1@gmail.com">mulak1@gmail.com</a></li>
    </ul>""",
    )


def render_about_html() -> str:
    """Return the About & Company Information page for ClauseGuard."""
    return _static_page_shell(
        "About ClauseGuard — Commercial Playbook Comparison &amp; Word Redlines",
        """<p><a href="/">← Return to ClauseGuard Review Desk</a></p>
    <h1>About ClauseGuard</h1>
    <p><strong>ClauseGuard</strong> builds plain-English commercial contract checklist comparison, Microsoft Word (<code>.docx</code>) Track Changes formatting, and security questionnaire tools designed to work both as a standalone commercial document comparison desk and natively inside AI assistants via the Model Context Protocol (MCP).</p>
    <div class="disclaimer-box">
      <strong>Informational Commercial Checklist Only — Not Legal Advice:</strong> ClauseGuard is an automated software utility, not a law firm, and does not provide legal advice, legal opinions, or attorney representation. Always review agreements with qualified legal counsel.
    </div>
    <h2>Our Mission</h2>
    <p>Founders, procurement leads, deal desks, and operations teams spend hours manually formatting standard commercial agreements—Master Services Agreements (MSAs), Mutual NDAs, Data Processing Addendums (DPAs), and Business Associate Agreements (BAAs). ClauseGuard gives every team instant, playbook-guided checklist comparisons, balanced fallback wording, counterparty discussion notes, and native Microsoft Word (<code>.docx</code>) Track Changes to review with their counsel.</p>
    <h2>Privacy &amp; Security by Design</h2>
    <ul>
      <li><strong>Zero Model Training:</strong> We never train AI models on customer agreements or security questionnaires.</li>
      <li><strong>Read-Only &amp; Ephemeral Architecture:</strong> All MCP tools are stateless and read-only, and generated Word Track Changes documents are held only in ephemeral memory for download.</li>
      <li><strong>Open Standards:</strong> Built on the Model Context Protocol (MCP) and OpenXML WordprocessingML standards so your redlines open cleanly in Microsoft Word, Google Docs, and Apple Pages.</li>
    </ul>
    <h2>Company &amp; Leadership</h2>
    <ul>
      <li><strong>Organization:</strong> ClauseGuard</li>
      <li><strong>Founder &amp; Creator:</strong> Kader Mula</li>
      <li><strong>Website:</strong> <a href="https://clauseguard-mcp-production.up.railway.app">https://clauseguard-mcp-production.up.railway.app</a></li>
      <li><strong>Documentation:</strong> <a href="/docs">https://clauseguard-mcp-production.up.railway.app/docs</a></li>
      <li><strong>GitHub:</strong> <a href="https://github.com/mulak1/clauseguard-mcp">https://github.com/mulak1/clauseguard-mcp</a></li>
      <li><strong>Contact &amp; Support:</strong> <a href="mailto:mulak1@gmail.com">mulak1@gmail.com</a></li>
    </ul>""",
    )


def render_terms_html() -> str:
    """Return the plain-English Terms of Service & Legal Disclaimer page."""
    return _static_page_shell(
        "Terms of Service &amp; Disclaimer — ClauseGuard",
        """<p><a href="/">Return to ClauseGuard Review Desk</a></p>
    <h1>Terms of Service &amp; Review Disclaimer</h1>
    <p><strong>Effective Date:</strong> November 2, 2026</p>
    <h2>1. Decision Support — You Remain in Control</h2>
    <p>ClauseGuard provides automated commercial contract benchmarking, suggested redlines, and Microsoft Word Track Changes exports based on standard commercial playbooks. ClauseGuard is a software review assistant, not a law firm, and does not provide formal legal representation or create an attorney-client relationship.</p>
    <h2>2. Reviewer Sovereignty</h2>
    <p>Every suggested revision is presented as a transparent Track Change so you or your legal counsel can accept, modify, or reject each edit before sending an agreement to a counterparty.</p>
    <h2>3. Service Plans</h2>
    <p>The Complimentary Plan includes 1 agreement review and Word Track Changes export per month. The Professional Plan ($49/month) provides unlimited agreement reviews, custom redline exports, draft comparisons, and security questionnaire automation.</p>""",
    )
