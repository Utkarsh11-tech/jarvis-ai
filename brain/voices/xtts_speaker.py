import json
import subprocess
import threading
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SERVICE_PYTHON = (
    PROJECT_ROOT
    / "voice-lab"
    / "Scripts"
    / "python.exe"
)

SERVICE_SCRIPT = (
    PROJECT_ROOT
    / "brain"
    / "voices"
    / "xtts_service.py"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "voice-lab"
    / "jarvis voice"
)


_process = None
_lock = threading.Lock()


def _start_service():
    global _process

    if _process is not None:
        if _process.poll() is None:
            return

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

    ready_line = _process.stdout.readline().strip()

    if not ready_line:
        raise RuntimeError(
            "XTTS service did not return a response."
        )

    response = json.loads(ready_line)

    if response.get("status") != "ready":
        raise RuntimeError(
            f"XTTS service failed to start: {response}"
        )


def initialize_xtts() -> None:
    """
    Starts the persistent XTTS service during
    JARVIS startup.

    The service remains alive and is reused for
    subsequent speech requests.
    """

    with _lock:
        _start_service()


def _generate(
    text: str,
    output_path: Path,
):
    request = {
        "command": "speak",
        "text": text,
        "output_path": str(output_path),
    }

    _process.stdin.write(
        json.dumps(request) + "\n"
    )

    _process.stdin.flush()

    response_line = (
        _process.stdout.readline().strip()
    )

    if not response_line:
        raise RuntimeError(
            "XTTS service returned no response."
        )

    response = json.loads(response_line)

    if response.get("status") != "ok":
        raise RuntimeError(
            f"XTTS generation failed: {response}"
        )


def _play_audio(
    output_path: Path,
):
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


def speak_xtts(
    text: str,
) -> None:
    """
    Generate and play speech using the persistent
    XTTS v2 service.
    """

    if not text:
        return

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / "jarvis_output.wav"
    )

    with _lock:

        _start_service()

        _generate(
            text,
            output_path,
        )

        _play_audio(
            output_path,
        )