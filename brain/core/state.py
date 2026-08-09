from enum import Enum
from bridge.bridge import JarvisBridge


class JarvisState(Enum):
    """
    Represents the current state of JARVIS.
    """

    IDLE = "idle"
    SLEEPING = "sleeping"
    LISTENING = "listening"
    THINKING = "thinking"
    EXECUTING = "executing"
    SPEAKING = "speaking"


class StateManager:
    """
    Manages the current state of JARVIS.
    """

    def __init__(self, bridge):
        self.current_state = JarvisState.IDLE
        self.bridge = bridge

    def set_state(self, state):
        """
        Changes the current JARVIS state.
        """

        self.current_state = state

        print(f"JARVIS STATE: {state.value.upper()}")

        self.bridge.set_state(state.value)

    def get_state(self):
        """
        Returns the current JARVIS state.
        """

        return self.current_state
