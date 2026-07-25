"""RavenIdentity external service integration client (fixture large-delta component 502)."""
import requests
from langchain_core.tools import tool


class RavenIdentityClient:
    """Client for the RavenIdentity third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.ravenidentity.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_ravenidentity(path: str, payload: dict) -> dict:
    """Invoke the RavenIdentity service at the given path with the given payload.

    Args:
        path: API path on the RavenIdentity service.
        payload: JSON payload.
    """
    return RavenIdentityClient(api_key="REDACTED").request(path, payload)
