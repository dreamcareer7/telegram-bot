from fastapi import APIRouter, Request, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from urllib.parse import quote

from pydantic import BaseModel
from db.models.creator.creator import Creator
from db.models.creator.creator_audio import CreatorAudio
from db.models.creator.creator_ai_message import CreatorAIMessage
from db.models.creator.creator_message import CreatorMessage

from db.models.user.user import User
from db.models.user.user_ai_message import UserAIMessage
from db.models.user.user_message import UserMessage
from db.models.user.user_payment import UserPayment

from ai.creator.training import respond_to_creator_message
from ai.creator.responding import generate_initial_message_to_user, respond_to_user_message, ask_user_for_payment, thank_user_for_payment, random_image_caption, get_name_from_message
from ai.creator.image_sending import send_contextual_image

from voice.generator import generate_voice

from payment.stripe import update_user_after_charge, charge_customer_automatically
from payment.paypal import get_paypal_payment_link

from pydub import AudioSegment
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

from utils.shorten import get_shorten_url_from_long_url

import os
import requests
from datetime import datetime
from ai.ai_api import transcribe_audio
import json

import random

# Token from bot fateher
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Secret key set to verify webhook
TELEGRAM_WEBHOOK_SECRET_TOKEN = os.getenv("TELEGRAM_WEBHOOK_SECRET_TOKEN")

# Token that bot father gives after connecting stripe
STRIPE_TOKEN = os.getenv("TELEGRAM_STRIPE_TOKEN")
telegram_bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

router = APIRouter(
    prefix="/messaging",
    tags=["messaging"],
    # dependencies=[Depends(validate_access_token)],
    # responses={404: {"description": "Not found"}},
)

@router.post("/handle_sms")
async def handle_sms(From: str = Form(...), Body: str = Form(...)) -> str:
  print("HERE!")

  # see if user first
  user = User.query({'phoneNumber': From})

  creator = None
  ai_response = ""

  if user:
    # user chatting flow
    UserMessage.save(user['userId'], Body, user['currentlyChattingWith'])

    # get creator data
    creator = Creator.query({'displayName': user['currentlyChattingWith']})

    creatorTextingStyle = CreatorMessage.getTextingStyle(creator['userId'])

    # generate AI response to creator message
    # ai_response = resspond_to_user_message(creator['fullName'], creator['creatorType'], creator['userType'], creatorTextingStyle, creator['textingTone'], Body)

    # save AI message to DB
    UserAIMessage.save(user['userId'], ai_response)
  else:
    # training creator messaging flow
    creator = Creator.query({'phoneNumber': From})
    if not creator:
      # user message
      pass
    else:
      creator = creator[0]

    # save creator message to db
    CreatorMessage.save(creator['userId'], Body)

    # generate AI response to creator message
    ai_response = resspond_to_creator_message(creator['creatorType'], creator['userType'], creator['textingTone'], Body)

    # save AI message to DB
    CreatorAIMessage.save(creator['userId'], ai_response)

  # send AI response SMS back to creator
  resp = MessagingResponse()
  resp.message(ai_response)
  return Response(content=str(resp), media_type="application/xml")


def tel_send_chat_action(chat_id, action='typing'):
  """
  An action such as typing, recording, uploading, etc.
  """
  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendChatAction'
  payload = {
    'chat_id': chat_id,
    'action': action
  }

  r = requests.post(url,json=payload)

  return r


def tel_set_chat_title(chat_id, title):
  """
  Change the title of a chat. Titles can't be changed for private chats. The bot must be an administrator in the chat for this to work and must have the appropriate admin rights. Returns True on success.
  """
  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setChatTitle'
  payload = {
    'chat_id': chat_id,
    'title': title
  }

  r = requests.post(url,json=payload)

  return r

def tel_send_message(chat_id, text, reply_to_message_id='', reply_markup=None):
  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
  
  payload = {
    'chat_id': chat_id,
    'text': text,
    'reply_to_message_id': reply_to_message_id,
    'allow_sending_without_reply': True,
  }

  # if reply_markup:
  #   payload['reply_markup'] = reply_markup

  r = requests.post(url,json=payload)

  return r
 
def tel_send_image(chat_id, photo_url, message=''):
  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto'
  
  payload = {
    'chat_id': chat_id,
    'photo': photo_url,
    'caption': message,
  }

  r = requests.post(url, json=payload)
  # print response as text
  print(r.text)
  
  # if response is not ok, print error
  if not r.ok:
    return tel_send_message(chat_id, message)
    
  return r

