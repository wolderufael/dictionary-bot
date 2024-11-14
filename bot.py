# import os

# from telegram.ext import Updater, MessageHandler, filters
# from telegram.ext import CommandHandler
# from diction import get_info

# telegram_bot_token = '7676463052:AAHbFgkFUDR5-Js7MfXsxlx39TIzIlvI430'

# updater = Updater(token=telegram_bot_token, use_context=True)
# dispatcher = updater.dispatcher


# # set up the introductory statement for the bot when the /start command is invoked
# def start(update, context):
#     chat_id = update.effective_chat.id
#     context.bot.send_message(chat_id=chat_id, text="Hello there. Provide any English word and I will give you a bunch "
#                                                    "of information about it.")


# # obtain the information of the word provided and format before presenting.
# def get_word_info(update, context):
#     # get the word info
#     word_info = get_info(update.message.text)

#     # If an invalid English word was provided by the user, return the custom response from get_info() and exit the
#     # function
#     if word_info.__class__ is str:
#         update.message.reply_text(word_info)
#         return

#     # extract the word the user provided
#     word = word_info['word']

#     # extract the origin of the word
#     origin = word_info['origin']
#     meanings = '\n'

#     synonyms = ''
#     definition = ''
#     example = ''
#     antonyms = ''

#     # a word may have several meanings. We'll use this counter to track each of the meanings provided from the response
#     meaning_counter = 1

#     for word_meaning in word_info['meanings']:
#         meanings += 'Meaning ' + str(meaning_counter) + ':\n'

#         for word_definition in word_meaning['definitions']:
#             # extract the each of the definitions of the word
#             definition = word_definition['definition']

#             # extract each example for the respective definition
#             if 'example' in word_definition:
#                 example = word_definition['example']

#             # extract the collection of synonyms for the word based on the definition
#             for word_synonym in word_definition['synonyms']:
#                 synonyms += word_synonym + ', '

#             # extract the antonyms of the word based on the definition
#             for word_antonym in word_definition['antonyms']:
#                 antonyms += word_antonym + ', '

#         meanings += 'Definition: ' + definition + '\n\n'
#         meanings += 'Example: ' + example + '\n\n'
#         meanings += 'Synonym: ' + synonyms + '\n\n'
#         meanings += 'Antonym: ' + antonyms + '\n\n\n'

#         meaning_counter += 1

#     # format the data into a string
#     message = f"Word: {word}\n\nOrigin: {origin}\n{meanings}"

#     update.message.reply_text(message)


# # run the start function when the user invokes the /start command
# dispatcher.add_handler(CommandHandler("start", start))

# # invoke the get_word_info function when the user sends a message
# # that is not a command.
# dispatcher.add_handler(MessageHandler(Filters.text, get_word_info))
# updater.start_webhook(listen="0.0.0.0",
#                       port=int(os.environ.get('PORT', 5000)),
#                       url_path=telegram_bot_token,
#                     #   webhook_url='https://dictionary-bot1.herokuapp.com/' + telegram_bot_token
#                       webhook_url='https://dictionary-bot-pbld.onrender.com/' + telegram_bot_token
#                       )


import os
import tempfile
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)
from diction import get_info
from dotenv import load_dotenv
import torch
import cv2
import numpy as np
import os


# Load environment variables once
load_dotenv('.env')
telegram_bot_token = os.getenv('TOKEN2')

##########Clone repo and install dependecies###################
import git
import os
import subprocess

# Clone the repository
git.Repo.clone_from('https://github.com/ultralytics/yolov5.git', 'yolov5')


# Change the working directory to yolov5
os.chdir('yolov5')

# Install dependencies from requirements.txt
subprocess.run(['pip', 'install', '-r', 'requirements.txt'])


##########################################################################

# Initialize the Application
app = Application.builder().token(telegram_bot_token).build()

# Introductory statement for the bot when the /start command is invoked
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello there. Provide any English word and I will give you a bunch of information about it."
    )

# Obtain the information of the word provided and format before presenting.
async def get_word_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # get the word info
    word_info = get_info(update.message.text)

    # If an invalid English word was provided by the user, return the custom response from get_info() and exit
    if isinstance(word_info, str):
        await update.message.reply_text(word_info)
        return

    # Extract the word information
    word = word_info['word']
    # origin = word_info['origin']
    meanings = '\n'
    synonyms = ''
    definition = ''
    example = ''
    antonyms = ''

    # Counter to track each meaning
    meaning_counter = 1
    for word_meaning in word_info['meanings']:
        meanings += f'Meaning {meaning_counter}:\n'

        for word_definition in word_meaning['definitions']:
            definition = word_definition['definition']
            example = word_definition.get('example', '')

            synonyms = ', '.join(word_definition.get('synonyms', []))
            antonyms = ', '.join(word_definition.get('antonyms', []))

            meanings += f'Definition: {definition}\n\n'
            meanings += f'Example: {example}\n\n'
            meanings += f'Synonym: {synonyms}\n\n'
            meanings += f'Antonym: {antonyms}\n\n\n'

        meaning_counter += 1

    # Format the data into a string
    message = f"Word: {word}\n{meanings}"
    await update.message.reply_text(message)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Download the photo
    photo_file = await update.message.photo[-1].get_file()
    photo_path = await photo_file.download_to_drive()

    # Load image with OpenCV
    img = cv2.imread(photo_path)

    # Load pre-trained YOLOv5 model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    results = model(img)

    # Render detections on image
    detected_img = results.render()[0]  # results.render() returns list of images (one for each input image)

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        temp_img_path = tmp_file.name
        cv2.imwrite(temp_img_path, detected_img)

    # Send the detected image back to the user
    await update.message.reply_photo(photo=open(temp_img_path, 'rb'))
    
# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_word_info))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))  # Photo handler

# # Run the webhook for the bot
# app.run_webhook(
#     listen="0.0.0.0",
#     port=int(os.environ.get('PORT', 5001)),
#     url_path=telegram_bot_token,
#     webhook_url=f'https://dictionary-bot-pbld.onrender.com/{telegram_bot_token}'
# )

# Start the bot
app.run_polling()