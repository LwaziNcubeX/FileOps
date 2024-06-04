#!/usr/bin/env python3
"""
Convert DOCX to PDF
"""
import os
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from telegram.ext.filters import MessageFilter
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from plugins.commands.file_detect import CONVERT_TO_PDF, detect_docx, GET_PDF_NAME, GET_DOCX_NAME, DOCX_TO_PDF
from plugins.commands.rename import cancel

last_message_ids = {}

class DocxFilter(MessageFilter):
    """ class for the creation for a custom
      filter method 
    for docx files 
    """
    def filter(self, message: Message) -> bool:
        if message.document:
            return message.document.mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        return False

docx_filter = DocxFilter()

async def req_pdf_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Request PDF name
    """
    query = update.callback_query
    await query.answer()

    context.user_data['choice'] = update.callback_query.data
    custom_keyboard = [
        [InlineKeyboardButton("Cancel", callback_data='cancel')],
    ]
    message = await query.edit_message_text(
        'Send me a new PDF name',
        reply_markup=InlineKeyboardMarkup(custom_keyboard)
    )

    last_message_ids[query.message.chat.id] = message.message_id

    return DOCX_TO_PDF

async def docx_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Convert DOCX to PDF
    """
    context.user_data['pdf_name'] = update.message.text
    new_pdf_name = update.message.text
    docx_file = context.bot_data.get('docx')

    message = await update.message.reply_text("Downloading file... please wait\n")
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=last_message_ids[update.message.chat.id])

    file_id = docx_file.file_id
    new_file = await context.bot.get_file(file_id)

    # Create a directory to save the DOCX and PDF files
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    docx_file_path = os.path.join('downloads', f"{new_pdf_name}.docx")
    pdf_file_path = os.path.join('downloads', f"{new_pdf_name}.pdf")
    await new_file.download_to_drive(docx_file_path)

    await context.bot.edit_message_text('File downloaded...', chat_id=update.message.chat_id,
                                        message_id=message.message_id)

    # Convert DOCX to PDF
    convert_docx_to_pdf(docx_file_path, pdf_file_path)

    # Send the converted PDF back to the user
    await context.bot.send_document(chat_id=update.message.chat_id, document=pdf_file_path)

    # Clean up
    os.remove(docx_file_path)
    os.remove(pdf_file_path)

    return ConversationHandler.END

def convert_docx_to_pdf(docx_path, pdf_path):
    # Load the DOCX file
    doc = Document(docx_path)
    
    # Create a PDF file
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    margin = 1 * inch
    text_width = width - 2 * margin
    text_height = height - 2 * margin
    y = height - margin
    
    # Set font
    c.setFont("Helvetica", 12)
    
    # Read and write the content
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            lines = run.text.split('\n')
            for line in lines:
                y -= 12  # Move cursor down by the height of the text line
                if y < margin:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = height - margin
                c.drawString(margin, y, line)
    
    # Save the PDF
    c.save()

# Define your ConversationHandler here
docx_to_pdf_handler = ConversationHandler(
    entry_points=[MessageHandler(docx_filter, detect_docx)],
    states={
        GET_DOCX_NAME: [CallbackQueryHandler(req_pdf_name, pattern='^convert_to_pdf$')],
        DOCX_TO_PDF: [MessageHandler(filters.TEXT & ~filters.COMMAND, docx_to_pdf)],
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern='^cancel$')],
)
