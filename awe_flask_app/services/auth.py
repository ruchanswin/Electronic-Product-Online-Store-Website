import json
import os
from utils.file_io import load_data, save_data

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_FILE = os.path.join(BASE_DIR, "data", "users.json")

def register_user(form):
    users = load_data(USERS_FILE)
    email = form.get("email")

    if any(u["email"] == email for u in users):
        return {"success": False, "message": "Email already registered."}

    #Ensure unique user ID by using the max existing ID
    max_id = max((u.get("id", 0) for u in users), default=0)

    new_user = {
        "id": max_id + 1,
        "email": email,
        "password": form.get("password"),
        "name": form.get("name"),
        "role": "admin" if email == "admin@awe.com" else "user"
    }

    users.append(new_user)
    save_data(USERS_FILE, users)
    return {"success": True}

from flask import session

def login_user(form):
    users = load_data(USERS_FILE)
    email = form.get("email")
    password = form.get("password")
    user = next((u for u in users if u["email"] == email and u["password"] == password), None)
    if user:
        session["user"] = user  # Store user in session
        return {"success": True, "user": user}
    return {"success": False, "message": "Invalid credentials."}


def logout_user():
    return True

def get_current_user():
    from flask import session
    return session.get("user")
