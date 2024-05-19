#!/usr/bin/env python3
"""
Register All handlers here
"""
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder
from core.commands.help import help_handler
from core.commands.start import start_handler
from core.helpers.logger import logger

try:
    load_dotenv()
except FileNotFoundError:
    logger.info("No .env file found. ignore if you are using a production bot")

BOT_TOKEN = os.getenv("BOT_TOKEN")


def register_handlers() -> None:
    """Register all handlers"""
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # Command Handlers
    app.add_handler(start_handler)
    app.add_handler(help_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)
