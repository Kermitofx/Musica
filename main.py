from telegram.ext import Updater, MessageHandler, Filters, Handler
from telegram import Bot
import json
import logging
import os


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

with open("config.json", "r") as read_file:
    config = json.load(read_file)


def update_config():
    with open("config.json", "w") as write_file:
        json.dump(config, write_file)


updater = Updater(config["TOKEN"])
dispatcher = updater.dispatcher


def get_single_song_handler(bot, update):
    if config["AUTH"]["ENABLE"]:
        authenticate(bot, update)
    get_single_song(bot, update)


def get_single_song(bot, update):
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    username = update.message.chat.username
    logging.log(logging.INFO, f'start para consultar a mensagem {message_id} in chat:{chat_id} from {username}')

    url = "'" + update.effective_message.text + "'"
    os.system('mkdir -p .temp')
    logging.log(logging.INFO, f'start baixando')
    bot.send_message(chat_id=chat_id, text="baixando...")
    os.system(f'spotdl --song {url} --folder ./.temp --file-format track{message_id}{chat_id}')

    logging.log(logging.INFO, 'enviando para o cliente')
    bot.send_message(chat_id=chat_id, text="enviando para você ...")
    bot.send_audio(chat_id=chat_id, audio=open(f'./.temp/track{message_id}{chat_id}.mp3', 'rb'), timeout=1000)

    logging.log(logging.INFO, 'sent')
    os.system(f'rm ./.temp/track{message_id}{chat_id}.mp3')


def authenticate(bot, update):
    username = update.message.chat.username
    chat_id = update.effective_message.chat_id
    if update.effective_message.text == config["AUTH"]["PASSWORD"]:
        logging.log(logging.INFO, f'novo login para o usuário {username}, {chat_id}')
        config["AUTH"]["USERS"].append(chat_id)
        update_config()
        bot.send_message(chat_id=chat_id, text="Você fez login com sucesso. Aproveitar🍻")
        raise Exception("Signed In")
    elif chat_id not in config["AUTH"]["USERS"]:
        logging.log(logging.INFO, f'tentativa não autenticada')
        bot.send_message(chat_id=chat_id, text="⚠️Este bot é pessoal e você não está conectado. Digite o "
                                               "senha para entrar. Se você não souber, entre em contato com o proprietário do bot. ")
        raise Exception("Não conectado")


handler = MessageHandler(Filters.text, get_single_song_handler)
dispatcher.add_handler(handler=handler)

POLLING_INTERVAL = 0.8
updater.start_polling(poll_interval=POLLING_INTERVAL)
updater.idle()
