import os
import sys
import json
import time

import pytest

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


def test_get_client_credentials_optional_secret(monkeypatch):
    monkeypatch.setenv("POE_CLIENT_ID", "abc")
    monkeypatch.delenv("POE_CLIENT_SECRET", raising=False)
    cid, secret = poe_auth._get_client_credentials()
    assert cid == "abc"
    assert secret is None


def test_get_client_credentials_with_secret(monkeypatch):
    monkeypatch.setenv("POE_CLIENT_ID", "abc")
    monkeypatch.setenv("POE_CLIENT_SECRET", "xyz")
    cid, secret = poe_auth._get_client_credentials()
    assert cid == "abc"
    assert secret == "xyz"


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
