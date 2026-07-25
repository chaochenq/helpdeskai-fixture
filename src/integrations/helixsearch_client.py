"""HelixSearch external service integration client (fixture large-delta component 218)."""
import requests
from langchain_core.tools import tool


class HelixSearchClient:
    """Client for the HelixSearch third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.helixsearch.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_helixsearch(path: str, payload: dict) -> dict:
    """Invoke the HelixSearch service at the given path with the given payload.

    Args:
        path: API path on the HelixSearch service.
        payload: JSON payload.
    """
    return HelixSearchClient(api_key="REDACTED").request(path, payload)
