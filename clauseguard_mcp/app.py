"""FastAPI Application & Entrypoint for ClauseGuard MCP on Port 8792."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from fastapi import FastAPI, Header, Query, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import ValidationError
import uvicorn

from clauseguard_mcp.analytics import (
    detect_source,
    get_analytics_snapshot,
    record_event,
    render_analytics_html,
)
from clauseguard_mcp.audit_engine import (
    audit_and_redline_contract,
    build_custom_redlined_docx,
)
from clauseguard_mcp.docx_engine import (
    extract_text_from_b64_docx,
    get_docx_artifact,
    get_docx_by_filename,
)
from clauseguard_mcp.mcp_protocol import (
    MCP_PROTOCOL_VERSION,
    MCP_TOOLS_CATALOG,
    handle_mcp_jsonrpc,
)
from clauseguard_mcp.models import (
    AuditContractRequest,
    CompareVersionsRequest,
    CustomDocxRequest,
    QuestionnaireRequest,
)
from clauseguard_mcp.oauth import (
    PRO_PRICE_LABEL,
    check_and_consume_quota,
    exchange_code_for_token,
    get_oauth_metadata,
    issue_authorization_code,
)
from clauseguard_mcp.playbooks import (
    SAMPLE_CONTRACTS,
    SAMPLE_DIFF_VERSIONS,
    SAMPLE_QUESTIONNAIRE,
)
from clauseguard_mcp.questionnaire_engine import (
    autofill_security_questionnaire,
    compare_contract_versions,
)
from clauseguard_mcp.studio_pages import render_about_html, render_docs_html
from clauseguard_mcp.studio_ui import (
    render_privacy_html,
    render_studio_html,
    render_terms_html,
)


ROOT_DIR = Path(__file__).resolve().parent.parent
_OPENAI_CHALLENGE_STATE: dict[str, str] = {
    "token": os.environ.get(
        "OPENAI_APPS_CHALLENGE",
        "jDYn4kfcZr0xfWceFTluiSzrrbhKoQiuKn3d_MPUPNE",
    ).strip()
}


def create_app() -> FastAPI:
    """Create and configure the ClauseGuard MCP FastAPI application."""
    app = FastAPI(
        title="ClauseGuard MCP",
        version="1.0.0",
        docs_url="/openapi-docs",
        description=(
            "Commercial Contract Review, Playbook Redlining (Microsoft Word Track Changes .docx), "
            "Draft Comparison & Security Questionnaire Desk."
        ),
    )

    @app.get("/", response_class=HTMLResponse)
    def get_studio(request: Request) -> HTMLResponse:
        if "pro_activated=1" in str(request.url.query):
            record_event(event_type="pro_unlock", source="Web Desk", detail="Stripe Redirect")
        else:
            record_event(event_type="page_view", source="Web Desk", detail="/")
        return HTMLResponse(content=render_studio_html())

    @app.get("/analytics", response_class=HTMLResponse)
    def get_analytics_page() -> HTMLResponse:
        return HTMLResponse(content=render_analytics_html())

    @app.get("/api/analytics")
    def get_analytics_json() -> dict[str, Any]:
        return get_analytics_snapshot()

    @app.get("/about", response_class=HTMLResponse)
    def get_about() -> HTMLResponse:
        return HTMLResponse(content=render_about_html())

    @app.get("/docs", response_class=HTMLResponse)
    @app.get("/documentation", response_class=HTMLResponse)
    def get_public_docs() -> HTMLResponse:
        return HTMLResponse(content=render_docs_html())

    @app.get("/privacy", response_class=HTMLResponse)
    def get_privacy() -> HTMLResponse:
        return HTMLResponse(content=render_privacy_html())

    @app.get("/terms", response_class=HTMLResponse)
    def get_terms() -> HTMLResponse:
        return HTMLResponse(content=render_terms_html())

    @app.get("/health")
    def get_health() -> dict[str, Any]:
        return {"status": "healthy", "service": "ClauseGuard MCP", "port": 8792}

    @app.get("/favicon.svg")
    def get_favicon_svg() -> Response:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
            '<rect width="48" height="48" rx="11" fill="#09221F" stroke="#1B6E66" stroke-width="2"/>'
            '<path d="M24 6L38 10.5V24.5C38 33.5 32 39.5 24 43C16 39.5 10 33.5 10 24.5V10.5L24 6Z" fill="#134E4A" stroke="#5ED4C6" stroke-width="1.5"/>'
            '<rect x="14" y="11" width="20" height="24" rx="3" fill="#F8FAFC"/>'
            '<rect x="16.5" y="14" width="10" height="2" rx="1" fill="#0F172A"/>'
            '<rect x="16.5" y="18" width="15" height="4" rx="1.5" fill="#FEE2E2"/>'
            '<rect x="18" y="19.3" width="12" height="1.4" rx="0.7" fill="#DC2626"/>'
            '<rect x="16.5" y="23.5" width="15" height="4" rx="1.5" fill="#D1FAE5"/>'
            '<rect x="18" y="24.8" width="12" height="1.4" rx="0.7" fill="#059669"/>'
            '<circle cx="33.5" cy="33.5" r="6.5" fill="#10B981" stroke="#F8FAFC" stroke-width="1.5"/>'
            '<path d="M30.8 33.6L32.6 35.4L36.4 31.6" stroke="#FFFFFF" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            "</svg>"
        )
        return Response(content=svg, media_type="image/svg+xml")

    @app.get("/favicon.ico")
    def get_favicon_ico() -> Response:
        ico_path = ROOT_DIR / "openai_plugin_package" / "assets" / "favicon.ico"
        if ico_path.exists():
            return Response(content=ico_path.read_bytes(), media_type="image/x-icon")
        return get_favicon_svg()

    @app.get("/icon.png")
    @app.get("/apple-touch-icon.png")
    def get_icon_png() -> Response:
        png_path = ROOT_DIR / "openai_plugin_package" / "assets" / "icon.png"
        return Response(content=png_path.read_bytes(), media_type="image/png")

    @app.get("/.well-known/openai-apps-challenge", response_class=PlainTextResponse)
    def get_openai_challenge() -> PlainTextResponse:
        token = _OPENAI_CHALLENGE_STATE.get("token") or os.environ.get("OPENAI_APPS_CHALLENGE", "").strip()
        return PlainTextResponse(content=token)

    @app.post("/api/admin/openai-challenge")
    async def set_openai_challenge(request: Request) -> JSONResponse:
        raw = await request.json()
        token = str(raw.get("token", "")).strip()
        _OPENAI_CHALLENGE_STATE["token"] = token
        return JSONResponse(status_code=200, content={"success": True, "token": token})

    @app.get("/openai-plugin.zip")
    def download_openai_plugin_zip() -> Response:
        zip_path = ROOT_DIR / "clauseguard-openai-plugin.zip"
        if not zip_path.exists():
            return JSONResponse(status_code=404, content={"error": "ZIP not found"})
        return Response(
            content=zip_path.read_bytes(),
            media_type="application/zip",
            headers={"Content-Disposition": 'attachment; filename="clauseguard-openai-plugin.zip"'},
        )

    @app.get("/.well-known/oauth-authorization-server")
    def oauth_discovery(request: Request) -> Response:
        base_url = str(request.base_url).rstrip("/")
        if (
            request.headers.get("x-forwarded-proto") == "https" or "railway.app" in base_url
        ) and request.query_params.get("oauth") != "1":
            return JSONResponse(status_code=404, content={"detail": "No authentication required for this MCP server."})
        return JSONResponse(status_code=200, content=get_oauth_metadata(base_url))

    @app.get("/oauth/authorize")
    def oauth_authorize(
        response_type: str = Query(default="code"),
        client_id: str = Query(...),
        redirect_uri: str = Query(...),
        code_challenge: str = Query(...),
        code_challenge_method: str = Query(default="S256"),
        scope: str = Query(default="mcp:tools"),
        state: str | None = Query(default=None),
    ) -> JSONResponse:
        if response_type != "code":
            return JSONResponse(
                status_code=400,
                content={"error": "unsupported_response_type", "error_description": "Use response_type=code"},
            )
        try:
            grant = issue_authorization_code(
                client_id=client_id,
                redirect_uri=redirect_uri,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
                scope=scope,
                state=state,
            )
            return JSONResponse(status_code=200, content=grant)
        except ValueError as exc:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "error_description": str(exc)},
            )

    @app.post("/oauth/token")
    async def oauth_token(request: Request) -> JSONResponse:
        raw_body = (await request.body()).decode("utf-8", errors="replace").strip()
        content_type = request.headers.get("content-type", "")
        params: dict[str, str] = {}
        if "application/json" in content_type or raw_body.startswith("{"):
            try:
                parsed_json = json.loads(raw_body)
                if isinstance(parsed_json, dict):
                    params = {str(k): str(v) for k, v in parsed_json.items() if v is not None}
            except Exception:
                params = {}
        else:
            qs = parse_qs(raw_body, keep_blank_values=True)
            params = {k: v[0] for k, v in qs.items() if v}

        if params.get("grant_type") != "authorization_code":
            return JSONResponse(status_code=400, content={"error": "unsupported_grant_type"})
        try:
            token_data = exchange_code_for_token(
                code=params.get("code", ""),
                code_verifier=params.get("code_verifier", ""),
                client_id=params.get("client_id", ""),
                redirect_uri=params.get("redirect_uri", ""),
            )
            return JSONResponse(status_code=200, content=token_data)
        except ValueError as exc:
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_grant", "error_description": str(exc)},
            )

    @app.get("/mcp")
    def mcp_stream_info() -> dict[str, Any]:
        return {
            "name": "ClauseGuard MCP",
            "version": "1.0.0",
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "transport": "streamable-http",
            "endpoint": "/mcp",
            "oauth_metadata": "/.well-known/oauth-authorization-server",
            "tools": [t["name"] for t in MCP_TOOLS_CATALOG],
        }

    @app.post("/mcp")
    async def mcp_jsonrpc_endpoint(request: Request) -> Response:
        try:
            payload = await request.json()
        except Exception:
            return JSONResponse(
                status_code=200,
                content={"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
            )
        if isinstance(payload, list):
            results = []
            for item in payload:
                if isinstance(item, dict) and item.get("id") is None and str(item.get("method", "")).startswith("notifications/"):
                    continue
                if isinstance(item, dict):
                    results.append(handle_mcp_jsonrpc(item))
            if not results:
                return Response(status_code=202)
            return JSONResponse(status_code=200, content=results)

        method = str(payload.get("method", ""))
        params = payload.get("params") or {}
        client_info = params.get("clientInfo") or {}
        src = detect_source(
            request.headers.get("user-agent", ""),
            path="/mcp",
            client_name=str(client_info.get("name", "")),
        )
        if method in ("initialize", "tools/list"):
            record_event(event_type="mcp_connect", source=src, detail=method)
        elif method == "tools/call":
            t_name = str(params.get("name", "-"))
            t_args = params.get("arguments") or {}
            pb = str(t_args.get("playbook", "")) if isinstance(t_args, dict) else ""
            record_event(event_type="tool_call", source=src, tool_name=t_name, detail=pb or "MCP tool")

        if payload.get("id") is None and method.startswith("notifications/"):
            return Response(status_code=202)

        return JSONResponse(status_code=200, content=handle_mcp_jsonrpc(payload))

    @app.get("/api/samples")
    def get_samples() -> dict[str, Any]:
        return {
            "contracts": SAMPLE_CONTRACTS,
            "questionnaire": list(SAMPLE_QUESTIONNAIRE),
            "diff_versions": SAMPLE_DIFF_VERSIONS,
        }

    @app.get("/api/quota")
    def get_quota_status(
        x_client_id: str = Header(default="anonymous"),
        x_clauseguard_key: str | None = Header(default=None),
        authorization: str | None = Header(default=None),
    ) -> dict[str, Any]:
        q = check_and_consume_quota(
            client_id=x_client_id,
            api_key=x_clauseguard_key,
            bearer_token=authorization,
            consume=False,
        )
        return q.__dict__

    @app.post("/api/extract-docx")
    async def api_extract_docx(request: Request) -> JSONResponse:
        try:
            raw = await request.json()
            b64 = str(raw.get("docx_base64", "")).strip()
            text = extract_text_from_b64_docx(b64)
            return JSONResponse(status_code=200, content={"success": True, "text": text})
        except Exception as exc:
            return JSONResponse(status_code=422, content={"success": False, "error": str(exc)})

    @app.post("/api/docx/custom")
    async def api_custom_docx(request: Request) -> JSONResponse:
        try:
            raw = await request.json()
            req = CustomDocxRequest(**raw)
            out = build_custom_redlined_docx(req)
            return JSONResponse(status_code=200, content={"success": True, **out})
        except (ValidationError, ValueError) as exc:
            return JSONResponse(status_code=422, content={"success": False, "error": str(exc)})

    @app.post("/api/audit")
    async def api_audit_contract(
        request: Request,
        x_client_id: str = Header(default="anonymous"),
        x_clauseguard_key: str | None = Header(default=None),
        authorization: str | None = Header(default=None),
    ) -> JSONResponse:
        try:
            raw = await request.json()
            audit_req = AuditContractRequest(**raw)
        except (ValidationError, ValueError) as exc:
            return JSONResponse(
                status_code=422,
                content={"success": False, "error": str(exc), "code": "VALIDATION_ERROR"},
            )

        quota = check_and_consume_quota(
            client_id=x_client_id,
            api_key=x_clauseguard_key,
            bearer_token=authorization,
            consume=True,
        )
        if not quota.allowed:
            return JSONResponse(
                status_code=402,
                content={
                    "success": False,
                    "code": "FREE_QUOTA_EXCEEDED",
                    "error": (
                        f"You have used your 1 complimentary agreement review for this month. "
                        f"Switch to the Professional Plan ({PRO_PRICE_LABEL}) for unlimited agreement "
                        "reviews, custom redline exports, and security questionnaire responses."
                    ),
                    "quota": quota.__dict__,
                },
            )

        res = audit_and_redline_contract(audit_req)
        src = detect_source(request.headers.get("user-agent", ""), path="/api/audit")
        record_event(
            event_type="tool_call",
            source=src,
            tool_name="audit_and_redline_contract",
            detail=audit_req.playbook,
        )
        audit_dict = res.model_dump(mode="json")
        audit_dict["public_download_url"] = f"https://clauseguard-mcp-production.up.railway.app{res.download_url}"
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "quota": quota.__dict__,
                "audit": audit_dict,
            },
        )

    @app.post("/api/questionnaire")
    async def api_questionnaire(request: Request) -> JSONResponse:
        try:
            raw = await request.json()
            q_req = QuestionnaireRequest(**raw)
            res = autofill_security_questionnaire(q_req)
            src = detect_source(request.headers.get("user-agent", ""), path="/api/questionnaire")
            record_event(
                event_type="tool_call",
                source=src,
                tool_name="autofill_security_questionnaire",
                detail=f"{len(q_req.items)} items",
            )
            return JSONResponse(status_code=200, content={"success": True, "result": res.model_dump(mode="json")})
        except (ValidationError, ValueError) as exc:
            return JSONResponse(status_code=422, content={"success": False, "error": str(exc)})

    @app.post("/api/compare")
    async def api_compare(request: Request) -> JSONResponse:
        try:
            raw = await request.json()
            c_req = CompareVersionsRequest(**raw)
            res = compare_contract_versions(c_req)
            src = detect_source(request.headers.get("user-agent", ""), path="/api/compare")
            record_event(
                event_type="tool_call",
                source=src,
                tool_name="compare_contract_versions",
                detail="draft diff",
            )
            return JSONResponse(status_code=200, content={"success": True, "result": res.model_dump(mode="json")})
        except (ValidationError, ValueError) as exc:
            return JSONResponse(status_code=422, content={"success": False, "error": str(exc)})

    @app.get("/api/docx/{doc_id}")
    def download_docx(doc_id: str, request: Request) -> Response:
        artifact = get_docx_artifact(doc_id)
        if artifact is None:
            return JSONResponse(status_code=404, content={"error": "Document artifact not found"})
        filename, docx_bytes = artifact
        src = detect_source(request.headers.get("user-agent", ""), path="/api/docx")
        record_event(event_type="docx_download", source=src, tool_name="download_docx", detail=filename)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.get("/downloads/{filename}")
    def download_docx_by_name(filename: str, request: Request) -> Response:
        artifact = get_docx_by_filename(filename)
        if artifact is None:
            return JSONResponse(status_code=404, content={"error": "Document artifact not found"})
        safe_name, docx_bytes = artifact
        src = detect_source(request.headers.get("user-agent", ""), path="/downloads")
        record_event(event_type="docx_download", source=src, tool_name="download_docx", detail=safe_name)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
        )

    @app.get("/manifests/claude")
    def get_claude_manifest() -> JSONResponse:
        path = ROOT_DIR / "claude-connector-manifest.json"
        return JSONResponse(content=json.loads(path.read_text(encoding="utf-8")))

    @app.get("/manifests/openai")
    def get_openai_manifest() -> JSONResponse:
        path = ROOT_DIR / "openai-mcp-app.json"
        return JSONResponse(content=json.loads(path.read_text(encoding="utf-8")))

    @app.post("/api/chatgpt/audit")
    async def api_chatgpt_audit(request: Request) -> JSONResponse:
        try:
            raw = await request.json()
            audit_req = AuditContractRequest(**raw)
        except (ValidationError, ValueError) as exc:
            return JSONResponse(status_code=422, content={"success": False, "error": str(exc)})
        res = audit_and_redline_contract(audit_req)
        record_event(
            event_type="tool_call",
            source="ChatGPT",
            tool_name="audit_and_redline_contract",
            detail=audit_req.playbook,
        )
        audit_dict = res.model_dump(mode="json", exclude={"docx_base64"})
        audit_dict["public_download_url"] = f"https://clauseguard-mcp-production.up.railway.app{res.download_url}"
        audit_dict["web_review_desk_url"] = "https://clauseguard-mcp-production.up.railway.app"
        return JSONResponse(status_code=200, content={"success": True, "audit": audit_dict})

    @app.get("/chatgpt-openapi.json")
    def get_chatgpt_openapi() -> JSONResponse:
        ok_resp = {
            "200": {
                "description": "Successful plain-English review response.",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                            },
                        }
                    }
                },
            }
        }
        return JSONResponse(
            content={
                "openapi": "3.1.0",
                "info": {
                    "title": "ClauseGuard: Contract Redlines",
                    "description": "Review commercial agreements in plain English, generate Microsoft Word (.docx) files with native Track Changes, compare contract versions, and complete customer security questionnaires.",
                    "version": "1.0.0",
                },
                "servers": [{"url": "https://clauseguard-mcp-production.up.railway.app"}],
                "paths": {
                    "/api/chatgpt/audit": {
                        "post": {
                            "operationId": "auditAndRedlineContract",
                            "summary": "Review a contract against a negotiation playbook and generate a downloadable Word (.docx) file with Track Changes.",
                            "x-openai-isConsequential": False,
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "required": ["contract_text"],
                                            "properties": {
                                                "contract_text": {
                                                    "type": "string",
                                                    "description": "Full plain-text wording of the commercial contract to review and redline.",
                                                },
                                                "playbook": {
                                                    "type": "string",
                                                    "enum": ["founder_friendly", "saas_vendor", "gdpr_dpa", "hipaa_baa"],
                                                    "default": "founder_friendly",
                                                    "description": "Negotiation playbook to apply: founder_friendly, saas_vendor, gdpr_dpa, or hipaa_baa.",
                                                },
                                                "contract_name": {
                                                    "type": "string",
                                                    "default": "Agreement_Redlined.docx",
                                                    "description": "Filename for the generated Microsoft Word (.docx) Track Changes document.",
                                                },
                                            },
                                        }
                                    }
                                },
                            },
                            "responses": ok_resp,
                        }
                    },
                    "/api/questionnaire": {
                        "post": {
                            "operationId": "autofillSecurityQuestionnaire",
                            "summary": "Complete customer security and privacy questionnaire items in plain English.",
                            "x-openai-isConsequential": False,
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
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
                                                            "id": {"type": "string", "description": "Question identifier (e.g., Q-01)."},
                                                            "question": {"type": "string", "description": "Full text of the security question."},
                                                        },
                                                    },
                                                }
                                            },
                                        }
                                    }
                                },
                            },
                            "responses": ok_resp,
                        }
                    },
                    "/api/compare": {
                        "post": {
                            "operationId": "compareContractVersions",
                            "summary": "Compare two agreement drafts and highlight material financial or legal risk shifts.",
                            "x-openai-isConsequential": False,
                            "requestBody": {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "required": ["version_a_text", "version_b_text"],
                                            "properties": {
                                                "version_a_text": {"type": "string", "description": "Original baseline contract draft text."},
                                                "version_b_text": {"type": "string", "description": "Revised counterparty contract draft text."},
                                                "version_a_name": {"type": "string", "default": "Initial_Agreement_Draft.docx", "description": "Baseline draft filename."},
                                                "version_b_name": {"type": "string", "default": "Counterparty_Returned_Markup.docx", "description": "Revised draft filename."},
                                            },
                                        }
                                    }
                                },
                            },
                            "responses": ok_resp,
                        }
                    },
                },
            }
        )

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run("clauseguard_mcp.app:app", host="0.0.0.0", port=8792, reload=False)
