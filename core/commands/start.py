#!/usr/bin/env python3
"""
start command
"""
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


async def start_command(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a greeting message to the user when the '/start' command is issued.
    """
    await update.message.reply_text(
        f"Hello! {update.effective_user.first_name}, "
        f"I'm FileOps Bot")


start_handler = CommandHandler("start", start_command)
