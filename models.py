from app import db
from datetime import datetime
import json

class HealthReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_data = db.Column(db.Text, nullable=False)  # JSON string of user answers
    free_report = db.Column(db.Text)  # Short free report
    paid_report = db.Column(db.Text)  # Full detailed report
    is_paid = db.Column(db.Boolean, default=False)
    payment_session_id = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_user_data(self):
        """Convert JSON string back to dictionary"""
        return json.loads(self.user_data) if self.user_data else {}
    
    def set_user_data(self, data):
        """Convert dictionary to JSON string"""
        self.user_data = json.dumps(data, ensure_ascii=False)
