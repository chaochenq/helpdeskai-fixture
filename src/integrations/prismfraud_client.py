"""PrismFraud external service integration client (fixture large-delta component 473)."""
import requests
from langchain_core.tools import tool


class PrismFraudClient:
    """Client for the PrismFraud third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.prismfraud.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_prismfraud(path: str, payload: dict) -> dict:
    """Invoke the PrismFraud service at the given path with the given payload.

    Args:
        path: API path on the PrismFraud service.
        payload: JSON payload.
    """
    return PrismFraudClient(api_key="REDACTED").request(path, payload)
