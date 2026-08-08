INTENT_MAP = {
    "open": "OPEN_APPLICATION",
    "launch": "OPEN_APPLICATION",
    "start": "OPEN_APPLICATION",

    "play": "PLAY_MEDIA",

    "shutdown": "SYSTEM_COMMAND",
    "restart": "SYSTEM_COMMAND",

    "search": "WEB_SEARCH",
}


def detect_intent(action, target=""):
    """
    Detects the user's intent based on the action
    and the target.
    """

    if action == "find":
        if target:
            return "FILE_SEARCH"

        return "WEB_SEARCH"

    return INTENT_MAP.get(action, "UNKNOWN")