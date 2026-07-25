"""OrbitLedger external service integration client (fixture large-delta component 111)."""
import requests
from langchain_core.tools import tool


class OrbitLedgerClient:
    """Client for the OrbitLedger third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.orbitledger.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_orbitledger(path: str, payload: dict) -> dict:
    """Invoke the OrbitLedger service at the given path with the given payload.

    Args:
        path: API path on the OrbitLedger service.
        payload: JSON payload.
    """
    return OrbitLedgerClient(api_key="REDACTED").request(path, payload)
