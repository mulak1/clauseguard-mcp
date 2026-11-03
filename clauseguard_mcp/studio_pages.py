"""Client-side interactive workflow script and Privacy/Terms pages for ClauseGuard MCP."""

from __future__ import annotations


def render_privacy_html() -> str:
    """Return the plain-English Privacy & Confidentiality Policy page required for store submission."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="icon" type="image/png" href="/icon.png" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Privacy &amp; Confidentiality Policy — ClauseGuard</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif:wght@400&display=swap" rel="stylesheet">
  <style>
    body { font-family:'Instrument Sans',system-ui,sans-serif; background:#f9f9f9; color:#1f201d; margin:0; padding:3rem 1.5rem; line-height:1.65; font-size:16px; }
    main { max-width:760px; margin:0 auto; background:#ffffff; border-radius:22px; padding:2.5rem; }
    h1 { font-family:'Instrument Serif',Georgia,serif; font-size:2.4rem; font-weight:400; margin:0 0 0.5rem; }
    h2 { font-size:1.1rem; margin:1.75rem 0 0.5rem; color:#1b6e66; }
    p, li { font-size:1rem; color:#1f201d; max-width:65ch; }
    a { color:#1b6e66; text-decoration:none; font-weight:500; }
  </style>
</head>
<body>
  <main>
    <p><a href="/">Return to ClauseGuard Review Desk</a></p>
    <h1>Privacy &amp; Confidentiality Policy</h1>
    <p><strong>Effective Date:</strong> November 2, 2026. Your agreements belong strictly to you. We never train AI models on your contracts, and we never sell or share your documents.</p>
    <h2>1. Zero Training on Your Agreements</h2>
    <p>Agreements, clauses, and security questionnaires submitted through the ClauseGuard Review Desk or via the Claude and ChatGPT connectors are processed solely to generate your requested review and Word Track Changes document. Your content is never used to train, fine-tune, or improve foundation models.</p>
    <h2>2. Ephemeral Document Handling</h2>
    <p>Generated Microsoft Word (<code>.docx</code>) files with Track Changes are held temporarily in memory solely so you can download them during your active session. We do not maintain permanent archives of your confidential commercial contracts.</p>
    <h2>3. Security &amp; Encryption</h2>
    <p>All connections use TLS 1.3 encryption in transit, and authentication via Claude and ChatGPT uses OAuth 2.1 with S256 PKCE verification.</p>
    <h2>4. Contact</h2>
    <p>Questions regarding privacy, security, or IT administrator reviews may be directed to <strong>mulak1@gmail.com</strong>.</p>
  </main>
</body>
</html>"""


