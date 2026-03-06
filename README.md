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
Running the App

1. Download and extract the project
Make sure all files are intact (especially the data/ and templates/ folders).

2. Run the app
Simply use the following command in the project root:
```
python app.py
``` 
Then open your browser and go to:
``` 
http://127.0.0.1:5001
``` 

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






