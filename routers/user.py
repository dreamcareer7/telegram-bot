from fastapi import APIRouter, Depends, File, UploadFile, Header

from pydantic import BaseModel
from dependencies import validate_access_token
from db.models.user.user import User

from firebase.storage import save_creator_sample

from messaging.sending import send_message

from ai.creator.training import generate_initial_message, respond_to_creator_message

router = APIRouter(
  prefix="/user",
  tags=["user"],
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
  currentlyChattingWith = queryData['currentlyChattingWith']

  User.save(email, userId, fullName, phoneNumber, currentlyChattingWith)


@router.post("/upload_audio")
def upload_audio(audio: UploadFile = File(...), userId: str = Header(...)):
  audio_bytes = audio.file.read()
  # MongoDB:
  sample_public_url = save_creator_sample(userId, audio.file.read())

  # Save public url to firebase in MongoDB
  audio_dict = {"audio": sample_public_url}
  CreatorAudio.save(userId, audio_bytes)
  return {"message": "Audio file saved successfully."}
    

@router.post("/submit_onboarding")
async def respond_to_messages(queryData: dict, userId: str = Header(...)):
  # extract displayName, creatorType, userType, textingTone

  # displayName = queryData['displayName']
  # creatorType = queryData['creatorType']
  # userType = queryData['userType']
  # textingTone = queryData['textingTone']

  Creator.update(userId, queryData)
  

@router.post("/send_first_message")
async def send_first_message(userId: str = Header(...)):
  # Get Creator data
  creator = Creator.query({'userId': userId})

  # Get Creator phone number
  creator_phone_number = creator['phoneNumber']

  # Generate initial message
  initial_message = generate_initial_message(creator['creatorType'], creator['userType'], creator['textingTone'])

  # TODO: might be exceeding length
  # initial_message = 'Welcome to your OnlyMirror! I am going to simulate your target user to learn your texting style. Please text back as if I\'m a real person :) Ahem... so anyways:' + initial_message

  CreatorAIMessage.save(userId, initial_message)

  # Send initial message
  send_message(creator_phone_number, initial_message)
