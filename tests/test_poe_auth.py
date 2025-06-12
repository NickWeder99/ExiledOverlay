import os
import sys

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


def test_login_env_missing(monkeypatch):
    monkeypatch.delenv("POE_CLIENT_ID", raising=False)
    monkeypatch.delenv("POE_CLIENT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        poe_auth.login()
