"""Client-side interactive workflow script for ClauseGuard MCP Web Desk."""

from __future__ import annotations

STUDIO_CLIENT_JS = """
let SAMPLE_DATA = null;
let CURRENT_AUDIT = null;
let CLAUSE_DECISIONS = {};
let ACTIVE_FILTER = 'all';

function setTimeGreeting() {
  const hr = new Date().getHours();
  const period = hr < 12 ? 'Good morning' : (hr < 18 ? 'Good afternoon' : 'Good evening');
  const el = document.getElementById('greetingHeadline');
  if (el) el.textContent = `${period}. Let's compare your agreement against your playbook.`;
}

async function initStudio() {
  setTimeGreeting();
  const savedKey = localStorage.getItem('cg_pro_key') || '';
  if (savedKey) {
    document.getElementById('apiKeyInput').value = savedKey;
    await verifyAndApplyKey(savedKey);
  }
  const r = await fetch('/api/samples');
  SAMPLE_DATA = await r.json();
  renderQuestionnaireCards(SAMPLE_DATA.questionnaire);
  document.getElementById('questItemsArea').value = JSON.stringify(SAMPLE_DATA.questionnaire, null, 2);
  document.getElementById('versionAText').value = SAMPLE_DATA.diff_versions.version_a_text;
  document.getElementById('versionBText').value = SAMPLE_DATA.diff_versions.version_b_text;
  await loadSampleContract('predatory_msa');
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
  const stickyBar = document.getElementById('stickyExportBar');
  if (stickyBar) stickyBar.style.display = (tab === 'audit' && CURRENT_AUDIT) ? 'flex' : 'none';
  const greetSub = document.getElementById('contextualStepGreeting');
  if (tab === 'audit') {
    greetSub.textContent = 'Welcome to your Commercial Playbook Comparison Desk. Follow the 3 steps below: pick your playbook, choose a sample or paste your contract, and build your tracked redlines.';
    if (CURRENT_AUDIT) renderAuditWorkspace();
  } else if (tab === 'quest') {
    greetSub.textContent = 'Welcome to the Security & Privacy Questionnaire Desk. Customize your organization profile and generate clear, audit-ready answers in one click.';
    runQuestionnaireTool();
  } else {
    greetSub.textContent = 'Welcome to the Draft Comparison Desk. Compare your initial agreement against the other side\\'s returned markup to see which changes shift commercial exposure.';
    runCompareTool();
  }
}

function copyMcpUrl() {
  navigator.clipboard.writeText(`${window.location.origin}/mcp`);
  const btn = document.getElementById('copyMcpBtn');
  if (btn) { btn.textContent = 'Copied URL'; setTimeout(() => { btn.textContent = 'Copy Assistant URL'; }, 2000); }
}

async function verifyAndApplyKey(val) {
  const clean = (val || '').trim();
  if (!clean) {
    clearProKey();
    return false;
  }
  const r = await fetch('/api/quota', { headers: { 'X-ClauseGuard-Key': clean } });
  const d = await r.json();
  if (r.ok && d.tier === 'pro') {
    localStorage.setItem('cg_pro_key', clean);
    document.getElementById('planBadgeText').textContent = '✓ Professional Plan Active ($49.99)';
    const hLink = document.getElementById('headerUpgradeLink');
    if (hLink) hLink.style.display = 'none';
    const dLink = document.getElementById('drawerUpgradeLink');
    if (dLink) dLink.style.display = 'none';
    return true;
  }
  clearProKey();
  return false;
}

async function applyManualKey() {
  const val = document.getElementById('apiKeyInput').value.trim();
  const ok = await verifyAndApplyKey(val);
  if (ok) {
    runAuditTool();
  } else {
    showToast('Invalid or unverified Pro API key');
  }
}

function clearProKey() {
  localStorage.removeItem('cg_pro_key');
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
      updateInputStats();
      statusEl.textContent = `Loaded ${file.name}. Running comparison...`;
      await runAuditTool();
    } else {
      statusEl.textContent = d.error || 'Could not read .docx file.';
    }
  } else {
    const text = await file.text();
    document.getElementById('contractTextArea').value = text;
    updateInputStats();
    await runAuditTool();
  }
}

let NEXT_RISK_CURSOR = 0;

function showToast(msg) {
  const el = document.getElementById('studioToast');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(window.__cgToastTimer);
  window.__cgToastTimer = setTimeout(() => el.classList.remove('show'), 2600);
}

function updateInputStats() {
  const ta = document.getElementById('contractTextArea');
  const badge = document.getElementById('inputStatsBadge');
  const clearBtn = document.getElementById('clearContractBtn');
  if (!ta || !badge) return;
  const raw = ta.value.trim();
  const words = raw ? raw.split(/\\s+/).length : 0;
  const clauses = raw ? Math.max(1, raw.split(/\\n\\s*\\n|(?:^|\\n)\\s*(?:\\d+\\.|Section\\s+\\d+)/i).filter(Boolean).length) : 0;
  badge.textContent = `${words} word${words === 1 ? '' : 's'} · ~${clauses} clause${clauses === 1 ? '' : 's'}`;
  if (clearBtn) clearBtn.style.display = words > 0 ? 'inline-flex' : 'none';
}

function clearContractInput() {
  const ta = document.getElementById('contractTextArea');
  if (!ta) return;
  ta.value = '';
  document.querySelectorAll('.sample-btn').forEach(b => b.classList.remove('active-sample'));
  updateInputStats();
  ta.focus();
  showToast('✓ Cleared contract text — paste or drop your agreement');
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
  updateInputStats();
  await runAuditTool();
}

function loadQuestionnaireSample() { switchTab('quest'); }
function loadDiffSample() { switchTab('diff'); }

async function runAuditTool() {
  const statusEl = document.getElementById('auditStatus');
  statusEl.textContent = 'Comparing clauses...';
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
    author: document.getElementById('reviewerNameInput').value || 'ClauseGuard Document Comparison'
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
  NEXT_RISK_CURSOR = 0;
  renderAuditWorkspace(data.quota);
}

function acceptAllSafeFixes() {
  if (!CURRENT_AUDIT) return;
  CURRENT_AUDIT.findings.forEach(f => {
    CLAUSE_DECISIONS[f.clause_id] = { mode: 'standard', customText: f.proposed_redline };
  });
  ACTIVE_FILTER = 'all';
  renderAuditWorkspace();
  showToast(`✓ Applied all ${CURRENT_AUDIT.findings.length} recommended safe fixes`);
}

function jumpToNextRisk() {
  const cards = Array.from(document.querySelectorAll('#visualOutput .redline-card[data-risky="1"]'));
  if (!cards.length) {
    showToast('✓ No remaining flagged clauses in current view');
    return;
  }
  const target = cards[NEXT_RISK_CURSOR % cards.length];
  NEXT_RISK_CURSOR = (NEXT_RISK_CURSOR + 1) % cards.length;
  document.querySelectorAll('#visualOutput .redline-card').forEach(c => c.classList.remove('highlight-pulse'));
  target.classList.add('highlight-pulse');
  target.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
  NEXT_RISK_CURSOR = 0;
  renderAuditWorkspace();
}

function getMarketNormLabel(f) {
  const t = `${f.title || ''} ${f.category || ''} ${f.playbook_reference || ''}`.toLowerCase();
  if (t.includes('liability')) return 'Market Norm: 12-Month Fee Cap';
  if (t.includes('indemn')) return 'Market Norm: Mutual Third-Party IP Only';
  if (t.includes('renew') || t.includes('terminat')) return 'Market Norm: Mutual 30-Day Notice';
  if (t.includes('ip') || t.includes('intellectual') || t.includes('ownership') || t.includes('work')) return 'Market Norm: Customer Owns Custom IP';
  if (t.includes('subprocessor') || t.includes('gdpr') || t.includes('data')) return 'Market Norm: 30-Day Prior Notice';
  if (t.includes('solicit') || t.includes('compete')) return 'Market Norm: Narrow Direct-Hire Carveout';
  return 'Market Norm: Balanced Mutual Protection';
}

function copySingleClause(clauseId) {
  if (!CURRENT_AUDIT) return;
  const f = (CURRENT_AUDIT.findings || []).find(item => item.clause_id === clauseId);
  if (!f) return;
  const dec = CLAUSE_DECISIONS[clauseId] || { mode: 'standard', customText: f.proposed_redline };
  const textToCopy = dec.mode === 'compromise'
    ? (f.compromise_redline || f.proposed_redline)
    : (dec.mode === 'custom' ? dec.customText : f.proposed_redline);
  navigator.clipboard.writeText(textToCopy);
  showToast(`✓ Copied replacement clause (${clauseId}) to clipboard`);
}

function copyCounterpartyEmail() {
  const el = document.getElementById('counterpartyEmailBox');
  if (!el) return;
  navigator.clipboard.writeText(el.value);
  const btn = document.getElementById('copyEmailBtn');
  if (btn) { btn.textContent = '✓ Copied to Clipboard'; setTimeout(() => { btn.textContent = 'Copy Polite Email to Counterparty'; }, 2200); }
  showToast('✓ Copied counterparty discussion email to clipboard');
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
      author: document.getElementById('reviewerNameInput').value || 'ClauseGuard Document Comparison'
    })
  });
  const d = await resp.json();
  if (resp.ok && d.download_url) {
    showToast(`✓ Downloaded ${CURRENT_AUDIT.contract_name} with ${accepted.length} Track Changes`);
    window.location.href = d.download_url;
  }
}

function renderAuditWorkspace() {
  const res = CURRENT_AUDIT;
  if (!res) return;

  let activeAcceptedCount = 0;
  let remainingRiskPoints = 0;
  let highPriorityCount = 0;
  res.findings.forEach(f => {
    if (f.severity === 'CRITICAL' || f.severity === 'HIGH') highPriorityCount += 1;
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
  document.getElementById('kpiInitialCap').textContent = `${res.risk_level} initial variance —Initial Draft Score`;
  document.getElementById('kpiPostVal').textContent = `${postRedlineScore}/100`;
  document.getElementById('kpiPostCap').textContent = `${activeAcceptedCount} of ${res.findings.length} revisions applied —After Your Redlines`;
  document.getElementById('kpiStandardVal').textContent = res.playbook_label;
  document.getElementById('kpiStandardCap').textContent = res.contract_name;

  const stickyBar = document.getElementById('stickyExportBar');
  if (stickyBar) {
    stickyBar.style.display = 'flex';
    const sbTitle = document.getElementById('stickyBarTitle');
    if (sbTitle) sbTitle.textContent = `${activeAcceptedCount} of ${res.findings.length} Redlines Ready (${res.risk_score} → ${postRedlineScore}/100 Score)`;
  }

  const filteredFindings = res.findings.filter(f => {
    const dec = CLAUSE_DECISIONS[f.clause_id] || { mode: 'standard' };
    if (ACTIVE_FILTER === 'critical') return f.severity === 'CRITICAL' || f.severity === 'HIGH';
    if (ACTIVE_FILTER === 'accepted') return dec.mode !== 'dismissed';
    return true;
  });

  const findingsHtml = filteredFindings.map(f => {
    const dec = CLAUSE_DECISIONS[f.clause_id] || { mode: 'standard', customText: f.proposed_redline };
    const activeReplacement = dec.mode === 'compromise'
      ? (f.compromise_redline || f.proposed_redline)
      : (dec.mode === 'custom' ? dec.customText : f.proposed_redline);

    const sevLabel = f.severity === 'CRITICAL' ? 'Critical Playbook Variance'
      : (f.severity === 'HIGH' ? 'High Priority Revision' : 'Commercial Negotiation Point');

    return `
      <div class="redline-card" data-risky="1" id="clauseCard_${f.clause_id}" style="opacity:${dec.mode === 'dismissed' ? '0.65' : '1'};">
        <div class="redline-header">
          <div>
            <div style="font-size:1.05rem;font-weight:600;color:var(--text);">${f.clause_id}: ${f.title}</div>
            <div style="font-size:0.84rem;color:var(--muted);">${f.playbook_reference}</div>
          </div>
          <div style="display:flex;gap:0.4rem;flex-wrap:wrap;align-items:center;">
            <span class="market-norm-pill">${getMarketNormLabel(f)}</span>
            <span class="sev-pill sev-${f.severity}">${sevLabel}</span>
          </div>
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
          <button class="chip-btn" style="border:1px solid var(--control);" onclick="copySingleClause('${f.clause_id}')">
            Copy Replacement Clause
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
        Most checklists only check what is written on the page. We also checked for standard commercial clauses that were omitted:
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

  const bottomLineSummary = res.findings.length === 0
    ? 'Playbook Summary: 0 variances flagged — this draft aligns with your selected commercial checklist.'
    : `Playbook Summary: ${highPriorityCount} high-impact clause${highPriorityCount === 1 ? '' : 's'} (${res.findings.length} total) flagged for review with your legal counsel — reducing variance score from ${res.risk_score}/100 to ${postRedlineScore}/100.`;

  document.getElementById('visualOutput').innerHTML = `
    <div class="greeting-callout" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.85rem;">
      <div style="max-width:64ch;">
        <div style="font-size:1rem;font-weight:600;color:var(--text);margin-bottom:0.2rem;">${bottomLineSummary}</div>
        <div style="font-size:0.88rem;color:var(--muted);">${res.sign_off_recommendation} — ${res.executive_summary}</div>
      </div>
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
        <button type="button" onclick="acceptAllSafeFixes()" class="success-btn">✓ Accept All Safe Fixes (${res.findings.length})</button>
        <button type="button" onclick="jumpToNextRisk()" class="secondary">Jump to Next Variance ↓</button>
      </div>
    </div>

    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.75rem;margin:0.85rem 0;">
      <div style="font-size:0.94rem;color:var(--text);">
        <strong>Filter &amp; Step Through Clauses:</strong> Click any pill to filter or jump straight to the next item.
      </div>
      <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
        <button class="chip-btn ${ACTIVE_FILTER === 'all' ? 'active-chip' : ''}" onclick="setFilter('all')">All Clauses (${res.findings.length})</button>
        <button class="chip-btn ${ACTIVE_FILTER === 'critical' ? 'active-chip' : ''}" onclick="setFilter('critical')">High-Impact Only (${highPriorityCount})</button>
        <button class="chip-btn ${ACTIVE_FILTER === 'accepted' ? 'active-chip' : ''}" onclick="setFilter('accepted')">Accepted (${activeAcceptedCount})</button>
        <button class="chip-btn" style="background:#e8f3f1;color:var(--accent);font-weight:600;" onclick="jumpToNextRisk()">Jump to Next Variance ↓</button>
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
      <strong>Draft Comparison Complete:</strong> We spotted <strong>${res.material_risk_shifts} significant commercial shift(s)</strong> between your initial draft and the returned markup.
      <div style="font-size:0.9rem;color:var(--muted);margin-top:0.2rem;max-width:65ch;">${res.summary}</div>
    </div>
    ${res.diffs.map(d => `
      <div class="redline-card">
        <div class="redline-header">
          <span style="font-weight:600;">Section #${d.clause_index} — ${d.plain_title || d.risk_shift_type}</span>
          <span class="sev-pill sev-${d.severity}">${d.severity === 'CRITICAL' || d.severity === 'HIGH' ? 'Major Commercial Shift' : d.change_type}</span>
        </div>
        <div class="diff-label">Your Initial Draft</div>
        <del class="w-del">${d.version_a_clause}</del>
        <div class="diff-label" style="color:var(--negative);">Counterparty's Returned Markup</div>
        <ins class="w-ins" style="border-left-color:var(--negative);background:var(--pill-negative-bg);color:var(--pill-negative-ink);">${d.version_b_clause}</ins>
        <div class="rationale"><strong>Commercial Impact:</strong> ${d.legal_impact}</div>
      </div>`).join('')}`;
}

window.addEventListener('DOMContentLoaded', initStudio);
"""
