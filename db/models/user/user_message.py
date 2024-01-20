from db.mongodb import db
from bson import ObjectId
from utils.json import parse_json
import json 
from datetime import timedelta, datetime

from db.models.creator.creator import Creator

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

s=set(stopwords.words('english'))

collection = db['user_messages']

# Messages from the User to the AI
class UserMessage:
  def __init__(self):
    pass
  
  @staticmethod
  def save(userId, message, creatorDisplayName):
    userMessage = {
      'userId': userId,
      'message': message,
      'type': 'normal',
      'datetime': datetime.utcnow(),
      'creatorDisplayName': creatorDisplayName,
    }
    UserMessage.extract_keywords_and_store_for_creator(message, creatorDisplayName)
    collection.insert_one(userMessage)

  @staticmethod
  def extract_keywords_and_store_for_creator(message, creatorDisplayName):
    """
    Extract keywords from the user's message 
    and save to creator's keywords for analytics
    """
    keywords = filter(lambda w: not w in s, message.split())
    # convert to list
    keywords = list(keywords)
    
    print('KEYWORDS')
    print(keywords)
    Creator.storeKeywords(None, keywords, creatorDisplayName)



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
  def getLast30DaysMessages(creatorDisplayName):
    try:
      results = collection.find({
        'creatorDisplayName': creatorDisplayName,
        'datetime': {
          '$gte': datetime.utcnow() - timedelta(days=30)
        }
      })
      # convert each item in results to a dictionary
      results = map(lambda result: parse_json(result), results)
      return list(results)
    except Exception as e:
      print('Error in query')
      print(e)
      return []