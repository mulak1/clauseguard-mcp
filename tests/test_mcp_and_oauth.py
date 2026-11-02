"""Integration tests for Streamable HTTP MCP, OAuth 2.1 PKCE, Web Studio, Manifests, and Tier Quotas."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from clauseguard_mcp.app import create_app


ROOT_DIR = Path(__file__).resolve().parent.parent


def _pkce_pair(verifier: str = "clauseguard-super-secret-pkce-verifier-2026-oauth21") -> tuple[str, str]:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def test_oauth21_discovery_and_s256_pkce_flow() -> None:
    """As Claude/ChatGPT MCP connector, I can authenticate using OAuth 2.1 with S256 PKCE."""
    client = TestClient(create_app())

    # 1. Discovery metadata
    meta_resp = client.get("/.well-known/oauth-authorization-server")
    assert meta_resp.status_code == 200
    meta = meta_resp.json()
    assert "S256" in meta["code_challenge_methods_supported"]
    assert meta["authorization_endpoint"].endswith("/oauth/authorize")
    assert meta["token_endpoint"].endswith("/oauth/token")

    # 2. Authorize with S256 challenge
    verifier, challenge = _pkce_pair()
    auth_resp = client.get(
        "/oauth/authorize",
        params={
            "response_type": "code",
            "client_id": "claude-connector-client",
            "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": "xyz987",
            "scope": "mcp:tools",
        },
    )
    assert auth_resp.status_code == 200
    auth_data = auth_resp.json()
    assert "code" in auth_data
    assert auth_data["state"] == "xyz987"
    code = auth_data["code"]

    # 3. Attempt token exchange with WRONG verifier -> must fail with 400
    bad_token_resp = client.post(
        "/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": "claude-connector-client",
            "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
            "code_verifier": "wrong-verifier-value-that-does-not-match-sha256",
        },
    )
    assert bad_token_resp.status_code == 400

    # 4. Issue a fresh code and exchange with valid verifier -> 200 access_token
    auth_resp2 = client.get(
        "/oauth/authorize",
        params={
            "response_type": "code",
            "client_id": "claude-connector-client",
            "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": "state2",
        },
    )
    code2 = auth_resp2.json()["code"]
    ok_token_resp = client.post(
        "/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code2,
            "client_id": "claude-connector-client",
            "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
            "code_verifier": verifier,
        },
    )
    assert ok_token_resp.status_code == 200
    tok = ok_token_resp.json()
    assert tok["token_type"] == "Bearer"
    assert tok["access_token"].startswith("cg_oauth_")


def test_mcp_streamable_http_jsonrpc_lifecycle() -> None:
    """Verify GET /mcp and POST /mcp support initialize, tools/list (with annotations), and tools/call."""
    client = TestClient(create_app())

    # GET /mcp discovery
    get_mcp = client.get("/mcp")
    assert get_mcp.status_code == 200
    assert get_mcp.json()["protocolVersion"] == "2025-03-26"

    # 1. initialize
    init_resp = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "claude-ai", "version": "1.0.0"},
            },
        },
    )
    assert init_resp.status_code == 200
    init_body = init_resp.json()
    assert init_body["result"]["serverInfo"]["name"] == "ClauseGuard MCP"

    # 2. notifications/initialized
    notif_resp = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
    )
    assert notif_resp.status_code == 200

    # 3. tools/list with required MCP annotations
    list_resp = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    )
    assert list_resp.status_code == 200
    tools = list_resp.json()["result"]["tools"]
    tool_names = {t["name"] for t in tools}
    assert tool_names == {
        "audit_and_redline_contract",
        "autofill_security_questionnaire",
        "compare_contract_versions",
    }
    for tool in tools:
        ann = tool["annotations"]
        assert "readOnlyHint" in ann
        assert "destructiveHint" in ann
        assert "idempotentHint" in ann
        assert "openWorldHint" in ann

    # 4. tools/call -> audit_and_redline_contract
    call_audit = client.post(
        "/mcp",
        headers={"X-ClauseGuard-Key": "cg_pro_enterprise_2026"},
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "audit_and_redline_contract",
                "arguments": {
                    "contract_text": (
                        "Customer liability shall be uncapped and unlimited. "
                        "Agreement shall automatically renew for 3-year terms unless given 90 days notice."
                    ),
                    "playbook": "founder_friendly",
                    "contract_name": "Test_MSA.docx",
                },
            },
        },
    )
    assert call_audit.status_code == 200
    audit_res = call_audit.json()["result"]
    assert audit_res["isError"] is False
    structured = audit_res["structuredContent"]
    assert structured["risk_score"] >= 35
    doc_id = structured["doc_id"]

    # Download the generated .docx file via GET /api/docx/{doc_id}
    docx_resp = client.get(f"/api/docx/{doc_id}")
    assert docx_resp.status_code == 200
    assert (
        docx_resp.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert docx_resp.content[:2] == b"PK"

    # 5. tools/call -> autofill_security_questionnaire
    call_q = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "autofill_security_questionnaire",
                "arguments": {
                    "items": [
                        {"id": "1", "question": "Do you have a SOC 2 Type II report?"},
                        {"id": "2", "question": "How do you encrypt data at rest?"},
                    ]
                },
            },
        },
    )
    assert call_q.status_code == 200
    assert len(call_q.json()["result"]["structuredContent"]["answers"]) == 2

    # 6. tools/call -> compare_contract_versions
    call_cmp = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "compare_contract_versions",
                "arguments": {
                    "version_a_text": "1. Liability capped at 12 months fees.",
                    "version_b_text": "1. Customer liability shall be uncapped and unlimited.",
                },
            },
        },
    )
    assert call_cmp.status_code == 200
    assert call_cmp.json()["result"]["structuredContent"]["material_risk_shifts"] >= 1

    # 7. Unknown method returns JSON-RPC -32601
    unk = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 99, "method": "nonexistent/method"},
    )
    assert unk.status_code == 200
    assert unk.json()["error"]["code"] == -32601


def test_free_vs_pro_tier_quota_enforcement() -> None:
    """Free tier allows 1 contract audit/mo per client; Pro API key allows unlimited."""
    client = TestClient(create_app())
    headers = {"X-Client-Id": "free-user-test-01"}

    # 1st audit on Free tier -> succeeds (200)
    r1 = client.post(
        "/api/audit",
        headers=headers,
        json={
            "contract_text": "Customer liability shall be uncapped and unlimited.",
            "playbook": "founder_friendly",
        },
    )
    assert r1.status_code == 200
    assert r1.json()["quota"]["tier"] == "free"
    assert r1.json()["quota"]["remaining"] == 0

    # 2nd audit on Free tier -> blocked with HTTP 402 Payment Required
    r2 = client.post(
        "/api/audit",
        headers=headers,
        json={
            "contract_text": "Customer liability shall be uncapped and unlimited.",
            "playbook": "founder_friendly",
        },
    )
    assert r2.status_code == 402
    assert "$49/mo" in r2.json()["error"]

    # Upgrading with Pro key -> succeeds!
    r3 = client.post(
        "/api/audit",
        headers={"X-Client-Id": "free-user-test-01", "X-ClauseGuard-Key": "cg_pro_live_key"},
        json={
            "contract_text": "Customer liability shall be uncapped and unlimited.",
            "playbook": "founder_friendly",
        },
    )
    assert r3.status_code == 200
    assert r3.json()["quota"]["tier"] == "pro"


def test_web_studio_and_submission_manifests() -> None:
    """Verify Web Studio UI at GET / and both Claude & OpenAI submission manifests."""
    client = TestClient(create_app())

    studio = client.get("/")
    assert studio.status_code == 200
    html = studio.text
    assert "ClauseGuard MCP" in html
    assert "http://localhost:8792/mcp" in html
    assert "Predatory Enterprise MSA" in html
    assert "Unbalanced Mutual NDA" in html
    assert "GDPR Vendor DPA" in html
    assert "SOC2 Security Questionnaire" in html

    samples = client.get("/api/samples")
    assert samples.status_code == 200
    assert "predatory_msa" in samples.json()["contracts"]

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["port"] == 8792

    quota_resp = client.get("/api/quota", headers={"X-Client-Id": "quota-check-user"})
    assert quota_resp.status_code == 200
    assert quota_resp.json()["tier"] == "free"

    rest_q = client.post(
        "/api/questionnaire",
        json={"items": [{"id": "Q1", "question": "Do you have SOC 2 Type II?"}]},
    )
    assert rest_q.status_code == 200

    rest_cmp = client.post(
        "/api/compare",
        json={
            "version_a_text": "1. Liability capped at 12 months fees.",
            "version_b_text": "1. Liability shall be uncapped and unlimited.",
        },
    )
    assert rest_cmp.status_code == 200

    m_claude = client.get("/manifests/claude")
    m_openai = client.get("/manifests/openai")
    assert m_claude.status_code == 200
    assert m_openai.status_code == 200
    assert client.get("/api/docx/doc_missing").status_code == 404

    claude_path = ROOT_DIR / "claude-connector-manifest.json"
    openai_path = ROOT_DIR / "openai-mcp-app.json"
    assert claude_path.exists()
    assert openai_path.exists()

    claude_manifest = json.loads(claude_path.read_text(encoding="utf-8"))
    openai_manifest = json.loads(openai_path.read_text(encoding="utf-8"))
    assert claude_manifest["name"] == "ClauseGuard MCP"
    assert len(claude_manifest["tools"]) == 3
    assert openai_manifest["name_for_human"] == "ClauseGuard MCP"
    assert len(openai_manifest["mcp_server"]["tools"]) == 3

    # Verify Greeting, Privacy, Terms, Zero Vendor Jargon, Custom .docx, and Upload Extract
    assert "Which agreement are we reviewing today?" in html
    assert "Welcome to your Contract Review Desk" in html
    for forbidden_vendor in ("Drata", "Deloitte", "AWS KMS"):
        assert forbidden_vendor not in html

    priv = client.get("/privacy")
    terms = client.get("/terms")
    assert priv.status_code == 200
    assert "Zero Training on Your Agreements" in priv.text
    assert terms.status_code == 200
    assert "Reviewer Sovereignty" in terms.text

    custom_docx_resp = client.post(
        "/api/docx/custom",
        json={
            "contract_name": "Custom_Selected_Redlines.docx",
            "playbook": "founder_friendly",
            "risk_score": 25,
            "risk_level": "MODERATE",
            "contract_text": "1. Customer liability shall be uncapped and unlimited.",
            "accepted_redlines": [
                {
                    "clause_id": "CL-01",
                    "title": "Unlimited Financial Liability Exposure",
                    "severity": "CRITICAL",
                    "original_excerpt": "1. Customer liability shall be uncapped and unlimited.",
                    "replacement_text": "1. Mutual liability is capped at 12 months of fees.",
                    "rationale": "Standard mutual cap.",
                    "playbook_reference": "Standard §1.1",
                }
            ],
        },
    )
    assert custom_docx_resp.status_code == 200
    custom_dl = custom_docx_resp.json()["download_url"]
    raw_custom_docx = client.get(custom_dl).content
    assert raw_custom_docx[:2] == b"PK"

    extract_resp = client.post(
        "/api/extract-docx",
        json={"docx_base64": base64.b64encode(raw_custom_docx).decode("ascii")},
    )
    assert extract_resp.status_code == 200
    assert "Mutual liability" in extract_resp.json()["text"]


