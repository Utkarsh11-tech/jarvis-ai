import json
import subprocess
import threading
from pathlib import Path

# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SERVICE_PYTHON = PROJECT_ROOT / "voice-lab" / "Scripts" / "python.exe"

SERVICE_SCRIPT = PROJECT_ROOT / "brain" / "voices" / "xtts_service.py"

OUTPUT_DIR = PROJECT_ROOT / "voice-lab" / "jarvis voice"


# ==========================================================
# PROCESS STATE
# ==========================================================

_process = None

_lock = threading.Lock()


# ==========================================================
# START XTTS SERVICE
# ==========================================================


def _start_service():
    """
    Starts the persistent XTTS service if it is not already
    running.

    XTTS is intentionally started lazily.

    This means JARVIS itself does NOT require XTTS during
    startup.

    The service starts only when voice output is actually
    requested.
    """

    global _process

    # ------------------------------------------------------
    # Existing service
    # ------------------------------------------------------

    if _process is not None:

        if _process.poll() is None:
            return

    # ------------------------------------------------------
    # Validate XTTS environment
    # ------------------------------------------------------

    if not SERVICE_PYTHON.exists():

        raise FileNotFoundError(
            "XTTS Python environment not found: " f"{SERVICE_PYTHON}"
        )

    if not SERVICE_SCRIPT.exists():

        raise FileNotFoundError("XTTS service script not found: " f"{SERVICE_SCRIPT}")

    # ------------------------------------------------------
    # Start persistent service
    # ------------------------------------------------------

    _process = subprocess.Popen(
        [
            str(SERVICE_PYTHON),
            str(SERVICE_SCRIPT),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=None,
        text=True,
        bufsize=1,
    )

    # ------------------------------------------------------
    # Wait for service initialization
    # ------------------------------------------------------

    ready_line = _process.stdout.readline().strip()

    if not ready_line:

        raise RuntimeError("XTTS service did not return a response.")

    try:

        response = json.loads(ready_line)

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "XTTS service returned invalid JSON: " f"{ready_line}"
        ) from error

    # ------------------------------------------------------
    # Validate startup response
    # ------------------------------------------------------

    if response.get("status") != "ready":

        raise RuntimeError("XTTS service failed to start: " f"{response}")


# ==========================================================
# INITIALIZE XTTS
# ==========================================================


def initialize_xtts() -> None:
    """
    Explicitly initializes the XTTS service.

    This function remains available for compatibility with
    existing code/tests.

    Normal JARVIS startup should NOT call this function.

    XTTS should preferably be started lazily when speech is
    actually requested.
    """

    with _lock:

        _start_service()


# ==========================================================
# GENERATE SPEECH
# ==========================================================


def _generate(
    text: str,
    output_path: Path,
):
    """
    Sends a speech generation request to the persistent
    XTTS service.
    """

    if _process is None:

        raise RuntimeError("XTTS service is not running.")

    if _process.poll() is not None:

        raise RuntimeError("XTTS service has stopped.")

    request = {
        "command": "speak",
        "text": text,
        "output_path": str(output_path),
    }

    # ------------------------------------------------------
    # Send request
    # ------------------------------------------------------

    try:

        _process.stdin.write(json.dumps(request) + "\n")

        _process.stdin.flush()

    except Exception as error:

        raise RuntimeError("Failed to send request to XTTS service.") from error

    # ------------------------------------------------------
    # Read response
    # ------------------------------------------------------

    response_line = _process.stdout.readline().strip()

    if not response_line:

        raise RuntimeError("XTTS service returned no response.")

    try:

        response = json.loads(response_line)

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "XTTS service returned invalid JSON: " f"{response_line}"
        ) from error

    # ------------------------------------------------------
    # Validate response
    # ------------------------------------------------------

    if response.get("status") != "ok":

        raise RuntimeError("XTTS generation failed: " f"{response}")


# ==========================================================
# PLAY AUDIO
# ==========================================================


def _play_audio(
    output_path: Path,
):
    """
    Plays the generated WAV file using ffplay.
    """

    subprocess.run(
        [
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-loglevel",
            "quiet",
            str(output_path),
        ],
        check=True,
    )


# ==========================================================
# PUBLIC SPEAK FUNCTION
# ==========================================================


def speak_xtts(
    text: str,
) -> None:
    """
    Generates and plays speech using the persistent
    XTTS v2 service.

    XTTS is started only when this function is actually
    called.
    """

    if not text:
        return

    # ------------------------------------------------------
    # Prepare output directory
    # ------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = OUTPUT_DIR / "jarvis_output.wav"

    # ------------------------------------------------------
    # Serialize XTTS requests
    # ------------------------------------------------------

    with _lock:

        _start_service()

        _generate(
            text,
            output_path,
        )

        _play_audio(
            output_path,
        )
