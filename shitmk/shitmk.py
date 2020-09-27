import json
import telegram
from telegram.ext import Updater, CommandHandler
import websocket
import yaml

# load configuration
with open(r'config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

deconz_rest = config['deconz_rest'] + config['deconz_api_key']

# start telegram bot
updater = Updater(token=config['telegram_bot_token'], use_context=True)
dp = updater.dispatcher
bot = telegram.Bot(token=config['telegram_bot_token'])


# /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=config['message_start'])


# message handlers
dp.add_handler(CommandHandler('start', start))

# start telegram bot
updater.start_polling()

occupied = False


# websocket client
class WsClient(object):
    def __init__(self):
        self.ws = websocket.WebSocketApp(config['deconz_websocket'],
                                         on_message=on_message,
                                         on_open=self.on_open)

    def run_forever(self):
        self.ws.run_forever()

    def on_open(self):
        bot.sendMessage(chat_id=config['telegram_chat_id'], text=config['message_init'])


def on_message(message):
    global occupied
    event = json.loads(message)
    if event['id'] == config['sensor_id']:
        if event['state']['presence'] and not occupied:
            occupied = True
            bot.sendMessage(chat_id=config['telegram_chat_id'], text=config['message_occupied'])
        if not event['state']['presence'] and occupied:
            occupied = False
            bot.sendMessage(chat_id=config['telegram_chat_id'], text=config['message_vacant'])


if __name__ == '__main__':
    ws = WsClient()
    ws.run_forever()
