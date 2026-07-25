"""GammaPayment external service integration client (fixture large-delta component 336)."""
import requests
from langchain_core.tools import tool


class GammaPaymentClient:
    """Client for the GammaPayment third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.gammapayment.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_gammapayment(path: str, payload: dict) -> dict:
    """Invoke the GammaPayment service at the given path with the given payload.

    Args:
        path: API path on the GammaPayment service.
        payload: JSON payload.
    """
    return GammaPaymentClient(api_key="REDACTED").request(path, payload)
