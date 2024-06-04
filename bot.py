#!/usr/bin/env python3
"""
This is the main file for the bot.
"""
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.request import HTTPXRequest

from plugins.commands.convert_to_pdf import pdf_conv_handler
from plugins.commands.help import help_handler
from plugins.commands.rename import conv_handler
from plugins.commands.docx_pdf import docx_to_pdf_handler 
from plugins.commands.start import start_handler
from plugins.commands.analyze_colors import analyze_callback
from plugins.commands.url_upload import conv_handler2
from plugins.helpers.logger import logger

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
    app.add_handler(analyze_callback)
    # conv Handlers
    app.add_handler(conv_handler)
    app.add_handler(conv_handler2)
    app.add_handler(pdf_conv_handler)

    app.add_handler(docx_to_pdf_handler)


    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()