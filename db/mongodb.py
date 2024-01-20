import os
from dotenv import load_dotenv

from pymongo import MongoClient
# get client string from .env file
connection_string = os.getenv("MONGO_CONNECTION_STRING")
client = MongoClient(connection_string)
print('Connected to MongoDB')

db = client['main']


