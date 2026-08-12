import json
import os
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

# FFmpeg shared build required by TorchCodec on Windows.
FFMPEG_BIN = Path(
    r"C:\ffmpeg-shared\ffmpeg-8.1.2-full_build-shared\bin"
)


_process = None
_lock = threading.Lock()


def _get_service_environment():
    """
    Build the environment used by the XTTS service.

    TorchCodec needs the FFmpeg shared DLLs to be discoverable
    when the XTTS Python process starts.
    """

    env = os.environ.copy()

    if FFMPEG_BIN.exists():
        env["PATH"] = (
            str(FFMPEG_BIN)
            + os.pathsep
            + env.get("PATH", "")
        )

    return env


def _start_service():
    global _process

    if _process is not None:
        if _process.poll() is None:
            return

    if not SERVICE_PYTHON.exists():
        raise FileNotFoundError(
            f"XTTS Python executable not found: {SERVICE_PYTHON}"
        )

    if not SERVICE_SCRIPT.exists():
        raise FileNotFoundError(
            f"XTTS service script not found: {SERVICE_SCRIPT}"
        )

    if not FFMPEG_BIN.exists():
        raise FileNotFoundError(
            f"FFmpeg shared DLL directory not found: {FFMPEG_BIN}"
        )

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
        env=_get_service_environment(),
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


def _generate(text: str, output_path: Path):
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


def _play_audio(output_path: Path):
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
        env=_get_service_environment(),
    )


def speak_xtts(text: str) -> None:
    """
    Generate and play speech using the persistent XTTS v2 service.
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
            output_path
        )