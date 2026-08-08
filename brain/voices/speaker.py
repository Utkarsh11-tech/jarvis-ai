import pyttsx3


def speak(text: str) -> None:
    """
    Speaks the supplied text using the selected JARVIS voice.
    """

    if not text:
        return

    engine = pyttsx3.init()

    voices = engine.getProperty("voices")

    if voices:
        engine.setProperty("voice", voices[0].id)

    # Slightly slower and calmer than the default.
    engine.setProperty("rate", 165)

    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()

    engine.stop()
