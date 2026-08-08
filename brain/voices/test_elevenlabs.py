import os

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play


load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("ELEVENLABS_VOICE_ID")

if not api_key:
    raise RuntimeError(
        "ELEVENLABS_API_KEY was not found in .env"
    )

if not voice_id:
    raise RuntimeError(
        "ELEVENLABS_VOICE_ID was not found in .env"
    )


client = ElevenLabs(
    api_key=api_key
)


audio = client.text_to_speech.convert(
    voice_id=voice_id,
    text=(
        "Good evening. I am JARVIS. "
        "All systems are operational."
    ),
    model_id="eleven_multilingual_v2",
)


play(audio)