import telegram
import os
import asyncio
import requests

global bot
global TOKEN

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_SECRET_TOKEN = os.getenv("TELEGRAM_WEBHOOK_SECRET_TOKEN")

bot = telegram.Bot(token=TOKEN)

WEBHOOK_URL = 'https://only-mirror.herokuapp.com/messaging/telegram_message'

# DEV URL
WEBHOOK_URL='https://c70975d31ae5.ngrok.app/messaging/telegram_message'


async def set_webhook_2():
  # setup webhook for telegram
  url = f'https://api.telegram.org/bot{TOKEN}/setWebhook?url='+WEBHOOK_URL\
    +'&secret_token='+TELEGRAM_WEBHOOK_SECRET_TOKEN\
      +'&allowed_updates=["callback_query","message","pre_checkout_query","channel_post","chat_member"]'

  r = requests.post(url)
  # print response data
  print(r.text)
  return r

async def unset_webhook():
  # setup webhook for telegram
  url = f'https://api.telegram.org/bot{TOKEN}/setWebhook?url='

  r = requests.post(url)
  # print response data
  print(r.text)
  return r

async def unset_and_set_webhook():
  await unset_webhook()
  await set_webhook_2()

asyncio.run(unset_and_set_webhook())
