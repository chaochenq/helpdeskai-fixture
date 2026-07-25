"""TitanFraud external service integration client (fixture large-delta component 529)."""
import requests
from langchain_core.tools import tool


class TitanFraudClient:
    """Client for the TitanFraud third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.titanfraud.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_titanfraud(path: str, payload: dict) -> dict:
    """Invoke the TitanFraud service at the given path with the given payload.

    Args:
        path: API path on the TitanFraud service.
        payload: JSON payload.
    """
    return TitanFraudClient(api_key="REDACTED").request(path, payload)
