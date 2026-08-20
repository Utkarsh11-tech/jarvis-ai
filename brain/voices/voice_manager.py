import os

# ==========================================================
# VOICE MODE
# ==========================================================

VOICE_MODE = (
    os.getenv(
        "JARVIS_VOICE_MODE",
        "xtts",
    )
    .strip()
    .lower()
)


# ==========================================================
# VOICE MANAGER
# ==========================================================


def speak(text: str) -> bool:
    """
    Speaks text using the configured voice backend.

    Supported modes:

        xtts
        online
        disabled

    The voice layer is intentionally isolated from the
    JARVIS brain.

    Voice is optional.

    If the selected voice backend is unavailable or fails,
    the function returns False instead of crashing JARVIS.

    This allows JARVIS to continue operating and return
    the response through the normal typed/bridge interface.
    """

    if not text:
        return True

    # ------------------------------------------------------
    # DISABLED
    # ------------------------------------------------------

    if VOICE_MODE in (
        "disabled",
        "none",
        "off",
    ):

        print("JARVIS Voice: voice output disabled.")

        return True

    # ------------------------------------------------------
    # ONLINE
    # ------------------------------------------------------

    if VOICE_MODE == "online":

        try:

            from brain.voices.online_speaker import (
                speak_online,
            )

            speak_online(text)

            return True

        except Exception as error:

            print("JARVIS Voice: online voice " f"backend failed: {error}")

            return False

    # ------------------------------------------------------
    # XTTS
    # ------------------------------------------------------

    if VOICE_MODE == "xtts":

        try:

            from brain.voices.xtts_speaker import (
                speak_xtts,
            )

            speak_xtts(text)

            return True

        except Exception as error:

            print("JARVIS Voice: XTTS backend " f"failed: {error}")

            return False

    # ------------------------------------------------------
    # UNKNOWN MODE
    # ------------------------------------------------------

    print("JARVIS Voice: unknown voice mode: " f"{VOICE_MODE}")

    return False
