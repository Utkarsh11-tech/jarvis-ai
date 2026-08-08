from brain.voices.online_speaker import speak_online
from brain.voices.offline_speaker import speak_offline

VOICE_MODE = "online"


def speak(text: str) -> None:
    """
    Speaks text using the currently selected voice engine.
    """

    if not text:
        return

    if VOICE_MODE == "online":
        speak_online(text)

    elif VOICE_MODE == "offline":
        speak_offline(text)

    else:
        raise ValueError(f"Unknown VOICE_MODE: {VOICE_MODE}")
