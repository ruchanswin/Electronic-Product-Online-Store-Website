from datetime import datetime, timedelta
from utils.supabase_db import fetch_rows

def get_sales_statistics(period='day'):
    from utils.supabase_store import normalize_order

    orders = [normalize_order(order) for order in fetch_rows("orders")]
    products = fetch_rows("products")
    
    # Create a product lookup dictionary for faster access
    product_lookup = {str(p['id']): p for p in products}
    
    # Get current date and calculate period start
    now = datetime.now()
    if period == 'day':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == 'ytd':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        raise ValueError("Invalid period specified")

    # Filter orders within the period
    period_orders = [
        order for order in orders 
        if datetime.fromisoformat(order['timestamp']) >= start_date
    ]

    # Calculate statistics
    total_sales = 0
    product_sales = {}
    
    for order in period_orders:
        order_total = 0
        for product_id in order['products']:
            product = product_lookup.get(product_id)
            if product:
                order_total += product['price']
                if product_id not in product_sales:
                    product_sales[product_id] = {
                        'quantity': 0,
                        'revenue': 0
                    }
                product_sales[product_id]['quantity'] += 1
                product_sales[product_id]['revenue'] += product['price']
        total_sales += order_total

    total_orders = len(period_orders)

    # Get top 5 selling products
    top_products = []
    for product_id, sales_data in sorted(product_sales.items(), key=lambda x: x[1]['quantity'], reverse=True)[:5]:
        product = product_lookup.get(product_id)
        if product:
            top_products.append({
                'name': product['name'],
                'quantity': sales_data['quantity'],
                'revenue': sales_data['revenue']
            })

    return {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'average_order_value': total_sales / total_orders if total_orders > 0 else 0,
        'top_products': top_products,
        'period': period
    } 