"""Streamable HTTP MCP Protocol Handler (JSON-RPC 2.0) for Claude & ChatGPT Connectors."""

from __future__ import annotations

import json
from typing import Any
from pydantic import ValidationError

from clauseguard_mcp.audit_engine import audit_and_redline_contract
from clauseguard_mcp.docx_engine import sanitize_docx_filename
from clauseguard_mcp.models import (
    AuditContractRequest,
    CompareVersionsRequest,
    QuestionnaireRequest,
)
from clauseguard_mcp.questionnaire_engine import (
    autofill_security_questionnaire,
    compare_contract_versions,
)


MCP_PROTOCOL_VERSION = "2025-03-26"

MCP_TOOLS_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "name": "audit_and_redline_contract",
        "title": "Review & Redline Contract",
        "description": (
            "Analyzes commercial agreements (MSA, Mutual NDA, SaaS Subscription, or Data Processing "
            "Agreement) in plain English against a negotiation playbook, calculates a 0–100 risk score, "
            "flags missing protections, and returns clause-by-clause replacement wording and a draft "
            "counterparty negotiation summary without modifying external systems."
        ),
        "annotations": {
            "title": "Review & Redline Contract",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "required": ["contract_text"],
            "properties": {
                "contract_text": {
                    "type": "string",
                    "description": "Full plain-text wording of the commercial contract to review.",
                },
                "playbook": {
                    "type": "string",
                    "enum": ["founder_friendly", "saas_vendor", "gdpr_dpa", "hipaa_baa"],
                    "default": "founder_friendly",
                    "description": "Negotiation playbook to evaluate against: founder_friendly, saas_vendor, gdpr_dpa, or hipaa_baa.",
                },
                "contract_name": {
                    "type": "string",
                    "default": "Contract_Redlined.docx",
                    "description": "Document label for the contract review report.",
                },
                "author": {
                    "type": "string",
                    "default": "ClauseGuard Legal Desk",
                    "description": "Reviewer label displayed in the redline summary.",
                },
            },
        },
    },
    {
        "name": "autofill_security_questionnaire",
        "title": "Complete Security Questionnaire",
        "description": (
            "Drafts plain-English security and privacy responses, control evidence citations, and "
            "confidence ratings for customer due-diligence questionnaires across SOC 2 Type II, "
            "GDPR, HIPAA, ISO 27001, encryption, incident response, access control, and resilience."
        ),
        "annotations": {
            "title": "Complete Security Questionnaire",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "description": "List of customer security or privacy questionnaire items to answer.",
                    "items": {
                        "type": "object",
                        "required": ["id", "question"],
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Question identifier or row number (for example, Q-01).",
                            },
                            "question": {
                                "type": "string",
                                "description": "Full text of the customer security or compliance question.",
                            },
                            "category_hint": {
                                "type": "string",
                                "description": "Optional topic hint such as encryption, soc2, gdpr, hipaa, or incident_response.",
                            },
                        },
                    },
                },
                "profile": {
                    "type": "object",
                    "description": "Optional organization security posture overrides (such as encryption standard or breach notification window).",
                },
            },
        },
    },
    {
        "name": "compare_contract_versions",
        "title": "Compare Two Contract Drafts",
        "description": (
            "Compares an earlier contract draft against a counterparty markup clause-by-clause and "
            "flags material business or legal shifts such as uncapped liability, extended payment "
            "windows, changed governing law, multi-year auto-renewals, and one-sided indemnity."
        ),
        "annotations": {
            "title": "Compare Two Contract Drafts",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "required": ["version_a_text", "version_b_text"],
            "properties": {
                "version_a_text": {
                    "type": "string",
                    "description": "Full text of the original baseline contract draft (Version A).",
                },
                "version_b_text": {
                    "type": "string",
                    "description": "Full text of the revised or counterparty-returned contract draft (Version B).",
                },
                "version_a_name": {
                    "type": "string",
                    "default": "Baseline_Draft_v1.docx",
                    "description": "Label or filename for the baseline contract draft.",
                },
                "version_b_name": {
                    "type": "string",
                    "default": "Counterparty_Markup_v2.docx",
                    "description": "Label or filename for the revised counterparty contract draft.",
                },
            },
        },
    },
)


