# catalog.py
from utils.supabase_db import get_supabase_client, next_id


def load_products():
    response = (
        get_supabase_client()
        .table("products")
        .select("*")
        .order("id")
        .execute()
    )
    return response.data


def create_product(product):
    product["id"] = next_id("products")
    response = (
        get_supabase_client()
        .table("products")
        .insert(product)
        .select("id")
        .execute()
    )
    return bool(response.data)


def update_product(product_id, values):
    response = (
        get_supabase_client()
        .table("products")
        .update(values)
        .eq("id", product_id)
        .select("id")
        .execute()
    )
    return bool(response.data)


def delete_product(product_id):
    response = (
        get_supabase_client()
        .table("products")
        .delete()
        .eq("id", product_id)
        .select("id")
        .execute()
    )
    return bool(response.data)
