import time
from flask import session
from utils.file_io import load_data, save_data
import os

PRODUCTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "products.json")
ORDERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "orders.json")

# Delivery status constants
DELIVERY_STATUS = {
    "PENDING": "Pending",
    "PROCESSING": "Processing",
    "SHIPPED": "Shipped",
    "OUT_FOR_DELIVERY": "Out for Delivery",
    "DELIVERED": "Delivered",
    "CANCELLED": "Cancelled"
}

def create_order(user):
    cart = session.get("cart", [])
    if not cart:
        return {"success": False, "message": "Your cart is empty."}

    products = load_data(PRODUCTS_FILE)
    orders = load_data(ORDERS_FILE)

    # Count how many of each product was ordered
    counts = {}
    for pid in cart:
        counts[pid] = counts.get(pid, 0) + 1

    # Check and update stock
    for pid, qty in counts.items():
        matched = False
        for product in products:
            if str(product["id"]) == str(pid):
                matched = True
                if product["stock"] >= qty:
                    product["stock"] -= qty
                else:
                    return {
                        "success": False,
                        "message": f"'{product['name']}' has only {product['stock']} in stock."
                    }
        if not matched:
            return {"success": False, "message": f"Product ID {pid} not found."}

    # Save updated products
    save_data(PRODUCTS_FILE, products)

    # Create new order
    new_order = {
        "id": len(orders) + 1,
        "user_id": user["id"],
        "products": cart,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "delivery_status": DELIVERY_STATUS["PENDING"],
        "delivery_updates": [
            {
                "status": DELIVERY_STATUS["PENDING"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "message": "Order placed"
            }
        ]
    }

    orders.append(new_order)
    save_data(ORDERS_FILE, orders)
    session.pop("cart", None) 
    return {"success": True, "id": new_order["id"]}


def get_user_orders(user):
    orders = load_data(ORDERS_FILE)
    return [order for order in orders if order["user_id"] == user["id"]]

def update_delivery_status(order_id, new_status, message=None):
    orders = load_data(ORDERS_FILE)
    for order in orders:
        if order["id"] == order_id:
            if new_status not in DELIVERY_STATUS.values():
                return {"success": False, "message": "Invalid delivery status"}
            
            # Initialize delivery tracking fields if they don't exist
            if "delivery_status" not in order:
                order["delivery_status"] = DELIVERY_STATUS["PENDING"]
            if "delivery_updates" not in order:
                order["delivery_updates"] = [{
                    "status": DELIVERY_STATUS["PENDING"],
                    "timestamp": order["timestamp"],
                    "message": "Order placed"
                }]
            
            order["delivery_status"] = new_status
            order["delivery_updates"].append({
                "status": new_status,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "message": message or f"Status updated to {new_status}"
            })
            save_data(ORDERS_FILE, orders)
            return {"success": True, "message": "Delivery status updated"}
    
    return {"success": False, "message": "Order not found"}

def get_delivery_status(order_id):
    orders = load_data(ORDERS_FILE)
    for order in orders:
        if order["id"] == order_id:
            # Initialize delivery tracking fields if they don't exist
            if "delivery_status" not in order:
                order["delivery_status"] = DELIVERY_STATUS["PENDING"]
            if "delivery_updates" not in order:
                order["delivery_updates"] = [{
                    "status": DELIVERY_STATUS["PENDING"],
                    "timestamp": order["timestamp"],
                    "message": "Order placed"
                }]
                save_data(ORDERS_FILE, orders)
            
            return {
                "success": True,
                "current_status": order["delivery_status"],
                "updates": order["delivery_updates"]
            }
    return {"success": False, "message": "Order not found"}

