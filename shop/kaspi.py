"""Kaspi payments through DauysKit QuickPayments (partner-kaspi).

Docs: attached_assets/Pasted--QuickPayments-Kaspi-Partner--1749053914808.txt
"""
import hmac
import logging
import os

import requests

log = logging.getLogger(__name__)

BASE_URL = "https://ks.dauys.com/api/quick-payment/partner-kaspi"
PAID_STATUSES = {"PAID", "SUCCESS", "COMPLETED", "DONE"}


def _integration_id():
    return os.environ.get("KASPI_INTEGRATION_ID", "")


def create_invoice(amount, product_name, account):
    """Returns the invoice dict (with `_id` and `paymentUrl`) or None."""
    integration_id = _integration_id()
    if not integration_id:
        log.error("KASPI_INTEGRATION_ID is not set")
        return None
    try:
        response = requests.post(
            f"{BASE_URL}/{integration_id}/invoice",
            json={"sum": amount, "productName": product_name, "account": account},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        log.error("Kaspi invoice error: %s", e)
        return None


def invoice_is_paid(invoice_id):
    try:
        response = requests.get(f"{BASE_URL}/{_integration_id()}/invoice/{invoice_id}", timeout=10)
        response.raise_for_status()
        status = str(response.json().get("status", "")).strip().upper()
    except (requests.RequestException, ValueError, AttributeError) as e:
        log.warning("Kaspi status check error: %s", e)
        return False
    return status in PAID_STATUSES


def webhook_is_authentic(headers):
    token = os.environ.get("KASPI_WEBHOOK_TOKEN", "")
    if not token:
        log.error("KASPI_WEBHOOK_TOKEN is not set, rejecting webhook")
        return False
    return hmac.compare_digest(headers.get("Authorization", ""), f"Bearer {token}")
