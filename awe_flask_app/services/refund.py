# refund.py
from utils.file_io import load_data, save_data
from datetime import datetime
import os

REFUND_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "refunds.json")
ORDERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "orders.json")

def request_refund(user, form):
    refunds = load_data(REFUND_FILE)
    orders = load_data(ORDERS_FILE)
    
    # Validate order exists
    order_id = form.get("order_id")
    order = next((o for o in orders if o["id"] == int(order_id)), None)
    if not order:
        return {"success": False, "message": "Order not found."}
    
    # Validate order belongs to user
    if order["user_id"] != user["id"]:
        return {"success": False, "message": "This order does not belong to you."}

    new_refund = {
        "id": len(refunds) + 1,
        "user_id": user["id"],
        "order_id": order_id,
        "reason": form.get("reason"),
        "timestamp": str(datetime.now()),
        "status": "Pending"
    }
    refunds.append(new_refund)
    save_data(REFUND_FILE, refunds)
    return {"success": True}

def get_refunds_for_user(user):
    refunds = load_data(REFUND_FILE)
    return [r for r in refunds if r["user_id"] == user["id"]]
