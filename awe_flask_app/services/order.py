import time
from collections import Counter
from typing import cast

from flask import session
from postgrest.exceptions import APIError
from utils.supabase_db import find_by_id, get_supabase_client, next_id
from utils.supabase_store import (
    ORDER_PRODUCT_SLOTS,
    ORDER_UPDATE_SLOTS,
    flatten_order,
    normalize_order,
)


# Delivery status constants
DELIVERY_STATUS = {
    "PENDING": "Pending",
    "PROCESSING": "Processing",
    "SHIPPED": "Shipped",
    "OUT_FOR_DELIVERY": "Out for Delivery",
    "DELIVERED": "Delivered",
    "CANCELLED": "Cancelled"
}


def _restore_stock(client, stock_changes):
    for product, _quantity in stock_changes:
        response = (
            client.table("products")
            .update({"stock": int(product["stock"])})
            .eq("id", product["id"])
            .select("id")
            .execute()
        )
        if not response.data:
            raise RuntimeError(
                f"Supabase did not restore stock for product {product['id']}."
            )


def create_order(user):
    cart = session.get("cart", [])
    if not cart:
        return {"success": False, "message": "Your cart is empty."}

    if len(cart) > ORDER_PRODUCT_SLOTS:
        return {
            "success": False,
            "message": (
                f"The current Supabase orders dataset supports at most "
                f"{ORDER_PRODUCT_SLOTS} products per order."
            ),
        }

    client = get_supabase_client()
    products_response = client.table("products").select("*").execute()
    products = products_response.data
    counts = Counter(str(product_id) for product_id in cart)
    stock_changes = []
    for product_id, quantity in counts.items():
        product = next(
            (
                item
                for item in products
                if isinstance(item, dict)
                and str(item.get("id")) == product_id
            ),
            None,
        )
        if product is None:
            return {"success": False, "message": f"Product ID {product_id} not found."}
        if int(cast(int | float | str, product["stock"])) < quantity:
            return {
                "success": False,
                "message": f"'{product['name']}' has only {product['stock']} in stock.",
            }
        stock_changes.append((product, quantity))

    # Create new order
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    new_order = {
        "id": next_id("orders"),
        "user_id": user["id"],
        "products": [str(product_id) for product_id in cart],
        "timestamp": timestamp,
        "delivery_status": DELIVERY_STATUS["PENDING"],
        "delivery_updates": [
            {
                "status": DELIVERY_STATUS["PENDING"],
                "timestamp": timestamp,
                "message": "Order placed"
            }
        ]
    }

    updated_stock = []
    try:
        for product, quantity in stock_changes:
            response = (
                client.table("products")
                .update({"stock": int(product["stock"]) - quantity})
                .eq("id", product["id"])
                .select("id")
                .execute()
            )
            if not response.data:
                _restore_stock(client, updated_stock)
                return {
                    "success": False,
                    "message": "Supabase did not update product stock; the order was not placed.",
                }
            updated_stock.append((product, quantity))

        inserted = (
            client.table("orders")
            .insert(flatten_order(new_order))
            .select("id")
            .execute()
        )
    except APIError:
        _restore_stock(client, updated_stock)
        raise

    if not inserted.data:
        _restore_stock(client, updated_stock)
        return {
            "success": False,
            "message": "Supabase did not save the order; product stock was restored.",
        }

    session.pop("cart", None) 
    return {"success": True, "id": new_order["id"]}


def get_user_orders(user):
    response = (
        get_supabase_client()
        .table("orders")
        .select("*")
        .eq("user_id", user["id"])
        .execute()
    )
    return [normalize_order(cast(dict, order)) for order in response.data]


def get_order_by_id(order_id):
    order = find_by_id("orders", order_id)
    return normalize_order(order) if order else None

def update_delivery_status(order_id, new_status, message=None):
    if new_status not in DELIVERY_STATUS.values():
        return {"success": False, "message": "Invalid delivery status"}
    order = get_order_by_id(order_id)
    if not order:
        return {"success": False, "message": "Order not found"}

    order["delivery_updates"].append({
        "status": new_status,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "message": message or f"Status updated to {new_status}"
    })
    order["delivery_status"] = new_status
    if len(order["delivery_updates"]) > ORDER_UPDATE_SLOTS:
        return {
            "success": False,
            "message": (
                f"The current Supabase orders dataset supports at most "
                f"{ORDER_UPDATE_SLOTS} delivery updates per order."
            ),
        }

    response = (
        get_supabase_client()
        .table("orders")
        .update(flatten_order(order, include_products=False))
        .eq("id", order_id)
        .select("id")
        .execute()
    )
    if not response.data:
        return {"success": False, "message": "Supabase did not update the order."}
    return {"success": True, "message": "Delivery status updated"}

def get_delivery_status(order_id):
    order = get_order_by_id(order_id)
    if not order:
        return {"success": False, "message": "Order not found"}
    return {
        "success": True,
        "current_status": order.get("delivery_status", DELIVERY_STATUS["PENDING"]),
        "updates": order["delivery_updates"],
    }


def cancel_order(order_id):
    order = get_order_by_id(order_id)
    if not order:
        return {"success": False, "message": "Order not found."}

    client = get_supabase_client()
    products_response = client.table("products").select("*").execute()
    products = products_response.data
    quantities = Counter(str(product_id) for product_id in order["products"])
    for product_id, quantity in quantities.items():
        product = next(
            (
                item
                for item in products
                if isinstance(item, dict)
                and str(item.get("id")) == product_id
            ),
            None,
        )
        if product:
            response = (
                client.table("products")
                .update({"stock": int(cast(int | float | str, product["stock"])) + quantity})
                .eq("id", product["id"])
                .select("id")
                .execute()
            )
            if not response.data:
                return {
                    "success": False,
                    "message": "Supabase did not restore product stock; the order remains.",
                }

    deleted = (
        client.table("orders")
        .delete()
        .eq("id", order_id)
        .select("id")
        .execute()
    )
    if not deleted.data:
        return {
            "success": False,
            "message": "Supabase did not delete the order after restoring stock.",
        }
    return {"success": True}
