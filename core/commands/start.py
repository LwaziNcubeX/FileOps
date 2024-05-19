#!/usr/bin/env python3
"""
start command
"""
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


async def start_command(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the bot"""
    await update.message.reply_text("Hello! I'm FileOps Bot")


start_handler = CommandHandler("start", start_command)
