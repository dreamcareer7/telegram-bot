from db.mongodb import db
from bson import ObjectId
from utils.json import parse_json
import json 
from datetime import datetime
import uuid

collection = db['user_payments']

# Messages from the User to the AI
class UserPayment:
  def __init__(self):
    pass
  
  @staticmethod
  def save(creatorDisplayName, chatId, amount, currency, name):
    userPayment = {
      'creatorDisplayName': creatorDisplayName,
      'chatId': chatId,
      'datetime': datetime.utcnow(),
      'amount': amount,
      'currency': currency,
      'name': name,
    }
    res = collection.insert_one(userPayment)
    # get _id
    return res.inserted_id


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