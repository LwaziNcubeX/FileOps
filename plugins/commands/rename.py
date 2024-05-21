#!/usr/bin/env python3
"""
rename file
"""
import os
from telegram import Update, Bot
from telegram.ext import ContextTypes, CallbackQueryHandler


async def rename_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Rename file
    """
    from bot import BOT_TOKEN
    query = update.callback_query

    document = context.bot_data.get('document')

    await query.answer()
    await query.edit_message_text(f"Send a new file name\n")

    bot = Bot(token=BOT_TOKEN)
    file_id = document.file_id
    new_file = await bot.get_file(file_id)
    await new_file.download_to_drive(document.file_name)

    os.rename(new_file.file_path, 'test.jpg')

    await bot.send_document(chat_id=query.message.chat.id, document=new_file.file_path)

rename_callback = CallbackQueryHandler(rename_file)
