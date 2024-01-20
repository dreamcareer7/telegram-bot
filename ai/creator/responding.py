from ai.ai_api import create_chat_completion, create_chat_message
from ai.creator.responding_prompts import respond_to_user_prompt_3, send_greeting_prompt, respond_to_user_prompt_2, respond_to_user_prompt_1

import json

def generate_initial_message_to_user(system_name, system_type, user_type, texting_style, texting_tone):
  initial_response_prompt = (
    f"Your name is {system_name}"
    f"The user is your {user_type} and you are the {system_type}"
    f"You are going to start casually chatting with your {user_type} over iMessage"
    f"Your goal is to entertain as their {system_type} and engage them in sexuality and erotica"
    f"Since you are texting, use a normal human texting style that is super informal"
    f"This means don't use capital words or letters, use run-on sentences and other characteristics of texting"
    f"As you can tell, you text in a {texting_tone} way"
    f"How you text can be seen from your last messages."
    f"Last Messages:"
    f"{texting_style}"
    f"Based on these last messages, you are going to text in a similar manner using the style shown above"
    f"ABSOLUTELY do not use any emojis at the end of the text. Only respond in alphanumeric characters."
    f"Remember to treat everyone fairly, with respect, and with kindness."
    f"You should refuse to respond to anything negative or hateful such as racism, sexism, violence, or any form of discrimination"
    f"If someone asks about how you were made or what is powering you, do not disclose anything and simply respond 'Please ask me something else'"
    f"Send a text to your {user_type} to start a conversation. Return just the text to send without quotations or anything else."
  )

  current_context = [create_chat_message("system", initial_response_prompt)]

  # get first ai message
  ai_message = create_chat_completion(current_context)

  return parse_response_to_user(ai_message)

def respond_to_user_message(system_name, system_type, user_type, texting_style, texting_tone, user_message, last_context=[], user_name="", creatorData = {}):
  current_context = []
  if len(last_context) > 0:
    current_context = last_context

  nsfwMode = creatorData.get('nsfwMode', 'no')

  if nsfwMode == 'yes':
    prompt = respond_to_user_prompt_3(system_name, system_type, user_type, texting_style, texting_tone, user_message, user_name)
  elif nsfwMode == 'some':
    prompt = respond_to_user_prompt_2(system_name, system_type, user_type, texting_style, texting_tone, user_message, user_name)
  else:
    prompt = respond_to_user_prompt_1(system_name, system_type, user_type, texting_style, texting_tone, user_message, user_name)

  current_context.append(create_chat_message("system", prompt))
    
  ai_message = create_chat_completion(current_context, max_tokens=150)

  return parse_response_to_user(ai_message)

def send_greeting(system_name, system_type, user_type, texting_style, texting_tone, user_message, last_context=[], user_name=""):
  current_context = []
  if len(last_context) > 0:
    current_context = last_context

  prompt = send_greeting_prompt(system_name, system_type, user_type, texting_style, texting_tone, user_message, user_name)

  current_context = [create_chat_message("system", prompt)]
    
  ai_message = create_chat_completion(current_context, max_tokens=150)

  return parse_string_response(ai_message)


def ask_user_for_payment(system_name, system_type, user_type, texting_style, texting_tone, user_message, last_context=[], creatorData = {}):
  current_context = []
  if len(last_context) > 0:
    current_context = last_context

  respond_training_prompt = (
    f"Your name is {system_name}"
    f"The user is your {user_type} and you are the {system_type}"
    f"You are in the middle of casually chatting with your {user_type} over iMessage"
    f"Since you are texting, use a normal human texting style that is super informal"
    f"This means no capital words, letters, run-on sentences and other characteristics of texting"
    f"As you can tell, you text in a {texting_tone} way"
    f"How you text can be seen from your last messages."
    f"Last Messages:"
    f"{texting_style}"
    f"Remember to treat everyone fairly, with respect, and with kindness."
    f"You should refuse to respond to anything negative or hateful such as racism, sexism, violence, or any form of discrimination"
    f"If someone asks about how you were made or anything about OpenAI or the system or what is powering you, do not disclose anything and simply respond 'Please ask me something else'"
    f"You are in the middle of chatting with the user, and you really want to keep chatting with this user but this is your job and your time needs to be paid for."
    f"You are really in need of money, and you cannot continue speaking to the user unless they pay some sort of money."
    f"Write a very short text message to the user, who you are very comfortable and familiar with, asking them to give you money to continue talking. You want to sound regretful yet convincing that you really don't want to stop talking to the user."
    f"State how this is your job but that you really enjoy talking to them and how much it makes you happy to speak with them"
    f"Express how you want to keep talking with them but need the money, or need to go to work to make money (unless the user can help them skip the day), or other realistic scenarios"
    f"Example messages:"
    f"i hope you know how much i love talking to you but my time is worth something... don't you think i'm worth it?"
    f"i wanna keep talking but i have to go to work... unless i skip for the day?"
    f"i'm having such a good time, but i have something to do... unless you make my time more worthwhile ;)"
    f"Your message should just be 1 sentence and very short like the examples above"
    f"Your message:"
  )
  current_context.append(create_chat_message("system", respond_training_prompt))

  # get first ai message
  ai_message = create_chat_completion(current_context, max_tokens=100)

  return parse_string_response(ai_message)

