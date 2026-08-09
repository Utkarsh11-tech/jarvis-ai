from brain.core.normalizer import normalize
from brain.core.intent_detector import detect_intent
from brain.core.target_extractor import extract_target
from brain.core.executor import (
    execute,
    get_acknowledgement,
)

from bridge.bridge import JarvisBridge

from brain.voices.voice_manager import speak
from brain.voices.listener import VoiceListener

from brain.core.state import (
    JarvisState,
    StateManager,
)

from PySide6.QtCore import QObject


class Assistant(QObject):

    def __init__(self, bridge):
        super().__init__()

        print("Assistant created")

        self.listener = None
        self.bridge = bridge
        self.state_manager = StateManager(bridge)

        self.bridge.command_requested.connect(self.handle_command)

    def run(self):
        """
        Starts the Brain worker.
        """

        self.initialize()

        print("JARVIS Brain is ready.")

    def start(self):
        self.initialize()

        print("JARVIS is now online.")

        self.listener = VoiceListener()

        try:

            while True:

                # -------------------------
                # SLEEPING
                # -------------------------

                self.state_manager.set_state(JarvisState.SLEEPING)

                awakened = self.listener.listen_for_wake_word()

                if not awakened:
                    continue

                # -------------------------
                # LISTENING
                # -------------------------

                self.state_manager.set_state(JarvisState.LISTENING)

                speak("Yes?")

                command = self.listener.listen_for_command()

                if not command:

                    self.state_manager.set_state(JarvisState.SPEAKING)

                    speak("I didn't hear a command.")

                    self.listener.prepare_for_wake_word()

                    continue

                # -------------------------
                # THINKING
                # -------------------------

                self.state_manager.set_state(JarvisState.THINKING)

                results = self.process_command(command)

                # -------------------------
                # COMMAND PROCESSING
                # -------------------------

                for result in results:

                    # -------------------------
                    # SPEAKING
                    # -------------------------

                    self.state_manager.set_state(JarvisState.SPEAKING)

                    acknowledgement = get_acknowledgement(result)

                    print(acknowledgement)

                    speak(acknowledgement)

                    # -------------------------
                    # EXECUTING
                    # -------------------------

                    self.state_manager.set_state(JarvisState.EXECUTING)

                    response = execute(result)

                    print(response)

                self.state_manager.set_state(JarvisState.IDLE)

                self.listener.prepare_for_wake_word()

        except KeyboardInterrupt:

            print("\nJARVIS: Shutting down.")

        finally:

            if self.listener:
                self.listener.close()

    def handle_command(self, command):
        """
        Handles commands received from the Body.
        """

        self.state_manager.set_state(JarvisState.THINKING)

        results = self.process_command(command)

        for result in results:

            # -------------------------
            # SPEAKING
            # -------------------------

            self.state_manager.set_state(JarvisState.SPEAKING)

            acknowledgement = get_acknowledgement(result)

            print(acknowledgement)

            speak(acknowledgement)

            # -------------------------
            # EXECUTING
            # -------------------------

            self.state_manager.set_state(JarvisState.EXECUTING)

            response = execute(result)

            print(response)

            self.bridge.send_response(response)

        # -------------------------
        # RETURN TO IDLE
        # -------------------------

        self.state_manager.set_state(JarvisState.IDLE)

    def initialize(self):
        """
        Initializes all required modules.
        """

        print("Initializing all required modules.....")

    def process_command(self, command):
        """
        Processes one or multiple user commands.
        """

        command = normalize(command)

        if not command:
            return []

        commands = command.replace(" and then ", " and ").split(" and ")

        results = []

        for current_command in commands:

            words = current_command.split()

            if not words:
                continue

            action = words[0]

            target = extract_target(words)

            intent = detect_intent(
                action,
                target,
            )

            if intent == "SYSTEM_COMMAND" and not target:
                target = action

            results.append(
                {
                    "intent": intent,
                    "target": target,
                }
            )

        return results
