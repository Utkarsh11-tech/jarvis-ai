from core.normalizer import normalize
from core.intent_detector import detect_intent
from core.target_extractor import extract_target
from core.executor import execute


class Assistant:

    def __init__(self):
        print("Assistant created")

    def start(self):
        self.initialize()
        print("JARVIS is now online.")

        while True:
            command = self.listen()
            results = self.process_command(command)

            for result in results:
                response = execute(result)
                print(response)

    def initialize(self):
        """Initializes all required modules."""

        print("Initializing all required modules.....")

    def listen(self):
        """Receives a command from the user."""

        return input("You: ")

    def process_command(self, command):
        """Processes one or multiple user commands."""

        # Normalize the command
        command = normalize(command)

        # Handle empty input
        if not command:
            return [
                {
                    "intent": "UNKNOWN",
                    "target": ""
                }
            ]

        # Split multiple commands
        commands = command.replace(" and then ", " and ").split(" and ")

        results = []

        for current_command in commands:

            words = current_command.split()

            if not words:
                continue

            # Extract the action
            action = words[0]

            # Extract the target
            target = extract_target(words)

            # Detect the intent
            intent = detect_intent(action, target)

            # System commands use the action itself as the target
            if intent == "SYSTEM_COMMAND" and not target:
                target = action

                
            # Store structured command
            results.append(
                {
                    "intent": intent,
                    "target": target
                }
            )

        return results