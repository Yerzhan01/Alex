import json
import secrets
from datetime import datetime, timezone

from shop import db


class Order(db.Model):
    __tablename__ = "shop_order"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(32), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(16))
    items = db.Column(db.Text, nullable=False)  # JSON: {"black": 1, "brown": 1}
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    lang = db.Column(db.String(2), nullable=False, default="kk")
    status = db.Column(db.String(16), nullable=False, default="pending")  # pending | paid
    invoice_id = db.Column(db.String(64), index=True)
    payment_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    paid_at = db.Column(db.DateTime)

    def get_items(self):
        return json.loads(self.items)

    def mark_paid(self):
        if self.status != "paid":
            self.status = "paid"
            self.paid_at = datetime.now(timezone.utc)
