"""Module with helper functions to interact with Twitch API."""

import logging
import urllib

import httpx

from .settings import settings

logger = logging.getLogger(__name__)


def twitch_api_client(access_token: str) -> httpx.Client:
    """Create a simple client to access Twitch API."""
    base_url = "https://api.twitch.tv"
    headers = {
        "Client-ID": settings.client_id,
        "Authorization": f"Bearer {access_token}",
    }
    return httpx.Client(base_url=base_url, headers=headers)


def raise_for_status(response: httpx.Response) -> None:
    """Unify the handle of errors in API requests."""
    if not response.is_success:
        logger.error(
            f"Error calling to {response.request.url}:\n"
            f"{response.content.decode('utf-8')}"
        )
        response.raise_for_status()


def retrieve_token(code: str) -> dict:
    """Retrieve the token information from Twitch using the given code."""
    logger.debug(f"Obtaining token information using code {code}")
    token_url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": settings.client_id,
        "client_secret": settings.client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.redirect_uri,
    }

    response = httpx.post(token_url, params=params)
    raise_for_status(response)

    return response.json()


def retrieve_authorize_url() -> str:
    """Create and return the authorize URL."""
    authorize_url = "https://id.twitch.tv/oauth2/authorize"
    params = {
        "client_id": settings.client_id,
        "redirect_uri": settings.redirect_uri,
        "response_type": "code",
        "scope": settings.scopes,
    }
    return f"{authorize_url}?{urllib.parse.urlencode(params)}"


def retrieve_user(access_token: str) -> dict:
    """Retrieve the user information."""
    with twitch_api_client(access_token) as client:
        response = client.get("/helix/users")
    raise_for_status(response)

    data = response.json()
    return data["data"][0]


def retrieve_followed_channels(access_token: str, user_id: str) -> list[dict]:
    """Retrieve the list of followed channels."""
    page_size = 100
    params: dict[str, str | int] = {
        "user_id": user_id,
        "first": page_size,
    }

    followed: list[dict] = []
    total: int | None = None

    while total is None or len(followed) > total:
        with twitch_api_client(access_token) as client:
            response = client.get("/helix/channels/followed", params=params)
            raise_for_status(response)
            data = response.json()

        if total is None:
            total = data["total"]

        followed.extend(
            [
                {
                    "name": channel["broadcaster_name"],
                    "login": channel["broadcaster_login"],
                    "id": channel["broadcaster_id"],
                    "followed_at": channel["followed_at"],
                }
                for channel in data["data"]
            ]
        )

        cursor = data["pagination"].get("cursor")
        if cursor:
            params["after"] = cursor

    return followed


def retireve_followed_streams(access_token: str, user_id: str) -> list[dict]:
    """Retrieve the list of followed streams."""
    page_size = 100
    params = {
        "user_id": user_id,
        "first": page_size,
    }

    streams: list[dict] = []
    total: int | None = None

    while total is None or len(streams) > total:
        with twitch_api_client(access_token) as client:
            response = client.get("/helix/streams/followed")
            raise_for_status(response)
            data = response.json()

        if total is None:
            total = data["total"]

        streams.extend(data["data"])

        cursor = data["pagination"].get("cursor")
        if cursor:
            params["after"] = cursor

    return streams


def validate_access_token(access_token: str) -> bool:
    """Validate the given access token."""
    headers = {"Authorization": f"OAuth {access_token}"}
    response = httpx.get("https://id.twitch.tv/oauth2/validate", headers=headers)
    return response.status_code == 200


def refresh_access_token(refresh_token: str) -> dict:
    """Refresh the access token."""
    params = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": settings.client_id,
        "client_secret": settings.client_secret,
    }
    response = httpx.post("https://id.twitch.tv/oauth2/token", params=params)
    raise_for_status(response)

    data = response.json()
    return data
