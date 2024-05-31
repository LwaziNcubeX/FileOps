#!/usr/bin/env python3
"""
detect file type
"""
from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from plugins.helpers.escape_markdown import escape_markdown
from plugins.helpers.file_size import convert_bytes

FIRST, SECOND = range(2)


async def detect_doc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    detect document
    """
    document = update.message.document
    context.bot_data['document'] = document

    custom_keyboard = [
        [InlineKeyboardButton("✏️ Rename", callback_data='Rename')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel')],
    ]

    file_size = convert_bytes(document.file_size)
    file_name = document.file_name

    await update.message.reply_text(
        f"*Name*: {escape_markdown(file_name)}\n"
        f"*Size:* {escape_markdown(file_size)}\n",
        parse_mode=constants.ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(
            custom_keyboard
        )
    )

    return FIRST

GET_PDF_NAME, CONVERT_TO_PDF, CONVERT = range(3)


async def detect_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    detect photo
    """
    photo = update.message.photo[-1]
    context.bot_data['photo'] = photo

    custom_keyboard = [
        [InlineKeyboardButton("✏️ Convert To PDF", callback_data='convert_to_pdf')],
         [InlineKeyboardButton("Analyse image colors", callback_data='convert')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel')],
    ]

    file_size = convert_bytes(photo.file_size)

    await update.message.reply_text(
        f"*Name*: Photo\n"
        f"*Size:* {escape_markdown(file_size)}\n",
        parse_mode=constants.ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(custom_keyboard)
    )

    return GET_PDF_NAME
