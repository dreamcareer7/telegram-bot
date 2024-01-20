import openai
from openai.error import APIError, RateLimitError
import time
import os
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")

goose_ai_key = os.getenv("GOOSE_AI_KEY")

def create_chat_completion(
    messages: list,  # type: ignore
    temperature: float = 0,
    max_tokens: int | None = 100, # max of 100 tokens by default
		model: str | None = "gpt-3.5-turbo", # change default model here
) -> str:
	"""Create a chat completion using the OpenAI API

	Args:
    messages (list[dict[str, str]]): The messages to send to the chat completion
    model (str, optional): The model to use. Defaults to None.
    temperature (float, optional): The temperature to use. Defaults to 0.9.
    max_tokens (int, optional): The max tokens to use. Defaults to None.

	Returns:
    str: The response from the chat completion
	"""
	response = None
	num_retries = 10
	warned_user = False
	print(
		f"Creating chat completion with model {model}, temperature {temperature},"
		f" max_tokens {max_tokens}"
	)
	for attempt in range(num_retries):
		backoff = 2 ** (attempt + 2)
		try:
			response = openai.ChatCompletion.create(
				model=model,
				messages=messages,
				temperature=temperature,
				max_tokens=max_tokens,
			)
			break
		except RateLimitError:
			pass
		except APIError as e:
			# Retry on 502
			if e.http_status == 502:
				pass
			# Reached max attempts
			if attempt == num_retries - 1:
				break
		print(
			"Error: ",
			f"API Bad gateway. Waiting {backoff} seconds..."
		)
		time.sleep(backoff)
	if response is None:
		print(
				"FAILED TO GET RESPONSE FROM OPENAI",
				"Auto-GPT has failed to get a response from OpenAI's services. "
				+ f"Try running Auto-GPT again, and if the problem the persists try running it with",
		)
		print(f"Failed to get response after {num_retries} retries")


	return response.choices[0].message["content"]


def create_chat_message(role, content):
	"""
	Create a chat message with the given role and content.

	Args:
	role (str): The role of the message sender, e.g., "system", "user", or "assistant".
	content (str): The content of the message.

	Returns:
	dict: A dictionary containing the role and content of the message.
	"""
	return {"role": role, "content": content}


def transcribe_audio(file_path):
  """
  Transcribe audio file using OpenAI Whisper
  """
  try:
    audio_file= open(file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript)
    return transcript["text"]
  except Exception as e:
    print("Error trnascribing")
    print(e)
    return "Sorry, I couldn't understand that. Please try texting me :)"

def alternate_chat_completion(messages, max_tokens):
  """
  If OpenAI API fails, use this function to generate a response
  GooseAI: https://goose.ai/docs/api/completions
  """
  prompt = \
    """Riley is a hot female, girlfriend who is there to make conversation with the Boyfriend in a meaningful way while also being playful and flirty.
    The boyfriend is a man who will respond to Riley.
    Only respond with Riley's text and do not add anything else.
    Riley should be respectful and courteous and treat everyone with fairness, respect, and kindness.
    Riley is against racism and discrimination of any kind.
    Riley is a very kind person and will refuse to respond about anything that is racist, discriminatory, or violent.

    Boyfriend: heeey Riley, help me with my loneliness babe.
    Riley:"""
  # make a post request to https://api.goose.ai/v1/engines/{engine_id}/completions
  resp = requests.post(
    "https://api.goose.ai/v1/engines/cassandra-lit-6-9b/completions",
    headers={
      'Authorization': 'Bearer ' + goose_ai_key,
      'Content-Type': 'application/json'
    },
    json={
      "prompt": prompt,
      "max_tokens": max_tokens,
      "temperature": 0.2,
      "stop": ["\n", " Boyfriend:", " Riley:"],
    }
  )
  # get the result
  result = resp.json()
  # return the text
  return result
