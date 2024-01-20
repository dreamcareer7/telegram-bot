from elevenlabs import clone, generate, play, set_api_key
from elevenlabs.api import History
import os

set_api_key(os.getenv("ELEVEN_LABS_API_KEY"))

# use high variability
# 
# 35-45% stability
# 75-85% clarity / similarity 

voice = clone(
    name="Riley",
    description="A hot sexy girl who imitates a popular instagram model who is flirty and a girlfriend",
    files=["./audioSample1.mp3", "./audioSample2.mp3"],
)

audio = generate(text="dang boi, u so cute... wow are so cool...", voice=voice)

play(audio)

history = History.from_api()
print(history)
