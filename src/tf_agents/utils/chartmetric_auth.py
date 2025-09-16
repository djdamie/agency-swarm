"""Chartmetric authentication helper for Agency Swarm tools."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

_ACCESS_TOKEN: Optional[str] = None
_TOKEN_EXPIRY: Optional[datetime] = None


def get_access_token() -> str:
    """Retrieve (and cache) a Chartmetric access token."""
    global _ACCESS_TOKEN, _TOKEN_EXPIRY

    if _ACCESS_TOKEN and _TOKEN_EXPIRY and datetime.now() < _TOKEN_EXPIRY:
        return _ACCESS_TOKEN

    refresh_token = os.environ.get("CHARTMETRIC_REFRESH_TOKEN")
    if not refresh_token:
        raise RuntimeError("CHARTMETRIC_REFRESH_TOKEN not set")

    response = requests.post("https://api.chartmetric.com/api/token", data={"refreshtoken": refresh_token}, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            "Failed to obtain Chartmetric access token: "
            f"status={response.status_code}, body={response.text[:200]}"
        )

    token_data = response.json()
    _ACCESS_TOKEN = token_data["token"]
    _TOKEN_EXPIRY = datetime.now() + timedelta(minutes=55)
    return _ACCESS_TOKEN


__all__ = ["get_access_token"]
