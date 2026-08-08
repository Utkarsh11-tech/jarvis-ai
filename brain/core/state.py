from enum import Enum


class JarvisState(Enum):
    """
    Represents the current state of JARVIS.
    """

    SLEEPING = "sleeping"
    LISTENING = "listening"
    THINKING = "thinking"
    EXECUTING = "executing"
    SPEAKING = "speaking"


class StateManager:
    """
    Manages the current state of JARVIS.
    """

    def __init__(self):
        self.current_state = JarvisState.SLEEPING

    def set_state(self, state):
        """
        Changes the current JARVIS state.
        """

        self.current_state = state

        print(f"JARVIS STATE: {state.value.upper()}")

    def get_state(self):
        """
        Returns the current JARVIS state.
        """

        return self.current_state
