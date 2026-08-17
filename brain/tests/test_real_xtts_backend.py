from pathlib import Path

from brain.voices import voice_manager


# ==========================================================
# TEST: REAL XTTS BACKEND
# ==========================================================

def test_real_xtts_backend():

    print()
    print("========================================")
    print("JARVIS REAL XTTS BACKEND TEST")
    print("========================================")

    text = (
        "JARVIS voice backend test successful."
    )

    print()
    print("----------------------------------------")
    print("TEST: VOICE MANAGER → XTTS")
    print("----------------------------------------")

    print(
        f"TEXT: {text}"
    )

    # ------------------------------------------------------
    # Force the production voice manager to use XTTS.
    # ------------------------------------------------------

    voice_manager.VOICE_MODE = "xtts"

    # ------------------------------------------------------
    # Call the real production voice boundary.
    #
    # This is NOT a fake speaker.
    # This invokes the existing XTTS backend.
    # ------------------------------------------------------

    result = voice_manager.speak(
        text
    )

    print()
    print(
        f"VOICE RESULT: {result}"
    )

    # ------------------------------------------------------
    # The voice manager should report success.
    # ------------------------------------------------------

    assert result is True

    print()
    print(
        "PASS: voice_manager.speak() returned True."
    )

    print(
        "PASS: Real XTTS backend accepted the text."
    )

    print()
    print("========================================")
    print("REAL XTTS BACKEND TEST: PASSED")
    print("========================================")


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    test_real_xtts_backend()