import time
import os
from utils.file_io import load_data
from services.order import get_delivery_status

def generate_invoice(order_id):
    orders = load_data(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "orders.json"))
    products = load_data(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "products.json"))
    users = load_data(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "users.json"))
    
    # Find the order
    order = None
    for o in orders:
        if o["id"] == order_id:
            order = o
            break
    
    if not order:
        return {"success": False, "message": "Order not found"}
    
    # Find the customer
    customer = None
    for u in users:
        if u["id"] == order["user_id"]:
            customer = u
            break
    
    if not customer:
        return {"success": False, "message": "Customer not found"}
    
    # Calculate order details
    order_items = []
    subtotal = 0
    
    # Count product quantities
    product_counts = {}
    for pid in order["products"]:
        product_counts[pid] = product_counts.get(pid, 0) + 1
    
    # Calculate prices
    for pid, quantity in product_counts.items():
        for product in products:
            if str(product["id"]) == str(pid):
                item_total = product["price"] * quantity
                subtotal += item_total
                order_items.append({
                    "name": product["name"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "total": item_total
                })
    
    # Calculate tax (assuming 10% tax rate)
    tax_rate = 0.10
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    # Get delivery status
    delivery_info = get_delivery_status(order_id)
    
    # Generate invoice number (format: INV-YYYYMMDD-XXXX)
    invoice_number = f"INV-{time.strftime('%Y%m%d')}-{order_id:04d}"
    
    invoice_data = {
        "success": True,
        "invoice_number": invoice_number,
        "date": time.strftime("%Y-%m-%d"),
        "order_id": order_id,
        "customer": {
            "name": customer["name"],
            "email": customer["email"]
        },
        "order_items": order_items,
        "subtotal": subtotal,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "total": total,
        "delivery_status": delivery_info.get("current_status", "Unknown"),
        "order_date": order["timestamp"]
    }
    
    return invoice_data 