# refund.py
class Refund:
    def __init__(self, refund_id, user_id, order_id, reason, status, timestamp):
        self.id = refund_id
        self.user_id = user_id
        self.order_id = order_id
        self.reason = reason
        self.status = status  # Pending / Approved / Rejected
        self.timestamp = timestamp
