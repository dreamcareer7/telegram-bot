from db.models.user import collection
from utils.json import parse_json
from ai.quests.quest_generation import Quest

def generate_quests_for_all_users():
  # get all users in batches of 5000
  cursor = collection.find().batch_size(5000)
  for document in cursor:
      # process the document
      user = parse_json(document)
      # generate quests for the user
      Quest.generate_quests(user)
