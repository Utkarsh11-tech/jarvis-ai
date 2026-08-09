from PySide6.QtCore import QObject

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


class Assistant(QObject):

    def __init__(self, bridge):

        super().__init__()

        print("Assistant created")

        self.bridge = bridge

        self.state_manager = StateManager(bridge)

        self.context = ContextManager()

        self.awaiting_chrome_profile = False
        self.chrome_profiles = {}

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

        # ==========================================
        # CHROME PROFILE RESPONSE
        # ==========================================

        if self.awaiting_chrome_profile:

            self.handle_chrome_profile_response(command)

            return

        # ==========================================
        # NORMAL COMMAND
        # ==========================================

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
        Gets Chrome profiles and asks the user
        to select one using voice.
        """

        profiles = get_chrome_profiles()

        if not profiles:

            response = "No Chrome profiles were found."

            print(response)

            speak(response)

            self.bridge.send_response(response)

            self.state_manager.set_state(JarvisState.IDLE)

            return

        self.chrome_profiles = profiles

        self.awaiting_chrome_profile = True

        # ==========================================
        # CREATE SPOKEN PROFILE LIST
        # ==========================================

        profile_names = []

        for index, (
            profile_directory,
            profile_data,
        ) in enumerate(
            profiles.items(),
            start=1,
        ):

            name = profile_data.get(
                "name",
                f"Profile {index}",
            )

            profile_names.append(f"{index}. {name}")

        message = (
            "I found "
            f"{len(profile_names)} Chrome profiles. "
            "Please choose one. "
            + ", ".join(profile_names)
            + ". You can say the profile number "
            "or its name."
        )

        print(f"JARVIS: {message}")

        self.state_manager.set_state(JarvisState.SPEAKING)

        speak(message)

        self.bridge.send_response(message)

        # ==========================================
        # REQUEST ONE-TIME VOICE INPUT
        # ==========================================

        self.bridge.request_voice_input()

    # ==================================================
    # HANDLE CHROME PROFILE RESPONSE
    # ==================================================

    def handle_chrome_profile_response(
        self,
        response,
    ):
        """
        Resolves a spoken Chrome profile
        selection by number or name.
        """

        if not response:

            return

        response = normalize(response)

        print(f"JARVIS: Profile selection: {response}")

        profiles = list(self.chrome_profiles.items())

        selected_profile = None

        # ==========================================
        # NUMBER SELECTION
        # ==========================================

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

        words = response.split()

        number = None

        for word in words:

            if word.isdigit():

                number = int(word)

                break

            if word in number_words:

                number = number_words[word]

                break

        if number is not None:

            if 1 <= number <= len(profiles):

                selected_profile = profiles[number - 1]

        # ==========================================
        # NAME SELECTION
        # ==========================================

        if selected_profile is None:

            response_lower = response.lower()

            for profile_directory, profile_data in profiles:

                name = profile_data.get(
                    "name",
                    "",
                ).lower()

                if (
                    response_lower == name
                    or response_lower in name
                    or name in response_lower
                ):

                    selected_profile = (
                        profile_directory,
                        profile_data,
                    )

                    break

        # ==========================================
        # INVALID SELECTION
        # ==========================================

        if selected_profile is None:

            message = (
                "I couldn't identify that Chrome "
                "profile. Please say its number "
                "or name."
            )

            print(f"JARVIS: {message}")

            speak(message)

            self.bridge.send_response(message)

            self.bridge.request_voice_input()

            return

        # ==========================================
        # PROFILE FOUND
        # ==========================================

        profile_directory = selected_profile[0]

        profile_name = selected_profile[1].get(
            "name",
            "selected profile",
        )

        self.awaiting_chrome_profile = False

        self.state_manager.set_state(JarvisState.EXECUTING)

        message = f"Opening Chrome with " f"{profile_name}."

        print(f"JARVIS: {message}")

        speak(message)

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
    # REQUEST GUI CHROME PROFILE
    # ==================================================

    def request_chrome_profile_gui(self):
        """
        Requests Chrome profile selection
        from the GUI as a fallback.
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
    # HANDLE GUI PROFILE SELECTION
    # ==================================================

    def handle_profile_selected(
        self,
        profile_directory,
    ):
        """
        Handles a Chrome profile selected
        by the GUI.
        """

        self.awaiting_chrome_profile = False

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
            # UPDATE CONTEXT
            # -------------------------

            if target:

                self.context.remember(
                    intent=intent,
                    target=target,
                )

        return results
