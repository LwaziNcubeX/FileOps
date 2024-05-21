#!/usr/bin/env python3
"""
detect file type
"""
from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from plugins.helpers.escape_markdown import escape_markdown
from plugins.helpers.file_size import convert_bytes


async def file_detector(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Detect file type
    """
    reply_markup = None
    file = None
    if update.message.document:
        file = update.message.document
        context.bot_data['document'] = file

        keyboard = [
            [
                InlineKeyboardButton("rename", callback_data="rename_file")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    elif update.message.video:
        file = update.message.video
        context.bot_data['video'] = file
    elif update.message.audio:
        file = update.message.audio
        context.bot_data['audio'] = file
    elif update.message.photo:
        file = update.message.photo[-1]
        context.bot_data['photo'] = file

    file_size = convert_bytes(file.file_size)
    if update.message.photo:
        await update.message.reply_text(
            f"*Name*: Photo\n"
            f"*Size:* {escape_markdown(file_size)}\n",
            parse_mode=constants.ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            f"*Name*: {escape_markdown(file.file_name)}\n"
            f"*Size:* {escape_markdown(file_size)}\n"
            f"File Type: {escape_markdown(file.mime_type)}\n",
            parse_mode=constants.ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup
        )

filter_type = (filters.Document.ALL & ~filters.COMMAND | filters.VIDEO | filters.AUDIO | filters.PHOTO)

file_handler = MessageHandler(filter_type, file_detector)