def tel_set_chat_photo(chat_id, photo_url):
  # download photo locally from photo_url
  response = requests.get(photo_url)

  with open(f"temp/{chat_id}-chat-photo.jpg", "wb") as f:
      f.write(response.content)

  url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setChatPhoto'
  payload = {
    'chat_id': chat_id,
  }

  files={
    'photo': response.content
  }

  r = requests.post(url, 
    data=payload,
    files=files).json()
  
  print(r)

  return r

def tel_send_voice(chat_id, audio, reply_to_message_id=''):
  # get current datetime and convert to string
  
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

  payload = {
    'chat_id': chat_id,
    'title': dt_string,
    'parse_mode': 'HTML',
    'reply_to_message_id': reply_to_message_id,
    'allow_sending_without_reply': True,
  }
  files = {
    'voice': audio,
  }
  resp = requests.post(
      f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVoice",
      data=payload,
      files=files).json()
  return resp


def handle_purchase_request(chat_id, telegram_username, text):
  print('ADDING HERE!')
  markup = InlineKeyboardMarkup(row_width=2)
  markup.add(InlineKeyboardButton("$10", callback_data="10"))
  markup.add(InlineKeyboardButton("$25", callback_data="25"))
  markup.add(InlineKeyboardButton("$50", callback_data="50"))
  markup.add(InlineKeyboardButton("$100", callback_data="100"))
  markup.add(InlineKeyboardButton("$250", callback_data="250"))
  markup.add(InlineKeyboardButton("$500", callback_data="500"))
  markup.add(InlineKeyboardButton("Paypal", callback_data="paypal"))

  telegram_bot.send_message(chat_id, text, reply_markup=markup)
  
  return "success"

def handle_purchase_request_audio(chat_id, audio):
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

  markup = InlineKeyboardMarkup(row_width=2)
  markup.add(InlineKeyboardButton("$5", callback_data="5"), InlineKeyboardButton("$10", callback_data="10"))
  markup.add(InlineKeyboardButton("$25", callback_data="25"), InlineKeyboardButton("$50", callback_data="50"))
  markup.add(InlineKeyboardButton("$100", callback_data="100"), InlineKeyboardButton("$250", callback_data="250"))
  markup.add(InlineKeyboardButton("$500", callback_data="500"))
  
  markup = markup.to_json()

  payload = {
    'chat_id': chat_id,
    'title': dt_string,
    'parse_mode': 'HTML',
    'allow_sending_without_reply': True,
    'reply_markup': markup,
  }
  files = {
    'voice': audio,
  }
  resp = requests.post(
      f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVoice",
      data=payload,
      files=files).json()
  return resp

def send_thank_you_for_payment(chat_id, amount, currency, first_name='?', last_name=''):
  user = User.query({'chatId': chat_id})

  if user:
    # get creator data based on who the user's currently chatting with field is set
    creator = Creator.query({'displayName': user['currentlyChattingWith']})

    invoice_id = UserPayment.save(user['currentlyChattingWith'], chat_id, amount, currency, first_name + ' ' + last_name)

    # if creator not found
    if not creator:
      return tel_send_message(chat_id, "Creator not found. Please enter /start <creator_display_name>", '')

    # TODO: shift up to handle whisper transcription
    tel_send_chat_action(chat_id, 'record_voice')

    creatorTextingStyle = CreatorMessage.getTextingStyle(creator['userId'])

    last_context = User.getUserLastMessages(user['userId'])

    # generate AI response to creator message
    ai_response = thank_user_for_payment(creator['fullName'], creator['creatorType'], creator['userType'], creatorTextingStyle, creator['textingTone'], last_context)
    audio = generate_voice(creator['displayName'], ai_response, creator['email'])

    return tel_send_voice(chat_id, audio)

