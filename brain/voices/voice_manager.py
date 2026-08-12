from brain.voices.online_speaker import speak_online
from brain.voices.offline_speaker import speak_offline
from brain.voices.xtts_speaker import speak_xtts


VOICE_MODE = "xtts"


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

    elif VOICE_MODE == "xtts":
        speak_xtts(text)

    else:
        raise ValueError(
            f"Unknown VOICE_MODE: {VOICE_MODE}"
        )