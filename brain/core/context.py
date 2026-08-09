# ==========================================
# JARVIS CONTEXT MANAGER
# ==========================================


class ContextManager:
    """
    Stores short-term conversational context
    for JARVIS.
    """

    def __init__(self):
        """
        Initializes the context.
        """

        self.last_target = ""
        self.last_intent = ""
        self.last_response = ""

    # ==========================================
    # REMEMBER
    # ==========================================

    def remember(
        self,
        intent="",
        target="",
        response="",
    ):
        """
        Stores information about the most
        recent meaningful command.
        """

        if target:
            self.last_target = target

        if intent:
            self.last_intent = intent

        if response:
            self.last_response = response

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
        """

        if not target:
            return target

        reference_words = {
            "it",
            "that",
            "this",
            "them",
        }

        words = target.split()

        if not words:
            return target

        # ------------------------------------------
        # Target is only a reference
        # ------------------------------------------

        if len(words) == 1:

            if words[0] in reference_words:

                if self.last_target:

                    return self.last_target

        return target

    # ==========================================
    # GET LAST TARGET
    # ==========================================

    def get_last_target(self):
        """
        Returns the most recently remembered target.
        """

        return self.last_target

    # ==========================================
    # GET LAST INTENT
    # ==========================================

    def get_last_intent(self):
        """
        Returns the most recently remembered intent.
        """

        return self.last_intent

    # ==========================================
    # GET LAST RESPONSE
    # ==========================================

    def get_last_response(self):
        """
        Returns the most recently remembered response.
        """

        return self.last_response

    # ==========================================
    # CLEAR
    # ==========================================

    def clear(self):
        """
        Clears the current conversational context.
        """

        self.last_target = ""
        self.last_intent = ""
        self.last_response = ""
