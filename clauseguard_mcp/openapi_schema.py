"""OpenAPI 3.1.0 Specification Builder for ClauseGuard ChatGPT Actions (/chatgpt-openapi.json)."""

from __future__ import annotations

from typing import Any


def build_chatgpt_openapi_spec() -> dict[str, Any]:
    """Return the OpenAPI 3.1.0 schema for ClauseGuard with explicit non-legal-advice disclosures."""
    ok_resp = {
        "200": {
            "description": "Successful plain-English commercial checklist comparison response (informational only — not legal advice).",
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
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "ClauseGuard: Contract Redlines",
            "description": (
                "Compare commercial agreement drafts against standard commercial playbooks in plain English, "
                "format Microsoft Word (.docx) files with native Track Changes, compare draft versions, and "
                "draft customer security questionnaire responses. Informational checklist & document formatting "
                "utility only — does not provide legal advice or substitute for review by a licensed attorney."
            ),
            "version": "1.0.3",
        },
        "servers": [{"url": "https://clauseguard-mcp-production.up.railway.app"}],
        "paths": {
            "/api/chatgpt/audit": {
                "post": {
                    "operationId": "auditAndRedlineContract",
                    "summary": (
                        "Compare a commercial contract draft against a selected playbook checklist and format a "
                        "downloadable Word (.docx) file with Track Changes (informational checklist only — not legal advice)."
                    ),
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
                                            "description": "Full plain-text wording of the commercial contract draft to compare.",
                                        },
                                        "playbook": {
                                            "type": "string",
                                            "enum": ["founder_friendly", "saas_vendor", "gdpr_dpa", "hipaa_baa"],
                                            "default": "founder_friendly",
                                            "description": "Commercial checklist to apply: founder_friendly, saas_vendor, gdpr_dpa, or hipaa_baa.",
                                        },
                                        "contract_name": {
                                            "type": "string",
                                            "default": "Agreement_Redlined.docx",
                                            "description": "Filename for the generated Microsoft Word (.docx) Track Changes document.",
                                        },
                                        "api_key": {
                                            "type": "string",
                                            "description": "Optional ClauseGuard Professional Plan API key for unlimited monthly reviews.",
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
                    "summary": "Draft customer security and privacy questionnaire responses in plain English (informational helper only).",
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
                    "summary": "Compare two agreement drafts clause-by-clause and highlight commercial text changes (informational diff only — not legal advice).",
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
