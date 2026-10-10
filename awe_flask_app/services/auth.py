import hmac

from werkzeug.security import check_password_hash, generate_password_hash

from utils.supabase_db import get_supabase_client, next_id

def register_user(form):
    email = (form.get("email") or "").strip().lower()
    client = get_supabase_client()
    existing = (
        client.table("users")
        .select("id")
        .eq("email", email)
        .limit(1)
        .execute()
    )
    if existing.data:
        return {"success": False, "message": "Email already registered."}

    new_user = {
        "id": next_id("users"),
        "email": email,
        "password": generate_password_hash(form.get("password") or ""),
        "name": form.get("name"),
        "role": "admin" if email == "admin@awe.com" else "user"
    }

    client.table("users").insert(new_user).execute()
    return {"success": True}

from flask import session

def login_user(form):
    email = (form.get("email") or "").strip().lower()
    password = form.get("password") or ""
    response = (
        get_supabase_client()
        .table("users")
        .select("*")
        .eq("email", email)
        .limit(1)
        .execute()
    )
    user = response.data[0] if response.data else None
    if not isinstance(user, dict):
        user = None
    if user:
        stored_password = str(user.get("password") or "")
        if stored_password.startswith(("scrypt:", "pbkdf2:")):
            password_matches = check_password_hash(stored_password, password)
        else:
            password_matches = hmac.compare_digest(
                stored_password.encode("utf-8"),
                password.encode("utf-8"),
            )
        if not password_matches:
            user = None

    if user:
        public_user = {key: value for key, value in user.items() if key != "password"}
        session["user"] = public_user
        return {"success": True, "user": public_user}
    return {"success": False, "message": "Invalid credentials."}


def reset_user_password(email, new_password):
    response = (
        get_supabase_client()
        .table("users")
        .update({"password": generate_password_hash(new_password)})
        .eq("email", (email or "").strip().lower())
        .select("id")
        .execute()
    )
    return bool(response.data)


def load_users():
    response = get_supabase_client().table("users").select("*").execute()
    return [
        {key: value for key, value in user.items() if key != "password"}
        for user in response.data
        if isinstance(user, dict)
    ]


def get_user_by_id(user_id):
    response = (
        get_supabase_client()
        .table("users")
        .select("*")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None

    user = response.data[0]
    if not isinstance(user, dict):
        return None

    return {
        key: value
        for key, value in user.items()
        if key != "password"
    }


def logout_user():
    return True

def get_current_user():
    from flask import session
    return session.get("user")
