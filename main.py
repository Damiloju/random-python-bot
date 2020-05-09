import os
from telegram.ext import Updater, CommandHandler
import logging
import re
import requests
from dotenv import load_dotenv
from telegram.ext import MessageHandler, Filters


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(filename="main.log", filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


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


def start(update, context):
    chat_id = update.effective_chat.id
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    text = "I can send you random cute dog images!, just send /bop command."
    context.bot.send_message(
        chat_id, text)


def echo(update, context):
    chat_id = update.effective_chat.id
    user = update.message.from_user
    logger.info("User %s is interacted with bot.", user.first_name)
    text = update.message.text
    context.bot.send_message(
        chat_id, text)


def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop', bop))
    dp.add_handler(CommandHandler('start', start))
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dp.add_handler(echo_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
