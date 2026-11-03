"""Privacy-safe real-time telemetry & analytics for Claude, ChatGPT, and Web Studio usage.

Zero confidential contract text or customer PII is ever stored — only aggregate counters
and anonymized event metadata (timestamp, platform, tool name, playbook).
"""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any


_COUNTERS: dict[str, int] = {
    "total_events": 0,
    "mcp_connections": 0,
    "tool_calls_total": 0,
    "docx_downloads": 0,
    "web_page_views": 0,
    "pro_unlocks": 0,
}

_BY_SOURCE: dict[str, int] = {
    "Claude": 0,
    "ChatGPT": 0,
    "Web Desk": 0,
    "Other MCP Client": 0,
}

_BY_TOOL: dict[str, int] = {
    "audit_and_redline_contract": 0,
    "autofill_security_questionnaire": 0,
    "compare_contract_versions": 0,
}

_BY_PLAYBOOK: dict[str, int] = {
    "founder_friendly": 0,
    "saas_vendor": 0,
    "gdpr_dpa": 0,
    "hipaa_baa": 0,
}

_RECENT_EVENTS: deque[dict[str, str]] = deque(maxlen=50)


def detect_source(user_agent: str, path: str = "", client_name: str = "") -> str:
    """Classify the request caller as Claude, ChatGPT, Web Desk, or Other MCP Client."""
    ua = (user_agent or "").lower()
    cn = (client_name or "").lower()
    if "claude" in ua or "anthropic" in ua or "claude" in cn or "anthropic" in cn:
        return "Claude"
    if "chatgpt" in ua or "openai" in ua or "gpt" in cn or "/chatgpt" in path:
        return "ChatGPT"
    if path.startswith("/mcp"):
        return "Claude" if not ua or "python" not in ua else "Other MCP Client"
    return "Web Desk"


def record_event(
    *,
    event_type: str,
    source: str,
    tool_name: str = "-",
    detail: str = "",
) -> None:
    """Record a privacy-safe telemetry event in memory."""
    _COUNTERS["total_events"] += 1
    if source in _BY_SOURCE:
        _BY_SOURCE[source] += 1
    else:
        _BY_SOURCE["Other MCP Client"] += 1

    if event_type == "mcp_connect":
        _COUNTERS["mcp_connections"] += 1
    elif event_type == "tool_call":
        _COUNTERS["tool_calls_total"] += 1
        if tool_name in _BY_TOOL:
            _BY_TOOL[tool_name] += 1
        if detail in _BY_PLAYBOOK:
            _BY_PLAYBOOK[detail] += 1
    elif event_type == "docx_download":
        _COUNTERS["docx_downloads"] += 1
    elif event_type == "page_view":
        _COUNTERS["web_page_views"] += 1
    elif event_type == "pro_unlock":
        _COUNTERS["pro_unlocks"] += 1

    _RECENT_EVENTS.appendleft(
        {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "source": source,
            "event": event_type,
            "tool": tool_name,
            "detail": detail or "-",
        }
    )


def get_analytics_snapshot() -> dict[str, Any]:
    """Return current telemetry counters and recent anonymized events."""
    return {
        "counters": dict(_COUNTERS),
        "by_source": dict(_BY_SOURCE),
        "by_tool": dict(_BY_TOOL),
        "by_playbook": dict(_BY_PLAYBOOK),
        "recent_events": list(_RECENT_EVENTS),
    }


