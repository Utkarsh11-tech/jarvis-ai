import re
import webbrowser
from urllib.parse import quote

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

# ==================================================
# CHROME PROFILE COMMAND PARSER
# ==================================================


def extract_chrome_profile_command(command):
    """
    Extracts a Chrome profile name and the remaining
    command from natural-language Chrome profile
    requests.

    Supported examples:

        open vinod chrome
            -> ("vinod", "")

        open vinod's chrome
            -> ("vinod", "")

        open vinod chrome profile
            -> ("vinod", "")

        open vinod's chrome profile
            -> ("vinod", "")

        open the chrome profile of vinod
            -> ("vinod", "")

        open chrome profile of vinod
            -> ("vinod", "")

        open vinod chrome profile and play believer
            -> ("vinod", "play believer")

        open vinod's chrome and play believer
            -> ("vinod", "play believer")

        open the chrome profile of vinod and then
        play believer
            -> ("vinod", "play believer")
    """

    command = normalize(command)

    if not command:
        return "", ""

    command = command.lower().strip()

    patterns = [
        # ------------------------------------------
        # open the chrome profile of vinod
        # ------------------------------------------
        (
            r"^open\s+(?:the\s+)?chrome\s+profile\s+of\s+"
            r"(.+?)(?:\s+and(?:\s+then)?\s+(.+))?$"
        ),
        # ------------------------------------------
        # open vinod's chrome profile
        # ------------------------------------------
        (r"^open\s+(.+?)['’]s\s+chrome\s+profile" r"(?:\s+and(?:\s+then)?\s+(.+))?$"),
        # ------------------------------------------
        # open vinod's chrome
        # ------------------------------------------
        (r"^open\s+(.+?)['’]s\s+chrome" r"(?:\s+and(?:\s+then)?\s+(.+))?$"),
        # ------------------------------------------
        # open vinod chrome profile
        # ------------------------------------------
        (r"^open\s+(.+?)\s+chrome\s+profile" r"(?:\s+and(?:\s+then)?\s+(.+))?$"),
        # ------------------------------------------
        # open vinod chrome
        # ------------------------------------------
        (r"^open\s+(.+?)\s+chrome" r"(?:\s+and(?:\s+then)?\s+(.+))?$"),
        # ------------------------------------------
        # open chrome profile vinod
        # ------------------------------------------
        (r"^open\s+chrome\s+profile\s+(.+?)" r"(?:\s+and(?:\s+then)?\s+(.+))?$"),
    ]

    for pattern in patterns:

        match = re.match(
            pattern,
            command,
        )

        if not match:
            continue

        profile_name = match.group(1).strip()

        remaining_command = ""

        if match.group(2):

            remaining_command = match.group(2).strip()

        return (
            profile_name,
            remaining_command,
        )

    return "", ""


