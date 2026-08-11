from brain.core.conversation_manager import (
    ConversationManager,
    ConversationState,
)


def test_starts_and_reads_pending_interaction():
    manager = ConversationManager()

    pending = manager.start(
        kind="chrome_profile",
        state=ConversationState.WAITING_FOR_SELECTION,
        prompt="Please choose a Chrome profile.",
        metadata={"target": "chrome"},
    )

    assert manager.is_waiting()
    assert manager.is_waiting_for("chrome_profile")
    assert pending.state == ConversationState.WAITING_FOR_SELECTION
    assert pending.metadata["target"] == "chrome"


def test_records_attempts_without_clearing_interaction():
    manager = ConversationManager()
    manager.start("chrome_profile", ConversationState.WAITING_FOR_SELECTION)

    manager.record_attempt()
    manager.record_attempt()

    assert manager.get_pending().attempts == 2
    assert manager.is_waiting()


def test_clear_ends_interaction():
    manager = ConversationManager()
    manager.start("chrome_profile")

    pending = manager.clear()

    assert pending.kind == "chrome_profile"
    assert not manager.is_waiting()
    assert manager.get_pending() is None
