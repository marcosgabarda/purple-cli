"""Module to handle authentication."""

import asyncio
import json
import logging
import webbrowser

import httpx
from aiohttp import web

from .api import (
    refresh_access_token,
    retrieve_authorize_url,
    retrieve_token,
    validate_access_token,
)
from .settings import settings

logger = logging.getLogger(__name__)


class OAuthServer:
    """HTTP server to handle the redirection from authentication flow."""

    access_token: str | None = None
    access_token_complete: dict | None = None

    def __init__(self):
        """Initialize the server."""
        self.access_token = None
        self.access_token_complete = None

    async def handler(self, request: web.Request):
        """Handle the request."""
        code = request.rel_url.query.get("code", None)
        if not code:
            logger.error("No code found in the request.")
            return web.Response(text="⚠️ Error, code parameter not found.")

        # change the code for a token
        token_data = retrieve_token(code=code)

        if "access_token" in token_data:
            self.access_token = token_data["access_token"]
            self.access_token_complete = token_data
        else:
            logger.error("Access token not found in response.")
            return web.Response(text="⚠️ Error, no se encuentra el parametro code.")

        # event to close the server
        logger.debug("Sending event to close web server...")
        self.event.set()

        return web.Response(
            text="✅ Authentication complete! You can close this window."
        )

    async def run(self):
        """Run the server."""
        logger.debug("Starging the server...")
        self.event = asyncio.Event()

        self.server = web.Server(self.handler)
        self.runner = web.ServerRunner(self.server)

        await self.runner.setup()
        site = web.TCPSite(self.runner, settings.host, settings.port)
        await site.start()

        await self.event.wait()
        logger.debug("Server started")


def _save_token_data(token_data: dict | None) -> None:
    """Save the token data in the auth file."""
    if token_data:
        auth_file = settings.auth_file
        auth_file.write_text(json.dumps(token_data, indent=2))


def _request_new_access_token() -> str:
    """Get a new valid access token."""
    logger.debug("Opening browser for authentication...")
    webbrowser.open(retrieve_authorize_url())

    server = OAuthServer()
    asyncio.run(server.run())

    logger.debug(f"Obtaioned acces token: {server.access_token}")
    assert server.access_token, "Access token not set"

    # save access token data
    _save_token_data(server.access_token_complete)

    return server.access_token


def obtain_access_token() -> str:
    """Check if there is a saved access token and use it if it's valid.

    If not, renews or get a new one.
    """
    auth_file = settings.auth_file
    if not auth_file.is_file():
        return _request_new_access_token()

    token_data = json.loads(auth_file.read_text())
    access_token = token_data["access_token"]

    if validate_access_token(access_token):
        return access_token

    # try to refresh token
    if "refresh_token" in token_data:
        refresh_token = token_data["refresh_token"]
        try:
            token_data = refresh_access_token(refresh_token)
            _save_token_data(token_data)
            return token_data["access_token"]
        except httpx.HTTPError:
            # in case of error, request a new access token
            return _request_new_access_token()

    return _request_new_access_token()
