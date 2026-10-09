# AWE Electronics Online Store

A simple yet functional online electronics store built with Python Flask, using JSON files for data storage. It supports customers and administrators with features like browsing, cart management, order tracking, refunds, and basic analytics.

## Features
Customers:
- Register and log in
- Browse and search products
- Add items to cart
- Place orders and track delivery
- Request refunds for completed orders

Admins:
- Add/edit/delete products
- Manage user accounts
- Fulfill and refund orders
- View sales and inventory stats

Technologies Used
- Python 3
- Flask (web framework)
- JSON (for storing data)
- HTML + Jinja templates (for UI)
- Modular file structure with models/ and services/

## Setup Instructions

1. Install the dependencies from the project root:
   ```
   pip install -r requirements.txt
   ```

2. Create `awe_flask_app/.env` from `awe_flask_app/.env.example` and set `SUPABASE_URL` and `SUPABASE_KEY` to your Supabase project values. The `.env` file is ignored by Git.

3. Run the app from the `awe_flask_app` directory:
   ```
   python app.py
   ```

Open `http://127.0.0.1:5001` for the store or `http://127.0.0.1:5001/todos` to view rows from the Supabase `todos` table.

## Deploying to Vercel

The repository root contains `index.py`, which exposes the Flask app in `awe_flask_app/app.py` to Vercel's Python runtime. Keep the Vercel project's **Root Directory** set to the repository root, and deploy the latest commit to the Production environment. The root `requirements.txt` lists the Python dependencies.

In Vercel, add `FLASK_SECRET_KEY`, `SUPABASE_URL`, and `SUPABASE_KEY` under **Project Settings → Environment Variables** for the environments you deploy (Production and Preview as needed). Use a long, random value for `FLASK_SECRET_KEY`; never commit deployment secrets or rely on `.env` files being uploaded.

**Important:** The store currently saves users, orders, refunds, and products in JSON files. Vercel Functions do not provide persistent writable local storage, so changes to those files will not reliably persist across requests or deployments. Use a persistent database (for example, Supabase) for store data before using registration, order, refund, or admin write features in production. The Todos page already reads from Supabase.

## Project Structure
```
A3_Final_Version/
├── data/
│   ├── users.json
│   ├── products.json
│   ├── orders.json
│   └── refunds.json
├── models/
│   ├── user.py
│   ├── product.py
│   ├── order.py
│   └── refund.py
├── services/
|   |── __init_.py
│   ├── auth.py
│   ├── cart.py
│   ├── catalog.py
│   ├── invoice.py
│   ├── order.py
│   └── refund.py
|   └── statistics.py
├── static/
│   └── style.css
├── templates/
│   └── admin_dashboard.html
│   └── admin_orders.html
│   └── admin_refunds.html
│   └── admin_statistics.html
│   └── cart.html
│   └── catalog.html
│   └── checkout.html
│   └── invoice.html
│   └── layout.html
│   └── login.html
│   └── orders.html
│   └── refunds.html
│   └── register.html
│   └── reset_password.html
├── utils/
|   |── __init_.py
│   └── file.io.py
|── app.py
``` 




