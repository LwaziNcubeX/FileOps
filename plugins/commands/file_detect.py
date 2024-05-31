#!/usr/bin/env python3
"""
detect file type
"""
import re

import requests
from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

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

GET_PDF_NAME, CONVERT_TO_PDF = range(2)


async def detect_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    detect photo
    """
    photo = update.message.photo[-1]
    context.bot_data['photo'] = photo

    custom_keyboard = [
        [InlineKeyboardButton("✏️ Convert To PDF", callback_data='convert_to_pdf')],
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

REQUEST_URL_FILE_NAME, RENAME_AND_UPLOAD = range(2)


async def detect_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Detect URL in the message and download the file with progress updates.
    """
    check_url = bool(re.search(r'https?://\S+', update.message.text))

    if check_url:
        url = update.message.text.strip()
        await update.message.reply_text(
            f'Name: {url.rsplit("/", 1)[-1]}\n'
            f'Size: {convert_bytes(0)}\n',
            parse_mode=constants.ParseMode.MARKDOWN_V2
        )

    return REQUEST_URL_FILE_NAME
"""

        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        chunk_size = 1024
        file_name = url.rsplit('/', 1)[-1]
        file_path = 'downloads/' + file_name

        message = await context.bot.send_message(update.message.chat_id, f"Processing...")

        with open(file_path, 'wb') as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                downloaded_size += len(data)

                # Send progress update every 1 MB
                if downloaded_size % (1024 * 1024) == 0 or downloaded_size == total_size:
                    progress = (downloaded_size / total_size) * 100
                    await context.bot.edit_message_text(f"Download progress: {progress:.2f}%",
                                                        chat_id=update.message.chat_id,
                                                        message_id=message.message_id)

        await update.message.reply_text(f"Download complete. File saved to {file_path}")

url_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    detect_url
)
"""