from datetime import datetime


def get_greeting():
    """
    Returns a time-based greeting for JARVIS.
    """

    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "Good morning, Sir."

    if 12 <= hour < 17:
        return "Good afternoon, Sir."

    if 17 <= hour < 21:
        return "Good evening, Sir."

    return "Good night, Sir."
