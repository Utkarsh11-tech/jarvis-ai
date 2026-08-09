# ==========================================
# INTENT DETECTOR
# ==========================================


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
    "listen": "PLAY_MEDIA",
    "put": "PLAY_MEDIA",
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
    "lookup": "WEB_SEARCH",
    "look": "WEB_SEARCH",
    # ==========================================
    # UI AUTOMATION
    # ==========================================
    "automate": "UI_AUTOMATION",
    "automation": "UI_AUTOMATION",
}


def detect_intent(action, target=""):
    """
    Detects the user's intent based on
    the action and target.
    """

    action = action.lower().strip()
    target = target.lower().strip()

    # ==========================================
    # UI AUTOMATION
    # ==========================================

    if action in {
        "automate",
        "automation",
    }:

        return "UI_AUTOMATION"

    # ==========================================
    # AUTOMATION TEST
    # ==========================================

    if action == "run" and target in {
        "automation test",
        "the automation test",
        "ui automation test",
        "the ui automation test",
    }:

        return "UI_AUTOMATION"

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
    # INTENT MAP
    # ==========================================

    return INTENT_MAP.get(
        action,
        "UNKNOWN",
    )
