"""Module with CLI application."""

import argparse
import json
import logging
import sys

import purple

from .api import (
    retrieve_followed_channels,
    retrieve_followed_streams,
    retrieve_user,
)
from .auth import obtain_access_token

logger = logging.getLogger(__name__)


def followed(args: argparse.Namespace) -> None:
    """List the channels the user follows."""
    # logger
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # obtain access token
    access_token = obtain_access_token()

    # get user id
    user = retrieve_user(access_token=access_token)
    logger.debug(f"User data:\n{user}")
    user_id = user["id"]

    # get followed channels
    followed = retrieve_followed_channels(access_token=access_token, user_id=user_id)

    print(json.dumps(followed, indent=2))


def live(args: argparse.Namespace) -> None:
    """List the channels the user follows."""
    # logger
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # obtain access token
    access_token = obtain_access_token()

    # get user id
    user = retrieve_user(access_token=access_token)
    logger.debug(f"User data:\n{user}")
    user_id = user["id"]

    # get followed channels
    streams = retrieve_followed_streams(access_token=access_token, user_id=user_id)

    print(json.dumps(streams, indent=2))


def main():
    """Execute main function to handle the CLI parameters and operations."""
    parser = argparse.ArgumentParser(
        description="Collects data from your Twitch account to use it in other scripts."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true",
    )
    parser.add_argument("-V", "--version", help="show version", action="store_true")
    parser.set_defaults(func=live)

    args = parser.parse_args()

    # just print version
    if args.version:
        print(purple.__version__)
        sys.exit(0)

    args.func(args)
