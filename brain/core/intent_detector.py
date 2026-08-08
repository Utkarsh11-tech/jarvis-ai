INTENT_MAP = {
    "open": "OPEN_APPLICATION",
    "launch": "OPEN_APPLICATION",
    "start": "OPEN_APPLICATION",

    "play": "PLAY_MEDIA",

    "shutdown": "SYSTEM_COMMAND",
    "restart": "SYSTEM_COMMAND",

    "search": "WEB_SEARCH",
    "find": "WEB_SEARCH",
}


def detect_intent(action):
    """
    Detects the user's intent based on the action word.
    """

    return INTENT_MAP.get(action, "UNKNOWN") 