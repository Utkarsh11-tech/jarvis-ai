from brain.core.normalizer import normalize
from brain.core.intent_detector import detect_intent
from brain.core.target_extractor import extract_target
from brain.core.context import ContextManager

from brain.core.executor import (
    execute,
    get_acknowledgement,
    get_chrome_profiles,
    open_chrome,
)

from bridge.bridge import JarvisBridge

from brain.voices.voice_manager import speak

from brain.core.state import (
    JarvisState,
    StateManager,
)

from PySide6.QtCore import QObject


class Assistant(QObject):

    def __init__(self, bridge):
        super().__init__()

        print("Assistant created")

        self.bridge = bridge
        self.state_manager = StateManager(bridge)
        self.context = ContextManager()

        self.bridge.command_requested.connect(self.handle_command)

        self.bridge.profile_selected.connect(self.handle_profile_selected)

    # ==================================================
    # BRAIN STARTUP
    # ==================================================

    def run(self):
        """
        Starts the Brain worker.
        """

        self.initialize()

        print("JARVIS Brain is ready.")

    # ==================================================
    # HANDLE COMMAND
    # ==================================================

    def handle_command(self, command):
        """
        Handles commands received from the Body.
        """

        self.state_manager.set_state(JarvisState.THINKING)

        results = self.process_command(command)

        if not results:

            self.state_manager.set_state(JarvisState.IDLE)

            return

        for result in results:

            # -------------------------
            # SPEAKING
            # -------------------------

            self.state_manager.set_state(JarvisState.SPEAKING)

            acknowledgement = get_acknowledgement(result)

            print(acknowledgement)

            speak(acknowledgement)

            # -------------------------
            # CHROME
            # -------------------------

            if result["intent"] == "OPEN_APPLICATION" and result["target"] == "chrome":

                self.request_chrome_profile()

                return

            # -------------------------
            # EXECUTING
            # -------------------------

            self.state_manager.set_state(JarvisState.EXECUTING)

            response = execute(result)

            print(response)

            self.bridge.send_response(response)

            # -------------------------
            # UPDATE RESPONSE
            # -------------------------

            self.context.remember(
                intent=result["intent"],
                target=result["target"],
                response=response,
            )

        # -------------------------
        # RETURN TO IDLE
        # -------------------------

        self.state_manager.set_state(JarvisState.IDLE)

    # ==================================================
    # REQUEST CHROME PROFILE
    # ==================================================

    def request_chrome_profile(self):
        """
        Requests Chrome profile selection
        from the GUI.
        """

        profiles = get_chrome_profiles()

        if not profiles:

            response = "No Chrome profiles were found."

            print(response)

            self.bridge.send_response(response)

            self.state_manager.set_state(JarvisState.IDLE)

            return

        self.state_manager.set_state(JarvisState.EXECUTING)

        self.bridge.request_profile_selection(list(profiles.items()))

    # ==================================================
    # HANDLE CHROME PROFILE SELECTION
    # ==================================================

    def handle_profile_selected(
        self,
        profile_directory,
    ):
        """
        Handles the Chrome profile selected
        by the user in the GUI.
        """

        self.state_manager.set_state(JarvisState.EXECUTING)

        response = open_chrome(profile_directory)

        print(response)

        self.bridge.send_response(response)

        self.context.remember(
            intent="OPEN_APPLICATION",
            target="chrome",
            response=response,
        )

        self.state_manager.set_state(JarvisState.IDLE)

    # ==================================================
    # INITIALIZE
    # ==================================================

    def initialize(self):
        """
        Initializes all required modules.
        """

        print("Initializing all required modules.....")

    # ==================================================
    # PROCESS COMMAND
    # ==================================================

    def process_command(self, command):
        """
        Processes one or multiple user commands.

        Context is updated after every command
        so later commands can reference earlier ones.
        """

        command = normalize(command)

        if not command:
            return []

        commands = command.replace(
            " and then ",
            " and ",
        ).split(" and ")

        results = []

        for current_command in commands:

            words = current_command.split()

            if not words:
                continue

            # -------------------------
            # ACTION
            # -------------------------

            action = words[0]

            # -------------------------
            # TARGET
            # -------------------------

            target = extract_target(words)

            # -------------------------
            # CONTEXT RESOLUTION
            # -------------------------

            target = self.context.resolve_reference(target)

            # -------------------------
            # INTENT
            # -------------------------

            intent = detect_intent(
                action,
                target,
            )

            # -------------------------
            # SYSTEM COMMAND
            # -------------------------

            if intent == "SYSTEM_COMMAND" and not target:

                target = action

            # -------------------------
            # STORE RESULT
            # -------------------------

            result = {
                "intent": intent,
                "target": target,
            }

            results.append(result)

            # -------------------------
            # UPDATE CONTEXT IMMEDIATELY
            # -------------------------

            if target:

                self.context.remember(
                    intent=intent,
                    target=target,
                )

        return results
