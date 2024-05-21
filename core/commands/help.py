#!/usr/bin/env python3
"""
Help command
"""
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


async def help_command(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the command /help is issued."""
    await update.message.reply_text("help section.............")


help_handler = CommandHandler("help", help_command)