def render_analytics_html() -> str:
    """Render the live HTML Analytics Dashboard for ClauseGuard across Claude, ChatGPT, and Web."""
    snap = get_analytics_snapshot()
    c = snap["counters"]
    src = snap["by_source"]
    tools = snap["by_tool"]
    pbs = snap["by_playbook"]
    rows = "".join(
        f"<tr><td>{ev['timestamp']}</td><td><strong>{ev['source']}</strong></td>"
        f"<td>{ev['event']}</td><td><code>{ev['tool']}</code></td><td>{ev['detail']}</td></tr>"
        for ev in snap["recent_events"]
    ) or '<tr><td colspan="5" style="color:#666;">No events recorded yet in this container session.</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Live Analytics (Claude, ChatGPT &amp; Web) — ClauseGuard</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif:wght@400&display=swap" rel="stylesheet">
  <style>
    body {{ font-family:'Instrument Sans',system-ui,sans-serif; background:#f9f9f9; color:#1f201d; margin:0; padding:2.5rem 1.5rem; line-height:1.6; }}
    main {{ max-width:980px; margin:0 auto; background:#ffffff; border-radius:22px; padding:2.5rem; }}
    h1 {{ font-family:'Instrument Serif',Georgia,serif; font-size:2.3rem; font-weight:400; margin:0 0 0.35rem; }}
    h2 {{ font-size:1.1rem; margin:2rem 0 0.75rem; color:#1b6e66; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-top:1rem; }}
    .card {{ background:#f9f9f9; border-radius:16px; padding:1.1rem 1.25rem; }}
    .val {{ font-size:1.85rem; font-weight:600; color:#1b6e66; font-variant-numeric:tabular-nums; }}
    .lbl {{ font-size:0.86rem; color:#63645e; }}
    table {{ width:100%; border-collapse:collapse; margin-top:0.5rem; font-size:0.9rem; }}
    th, td {{ text-align:left; padding:0.6rem 0.75rem; border-bottom:1px solid #e7e7e5; }}
    th {{ background:#f9f9f9; color:#1b6e66; font-weight:600; }}
    code {{ background:#f2f2f0; padding:0.15rem 0.4rem; border-radius:6px; font-size:0.84rem; }}
    a {{ color:#1b6e66; text-decoration:none; font-weight:500; }}
  </style>
</head>
<body>
  <main>
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
      <a href="/">← Return to ClauseGuard Review Desk</a>
      <a href="/analytics">↻ Refresh Live Telemetry</a>
    </div>
    <h1>ClauseGuard Live Analytics</h1>
    <p style="color:#63645e;margin-top:0;">Real-time, privacy-safe usage telemetry across <strong>Claude Connectors</strong>, <strong>ChatGPT</strong>, and the <strong>Web Review Desk</strong> (zero contract text stored).</p>

    <div class="grid">
      <div class="card"><div class="val">{src.get('Claude', 0)}</div><div class="lbl">Claude MCP Events</div></div>
      <div class="card"><div class="val">{src.get('ChatGPT', 0)}</div><div class="lbl">ChatGPT Events</div></div>
      <div class="card"><div class="val">{src.get('Web Desk', 0)}</div><div class="lbl">Web Studio Events</div></div>
      <div class="card"><div class="val">{c.get('tool_calls_total', 0)}</div><div class="lbl">Total Tool Runs</div></div>
      <div class="card"><div class="val">{c.get('docx_downloads', 0)}</div><div class="lbl">Word (.docx) Downloads</div></div>
      <div class="card"><div class="val">{c.get('pro_unlocks', 0)}</div><div class="lbl">Pro Plan Activations</div></div>
    </div>

    <h2>Tool Breakdown</h2>
    <div class="grid">
      <div class="card"><div class="val">{tools.get('audit_and_redline_contract', 0)}</div><div class="lbl">Review &amp; Redline Contract</div></div>
      <div class="card"><div class="val">{tools.get('autofill_security_questionnaire', 0)}</div><div class="lbl">Security Questionnaire</div></div>
      <div class="card"><div class="val">{tools.get('compare_contract_versions', 0)}</div><div class="lbl">Compare Contract Drafts</div></div>
    </div>

    <h2>Playbook Popularity</h2>
    <div class="grid">
      <div class="card"><div class="val">{pbs.get('founder_friendly', 0)}</div><div class="lbl">Founder-Friendly</div></div>
      <div class="card"><div class="val">{pbs.get('saas_vendor', 0)}</div><div class="lbl">SaaS Vendor</div></div>
      <div class="card"><div class="val">{pbs.get('gdpr_dpa', 0)}</div><div class="lbl">GDPR DPA</div></div>
      <div class="card"><div class="val">{pbs.get('hipaa_baa', 0)}</div><div class="lbl">HIPAA BAA</div></div>
    </div>

    <h2>Recent Activity Feed (Last 50 Events)</h2>
    <table>
      <thead>
        <tr><th>Timestamp</th><th>Platform</th><th>Event</th><th>Tool</th><th>Playbook / Detail</th></tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </main>
</body>
</html>"""
