import ctypes
import subprocess

from PySide6.QtCore import QTimer

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
from brain.memory.conversation_memory import ConversationMemory
from brain.models.ollama_client import OllamaClient
from brain.voices.voice_manager import speak
from brain.config.llm_config import JARVIS_SYSTEM_PROMPT


class Assistant(BaseAssistant):
    """
    Canonical conversational Assistant used by main.py.

    Extends the stable command-processing Assistant with:
    - wake word handling
    - text-mode wake timeout
    - sleeping-state command protection
    - confirmation handling
    - Chrome profile conversations
    - contextual follow-ups
    - stop playback
    - Ollama / Qwen conversational fallback
    - LLM conversation memory
    """

    # ==================================================
    # TEXT CONVERSATION CONFIGURATION
    # ==================================================

    # Time JARVIS waits for a command after the
    # text-based wake word.
    WAKE_COMMAND_TIMEOUT = 5000  # milliseconds

    def __init__(self, bridge):
        super().__init__(bridge)

        # ==================================================
        # LLM
        # ==================================================

        self.ollama = OllamaClient()

        # ==================================================
        # LLM CONVERSATION MEMORY
        # ==================================================

        self.llm_memory = ConversationMemory(max_messages=20)

        # ==================================================
        # CONVERSATION
        # ==================================================

        self.conversation = ConversationManager()

        # ==================================================
        # TEXT WAKE TIMEOUT
        # ==================================================

        self.wake_timeout_timer = QTimer(self)

        self.wake_timeout_timer.setSingleShot(True)

        self.wake_timeout_timer.timeout.connect(self._handle_wake_timeout)

    # ==================================================
    # TEXT WAKE TIMEOUT
    # ==================================================

    def _start_wake_timeout(self):
        """
        Starts the timeout for the text-based wake state.

        If the user wakes JARVIS but does not provide a
        command within the configured time, JARVIS returns
        to the sleeping state.
        """

        self.wake_timeout_timer.stop()

        self.wake_timeout_timer.start(self.WAKE_COMMAND_TIMEOUT)

        print(
            "JARVIS: Waiting for command "
            f"({self.WAKE_COMMAND_TIMEOUT / 1000:.0f}s timeout)..."
        )

    def _stop_wake_timeout(self):
        """
        Stops the active wake-command timeout.
        """

        if self.wake_timeout_timer.isActive():
            self.wake_timeout_timer.stop()

    def _handle_wake_timeout(self):
        """
        Handles the situation where JARVIS was awakened
        but received no command.
        """

        print("JARVIS: No command received.")

        # ==========================================
        # EXIT LISTENING
        # ==========================================

        self.state_manager.set_state(JarvisState.IDLE)

        # ==========================================
        # RETURN TO SLEEPING
        # ==========================================

        self.state_manager.set_state(JarvisState.SLEEPING)

        print("JARVIS: Returning to sleep.")

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

        self._stop_wake_timeout()

        self.state_manager.set_state(JarvisState.EXECUTING)

        try:

            ctypes.windll.user32.keybd_event(
                0xB2,
                0,
                0,
                0,
            )

            ctypes.windll.user32.keybd_event(
                0xB2,
                0,
                2,
                0,
            )

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
        """
        Returns True/False for clear confirmation answers,
        otherwise None.
        """

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
        """Starts a reusable confirmation interaction."""

        self._stop_wake_timeout()

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

    def _execute_confirmed_action(
        self,
        action,
        action_data,
    ):
        """
        Executes an already-confirmed system action.
        """

        if action == "shutdown":

            try:

                subprocess.Popen(
                    [
                        "shutdown",
                        "/s",
                        "/t",
                        "5",
                    ]
                )

                return "Shutting down the computer " "in 5 seconds."

            except OSError:

                return "I couldn't shut down the computer."

        if action == "restart":

            try:

                subprocess.Popen(
                    [
                        "shutdown",
                        "/r",
                        "/t",
                        "5",
                    ]
                )

                return "Restarting the computer " "in 5 seconds."

            except OSError:

                return "I couldn't restart the computer."

        return None

    def _handle_confirmation_response(
        self,
        command,
    ):
        """
        Resolves a pending confirmation without
        executing ambiguous actions.
        """

        pending = self.conversation.get_pending()

        if (
            pending is None
            or pending.state != ConversationState.WAITING_FOR_CONFIRMATION
        ):
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

        action_data = pending.metadata.get(
            "action_data",
            {},
        )

        cancel_response = pending.metadata.get(
            "cancel_response",
            "Cancelled.",
        )

        self.conversation.clear()

        if not answer:

            print(f"JARVIS: {cancel_response}")

            speak(cancel_response)

            self.bridge.send_response(cancel_response)

            self.state_manager.set_state(JarvisState.IDLE)

            return True

        self.state_manager.set_state(JarvisState.EXECUTING)

        response = self._execute_confirmed_action(
            action,
            action_data,
        )

        if response is None:

            response = "I couldn't complete that " "confirmed action."

        print(f"JARVIS: {response}")

        speak(response)

        self.bridge.send_response(response)

        self.state_manager.set_state(JarvisState.IDLE)

        return True

    def _start_system_confirmation(
        self,
        target,
    ):
        prompts = {
            "shutdown": (
                "Are you sure you want to shut down the computer?",
                "Shutdown cancelled.",
            ),
            "restart": (
                "Are you sure you want to restart the computer?",
                "Restart cancelled.",
            ),
        }

        prompt, cancel_response = prompts[target]

        return self.request_confirmation(
            action=target,
            prompt=prompt,
            cancel_response=cancel_response,
        )

    # ==================================================
    # CONTEXTUAL PROFILE HELPERS
    # ==================================================

    def _find_profile_selection(
        self,
        response,
    ):
        """
        Resolves a spoken/typed Chrome profile
        selection from the current list.
        """

        response = normalize(response).strip().lower()

        profiles = list(self.chrome_profiles.items())

        number_words = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        }

        number = None

        for word in response.split():

            if word.isdigit():

                number = int(word)

                break

            if word in number_words:

                number = number_words[word]

                break

        if number is not None and 1 <= number <= len(profiles):

            return profiles[number - 1]

        for (
            profile_directory,
            profile_data,
        ) in profiles:

            name = profile_data.get("name", "").lower().strip()

            if response == name or response in name or name in response:

                return (
                    profile_directory,
                    profile_data,
                )

        return None

    def _remember_profile(
        self,
        profile_directory,
        profile_name="",
    ):
        """
        Stores the selected Chrome profile
        without replacing media context.
        """

        self.context.remember(
            profile_directory=profile_directory,
            profile_name=profile_name,
        )

    def handle_directed_chrome_command(
        self,
        profile_name,
        remaining_command,
    ):
        """
        Preserves the selected profile for later
        conversational follow-ups.
        """

        selected_profile = self.resolve_chrome_profile(profile_name)

        super().handle_directed_chrome_command(
            profile_name,
            remaining_command,
        )

        if selected_profile is not None:

            (
                profile_directory,
                profile_data,
            ) = selected_profile

            self._remember_profile(
                profile_directory,
                profile_data.get(
                    "name",
                    profile_name,
                ),
            )

    # ==================================================
    # OLLAMA / QWEN COMMAND HANDLER
    # ==================================================

    def _handle_llm_command(self, command):
        """
        Sends an unhandled conversational command
        to Qwen using the recent LLM conversation
        history.
        """

        if not command:
            return False

        print(f"JARVIS: Sending to Qwen: {command}")

        self.state_manager.set_state(JarvisState.THINKING)

        # ==================================================
        # GET PREVIOUS CONVERSATION
        # ==================================================

        history = self.llm_memory.get_messages()

        # ==================================================
        # SEND CURRENT COMMAND + HISTORY TO QWEN
        # ==================================================

        try:

            response = self.ollama.generate(
                prompt=command,
                system_prompt=JARVIS_SYSTEM_PROMPT,
                history=history,
            )

        except RuntimeError as error:

            print(f"JARVIS: Ollama error: {error}")

            response = "I'm unable to reach my " "language model right now."

            self.state_manager.set_state(JarvisState.SPEAKING)

            speak(response)

            self.bridge.send_response(response)

            self.state_manager.set_state(JarvisState.IDLE)

            return True

        # ==================================================
        # VALIDATE RESPONSE
        # ==================================================

        if not response:

            response = "I didn't receive a response " "from the language model."

            self.state_manager.set_state(JarvisState.SPEAKING)

            speak(response)

            self.bridge.send_response(response)

            self.state_manager.set_state(JarvisState.IDLE)

            return True

        # ==================================================
        # STORE SUCCESSFUL CONVERSATION
        # ==================================================

        self.llm_memory.add_user_message(command)

        self.llm_memory.add_assistant_message(response)

        # ==================================================
        # LOG RESPONSE
        # ==================================================

        print(f"JARVIS: Qwen response: {response}")

        # ==================================================
        # SPEAKING
        # ==================================================

        self.state_manager.set_state(JarvisState.SPEAKING)

        speak(response)

        self.bridge.send_response(response)

        # ==================================================
        # RETURN TO IDLE
        # ==================================================

        self.state_manager.set_state(JarvisState.IDLE)

        return True

    # ==================================================
    # CONVERSATION-AWARE COMMAND HANDLER
    # ==================================================

    def handle_command(self, command):
        """
        Routes wake words, pending responses,
        contextual commands, normal commands,
        and unhandled commands to Qwen.

        IMPORTANT:
        If JARVIS is SLEEPING, normal commands are
        ignored until the wake word is received.
        """

        if not command:
            return

        # ==========================================
        # WAKE WORD
        # ==========================================

        if self.is_wake_word(command):

            self.handle_wake_word()

            self._start_wake_timeout()

            return

        # ==========================================
        # SLEEPING STATE GATE
        # ==========================================

        current_state = self.state_manager.get_state()

        if current_state == JarvisState.SLEEPING:

            print("JARVIS: Ignoring command because " "JARVIS is sleeping.")

            return

        # ==========================================
        # REAL COMMAND RECEIVED
        # ==========================================

        self._stop_wake_timeout()

        # ==========================================
        # STOP COMMAND
        # ==========================================

        if self._handle_stop_command(command):

            return

        # ==========================================
        # CONFIRMATION RESPONSE
        # ==========================================

        if self.conversation.is_waiting_for("confirmation"):

            self._handle_confirmation_response(command)

            return

        # ==========================================
        # CHROME PROFILE RESPONSE
        # ==========================================

        if self.conversation.is_waiting_for("chrome_profile"):

            self._handle_chrome_profile_response(command)

            return

        # ==========================================
        # SYSTEM COMMANDS
        # ==========================================

        normalized = normalize(command).strip().lower()

        system_targets = {
            "shutdown": "shutdown",
            "shut down": "shutdown",
            "turn off the computer": "shutdown",
            "turn off computer": "shutdown",
            "restart": "restart",
            "reboot": "restart",
        }

        if normalized in system_targets:

            self.state_manager.set_state(JarvisState.THINKING)

            self._start_system_confirmation(system_targets[normalized])

            return

        # ==========================================
        # DIRECTED CHROME COMMAND
        # ==========================================

        (
            profile_name,
            remaining_command,
        ) = extract_chrome_profile_command(command)

        if profile_name:

            self.handle_directed_chrome_command(
                profile_name,
                remaining_command,
            )

            return

        # ==========================================
        # NORMAL COMMAND
        # ==========================================

        self.state_manager.set_state(JarvisState.THINKING)

        results = self.process_command(command)

        # ==========================================
        # LLM FALLBACK
        # ==========================================

        if not results:

            self._handle_llm_command(command)

            return

        for result in results:

            # --------------------------------------
            # CHROME PROFILE
            # --------------------------------------

            if result["intent"] == "OPEN_APPLICATION" and result["target"] == "chrome":

                self.state_manager.set_state(JarvisState.SPEAKING)

                self.conversation.start(
                    kind="chrome_profile",
                    state=(ConversationState.WAITING_FOR_SELECTION),
                    prompt=("Please choose a Chrome profile."),
                    metadata={
                        "intent": result["intent"],
                        "target": result["target"],
                    },
                )

                self.request_chrome_profile()

                return

            # --------------------------------------
            # SPEAKING
            # --------------------------------------

            self.state_manager.set_state(JarvisState.SPEAKING)

            acknowledgement = get_acknowledgement(result)

            print(acknowledgement)

            speak(acknowledgement)

            # --------------------------------------
            # PROFILE CONTEXT
            # --------------------------------------

            if (
                result["intent"] == "PLAY_MEDIA"
                and not result.get("profile_directory")
                and self.context.get_last_profile_directory()
            ):

                result["profile_directory"] = self.context.get_last_profile_directory()

            # --------------------------------------
            # EXECUTING
            # --------------------------------------

            self.state_manager.set_state(JarvisState.EXECUTING)

            response = execute(result)

            print(response)

            self.bridge.send_response(response)

            # --------------------------------------
            # UPDATE CONTEXT
            # --------------------------------------

            self.context.remember(
                intent=result["intent"],
                target=result["target"],
                response=response,
            )

        # ==========================================
        # RETURN TO IDLE
        # ==========================================

        self.state_manager.set_state(JarvisState.IDLE)

    # ==================================================
    # CHROME PROFILE RESPONSE
    # ==================================================

    def _handle_chrome_profile_response(
        self,
        response,
    ):
        """
        Resolves a profile and stores it for
        later follow-up commands.
        """

        selected_profile = self._find_profile_selection(response)

        self.state_manager.set_state(JarvisState.THINKING)

        self.handle_chrome_profile_response(response)

        if self.awaiting_chrome_profile:

            self.conversation.record_attempt()

            return

        if selected_profile is not None:

            (
                profile_directory,
                profile_data,
            ) = selected_profile

            self._remember_profile(
                profile_directory,
                profile_data.get(
                    "name",
                    "",
                ),
            )

        self.conversation.clear()

    # ==================================================
    # GUI PROFILE SELECTION
    # ==================================================

    def handle_profile_selected(
        self,
        profile_directory,
    ):
        """
        Completes a GUI Chrome profile selection
        and stores it for follow-ups.
        """

        profile_name = ""

        for (
            directory,
            profile_data,
        ) in self.chrome_profiles.items():

            if directory == profile_directory:

                profile_name = profile_data.get(
                    "name",
                    "",
                )

                break

        self.conversation.clear()

        super().handle_profile_selected(profile_directory)

        self._remember_profile(
            profile_directory,
            profile_name,
        )

    # ==================================================
    # CONVERSATION HELPERS
    # ==================================================

    def is_waiting_for_user(self):

        return self.conversation.is_waiting()

    def get_pending_interaction(self):

        return self.conversation.get_pending()
