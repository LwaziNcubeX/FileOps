#!/usr/bin/env python3
"""
filter name
"""
from telegram import Update, Bot
from telegram.ext import ContextTypes, MessageHandler, filters


async def filter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    filter name
    """
    if update.message is not None and update.message.text is not None:
        file_name = update.message.text
        return file_name
    return None


file_name_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    lambda update, context: filter_name(update, context)
)
