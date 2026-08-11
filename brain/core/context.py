# ==========================================
# JARVIS CONTEXT MANAGER
# ==========================================


class ContextManager:
    """
    Stores short-term conversational context
    for JARVIS.
    """

    def __init__(self):
        self.last_target = ""
        self.last_intent = ""
        self.last_response = ""
        self.last_profile_directory = ""
        self.last_profile_name = ""

    # ==========================================
    # REMEMBER
    # ==========================================

    def remember(
        self,
        intent="",
        target="",
        response="",
        profile_directory="",
        profile_name="",
    ):
        """Stores the most recent meaningful conversational context."""

        if target:
            self.last_target = target

        if intent:
            self.last_intent = intent

        if response:
            self.last_response = response

        if profile_directory:
            self.last_profile_directory = profile_directory

        if profile_name:
            self.last_profile_name = profile_name

    # ==========================================
    # RESOLVE REFERENCE
    # ==========================================

    def resolve_reference(self, target):
        """
        Resolves conversational references such as:

        it
        that
        this
        them
        it again
        that again
        once more
        """

        if not target:
            return target

        words = target.split()

        if not words:
            return target

        # "again" and "once more" describe the previous action rather
        # than being part of the media/file target itself.
        while words and words[-1] in {"again", "once", "more"}:
            words.pop()

        if words[-2:] == ["once", "more"]:
            words = words[:-2]

        if not words:
            return self.last_target

        reference_words = {"it", "that", "this", "them"}

        if len(words) == 1 and words[0] in reference_words:
            return self.last_target or target

        # Handle phrases such as "it again" after removing the modifier.
        if words[0] in reference_words and self.last_target:
            return " ".join([self.last_target, *words[1:]]).strip()

        return " ".join(words).strip()

    # ==========================================
    # GET LAST CONTEXT
    # ==========================================

    def get_last_target(self):
        return self.last_target

    def get_last_intent(self):
        return self.last_intent

    def get_last_response(self):
        return self.last_response

    def get_last_profile_directory(self):
        return self.last_profile_directory

    def get_last_profile_name(self):
        return self.last_profile_name

    # ==========================================
    # CLEAR
    # ==========================================

    def clear(self):
        """Clears the current conversational context."""
        self.last_target = ""
        self.last_intent = ""
        self.last_response = ""
        self.last_profile_directory = ""
        self.last_profile_name = ""