def send_invoice(chat_id, telegram_username='', callback_data='', first_name='?', last_name=''):
  prices = [
    LabeledPrice(label=f'${callback_data}', amount=int(callback_data) * 100)
  ]

  user = User.query({'chatId': chat_id})
  creator = Creator.query({'displayName': user['currentlyChattingWith']})
  
  automatic_charge_res = charge_customer_automatically(chat_id, callback_data)

  if automatic_charge_res:
    return send_thank_you_for_payment(chat_id, callback_data, 'USD', first_name, last_name)

  description = ''

  # set invoice id to be chat_id + timestamp
  invoice_id = str(chat_id) + '--' + str(datetime.now())

  description = f'{creator["creatorType"]} obligations {creator["fullName"]}'

  res = telegram_bot.send_invoice(
    chat_id=chat_id,
    title="Beemo",
    description=description,
    invoice_payload=invoice_id,
    provider_token=STRIPE_TOKEN,
    currency="USD",
    prices=prices,
    need_email=True,
    send_email_to_provider=True
  )

  return "success"


def handle_command(chat_id, telegram_username, message, full_data):
  print('handling command')

  message_id = full_data['message']['message_id']

  # if start, add chat_id to the user with user_id provided
  if '/start' in message:    
    # split start and get id passed after
    split_message = message.split(' ')
    if len(split_message) > 1:
      creator_display_name = split_message[1]
      # make lowercase
      creator_display_name = creator_display_name.lower()

      first_name = ''
      last_name = ''

      try:
        first_name = full_data['message']['from']['first_name']
        last_name = full_data['message']['from']['last_name']
      except Exception as e:
        print('no first or last name')

      user = User.create_user_if_does_not_exist(telegram_username, chat_id, first_name, last_name, creator_display_name)

      # get current creator they're chatting with
      creator = Creator.query({'displayName': creator_display_name})

      # if creator not found
      if not creator:
        return tel_send_message(chat_id, "Creator not found. Please enter /start creator_handle", message_id)
    
      # get creator's texting style
      creatorTextingStyle = CreatorMessage.getTextingStyle(creator['userId'])

      # Send typing action
      tel_send_chat_action(chat_id)

      # Set Chat title
      # tel_set_chat_photo(chat_id, creator['profilePicture'])
      tel_set_chat_title(chat_id, 'Chatting with ' + creator['displayName'])

      # TODO: set bot name and chat title not working?

      # TODO: update to use profile picture rather than 1st image
      creator_profile_photo = None

      if 'profilePhoto' in creator:
        creator_profile_photo = creator['profilePhoto']

      name_to_use = None
      if first_name:
        name_to_use = first_name
      elif last_name:
        name_to_use = last_name

      languages_message = ''
      if 'otherLanguages' in creator and 'spanish' in creator['otherLanguages']:
        languages_message += '  hablo en español también si prefieres'
      
      if 'telegramName' in user and creator_profile_photo:
        # if name_to_use:
        #   return tel_send_image(chat_id, creator_profile_photo, f'heyy {name_to_use} :) it’s nice to meet you')
        # else:
        return tel_send_image(chat_id, creator_profile_photo, f'heyy {user["telegramName"]} 😊  - it\'s nice to talk to you' + languages_message)
      elif creator_profile_photo:
        return tel_send_image(chat_id, creator_profile_photo, f'heyy nice to meet you 😊 — what’s your name?' + languages_message)
      else:
        return tel_send_message(chat_id, f'heyy nice to meet you 😊 — what’s your name?', message_id)

      # generate initial message to send to user
      # ai_response = generate_initial_message_to_user(creator['displayName'], creator['creatorType'], creator['userType'], creatorTextingStyle, creator['textingTone'])
      
      # # save message to DB
      # UserAIMessage.save(chat_id, ai_response)

      # audio = generate_voice(creator['displayName'], ai_response)

      # return tel_send_voice(chat_id, audio, message_id)
    else:
      return tel_send_message(chat_id, "Creator not found. Please enter /start <creator_display_name>", message_id)
  elif '/purchase' in message:
    handle_purchase_request(chat_id, telegram_username, message)
  elif '/balance' in message:
    user = User.query({'chatId': chat_id})
    balance = user['balance']
    # convert cents to dollars
    balance_dollars = "${:.2f}".format(balance / 100)
    return tel_send_message(chat_id, f'Your balance is {balance_dollars}', message_id)
  elif '/help' in message:
    return tel_send_message(chat_id, 'Need help with something? Send us a message @BeemoHelp', message_id)

