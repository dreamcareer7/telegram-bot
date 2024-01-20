from fastapi import APIRouter, Depends, File, UploadFile, Header
from typing import List
from fastapi.responses import StreamingResponse, JSONResponse
import io 
from pydantic import BaseModel
from dependencies import validate_access_token
from db.models.creator.creator import Creator
from db.models.creator.creator_audio import CreatorAudio
from db.models.creator.creator_ai_message import CreatorAIMessage
from db.models.creator.creator_message import CreatorMessage
from db.models.creator.daily_beemo import DailyBeemo

from db.models.user.user import User
from db.models.user.user_ai_message import UserAIMessage

from firebase.storage import save_creator_sample

from messaging.sending import send_message

from ai.creator.training import generate_initial_message, respond_to_creator_message, convert_frontend_messages_to_context
from ai.creator.responding import generate_initial_message_to_user, send_greeting

from voice.generator import generate_voice

from elevenlabs import clone, generate, play, set_api_key
from elevenlabs.api import History
import os
import requests

import base64

# url = "https://api.elevenlabs.io/v1/voices/<voice-id>/edit"

# headers = {
#   "Accept": "application/json",
#   "xi-api-key": "<xi-api-key>"
# }

# data = {
#     'name': 'Voice New name',
#     'labels': '{"accent": "British"}',
#     'description': 'Voice description'
# }

# files = [
#     ('files', ('sample1.mp3', open('sample1.mp3', 'rb'), 'audio/mpeg')),
#     ('files', ('sample2.mp3', open('sample2.mp3', 'rb'), 'audio/mpeg'))
# ]

# response = requests.post(url, headers=headers, data=data, files=files)
# print(response.text)

set_api_key(os.getenv("ELEVEN_LABS_API_KEY"))


router = APIRouter(
    prefix="/creator",
    tags=["creator"],
    # dependencies=[Depends(validate_access_token)],
    # responses={404: {"description": "Not found"}},
)

@router.post("/create")
async def create_creator(queryData: dict):
  # extract email, userId, fullName from queryDAta
  email = queryData['email']
  userId = queryData['userId']

  fullName = queryData['fullName']
  phoneNumber = queryData['phoneNumber']
  displayName = queryData['displayName']

  Creator.save(email, userId, fullName, phoneNumber, displayName)

@router.post("/get")
async def create_creator(userId: str = Header(...)):
  # extract email, userId, fullName from queryDAta
  return Creator.query({'userId': userId})

@router.post("/get_by_display_name")
async def create_creator(queryData: dict):
  # Get public creator data for /[creator_display_name] page
  displayName = queryData['displayName']
  creator = Creator.query({'displayName': displayName})

  return {
    'displayName': creator['displayName'],
    'profilePhoto': creator['profilePhoto'],
    'name': creator['fullName'],
  }

@router.post("/get_greeting")
async def get_greeting(queryData: dict):
  # Get public creator data for /[creator_display_name] page
  displayName = queryData['displayName']
  creator = Creator.query({'displayName': displayName})

  creatorTextingStyle = CreatorMessage.getTextingStyle(creator['userId'])
  greeting_message = send_greeting(creator['fullName'], creator['creatorType'], creator['userType'], creatorTextingStyle, creator['textingTone'], '', [], '')

  voice = generate_voice(displayName, greeting_message)
  voice_encoded = base64.b64encode(voice)

  return {
    'message': greeting_message,
    'audio': voice_encoded,
  }
  



@router.post("/upload_audio")
async def upload_audio(audioRecordings: List[UploadFile] = File(...), userId: str = Header(...), creatorType: str = Header(...), nsfwMode: str = Header(...), otherLanguage: str = Header(...)):
  print('HERE!')
  file_locations = []

  i = 0
  # For each audio
  for audio in audioRecordings:
    file_location = f'./temp/{userId}-{i}'
    file_locations.append(file_location)
    i += 1

    audio_bytes = audio.file.read()
    
    # Save to mongoDB
    CreatorAudio.save(userId, audio_bytes)

    # Write locally for passing to ElevenLabs
    with open(file_location, "wb+") as file_object:
      file_object.write(audio_bytes)

  # Get creator
  creator = Creator.query({'userId': userId})

  name = creator['displayName']

  if otherLanguage == 'spanish':
    name = name + '-spanish'
  
  # Clone creator voice based on nsfw or not
  if nsfwMode == 'yes':
    voice = clone(
      name=name,
      description="A sexy, flirty, goofy and conversational fun voice of a " + creatorType,
      files=file_locations,
    )
  else:
    voice = clone(
      name=name,
      description="A conversational, friendly, familiar, comfortable voice of a " + creatorType,
      files=file_locations,
      nsfw=False,
    )
  
  # delete temp files
  for file_location in file_locations:
    os.remove(file_location)

  # Save bytes to firebase in MongoDB
  return {"message": "Audio file saved successfully."}
    

@router.post("/get_audio_recordings")
async def get_audio_recordings(userId: str = Header(...)):
  resp = CreatorAudio.query({'userId': userId})
  print(resp)
  return resp

