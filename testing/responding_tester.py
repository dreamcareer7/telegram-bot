from ai.ai_api import create_chat_completion, create_chat_message

# system = prompter, assistant = responder (Mirror You), user = actual user talking


system_name = "Riley"
system_type ="girlfriend"
user_type = "boyfriend"
tone = "flirty, casual, horny"

# load in current context list from text file
with open('current_context.txt', 'r') as f:
  current_context = f.readlines()

# # Note: for training prompt, user_type & system type are reversed to maximize training 
initial_response_prompt = (
  f"Your name is {system_name}"
  f"The user is your {user_type} and you are the {system_type}"
  f"You are going to start casually chatting with your {user_type} over iMessage"
  f"Since you are texting, use a normal human texting style that is super informal"
  f"This means no capital words, letters, run-on sentences and other characteristics of texting"
  f"The way you talk and text can be seen from your last messages."
  f"The last messages are formatted in a list of dictionaries."
  f"Each dictionary has a key representing your {user_type} and the value being what they said"
  f"and a key representing you, the {system_type}, and the value being your response to that message"
  f"Imitate your responses to the messages, not your {user_type}'s messages"
  f"{current_context}"
  f"Based on these last messages, you are going to text in a similar manner using the style shown above"
  f"Send a text to your {user_type} to start a conversation"
)

def get_respond_training_prompt(user_message):
  respond_training_prompt = (
    f"Your name is {system_name}"
    f"The user is your {user_type} and you are the {system_type}"
    f"You are going to start casually chatting with your {user_type} over iMessage"
    f"Since you are texting, use a normal human texting style that is super informal"
    f"This means no capital words, letters, run-on sentences and other characteristics of texting"
    f"The way you talk and text can be seen from your last messages."
    f"The last messages are formatted in a list of dictionaries."
    f"Each dictionary has a key representing your {user_type} and the value being what they said"
    f"and a key representing you, the {system_type}, and the value being your response to that message"
    f"Imitate your responses to the messages, not your {user_type}'s messages"
    f"{current_context}"
    f"Based on these last messages, you are going to send response texts in a similar manner using the style shown above"
    f"Your {user_type} has just sent you this message:"
    f"{user_message}"
    f"Your response:"
  )
  return respond_training_prompt

# Keep track of current context
current_context = [create_chat_message("system", initial_response_prompt)]

# get first ai message
last_ai_message = create_chat_completion(current_context)

# add assistant message to context
current_context.append(create_chat_message("assistant", last_ai_message))

# Number of times to collect data
numb_back_and_forths = 5

message_history = []

for i in range(numb_back_and_forths):
  print(last_ai_message)

  # Get the user input
  user_input = input("User: ")

  # Add the user input to the context
  current_context.append(create_chat_message("user", user_input))

  message_history.append({
    f"{system_type}": last_ai_message,
    f"{user_type}": user_input,
  })

  # # Now add a system prompt to instruct AI to respond to last user's message
  current_context.append(create_chat_message("system", get_respond_training_prompt(user_input)))

  # Set the last_ai_message as the response to the user's message
  last_ai_message = create_chat_completion(current_context)
  # Add the assistant response to the context
  current_context.append(create_chat_message("assistant", last_ai_message))


# save training_data list to text file to be loaded later
with open('current_context.txt', 'w') as f:
  for item in message_history:
    f.write("%s\n" % item)


