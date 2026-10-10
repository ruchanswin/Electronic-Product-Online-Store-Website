# AWE Electronics Online Store

A simple yet functional online electronics store built with Python Flask and Supabase. It supports customers and administrators with features like browsing, cart management, order tracking, refunds, and basic analytics.

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
- Supabase (for storing products, users, orders, and refunds)
- HTML + Jinja templates (for UI)
- Modular file structure with models/ and services/

## Setup Instructions

1. Install the dependencies from the project root:
   ```
   pip install -r requirements.txt
   ```

2. Create `awe_flask_app/.env` and set `SUPABASE_URL` and `SUPABASE_KEY` to your Supabase project values. Keep the `.env` file out of Git.

3. Run the app from the `awe_flask_app` directory:
   ```
   python app.py
   ```

Open `http://127.0.0.1:5001` for the store.

The app reads and writes the `products`, `users`, `orders`, and `refunds` tables in Supabase. The uploaded `orders` table stores products and delivery updates in numbered columns (for example, `products/0` and `delivery_updates/0/status`); the app maps these columns to the order structure used by the store. With the current table shape, an order can contain up to three product entries and up to three delivery updates.

The app uses its Supabase key for server-side database requests. Supabase Row Level Security (RLS) and table permissions still apply; configure policies appropriate for this Flask app before enabling database writes. Do not add broad anonymous access policies for the `users` table.

## Deploying to Vercel

The repository root contains `index.py`, which exposes the Flask app in `awe_flask_app/app.py` to Vercel's Python runtime. Keep the Vercel project's **Root Directory** set to the repository root, and deploy the latest commit to the Production environment. The root `requirements.txt` lists the Python dependencies.

In Vercel, add `FLASK_SECRET_KEY`, `SUPABASE_URL`, and `SUPABASE_KEY` under **Project Settings → Environment Variables** for the environments you deploy (Production and Preview as needed). Use a long, random value for `FLASK_SECRET_KEY`; never commit deployment secrets or rely on `.env` files being uploaded.

**Important:** Store data is persisted in Supabase. In Vercel, configure `SUPABASE_URL` and `SUPABASE_KEY` as environment variables and verify your Supabase RLS policies permit the intended operations without exposing user data.

## Database integration

The Flask app reads and writes the `products`, `users`, `orders`, and `refunds` tables in Supabase through the service layer and shared database helpers in `awe_flask_app/utils/`. The app maps the uploaded `orders` table's numbered product and delivery-update columns to the order structure used by the store. With the current table shape, an order supports up to three product entries and three delivery updates.

Supabase Row Level Security (RLS) and table permissions apply to all requests. Configure policies for the server-side Flask app before enabling database writes; do not add broad anonymous access policies for the `users` table.

