from flask import Flask, render_template, redirect, request, session, url_for, flash
import os
from services.auth import (
    get_current_user,
    load_users,
    login_user,
    logout_user,
    register_user,
    reset_user_password,
)
from services.catalog import (
    create_product,
    delete_product,
    load_products,
    update_product,
)
from services.cart import get_cart, add_to_cart, remove_from_cart, update_cart_quantity 
from services.order import (
    cancel_order,
    create_order,
    get_order_by_id,
    get_user_orders,
    update_delivery_status,
)
from services.refund import request_refund, get_refunds_for_user
from services.statistics import get_sales_statistics
from services.invoice import generate_invoice
from utils.supabase_db import fetch_rows, get_supabase_client
from utils.supabase_store import normalize_order

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)

@app.route('/')
def home():
    return redirect(url_for('catalog'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        result = register_user(request.form)
        if result['success']:
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        else:
            flash(str(result['message']), 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        result = login_user(request.form)
        if result['success']:
            session['user'] = result['user']
            return redirect(url_for('catalog'))
        else:
            flash(str(result['message']), 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/reset', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get("email")
        new_pass = request.form.get("new_password")
        if reset_user_password(email, new_pass or ""):
            flash("Password reset successful.", "success")
            return redirect(url_for('login'))
        else:
            flash("No user found with that email.", "danger")
    return render_template("reset_password.html")

@app.route('/catalog')
def catalog():
    user = get_current_user()
    products = load_products()
    return render_template('catalog.html', user=user, products=products)

@app.route('/cart')
def cart():
    user = get_current_user()
    if user and user.get("role") == "admin":
        flash("Admins do not use the cart.", "danger")
        return redirect(url_for('catalog'))
    cart_items = get_cart()
    products = load_products()
    return render_template('cart.html', user=user, cart=cart_items, products=products)

@app.route('/cart/add/<product_id>')
def add_item(product_id):
    # Check if the user is logged in
    if 'user' not in session:
        flash("You must be logged in to add items to your cart.", "warning")
        return redirect(url_for('login'))

    # Prevent admins from adding items
    if session['user']['role'] == 'admin':
        flash("Administrators cannot add items to the cart.", "danger")
        return redirect(url_for('catalog'))

    # Normal customer flow
    add_to_cart(product_id)
    flash("Item added to cart.", "success")
    return redirect(url_for('catalog'))

@app.route('/cart/remove/<product_id>')
def remove_item(product_id):
    remove_from_cart(product_id)
    flash("Item removed from cart.", "warning")
    return redirect(url_for('cart'))

@app.route('/cart/update/<product_id>', methods=['POST'])
def update_quantity(product_id):
    quantity = int(request.form.get('quantity', 1))
    if quantity > 0:
        update_cart_quantity(product_id, quantity)
        flash("Cart updated successfully.", "success")
    else:
        remove_from_cart(product_id)
        flash("Item removed from cart.", "warning")
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user = get_current_user()
    if user and user.get("role") == "admin":
        flash("Admins cannot place orders.", "danger")
        return redirect(url_for('catalog'))
    if request.method == 'POST':
        result = create_order(user)
        if result['success']:
            flash('Order placed successfully!', 'success')
            return redirect(url_for('orders'))
        else:
            flash(result['message'], 'danger')
    return render_template('checkout.html', user=user)

@app.route('/orders')
def orders():
    user = get_current_user()
    if not user:
        flash("Please login to view your orders", "warning")
        return redirect(url_for('login'))
        
    if user.get("role") == "admin":
        return redirect(url_for('admin_orders'))
    orders = get_user_orders(user)
    products = load_products()
    return render_template('orders.html', user=user, orders=orders, products=products)

@app.route('/refund', methods=['GET', 'POST'])
def refund():
    user = get_current_user()
    if request.method == 'POST':
        result = request_refund(user, request.form)
        if result['success']:
            flash('Refund requested.', 'success')
        else:
            flash(str(result['message']), 'danger')
    refunds = get_refunds_for_user(user)
    return render_template('refunds.html', user=user, refunds=refunds)

@app.route('/admin/orders', methods=['GET', 'POST'])
def admin_orders():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for('catalog'))
    
    if request.method == 'POST':
        action = request.form.get("action")
        order_id_value = request.form.get("order_id")
        if order_id_value is None:
            flash("Invalid order ID.", "danger")
            return redirect(url_for('admin_orders'))
        order_id = int(order_id_value)
        if action == "cancel":
            result = cancel_order(order_id)
            if result["success"]:
                flash(f"Order #{order_id} cancelled and stock restored.", "warning")
            else:
                flash(result["message"], "danger")
        elif action == "update_status":
            new_status = request.form.get("new_status")
            message = request.form.get("status_message")
            result = update_delivery_status(order_id, new_status, message)
            if result["success"]:
                flash(f"Order #{order_id} status updated to {new_status}.", "success")
            else:
                flash(result["message"], "danger")
    
    orders = [normalize_order(order) for order in fetch_rows("orders")]
    users = load_users()
    products = load_products()
    return render_template("admin_orders.html", user=user, orders=orders, users=users, products=products)

@app.route('/admin/refunds', methods=['GET', 'POST'])
def admin_refunds():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for('catalog'))

    refunds = fetch_rows("refunds")

    if request.method == 'POST':
        refund_id = int(request.form.get("refund_id", "0"))
        action = request.form.get("action")  # "approve" or "reject"
        response = (
            get_supabase_client()
            .table("refunds")
            .update({"status": "approved" if action == "approve" else "rejected"})
            .eq("id", refund_id)
            .select("id")
            .execute()
        )
        if response.data:
            flash(f"Refund #{refund_id} {action}d.", "success")
        else:
            flash(f"Refund #{refund_id} was not found or could not be updated.", "danger")
        refunds = fetch_rows("refunds")

    return render_template("admin_refunds.html", user=user, refunds=refunds)

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("catalog"))

    products = load_products()
    
    if request.method == 'POST':
        action = request.form.get("action")

        if action == "update":
            for product in products:
                pid = str(product["id"])
                values = {
                    "name": request.form.get(f"name_{pid}", product["name"]),
                    "description": request.form.get(
                        f"description_{pid}", product["description"]
                    ),
                    "price": float(
                        request.form.get(f"price_{pid}") or str(product["price"])
                    ),
                    "stock": int(
                        request.form.get(f"stock_{pid}") or str(product["stock"])
                    ),
                    "image": request.form.get(f"image_{pid}", product["image"]),
                }
                if not update_product(product["id"], values):
                    flash(f"Product #{pid} was not found or could not be updated.", "danger")
                    return redirect(url_for("admin_dashboard"))
            flash("Products updated successfully.", "success")
            return redirect(url_for('admin_dashboard'))

        elif action == "delete":
            delete_id = int(request.form.get("delete_id") or "0")
            if delete_product(delete_id):
                flash("Product deleted.", "warning")
            else:
                flash(f"Product #{delete_id} was not found or could not be deleted.", "danger")
            return redirect(url_for("admin_dashboard"))

        elif action == "add":
            new_product = {
                "name": request.form.get("new_name") or "",
                "description": request.form.get("new_description") or "",
                "price": float(request.form.get("new_price") or "0"),
                "stock": int(request.form.get("new_stock") or "0"),
                "image": request.form.get("new_image") or ""
            }
            if create_product(new_product):
                flash("New product added.", "success")
            else:
                flash("Supabase did not save the new product.", "danger")
            return redirect(url_for("admin_dashboard"))

    return render_template("admin_dashboard.html", user=user, products=products)

@app.route('/admin/statistics')
def admin_statistics():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        flash("Access denied", "danger")
        return redirect(url_for("catalog"))

    period = request.args.get('period', 'day')
    stats = get_sales_statistics(period)
    return render_template("admin_statistics.html", user=user, stats=stats)

@app.route('/invoice/<int:order_id>')
def view_invoice(order_id):
    user = get_current_user()
    if not user:
        flash("Please login to view invoices", "warning")
        return redirect(url_for('login'))
    
    # Load orders
    order = get_order_by_id(order_id)

    if not order:
        flash("Order not found", "danger")
        return redirect(url_for('orders'))

    try:
        order_user_id = int(order.get("user_id"))
        current_user_id = int(user.get("id"))
    except (TypeError, ValueError):
        flash("Invalid user ID format", "danger")
        return redirect(url_for('orders'))

    # 🔧 Fix: Check ownership correctly
    if user.get("role") != "admin" and order_user_id != current_user_id:
        flash("Access denied", "danger")
        return redirect(url_for('orders'))
    
    # Generate invoice data
    invoice_data = generate_invoice(order_id)
    if not invoice_data["success"]:
        flash(invoice_data["message"], "danger")
        return redirect(url_for('orders'))

    return render_template("invoice.html", invoice=invoice_data)


if __name__ == '__main__':
    app.run(debug=True, port=5001)

 