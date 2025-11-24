"""Module with CLI application."""

import argparse
import json
import logging
import sys

from pydantic import ValidationError

import purple

from .api import (
    retrieve_followed_streams,
    retrieve_live_streams,
    retrieve_user,
)
from .auth import obtain_access_token
from .settings import settings

logger = logging.getLogger(__name__)


def live_followed(languages: list[str] | None = None) -> str:
    """List the channels the user follows."""
    # obtain access token
    access_token = obtain_access_token()

    # get user id
    user = retrieve_user(access_token=access_token)
    logger.debug(f"User data:\n{user}")
    user_id = user["id"]

    # get followed channels
    streams = retrieve_followed_streams(access_token=access_token, user_id=user_id)

    # filter streams by language
    if languages:
        streams = [stream for stream in streams if stream["language"] in languages]

    return json.dumps(streams, indent=2)


def live_popular(size: int, languages: list[str] | None = None) -> str:
    """List the most popular channels."""
    # obtain access token
    access_token = obtain_access_token()

    # get followed channels
    streams = retrieve_live_streams(
        access_token=access_token,
        size=size,
        language=languages,
    )

    return json.dumps(streams, indent=2)


def parse_languages(value: str | None) -> list[str] | None:
    """Parse the popular argument."""
    if not value or value == "all":
        return None
    return value.split(",")


def do_it(args: argparse.Namespace) -> None:
    """Execute the command."""
    if not args.popular:
        streams = live_followed(languages=args.lang)
    else:
        streams = live_popular(size=args.popular, languages=args.lang)
    print(streams)


def main():
    """Execute main function to handle the CLI parameters and operations."""
    parser = argparse.ArgumentParser(
        description=(
            "Get the list of live streams from the list of following channels in "
            "Twitch."
        )
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true",
    )
    parser.add_argument("-V", "--version", help="show version", action="store_true")
    parser.add_argument(
        "--popular",
        type=int,
        nargs="?",
        const=20,
        help="get the list of live streams with most viewers (top 20 by default).",
    )
    parser.add_argument(
        "-l",
        "--lang",
        nargs="?",
        const="all",
        default="all",
        type=parse_languages,
        help="filter the list of live streams by language.",
    )

    parser.set_defaults(func=do_it)

    args = parser.parse_args()

    # debug logger
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # just print version
    if args.version:
        print(purple.__version__)
        sys.exit(0)

    # check settings
    try:
        settings.client_id
        settings.client_secret
    except ValidationError:
        logger.error(
            "\033[93mYou need to define the client ID and the client secret to execute "
            "purple. This is done using the following environment variables:\033[0m\n\n"
            " - \033[96mPURPLE_CLIENT_ID\033[0m\n"
            " - \033[96mPURPLE_CLIENT_SECRET\033[0m"
        )
        sys.exit(-1)

    args.func(args)
