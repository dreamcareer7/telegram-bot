from db.mongodb import db
from bson import ObjectId
from utils.json import parse_json
import json 

from datetime import datetime


collection = db['creatorAudios']

class CreatorAudio:
  def __init__(self, userId, type, name, topic, currTopics, userStartingLevel, userStartingExperience, userCurrExperience, userXP, userGoals):
    pass
  
  @staticmethod
  def save(userId, audio):
    newAudio = {
      'userId': userId,
      'audio': audio,
      'date': datetime.utcnow(),
    }
    collection.insert_one(newAudio)
  
  @staticmethod
  def get_audio(userId):
      audio_data = collection.find_one({'userId': userId})  # retrieve the binary data from MongoDB
      with open(f'temp/{userId}.mp3', 'wb') as f:  # create a new file and write the binary data to it
          f.write(audio_data['audio'])

  @staticmethod
  def update(disk_id, update_data):
    result = collection.update_one({'_id': ObjectId(disk_id)}, {'$set': update_data})

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
  
  
