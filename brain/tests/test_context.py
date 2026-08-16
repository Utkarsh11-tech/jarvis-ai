from brain.core.context import ContextManager


def test_resolves_it_again_to_last_target():
    context = ContextManager()
    context.remember(intent="PLAY_MEDIA", target="believer")

    assert context.resolve_reference("it again") == "believer"


def test_resolves_plain_reference_to_last_target():
    context = ContextManager()
    context.remember(intent="PLAY_MEDIA", target="believer")

    assert context.resolve_reference("it") == "believer"


def test_stores_last_chrome_profile_for_followups():
    context = ContextManager()
    context.remember(
        intent="OPEN_APPLICATION",
        target="chrome",
        profile_directory="Profile 10",
        profile_name="Vinod",
    )

    assert context.get_last_profile_directory() == "Profile 10"
    assert context.get_last_profile_name() == "Vinod"


def test_clear_removes_profile_context():
    context = ContextManager()
    context.remember(
        profile_directory="Profile 10",
        profile_name="Vinod",
    )

    context.clear()

    assert context.get_last_profile_directory() == ""
    assert context.get_last_profile_name() == ""
