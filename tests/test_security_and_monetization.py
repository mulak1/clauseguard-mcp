"""Security hardening, monetization quota enforcement, and OpenAI Store Option B regression tests."""

from __future__ import annotations

import io
import json
import os
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from clauseguard_mcp.app import create_app
from clauseguard_mcp.docx_engine import (
    _DOCX_STORE,
    extract_text_from_docx_bytes,
    store_docx_artifact,
)
from clauseguard_mcp.oauth import is_pro_credential, issue_pro_api_key


ROOT_DIR = Path(__file__).resolve().parent.parent


def test_cloudflare_and_application_security_hardening() -> None:
    """Verify admin challenge auth, analytics XSS escaping, .docx XXE/size guards, and security headers."""
    client = TestClient(create_app())

    home_resp = client.get("/")
    assert home_resp.status_code == 200
    assert (
        home_resp.headers["Strict-Transport-Security"]
        == "max-age=31536000; includeSubDomains; preload"
    )
    assert home_resp.headers["X-Content-Type-Options"] == "nosniff"
    assert home_resp.headers["X-Frame-Options"] == "DENY"
    assert home_resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert (
        home_resp.headers["Permissions-Policy"]
        == "camera=(), microphone=(), geolocation=(), payment=()"
    )
    assert home_resp.headers["Cross-Origin-Opener-Policy"] == "same-origin"
    assert (
        home_resp.headers["Content-Security-Policy"]
        == "base-uri 'self'; object-src 'none'; frame-ancestors 'none'"
    )

    oversized_resp = client.post(
        "/mcp",
        content=b"{}",
        headers={
            "Content-Type": "application/json",
            "Content-Length": "6000000",
        },
    )
    assert oversized_resp.status_code == 413
    assert oversized_resp.headers["X-Content-Type-Options"] == "nosniff"

    unauth_resp = client.post(
        "/api/admin/openai-challenge", json={"token": "malicious_override"}
    )
    assert unauth_resp.status_code == 403
    assert (
        client.get("/.well-known/openai-apps-challenge").text
        == "jDYn4kfcZr0xfWceFTluiSzrrbhKoQiuKn3d_MPUPNE"
    )

    os.environ["ADMIN_API_SECRET"] = "test_super_secret_admin_key"
    try:
        wrong_resp = client.post(
            "/api/admin/openai-challenge",
            json={"token": "malicious_override"},
            headers={"X-Admin-Secret": "wrong_secret"},
        )
        assert wrong_resp.status_code == 403

        valid_resp = client.post(
            "/api/admin/openai-challenge",
            json={"token": "jDYn4kfcZr0xfWceFTluiSzrrbhKoQiuKn3d_MPUPNE"},
            headers={"X-Admin-Secret": "test_super_secret_admin_key"},
        )
        assert valid_resp.status_code == 200
    finally:
        os.environ.pop("ADMIN_API_SECRET", None)

    client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 999,
            "method": "tools/call",
            "params": {
                "name": "<script>alert('xss')</script>",
                "arguments": {"playbook": "<img src=x onerror=alert(1)>"},
            },
        },
    )
    analytics_html = client.get("/analytics").text
    assert "<script>alert('xss')</script>" not in analytics_html
    assert "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;" in analytics_html

    for i in range(65):
        store_docx_artifact(f"evict_{i}.docx", b"PK\x03\x04dummy")
    assert len(_DOCX_STORE) <= 60

    with pytest.raises(ValueError, match="exceeds 5 MB"):
        extract_text_from_docx_bytes(b"x" * 5_000_001)

    xxe_buf = io.BytesIO()
    with zipfile.ZipFile(xxe_buf, "w") as zf:
        zf.writestr(
            "word/document.xml",
            b'<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><w:document/>',
        )
    with pytest.raises(ValueError, match="external entities or DOCTYPE"):
        extract_text_from_docx_bytes(xxe_buf.getvalue())


