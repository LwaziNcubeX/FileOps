import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import Application, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt

def image_analyser(path):
    img = cv2.imread(path)
    all_pixels = img.shape[0] * img.shape[1]
    precoded_pixels = {
        (255, 255, 255): ["white", 0],
        (0, 0, 0): ["black", 0],
        (255, 0, 0): ["blue", 0],
        (0, 255, 0): ["green", 0],
        (0, 0, 255): ["red", 0],
        (255, 255, 0): ["yellow", 0],
        (250, 128, 250): ["mauve", 0],
        (105, 245, 195): ["cyan", 0],
    }
    
    colors = np.array(list(precoded_pixels.keys()))
    pixels = img.reshape((-1, 3))
    
    # Calculate the difference between each pixel and the precoded colors
    diffs = np.linalg.norm(pixels[:, None] - colors, axis=2)
    
    # Get the index of the closest color
    closest_colors = np.argmin(diffs, axis=1)
    
    # Count occurrences of each color
    unique, counts = np.unique(closest_colors, return_counts=True)
    
    color_percentages = {}
    for i, count in zip(unique, counts):
        color = colors[i]
        name = precoded_pixels[tuple(color)][0]
        percentage = (count * 100) / all_pixels
        color_percentages[name] = percentage
    
    return color_percentages

def generate_chart(data, file_path):
    labels = list(data.keys())
    sizes = list(data.values())
    colors = ['white', 'black', 'blue', 'green', 'red', 'yellow', 'cyan']

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Color Distribution')
    plt.savefig(file_path)
    plt.close()

async def analyse_colors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> dict:
    """
    Analyze image colors and return the data.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Image will be analyzed...")

    image = context.bot_data.get('photo')

    message = await query.edit_message_text("Downloading file... please wait")

    file_id = image.file_id
    new_file = await context.bot.get_file(file_id)

    # Create a directory to save the image
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    image_file_path = os.path.join('downloads', f'{file_id}.jpg')
    await new_file.download_to_drive(image_file_path)

    await context.bot.edit_message_text(f'File downloaded...', chat_id=query.message.chat_id, message_id=query.message.message_id)

    # Analyze image colors
    colors_data = image_analyser(image_file_path)

    # Generate chart
    chart_file_path = os.path.join('downloads', f'{file_id}_chart.png')
    generate_chart(colors_data, chart_file_path)

    # Send the chart
    with open(chart_file_path, 'rb') as chart_file:
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=chart_file)

    # Clean up
    os.remove(image_file_path)
    os.remove(chart_file_path)

    context.user_data.pop('photo', None)

    return colors_data

analyze_callback = CallbackQueryHandler(analyse_colors, pattern="^analyze_colors$")


