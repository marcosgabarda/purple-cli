"""Module for configure the CLI application."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


def lazy_settings(cls: type) -> type:
    """Define a decorator for use a settings instance as a lazy object.

    That it is only initialized when it is called the first time.
    """

    class LazySettings:
        """Wrap a Settings class, to allow on need evaluation."""

        _wrapped_settings_class: type[BaseSettings] = cls
        _wrapped_settings: BaseSettings | None = None

        def __getattr__(self, name: str) -> Any:
            if not self._wrapped_settings:
                self._wrapped_settings = self._wrapped_settings_class()
            return getattr(self._wrapped_settings, name)

        def __setattr__(self, name: str, value: Any) -> None:
            if name in ("_wrapped_settings_class", "_wrapped_settings"):
                self.__dict__[name] = value
            else:
                if not self._wrapped_settings:
                    self._wrapped_settings = self._wrapped_settings_class()
                setattr(self._wrapped_settings, name, value)

    return LazySettings


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


@lazy_settings
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


# Lazy instance of settings to enable on need evaluation of the settings properties
settings = Settings()
