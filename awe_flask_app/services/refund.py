# refund.py
from datetime import datetime
from typing import Any, cast
from utils.supabase_db import get_supabase_client, next_id

def request_refund(user, form):
    order_id = form.get("order_id")
    try:
        order_id = int(order_id)
    except (TypeError, ValueError):
        return {"success": False, "message": "Invalid order ID."}

    client = get_supabase_client()
    response = (
        client.table("orders")
        .select("id,user_id")
        .eq("id", order_id)
        .limit(1)
        .execute()
    )
    order = cast(dict[str, Any] | None, response.data[0] if response.data else None)
    if not order:
        return {"success": False, "message": "Order not found."}
    if str(order["user_id"]) != str(user["id"]):
        return {"success": False, "message": "This order does not belong to you."}

    new_refund = {
        "id": next_id("refunds"),
        "user_id": user["id"],
        "order_id": order_id,
        "reason": form.get("reason"),
        "timestamp": str(datetime.now()),
        "status": "Pending"
    }
    client.table("refunds").insert(new_refund).execute()
    return {"success": True}

def get_refunds_for_user(user):
    response = (
        get_supabase_client()
        .table("refunds")
        .select("*")
        .eq("user_id", user["id"])
        .execute()
    )
    return response.data
