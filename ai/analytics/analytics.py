from ai.ai_api import create_chat_completion, create_chat_message
from db.models.creator.creator import Creator
import json

def generate_initial_message_to_user(keywords: list):
  response_format = {
    "title": "string title of idea that is less than 5 words",
    "description": "an entire description of the idea",
    "fansIncrease": "number of fans that will be gained from this idea based on the keyword impressions",
  }

  keywords_formatted = ""
  for keyword in keywords:
    keywords_formatted += f"{keyword}: 0 impressions\n"

  prompt = (
    f"You are going to help a social media influencer come up with ideas for what they can do"
    f"Ideas can be anything from a short form video, long form video, post, story idea"
    f"or something very creative such as a public appearance, a new product, businesses they could reach out to"
    f"or anything else that you think would be a good idea for them to do"
    f"To guide generating ideas for them, a user study was done to figure out the most used keywords associated with them"
    f"Here are the most used keywords associated with them along with the impressions for each keyword:"
    f"{keywords_formatted}"
    f"Based on these keywords, you are going to generate ideas for them"
    f"Return your response as a Python list of ideas made up of the following objects"
    f"{json.dumps(response_format)}"
  )

  current_context = [create_chat_message("system", prompt)]

  # get first ai message
  ai_message = create_chat_completion(current_context)

  return parse_response(ai_message) 

def parse_response(response: str):
  # json parse response
  response = json.loads(response)


  return response