import contextlib
import io
import json
import os
import sys
import traceback
from pathlib import Path

import torch
import torchaudio
from TTS.api import TTS


PROJECT_ROOT = Path(__file__).resolve().parents[2]

VOICE_PATH = (
    PROJECT_ROOT
    / "voice-lab"
    / "jarvis voice"
    / "voice4.wav"
)

MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"

SPEED = 1.15
LANGUAGE = "en"


def log(message):
    print(
        message,
        file=sys.stderr,
        flush=True,
    )


def send_response(data):
    print(
        json.dumps(data),
        flush=True,
    )


def main():

    if not torch.cuda.is_available():

        send_response(
            {
                "status": "error",
                "message": "CUDA is not available.",
            }
        )

        return

    if not VOICE_PATH.exists():

        send_response(
            {
                "status": "error",
                "message": f"Voice reference not found: {VOICE_PATH}",
            }
        )

        return

    log("XTTS: Loading model...")

    try:

        # Keep Coqui startup logs away from
        # the JSON communication channel.
        with contextlib.redirect_stdout(io.StringIO()):

            tts = TTS(
                MODEL_NAME
            ).to("cuda")

        model = tts.synthesizer.tts_model

        log("XTTS: Computing speaker conditioning...")

        with contextlib.redirect_stdout(io.StringIO()):

            (
                gpt_cond_latent,
                speaker_embedding,
            ) = model.get_conditioning_latents(
                audio_path=[
                    str(VOICE_PATH)
                ]
            )

        log("XTTS: Model ready.")

        send_response(
            {
                "status": "ready",
                "gpu": torch.cuda.get_device_name(0),
            }
        )

    except Exception as error:

        log(traceback.format_exc())

        send_response(
            {
                "status": "error",
                "message": str(error),
            }
        )

        return

    # ==================================================
    # REQUEST LOOP
    # ==================================================

    for line in sys.stdin:

        line = line.strip()

        if not line:
            continue

        try:

            request = json.loads(line)

            command = request.get(
                "command"
            )

            # ------------------------------------------
            # SHUTDOWN
            # ------------------------------------------

            if command == "shutdown":

                send_response(
                    {
                        "status": "shutdown",
                    }
                )

                break

            # ------------------------------------------
            # SPEAK
            # ------------------------------------------

            if command != "speak":

                send_response(
                    {
                        "status": "error",
                        "message": "Unknown command.",
                    }
                )

                continue

            text = request.get(
                "text",
                "",
            ).strip()

            output_path = request.get(
                "output_path",
                "",
            )

            if not text:

                send_response(
                    {
                        "status": "error",
                        "message": "No text provided.",
                    }
                )

                continue

            if not output_path:

                send_response(
                    {
                        "status": "error",
                        "message": "No output path provided.",
                    }
                )

                continue

            log(
                f"XTTS: Generating speech: {text}"
            )

            with contextlib.redirect_stdout(
                io.StringIO()
            ):

                result = model.inference(
                    text=text,
                    language=LANGUAGE,
                    gpt_cond_latent=gpt_cond_latent,
                    speaker_embedding=speaker_embedding,
                    speed=SPEED,
                    enable_text_splitting=True,
                )

            waveform = torch.tensor(
                result["wav"]
            ).unsqueeze(0)

            torchaudio.save(
                output_path,
                waveform.cpu(),
                24000,
            )

            send_response(
                {
                    "status": "ok",
                    "output_path": output_path,
                }
            )

        except Exception as error:

            log(traceback.format_exc())

            send_response(
                {
                    "status": "error",
                    "message": str(error),
                }
            )


if __name__ == "__main__":
    main()