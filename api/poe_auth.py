# api/poe_auth.py
"""Simple OAuth helper for logging into Path of Exile.

This module handles obtaining and refreshing OAuth tokens using
Path of Exile's official API. Tokens are stored on disk with
restricted permissions so only the user can read them.
"""

from __future__ import annotations

import json
import os
import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from urllib.parse import urlencode, urlparse, parse_qs
from urllib import request

AUTH_URL = "https://www.pathofexile.com/oauth/authorize"
TOKEN_URL = "https://www.pathofexile.com/oauth/token"
DEFAULT_SCOPE = "account:profile"
TOKEN_FILE = os.path.expanduser("~/.exiledoverlay_tokens.json")
CALLBACK_PORT = 8765
LOGIN_TIMEOUT = 120  # seconds to wait for browser callback


class _CallbackHandler(BaseHTTPRequestHandler):
    """Handler used for the temporary OAuth callback server."""

    server: "_AuthServer"  # type: ignore[assignment]

    def do_GET(self) -> None:  # noqa: D401
        params = parse_qs(urlparse(self.path).query)
        state = params.get("state", [""])[0]
        if state != self.server.state:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid state")
            return
        self.server.code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Login complete. You may close this window.")


class _AuthServer(HTTPServer):
    def __init__(self, addr: tuple[str, int], state: str):
        super().__init__(addr, _CallbackHandler)
        self.code: str | None = None
        self.state = state


def _get_token_path() -> str:
    return TOKEN_FILE


def _save_token(token: dict) -> None:
    path = _get_token_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(token, f)
    os.chmod(path, 0o600)


def load_token() -> dict | None:
    """Load a previously saved OAuth token, if available."""
    try:
        with open(_get_token_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def _get_client_credentials() -> tuple[str, str | None]:
    """Return the configured client id and secret."""
    client_id = os.environ.get("POE_CLIENT_ID")
    client_secret = os.environ.get("POE_CLIENT_SECRET")
    if not client_id:
        raise RuntimeError("POE_CLIENT_ID must be set")
    return client_id, client_secret


def login(scope: str = DEFAULT_SCOPE) -> dict:
    """Perform OAuth login flow and return the obtained token."""
    client_id, client_secret = _get_client_credentials()

    redirect_uri = f"http://localhost:{CALLBACK_PORT}/callback"
    state = secrets.token_urlsafe(16)

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
    }
    url = f"{AUTH_URL}?{urlencode(params)}"
    webbrowser.open(url)

    try:
        httpd = _AuthServer(("localhost", CALLBACK_PORT), state)
    except OSError as exc:  # pragma: no cover - depends on system state
        raise RuntimeError(
            f"Port {CALLBACK_PORT} is unavailable"
        ) from exc

    with httpd:
        httpd.timeout = 1
        start = time.monotonic()
        while httpd.code is None:
            if time.monotonic() - start > LOGIN_TIMEOUT:
                raise TimeoutError("Login timed out waiting for callback")
            httpd.handle_request()
        code = httpd.code

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
    }
    if client_secret:
        data["client_secret"] = client_secret
    req = request.Request(
        TOKEN_URL,
        data=urlencode(data).encode(),
        headers={"User-Agent": "ExiledOverlay"},
    )
    with request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Token request failed: {resp.status}")
        token = json.load(resp)

    if "access_token" not in token or "refresh_token" not in token:
        raise RuntimeError("Token response missing required fields")

    token["expires_at"] = time.time() + token.get("expires_in", 0)
    _save_token(token)
    return token


def refresh_token(token: dict) -> dict:
    """Refresh an expired OAuth token."""
    client_id, client_secret = _get_client_credentials()

    data = {
        "grant_type": "refresh_token",
        "refresh_token": token.get("refresh_token"),
        "client_id": client_id,
    }
    if client_secret:
        data["client_secret"] = client_secret
    req = request.Request(
        TOKEN_URL,
        data=urlencode(data).encode(),
        headers={"User-Agent": "ExiledOverlay"},
    )
    with request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Token refresh failed: {resp.status}")
        new_token = json.load(resp)

    if "access_token" not in new_token or "refresh_token" not in new_token:
        raise RuntimeError("Token refresh response missing required fields")

    new_token["expires_at"] = time.time() + new_token.get("expires_in", 0)
    _save_token(new_token)
    return new_token


def request_token_via_refresh(refresh_token: str) -> dict:
    """Request a new OAuth token using an explicit refresh token."""
    client_id, client_secret = _get_client_credentials()

    data = {
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    if client_secret:
        data["client_secret"] = client_secret
    req = request.Request(
        TOKEN_URL,
        data=urlencode(data).encode(),
        headers={
            "User-Agent": "ExiledOverlay",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Token request failed: {resp.status}")
        token = json.load(resp)

    if "access_token" not in token or "refresh_token" not in token:
        raise RuntimeError("Token response missing required fields")

    token["expires_at"] = time.time() + token.get("expires_in", 0)
    _save_token(token)
    return token


def ensure_valid_token(scope: str = DEFAULT_SCOPE) -> dict:
    """Return a valid OAuth token, refreshing or logging in if necessary."""
    token = load_token()
    if token is None:
        return login(scope)

    expires_at = token.get("expires_at")
    if isinstance(expires_at, (int, float)) and expires_at <= time.time():
        return refresh_token(token)

    return token