@router.post("/submit_onboarding")
async def submit_onboarding(queryData: dict, userId: str = Header(...)):
  Creator.update(userId, queryData)
  
@router.post("/update")
async def update(queryData: dict, userId: str = Header(...)):
  Creator.update(userId, queryData)

@router.post("/add_audios")
async def add_audios(audioRecordings: List[UploadFile] = File(...), userId: str = Header(...)):
  file_locations = []

  i = 0
  # For each audio
  for audio in audioRecordings:
    file_location = f'./temp/{userId}-{i}'
    file_locations.append(file_location)
    i += 1

    audio_bytes = audio.file.read()
    
    # Save to mongoDB
    CreatorAudio.save(userId, audio_bytes)

    # Write locally for passing to ElevenLabs
    with open(file_location, "wb+") as file_object:
      file_object.write(audio.file.read())

  return 
  # Get creator
  creator = Creator.query({'userId': userId})
  
  # Clone creator voice based on nsfw or not
  if nsfwMode == 'yes':
    voice = clone(
      name=creator['displayName'],
      description="A sexy, flirty, goofy and conversational fun voice of a " + creatorType,
      files=file_locations,
    )
  else:
    voice = clone(
      name=creator['displayName'],
      description="A conversational, friendly, familiar, comfortable voice of a " + creatorType,
      files=file_locations,
      nsfw=False,
    )

  # delete temp file
  os.remove(file_location)

  # Save bytes to firebase in MongoDB
  return {"message": "Audio file saved successfully."}
    
@router.post("/send_first_training_message")
async def send_first_training_message(queryData: dict):
  # Get Creator data
  # creator = Creator.query({'userId': userId})

  # Get creator user type
  creator_type = queryData['creatorType']
  nsfwMode = queryData['nsfwMode']

  # Generate initial message
  initial_message = generate_initial_message(creator_type, '', '', nsfwMode)

  # TODO: might be exceeding length
  # initial_message = 'Welcome to your OnlyMirror! I am going to simulate your target user to learn your texting style. Please text back as if I\'m a real person :) Ahem... so anyways:' + initial_message

  # CreatorAIMessage.save(userId, initial_message)

  if 'doNotSendSms' not in queryData or queryData['doNotSendSms']:
    return initial_message
  else:
    # Send sms initial message
    print('Sending messages')
    # send_message(creator_phone_number, initial_message)
    return initial_message

@router.post("/respond_to_training_message")
async def respond_to_training_message(queryData: dict):
  # Get messages data
  message = queryData['message']
  # Get creator user type
  creator_type = queryData['creatorType']
  # Messages
  messages = queryData['messages']
  # Display name
  creator_display_name = queryData['creatorDisplayName']
  # nsfw mode
  nsfwMode = queryData['nsfwMode']

  
  # TODO: reimplement context with no user id
  # TODO: send context from frontend as request body and parse here
  # Get Creator data
  # creator = Creator.query({'userId': userId})

  # # Save creator's current message to DB
  CreatorMessage.saveByDisplayName(creator_display_name, message)

  # Get context
  context = convert_frontend_messages_to_context(messages)
  
  # generate AI response to creator message
  ai_response = respond_to_creator_message(creator_type, '', '', message, context, nsfwMode)

  # save AI response message to DB
  # CreatorAIMessage.save(creator['userId'], ai_response)

  return ai_response

@router.post("/send_first_message_to_user")
async def send_first_message_to_user(queryData: dict, userId: str = Header(...)):
  creatorDisplayName = queryData['creatorDisplayName']
  userPhoneNumber = queryData['phoneNumber']
  userId = queryData['userId']

  # Get Creator data
  creator = Creator.query({'displayName': creatorDisplayName})


  # Update user currently chatting with
  User.update(userId, {'currentlyChattingWith': creator['displayName']})

  creatorTextingStyle = CreatorMessage.getTextingStyle(creator['userId'])

  # Generate initial message
  initial_message = generate_initial_message_to_user(creatorDisplayName, creator['creatorType'], creator['userType'], creatorTextingStyle, creator['textingTone'])

  # TODO: might be exceeding length
  # initial_message = 'Welcome to your OnlyMirror! I am going to simulate your target user to learn your texting style. Please text back as if I\'m a real person :) Ahem... so anyways:' + initial_message

  UserAIMessage.save(userId, initial_message)

  # Send initial message
  send_message(userPhoneNumber, initial_message)

@router.post("/uploadDailyBeemo")
async def upload_daily_beemo(queryData: dict, userId: str = Header(...)):
  creator = Creator.query({'userId': userId})

  dailyBeemos = queryData['dailyBeemos']

  for dailyBeemo in dailyBeemos:
    DailyBeemo.save(creator['userId'], creator['displayName'], dailyBeemo)
  
  return "success"


@router.post("/getDailyBeemos")
async def get_daily_beemos(queryData: dict, userId: str = Header(...)):
  print(userId)
  return DailyBeemo.query({'creatorUserId': userId})

@router.post("/check_handle_taken")
async def check_handle_taken(queryData: dict):
  displayName = queryData['displayName']
  creator = Creator.query({'displayName': displayName})
  return creator != None