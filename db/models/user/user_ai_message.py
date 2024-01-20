from db.mongodb import db
from bson import ObjectId
from utils.json import parse_json
import json 
from datetime import datetime

from db.models.creator.creator import Creator

collection = db['user_ai_messages']


# Messages from the AI to the User
class UserAIMessage:
  def __init__(self):
    pass
  
  @staticmethod
  def save(userId, message):
    user_ai_message = {
      'userId': userId,
      'message': message,
      'type': 'normal',
      'datetime': datetime.utcnow(),
    }
    collection.insert_one(user_ai_message)

  @staticmethod
  def update(userId, update_data):
    # displayName, creatorType, userType, textingTone
    result = collection.update_one({'userId': userId}, {'$set': update_data})

  @staticmethod
  def extract_keywords_and_store_for_creator(topics: str, creatorDisplayName: str):
    """
    Extract keywords from the user's message 
    and save to creator's keywords for analytics
    """
    # split by comma space
    keywords = topics.split(', ')
    # convert to list
    keywords = list(keywords)
    Creator.storeKeywords(None, keywords, creatorDisplayName)


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