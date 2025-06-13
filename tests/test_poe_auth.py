import os
import sys
import json
import time

import pytest
import threading
import http.client

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api import poe_auth


def test_get_token_path(monkeypatch, tmp_path):
    path = tmp_path / "token.json"
    monkeypatch.setattr(poe_auth, "TOKEN_FILE", str(path))
    assert poe_auth._get_token_path() == str(path)


def test_save_and_load_token(monkeypatch, tmp_path):
    path = tmp_path / "token.json"
    monkeypatch.setattr(poe_auth, "TOKEN_FILE", str(path))
    token = {"access_token": "abc", "refresh_token": "def"}
    poe_auth._save_token(token)
    mode = path.stat().st_mode & 0o777
    assert mode == 0o600
    loaded = poe_auth.load_token()
    assert loaded == token


def test_get_client_credentials_missing(monkeypatch):
    monkeypatch.delenv("POE_CLIENT_ID", raising=False)
    monkeypatch.delenv("POE_CLIENT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        poe_auth._get_client_credentials()


def test_get_client_credentials_missing_secret(monkeypatch):
    monkeypatch.setenv("POE_CLIENT_ID", "abc")
    monkeypatch.delenv("POE_CLIENT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        poe_auth._get_client_credentials()


def test_get_client_credentials_with_secret(monkeypatch, tmp_path):
    cred = tmp_path / "creds.json"
    monkeypatch.setattr(poe_auth, "CREDENTIALS_FILE", str(cred))
    monkeypatch.setenv("POE_CLIENT_ID", "abc")
    monkeypatch.setenv("POE_CLIENT_SECRET", "xyz")
    cid, secret = poe_auth._get_client_credentials()
    assert cid == "abc"
    assert secret == "xyz"
    saved = json.load(open(cred, "r", encoding="utf-8"))
    assert saved == {"client_id": "abc", "client_secret": "xyz"}
    mode = cred.stat().st_mode & 0o777
    assert mode == 0o600


def test_get_client_credentials_from_file(monkeypatch, tmp_path):
    cred = tmp_path / "creds.json"
    monkeypatch.setattr(poe_auth, "CREDENTIALS_FILE", str(cred))
    with open(cred, "w", encoding="utf-8") as f:
        json.dump({"client_id": "abc", "client_secret": "xyz"}, f)
    os.chmod(cred, 0o600)
    monkeypatch.delenv("POE_CLIENT_ID", raising=False)
    monkeypatch.delenv("POE_CLIENT_SECRET", raising=False)
    cid, secret = poe_auth._get_client_credentials()
    assert (cid, secret) == ("abc", "xyz")


def test_ensure_valid_token_refresh(monkeypatch, tmp_path):
    path = tmp_path / "token.json"
    monkeypatch.setattr(poe_auth, "TOKEN_FILE", str(path))

    expired = {"access_token": "a", "refresh_token": "b", "expires_at": time.time() - 1}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(expired, f)

    refreshed = {"access_token": "new", "refresh_token": "b", "expires_at": time.time() + 3600}

    def fake_refresh(token):
        return refreshed

    monkeypatch.setattr(poe_auth, "refresh_token", fake_refresh)
    monkeypatch.setattr(poe_auth, "login", lambda scope=poe_auth.DEFAULT_SCOPE: refreshed)

    token = poe_auth.ensure_valid_token()
    assert token == refreshed


def test_ensure_valid_token_public_refresh(monkeypatch, tmp_path):
    path = tmp_path / "token.json"
    monkeypatch.setattr(poe_auth, "TOKEN_FILE", str(path))

    expired = {
        "access_token": "a",
        "refresh_token": "b",
        "expires_at": time.time() - 1,
        "client_id": "acc",
        "public": True,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(expired, f)

    refreshed = {
        "access_token": "new",
        "refresh_token": "b",
        "expires_at": time.time() + 3600,
        "client_id": "acc",
        "public": True,
    }

    def fake_refresh(token):
        return refreshed

    monkeypatch.setattr(poe_auth, "refresh_token_public", fake_refresh)
    monkeypatch.setattr(
        poe_auth,
        "login_public",
        lambda account, scope=poe_auth.DEFAULT_SCOPE: refreshed,
    )

    token = poe_auth.ensure_valid_token_public("acc")
    assert token == refreshed


def test_callback_error(monkeypatch):
    server = poe_auth._AuthServer(("localhost", 0), "xyz")
    port = server.server_address[1]

    def serve_once():
        server.handle_request()

    t = threading.Thread(target=serve_once)
    t.start()

    conn = http.client.HTTPConnection("localhost", port)
    conn.request(
        "GET",
        "/callback?state=xyz&error=invalid_client&error_description=bad+id",
    )
    resp = conn.getresponse()
    resp.read()
    conn.close()
    t.join()

    assert resp.status == 200
    assert server.error == "bad id"
    assert server.code is None