def render_docs_html() -> str:
    """Return the Public User & IT Administrator Documentation page for Claude/ChatGPT MCP review."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="icon" type="image/png" href="/icon.png" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>User &amp; IT Admin Documentation — ClauseGuard: Contract Redlines</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif:wght@400&display=swap" rel="stylesheet">
  <style>
    body { font-family:'Instrument Sans',system-ui,sans-serif; background:#f9f9f9; color:#1f201d; margin:0; padding:3rem 1.5rem; line-height:1.65; font-size:16px; }
    main { max-width:820px; margin:0 auto; background:#ffffff; border-radius:22px; padding:2.75rem; }
    h1 { font-family:'Instrument Serif',Georgia,serif; font-size:2.4rem; font-weight:400; margin:0 0 0.5rem; }
    h2 { font-size:1.15rem; margin:2rem 0 0.55rem; color:#1b6e66; }
    p, li { font-size:1rem; color:#1f201d; max-width:68ch; }
    code { background:#f3f3f2; padding:0.15rem 0.4rem; border-radius:6px; font-size:0.9rem; }
    table { width:100%; border-collapse:collapse; margin:1rem 0; font-size:0.94rem; }
    th, td { text-align:left; padding:0.65rem 0.75rem; border-bottom:1px solid #e7e7e5; vertical-align:top; }
    th { font-weight:600; color:#1b6e66; background:#f9f9f9; }
    a { color:#1b6e66; text-decoration:none; font-weight:500; }
  </style>
</head>
<body>
  <main>
    <p><a href="/">← Return to ClauseGuard Review Desk</a></p>
    <h1>User &amp; IT Administrator Documentation</h1>
    <p><strong>Connector Name:</strong> ClauseGuard: Contract Redlines<br/>
    <strong>Remote MCP Endpoint:</strong> <code>https://clauseguard-mcp-production.up.railway.app/mcp</code><br/>
    <strong>Support Contact:</strong> <a href="mailto:mulak1@gmail.com">mulak1@gmail.com</a></p>

    <h2>1. Overview for End Users &amp; Legal Teams</h2>
    <p>ClauseGuard connects directly to Claude and ChatGPT to review commercial agreements (MSAs, Mutual NDAs, SaaS Subscriptions, Data Processing Agreements, and HIPAA BAAs) against plain-English negotiation playbooks. It returns clause-by-clause risk ratings, balanced replacement wording, a ready-to-send negotiation email, and a downloadable Microsoft Word (<code>.docx</code>) file with native Track Changes.</p>

    <h2>2. Security &amp; IT Administrator Review Summary</h2>
    <ul>
      <li><strong>100% Read-Only &amp; Idempotent Tools:</strong> All three exposed MCP tools (<code>audit_and_redline_contract</code>, <code>autofill_security_questionnaire</code>, and <code>compare_contract_versions</code>) are strictly stateless, read-only (<code>readOnlyHint: true</code>), and non-destructive (<code>destructiveHint: false</code>). The connector cannot mutate, delete, or modify any external systems or user records.</li>
      <li><strong>Zero Model Training &amp; Ephemeral Memory:</strong> Submitted contract text and generated <code>.docx</code> Track Changes artifacts are processed in ephemeral memory solely to fulfill the immediate request. No customer contracts or questionnaires are stored in persistent databases or used to train AI models.</li>
      <li><strong>Transport &amp; Authentication Security:</strong> All traffic is encrypted over HTTPS (TLS 1.3). The server supports open read-only evaluation as well as OAuth 2.1 with S256 PKCE discovery at <code>/.well-known/oauth-authorization-server</code>.</li>
    </ul>

    <h2>3. Included MCP Tools &amp; Scope</h2>
    <table>
      <thead>
        <tr><th>Tool Name</th><th>Permission Scope</th><th>Description</th></tr>
      </thead>
      <tbody>
        <tr>
          <td><code>audit_and_redline_contract</code></td>
          <td>Read-Only · Idempotent</td>
          <td>Reviews commercial contracts against a playbook (<code>founder_friendly</code>, <code>saas_vendor</code>, <code>gdpr_dpa</code>, or <code>hipaa_baa</code>), scores risk (0–100), drafts a negotiation email, and returns a downloadable Microsoft Word (<code>.docx</code>) file with Track Changes.</td>
        </tr>
        <tr>
          <td><code>autofill_security_questionnaire</code></td>
          <td>Read-Only · Idempotent</td>
          <td>Drafts plain-English compliance responses and evidence citations across SOC 2 Type II, GDPR, HIPAA, ISO 27001, encryption, incident response, and access control.</td>
        </tr>
        <tr>
          <td><code>compare_contract_versions</code></td>
          <td>Read-Only · Idempotent</td>
          <td>Compares two contract drafts clause-by-clause and highlights material shifts in liability caps, payment windows, governing law, auto-renewal, and indemnity.</td>
        </tr>
      </tbody>
    </table>

    <h2>4. Example Prompts in Claude</h2>
    <ul>
      <li><em>"Use ClauseGuard to review this vendor MSA using the founder_friendly playbook and give me the download link for the redlined Word (.docx) file."</em></li>
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
    </ul>
  </main>
</body>
</html>"""


def render_about_html() -> str:
    """Return the About & Company Information page for ClauseGuard."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="icon" type="image/png" href="/icon.png" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>About ClauseGuard — Commercial Contract Review &amp; Word Redlines</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif:wght@400&display=swap" rel="stylesheet">
  <style>
    body { font-family:'Instrument Sans',system-ui,sans-serif; background:#f9f9f9; color:#1f201d; margin:0; padding:3rem 1.5rem; line-height:1.65; font-size:16px; }
    main { max-width:780px; margin:0 auto; background:#ffffff; border-radius:22px; padding:2.75rem; }
    h1 { font-family:'Instrument Serif',Georgia,serif; font-size:2.4rem; font-weight:400; margin:0 0 0.5rem; }
    h2 { font-size:1.15rem; margin:1.85rem 0 0.5rem; color:#1b6e66; }
    p, li { font-size:1rem; color:#1f201d; max-width:66ch; }
    a { color:#1b6e66; text-decoration:none; font-weight:500; }
  </style>
</head>
<body>
  <main>
    <p><a href="/">← Return to ClauseGuard Review Desk</a></p>
    <h1>About ClauseGuard</h1>
    <p><strong>ClauseGuard</strong> builds plain-English commercial contract review, redlining, and security questionnaire tools designed to work both as a standalone legal review desk and natively inside AI assistants via the Model Context Protocol (MCP).</p>

    <h2>Our Mission</h2>
    <p>Founders, legal counsel, procurement leads, and revenue teams spend hours manually marking up standard commercial agreements—Master Services Agreements (MSAs), Mutual NDAs, Data Processing Agreements (DPAs), and HIPAA Business Associate Agreements (BAAs). ClauseGuard gives every team instant, playbook-guided risk scoring, balanced fallback wording, negotiation emails, and native Microsoft Word (<code>.docx</code>) Track Changes without requiring an enterprise CLM contract.</p>

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
    </ul>
  </main>
</body>
</html>"""


