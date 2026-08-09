INTENT_MAP = {
    # ==========================================
    # APPLICATIONS
    # ==========================================
    "open": "OPEN_APPLICATION",
    "launch": "OPEN_APPLICATION",
    "start": "OPEN_APPLICATION",
    "run": "OPEN_APPLICATION",
    "load": "OPEN_APPLICATION",
    # ==========================================
    # MEDIA
    # ==========================================
    "play": "PLAY_MEDIA",
    # ==========================================
    # SYSTEM
    # ==========================================
    "shutdown": "SYSTEM_COMMAND",
    "restart": "SYSTEM_COMMAND",
    "reboot": "SYSTEM_COMMAND",
    # ==========================================
    # WEB
    # ==========================================
    "search": "WEB_SEARCH",
    "google": "WEB_SEARCH",
    "browse": "WEB_SEARCH",
}


def detect_intent(action, target=""):
    """
    Detects the user's intent based on
    the action and target.
    """

    action = action.lower().strip()

    # ==========================================
    # FILE SEARCH
    # ==========================================

    if action in {
        "find",
        "locate",
    }:

        if target:
            return "FILE_SEARCH"

        return "WEB_SEARCH"

    # ==========================================
    # WEB LOOKUP
    # ==========================================

    if action in {
        "lookup",
    }:

        return "WEB_SEARCH"

    # ==========================================
    # INTENT MAP
    # ==========================================

    return INTENT_MAP.get(action, "UNKNOWN")
