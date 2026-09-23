import os
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise RuntimeError("Supabase environment variables are not configured")


def supabase_request(method, table, params=None, json=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"

    headers = {
        "apikey": SUPABASE_SECRET_KEY,
        "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    response = requests.request(
        method,
        url,
        headers=headers,
        params=params,
        json=json,
        timeout=15,
    )

    response.raise_for_status()

    if not response.content:
        return None

    return response.json()
