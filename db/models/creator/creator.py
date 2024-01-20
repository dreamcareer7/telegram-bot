from db.mongodb import db
from bson import ObjectId
from utils.json import parse_json
import json 

from datetime import datetime
from db.models.creator.creator_ai_message import CreatorAIMessage
from db.models.creator.creator_message import CreatorMessage
from ai.ai_api import create_chat_message 

collection = db['creators']

class Creator:
  def __init__(self, userId, type, name, topic, currTopics, userStartingLevel, userStartingExperience, userCurrExperience, userXP, userGoals):
    pass
  
  @staticmethod
  def save(email, userId, fullName, phoneNumber, displayName):
    creator = {
      'email': email,
      'userId': userId,
      'fullName': fullName,
      'phoneNumber': phoneNumber,
      'displayName': displayName,
      'joinDate': datetime.utcnow(),
    }
    collection.insert_one(creator)

  @staticmethod
  def update(userId, update_data):
    # displayName, creatorType, userType, textingTone
    result = collection.update_one({'userId': userId}, {'$set': update_data})

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
  def getTrainingLastMessagesContextForOpenAI(userId: str):
    """
    Get's the last context as OpenAI ChatGPT formatted context (with role and message)
    Get's only the last context until the maxContextMessagesLength is exceeded
    """
    maxContextMessagesLength = 4000 # 4000 characters

    # Get all CreatorAIMessage and CreatorMessage before this
    creatorMessages = CreatorMessage.query({'userId': userId})
    creatorAIMessages = CreatorAIMessage.query({'userId': userId})

    # Add role = user field for creatorMessages
    for message in creatorMessages:
      message['role'] = 'user'

    # Add role = assistant field for creatorAIMessages
    for message in creatorAIMessages:
      message['role'] = 'assistant' 

    # now merge and sort the two by their datetime MongoDb field
    last_messages = creatorMessages + creatorAIMessages
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
  def storeKeywords(userId: str = None, keywords: list = "", displayName: str = None):
    if not displayName:
      creator = Creator.query({'userId': userId})
    else:
      creator = Creator.query({'displayName': displayName})

    # get keywords hashmap
    newKeywords = creator['keywords'] if 'keywords' in creator else {}


    # add keywords to hashmap
    for keyword in keywords:
      if keyword not in newKeywords:
        newKeywords[keyword] = 0
      newKeywords[keyword] += 1
    
    # update creator
    Creator.update(creator['userId'], {'keywords': newKeywords})



  
