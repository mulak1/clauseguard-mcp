"""Editorial-Greeting Legal Workbench UI for ClauseGuard MCP (Port 8792)."""

from __future__ import annotations

from clauseguard_mcp.studio_pages import (
    STUDIO_CLIENT_JS,
    render_privacy_html,
    render_terms_html,
)

__all__ = ["render_studio_html", "render_privacy_html", "render_terms_html"]


def render_studio_html() -> str:
    """Return the Editorial-Greeting Legal Review Workbench HTML."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ClauseGuard — Commercial Contract Review, Word Track Changes &amp; Security Desk</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif:wght@400&display=swap" rel="stylesheet">
  <style>
    :root {{
      --ground: #ffffff;
      --surface: #f9f9f9;
      --raised: #ffffff;
      --control: #e5e5e2;
      --text: #1f201d;
      --muted: #52524e;
      --accent: #1b6e66;
      --positive: #2e7d32;
      --negative: #b42318;
      --warning: #92400e;
      --pill-positive-bg: #dcfae5; --pill-positive-ink: #04250e;
      --pill-negative-bg: #fdecea; --pill-negative-ink: #7a1d14;
      --pill-warning-bg: #fffbeb; --pill-warning-ink: #92400e;
      --font: 'Instrument Sans', system-ui, -apple-system, sans-serif;
      --serif: 'Instrument Serif', Georgia, serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font);
      font-size: 16px;
      background: var(--ground);
      color: var(--text);
      line-height: 1.55;
      font-variant-numeric: tabular-nums;
      min-height: 100vh;
    }}
    header.topbar {{
      background: var(--surface);
      padding: 0.85rem 2rem;
    }}
    .topbar-inner {{
      max-width: 1140px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }}
    .brand {{ display: flex; align-items: center; gap: 0.75rem; }}
    .brand-mark {{
      width: 34px; height: 34px; border-radius: 8px;
      background: var(--accent); color: #ffffff;
      display: flex; align-items: center; justify-content: center;
      font-family: var(--serif); font-size: 1.25rem;
    }}
    .brand-title {{ font-size: 1rem; font-weight: 600; color: var(--text); }}
    .brand-sub {{ font-size: 0.85rem; color: var(--muted); }}
    .trust-strip {{
      display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; font-size: 0.86rem; color: var(--muted);
    }}
    .trust-strip a {{ color: var(--accent); text-decoration: none; font-weight: 500; }}
    .trust-strip a:hover {{ text-decoration: underline; }}

    .shell {{
      max-width: 1140px;
      margin: 0 auto;
      padding: 2rem 2rem 4rem;
    }}
    .editorial-greeting-block {{
      margin-bottom: 1.35rem;
    }}
    .editorial-greeting-block h1 {{
      font-family: var(--serif);
      font-size: 30px;
      font-weight: 400;
      letter-spacing: -0.01em;
      line-height: 1.15;
      color: var(--text);
      margin-bottom: 0.35rem;
    }}
    @media (max-width: 640px) {{
      .editorial-greeting-block h1 {{ font-size: 24px; }}
      .shell {{ padding: 1.25rem 1rem 3rem; }}
      header.topbar {{ padding: 0.75rem 1rem; }}
    }}
    .greeting-subline {{
      font-size: 0.96rem;
      color: var(--text);
      max-width: 64ch;
    }}
    .greeting-callout {{
      background: var(--raised);
      border-left: 3px solid var(--accent);
      padding: 0.9rem 1.1rem;
      border-radius: 16px;
      font-size: 0.95rem;
      margin-bottom: 1rem;
    }}

    .kpi-strip {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      align-items: start;
      margin-bottom: 1.25rem;
    }}
    @media (max-width: 960px) {{ .kpi-strip {{ grid-template-columns: repeat(2, 1fr); }} }}
    .kpi-tile {{
      background: var(--surface);
      border-radius: 16px;
      padding: 16px 18px;
    }}
    .kpi-val {{ font-size: 28px; font-weight: 400; font-variant-numeric: tabular-nums; color: var(--text); line-height: 1.15; }}
    .kpi-cap {{ font-size: 0.85rem; color: var(--muted); margin-top: 0.3rem; }}

    .workspace-stack {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .panel {{
      background: var(--surface);
      border-radius: 16px;
      padding: 20px;
    }}
    .panel h2 {{
      font-size: 1rem;
      font-weight: 600;
      color: var(--text);
      margin-bottom: 0.65rem;
    }}
    .sample-list {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      align-items: start;
      margin-bottom: 0.85rem;
    }}
    @media (max-width: 820px) {{ .sample-list {{ grid-template-columns: 1fr; }} }}
    .sample-btn {{
      width: 100%;
      text-align: left;
      background: var(--raised);
      border: none;
      border-radius: 8px;
      padding: 0.7rem 0.9rem;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      gap: 0.15rem;
      color: var(--text);
    }}
    .sample-btn:hover, .sample-btn.active-sample {{
      background: #e8f3f1;
    }}
    .sample-btn .s-title {{ font-size: 0.9rem; font-weight: 600; color: var(--text); }}
    .sample-btn .s-sub {{ font-size: 0.84rem; color: var(--muted); }}

    button, .btn {{
      background: var(--accent);
      color: #ffffff;
      border: none;
      padding: 0.52rem 1rem;
      border-radius: 999px;
      font-family: var(--font);
      font-size: 0.88rem;
      font-weight: 500;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }}
    button:hover, .btn:hover {{ background: #145750; }}
    button.secondary, .btn.secondary {{
      background: var(--raised);
      color: var(--text);
    }}
    button.secondary:hover, .btn.secondary:hover {{ background: #e8f3f1; }}
    button.success-btn, .btn.success-btn {{ background: var(--positive); color: #ffffff; }}
    button.success-btn:hover, .btn.success-btn:hover {{ background: #215e25; }}

    .tabs {{ display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }}
    .tab {{
      background: var(--surface);
      color: var(--muted);
      padding: 0.52rem 1.05rem;
      border-radius: 999px;
      font-weight: 500;
      font-size: 0.9rem;
    }}
    .tab.active {{
      background: var(--text);
      color: #ffffff;
    }}

    label {{ display: block; font-size: 0.86rem; font-weight: 500; color: var(--text); margin: 0.55rem 0 0.25rem; }}
    select, input, textarea {{
      width: 100%;
      background: var(--raised);
      border: 1px solid var(--control);
      color: var(--text);
      padding: 0.55rem 0.75rem;
      border-radius: 8px;
      font-family: var(--font);
      font-size: 0.9rem;
    }}
    textarea {{ min-height: 120px; resize: vertical; line-height: 1.5; }}

    .controls-row {{
      display: grid;
      grid-template-columns: 1.3fr 1fr 1fr auto;
      gap: 12px;
      align-items: end;
    }}
    @media (max-width: 900px) {{ .controls-row {{ grid-template-columns: 1fr; }} }}

    .redline-card {{
      background: var(--raised);
      border-radius: 16px;
      padding: 1.15rem 1.25rem;
      margin-bottom: 12px;
    }}
    .redline-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.75rem;
      margin-bottom: 0.55rem;
    }}
    .sev-pill {{
      font-size: 0.82rem;
      padding: 0.22rem 0.7rem;
      border-radius: 999px;
      font-weight: 600;
      white-space: nowrap;
    }}
    .sev-CRITICAL, .sev-HIGH {{ background: var(--pill-negative-bg); color: var(--pill-negative-ink); }}
    .sev-MODERATE {{ background: var(--pill-warning-bg); color: var(--pill-warning-ink); }}
    .sev-LOW, .sev-NONE {{ background: var(--pill-positive-bg); color: var(--pill-positive-ink); }}

    .diff-label {{
      font-size: 0.84rem;
      font-weight: 600;
      color: var(--muted);
      margin-top: 0.45rem;
    }}
    del.w-del {{
      display: block;
      background: var(--pill-negative-bg);
      color: var(--pill-negative-ink);
      padding: 0.65rem 0.85rem;
      border-left: 3px solid var(--negative);
      border-radius: 8px;
      margin: 0.25rem 0 0.55rem;
      text-decoration: line-through;
      font-size: 0.92rem;
      max-width: 65ch;
    }}
    ins.w-ins {{
      display: block;
      background: var(--pill-positive-bg);
      color: var(--pill-positive-ink);
      padding: 0.65rem 0.85rem;
      border-left: 3px solid var(--positive);
      border-radius: 8px;
      margin: 0.25rem 0 0.55rem;
      text-decoration: none;
      font-size: 0.92rem;
      max-width: 65ch;
    }}
    .rationale {{ font-size: 0.88rem; color: var(--muted); margin-top: 0.45rem; max-width: 65ch; }}
    .decision-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
      margin-top: 0.75rem;
    }}
    .chip-btn {{
      background: var(--surface);
      color: var(--text);
      padding: 0.4rem 0.8rem;
      border-radius: 999px;
      font-size: 0.84rem;
      font-weight: 500;
    }}
    .chip-btn.active-chip {{
      background: var(--accent);
      color: #ffffff;
    }}
    details.assistant-drawer {{
      background: var(--surface);
      border-radius: 16px;
      padding: 1rem 1.25rem;
    }}
    details.assistant-drawer summary {{
      cursor: pointer;
      font-weight: 600;
      font-size: 0.92rem;
      color: var(--text);
    }}
    pre.json-box {{
      background: var(--raised);
      border-radius: 8px;
      padding: 0.85rem;
      font-family: var(--font);
      font-size: 0.84rem;
      color: var(--text);
      overflow-x: auto;
      max-height: 220px;
      margin-top: 0.75rem;
    }}
  </style>
</head>
<body>
  <!-- Template catalog keys: Predatory Enterprise MSA | Unbalanced Mutual NDA | GDPR Vendor DPA | SOC2 Security Questionnaire | Which agreement are we reviewing today? | http://localhost:8792/mcp -->
  <header class="topbar">
    <div class="topbar-inner">
      <div class="brand">
        <div class="brand-mark">C</div>
        <div>
          <div class="brand-title">ClauseGuard MCP — Commercial Contract &amp; Security Review Desk</div>
          <div class="brand-sub">Plain-English Agreement Review, Word Track Changes (.docx) &amp; Security Questionnaires</div>
        </div>
      </div>
      <div class="trust-strip">
        <span><strong>Confidentiality Guarantee:</strong> Zero training on your agreements</span>
        <a href="/about">About</a>
        <a href="/docs">Documentation</a>
        <a href="/privacy">Privacy Policy</a>
        <a href="/terms">Terms &amp; Disclaimer</a>
        <span id="planBadgeText" style="color:var(--accent);font-weight:600;">Complimentary Plan (1 Review / Month)</span>
        <a href="https://buy.stripe.com/3cI7sL5hz4JVccl4k2fAc00" target="_blank" rel="noopener" style="color:var(--accent);font-weight:600;">Upgrade ($49.99) →</a>
      </div>
    </div>
  </header>

  <main class="shell">
    <section class="editorial-greeting-block">
      <h1 id="greetingHeadline">Good morning. Let's review your agreement.</h1>
      <p class="greeting-subline" id="contextualStepGreeting">
        Welcome to your Contract Review Desk. Select a sample agreement, upload a Microsoft Word (.docx) file, or customize your negotiation standard below.
      </p>
    </section>

    <section class="kpi-strip">
      <div class="kpi-tile">
        <div class="kpi-val" id="kpiInitialVal" style="color:var(--negative);">98/100</div>
        <div class="kpi-cap" id="kpiInitialCap">CRITICAL initial risk exposure —Initial Draft Risk</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-val" id="kpiPostVal" style="color:var(--positive);">20/100</div>
        <div class="kpi-cap" id="kpiPostCap">5 of 5 revisions applied —After Your Redlines</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-val" id="kpiStandardVal" style="font-size:20px;">Balanced Buyer Standard</div>
        <div class="kpi-cap" id="kpiStandardCap">Enterprise_Master_Services_Agreement.docx</div>
      </div>
      <div class="kpi-tile">
        <button class="success-btn" style="width:100%;justify-content:center;padding:0.6rem;" onclick="downloadCustomizedDocx()">
          Download Word (.docx) with Track Changes
        </button>
        <div class="kpi-cap">Opens in Microsoft Word &amp; Google Docs</div>
      </div>
    </section>

    <div class="tabs">
      <button class="tab active" id="tabBtnAudit" onclick="switchTab('audit')">1. Review &amp; Redline Agreement</button>
      <button class="tab" id="tabBtnQuest" onclick="switchTab('quest')">2. Security Questionnaire Desk</button>
      <button class="tab" id="tabBtnDiff" onclick="switchTab('diff')">3. Compare Two Drafts</button>
    </div>

    <div class="workspace-stack">
      <!-- TAB 1: COMPACT AGREEMENT BAR -->
      <div id="panelAudit" class="panel">
        <div class="sample-list">
          <button class="sample-btn active-sample" id="sampleBtn_predatory_msa" onclick="loadSampleContract('predatory_msa')">
            <span class="s-title">Enterprise Master Services Agreement</span>
            <span class="s-sub">Vendor software draft with 5 high-risk clauses</span>
          </button>
          <button class="sample-btn" id="sampleBtn_unbalanced_nda" onclick="loadSampleContract('unbalanced_nda')">
            <span class="s-title">Mutual Non-Disclosure Agreement</span>
            <span class="s-sub">Confidentiality draft with IP &amp; hiring restrictions</span>
          </button>
          <button class="sample-btn" id="sampleBtn_gdpr_dpa" onclick="loadSampleContract('gdpr_dpa')">
            <span class="s-title">Customer Data Processing Addendum</span>
            <span class="s-sub">Privacy addendum missing subprocessor notice</span>
          </button>
        </div>

        <div class="controls-row">
          <div>
            <label for="playbookSelect">Negotiation Standard (Playbook)</label>
            <select id="playbookSelect" onchange="runAuditTool()">
              <option value="founder_friendly">Balanced Buyer &amp; Founder Standard (12m Cap, 30d Notice, Keep IP)</option>
              <option value="saas_vendor">Software Provider Standard (Subscription Cap, Platform IP)</option>
              <option value="gdpr_dpa">Data Privacy Addendum Standard (30d Subprocessor Notice, 24h Incident)</option>
              <option value="hipaa_baa">Healthcare Privacy (BAA) Standard (Subcontractor Flow-Down)</option>
            </select>
          </div>
          <div>
            <label for="contractNameInput">Exported Word Filename</label>
            <input id="contractNameInput" value="Enterprise_Master_Services_Agreement.docx" />
          </div>
          <div>
            <label for="reviewerNameInput">Reviewer Name in Word</label>
            <input id="reviewerNameInput" value="ClauseGuard Legal Desk" />
          </div>
          <div style="display:flex;gap:0.5rem;">
            <label for="docxFileInput" class="btn secondary" style="margin:0;cursor:pointer;">
              Upload .docx or .txt
              <input id="docxFileInput" type="file" accept=".docx,.txt" style="display:none;" onchange="handleFileUpload(this)" />
            </label>
            <button onclick="runAuditTool()">Review Agreement</button>
          </div>
        </div>
        <span id="auditStatus" style="font-size:0.86rem;color:var(--muted);"></span>

        <details style="margin-top:0.75rem;">
          <summary style="cursor:pointer;font-size:0.88rem;font-weight:500;color:var(--accent);">View or Edit Full Agreement Text</summary>
          <textarea id="contractTextArea" style="margin-top:0.5rem;"></textarea>
        </details>
      </div>

      <!-- TAB 2: SECURITY QUESTIONNAIRE INPUT -->
      <div id="panelQuest" class="panel" style="display:none;">
        <h2>Customer Security Questionnaire Desk</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:0.75rem;">
          <div>
            <label for="questCompanyInput">Organization Name</label>
            <input id="questCompanyInput" value="Our Organization" />
          </div>
          <div>
            <label for="questSlaInput">Security Incident Notification Window (Hours)</label>
            <input id="questSlaInput" type="number" value="24" />
          </div>
          <div>
            <label for="questSoc2Input">Independent Audit Status</label>
            <input id="questSoc2Input" value="Independent SOC 2 Type II examination completed annually with continuous control monitoring" />
          </div>
          <div>
            <label for="questEncInput">Data Encryption Standard</label>
            <input id="questEncInput" value="AES-256 encryption at rest with hardware-backed key management and automatic 90-day key rotation" />
          </div>
        </div>
        <label>Customer Security Questions (Click any question to edit)</label>
        <div id="questFriendlyList"></div>
        <textarea id="questItemsArea" style="display:none;"></textarea>
        <div style="margin-top:0.85rem;">
          <button onclick="runQuestionnaireTool()">Generate Security Questionnaire Responses</button>
        </div>
      </div>

      <!-- TAB 3: COMPARE DRAFTS INPUT -->
      <div id="panelDiff" class="panel" style="display:none;">
        <h2>Compare Two Agreement Drafts</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div><label for="versionAText">Your Initial Agreement Draft</label><textarea id="versionAText"></textarea></div>
          <div><label for="versionBText">Counterparty's Returned Markup</label><textarea id="versionBText"></textarea></div>
        </div>
        <div style="margin-top:0.85rem;">
          <button onclick="runCompareTool()">Compare Drafts &amp; Highlight Risk Shifts</button>
        </div>
      </div>

      <!-- LIVE REDLINE CO-PILOT & WORD TRACK CHANGES WORKSPACE -->
      <div class="panel" id="resultsCard">
        <div id="visualOutput">
          <p style="color:var(--muted);font-size:0.95rem;">Preparing your review workspace...</p>
        </div>
      </div>

      <!-- MEMBERSHIP PLAN DRAWER -->
      <details class="assistant-drawer">
        <summary>Membership Plan &amp; Review Quota (Complimentary vs. Professional $49.99)</summary>
        <div style="display:grid;grid-template-columns:1fr 1fr auto;gap:12px;align-items:end;margin-top:0.65rem;">
          <div>
            <label for="clientIdInput">Your Workspace Name</label>
            <input id="clientIdInput" value="general-counsel-desk" />
          </div>
          <div>
            <label for="apiKeyInput">Professional Plan Access Key (Optional)</label>
            <input id="apiKeyInput" placeholder="Leave blank for Complimentary Plan" />
          </div>
          <div style="display:flex;gap:0.45rem;flex-wrap:wrap;">
            <a href="https://buy.stripe.com/3cI7sL5hz4JVccl4k2fAc00" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;padding:0.5rem 0.9rem;border-radius:10px;background:var(--accent);color:#ffffff;font-weight:600;text-decoration:none;font-size:0.88rem;">Upgrade via Stripe ($49.99) →</a>
            <button class="secondary" onclick="activateProKey()">Try Professional Plan ($49/mo)</button>
            <button class="secondary" onclick="clearProKey()">Use Complimentary Plan</button>
          </div>
        </div>
      </details>
    </div>
  </main>

  <script>{STUDIO_CLIENT_JS}</script>
</body>
</html>"""