def render_terms_html() -> str:
    """Return the plain-English Terms of Service & Legal Disclaimer page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="icon" type="image/png" href="/icon.png" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Terms of Service &amp; Disclaimer — ClauseGuard</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif:wght@400&display=swap" rel="stylesheet">
  <style>
    body { font-family:'Instrument Sans',system-ui,sans-serif; background:#f9f9f9; color:#1f201d; margin:0; padding:3rem 1.5rem; line-height:1.65; font-size:16px; }
    main { max-width:760px; margin:0 auto; background:#ffffff; border-radius:22px; padding:2.5rem; }
    h1 { font-family:'Instrument Serif',Georgia,serif; font-size:2.4rem; font-weight:400; margin:0 0 0.5rem; }
    h2 { font-size:1.1rem; margin:1.75rem 0 0.5rem; color:#1b6e66; }
    p { font-size:1rem; color:#1f201d; max-width:65ch; }
    a { color:#1b6e66; text-decoration:none; font-weight:500; }
  </style>
</head>
<body>
  <main>
    <p><a href="/">Return to ClauseGuard Review Desk</a></p>
    <h1>Terms of Service &amp; Review Disclaimer</h1>
    <p><strong>Effective Date:</strong> November 2, 2026</p>
    <h2>1. Decision Support — You Remain in Control</h2>
    <p>ClauseGuard provides automated commercial contract benchmarking, suggested redlines, and Microsoft Word Track Changes exports based on standard commercial playbooks. ClauseGuard is a software review assistant, not a law firm, and does not provide formal legal representation or create an attorney-client relationship.</p>
    <h2>2. Reviewer Sovereignty</h2>
    <p>Every suggested revision is presented as a transparent Track Change so you or your legal counsel can accept, modify, or reject each edit before sending an agreement to a counterparty.</p>
    <h2>3. Service Plans</h2>
    <p>The Complimentary Plan includes 1 agreement review and Word Track Changes export per month. The Professional Plan ($49/month) provides unlimited agreement reviews, custom redline exports, draft comparisons, and security questionnaire automation.</p>
  </main>
</body>
</html>"""


