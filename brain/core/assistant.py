class Assistant:

    def __init__(self):
        print("Assistant created")

    def start(self):
        self.initialize()
        print("JARVIS is now online.")

        while True:
            command = self.listen()
            result = self.process_command(command)

    def initialize(self):
        print("Initializing all required modules.....")

    def listen(self):
        command = input("You : ")
        return command

    def process_command(self, command): 
        command = command.strip()
        command = command.lower() 
        command  = command.split()
        command = " ".join(command)
        words = command.split()
        action = words[0]
        target = " ".join(words[1:])
