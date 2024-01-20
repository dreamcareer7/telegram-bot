from db.mongodb import db
from bson import ObjectId
from utils.json import parse_json
import json 
from datetime import datetime

collection = db['creator_messages']

# Messages from the Creator to the AI
class CreatorMessage:
  def __init__(self):
    pass
  
  @staticmethod
  def save(userId, message):
    creatorMessage = {
      'userId': userId,
      'message': message,
      'type': 'normal',
      'datetime': datetime.utcnow(),
    }
    collection.insert_one(creatorMessage)
  
  @staticmethod
  def saveByDisplayName(displayName, message):
    creatorMessage = {
      'creatorDisplayName': displayName,
      'message': message,
      'type': 'normal',
      'datetime': datetime.utcnow(),
    }
    collection.insert_one(creatorMessage)

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
      return list(results)
    except Exception as e:
      print('Error in query')
      print(e)
      return []

    
  @staticmethod
  def getTextingStyle(userId):
    try:
      messages = CreatorMessage.query({'userId': userId})

      textingStyle = ""

      for message in messages:
        textingStyle += message['message'] + "\n"

      max_characters = 800 * 4 # 800 words * 4 characters per word

      # if texting style length
      if len(textingStyle) > max_characters:
        textingStyle = textingStyle[:max_characters]

      return textingStyle
    except:
      return ""

  
  @staticmethod
  def getTextingStyleByDisplayName(displayName):
    try:
      messages = CreatorMessage.query({'displayName': displayName})

      textingStyle = ""

      for message in messages:
        textingStyle += message['message'] + "\n"

      max_characters = 800 * 4 # 800 words * 4 characters per word

      # if texting style length
      if len(textingStyle) > max_characters:
        textingStyle = textingStyle[:max_characters]

      return textingStyle
    except:
      return ""