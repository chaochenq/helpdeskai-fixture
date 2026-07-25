"""PrismPayment external service integration client (fixture large-delta component 462)."""
import requests
from langchain_core.tools import tool


class PrismPaymentClient:
    """Client for the PrismPayment third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.prismpayment.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_prismpayment(path: str, payload: dict) -> dict:
    """Invoke the PrismPayment service at the given path with the given payload.

    Args:
        path: API path on the PrismPayment service.
        payload: JSON payload.
    """
    return PrismPaymentClient(api_key="REDACTED").request(path, payload)
