import os
import requests
import json
from datetime import datetime

class KaspiPayment:
    def __init__(self):
        self.integration_id = os.environ.get('KASPI_INTEGRATION_ID', '68405a37b7170fa164bd4158')
        self.base_url = 'https://ks.dauys.com/api/quick-payment/partner-kaspi'
        self.webhook_token = os.environ.get('KASPI_WEBHOOK_TOKEN', '111')
    
    def create_invoice(self, amount, product_name, account_id):
        """Create Kaspi payment invoice"""
        url = f"{self.base_url}/{self.integration_id}/invoice"
        
        payload = {
            "sum": amount,
            "productName": product_name,
            "account": account_id
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating Kaspi invoice: {e}")
            return None
    
    def check_payment_status(self, invoice_id):
        """Check payment status"""
        url = f"{self.base_url}/{self.integration_id}/invoice/{invoice_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error checking payment status: {e}")
            return None
    
    def verify_webhook(self, request_headers, request_data):
        """Verify webhook authenticity"""
        auth_header = request_headers.get('Authorization', '')
        expected_token = f"Bearer {self.webhook_token}"
        
        return auth_header == expected_token