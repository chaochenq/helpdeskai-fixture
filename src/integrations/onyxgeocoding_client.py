"""OnyxGeocoding external service integration client (fixture large-delta component 163)."""
import requests
from langchain_core.tools import tool


class OnyxGeocodingClient:
    """Client for the OnyxGeocoding third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.onyxgeocoding.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_onyxgeocoding(path: str, payload: dict) -> dict:
    """Invoke the OnyxGeocoding service at the given path with the given payload.

    Args:
        path: API path on the OnyxGeocoding service.
        payload: JSON payload.
    """
    return OnyxGeocodingClient(api_key="REDACTED").request(path, payload)
