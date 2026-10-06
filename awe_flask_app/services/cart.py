# cart.py
from flask import session

def get_cart():
    return session.get("cart", [])

def add_to_cart(product_id):
    cart = session.get("cart", [])
    cart.append(product_id)
    session["cart"] = cart

def clear_cart():
    session["cart"] = []

def remove_from_cart(product_id):
    cart = session.get("cart", [])
    if product_id in cart:
        cart.remove(product_id)
    session["cart"] = cart

def update_cart_quantity(product_id, quantity):
    cart = session.get("cart", [])
    # Remove all instances of the product
    cart = [pid for pid in cart if pid != product_id]
    # Add the product the specified number of times
    cart.extend([product_id] * quantity)
    session["cart"] = cart

def get_cart_quantity(product_id):
    cart = session.get("cart", [])
    return cart.count(product_id)
