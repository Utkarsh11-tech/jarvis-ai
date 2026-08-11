from PySide6.QtCore import QObject

from brain.core.assistant import (
    Assistant as BaseAssistant,
    extract_chrome_profile_command,
)
from brain.core.conversation_manager import (
    ConversationManager,
    ConversationState,
)
from brain.core.executor import execute, get_acknowledgement
from brain.core.normalizer import normalize
from brain.core.state import JarvisState
from brain.voices.voice_manager import speak


class Assistant(BaseAssistant):
    """
    Day 8 conversational Assistant.

    Extends the existing Assistant without removing any of its current
    command execution capabilities. Pending user interactions are managed by
    ConversationManager instead of adding a new feature-specific state flag.
    """

    def __init__(self, bridge):
        super().__init__(bridge)
        self.conversation = ConversationManager()

    # ==================================================
    # MEDIA COMMAND CLEANUP
    # ==================================================

    def clean_media_command(self, command):
        """
        Normalizes a media command without removing the platform suffix.

        The base implementation strips phrases such as "on youtube music".
        That is incorrect for the conversational Chrome flow because the
        executor uses that phrase to decide between YouTube and YouTube Music.
        """

        return normalize(command).strip()

    # ==================================================
    # CONVERSATION-AWARE COMMAND HANDLER
    # ==================================================

    def handle_command(self, command):
        """Routes wake words, pending responses, and normal commands."""

        if not command:
            return

        # ------------------------------------------
        # WAKE WORD
        # ------------------------------------------

        if self.is_wake_word(command):
            self.handle_wake_word()
            return

        # ------------------------------------------
        # PENDING CONVERSATION
        # ------------------------------------------

        if self.conversation.is_waiting_for("chrome_profile"):
            self._handle_chrome_profile_response(command)
            return

        # ------------------------------------------
        # DIRECTED CHROME PROFILE COMMAND
        # ------------------------------------------

        profile_name, remaining_command = extract_chrome_profile_command(command)

        if profile_name:
            self.handle_directed_chrome_command(
                profile_name,
                remaining_command,
            )
            return

        # ------------------------------------------
        # NORMAL COMMAND
        # ------------------------------------------

        self.state_manager.set_state(JarvisState.THINKING)

        results = self.process_command(command)

        if not results:
            self.state_manager.set_state(JarvisState.IDLE)
            return

        for result in results:
            self.state_manager.set_state(JarvisState.SPEAKING)

            acknowledgement = get_acknowledgement(result)

            print(acknowledgement)
            speak(acknowledgement)

            if (
                result["intent"] == "OPEN_APPLICATION"
                and result["target"] == "chrome"
            ):
                self.conversation.start(
                    kind="chrome_profile",
                    state=ConversationState.WAITING_FOR_SELECTION,
                    prompt="Please choose a Chrome profile.",
                    metadata={
                        "intent": result["intent"],
                        "target": result["target"],
                    },
                )

                self.request_chrome_profile()
                return

            self.state_manager.set_state(JarvisState.EXECUTING)

            response = execute(result)

            print(response)
            self.bridge.send_response(response)

            self.context.remember(
                intent=result["intent"],
                target=result["target"],
                response=response,
            )

        self.state_manager.set_state(JarvisState.IDLE)

    # ==================================================
    # CHROME PROFILE RESPONSE
    # ==================================================

    def _handle_chrome_profile_response(self, response):
        """Resolves a response belonging to the pending Chrome selection."""

        self.state_manager.set_state(JarvisState.THINKING)

        self.handle_chrome_profile_response(response)

        if self.awaiting_chrome_profile:
            self.conversation.record_attempt()
            return

        self.conversation.clear()

    # ==================================================
    # GUI PROFILE SELECTION
    # ==================================================

    def handle_profile_selected(self, profile_directory):
        """Completes a pending interaction selected through the GUI."""

        self.conversation.clear()
        super().handle_profile_selected(profile_directory)

    # ==================================================
    # CONVERSATION HELPERS
    # ==================================================

    def is_waiting_for_user(self):
        """Returns whether JARVIS is currently waiting for a response."""

        return self.conversation.is_waiting()

    def get_pending_interaction(self):
        """Returns the active pending interaction, if one exists."""

        return self.conversation.get_pending()