def test_mcp_quota_enforcement_and_forged_pro_key_rejection() -> None:
    """Verify POST /mcp enforces check_and_consume_quota(), rejects forged cg_pro_* prefixes, and validates Option B v1.0.4."""
    assert is_pro_credential("cg_pro_forged_fake_key", None) is False
    assert is_pro_credential(None, "Bearer cg_pro_forged_fake_key") is False
    signed_key = issue_pro_api_key("customer")
    assert is_pro_credential(signed_key, None) is True

    client = TestClient(create_app())
    headers = {"X-Client-Id": "mcp-monetization-test-client"}
    payload = {
        "jsonrpc": "2.0",
        "id": 701,
        "method": "tools/call",
        "params": {
            "name": "audit_and_redline_contract",
            "arguments": {
                "contract_text": "1. Customer liability shall be uncapped and unlimited for all claims.",
                "playbook": "founder_friendly",
            },
        },
    }

    r1 = client.post("/mcp", headers=headers, json=payload)
    assert r1.status_code == 200
    assert r1.json()["result"]["isError"] is False
    assert r1.json()["result"]["structuredContent"]["quota"]["tier"] == "free"

    forged_payload = {
        "jsonrpc": "2.0",
        "id": 702,
        "method": "tools/call",
        "params": {
            "name": "audit_and_redline_contract",
            "arguments": {
                "contract_text": "1. Customer liability shall be uncapped and unlimited for all claims.",
                "api_key": "cg_pro_forged_attacker_key",
            },
        },
    }
    r2 = client.post("/mcp", headers=headers, json=forged_payload)
    assert r2.status_code == 200
    assert r2.json()["result"]["isError"] is True
    assert "buy.stripe.com" in r2.json()["result"]["content"][0]["text"]
    assert r2.json()["result"]["structuredContent"]["code"] == "FREE_QUOTA_EXCEEDED"

    valid_payload = {
        "jsonrpc": "2.0",
        "id": 703,
        "method": "tools/call",
        "params": {
            "name": "audit_and_redline_contract",
            "arguments": {
                "contract_text": "1. Customer liability shall be uncapped and unlimited for all claims.",
                "api_key": signed_key,
            },
        },
    }
    r3 = client.post("/mcp", headers=headers, json=valid_payload)
    assert r3.status_code == 200
    assert r3.json()["result"]["isError"] is False
    assert r3.json()["result"]["structuredContent"]["quota"]["tier"] == "pro"
    assert "Not Legal Advice" in r3.json()["result"]["structuredContent"]["disclaimer"]
    assert "Playbook Alignment Summary:" in r3.json()["result"]["structuredContent"]["sign_off_recommendation"]

    tampered_key = signed_key[:-1] + ("0" if signed_key[-1] != "0" else "1")
    assert is_pro_credential(tampered_key, None) is False

    priv_html = client.get("/privacy").text
    for term in (
        "audit_and_redline_contract",
        "autofill_security_questionnaire",
        "compare_contract_versions",
        "Purposes of Data Processing",
        "Recipients",
        "Data Retention",
        "User Controls",
        "Not Legal Advice",
    ):
        assert term in priv_html

    chatgpt_headers = {"X-Client-Id": "chatgpt-action-quota-test"}
    cg1 = client.post(
        "/api/chatgpt/audit",
        headers=chatgpt_headers,
        json={"contract_text": "1. Customer liability shall be uncapped and unlimited."},
    )
    assert cg1.status_code == 200
    assert "redlined_docx_b64" not in cg1.json()["audit"]
    assert "Not Legal Advice" in cg1.json()["audit"]["disclaimer"]

    cg2 = client.post(
        "/api/chatgpt/audit",
        headers=chatgpt_headers,
        json={"contract_text": "1. Customer liability shall be uncapped and unlimited."},
    )
    assert cg2.status_code == 402
    assert cg2.json()["code"] == "FREE_QUOTA_EXCEEDED"

    tools_list = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 801, "method": "tools/list", "params": {}},
    ).json()["result"]["tools"]
    audit_tool_def = next(t for t in tools_list if t["name"] == "audit_and_redline_contract")
    audit_schema_dump = json.dumps(audit_tool_def)
    for forbidden_trigger in ("HIPAA BAA", "GDPR DPA", "qualified attorney", "Contract_Redlined.docx"):
        assert forbidden_trigger not in audit_schema_dump

    alias_resp = client.post(
        "/mcp",
        headers={"X-Client-Id": "alias-test-client"},
        json={
            "jsonrpc": "2.0",
            "id": 802,
            "method": "tools/call",
            "params": {
                "name": "compare_agreement_to_playbook",
                "arguments": {
                    "contract_text": "1. Customer liability shall be uncapped and unlimited.",
                    "playbook": "founder_friendly",
                },
            },
        },
    )
    assert alias_resp.status_code == 200
    assert alias_resp.json()["result"]["isError"] is False

    plugin_json = json.loads((ROOT_DIR / "openai_plugin_package" / "plugin.json").read_text(encoding="utf-8"))
    assert plugin_json["version"] == "1.0.4"
    plugin_dump = json.dumps(plugin_json["extensions"]["com.openai"]["review"]["test_cases"]["positive"])
    for forbidden_claim in ("HIPAA compliance gaps", "GDPR-compliant replacement"):
        assert forbidden_claim not in plugin_dump

    # 1. Verify GET /chatgpt-openapi.json v1.0.4, Agreement_Track_Changes.docx default, and non-legal-advice disclosures
    openapi_resp = client.get("/chatgpt-openapi.json")
    assert openapi_resp.status_code == 200
    openapi_body = openapi_resp.json()
    assert openapi_body["info"]["version"] == "1.0.4"
    audit_op = openapi_body["paths"]["/api/chatgpt/audit"]["post"]
    assert audit_op["x-openai-isConsequential"] is False
    assert (
        audit_op["requestBody"]["content"]["application/json"]["schema"]["properties"]["contract_name"]["default"]
        == "Agreement_Track_Changes.docx"
    )
    assert "not legal advice" in audit_op["summary"].lower()

    # 2. Verify 0-findings, moderate-only, and gdpr_dpa checklist branches in audit_engine
    from clauseguard_mcp.audit_engine import audit_and_redline_contract
    from clauseguard_mcp.models import AuditContractRequest
    from clauseguard_mcp.playbooks import SAMPLE_CONTRACTS

    clean_res = audit_and_redline_contract(
        AuditContractRequest(
            contract_text=(
                "1. LIMITATION OF LIABILITY. Mutual liability is capped at 12 months of fees. "
                "2. TERMINATION FOR CAUSE. Either party may terminate for material breach with a 30-day cure period. "
                "3. FORCE MAJEURE. Neither party is liable for delays beyond reasonable control."
            )
        )
    )
    assert clean_res.contract_name == "Agreement_Track_Changes.docx"
    assert "0 commercial checklist variances detected" in clean_res.sign_off_recommendation
    assert "low checklist variance score" in clean_res.executive_summary

    mod_res = audit_and_redline_contract(
        AuditContractRequest(
            contract_text="Customer shall not solicit or hire any employee anywhere in the world for a period of 4 years."
        )
    )
    assert "Minor commercial checklist variances noted" in mod_res.sign_off_recommendation

    dpa_res = audit_and_redline_contract(
        AuditContractRequest(
            contract_text=SAMPLE_CONTRACTS["gdpr_dpa"]["text"],
            playbook="gdpr_dpa",
        )
    )
    assert any("Standard commercial data-handling checklists" in w.why_it_matters for w in dpa_res.missing_clauses)
    assert any("Standard enterprise" in f.rationale for f in dpa_res.findings)

    # 3. Verify GET /openai-plugin.zip archive sync with plugin.json v1.0.4, <=30 char shortDescription, 3 negative test cases, and no screenshots
    zip_resp = client.get("/openai-plugin.zip")
    assert zip_resp.status_code == 200
    with zipfile.ZipFile(io.BytesIO(zip_resp.content), "r") as zf:
        archived_plugin = json.loads(zf.read("plugin.json").decode("utf-8"))
        assert archived_plugin["version"] == "1.0.4"
        iface = archived_plugin["extensions"]["com.openai"]["interface"]
        assert "screenshots" not in iface
        assert len(iface["shortDescription"]) <= 30
        assert len(archived_plugin["extensions"]["com.openai"]["review"]["test_cases"]["negative"]) == 3
        assert "mcp.json" in zf.namelist()

