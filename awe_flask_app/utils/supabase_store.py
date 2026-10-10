import json

ORDER_PRODUCT_SLOTS = 3
ORDER_UPDATE_SLOTS = 3


def normalize_order(row: dict) -> dict:
    order = dict(row)

    if "products" in row and isinstance(row["products"], list):
        products = row["products"]
    else:
        products = []
        for index in range(ORDER_PRODUCT_SLOTS):
            product_id = row.get(f"products/{index}")
            if product_id is None or product_id == "":
                continue
            if isinstance(product_id, str) and product_id.startswith("["):
                parsed = json.loads(product_id)
                products.extend(parsed if isinstance(parsed, list) else [product_id])
            else:
                products.append(str(product_id))

    if "delivery_updates" in row and isinstance(row["delivery_updates"], list):
        updates = row["delivery_updates"]
    else:
        updates = []
        for index in range(ORDER_UPDATE_SLOTS):
            update = {
                field: row.get(f"delivery_updates/{index}/{field}")
                for field in ("status", "timestamp", "message")
            }
            if any(value is not None for value in update.values()):
                updates.append(update)

    order["products"] = products
    order["delivery_updates"] = updates
    return order


def flatten_order(order: dict, *, include_products: bool = True) -> dict:
    flattened = {"delivery_status": order["delivery_status"]}
    if include_products:
        flattened.update(
            {
                "user_id": order["user_id"],
                "timestamp": order["timestamp"],
            }
        )
        if "id" in order:
            flattened["id"] = order["id"]

    if include_products:
        products = order["products"]
        if len(products) > ORDER_PRODUCT_SLOTS:
            raise ValueError(
                f"The Supabase orders table supports at most {ORDER_PRODUCT_SLOTS} "
                "products per order."
            )
        for index in range(ORDER_PRODUCT_SLOTS):
            flattened[f"products/{index}"] = (
                str(products[index]) if index < len(products) else None
            )

    updates = order["delivery_updates"]
    if len(updates) > ORDER_UPDATE_SLOTS:
        raise ValueError(
            f"The Supabase orders table supports at most {ORDER_UPDATE_SLOTS} "
            "delivery updates per order."
        )
    for index in range(ORDER_UPDATE_SLOTS):
        update = updates[index] if index < len(updates) else {}
        for field in ("status", "timestamp", "message"):
            flattened[f"delivery_updates/{index}/{field}"] = update.get(field)

    return flattened