def get_message_text_from_update(incoming_data):
  # if voice file
  if 'voice' in incoming_data['message']:
    voice_file = incoming_data['message']['voice']['file_id']
    update_id = incoming_data['update_id']
    voice_file = telegram_bot.get_file(voice_file)

    downloaded_file = telegram_bot.download_file(voice_file.file_path)

    with open(f'temp/{update_id}', 'wb') as new_file:
      new_file.write(downloaded_file)

      AudioSegment.from_file(f'temp/{update_id}').export(f'temp/{update_id}-converted.mp3', format="mp3")
      
      # transcribe
      transcribed_text = transcribe_audio(f'temp/{update_id}-converted.mp3')

      # delete temp files
      os.remove(f'temp/{update_id}')
      os.remove(f'temp/{update_id}-converted.mp3')

      return transcribed_text

  else:
    message = incoming_data["message"]["text"]
    return message

# handles callback from inline buttons
def handle_callback(incoming_data):
  chat_id = incoming_data['callback_query']['message']['chat']['id']
  callback_data = incoming_data['callback_query']['data']

  if callback_data == 'paypal':
    payment_link = get_paypal_payment_link()
    return tel_send_message(chat_id, f'Please send payment to {payment_link}', '')

  first_name = ''
  last_name = ''
  if 'first_name' in incoming_data['callback_query']['message']['from']:
    first_name = incoming_data['callback_query']['message']['from']['first_name']
  if 'last_name' in incoming_data['callback_query']['message']['from']:
    last_name = incoming_data['callback_query']['message']['from']['last_name']

  send_invoice(chat_id, '', callback_data, first_name, last_name)

  return "success"

def verify_secure_webhook(headers):
  # verify webhook
  if 'x-telegram-bot-api-secret-token' in headers:
    if headers['x-telegram-bot-api-secret-token'] == os.getenv("TELEGRAM_WEBHOOK_SECRET_TOKEN"):
      return True
    else:
      return False
  else:
    return False
  
def answer_pre_checkout_query(incoming_data):
  id = incoming_data['pre_checkout_query']['id']
  telegram_bot.answer_pre_checkout_query(id, True)
  return "success"

def handle_successful_payment(chat_id, incoming_data):
  print('INCOMING HERE')
  print(incoming_data)

  amount = incoming_data['message']['successful_payment']['total_amount']
  currency = incoming_data['message']['successful_payment']['currency']
  charge_id = incoming_data['message']['successful_payment']['provider_payment_charge_id']
  email = incoming_data['message']['successful_payment']['order_info']['email']
  
  first_name = ''
  last_name = ''
  if 'first_name' in incoming_data['message']['from']:
    first_name = incoming_data['message']['from']['first_name']
  if 'last_name' in incoming_data['message']['from']:
    last_name = incoming_data['message']['from']['last_name']

  # update user in DB with Stripe details and update Stripe with user details
  update_user_after_charge(chat_id, charge_id, email)

  # send thank you message for payment
  send_thank_you_for_payment(chat_id, amount, currency, first_name, last_name)

  return "success"

def prompt_for_payment(user, chat_id, message):
  creator = None
  ai_response = ""

  if user:
    UserMessage.save(chat_id, message, user['currentlyChattingWith'])

    # get creator data based on who the user's currently chatting with field is set
    creator = Creator.query({'displayName': user['currentlyChattingWith']})

    # if creator not found
    if not creator:
      return tel_send_message(chat_id, "Creator not found. Please enter /start <creator_display_name>", message_id)

    # TODO: shift up to handle whisper transcription
    tel_send_chat_action(chat_id, 'record_voice')

    creatorTextingStyle = CreatorMessage.getTextingStyle(creator['userId'])

    last_context = User.getUserLastMessages(user['userId'])

    # generate AI response to creator message
    ai_response = ask_user_for_payment(creator['fullName'], creator['creatorType'], creator['userType'], creatorTextingStyle, creator['textingTone'], message, last_context)
    audio = generate_voice(creator['displayName'], ai_response, creator['email'])

    return handle_purchase_request_audio(chat_id, audio)

