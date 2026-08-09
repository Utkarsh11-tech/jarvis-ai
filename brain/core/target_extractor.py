# ==========================================
# TARGET EXTRACTOR
# ==========================================


TARGET_PREFIXES = {
    "for",
    "about",
    "on",
    "regarding",
}


def extract_target(words):
    """
    Extracts the meaningful target from a command.

    Removes the action word and optional
    structural words such as 'for' or 'about'.
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
    # RETURN TARGET
    # ==========================================

    return " ".join(target_words).strip()
