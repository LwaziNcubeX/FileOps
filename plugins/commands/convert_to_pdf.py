#!/usr/bin/env python3
"""
rename file
"""
import os
import shutil
from asyncio import sleep

from telegram import Update, Bot, ForceReply
from telegram.ext import ContextTypes, CallbackQueryHandler

from plugins.helpers.filter_name import filter_name


async def convert_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    convert to pdf
    """
    from bot import BOT_TOKEN
    query = update.callback_query

    image = context.bot_data.get('photo')

    await query.answer()
    await query.edit_message_text(f"will be converted to pdf \n")




    bot = Bot(token=BOT_TOKEN)
    file_id = image.file_id
    new_file = await bot.get_file(file_id)
    await new_file.download_to_drive(image.file_name)

    await bot.send_document(chat_id=query.message.chat.id, document=str(new_file_name))

to_pdf_callback = CallbackQueryHandler(convert_to_pdf, pattern="^convert_to_pdf$")