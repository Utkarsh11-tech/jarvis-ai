import ctypes

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
    Day 9 conversational Assistant.

    Extends the existing Assistant without removing any of its current
    command execution capabilities. Pending user interactions are managed by
    ConversationManager instead of adding feature-specific state flags.
    """

    def __init__(self, bridge):
        super().__init__(bridge)
        self.conversation = ConversationManager()

    # ==================================================
    # MEDIA COMMAND CLEANUP
    # ==================================================

    def clean_media_command(self, command):
        """Normalizes a media command without removing platform suffixes."""
        return normalize(command).strip()

    # ==================================================
    # STOP PLAYBACK
    # ==================================================

    def _handle_stop_command(self, command):
        """Stops active media using the Windows media-stop key."""
        normalized = normalize(command).strip()

        if normalized not in {
            "stop",
            "stop playing",
            "stop the music",
            "stop the song",
            "stop the video",
        }:
            return False

        self.state_manager.set_state(JarvisState.EXECUTING)

        try:
            ctypes.windll.user32.keybd_event(0xB2, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xB2, 0, 2, 0)
            response = "Playback stopped."
        except Exception as error:
            print(f"JARVIS: Could not stop playback: {error}")
            response = "I couldn't stop playback."

        print(response)
        speak(response)
        self.bridge.send_response(response)
        self.state_manager.set_state(JarvisState.IDLE)
        return True

    # ==================================================
    # GENERIC CONFIRMATION HANDLING
    # ==================================================

    @staticmethod
    def _parse_confirmation(command):
        """Returns True/False for clear confirmation answers, otherwise None."""
        normalized = normalize(command).strip().lower()

        yes = {
            "yes",
            "yeah",
            "yep",
            "yup",
            "sure",
            "confirm",
            "confirmed",
            "do it",
        }
        no = {
            "no",
            "nope",
            "nah",
            "cancel",
            "cancel it",
            "don't",
            "do not",
        }

        if normalized in yes:
            return True
        if normalized in no:
            return False
        return None

    def request_confirmation(
        self,
        action,
        prompt,
        cancel_response="Cancelled.",
        action_data=None,
    ):
        """
        Starts a reusable confirmation interaction.

        `action` identifies what should happen after confirmation and
        `action_data` contains any data needed by that action. This keeps
        confirmation state independent from the command being confirmed.
        """
        self.conversation.start(
            kind="confirmation",
            state=ConversationState.WAITING_FOR_CONFIRMATION,
            prompt=prompt,
            metadata={
                "action": action,
                "action_data": dict(action_data or {}),
                "cancel_response": cancel_response,
            },
        )

        print(f"JARVIS: {prompt}")
        speak(prompt)
        self.bridge.send_response(prompt)
        return True

    def _execute_confirmed_action(self, action, action_data):
        """
        Executes a confirmed action through one centralized dispatcher.

        Add future confirmed actions here without changing the generic
        confirmation conversation flow.
        """
        if action == "shutdown":
            return execute({"intent": "SYSTEM", "target": "shutdown"})

        return None

    def _handle_confirmation_response(self, command):
        """Resolves a pending confirmation without executing ambiguous actions."""
        pending = self.conversation.get_pending()
        if pending is None or pending.state != ConversationState.WAITING_FOR_CONFIRMATION:
            return False

        answer = self._parse_confirmation(command)

        if answer is None:
            pending.attempts += 1
            message = "Please answer yes or no."
            print(f"JARVIS: {message}")
            speak(message)
            self.bridge.send_response(message)
            return True

        action = pending.metadata.get("action")
        action_data = pending.metadata.get("action_data", {})
        cancel_response = pending.metadata.get("cancel_response", "Cancelled.")
        self.conversation.clear()

        if not answer:
            print(f"JARVIS: {cancel_response}")
            speak(cancel_response)
            self.bridge.send_response(cancel_response)
            self.state_manager.set_state(JarvisState.IDLE)
            return True

        self.state_manager.set_state(JarvisState.EXECUTING)
        response = self._execute_confirmed_action(action, action_data)

        if response is None:
            response = "I couldn't complete that confirmed action."

        print(f"JARVIS: {response}")
        speak(response)
        self.bridge.send_response(response)
        self.state_manager.set_state(JarvisState.IDLE)
        return True

    def _start_shutdown_confirmation(self):
        """Starts the reusable confirmation flow for shutdown."""
        return self.request_confirmation(
            action="shutdown",
            prompt="Are you sure you want to shut down the computer?",
            cancel_response="Shutdown cancelled.",
        )

    # ==================================================
    # CONVERSATION-AWARE COMMAND HANDLER
    # ==================================================

    def handle_command(self, command):
        """Routes wake words, pending responses, and normal commands."""
        if not command:
            return

        if self.is_wake_word(command):
            self.handle_wake_word()
            return

        if self._handle_stop_command(command):
            return

        # A pending confirmation takes priority over normal intent parsing.
        if self.conversation.is_waiting_for("confirmation"):
            self._handle_confirmation_response(command)
            return

        if self.conversation.is_waiting_for("chrome_profile"):
            self._handle_chrome_profile_response(command)
            return

        # Start confirmation before executor's legacy interactive input().
        normalized = normalize(command).strip().lower()
        if normalized in {
            "shutdown",
            "shut down",
            "turn off the computer",
            "turn off computer",
        }:
            self.state_manager.set_state(JarvisState.THINKING)
            self._start_shutdown_confirmation()
            return

        profile_name, remaining_command = extract_chrome_profile_command(command)
        if profile_name:
            self.handle_directed_chrome_command(profile_name, remaining_command)
            return

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

            if result["intent"] == "OPEN_APPLICATION" and result["target"] == "chrome":
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