# ==================================================
# ASSISTANT
# ==================================================


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

        self.initialize()

        print("JARVIS Brain is ready.")

    # ==================================================
    # HANDLE COMMAND
    # ==================================================

    def handle_command(self, command):

        if not command:
            return

        # ==========================================
        # DIRECTED CHROME PROFILE COMMAND
        # ==========================================

        profile_name, remaining_command = extract_chrome_profile_command(command)

        if profile_name:

            self.handle_directed_chrome_command(
                profile_name,
                remaining_command,
            )

            return

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

            self.state_manager.set_state(JarvisState.SPEAKING)

            acknowledgement = get_acknowledgement(result)

            print(acknowledgement)

            speak(acknowledgement)

            # -------------------------
            # NORMAL CHROME
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
            # UPDATE CONTEXT
            # -------------------------

            self.context.remember(
                intent=result["intent"],
                target=result["target"],
                response=response,
            )

        self.state_manager.set_state(JarvisState.IDLE)

    # ==================================================
    # RESOLVE CHROME PROFILE
    # ==================================================

    def resolve_chrome_profile(
        self,
        profile_name,
    ):

        profiles = get_chrome_profiles()

        if not profiles:
            return None

        profile_name = normalize(profile_name).lower().strip()

        profile_name = re.sub(
            r"\b(profile|chrome)\b",
            "",
            profile_name,
        ).strip()

        for (
            profile_directory,
            profile_data,
        ) in profiles.items():

            name = (
                profile_data.get(
                    "name",
                    "",
                )
                .lower()
                .strip()
            )

            if profile_name == name or profile_name in name or name in profile_name:

                return (
                    profile_directory,
                    profile_data,
                )

        return None

    # ==================================================
    # NORMALIZE MEDIA COMMAND
    # ==================================================

    def clean_media_command(
        self,
        command,
    ):

        return normalize(command).strip()

    # ==================================================
    # EXECUTE DIRECTED CHROME COMMAND
    # ==================================================

    def handle_directed_chrome_command(
        self,
        profile_name,
        remaining_command,
    ):

        selected_profile = self.resolve_chrome_profile(profile_name)

        if selected_profile is None:

            message = f"I couldn't find the Chrome " f"profile {profile_name}."

            print(f"JARVIS: {message}")

            speak(message)

            self.bridge.send_response(message)

            self.state_manager.set_state(JarvisState.IDLE)

            return

        profile_directory = selected_profile[0]

        profile_data = selected_profile[1]

        actual_profile_name = profile_data.get(
            "name",
            profile_name,
        )

        # ==========================================
        # NO FOLLOW-UP
        # ==========================================

        if not remaining_command:

            self.state_manager.set_state(JarvisState.EXECUTING)

            message = f"Opening Chrome with " f"{actual_profile_name}."

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

            return

        # ==========================================
        # FOLLOW-UP COMMAND
        # ==========================================

        print("JARVIS: Executing after Chrome: " f"{remaining_command}")

        cleaned_command = normalize(remaining_command)

        # ==========================================
        # PLAY MEDIA
        # ==========================================

        if (
            cleaned_command.startswith("play ")
            or cleaned_command.startswith("listen ")
            or cleaned_command.startswith("put ")
        ):

            media_command = self.clean_media_command(cleaned_command)

            if media_command.startswith("play "):

                media_target = media_command[len("play ") :].strip()

            elif media_command.startswith("listen "):

                media_target = media_command[len("listen ") :].strip()

            elif media_command.startswith("put "):

                media_target = media_command[len("put ") :].strip()

            else:

                media_target = media_command

            result = {
                "intent": "PLAY_MEDIA",
                "target": media_target,
                "profile_directory": profile_directory,
            }

            self.execute_directed_result(result)

            return

        # ==========================================
        # WEB SEARCH
        # ==========================================

        if (
            cleaned_command.startswith("search ")
            or cleaned_command.startswith("google ")
            or cleaned_command.startswith("browse ")
            or cleaned_command.startswith("lookup ")
        ):

            words = cleaned_command.split(maxsplit=1)

            if len(words) == 2:

                search_target = words[1].strip()

            else:

                search_target = ""

            result = {
                "intent": "WEB_SEARCH",
                "target": search_target,
                "profile_directory": profile_directory,
            }

            self.execute_directed_result(result)

            return

        # ==========================================
        # FALLBACK PROCESSING
        # ==========================================

        results = self.process_command(remaining_command)

        for result in results:

            result["profile_directory"] = profile_directory

            self.execute_directed_result(result)

        self.state_manager.set_state(JarvisState.IDLE)

    # ==================================================
    # EXECUTE DIRECTED RESULT
    # ==================================================

    def execute_directed_result(
        self,
        result,
    ):

        self.state_manager.set_state(JarvisState.SPEAKING)

        acknowledgement = get_acknowledgement(result)

        print(acknowledgement)

        speak(acknowledgement)

        self.state_manager.set_state(JarvisState.EXECUTING)

        # ==========================================
        # WEB SEARCH
        # ==========================================

        if result["intent"] == "WEB_SEARCH":

            target = result.get(
                "target",
                "",
            )

            if target:

                search_url = "https://www.google.com/search?q=" + quote(target)

                webbrowser.open(search_url)

                response = f"Searching for {target}."

            else:

                response = "What would you like " "me to search for?"

        else:

            response = execute(result)

        print(response)

        self.bridge.send_response(response)

        self.context.remember(
            intent=result["intent"],
            target=result["target"],
            response=response,
        )

    # ==================================================
    # REQUEST CHROME PROFILE
    # ==================================================

    def request_chrome_profile(self):

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

        self.bridge.request_voice_input()

    # ==================================================
    # HANDLE CHROME PROFILE RESPONSE
    # ==================================================

    def handle_chrome_profile_response(
        self,
        response,
    ):

        if not response:
            return

        response = normalize(response)

        print("JARVIS: Profile selection: " f"{response}")

        profiles = list(self.chrome_profiles.items())

        selected_profile = None

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

        if selected_profile is None:

            response_lower = response.lower()

            for (
                profile_directory,
                profile_data,
            ) in profiles:

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

        print("Initializing all required modules.....")

    # ==================================================
    # PROCESS COMMAND
    # ==================================================

    def process_command(
        self,
        command,
    ):

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
