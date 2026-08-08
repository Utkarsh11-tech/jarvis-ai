from pathlib import Path
import subprocess
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "en_GB-northern_english_male-medium.onnx"


def speak_offline(text: str) -> None:
    """
    Speaks text using the local Piper JARVIS voice.
    """

    if not text:
        return

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Piper model not found: {MODEL_PATH}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:

        output_path = Path(temp_file.name)

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "piper",
                "-m",
                str(MODEL_PATH),
                "-f",
                str(output_path),
            ],
            input=text,
            text=True,
            check=True,
        )

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

    finally:
        if output_path.exists():
            output_path.unlink()
