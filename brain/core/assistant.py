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
        print("Initializing all required modules.....")

    def listen(self):
        """Receives a command from the user."""
        command = input("You : ")
        return command

    def process_command(self, command):
        """Cleans the command and extracts intent and target."""

        # Cleaning
        command = command.strip()
        command = command.lower()
        command = " ".join(command.split())

        # Split command
        words = command.split()

        # Safety check
        if not words:
            return {
                "intent": "UNKNOWN",
                "target": ""
            }

        # Extract action and target
        action = words[0]
        target = " ".join(words[1:])

        # Intent Mapping (Temporary)
        intent_map = {
            "open": "OPEN_APPLICATION",
            "launch": "OPEN_APPLICATION",
            "start": "OPEN_APPLICATION",

            "play": "PLAY_MEDIA",

            "shutdown": "SYSTEM_COMMAND",
            "restart": "SYSTEM_COMMAND",

            "search": "WEB_SEARCH",
            "find": "WEB_SEARCH",
        }

        # Find Intent
        intent = intent_map.get(action, "UNKNOWN")

        # Return structured data
        result = {
            "intent": intent,
            "target": target
        }

        return result