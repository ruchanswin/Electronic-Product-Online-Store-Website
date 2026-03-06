# order.py
class Order:
    def __init__(self, order_id, user_id, product_ids, timestamp):
        self.id = order_id
        self.user_id = user_id
        self.products = product_ids
        self.timestamp = timestamp
