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

# ==========================================================
# TOOL CAPABILITY LAYER
# ==========================================================

from brain.tools.registry import (
    ToolRegistry,
    get_default_registry,
)

from brain.tools.capabilities import (
    build_capability_document,
)


class Assistant(BaseAssistant):
    """Canonical conversational Assistant used by main.py."""

    WAKE_COMMAND_TIMEOUT = 5000

    def __init__(self, bridge):
        super().__init__(bridge)

        # ==================================================
        # LLM
        # ==================================================

        self.ollama = OllamaClient()

        self.llm_memory = ConversationMemory(max_messages=20)

        # ==================================================
        # CONVERSATION STATE
        # ==================================================

        self.conversation = ConversationManager()

        # ==================================================
        # TOOL CAPABILITY REGISTRY
        # ==================================================

        self.tool_registry = get_default_registry()

        # ==================================================
        # WAKE TIMEOUT
        # ==================================================

        self.wake_timeout_timer = QTimer(self)

        self.wake_timeout_timer.setSingleShot(True)

        self.wake_timeout_timer.timeout.connect(self._handle_wake_timeout)

    # ======================================================
    # CAPABILITY ACCESS
    # ======================================================

    def get_capabilities(self):
        """
        Return the current JARVIS capability document.

        This is a read-only capability view.

        It does not:
            - execute a tool
            - call Ollama
            - call XTTS
            - modify the registry
            - modify conversation memory

        The returned structure is safe to pass to a future
        LLM tool-selection layer.
        """

        return build_capability_document(self.tool_registry)

    def get_tool_registry(self) -> ToolRegistry:
        """
        Return the JARVIS tool registry.

        The registry itself is kept separate from the LLM
        capability representation.
        """

        return self.tool_registry

    # ======================================================
    # WAKE TIMEOUT
    # ======================================================

    def _start_wake_timeout(self):
        self.wake_timeout_timer.stop()

        self.wake_timeout_timer.start(self.WAKE_COMMAND_TIMEOUT)

        print(
            "JARVIS: Waiting for command "
            f"({self.WAKE_COMMAND_TIMEOUT / 1000:.0f}s timeout)..."
        )

    def _stop_wake_timeout(self):
        if self.wake_timeout_timer.isActive():
            self.wake_timeout_timer.stop()

    def _handle_wake_timeout(self):
        print("JARVIS: No command received.")

        self.state_manager.set_state(JarvisState.IDLE)

        self.state_manager.set_state(JarvisState.SLEEPING)

        print("JARVIS: Returning to sleep.")

    # ======================================================
    # MEDIA
    # ======================================================

    def clean_media_command(self, command):
        return normalize(command).strip()

    # ======================================================
    # STOP COMMAND
    # ======================================================

    def _handle_stop_command(
        self,
        command,
    ):

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

    # ======================================================
    # CONFIRMATION PARSER
    # ======================================================

    @staticmethod
    def _parse_confirmation(
        command,
    ):

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

    # ======================================================
    # REQUEST CONFIRMATION
    # ======================================================

    def request_confirmation(
        self,
        action,
        prompt,
        cancel_response="Cancelled.",
        action_data=None,
    ):

        self._stop_wake_timeout()

        self.conversation.start(
            kind="confirmation",
            state=(ConversationState.WAITING_FOR_CONFIRMATION),
            prompt=prompt,
            metadata={
                "action": action,
                "action_data": dict(action_data or {}),
                "cancel_response": (cancel_response),
            },
        )

        print(f"JARVIS: {prompt}")

        speak(prompt)

        self.bridge.send_response(prompt)

        return True

    # ======================================================
    # EXECUTE CONFIRMED ACTION
    # ======================================================

    def _execute_confirmed_action(
        self,
        action,
        action_data,
    ):

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

    # ======================================================
    # CONFIRMATION RESPONSE
    # ======================================================

    def _handle_confirmation_response(
        self,
        command,
    ):

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

            response = "I couldn't complete " "that confirmed action."

        print(f"JARVIS: {response}")

        speak(response)

        self.bridge.send_response(response)

        self.state_manager.set_state(JarvisState.IDLE)

        return True

    # ======================================================
    # SYSTEM CONFIRMATION
    # ======================================================

    def _start_system_confirmation(
        self,
        target,
    ):

        prompts = {
            "shutdown": (
                "Are you sure you want to " "shut down the computer?",
                "Shutdown cancelled.",
            ),
            "restart": (
                "Are you sure you want to " "restart the computer?",
                "Restart cancelled.",
            ),
        }

        prompt, cancel_response = prompts[target]

        return self.request_confirmation(
            action=target,
            prompt=prompt,
            cancel_response=cancel_response,
        )

    # ======================================================
    # CHROME PROFILE
    # ======================================================

    def _find_profile_selection(
        self,
        response,
    ):

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

    # ======================================================
    # REMEMBER PROFILE
    # ======================================================

    def _remember_profile(
        self,
        profile_directory,
        profile_name="",
    ):

        self.context.remember(
            profile_directory=(profile_directory),
            profile_name=profile_name,
        )

    # ======================================================
    # DIRECTED CHROME COMMAND
    # ======================================================

    def handle_directed_chrome_command(
        self,
        profile_name,
        remaining_command,
    ):

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

    # ======================================================
    # LLM COMMAND
    # ======================================================

    def _handle_llm_command(
        self,
        command,
    ):

        if not command:
            return False

        print(f"JARVIS: Sending to Qwen: {command}")

        self.state_manager.set_state(JarvisState.THINKING)

        history = self.llm_memory.get_messages()

        try:

            response = self.ollama.generate(
                prompt=command,
                system_prompt=(JARVIS_SYSTEM_PROMPT),
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

        if not response:

            response = "I didn't receive a response " "from the language model."

            self.state_manager.set_state(JarvisState.SPEAKING)

            speak(response)

            self.bridge.send_response(response)

            self.state_manager.set_state(JarvisState.IDLE)

            return True

        self.llm_memory.add_user_message(command)

        self.llm_memory.add_assistant_message(response)

        print(f"JARVIS: Qwen response: {response}")

        self.state_manager.set_state(JarvisState.SPEAKING)

        speak(response)

        self.bridge.send_response(response)

        self.state_manager.set_state(JarvisState.IDLE)

        return True

    # ======================================================
    # MAIN COMMAND HANDLER
    # ======================================================

    def handle_command(
        self,
        command,
    ):

        if not command:
            return

        if self.is_wake_word(command):

            self.handle_wake_word()

            self._start_wake_timeout()

            return

        current_state = self.state_manager.get_state()

        if current_state == JarvisState.SLEEPING:

            print("JARVIS: Ignoring command " "because JARVIS is sleeping.")

            return

        self._stop_wake_timeout()

        if self._handle_stop_command(command):

            return

        if self.conversation.is_waiting_for("confirmation"):

            self._handle_confirmation_response(command)

            return

        if self.conversation.is_waiting_for("chrome_profile"):

            self._handle_chrome_profile_response(command)

            return

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

        self.state_manager.set_state(JarvisState.THINKING)

        results = self.process_command(command)

        # IMPORTANT:
        # process_command() returns UNKNOWN for
        # unsupported/conversational commands.

        if not results or all(result.get("intent") == "UNKNOWN" for result in results):

            self._handle_llm_command(command)

            return

        for result in results:

            if result["intent"] == "UNKNOWN":

                self._handle_llm_command(command)

                return

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

            self.state_manager.set_state(JarvisState.SPEAKING)

            acknowledgement = get_acknowledgement(result)

            print(acknowledgement)

            speak(acknowledgement)

            if (
                result["intent"] == "PLAY_MEDIA"
                and not result.get("profile_directory")
                and self.context.get_last_profile_directory()
            ):

                result["profile_directory"] = self.context.get_last_profile_directory()

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

    # ======================================================
    # CHROME PROFILE RESPONSE
    # ======================================================

    def _handle_chrome_profile_response(
        self,
        response,
    ):

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

    # ======================================================
    # PROFILE SELECTED
    # ======================================================

    def handle_profile_selected(
        self,
        profile_directory,
    ):

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

    # ======================================================
    # INTERACTION STATE
    # ======================================================

    def is_waiting_for_user(
        self,
    ):

        return self.conversation.is_waiting()

    def get_pending_interaction(
        self,
    ):

        return self.conversation.get_pending()
