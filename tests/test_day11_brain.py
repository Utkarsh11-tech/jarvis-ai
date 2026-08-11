from unittest.mock import patch

from brain.core.assistant_v2 import Assistant


def test_confirmation_parser_accepts_yes_and_no_variants():
    assert Assistant._parse_confirmation("yes") is True
    assert Assistant._parse_confirmation("sure") is True
    assert Assistant._parse_confirmation("do it") is True
    assert Assistant._parse_confirmation("no") is False
    assert Assistant._parse_confirmation("cancel it") is False
    assert Assistant._parse_confirmation("maybe") is None


def test_confirmed_shutdown_uses_system_command_without_console_input():
    assistant = object.__new__(Assistant)

    with patch("brain.core.assistant_v2.subprocess.Popen") as popen:
        response = assistant._execute_confirmed_action("shutdown", {})

    popen.assert_called_once_with(["shutdown", "/s", "/t", "5"])
    assert response == "Shutting down the computer in 5 seconds."


def test_confirmed_restart_uses_system_command_without_console_input():
    assistant = object.__new__(Assistant)

    with patch("brain.core.assistant_v2.subprocess.Popen") as popen:
        response = assistant._execute_confirmed_action("restart", {})

    popen.assert_called_once_with(["shutdown", "/r", "/t", "5"])
    assert response == "Restarting the computer in 5 seconds."


def test_media_cleanup_preserves_platform_suffix():
    assistant = object.__new__(Assistant)

    assert assistant.clean_media_command(
        "play believer on youtube music"
    ) == "play believer on youtube music"
