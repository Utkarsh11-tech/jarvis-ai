class ConversationMemory:
    """
    Lightweight in-memory conversation history for JARVIS.

    Stores recent user and assistant messages so the LLM
    can maintain conversational context.
    """

    DEFAULT_MAX_MESSAGES = 20

    def __init__(self, max_messages=None):
        self.max_messages = (
            max_messages if max_messages is not None else self.DEFAULT_MAX_MESSAGES
        )

        self._messages = []

    # ==================================================
    # ADD MESSAGE
    # ==================================================

    def add_message(self, role, content):
        """
        Adds a message to the conversation history.

        Supported roles:
        - user
        - assistant
        - system
        """

        if not role or not content:
            return

        message = {
            "role": str(role),
            "content": str(content).strip(),
        }

        if not message["content"]:
            return

        self._messages.append(message)

        self._trim()

    # ==================================================
    # USER MESSAGE
    # ==================================================

    def add_user_message(self, content):
        """Adds a user message."""

        self.add_message(
            role="user",
            content=content,
        )

    # ==================================================
    # ASSISTANT MESSAGE
    # ==================================================

    def add_assistant_message(self, content):
        """Adds a JARVIS response."""

        self.add_message(
            role="assistant",
            content=content,
        )

    # ==================================================
    # SYSTEM MESSAGE
    # ==================================================

    def add_system_message(self, content):
        """Adds a system-level instruction."""

        self.add_message(
            role="system",
            content=content,
        )

    # ==================================================
    # HISTORY
    # ==================================================

    def get_messages(self):
        """
        Returns a copy of the current conversation history.

        A copy is returned so callers cannot accidentally
        modify the internal history.
        """

        return [dict(message) for message in self._messages]

    # ==================================================
    # RECENT HISTORY
    # ==================================================

    def get_recent_messages(self, count=None):
        """
        Returns the most recent messages.

        If count is None, returns the complete current
        history.
        """

        if count is None:
            return self.get_messages()

        if count <= 0:
            return []

        return [dict(message) for message in self._messages[-count:]]

    # ==================================================
    # MESSAGE COUNT
    # ==================================================

    def get_message_count(self):
        """Returns the number of stored messages."""

        return len(self._messages)

    # ==================================================
    # CLEAR
    # ==================================================

    def clear(self):
        """Clears the entire conversation history."""

        self._messages.clear()

    # ==================================================
    # TRIM
    # ==================================================

    def _trim(self):
        """
        Keeps only the configured number of recent
        messages.
        """

        if self.max_messages <= 0:
            self._messages.clear()
            return

        if len(self._messages) > self.max_messages:

            self._messages = self._messages[-self.max_messages :]
