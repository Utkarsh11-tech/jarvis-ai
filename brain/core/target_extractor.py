# ==========================================
# TARGET EXTRACTOR
# ==========================================


TARGET_PREFIXES = {
    "for",
    "about",
    "on",
    "regarding",
    "to",
    "up",
}


def extract_target(words):
    """
    Extracts the meaningful target from a command.

    Removes the action word and optional
    structural words used in natural language.
    """

    if not words or len(words) <= 1:
        return ""

    # ==========================================
    # REMOVE ACTION
    # ==========================================

    target_words = words[1:]

    # ==========================================
    # REMOVE STRUCTURAL PREFIX
    # ==========================================

    if target_words:

        if target_words[0] in TARGET_PREFIXES:

            target_words = target_words[1:]

    # ==========================================
    # REMOVE COMMON MEDIA PHRASES
    # ==========================================

    if len(target_words) >= 2:

        if target_words[0] == "the" and target_words[1] in {
            "song",
            "music",
            "track",
            "video",
        }:

            target_words = target_words[2:]

    # ==========================================
    # RETURN TARGET
    # ==========================================

    return " ".join(target_words).strip()
