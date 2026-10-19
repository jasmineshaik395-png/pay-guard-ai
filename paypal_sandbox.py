"""Minimal PayPal Sandbox Orders API helpers for the PayGuard AI demo.

Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET in your environment.
This module uses the sandbox API only; it does not use real-money credentials.
"""
import os
import requests

PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com"


class PayPalConfigError(RuntimeError):
    pass


def _credentials():
    client_id = os.getenv("PAYPAL_CLIENT_ID", "").strip()
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise PayPalConfigError(
            "Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET environment variables first."
        )
    return client_id, client_secret


def _access_token():
    client_id, client_secret = _credentials()
    response = requests.post(
        f"{PAYPAL_BASE_URL}/v1/oauth2/token",
        auth=(client_id, client_secret),
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        data={"grant_type": "client_credentials"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def create_sandbox_order(amount: str, currency: str = "USD"):
    """Create a PayPal sandbox order. amount must be a positive decimal string."""
    try:
        amount_value = float(amount)
    except (TypeError, ValueError):
        raise ValueError("amount must be a positive numeric string, e.g. '10.00'.")
    if amount_value <= 0:
        raise ValueError("amount must be greater than zero.")

    token = _access_token()
    response = requests.post(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": currency.upper(),
                    "value": f"{amount_value:.2f}",
                },
                "description": "PayGuard AI sandbox test payment",
            }],
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def capture_sandbox_order(order_id: str):
    """Capture an approved sandbox order using its PayPal order ID."""
    if not order_id or not order_id.strip():
        raise ValueError("order_id is required.")
    token = _access_token()
    response = requests.post(
        f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id.strip()}/capture",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        json={},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()
