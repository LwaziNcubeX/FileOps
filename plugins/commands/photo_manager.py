#!/usr/bin/env python3
"""
photo manager
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, \
    filters

from plugins.commands.analyze_colors import analyze_colors
from plugins.commands.convert_to_pdf import convert_to_pdf
from plugins.helpers.escape_markdown import escape_markdown
from plugins.helpers.file_size import convert_bytes

REQUEST_PHOTO, ACTION, CONVERT_TO_PDF, ANALYZE_COLORS = range(4)


async def photo_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    photo manager
    """
    await update.message.reply_text('Please send me a photo.')
    return REQUEST_PHOTO


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    get photo
    """
    photo = None
    photo_name = "Photo"

    if update.message.photo:
        photo = update.message.photo[-1]
    # If there's no photo, check if the message contains a document with a mime type indicating an image
    elif update.message.document and update.message.document.mime_type in ['image/png', 'image/jpeg']:
        photo = update.message.document
        photo_name = update.message.document.file_name

    context.bot_data['photo'] = photo

    custom_keyboard = [
        [InlineKeyboardButton("✏️ Convert To PDF", callback_data='convert_to_pdf')],
        [InlineKeyboardButton("🏙️ Analyze image colors", callback_data='analyze_colors')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel')],
    ]

    file_size = convert_bytes(photo.file_size)

    await update.message.reply_text(
        f"*Name*: {escape_markdown(photo_name)}\n"
        f"*Size:* {escape_markdown(file_size)}\n",
        parse_mode=constants.ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(custom_keyboard)
    )
    return ACTION


async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's choice.
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'convert_to_pdf':
        await query.edit_message_text(
            f'Send me a new PDF name\n'
            f'press /skip to use default name: '
        )
        return CONVERT_TO_PDF
    elif query.data == 'analyze_colors':
        return ANALYZE_COLORS
    else:
        await query.edit_message_text('Terminating Process.....')
        await query.edit_message_text('You can start a new task now!😇')
        return ConversationHandler.END

photo_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('photo_manager', photo_manager)],
    states={
        REQUEST_PHOTO: [MessageHandler(filters.PHOTO | filters.Document.IMAGE, get_photo)],
        ACTION: [CallbackQueryHandler(handle_action, pattern='^(convert_to_pdf|analyze_colors|cancel)$')],
        CONVERT_TO_PDF: [MessageHandler(filters.TEXT & ~filters.COMMAND, convert_to_pdf)],
        ANALYZE_COLORS: [CallbackQueryHandler(analyze_colors, pattern="^analyze_colors$")]
    },
    fallbacks=[],
    allow_reentry=True
)