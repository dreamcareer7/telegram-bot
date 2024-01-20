from ai.ai_api import create_chat_completion, create_chat_message
from ai.creator.responding_prompts import pick_image_to_send_to_user_prompt_3

from db.models.creator.creator import Creator
from db.models.creator.daily_beemo import DailyBeemo

import json

def send_contextual_image(creatorData, userData, topics, system_name, system_type, user_type, texting_style, texting_tone, user_message, last_context=[], user_name=""):  
  current_context = []
  if len(last_context) > 0:
    current_context = last_context
  
  qualityQuery = ''
  if 'totalPaid' in userData:
    totalPaid = userData['totalPaid']
  else:
    totalPaid = 0

  # depending on total paid, the images eligible for
  if totalPaid < 10:
    qualityQuery = ['free']
  elif totalPaid < 100:
    qualityQuery = ['free', '$']
  elif totalPaid < 1000:
    qualityQuery = ['free', '$', '$$']
  else:
    qualityQuery = ['free', '$', '$$', '$$$']


  query = {
    'creatorUserId': creatorData['userId'],
    'quality': {'$in': qualityQuery}
  }

  # TODO: make this just last 10 days
  dailyBeemos = DailyBeemo.query({
    'creatorUserId': creatorData['userId'],
    'quality': {'$in': qualityQuery}
  })


  dailyBeemosStr = ""

  i = 0
  for dailyBeemo in dailyBeemos:
    dailyBeemosStr = dailyBeemosStr + f"Image {i}: " + dailyBeemo['description'] + "\n"
    i += 1

  prompt = pick_image_to_send_to_user_prompt_3(system_name, system_type, user_type, texting_style, texting_tone, user_message, user_name, '', dailyBeemosStr)

  current_context.append(create_chat_message("system", prompt))

  # get first ai message
  ai_message = create_chat_completion(current_context)

  print(ai_message)

  return parse_image_response(ai_message, dailyBeemos)

def parse_image_response(ai_message, dailyBeemos):
  """
  Parses the response from the AI to send to the user
  """
  try:
    response = json.loads(ai_message)


    probability_str = response['probability']

    # get probability
    if '%' in probability_str:
      probability_str = probability_str.replace('%', '')
      
    probability = int(probability_str)

    # get photo
    photo_index = int(response['photo_number'])
    photo = dailyBeemos[photo_index]['imageUrl']

    return {
      'send_image': probability >= 80,
      "caption": response['caption'],
      "probability": response['probability'],
      'image': photo
    }
  except Exception as e:
    # print e stacktrace
    print(e)
    print('Error parsing image response')
    return {
      'send_image': False
    }
