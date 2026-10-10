import time

from services.catalog import load_products
from services.order import get_delivery_status, get_order_by_id
from services.auth import get_user_by_id

def generate_invoice(order_id):
    order = get_order_by_id(order_id)
    if not order:
        return {"success": False, "message": "Order not found"}
    
    customer = get_user_by_id(order["user_id"])
    if not customer:
        return {"success": False, "message": "Customer not found"}
    
    # Calculate order details
    order_items = []
    subtotal = 0
    products = load_products()
    
    # Count product quantities
    product_counts = {}
    for pid in order["products"]:
        product_counts[str(pid)] = product_counts.get(str(pid), 0) + 1
    
    # Calculate prices
    for pid, quantity in product_counts.items():
        for product in products:
            if isinstance(product, dict) and str(product.get("id")) == str(pid):
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