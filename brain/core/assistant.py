from core.normalizer import normalize
from core.intent_detector import detect_intent
from core.target_extractor import extract_target


class Assistant:

    def __init__(self):
        print("Assistant created")

    def start(self):
        self.initialize()
        print("JARVIS is now online.")

        while True:
            command = self.listen()
            result = self.process_command(command)
            print(result)  # Temporary for debugging 

    def initialize(self):
        """Initializes all required modules."""
        print("Initializing all required modules.....")

    def listen(self):
        """Receives a command from the user."""
        return input("You: ")

    def process_command(self, command):
        """Processes the user command and returns structured data."""

        # Normalize the command
        command = normalize(command)

        # Split the command into words
        words = command.split()

        # Handle empty input
        if not words:
            return {"intent": "UNKNOWN", "target": ""}

        # Extract the action
        action = words[0]

        # Detect the intent
        intent = detect_intent(action)

        # Extract the target
        target = extract_target(words)

        # Return structured result
        return {"intent": intent, "target": target}
