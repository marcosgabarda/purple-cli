"""Module for configure the CLI application."""

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
def app_data_path() -> Path:
    """Retrieve the path to the default application data path."""
    home_path = os.path.expanduser("~")
    xdg_data_home = os.environ.get("XDG_DATA_HOME") or os.path.join(
        home_path, ".local", "share"
    )

    # name to use as folder to save local data
    data_folder = "purple"

    data_home = os.path.join(xdg_data_home, data_folder)
    os.makedirs(data_home, exist_ok=True)

    return Path(data_home)


class Settings(BaseSettings):
    """Configuration of the purple script."""

    client_id: str
    client_secret: str
    scopes: str = "user:read:follows"

    host: str = "localhost"
    port: int = 8080

    model_config = SettingsConfigDict(env_prefix="purple_")

    @property
    def redirect_uri(self) -> str:
        """Build the redirect URI for authentication flow."""
        return f"http://{self.host}:{self.port}"

    @property
    def auth_file(self) -> Path:
        """Get the path to the auth.json file."""
        return app_data_path() / "auth.json"


settings = Settings()
