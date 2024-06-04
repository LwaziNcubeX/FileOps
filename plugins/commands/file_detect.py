#!/usr/bin/env python3
"""
detect file types
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


# GET_DOCX_NAME, DOCX_TO_PDF = range(2)


# async def detect_docx(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """
#     detect docx
#     """
#     docx = update.message.document
#     context.bot_data['docx'] = docx

#     custom_keyboard = [
#         [InlineKeyboardButton("Convert docx To PDF", callback_data='convert_to_pdf')],
#         [InlineKeyboardButton("❌ Cancel", callback_data='cancel')],
#     ]

#     file_size = convert_bytes(docx.file_size)

#     await update.message.reply_text(
#         f"*Name*: Docx\n"
#         f"*Size:* {escape_markdown(file_size)}\n",
#         parse_mode=constants.ParseMode.MARKDOWN_V2,
#         reply_markup=InlineKeyboardMarkup(custom_keyboard)
#     )

#     return GET_PDF_NAME

    return GET_PDF_NAME
