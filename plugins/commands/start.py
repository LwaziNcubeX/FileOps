#!/usr/bin/env python3
"""
start command
"""
from telegram import Update, constants
from telegram.ext import CommandHandler, ContextTypes
from database.db import DATABASE
from plugins.helpers.escape_markdown import escape_markdown
from translations.lang import get_translation


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a greeting message to the user when the '/start' command is issued.
    """
    await DATABASE.check_document_id(update)

    start_message = await get_translation("start_message", "Welcome!", update)

    first_name = update.effective_user.first_name
    start_message = start_message.format(name=first_name)

    await update.message.reply_text(start_message, parse_mode=constants.ParseMode.HTML, quote=True)

start_handler = CommandHandler("start", start_command)
