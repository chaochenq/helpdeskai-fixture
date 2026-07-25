"""LyraAnalytics external service integration client (fixture large-delta component 409)."""
import requests
from langchain_core.tools import tool


class LyraAnalyticsClient:
    """Client for the LyraAnalytics third-party service. Distinct external integration component."""

    def __init__(self, api_key: str, base_url: str = "https://api.lyraanalytics.example.com"):
        self.api_key = api_key
        self.base_url = base_url

    def request(self, path: str, payload: dict) -> dict:
        # No timeout, no cert pinning, key in header — planted for inventory breadth.
        r = requests.post(f"{self.base_url}/{path}", json=payload, headers={"Authorization": self.api_key})
        return r.json()


@tool
def call_lyraanalytics(path: str, payload: dict) -> dict:
    """Invoke the LyraAnalytics service at the given path with the given payload.

    Args:
        path: API path on the LyraAnalytics service.
        payload: JSON payload.
    """
    return LyraAnalyticsClient(api_key="REDACTED").request(path, payload)
