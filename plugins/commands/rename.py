#!/usr/bin/env python3
"""
rename file
"""
import os
import shutil

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler

from plugins.commands.file_detect import SECOND, FIRST, detect_doc
from plugins.helpers.logger import logger



async def req_file_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    request file name
    """
    query = update.callback_query
    await query.answer()

    context.user_data['choice'] = update.callback_query.data
    custom_keyboard = [
        [InlineKeyboardButton("Cancel", callback_data='cancel')],
    ]
    await query.edit_message_text(
        f'Send me a new file name',
        reply_markup=InlineKeyboardMarkup(custom_keyboard)
    )

    return SECOND


async def rename_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    rename file
    """
    context.user_data['file_name'] = update.message.text
    document = context.bot_data.get('document')
    new_file_name = update.message.text

    try:
        # Download the file
        file_id = document.file_id
        new_file = await context.bot.get_file(file_id)
        await new_file.download_to_drive(document.file_name)

        # Check if the source file exists
        if not os.path.isfile(document.file_name):
            raise FileNotFoundError(f"No such file or directory: '{document.file_name}'")

        # Move the file
        shutil.move(document.file_name, new_file_name)

        # Send the renamed file back
        await context.bot.send_document(chat_id=update.effective_chat.id, document=new_file_name)

    except FileNotFoundError as fnf_error:
        logger.error(fnf_error)
        await update.message.reply_text(f"Error: {fnf_error}")
    except Exception as e:
        logger.exception("An unexpected error occurred")
        await update.message.reply_text(f"An unexpected error occurred: {e}")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel and end the conversation
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"Cancelling...")
    await query.edit_message_text('You can send a new task now!😇')

    return ConversationHandler.END

async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel and end the conversation
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"okay")
    await query.edit_message_text('You can send a new task now!😇')

    return ConversationHandler.END

# from plugins.commands.docx_pdf import docx_filter
conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Document.ALL & ~filters.COMMAND , detect_doc)],
        states={
            FIRST: [CallbackQueryHandler(req_file_name, pattern='^Rename$')],
            SECOND: [MessageHandler(filters.TEXT & ~filters.COMMAND, rename_file)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern='^cancel$')],
    )
