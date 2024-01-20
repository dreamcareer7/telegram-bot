from fastapi import APIRouter, Request, Header

from pydantic import BaseModel
from dependencies import validate_access_token
from db.models.creator.creator import Creator
from db.models.creator.creator_audio import CreatorAudio
from db.models.creator.creator_ai_message import CreatorAIMessage
from db.models.creator.creator_message import CreatorMessage

from db.models.user.user import User
import json
import os
import stripe

import os

stripe_api_key = os.getenv("STRIPE_API_KEY")
# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


router = APIRouter(
    prefix="/stripe",
    tags=["stripe"],
    # dependencies=[Depends(validate_access_token)],
    # responses={404: {"description": "Not found"}},
)

@router.post("/webhook")
async def create_creator(request: Request):
  # fast
  event = None
  event = await request.json()  

  # Handle the event
  if event['type'] == 'payment_intent.created':
    payment_intent = event['data']['object']
    payment_intent_id = payment_intent['id']

    try:
      res = stripe.PaymentIntent.modify(
        payment_intent_id,
        setup_future_usage='off_session',
      )
      print('RESULT OF SETTING FUTURE USAGE')
      print(res)
    except Exception as e:
      print(e)
      print('Unable to setup future usage with card')
      return {'success': False}

    print(res)

  else:
    print('Unhandled event type {}'.format(event['type']))

  return {'success': True}


@router.post("/get_link")
async def get_link(userId: str = Header(...)):
  creator = Creator.query({'userId': userId})
  if not creator:
    return ''
    
  connectedStripeAccountId = ''
  
  # Create stripe account if does not exist
  if 'connectedStripeAccountId' not in creator:
    resp = stripe.Account.create(
      country="US",
      type="express",
      capabilities={"card_payments": {"requested": True}, "transfers": {"requested": True}, "tax_reporting_us_1099_k": {"requested": True}, },
      business_type="individual",
      business_profile={"product_description": "Influencer on Beemo selling their AI chatbot"},
    )
    connectedStripeAccountId = resp['id']
    Creator.update({'userId': userId}, {'connectedStripeAccountId': connectedStripeAccountId})

  resp = stripe.AccountLink.create(
    account=connectedStripeAccountId,
    refresh_url="https://beemo.ai/creator/dashboard?completedStripe",
    return_url="https://beemo.ai/creator/dashboard?returnFromStripe=true",
    type="account_onboarding",
  )

  return resp['url']

