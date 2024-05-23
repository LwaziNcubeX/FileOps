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


async def rename_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Rename file
    """
    from bot import BOT_TOKEN
    query = update.callback_query

    document = context.bot_data.get('document')

    await query.answer()
    await query.edit_message_text(f"Send a new file name\n")

    new_file_name = await filter_name(update, context)

    bot = Bot(token=BOT_TOKEN)
    file_id = document.file_id
    new_file = await bot.get_file(file_id)
    await new_file.download_to_drive(document.file_name)

    if new_file_name is None:
        new_file_name = "new_file_name.jpg"

    print(new_file_name)
    shutil.move(document.file_name, str(new_file_name))

    await sleep(5)

    await bot.send_document(chat_id=query.message.chat.id, document=str(new_file_name))

rename_callback = CallbackQueryHandler(rename_file)

