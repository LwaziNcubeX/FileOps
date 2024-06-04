#!/usr/bin/env python3
"""
Upload files from URL
"""
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import (MessageHandler, filters, CallbackQueryHandler, ConversationHandler,
                          ContextTypes)

from plugins.commands.file_detect import URL, ACTION, RENAME, detect_url
from plugins.commands.rename import cancel
from plugins.helpers.escape_markdown import escape_markdown
from plugins.helpers.file_size import convert_bytes


async def receive_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive URL and display information about the file.
    """
    context.user_data['url'] = update.message.text
    try:
        response = requests.head(context.user_data['url'], allow_redirects=True)
        filename = os.path.basename(context.user_data['url'])
        filesize = convert_bytes(int(response.headers.get('content-length', 0)))

        context.user_data['filename'] = filename
        context.user_data['filesize'] = filesize

        keyboard = [
            [InlineKeyboardButton("Rename and Upload", callback_data='rename')],
            [InlineKeyboardButton("Upload Directly", callback_data='upload')],
            [InlineKeyboardButton("Cancel", callback_data='cancel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"*Name*: {escape_markdown(filename)}\n"
            f"*Size:* {escape_markdown(filesize)}\n\n",
            parse_mode=constants.ParseMode.MARKDOWN_V2,
            reply_markup=reply_markup)
    except requests.exceptions.RequestException:
        await update.message.reply_text('Could not fetch URL. Please check the URL and try again.')
    return ACTION


async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle actions from the user.
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'rename':
        await query.edit_message_text('Please send me the new file name.')
        return RENAME
    elif query.data == 'upload':
        await query.edit_message_text('Uploading the file...')
        return await download_and_upload(update, context)
    else:
        await query.edit_message_text('Process cancelled.')
        return ConversationHandler.END


async def rename_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Rename the file before uploading.
    """
    new_filename = update.message.text
    context.user_data['new_filename'] = new_filename
    await download_and_upload(update, context)
    return ConversationHandler.END


async def download_and_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Download the file and send it to the user.
    """
    url = context.user_data['url']
    filename = context.user_data.get('new_filename', context.user_data['filename'])

    try:
        response = requests.get(url, stream=True)
        filepath = os.path.join('/tmp', filename)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Processing...")

        with open(filepath, 'wb') as file:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                downloaded_size += len(data)

                # Send progress update every 1 MB
                if downloaded_size % (1024 * 1024) == 0 or downloaded_size == total_size:
                    progress = (downloaded_size / total_size) * 100
                    await context.bot.edit_message_text(f"Download progress: {progress:.2f}%",
                                                        chat_id=update.message.chat_id,
                                                        message_id=message.message_id)

        await context.bot.send_document(chat_id=update.effective_chat.id, document=open(filepath, 'rb'))
        os.remove(filepath)
    except requests.exceptions.RequestException:
        await update.message.reply_text('Could not download the file. Please check the URL and try again.')
    return ConversationHandler.END

conv_handler2 = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, detect_url)],
        states={
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_url)],
            ACTION: [CallbackQueryHandler(handle_action, pattern='^(rename|upload|cancel)$')],
            RENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, rename_file)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern='^cancel$')],
    )

