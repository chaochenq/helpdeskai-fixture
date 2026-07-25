"""TitanBilling external service integration client (fixture large-delta component 525)."""
import requests
from langchain_core.tools import tool


class TitanBillingClient:
    """Client for the TitanBilling third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.titanbilling.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_titanbilling(path: str, payload: dict) -> dict:
    """Invoke the TitanBilling service at the given path with the given payload.

    Args:
        path: API path on the TitanBilling service.
        payload: JSON payload.
    """
    return TitanBillingClient(api_key="REDACTED").request(path, payload)
