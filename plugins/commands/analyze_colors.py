import os
from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import webcolors

def closest_color(requested_color):
    """
    Given a color, find the closest named CSS3 color
    """
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def image_analyser(path, num_colors=8):
    """
    Analyze an image and return the color percentages
    """
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.reshape((-1, 3))

    kmeans = KMeans(n_clusters=num_colors, random_state=42)
    kmeans.fit(img)
    colors = kmeans.cluster_centers_
    labels = kmeans.labels_

    counts = np.bincount(labels)
    percentages = counts / len(labels) * 100

    color_percentages = {tuple(map(int, color)): percentage for color, percentage in zip(colors, percentages)}

    return color_percentages


def generate_chart(data, file_path, background_color='white'):
    """
    Generate a pie chart of the color percentages
    """
    sizes = list(data.values())
    colors = [np.array(color)/255 for color in data.keys()]

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=['']*len(sizes), colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Color Distribution')

    # Set background color
    plt.gcf().set_facecolor(background_color)

    plt.savefig(file_path, facecolor=background_color)
    plt.close()


async def analyze_colors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Analyze the photo and send a pie chart of the color percentages
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Image will be analyzed...")

    image = context.bot_data.get('photo')
    if not image:
        await query.edit_message_text("No photo found. Please send a photo first.")
        return ConversationHandler.END  # Ensure conversation ends if no photo

    await query.edit_message_text("Downloading file... please wait")

    file_id = image.file_id
    new_file = await context.bot.get_file(file_id)

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    image_file_path = os.path.join('downloads', f'{file_id}.jpg')
    await new_file.download_to_drive(image_file_path)

    await context.bot.edit_message_text('File downloaded...', chat_id=query.message.chat_id, message_id=query.message.message_id)

    colors_data = image_analyser(image_file_path)

    background_color = '#f0f0f0'

    chart_file_path = os.path.join('downloads', f'{file_id}_chart.png')
    generate_chart(colors_data, chart_file_path, background_color)

    with open(chart_file_path, 'rb') as chart_file:
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=chart_file)

    color_info = "\n".join([f"Color {i+1}: {closest_color(color)} - {percentage:.2f}%" for i, (color, percentage) in enumerate(colors_data.items())])
    await context.bot.send_message(chat_id=query.message.chat_id, text=f"Color Analysis:\n{color_info}")

    os.remove(image_file_path)
    os.remove(chart_file_path)

    context.bot_data.pop('photo', None)

    return ConversationHandler.END  # End conversation after analysis

