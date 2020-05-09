import os
import random
from datetime import datetime
import telegram
from telegram.ext import Updater, CommandHandler
import logging
import re
import requests
from dotenv import load_dotenv
from telegram.ext import MessageHandler, Filters


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
HEROKU_BOT_URL = os.getenv("HEROKU_BOT_URL")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
PORT = int(os.environ.get('PORT', '8443'))


def get_current_time():
    now = datetime.now()
    current_time = now.strftime("%d %B, %Y %I:%S %p")
    return current_time


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


def get_simpson_quote():
    contents = requests.get(
        'https://thesimpsonsquoteapi.glitch.me/quotes').json()
    return contents[0]


def get_random_quote():
    contents = requests.get(
        'https://type.fit/api/quotes').json()
    array_len = len(contents)
    random_number = random.randint(1, array_len)
    return contents[random_number]


def get_image_url():
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


def bop(update, context):
    url = get_image_url()
    chat_id = update.effective_chat.id
    user = update.message.from_user
    logger.info("User %s requested for a dog picture.", user.first_name)
    context.bot.send_photo(chat_id=chat_id, photo=url)


def inspire_me(update, context):
    contents = get_random_quote()
    quote = contents['text']
    quote_author = contents['author']
    chat_id = update.effective_chat.id
    user = update.message.from_user
    logger.info("User %s requested for a random quote.", user.first_name)
    text = "<i>" + quote + "</i>" + "\n" + "<b>" + " - " + quote_author + "</b>"
    context.bot.send_message(
        chat_id, text, parse_mode=telegram.ParseMode.HTML)


def inspire_me_simpson(update, context):
    contents = get_simpson_quote()
    img_url = contents['image']
    quote = contents['quote']
    character = contents['character']
    chat_id = update.effective_chat.id
    user = update.message.from_user
    logger.info("User %s requested for a simpson quote.", user.first_name)
    context.bot.send_photo(chat_id=chat_id, photo=img_url)
    text = "<b>" + character + "</b>" + "\n" + "<pre>" + quote + "</pre>"
    context.bot.send_message(
        chat_id, text, parse_mode=telegram.ParseMode.HTML)


def start(update, context):
    chat_id = update.effective_chat.id
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    text = "Hello " + user.first_name + \
        ", welcome you can send any of the following commands send /bop /inspire /simpson to see what I can do."
    context.bot.send_message(
        chat_id, text)


def echo(update, context):
    chat_id = update.effective_chat.id
    user = update.message.from_user
    logger.info("User %s is interacted with bot.", user.first_name)
    text = get_current_time() + "\n\n" + "<b>" + "You said" + "</b>" + \
        "\n" + "<i>" + update.message.text + "</i>"
    context.bot.send_message(
        chat_id, text, parse_mode=telegram.ParseMode.HTML)


def use_webhook(updater):
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=BOT_TOKEN)
    updater.bot.set_webhook(HEROKU_BOT_URL + BOT_TOKEN)
    updater.idle()


def use_polling(updater):
    updater.start_polling()
    updater.idle()


def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop', bop))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('simpson', inspire_me_simpson))
    dp.add_handler(CommandHandler('inspire', inspire_me))
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dp.add_handler(echo_handler)
    use_webhook(updater)
    # use_polling(updater)


if __name__ == '__main__':
    main()
