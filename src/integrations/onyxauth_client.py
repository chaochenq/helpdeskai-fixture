"""OnyxAuth external service integration client (fixture large-delta component 159)."""
import requests
from langchain_core.tools import tool


class OnyxAuthClient:
    """Client for the OnyxAuth third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.onyxauth.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_onyxauth(path: str, payload: dict) -> dict:
    """Invoke the OnyxAuth service at the given path with the given payload.

    Args:
        path: API path on the OnyxAuth service.
        payload: JSON payload.
    """
    return OnyxAuthClient(api_key="REDACTED").request(path, payload)
