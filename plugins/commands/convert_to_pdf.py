#!/usr/bin/env python3
"""
Convert image to PDF
"""
import os
from telegram import Update, Bot
from telegram.ext import ContextTypes, CallbackQueryHandler
from PIL import Image

async def convert_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Convert image to PDF
    """
    from bot import BOT_TOKEN
    query = update.callback_query

    image = context.bot_data.get('photo')

    await query.answer()
    await query.edit_message_text("Will be converted to PDF\n")

    bot = Bot(token=BOT_TOKEN)
    file_id = image.file_id
    new_file = await bot.get_file(file_id)

    # Create a directory to save the image and PDF
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # Set the image file name manually since PhotoSize object has no file_name attribute
    image_file_name = f"{file_id}.jpg"
    image_file_path = os.path.join('downloads', image_file_name)
    await new_file.download_to_drive(image_file_path)

    # Convert image to PDF
    pdf_file_path = image_file_path.rsplit('.', 1)[0] + ".pdf"
    with Image.open(image_file_path) as img:
        img.convert('RGB').save(pdf_file_path, "PDF", resolution=100.0)

    # Send the converted PDF back to the user
    await bot.send_document(chat_id=query.message.chat.id, document=pdf_file_path)

    # Clean up
    os.remove(image_file_path)
    os.remove(pdf_file_path)

to_pdf_callback = CallbackQueryHandler(convert_to_pdf, pattern="^convert_to_pdf$")