STUDIO_CLIENT_JS = """
let SAMPLE_DATA = null;
let CURRENT_AUDIT = null;
let CLAUSE_DECISIONS = {};
let ACTIVE_FILTER = 'all';

function setTimeGreeting() {
  const hr = new Date().getHours();
  const period = hr < 12 ? 'Good morning' : (hr < 18 ? 'Good afternoon' : 'Good evening');
  const el = document.getElementById('greetingHeadline');
  if (el) el.textContent = `${period}. Let's review your agreement.`;
}

async function initStudio() {
  setTimeGreeting();
  if (window.location.search.includes('pro_activated=1') || localStorage.getItem('cg_pro_active') === '1') {
    localStorage.setItem('cg_pro_active', '1');
    activateProKey();
  }
  const r = await fetch('/api/samples');
  SAMPLE_DATA = await r.json();
  renderQuestionnaireCards(SAMPLE_DATA.questionnaire);
  document.getElementById('questItemsArea').value = JSON.stringify(SAMPLE_DATA.questionnaire, null, 2);
  document.getElementById('versionAText').value = SAMPLE_DATA.diff_versions.version_a_text;
  document.getElementById('versionBText').value = SAMPLE_DATA.diff_versions.version_b_text;
  await loadSampleContract('predatory_msa');
  if (window.location.search.includes('pro_activated=1')) {
    const sub = document.getElementById('contextualStepGreeting');
    if (sub) {
      sub.innerHTML = '<strong style="color:var(--positive);">✓ Payment confirmed — Professional Plan Unlocked!</strong> Unlimited agreement reviews and Word (.docx) Track Changes are now active in this browser. Your permanent access key (<code>cg_pro_studio_unlimited_2026</code>) has also been saved to your workspace below.';
    }
  }
}

function renderQuestionnaireCards(items) {
  const box = document.getElementById('questFriendlyList');
  if (!box) return;
  box.innerHTML = items.map((it, i) => `
    <div style="display:flex;gap:0.65rem;align-items:center;padding:0.55rem 0.75rem;background:#ffffff;border-radius:12px;margin-bottom:0.45rem;">
      <span style="font-size:0.84rem;font-weight:600;color:var(--accent);min-width:64px;">${it.id}</span>
      <input value="${it.question.replace(/"/g, '&quot;')}" onchange="updateQuestItem(${i}, this.value)" style="background:transparent;padding:0.25rem;font-size:0.92rem;width:100%;" />
    </div>
  `).join('');
}

function updateQuestItem(idx, newVal) {
  const arr = JSON.parse(document.getElementById('questItemsArea').value);
  if (arr[idx]) {
    arr[idx].question = newVal;
    document.getElementById('questItemsArea').value = JSON.stringify(arr, null, 2);
  }
}

function switchTab(tab) {
  ['audit', 'quest', 'diff'].forEach(t => {
    const cap = t.charAt(0).toUpperCase() + t.slice(1);
    document.getElementById('panel' + cap).style.display = (t === tab) ? 'block' : 'none';
    document.getElementById('tabBtn' + cap).classList.toggle('active', t === tab);
  });
  const greetSub = document.getElementById('contextualStepGreeting');
  if (tab === 'audit') {
    greetSub.textContent = 'Welcome to your Contract Review Desk. Select a sample agreement, upload a Word (.docx) file, or paste your draft on the left, then customize and export your tracked redlines on the right.';
  } else if (tab === 'quest') {
    greetSub.textContent = 'Welcome to the Security & Privacy Questionnaire Desk. Customize your organization profile and generate clear, audit-ready answers in one click.';
    runQuestionnaireTool();
  } else {
    greetSub.textContent = 'Welcome to the Draft Comparison Desk. Compare your initial agreement against the other side\\'s returned markup to see which changes shift financial or legal risk.';
    runCompareTool();
  }
}

function copyMcpUrl() {
  navigator.clipboard.writeText('http://localhost:8792/mcp');
  const btn = document.getElementById('copyMcpBtn');
  if (btn) { btn.textContent = 'Copied URL'; setTimeout(() => { btn.textContent = 'Copy Assistant URL'; }, 2000); }
}

function activateProKey() {
  document.getElementById('apiKeyInput').value = 'cg_pro_studio_unlimited_2026';
  document.getElementById('planBadgeText').textContent = '✓ Professional Plan Active ($49.99)';
  const hLink = document.getElementById('headerUpgradeLink');
  if (hLink) hLink.style.display = 'none';
  const dLink = document.getElementById('drawerUpgradeLink');
  if (dLink) dLink.style.display = 'none';
}

function applyManualKey() {
  const val = document.getElementById('apiKeyInput').value.trim();
  if (val.startsWith('cg_pro_')) {
    localStorage.setItem('cg_pro_active', '1');
    document.getElementById('planBadgeText').textContent = '✓ Professional Plan Active ($49.99)';
    const hLink = document.getElementById('headerUpgradeLink');
    if (hLink) hLink.style.display = 'none';
    const dLink = document.getElementById('drawerUpgradeLink');
    if (dLink) dLink.style.display = 'none';
    runAuditTool();
  } else {
    clearProKey();
  }
}

function clearProKey() {
  localStorage.removeItem('cg_pro_active');
  document.getElementById('apiKeyInput').value = '';
  document.getElementById('planBadgeText').textContent = 'Complimentary Plan (1 Review / Month)';
  const hLink = document.getElementById('headerUpgradeLink');
  if (hLink) hLink.style.display = 'inline';
  const dLink = document.getElementById('drawerUpgradeLink');
  if (dLink) dLink.style.display = 'inline-flex';
}

async function handleFileUpload(inputEl) {
  const file = inputEl.files && inputEl.files[0];
  if (!file) return;
  document.getElementById('contractNameInput').value = file.name.endsWith('.docx') ? file.name : (file.name + '.docx');
  const statusEl = document.getElementById('auditStatus');
  if (file.name.endsWith('.docx')) {
    statusEl.textContent = `Reading ${file.name}...`;
    const buf = await file.arrayBuffer();
    const bytes = new Uint8Array(buf);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
    const b64 = btoa(binary);
    const r = await fetch('/api/extract-docx', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ docx_base64: b64 })
    });
    const d = await r.json();
    if (r.ok && d.text) {
      document.getElementById('contractTextArea').value = d.text;
      statusEl.textContent = `Loaded ${file.name}. Running review...`;
      await runAuditTool();
    } else {
      statusEl.textContent = d.error || 'Could not read .docx file.';
    }
  } else {
    const text = await file.text();
    document.getElementById('contractTextArea').value = text;
    await runAuditTool();
  }
}

async function loadSampleContract(key) {
  switchTab('audit');
  if (!SAMPLE_DATA) return;
  const item = SAMPLE_DATA.contracts[key];
  document.getElementById('contractTextArea').value = item.text;
  document.getElementById('playbookSelect').value = item.playbook;
  document.getElementById('contractNameInput').value = item.name;
  document.querySelectorAll('.sample-btn').forEach(b => b.classList.remove('active-sample'));
  const activeBtn = document.getElementById('sampleBtn_' + key);
  if (activeBtn) activeBtn.classList.add('active-sample');
  await runAuditTool();
}

function loadQuestionnaireSample() { switchTab('quest'); }
function loadDiffSample() { switchTab('diff'); }

async function runAuditTool() {
  const statusEl = document.getElementById('auditStatus');
  statusEl.textContent = 'Reviewing clauses...';
  const headers = {
    'Content-Type': 'application/json',
    'X-Client-Id': document.getElementById('clientIdInput').value || 'workspace-guest'
  };
  const apiKey = document.getElementById('apiKeyInput').value.trim();
  if (apiKey) headers['X-ClauseGuard-Key'] = apiKey;

  const body = {
    contract_text: document.getElementById('contractTextArea').value,
    playbook: document.getElementById('playbookSelect').value,
    contract_name: document.getElementById('contractNameInput').value,
    author: document.getElementById('reviewerNameInput').value || 'ClauseGuard Legal Desk'
  };

  const resp = await fetch('/api/audit', { method: 'POST', headers, body: JSON.stringify(body) });
  const data = await resp.json();
  const mcpBox = document.getElementById('mcpJsonBox');
  if (mcpBox) mcpBox.textContent = JSON.stringify(data, null, 2);
  statusEl.textContent = '';

  if (!resp.ok) {
    document.getElementById('visualOutput').innerHTML = `
      <div class="redline-card" style="background:var(--pill-negative-bg);">
        <div class="redline-header"><span style="color:var(--pill-negative-ink);font-weight:600;">Complimentary Review Limit Reached</span></div>
        <p style="font-size:0.95rem;color:var(--text);margin-bottom:0.75rem;">${data.error}</p>
        <div style="display:flex;gap:0.65rem;flex-wrap:wrap;align-items:center;">
          <a href="https://buy.stripe.com/3cI7sL5hz4JVccl4k2fAc00" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;padding:0.55rem 1.05rem;border-radius:10px;background:var(--accent);color:#ffffff;font-weight:600;text-decoration:none;font-size:0.9rem;">Upgrade to Professional Plan ($49.99 via Stripe) →</a>
        </div>
      </div>`;
    return;
  }

  CURRENT_AUDIT = data.audit;
  CLAUSE_DECISIONS = {};
  CURRENT_AUDIT.findings.forEach(f => {
    CLAUSE_DECISIONS[f.clause_id] = { mode: 'standard', customText: f.proposed_redline };
  });
  renderAuditWorkspace(data.quota);
}

function setClauseDecision(clauseId, mode) {
  if (!CURRENT_AUDIT || !CLAUSE_DECISIONS[clauseId]) return;
  const finding = CURRENT_AUDIT.findings.find(f => f.clause_id === clauseId);
  CLAUSE_DECISIONS[clauseId].mode = mode;
  if (mode === 'standard' && finding) CLAUSE_DECISIONS[clauseId].customText = finding.proposed_redline;
  if (mode === 'compromise' && finding) CLAUSE_DECISIONS[clauseId].customText = finding.compromise_redline || finding.proposed_redline;
  renderAuditWorkspace();
}

function updateCustomClauseText(clauseId, val) {
  if (CLAUSE_DECISIONS[clauseId]) {
    CLAUSE_DECISIONS[clauseId].customText = val;
  }
}

function setFilter(filterVal) {
  ACTIVE_FILTER = filterVal;
  renderAuditWorkspace();
}

function copyCounterpartyEmail() {
  const el = document.getElementById('counterpartyEmailBox');
  if (!el) return;
  navigator.clipboard.writeText(el.value);
  const btn = document.getElementById('copyEmailBtn');
  if (btn) { btn.textContent = 'Copied Email Note'; setTimeout(() => { btn.textContent = 'Copy Polite Email to Counterparty'; }, 2000); }
}

async function downloadCustomizedDocx() {
  if (!CURRENT_AUDIT) return;
  const accepted = [];
  CURRENT_AUDIT.findings.forEach(f => {
    const dec = CLAUSE_DECISIONS[f.clause_id] || { mode: 'standard' };
    if (dec.mode !== 'dismissed') {
      const replacement = dec.mode === 'compromise'
        ? (f.compromise_redline || f.proposed_redline)
        : (dec.mode === 'custom' ? dec.customText : f.proposed_redline);
      accepted.push({
        clause_id: f.clause_id,
        title: f.title,
        severity: f.severity,
        original_excerpt: f.original_excerpt,
        replacement_text: replacement,
        rationale: f.rationale,
        playbook_reference: f.playbook_reference
      });
    }
  });

  const resp = await fetch('/api/docx/custom', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contract_name: CURRENT_AUDIT.contract_name,
      playbook: CURRENT_AUDIT.playbook,
      risk_score: CURRENT_AUDIT.risk_score,
      risk_level: CURRENT_AUDIT.risk_level,
      contract_text: document.getElementById('contractTextArea').value,
      accepted_redlines: accepted,
      author: document.getElementById('reviewerNameInput').value || 'ClauseGuard Legal Desk'
    })
  });
  const d = await resp.json();
  if (resp.ok && d.download_url) {
    window.location.href = d.download_url;
  }
}

function renderAuditWorkspace() {
  const res = CURRENT_AUDIT;
  if (!res) return;

  let activeAcceptedCount = 0;
  let remainingRiskPoints = 0;
  res.findings.forEach(f => {
    const dec = CLAUSE_DECISIONS[f.clause_id] || { mode: 'standard' };
    if (dec.mode === 'dismissed') {
      remainingRiskPoints += f.risk_points;
    } else {
      activeAcceptedCount += 1;
      remainingRiskPoints += (dec.mode === 'compromise' ? Math.round(f.risk_points * 0.25) : 4);
    }
  });
  const postRedlineScore = res.findings.length === 0 ? res.risk_score : Math.min(100, Math.max(8, remainingRiskPoints));

  document.getElementById('kpiInitialVal').textContent = `${res.risk_score}/100`;
  document.getElementById('kpiInitialCap').textContent = `${res.risk_level} initial risk exposure —Initial Draft Risk`;
  document.getElementById('kpiPostVal').textContent = `${postRedlineScore}/100`;
  document.getElementById('kpiPostCap').textContent = `${activeAcceptedCount} of ${res.findings.length} revisions applied —After Your Redlines`;
  document.getElementById('kpiStandardVal').textContent = res.playbook_label;
  document.getElementById('kpiStandardCap').textContent = res.contract_name;

  const filteredFindings = res.findings.filter(f => {
    if (ACTIVE_FILTER === 'critical') return f.severity === 'CRITICAL' || f.severity === 'HIGH';
    if (ACTIVE_FILTER === 'moderate') return f.severity === 'MODERATE' || f.severity === 'LOW';
    return true;
  });

  const findingsHtml = filteredFindings.map(f => {
    const dec = CLAUSE_DECISIONS[f.clause_id] || { mode: 'standard', customText: f.proposed_redline };
    const activeReplacement = dec.mode === 'compromise'
      ? (f.compromise_redline || f.proposed_redline)
      : (dec.mode === 'custom' ? dec.customText : f.proposed_redline);

    const sevLabel = f.severity === 'CRITICAL' ? 'Needs Change Before Signing'
      : (f.severity === 'HIGH' ? 'High Priority Revision' : 'Commercial Negotiation Point');

    return `
      <div class="redline-card" style="opacity:${dec.mode === 'dismissed' ? '0.65' : '1'};">
        <div class="redline-header">
          <div>
            <div style="font-size:1.05rem;font-weight:600;color:var(--text);">${f.clause_id}: ${f.title}</div>
            <div style="font-size:0.84rem;color:var(--muted);">${f.playbook_reference}</div>
          </div>
          <span class="sev-pill sev-${f.severity}">${sevLabel}</span>
        </div>

        <p style="font-size:0.95rem;color:var(--text);margin-bottom:0.65rem;max-width:65ch;">
          <strong>In Plain English:</strong> ${f.plain_english_summary || f.rationale}
        </p>

        <div class="diff-label">Current Wording in Agreement (Marked as Strikethrough in Word)</div>
        <del class="w-del">${f.original_excerpt}</del>

        ${dec.mode === 'dismissed' ? `
          <div style="padding:0.65rem 0.85rem;background:var(--surface);border-radius:8px;font-size:0.9rem;color:var(--muted);">
            You chose to keep the original clause as written. This clause will not be redlined in your Word export.
          </div>
        ` : `
          <div class="diff-label" style="color:var(--positive);">
            ${dec.mode === 'compromise' ? 'Middle-Ground Compromise Wording (Inserted in Word Track Changes)' : 'Suggested Balanced Revision (Inserted in Word Track Changes)'}
          </div>
          ${dec.mode === 'custom' ? `
            <textarea onchange="updateCustomClauseText('${f.clause_id}', this.value)" style="min-height:92px;margin:0.35rem 0;background:#f4fbf6;">${dec.customText}</textarea>
          ` : `
            <ins class="w-ins">${activeReplacement}</ins>
          `}
        `}

        <div class="rationale">
          <strong>Why this matters:</strong> ${f.rationale}
        </div>

        <div class="decision-bar">
          <button class="chip-btn ${dec.mode === 'standard' ? 'active-chip' : ''}" onclick="setClauseDecision('${f.clause_id}', 'standard')">
            Accept Balanced Revision
          </button>
          <button class="chip-btn ${dec.mode === 'compromise' ? 'active-chip' : ''}" onclick="setClauseDecision('${f.clause_id}', 'compromise')">
            Use Middle-Ground Compromise
          </button>
          <button class="chip-btn ${dec.mode === 'custom' ? 'active-chip' : ''}" onclick="setClauseDecision('${f.clause_id}', 'custom')">
            Edit Wording Myself
          </button>
          <button class="chip-btn ${dec.mode === 'dismissed' ? 'active-chip' : ''}" onclick="setClauseDecision('${f.clause_id}', 'dismissed')">
            Keep Original Clause
          </button>
        </div>
      </div>`;
  }).join('');

  const missingHtml = (res.missing_clauses && res.missing_clauses.length > 0) ? `
    <div style="margin-top:1.25rem;padding:1.15rem 1.25rem;background:var(--pill-warning-bg);border-radius:16px;">
      <div style="font-weight:600;font-size:1rem;color:var(--pill-warning-ink);margin-bottom:0.35rem;">
        What Is Missing From This Agreement (${res.missing_clauses.length} Omitted Standard Protection${res.missing_clauses.length > 1 ? 's' : ''})
      </div>
      <p style="font-size:0.9rem;color:var(--text);margin-bottom:0.75rem;max-width:65ch;">
        Most reviews only check what is written on the page. We also checked for standard protections that were left out entirely:
      </p>
      ${res.missing_clauses.map(m => `
        <div style="background:#ffffff;border-radius:16px;padding:0.9rem;margin-bottom:0.55rem;">
          <div style="display:flex;justify-content:space-between;font-weight:600;font-size:0.94rem;">
            <span>Missing: ${m.clause_name}</span>
            <span style="font-size:0.82rem;color:var(--pill-warning-ink);">${m.importance}</span>
          </div>
          <p style="font-size:0.88rem;color:var(--muted);margin:0.25rem 0 0.45rem;max-width:65ch;">${m.why_it_matters}</p>
          <div style="font-size:0.88rem;background:var(--surface);padding:0.6rem 0.75rem;border-radius:8px;color:var(--text);">
            <strong>Suggested Addition:</strong> ${m.suggested_language}
          </div>
        </div>
      `).join('')}
    </div>
  ` : '';

  document.getElementById('visualOutput').innerHTML = `
    <div class="greeting-callout">
      <strong>Here is where this agreement stands:</strong> ${res.sign_off_recommendation}
      <div style="font-size:0.9rem;color:var(--muted);margin-top:0.25rem;max-width:65ch;">${res.executive_summary}</div>
    </div>

    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.75rem;margin:0.85rem 0;">
      <div style="font-size:0.94rem;color:var(--text);">
        <strong>You are in the driver's seat:</strong> Review, customize, or dismiss any suggestion below.
      </div>
      <div style="display:flex;gap:0.4rem;">
        <button class="chip-btn ${ACTIVE_FILTER === 'all' ? 'active-chip' : ''}" onclick="setFilter('all')">All (${res.findings.length})</button>
        <button class="chip-btn ${ACTIVE_FILTER === 'critical' ? 'active-chip' : ''}" onclick="setFilter('critical')">Must Change First</button>
        <button class="chip-btn ${ACTIVE_FILTER === 'moderate' ? 'active-chip' : ''}" onclick="setFilter('moderate')">Negotiable</button>
      </div>
    </div>

    ${findingsHtml || '<p style="color:var(--positive);padding:1rem;">No clauses matched this filter.</p>'}
    ${missingHtml}

    <div style="margin-top:1.25rem;padding:1.15rem 1.25rem;background:#ffffff;border-radius:16px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;flex-wrap:wrap;gap:0.5rem;">
        <div>
          <strong style="font-size:0.98rem;">Ready-to-Send Email Note for the Other Side</strong>
          <p style="font-size:0.86rem;color:var(--muted);">Paste this polite, collaborative note into your email when sending back the redlined Word document.</p>
        </div>
        <button class="secondary" id="copyEmailBtn" onclick="copyCounterpartyEmail()">Copy Polite Email to Counterparty</button>
      </div>
      <textarea id="counterpartyEmailBox" style="min-height:135px;background:var(--surface);font-family:var(--font);font-size:0.9rem;">${res.counterparty_email_draft || ''}</textarea>
    </div>
  `;
}

async function runQuestionnaireTool() {
  const items = JSON.parse(document.getElementById('questItemsArea').value);
  const company = document.getElementById('questCompanyInput').value;
  const rpcReq = {
    jsonrpc: '2.0', id: 101, method: 'tools/call',
    params: {
      name: 'autofill_security_questionnaire',
      arguments: {
        items,
        profile: {
          company_name: company,
          soc2_status: document.getElementById('questSoc2Input').value,
          encryption_at_rest: document.getElementById('questEncInput').value,
          breach_notification_hours: parseInt(document.getElementById('questSlaInput').value || '24', 10)
        }
      }
    }
  };
  const resp = await fetch('/mcp', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(rpcReq) });
  const rpcData = await resp.json();
  const mcpBox = document.getElementById('mcpJsonBox');
  if (mcpBox) mcpBox.textContent = JSON.stringify(rpcData, null, 2);
  const res = rpcData.result.structuredContent;
  document.getElementById('visualOutput').innerHTML = `
    <div class="greeting-callout">
      <strong>Security Questionnaire Ready:</strong> We drafted ${res.auto_completed_count} of ${res.total_items} responses for <strong>${res.company_name}</strong> (${(res.average_confidence * 100).toFixed(0)}% average confidence).
    </div>
    ${res.answers.map(a => `
      <div class="redline-card">
        <div class="redline-header">
          <span style="font-weight:600;">${a.id} — ${a.domain}</span>
          <span class="sev-pill sev-LOW">${(a.confidence * 100).toFixed(0)}% Match Confidence</span>
        </div>
        <p style="font-size:0.92rem;color:var(--muted);margin-bottom:0.4rem;max-width:65ch;"><strong>Customer Question:</strong> ${a.question}</p>
        <ins class="w-ins">${a.answer}</ins>
        <div class="rationale">Supporting Documentation: <strong>${a.evidence_refs.join(', ')}</strong></div>
      </div>`).join('')}`;
}

async function runCompareTool() {
  const rpcReq = {
    jsonrpc: '2.0', id: 102, method: 'tools/call',
    params: {
      name: 'compare_contract_versions',
      arguments: {
        version_a_text: document.getElementById('versionAText').value,
        version_b_text: document.getElementById('versionBText').value
      }
    }
  };
  const resp = await fetch('/mcp', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(rpcReq) });
  const rpcData = await resp.json();
  const mcpBox = document.getElementById('mcpJsonBox');
  if (mcpBox) mcpBox.textContent = JSON.stringify(rpcData, null, 2);
  const res = rpcData.result.structuredContent;
  document.getElementById('visualOutput').innerHTML = `
    <div class="greeting-callout">
      <strong>Draft Comparison Complete:</strong> We spotted <strong>${res.material_risk_shifts} significant risk shift(s)</strong> between your initial draft and the returned markup.
      <div style="font-size:0.9rem;color:var(--muted);margin-top:0.2rem;max-width:65ch;">${res.summary}</div>
    </div>
    ${res.diffs.map(d => `
      <div class="redline-card">
        <div class="redline-header">
          <span style="font-weight:600;">Section #${d.clause_index} — ${d.plain_title || d.risk_shift_type}</span>
          <span class="sev-pill sev-${d.severity}">${d.severity === 'CRITICAL' || d.severity === 'HIGH' ? 'Major Risk Shift' : d.change_type}</span>
        </div>
        <div class="diff-label">Your Initial Draft</div>
        <del class="w-del">${d.version_a_clause}</del>
        <div class="diff-label" style="color:var(--negative);">Counterparty's Returned Markup</div>
        <ins class="w-ins" style="border-left-color:var(--negative);background:var(--pill-negative-bg);color:var(--pill-negative-ink);">${d.version_b_clause}</ins>
        <div class="rationale"><strong>Business &amp; Legal Impact:</strong> ${d.legal_impact}</div>
      </div>`).join('')}`;
}

window.addEventListener('DOMContentLoaded', initStudio);
"""
