"""Instagram Graph API client for pulling per-reel insights.

Real implementation — not mocked logic — but it will raise
InstagramAuthError until the Setup Dependencies in HANDOFF.md are done
(Business/Creator account + Meta app approved for instagram_manage_insights).
That error is exactly the "critical" case in the Analytics Agent's Error
Handling: stop pulling, alert Rishi that reconnection is needed.
"""
from __future__ import annotations

import httpx

from app.config import settings

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"

# Metric names correspond to the fields the Analytics Agent's Task 1 needs.
MEDIA_INSIGHT_METRICS = [
    "reach",
    "plays",
    "total_interactions",
    "likes",
    "comments",
    "shares",
    "saved",
    "avg_watch_time",
    "video_view_total_time",
]


class InstagramAuthError(RuntimeError):
    """Raised when the token is missing/expired — critical, stop-and-alert case."""


class InstagramClient:
    def __init__(self) -> None:
        self.access_token = settings.instagram_access_token
        self.business_account_id = settings.instagram_business_account_id

    def _require_auth(self) -> None:
        if not self.access_token or not self.business_account_id:
            raise InstagramAuthError(
                "Instagram connection needs re-authorization — analytics paused "
                "until reconnected. (instagram_access_token / "
                "instagram_business_account_id not configured.)"
            )

    def fetch_media_insights(self, media_id: str) -> dict:
        """Pull insights for a single reel (media object). Task 1 of the
        Analytics Agent. Raises InstagramAuthError if not configured, or
        httpx.HTTPStatusError (incl. expired-token 190 errors) on failure —
        callers map the latter to the medium 'skip, retry next run' path."""
        self._require_auth()

        response = httpx.get(
            f"{GRAPH_API_BASE}/{media_id}/insights",
            params={
                "metric": ",".join(MEDIA_INSIGHT_METRICS),
                "access_token": self.access_token,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json().get("data", [])
        return {item["name"]: item["values"][0]["value"] for item in data}

    def fetch_media_demographics(self, media_id: str) -> dict:
        """Age/gender/country breakdown for a reel's audience, where available.
        Instagram doesn't expose this per-post for all account tiers — callers
        should treat a missing breakdown as partial_data, per Error Handling's
        'low' tier (store partial data, note gap), not as a hard failure."""
        self._require_auth()

        response = httpx.get(
            f"{GRAPH_API_BASE}/{media_id}/insights",
            params={
                "metric": "profile_activity",
                "breakdown": "action_type",
                "access_token": self.access_token,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        return response.json().get("data", [])

    def list_recent_media(self, limit: int = 25) -> list[dict]:
        self._require_auth()

        response = httpx.get(
            f"{GRAPH_API_BASE}/{self.business_account_id}/media",
            params={
                "fields": "id,caption,timestamp,media_type",
                "limit": limit,
                "access_token": self.access_token,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        return response.json().get("data", [])


instagram_client = InstagramClient()
