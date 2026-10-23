"""Minimal client for ERCOT's Public API (api.ercot.com).

Every request needs two credentials: the subscription key, which identifies the
account, and an ID token from ERCOT's Azure B2C login, which lasts one hour and
can't be refreshed. This client logs in once per process, which is enough for a
batch fetch. Re-authenticating on expiry comes with the long-running producer
in week 6.
"""

import logging
import os
import time

import requests
from dotenv import load_dotenv

log = logging.getLogger(__name__)

TOKEN_URL = (
    "https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/"
    "B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token"
)
CLIENT_ID = "fec253ea-0d06-4272-a5e6-b478baeecd70"  # ERCOT's public app ID, not a secret
BASE_URL = "https://api.ercot.com/api/public-reports"

# ERCOT allows 30 requests per minute. Spacing requests out avoids most 429s;
# the retry loop in _get handles the rest.
MIN_SECONDS_BETWEEN_REQUESTS = 2.1
MAX_ATTEMPTS = 5


class ErcotClient:
    def __init__(self, email, password, subscription_key):
        self._email = email
        self._password = password
        self._subscription_key = subscription_key
        self._session = requests.Session()
        self._token = None
        self._last_request_at = 0.0

    @classmethod
    def from_env(cls):
        """Build a client from ERCOT_EMAIL, ERCOT_PW, and ERCOT_PUBLIC_API in .env."""
        load_dotenv()
        return cls(
            os.environ["ERCOT_EMAIL"],
            os.environ["ERCOT_PW"],
            os.environ["ERCOT_PUBLIC_API"],
        )

    def _login(self):
        # Credentials go in the form body, never the URL, so they can't show up
        # in an exception message or a proxy log.
        resp = self._session.post(
            TOKEN_URL,
            data={
                "username": self._email,
                "password": self._password,
                "grant_type": "password",
                "scope": f"openid {CLIENT_ID} offline_access",
                "client_id": CLIENT_ID,
                "response_type": "id_token",
            },
            timeout=30,
        )
        resp.raise_for_status()
        log.info("Logged in to ERCOT; token valid for %ss", resp.json().get("expires_in"))
        return resp.json()["id_token"]

    def _get(self, path, params):
        if self._token is None:
            self._token = self._login()
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Ocp-Apim-Subscription-Key": self._subscription_key,
        }
        for attempt in range(1, MAX_ATTEMPTS + 1):
            wait = self._last_request_at + MIN_SECONDS_BETWEEN_REQUESTS - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last_request_at = time.monotonic()

            resp = self._session.get(f"{BASE_URL}/{path}", params=params, headers=headers, timeout=60)
            if resp.status_code == 429:
                # Exponential backoff unless the server says how long to wait.
                delay = float(resp.headers.get("Retry-After", 2**attempt))
                log.warning("Throttled (429) on %s; retrying in %.0fs", path, delay)
                time.sleep(delay)
                continue
            resp.raise_for_status()
            return resp.json()
        raise RuntimeError(f"Still throttled after {MAX_ATTEMPTS} attempts: {path}")

    def get_all_pages(self, path, params, page_size=50_000):
        """Return every page of a report query as the raw response bodies."""
        pages = []
        page = 1
        while True:
            body = self._get(path, {**params, "page": page, "size": page_size})
            pages.append(body)
            if page >= body["_meta"]["totalPages"]:
                return pages
            page += 1
