import os
from typing import cast

from dotenv import load_dotenv
from flask import abort
from supabase import Client, create_client

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def get_supabase_client() -> Client:
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        abort(
            503,
            description="Supabase is not configured. Set SUPABASE_URL and SUPABASE_KEY.",
        )
    return create_client(supabase_url, supabase_key)


def fetch_rows(table: str) -> list[dict]:
    response = get_supabase_client().table(table).select("*").execute()
    return cast(list[dict], response.data)


def next_id(table: str) -> int:
    response = (
        get_supabase_client()
        .table(table)
        .select("id")
        .order("id", desc=True)
        .limit(1)
        .execute()
    )
    rows = cast(list[dict], response.data or [])
    if not rows:
        return 1

    first_id = rows[0].get("id")
    return int(first_id) + 1 if first_id is not None else 1


def find_by_id(table: str, record_id: int | str) -> dict | None:
    response = (
        get_supabase_client()
        .table(table)
        .select("*")
        .eq("id", record_id)
        .limit(1)
        .execute()
    )
    rows = cast(list[dict], response.data or [])
    return rows[0] if rows else None
