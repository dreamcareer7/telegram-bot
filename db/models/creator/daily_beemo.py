from db.mongodb import db
from bson import ObjectId
from utils.json import parse_json
import json 
from datetime import datetime

collection = db['daily_beemos']

# Messages from the Creator to the AI
class DailyBeemo:
  def __init__(self):
    pass
  
  @staticmethod
  def save(userId, displayName, dailyBeemo):
    dailyBeemo = {
      'creatorUserId': userId,
      'creatorDisplayName': displayName,
      'imageUrl': dailyBeemo['imageUrl'],
      'description': dailyBeemo['description'],
      'nsfw': dailyBeemo['nsfw'],
      'quality': dailyBeemo['quality'],
      'datetime': datetime.utcnow(),
    }
    collection.insert_one(dailyBeemo)

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