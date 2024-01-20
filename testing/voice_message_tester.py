from twilio.rest import Client

# Your Twilio account SID and auth token
account_sid = 'your_account_sid'
auth_token = 'your_auth_token'

client = Client(account_sid, auth_token)

# The phone number you want to send the message to (in the format +1xxx-xxx-xxxx)
to_number = "+14845579287"

# The Twilio phone number you want to send the message from (in the format +1xxx-xxx-xxxx)
from_number = "+1415xxx-xxxx"

# The URL of the MP3 file you want to send
media_url = "http://example.com/path/to/voice_message.mp3"

# Send the MMS message
message = client.messages.create(
    to=to_number,
    from_=from_number,
    media_url=media_url)