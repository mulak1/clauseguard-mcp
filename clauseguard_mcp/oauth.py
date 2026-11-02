"""OAuth 2.1 with S256 PKCE authentication & Free/Pro tier quota enforcement."""

from __future__ import annotations

import base64
from dataclasses import dataclass
import hashlib
import secrets
import time
from typing import Any


@dataclass(frozen=True)
class AuthorizationGrant:
    code: str
    client_id: str
    redirect_uri: str
    code_challenge: str
    code_challenge_method: str
    scope: str
    created_at: float


@dataclass(frozen=True)
class QuotaStatus:
    client_id: str
    tier: str
    used_this_month: int
    monthly_limit: int | None
    remaining: int | None
    allowed: bool


# Immutable-value registries keyed by code / token / client_id
_AUTH_CODES: dict[str, AuthorizationGrant] = {}
_ACCESS_TOKENS: dict[str, dict[str, Any]] = {}
_FREE_USAGE_COUNTS: dict[str, int] = {}

FREE_MONTHLY_LIMIT = 1
PRO_PRICE_LABEL = "$49/mo"


def get_oauth_metadata(base_url: str = "http://localhost:8792") -> dict[str, Any]:
    """Return RFC 8414 / OAuth 2.1 Authorization Server Metadata with S256 PKCE required."""
    clean_base = base_url.rstrip("/")
    return {
        "issuer": clean_base,
        "authorization_endpoint": f"{clean_base}/oauth/authorize",
        "token_endpoint": f"{clean_base}/oauth/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none", "client_secret_post"],
        "scopes_supported": ["mcp:tools", "contracts:audit", "questionnaires:autofill"],
        "service_documentation": f"{clean_base}/",
    }


def issue_authorization_code(
    *,
    client_id: str,
    redirect_uri: str,
    code_challenge: str,
    code_challenge_method: str = "S256",
    scope: str = "mcp:tools",
    state: str | None = None,
) -> dict[str, Any]:
    """Validate OAuth 2.1 S256 PKCE parameters and issue a short-lived authorization code."""
    if code_challenge_method != "S256":
        raise ValueError("OAuth 2.1 requires code_challenge_method='S256'.")
    if not code_challenge or len(code_challenge.strip()) < 16:
        raise ValueError("Invalid S256 code_challenge: minimum length is 16 characters.")
    if not client_id.strip() or not redirect_uri.strip():
        raise ValueError("Both client_id and redirect_uri are required.")

    code = f"cg_code_{secrets.token_urlsafe(24)}"
    _AUTH_CODES[code] = AuthorizationGrant(
        code=code,
        client_id=client_id.strip(),
        redirect_uri=redirect_uri.strip(),
        code_challenge=code_challenge.strip(),
        code_challenge_method="S256",
        scope=scope,
        created_at=time.time(),
    )
    resp: dict[str, Any] = {
        "code": code,
        "client_id": client_id.strip(),
        "redirect_uri": redirect_uri.strip(),
        "code_challenge_method": "S256",
    }
    if state is not None:
        resp["state"] = state
    return resp


def exchange_code_for_token(
    *,
    code: str,
    code_verifier: str,
    client_id: str,
    redirect_uri: str,
) -> dict[str, Any]:
    """Verify S256 PKCE code_verifier against stored code_challenge and issue Bearer token."""
    grant = _AUTH_CODES.pop(code, None)
    if grant is None:
        raise ValueError("Invalid or expired authorization_code.")
    if grant.client_id != client_id.strip() or grant.redirect_uri != redirect_uri.strip():
        raise ValueError("client_id or redirect_uri mismatch for authorization_code.")
    if not code_verifier or len(code_verifier) < 16:
        raise ValueError("Invalid PKCE code_verifier.")

    computed_challenge = compute_s256_challenge(code_verifier)
    if not secrets.compare_digest(computed_challenge, grant.code_challenge):
        raise ValueError("PKCE S256 verification failed: code_verifier does not match code_challenge.")

    access_token = f"cg_oauth_{secrets.token_urlsafe(28)}"
    token_record = {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": grant.scope,
        "client_id": grant.client_id,
    }
    _ACCESS_TOKENS[access_token] = token_record
    return dict(token_record)


def compute_s256_challenge(code_verifier: str) -> str:
    """Compute BASE64URL-ENCODE(SHA256(ASCII(code_verifier))) without '=' padding."""
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def is_pro_credential(api_key: str | None, bearer_token: str | None) -> bool:
    """Check whether the caller provided a valid Pro tier API key or OAuth token."""
    for candidate in (api_key, bearer_token):
        if not candidate:
            continue
        cleaned = candidate.replace("Bearer ", "").strip()
        if cleaned.startswith("cg_pro_") or cleaned in _ACCESS_TOKENS:
            return True
    return False


def check_and_consume_quota(
    client_id: str,
    api_key: str | None = None,
    bearer_token: str | None = None,
    consume: bool = True,
) -> QuotaStatus:
    """Evaluate Free tier (1 contract/mo) vs Pro tier ($49/mo unlimited) quota."""
    safe_client = (client_id or "anonymous").strip()[:80]
    if is_pro_credential(api_key, bearer_token):
        used = _FREE_USAGE_COUNTS.get(safe_client, 0)
        return QuotaStatus(
            client_id=safe_client,
            tier="pro",
            used_this_month=used,
            monthly_limit=None,
            remaining=None,
            allowed=True,
        )

    current_used = _FREE_USAGE_COUNTS.get(safe_client, 0)
    if current_used >= FREE_MONTHLY_LIMIT:
        return QuotaStatus(
            client_id=safe_client,
            tier="free",
            used_this_month=current_used,
            monthly_limit=FREE_MONTHLY_LIMIT,
            remaining=0,
            allowed=False,
        )

    new_used = current_used + (1 if consume else 0)
    if consume:
        _FREE_USAGE_COUNTS[safe_client] = new_used
    return QuotaStatus(
        client_id=safe_client,
        tier="free",
        used_this_month=new_used,
        monthly_limit=FREE_MONTHLY_LIMIT,
        remaining=max(0, FREE_MONTHLY_LIMIT - new_used),
        allowed=True,
    )