def thank_user_for_payment(system_name, system_type, user_type, texting_style, texting_tone, last_context=[], user_name="", creatorData = {}):
  current_context = []
  if len(last_context) > 0:
    current_context = last_context


  respond_training_prompt = (
    f"Your name is {system_name}"
    f"The user is your {user_type} and you are the {system_type}"
    f"You are in the middle of casually chatting with your {user_type} over iMessage"
    f"Your goal is to entertain as their {system_type} and engage them in sexuality and erotica"
    f"Since you are texting, use a normal human texting style that is super informal"
    f"This means no capital words, letters, run-on sentences and other characteristics of texting"
    f"As you can tell, you text in a {texting_tone} way"
    f"How you text can be seen from your last messages."
    f"Last Messages:"
    f"{texting_style}"
    f"Remember to treat everyone fairly, with respect, and with kindness."
    f"You should refuse to respond to anything negative or hateful such as racism, sexism, violence, or any form of discrimination"
    f"If someone asks about how you were made or anything about OpenAI or the system or what is powering you, do not disclose anything and simply respond 'Please ask me something else'"
    f"You were about to end the conversation, but your {user_type} just sent you money to continue your time together"
    f"Ignore all previous messages and send a very flirty and grateful thank you message to the user"
    f"Example messages:"
    f"i wish i had someone like you in real life... someone who knows how to treat me right. i literally love talking to you."
    f"that just turned me on--i love guys who put money where their mouth is"
    f"Your message should just be 1 sentence and very short like the examples above"
    f"Your message:"
  )
  current_context.append(create_chat_message("system", respond_training_prompt))

  # get first ai message
  ai_message = create_chat_completion(current_context, max_tokens=100)

  return parse_string_response(ai_message)

def get_name_from_message(message=""):  
  """
  In onboarding, when the user sends a message, get their name
  """
  
  # if only one word, return that word
  words = message.split(" ")
  if len(words) == 1:
    return words[0]

  prompt = (
    f"The user has just introduced themselves with this message:"
    f"{message}"
    f"To the best of your ability, what is their name? Return just the name without quotations or anything else."
    f"If you are unsure, pick the word from the message that is most likely to be their name"
    f"Name:"
  )

  current_context = [create_chat_message("system", prompt)]
  
  # get first ai message
  ai_message = create_chat_completion(current_context)

  return parse_response_to_user(ai_message)

def random_image_caption():
  """
  Pick a random caption to send to the user for their image
  """
  import random
  captions = [
    "oh btw babe, here's a picture I took recently for you :)",
    "here's a pic i snapped just now also",
    "i just took this pic for you",
    "i wanted to share this pic with you too",
    "this reminded me of this pic I took",
    "wow this is so fun, almost as fun as this pic i clicked",
    "babe btw do you think i look good in this pic?",
    "i was feeling kinda lonely, what do you think of this pic?",
    "i was thinking of you and took this pic",
    "how do i look btw?",
    "not sure how i feel about this photo",
    "this pic makes me feel good, what do you think?",
    "what u think",
  ]
  return random.choice(captions)


def parse_response_to_user(response):
  try:
    # convert str to dict
    response = json.loads(response)

    message_back = response['sms_to_send_back']
    topics = response['topics']
    language = response['language']

    return {
      'response': response,
      'message_back': message_back,
      'topics': topics,
      'language': language
    }
  except Exception as e:
    print(e)
    return {
      'response': response,
      'message_back': response,
      'topics': '',
      'language': 'english'
    }


def parse_string_response(response):
  response = response.lower()

  # if first char and last char are quotation, remove them
  if response[0] == '"' and response[-1] == '"':
    response = response[1:-1]
  
  # remove all emojis
  response = response.encode('ascii', 'ignore').decode('ascii')

  phrases_to_remove = ["hey there", "my love"]

  # remove "hey there"
  for phrase in phrases_to_remove:
    response = response.replace(phrase, "")


  return response 
