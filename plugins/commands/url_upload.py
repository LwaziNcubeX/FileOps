#!/usr/bin/env python3
"""
upload files from url
"""
import logging
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler,
                          ContextTypes)

# Define states
URL, ACTION, RENAME, DOWNLOAD = range(4)


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Please send me the URL of the file you want to download.')
    return URL


async def receive_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['url'] = update.message.text
    response = requests.head(context.user_data['url'], allow_redirects=True)
    filename = os.path.basename(context.user_data['url'])
    filesize = response.headers.get('content-length', 'unknown size')

    context.user_data['filename'] = filename
    context.user_data['filesize'] = filesize

    keyboard = [
        [InlineKeyboardButton("Rename and Upload", callback_data='rename')],
        [InlineKeyboardButton("Upload Directly", callback_data='upload')],
        [InlineKeyboardButton("Cancel", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"File name: {filename}\nFile size: {filesize}\nWhat would you like to do?",
                              reply_markup=reply_markup)
    return ACTION


async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    new_filename = update.message.text
    context.user_data['new_filename'] = new_filename
    await update.message.reply_text(f'New file name set to {new_filename}. Uploading the file...')
    await download_and_upload(update, context)
    return ConversationHandler.END


async def download_and_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = context.user_data['url']
    filename = context.user_data.get('new_filename', context.user_data['filename'])

    response = requests.get(url, stream=True)
    filepath = os.path.join('/tmp', filename)

    with open(filepath, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    await update.message.reply_document(document=open(filepath, 'rb'))
    os.remove(filepath)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Process cancelled.')
    return ConversationHandler.END

conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('test', test)],
        states={
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_url)],
            ACTION: [CallbackQueryHandler(handle_action, pattern='^(rename|upload|cancel)$')],
            RENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, rename_file)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )