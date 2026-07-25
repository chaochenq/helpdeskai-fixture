"""EmberSearch external service integration client (fixture large-delta component 176)."""
import requests
from langchain_core.tools import tool


class EmberSearchClient:
    """Client for the EmberSearch third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.embersearch.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_embersearch(path: str, payload: dict) -> dict:
    """Invoke the EmberSearch service at the given path with the given payload.

    Args:
        path: API path on the EmberSearch service.
        payload: JSON payload.
    """
    return EmberSearchClient(api_key="REDACTED").request(path, payload)
