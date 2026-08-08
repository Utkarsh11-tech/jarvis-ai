import os

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

load_dotenv()


def speak_online(text: str) -> None:
    """
    Speaks text using the ElevenLabs JARVIS voice.
    """

    if not text:
        return

    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY was not found.")

    if not voice_id:
        raise RuntimeError("ELEVENLABS_VOICE_ID was not found.")

    client = ElevenLabs(api_key=api_key)

    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
    )

    play(audio)
