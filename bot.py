#!/usr/bin/env python3
"""
This is the main file for the bot.
"""
import os
from telegram import Update
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from telegram.request import HTTPXRequest

from plugins.helpers.filter_name import file_name_handler
from plugins.helpers.logger import logger
from plugins.commands.file_detect import file_handler
from plugins.commands.help import help_handler
from plugins.commands.start import start_handler
from plugins.commands.rename import rename_callback
from plugins.commands.convert_to_pdf import to_pdf_callback

# Load environment variables
try:
    load_dotenv()
except FileNotFoundError:
    logger.info("No .env file found. Ignore if you are using a production bot")

BOT_TOKEN = os.getenv("BOT_TOKEN")

logger.info("Starting Bot...")


def main() -> None:
    """
    Register handlers and run the bot
    """
    # Create an HTTPXRequest object with increased timeout settings
    request = HTTPXRequest(
        connect_timeout=10.0,  # Increase connection timeout
        read_timeout=20.0  # Increase read timeout
    )

    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    # Command Handlers
    app.add_handler(start_handler)
    app.add_handler(help_handler)

    # Message Handlers
    app.add_handler(file_handler)
    app.add_handler(file_name_handler)

    # Callback Query Handlers
    app.add_handler(rename_callback)
    app.add_handler(to_pdf_callback)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