def handle_user_message(chat_id, message, message_id, name=""):
  # get user using the saved chat_id that was saved when they called /start user_id on that chat
  user = User.query({'chatId': chat_id})

  if not User.check_if_has_balance(user):
    return prompt_for_payment(user, chat_id, message)

  creator = None
  message_back = ""

  # keep track of how many messages sent since last image
  if 'messagesSentSinceImage' not in user:
    messagesSentSinceImage = 0
  else:
    messagesSentSinceImage = user['messagesSentSinceImage']

  # wait at least this many messages before sending image again
  min_messages_before_sending_image_again = 5

  language = 'english'

  if user:
    # make sure user found
    UserMessage.save(chat_id, message, user['currentlyChattingWith'])

    # get creator data based on who the user's currently chatting with field is set
    creator = Creator.query({'displayName': user['currentlyChattingWith']})

    # if creator not found
    if not creator:
      return tel_send_message(chat_id, "Creator not found. Please enter /start <creator_display_name>", message_id)

    # TODO: shift up to handle whisper transcription
    tel_send_chat_action(chat_id, 'record_voice')

    creatorTextingStyle = CreatorMessage.getTextingStyleByDisplayName(creator['displayName'])

    last_context = User.getUserLastMessages(user['userId'])

    # this message is an onboarding message containing their name
    if 'telegramName' not in user:
      extracted_name = get_name_from_message(message)
      User.update(user['userId'], {'telegramName': extracted_name})
      message_back = f'heyy {extracted_name}, i can’t wait to get close with you! feel free to send voice memos too so i can hear what you sound like!  '
    else:
      send_image_data = send_contextual_image(creator, user, [], creator['fullName'], creator['creatorType'], creator['userType'], creatorTextingStyle, creator['textingTone'], message, last_context, user.get('telegramName', ''))
      
      if send_image_data['send_image'] and messagesSentSinceImage > min_messages_before_sending_image_again:
        image_url = send_image_data['image']
        
        if 'sent_images' in user and image_url not in user['sent_images']:
          # send image and add to sent list
          user['sent_images'].append(image_url)
          User.update(user['userId'], {'sent_images': user['sent_images'], 'messagesSentSinceImage': 0})
          return tel_send_image(chat_id, image_url, send_image_data['caption'])
        elif 'sent_images' not in user:
          # if first time getting an image
          user['sent_images'] = [image_url]
          User.update(user['userId'], {'sent_images': user['sent_images']})
          return tel_send_image(chat_id, image_url, random_image_caption())
    
      # generate AI response to creator message
      full_response = respond_to_user_message(creator['fullName'], creator['creatorType'], creator['userType'], creatorTextingStyle, creator['textingTone'], message, last_context, user['telegramName'])
      message_back = full_response['message_back']
      language = full_response['language']
      topics = full_response['topics']

      # save topics
      UserAIMessage.extract_keywords_and_store_for_creator(topics, creator['displayName'])

      # Charge user for response
      User.charge_user_for_response(chat_id, message_back)

    # save AI message to DB
    UserAIMessage.save(user['userId'], message_back)

    # Generate audio using their creator's display name
    audio = generate_voice(creator['displayName'], message_back, creator['email'], language)

    # send voice back
    tel_send_voice(chat_id, audio, message_id)

    # user update
    User.update(user['userId'], {'messagesSentSinceImage': messagesSentSinceImage + 1})

# https://telegram.me/MeebleBot?start=taayjus
@router.post("/telegram_message")
async def handle_sms(request: Request) -> str:
  try:
    incoming_data = await request.json()
    print(incoming_data)

    if not verify_secure_webhook(request.headers):
      return "error"

    # Handle pre checkout query
    if 'pre_checkout_query' in incoming_data:
      return answer_pre_checkout_query(incoming_data)

    # Handle callback
    if 'callback_query' in incoming_data:
      return handle_callback(incoming_data)

    chat_id = incoming_data["message"]["chat"]["id"]

    # Handle successful payment
    if 'message' in incoming_data and 'successful_payment' in incoming_data['message']:
      return handle_successful_payment(chat_id, incoming_data)

    message = get_message_text_from_update(incoming_data)
    message_id = incoming_data["message"]["message_id"]
    telegram_username = ''

    first_name = ''
    last_name = ''

    try:
      first_name = incoming_data['message']['from']['first_name']
      last_name = incoming_data['message']['from']['last_name']
    except Exception as e:
      pass

    name = first_name if first_name else last_name

    # get fields that may not exist
    try:
      telegram_username = incoming_data["message"]["chat"]["username"]
    except Exception as e:
      print('no username')

    if (message.startswith('/')):
      handle_command(chat_id, telegram_username, message, incoming_data)
      return "success"

    
    # respond to user message
    handle_user_message(chat_id, message, message_id, name)

    return "success"
  except Exception as e:
    print(e)
    return "error"


# on server cleanup