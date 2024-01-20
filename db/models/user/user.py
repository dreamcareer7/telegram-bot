from db.mongodb import db
from bson import ObjectId
from utils.json import parse_json
import json 

from datetime import datetime

from db.models.user.user_ai_message import UserAIMessage
from db.models.user.user_message import UserMessage
from ai.ai_api import create_chat_message
import os
import stripe

stripe.api_key = os.getenv("STRIPE_API_KEY")

collection = db['users']

class User:
  def __init__(self):
    pass
  
  @staticmethod
  def save(email, userId, fullName, phoneNumber, currentlyChattingWith):
    user = {
      'email': email,
      'userId': userId,
      'fullName': fullName,
      'phoneNumber': phoneNumber,
      'currentlyChattingWith': currentlyChattingWith,
      'joinDate': datetime.utcnow(),
      'balance': 0,
      'stripeCustomerIds': [],
    }
    collection.insert_one(user)
  
  @staticmethod
  def create_user_if_does_not_exist(telegramUsername, chat_id, first_name, last_name, creator_chatting_with_display_name):
    """
    Creates a user if the user does not exist
    """
    user = User.query({'telegramUsername': telegramUsername})
    if not user:
      stripeCustomerId = stripe.Customer.create(
        metadata={"telegramUsername": telegramUsername, "telegram_chat_id": chat_id, "creator_chatting_with_display_name": creator_chatting_with_display_name}
      )['id']

      user = {
        'email': '',
        'userId': chat_id,
        'fullName': first_name + ' ' + last_name,
        'phoneNumber': '',
        'currentlyChattingWith': creator_chatting_with_display_name,
        'telegramUsername': telegramUsername,
        'chatId': chat_id,
        'joinDate': datetime.utcnow(),
        'balance': 100,
        'stripeCustomerIds': [stripeCustomerId],
      }
      collection.insert_one(user)
    else:
      # update chatId
      new_update = {
        'chatId': chat_id,
        'currentlyChattingWith': creator_chatting_with_display_name,
      }
      User.update(user['userId'], new_update)
    return user

  @staticmethod
  def update(userId, update_data):
    result = collection.update_one({'userId': userId}, {'$set': update_data})

  @staticmethod
  def updateWithCustomQuery(custom_query, update_data):
    result = collection.update_one(custom_query, {'$set': update_data})

    # print update count
    print('Update count: ', result.modified_count)

  def parse_json(self, data):
    return json.loads(json_util.dumps(data))

  # Static method query
  @staticmethod
  def query(query):
    try:
      results = collection.find(query)
      # convert each item in results to a dictionary
      results = map(lambda result: parse_json(result), results)

      results = list(results)

      if not results or len(results) == 0:
        return None
      else:
        return list(results)[0]

    except Exception as e:
      print('Error in query')
      print(e)
      return []
  
  @staticmethod
  def convertUserXPToLevelDescriptor(userXP: int):
    if userXP < 10:
      return 'Novice'
    elif userXP < 20:
      return 'Beginner'
    elif userXP < 30:
      return 'Intermediate'
    elif userXP < 40:
      return 'Advanced'
    elif userXP < 50:
      return 'Expert'
    else:
      return 'Master'

  @staticmethod
  def getUserLastMessages(userId: str):
    """
    Get's the last context as OpenAI ChatGPT formatted context (with role and message)
    Get's only the last context until the maxContextMessagesLength is exceeded
    """
    maxContextMessagesLength = 3500 # 3500 characters

    # Get all CreatorAIMessage and CreatorMessage before this
    userMessages = UserMessage.query({'userId': userId})
    userAIMessages = UserAIMessage.query({'userId': userId})

    # Add role = user field for creatorMessages
    for message in userMessages:
      message['role'] = 'user'

    # Add role = assistant field for creatorAIMessages
    for message in userAIMessages:
      message['role'] = 'assistant' 

    # now merge and sort the two by their datetime MongoDb field
    last_messages = userMessages + userAIMessages
    last_messages.sort(key=lambda x: x['datetime'])

    messageLength = 0
    last_context = []

    # start from end of last_messages and go backwards appending to last_context
    # until messageLength exceeds maxContextMessagesLength
    for i in range(len(last_messages) - 1, -1, -1):
      message = last_messages[i]
      messageLength += len(message['message'])

      if messageLength > maxContextMessagesLength:
        break
      else:
        last_context.append(create_chat_message(message['role'], message['message']))

    # reverse last_context
    last_context.reverse()

    return last_context
  
  @staticmethod
  def check_if_has_balance(user):
    """
    Checks if the user has a balance > 0
    """
    if not user:
      return False
    
    # get user balance
    user_balance = user['balance']
    
    print('BALANCE')
    print(user_balance)

    if user_balance > 0:
      return True
    else:
      return False
  
  @staticmethod
  def charge_user_for_response(chat_id, response_message):
    """
    Charges the user for the response_message
    """
    # get user
    user = User.query({'chatId': chat_id})
    if not user:
      return False
    
    # get user balance
    user_balance = user['balance']

    fixed_cost = 0.02
    cost_per_character = 0.0035

    # calculate cost
    cost = fixed_cost + (cost_per_character * len(response_message))

    # convert to cents and round up
    cost = int(cost * 100)

    print('COST: ', cost)
    print('LEN: ', len(response_message))

    # update user balance
    new_balance = user_balance - cost

    # ensure balance is not negative
    if new_balance < 0:
      new_balance = 0

    User.update(user['userId'], {'balance': new_balance})

    return True
  
  @staticmethod
  def charge_user_for_json_response(chat_id, response_message: dict):
    """
    Charges the user for the AI output that is in a JSON format
    """
    # get user
    user = User.query({'chatId': chat_id})
    if not user:
      return False
    
    # get user balance
    user_balance = user['balance']

    # convert response_message to string
    response_message = json.dumps(response_message)

    fixed_cost = 0.02
    cost_per_character = 0.0035

    # calculate cost
    cost = fixed_cost + (cost_per_character * len(response_message))

    # convert to cents and round up
    cost = int(cost * 100)

    print('COST: ', cost)
    print('LEN: ', len(response_message))

    # update user balance
    new_balance = user_balance - cost

    # ensure balance is not negative
    if new_balance < 0:
      new_balance = 0

    User.update(user['userId'], {'balance': new_balance})

    return True
    

  

  
