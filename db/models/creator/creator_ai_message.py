from db.mongodb import db
from bson import ObjectId
from utils.json import parse_json
import json 
from datetime import datetime

collection = db['creator_ai_messages']


# Messages from the AI to the Creator
class CreatorAIMessage:
  def __init__(self):
    pass
  
  @staticmethod
  def save(userId, message):
    creator_ai_message = {
      'userId': userId,
      'message': message,
      'type': 'normal',
      'datetime': datetime.utcnow(),
    }
    collection.insert_one(creator_ai_message)

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