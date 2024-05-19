#!/usr/bin/env python3
"""
This is the main file for the bot.
"""
from core import register_handlers
from core.helpers.logger import logger

logger.info("Starting Bot...")


def main() -> None:
    """
    register handlers and runs the bot
    """
    register_handlers()


if __name__ == "__main__":
    main()
