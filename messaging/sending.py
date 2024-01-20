import os
from twilio.rest import Client

# Create client
account_sid = "ACeec62e1aa54a2e98299cb63cdd756ca7"
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

# Phone number to send from
from_phone_number = "+18559301985"


def send_message(to, body):
  message = client.messages.create(
    body=body,
    from_=from_phone_number,
    to=to
  )
  print(message.sid)