def handle_mcp_jsonrpc(payload: dict[str, Any]) -> dict[str, Any]:
    """Process a single JSON-RPC 2.0 request for the Streamable HTTP /mcp endpoint."""
    rpc_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params") or {}

    if payload.get("jsonrpc") != "2.0" or not isinstance(method, str):
        return _rpc_error(rpc_id, -32600, "Invalid JSON-RPC 2.0 request envelope.")

    if method == "initialize":
        return _rpc_result(
            rpc_id,
            {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {
                    "name": "ClauseGuard MCP",
                    "version": "1.0.0",
                    "description": "Contract Redlining (.docx Word Track Changes) & Security Questionnaire MCP Server",
                },
            },
        )

    if method in ("notifications/initialized", "ping"):
        return _rpc_result(rpc_id, {"status": "ok"})

    if method == "tools/list":
        return _rpc_result(rpc_id, {"tools": list(MCP_TOOLS_CATALOG)})

    if method == "tools/call":
        return _dispatch_tool_call(rpc_id, params)

    return _rpc_error(rpc_id, -32601, f"Method not found: {method}")


def _dispatch_tool_call(rpc_id: Any, params: dict[str, Any]) -> dict[str, Any]:
    tool_name = params.get("name")
    arguments = params.get("arguments") or {}

    try:
        if tool_name == "audit_and_redline_contract":
            req = AuditContractRequest(**arguments) if isinstance(arguments, dict) else AuditContractRequest(contract_text=str(arguments))
            res = audit_and_redline_contract(req)
            data = res.model_dump(mode="json")
            safe_fn = sanitize_docx_filename(res.contract_name)
            friendly_docx_url = f"https://clauseguard-mcp-production.up.railway.app/downloads/{safe_fn}"
            public_docx_url = f"https://clauseguard-mcp-production.up.railway.app{res.download_url}"
            data["download_docx_url"] = friendly_docx_url
            data["public_download_url"] = public_docx_url
            text_summary = (
                f"{res.sign_off_recommendation}\n"
                f"{res.executive_summary}\n"
                f"Download Word (.docx) with Track Changes: {friendly_docx_url}"
            )
            return _tool_success(rpc_id, text_summary, data)

        if tool_name == "autofill_security_questionnaire":
            req_q = (
                QuestionnaireRequest(**arguments)
                if isinstance(arguments, dict)
                else QuestionnaireRequest.model_validate(arguments)
            )
            res_q = autofill_security_questionnaire(req_q)
            data_q = res_q.model_dump(mode="json")
            text_q = (
                f"Auto-completed {res_q.auto_completed_count}/{res_q.total_items} security questionnaire "
                f"items for {res_q.company_name} (avg confidence: {res_q.average_confidence:.0%})."
            )
            return _tool_success(rpc_id, text_q, data_q)

        if tool_name == "compare_contract_versions":
            req_c = (
                CompareVersionsRequest(**arguments)
                if isinstance(arguments, dict)
                else CompareVersionsRequest.model_validate(arguments)
            )
            res_c = compare_contract_versions(req_c)
            data_c = res_c.model_dump(mode="json")
            return _tool_success(rpc_id, res_c.summary, data_c)

        return _rpc_error(rpc_id, -32602, f"Unknown MCP tool: {tool_name}")
    except (ValidationError, ValueError) as exc:
        return _rpc_error(rpc_id, -32602, f"Invalid tool arguments: {exc}")


def _tool_success(rpc_id: Any, summary_text: str, structured: dict[str, Any]) -> dict[str, Any]:
    return _rpc_result(
        rpc_id,
        {
            "isError": False,
            "content": [
                {"type": "text", "text": summary_text},
                {"type": "text", "text": json.dumps(structured)},
            ],
            "structuredContent": structured,
        },
    )


def _rpc_result(rpc_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": rpc_id, "result": result}


def _rpc_error(rpc_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": code, "message": message}}
