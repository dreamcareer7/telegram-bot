from ai.ai_api import create_chat_completion, create_chat_message
from ai.creator.training_prompts import respond_training_message_prompt_3, initial_training_message_prompt_3, initial_training_message_prompt_1, respond_training_message_prompt_1

# system = prompter, assistant = fake messager, user = actual creator training

# system_type = creator (girlfriend), user_type = mock user (boyfriend)

def get_user_type_from_system_type(system_type):
  system_type.lower()

  if system_type == "boyfriend":
    return "girlfriend"
  elif system_type == "girlfriend":
    return "boyfriend"
  else:
    # TODO: think of default type if not either one of the two
    return "special someone"

def generate_initial_message(system_type, user_type='', tone='', nsfwMode='no'):
  """
  Generates the initial message to send to the creator to begin the training conversation 
  """
  if user_type == '':
    user_type = get_user_type_from_system_type(system_type)
  
  if nsfwMode == 'yes':
    prompt = initial_training_message_prompt_3(user_type, system_type)
  else:
    prompt = initial_training_message_prompt_1(user_type, system_type)

  current_context = [create_chat_message("system", prompt)]

  # get first ai message
  first_ai_message = create_chat_completion(current_context)

  # add assistant message to context
  current_context.append(create_chat_message("assistant", first_ai_message))

  return parse_response_to_user(first_ai_message)


def respond_to_creator_message(system_type, user_type='', tone='', user_message='', last_context=[], nsfwMode='no'):
  # add last context if provided
  if user_type == '':
    user_type = get_user_type_from_system_type(system_type)

  current_context = []
  if len(last_context) > 0:
    current_context = last_context
  
  if nsfwMode == 'yes':
    prompt = respond_training_message_prompt_3(user_type, system_type, user_message)
  else:
    prompt = respond_training_message_prompt_1(user_type, system_type, user_message)

  current_context.append(create_chat_message("system", prompt))

  # get first ai message
  ai_message = create_chat_completion(current_context)

  # add assistant message to context
  current_context.append(create_chat_message("assistant", ai_message))

  return parse_response_to_user(ai_message)

def parse_response_to_user(response):
  # if first char and last char are quotation, remove them
  if response[0] == '"' and response[-1] == '"':
    response = response[1:-1]
  
  # remove all emojis
  response = response.encode('ascii', 'ignore').decode('ascii')

  return response 

# TODO: context tracking
# # Keep track of current context
# current_context = [create_chat_message("system", initial_training_prompt)]

# # get first ai message
# last_ai_message = create_chat_completion(current_context)

# # add assistant message to context
# current_context.append(create_chat_message("assistant", last_ai_message))


# # Number of times to collect data
# numb_back_and_forths = 5


# training_data = []

# for i in range(numb_back_and_forths):
#   print(last_ai_message)
#   # if 1st message, generate initial message
#   # if i == 0:
#   #   initial_ai_response = create_chat_completion(current_context)
#   #   ai_response = create_chat_message("system", initial_ai_response)
#   #   current_context.append(ai_response)
#   # else:
#   #   # Get the assistant response as JSON
#   #   ai_response = create_chat_completion(current_context)

#   # Get the user input
#   user_input = input("User: ")

#   # Add the user input to the context
#   current_context.append(create_chat_message("user", user_input))

#   training_data.append({
#     f"{user_type}": last_ai_message,
#     f"{system_type}": user_input,
#   })

#   # Now add a system prompt to instruct AI to respond to last user's message
#   current_context.append(create_chat_message("system", get_respond_training_prompt(user_input)))
#   # Set the last_ai_message as the response to the user's message
#   last_ai_message = create_chat_completion(current_context)
#   # Add the assistant response to the context
#   current_context.append(create_chat_message("assistant", last_ai_message))


# # save training_data list to text file to be loaded later
# with open('current_context.txt', 'w') as f:
#   for item in training_data:
#     f.write("%s\n" % item)


def convert_frontend_messages_to_context(messages: list):
  converted_messages = []
  for message in messages:
    role = 'user'
    if message['type'].lower() == 'assistant':
      role = 'assistant'
    
    converted_messages.append(create_chat_message(role, message['text']))
  
  return converted_messages