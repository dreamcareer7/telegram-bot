import telebot
import os

from ai.ai_api import transcribe_audio
from pydub import AudioSegment

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Token that bot father gives after connecting stripe
STRIPE_TOKEN = os.getenv("TELEGRAM_STRIPE_TOKEN")
telegram_bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

voice_file = 'AwACAgEAAxkBAAPnZHFACJVVRFH395kuxwABETSwG6iLAAIHAwAC7u6JR82FNOhpHHroLwQ'
update_id = '12312321'
voice_file = telegram_bot.get_file(voice_file)
downloaded_file = telegram_bot.download_file(voice_file.file_path)

with open(f'temp/{update_id}', 'wb') as new_file:
  new_file.write(downloaded_file)

  AudioSegment.from_file(f'temp/{update_id}').export(f'temp/{update_id}-converted.mp3', format="mp3")

  print('saved file to temp')

  print('begin transcribing')
  
  # transcribe
  transcribe_audio(f'temp/{update_id}-converted.mp3')