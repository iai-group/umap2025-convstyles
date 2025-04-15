"""Main module."""

import argparse
import logging

from ada.agent import ADA
from ada.config import DEFAULT_CONFIG_PATH, Config
from ada.dialogue_connector.dialogue_connector_manager import (
    DialogueConnectorManager,
)
from ada.server.flask_socket_platform import ADAPlatform

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


def main(args: argparse.Namespace) -> None:
    """Main function.

    Args:
        args: Arguments from command-line call.
    """
    logger.info("Starting main function.")
    logger.debug(f"Arguments: {args}")

    Config(args.config)
    dc_manager = DialogueConnectorManager(agent_class=ADA)
    platform = ADAPlatform(dc_manager)
    platform.start(args.server, args.port, debug=args.debug)


def parse_args() -> argparse.Namespace:
    """Parses arguments from command-line call.

    Returns:
        Arguments from command-line call.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        help="Path to configuration file",
        default=DEFAULT_CONFIG_PATH,
    )
    parser.add_argument(
        "-s",
        "--server",
        help="Path to server",
        default="127.0.0.1",
    )
    parser.add_argument(
        "-p",
        "--port",
        help="Port to listen on",
        default=5000,
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Debugging mode",
        default=False,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    main(args)
