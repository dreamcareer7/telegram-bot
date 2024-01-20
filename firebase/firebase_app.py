import os
import firebase_admin
from firebase_admin import credentials

firebase_app = None

def getFirebaseApp():
  global firebase_app

  # If var is already intialized, return the firebase app
  if firebase_app:
    return firebase_app
  
  # If not initialized & never initialized, return the firebase app
  try:
    firebase_app = firebase_admin.get_app(name='onlymirror')
  except:
    cred = credentials.Certificate(os.path.abspath(os.path.dirname(__file__))+ '/onlymirror_firebase_creds.json')
    firebase_app = firebase_admin.initialize_app(credential=cred, name='onlymirror')

  
  return firebase_app



