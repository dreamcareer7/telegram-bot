from fastapi import APIRouter, Depends, File, UploadFile, Header

from pydantic import BaseModel
from dependencies import validate_access_token
from db.models.creator.creator import Creator
from db.models.creator.creator_audio import CreatorAudio
from db.models.creator.creator_ai_message import CreatorAIMessage
from db.models.creator.creator_message import CreatorMessage

from db.models.user.user import User
from db.models.user.user_message import UserMessage
from db.models.user.user_payment import UserPayment

from firebase.storage import save_creator_sample

from messaging.sending import send_message

from ai.creator.training import generate_initial_message, respond_to_creator_message
from ai.creator.responding import generate_initial_message_to_user


from elevenlabs import clone, generate, play, set_api_key
from elevenlabs.api import History
import os

set_api_key(os.getenv("ELEVEN_LABS_API_KEY"))


router = APIRouter(
    prefix="/creatorData",
    tags=["creatorData"],
    # dependencies=[Depends(validate_access_token)],
    # responses={404: {"description": "Not found"}},
)

@router.post("/totalEarnings")
async def getStats(userId: str = Header(...)):
  creator = Creator.query({'userId': userId})
  
  # return if no creatorDisplayName
  if not creator or 'displayName' not in creator:
    print('ERROR: RETURNING BECAUSE NO CREATOR NAME')
    return {
      'totalEarnings': 0,
      'averageEarningsPerFan': 0
    }
  
  creatorDisplayName = creator['displayName']
  payments = UserPayment.query({'creatorDisplayName': creatorDisplayName})
  # sum the payments
  totalEarnings = 0
  for payment in payments:
    totalEarnings += int(payment['amount'])
  
  return {
    'totalEarnings': totalEarnings,
    'averageEarningsPerFan': totalEarnings / len(payments) if len(payments) > 0 else 0
  }

@router.post("/monthlyActiveFans")
async def getStats(userId: str = Header(...)):
  creator = Creator.query({'userId': userId})  

  # return if no creatorDisplayName
  if not creator or 'displayName' not in creator:
    print('ERROR: RETURNING BECAUSE NO CREATOR NAME')    
    return {
      'monthlyActiveFans': 0
    }

  creatorDisplayName = creator['displayName']

  userMessages = UserMessage.getLast30DaysMessages(creatorDisplayName)
  # get unique users
  uniqueUsers = []
  for userMessage in userMessages:
    if userMessage['userId'] not in uniqueUsers:
      uniqueUsers.append(userMessage['userId'])
  
  return {
    'monthlyActiveFans': len(uniqueUsers)
  }


@router.post("/earningsByDayOfWeek")
async def getEarningsByDayOfWeek(userId: str = Header(...)):
  creator = Creator.query({'userId': userId})

  # return if no creatorDisplayName
  if not creator or 'displayName' not in creator:
    print('ERROR: RETURNING BECAUSE NO CREATOR NAME')
    return {
      'earningsByDayOfWeek': [0, 0, 0, 0, 0, 0, 0]
    }

  creatorDisplayName = creator['displayName']

  payments = UserPayment.query({'creatorDisplayName': creatorDisplayName})

  # sum the payments
  earningsByDayOfWeek = [0, 0, 0, 0, 0, 0, 0]
  for payment in payments:
    earningsByDayOfWeek[payment['datetime'].weekday()] += int(payment['amount'])
  
  return {
    'earningsByDayOfWeek': earningsByDayOfWeek,
  }

@router.post("/top5Chats")
async def top5Chats(userId: str = Header(...)):
  creator = Creator.query({'userId': userId})

  # return if no creatorDisplayName
  if not creator or 'displayName' not in creator:
    print('ERROR: RETURNING BECAUSE NO CREATOR NAME')
    return {
      'top5Chats': []
    }

  creatorDisplayName = creator['displayName']

  payments = UserPayment.query({'creatorDisplayName': creatorDisplayName})

  # organize payments by userId: totalAmount
  paymentsByUserId = {}

  # map a userId to a payment
  userIdData = {}

  for payment in payments:
    userId = payment['userId']
    amount = payment['amount'] or 0

    if userId in paymentsByUserId:
      paymentsByUserId[userId] += int(amount)
    else:
      paymentsByUserId[userId] = int(amount)
    
    if userId in userIdData:
      # see if payment contains name
      if 'name' in payment:
        userIdData[userId]['name'] = payment['name']
    else:
      userIdData[userId] = {
        'name': payment['name'],
        'userId': payment['userId'],
      }
  
  # sort paymentsByUserId by totalAmount
  paymentsByUserId = dict(sorted(paymentsByUserId.items(), key=lambda item: item[1], reverse=True))

  # get top 5
  top5 = []
  for userId in paymentsByUserId:
    if len(top5) < 5:
      top5.append(userIdData[userId])
    else:
      break
  
  return {
    'top5Chats': top5,
  }

@router.post("/topKeywords")
async def topKeywords(userId: str = Header(...)):
  creator = Creator.query({'userId': userId})

  # return if no creatorDisplayName
  if not creator or 'displayName' not in creator:
    print('ERROR: RETURNING BECAUSE NO CREATOR NAME')
    return {
      'topKeywords': []
    }

  creatorDisplayName = creator['displayName']

  creator = Creator.query({'displayName': creatorDisplayName})
  keywords = creator['keywords'] if 'keywords' in creator else {}

  # sort keywords by count but maintain all keywords data
  keywords = dict(sorted(keywords.items(), key=lambda item: item[1], reverse=True))

  # get top 5
  top5 = []
  for keyword in keywords:
    if len(top5) < 5:
      top5.append({
        'name': keyword,
        'impressions': keywords[keyword]
      })
    else:
      break
  
  print(top5)

  return {
    'topKeywords': top5,
  }

@router.post("/contentSuggestions")
async def contentSuggestions(userId: str = Header(...)):
  creator = Creator.query({'userId': userId})

  # return if no creatorDisplayName
  if not creator or 'displayName' not in creator:
    print('ERROR: RETURNING BECAUSE NO CREATOR NAME')
    return {
      'topKeywords': []
    }

  creatorDisplayName = creator['displayName']

  creator = Creator.query({'displayName': creatorDisplayName})
  keywords = creator['keywords'] if 'keywords' in creator else {}

  # sort keywords by count
  keywords = dict(sorted(keywords.items(), key=lambda item: item[1], reverse=True))

  # get top 5
  top5 = []
  for keyword in keywords:
    if len(top5) < 5:
      top5.append(keyword)
    else:
      break
  
  return {
    'topKeywords': top5,
  }