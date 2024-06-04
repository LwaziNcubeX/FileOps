#!/usr/bin/env python3
"""
Convert image to PDF
"""
import os
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters 
from PIL import Image


async def convert_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Convert image to PDF
    """
    context.user_data['pdf_name'] = update.message.text
    new_pdf_name = update.message.text
    image = context.bot_data.get('photo')

    message = await update.message.reply_text("Downloading file... please wait\n")

    file_id = image.file_id
    new_file = await context.bot.get_file(file_id)

    # Create a directory to save the image and PDF
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    image_file_path = os.path.join('downloads', new_pdf_name)
    await new_file.download_to_drive(image_file_path)

    await context.bot.edit_message_text(f'File downloaded......', chat_id=update.message.chat_id,
                                        message_id=message.message_id)

    # Convert image to PDF
    pdf_file_path = image_file_path.rsplit('.', 1)[0] + ".pdf"
    with Image.open(image_file_path) as img:
        img.convert('RGB').save(pdf_file_path, "PDF", resolution=100.0)

    await context.bot.edit_message_text(f'File converted to PDF......', chat_id=update.message.chat_id,
                                        message_id=message.message_id)

    # Send the converted PDF back to the user
    await context.bot.send_document(chat_id=update.message.chat.id, document=pdf_file_path)

    # Clean up
    os.remove(image_file_path)
    os.remove(pdf_file_path)

    return ConversationHandler.END
