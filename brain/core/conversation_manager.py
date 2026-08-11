from dataclasses import dataclass, field
from enum import Enum


class ConversationState(Enum):
    """Represents the conversational interaction state of JARVIS."""

    IDLE = "idle"
    WAITING_FOR_INPUT = "waiting_for_input"
    WAITING_FOR_SELECTION = "waiting_for_selection"
    WAITING_FOR_CONFIRMATION = "waiting_for_confirmation"


@dataclass
class PendingInteraction:
    """Describes the information JARVIS is currently waiting for."""

    kind: str
    state: ConversationState
    prompt: str = ""
    metadata: dict = field(default_factory=dict)
    attempts: int = 0


class ConversationManager:
    """
    Generic short-lived conversation controller.

    This keeps pending user interactions separate from command execution.
    New features can register their own interaction kind instead of adding
    feature-specific flags to Assistant.
    """

    def __init__(self):
        self._pending = None

    def start(
        self,
        kind,
        state=ConversationState.WAITING_FOR_INPUT,
        prompt="",
        metadata=None,
    ):
        """Starts a new pending interaction."""

        self._pending = PendingInteraction(
            kind=kind,
            state=state,
            prompt=prompt,
            metadata=dict(metadata or {}),
        )

        return self._pending

    def is_waiting(self):
        """Returns True when JARVIS is waiting for user input."""

        return self._pending is not None

    def is_waiting_for(self, kind):
        """Returns True when the pending interaction has the given kind."""

        return self._pending is not None and self._pending.kind == kind

    def get_pending(self):
        """Returns the pending interaction, or None."""

        return self._pending

    def record_attempt(self):
        """Records another response attempt for the pending interaction."""

        if self._pending is not None:
            self._pending.attempts += 1

        return self._pending

    def clear(self):
        """Ends the current interaction and returns it."""

        pending = self._pending
        self._pending = None
        return pending

    def cancel(self):
        """Cancels the current interaction."""

        return self.clear()
