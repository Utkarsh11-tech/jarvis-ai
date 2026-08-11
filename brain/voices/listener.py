import time

import pyaudio
import numpy as np
import openwakeword

from openwakeword.model import Model
import speech_recognition as sr

# ==================================================
# CONFIGURATION
# ==================================================

WAKE_WORD = "hey_jarvis"
WAKE_THRESHOLD = 0.5

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280

# Maximum time JARVIS waits for the user to
# START speaking after wake word detection.
COMMAND_TIMEOUT = 5

# Maximum length of a spoken command.
COMMAND_PHRASE_TIME_LIMIT = 8


class VoiceListener:

    def __init__(self):
        """
        Initializes the wake-word detector and
        speech recognition system.
        """

        self.recognizer = sr.Recognizer()

        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5

        self.microphone = sr.Microphone()

        self.audio = pyaudio.PyAudio()

        openwakeword.utils.download_models(model_names=["hey_jarvis"])

        self.wake_model = Model(
            wakeword_models=[WAKE_WORD],
            inference_framework="onnx",
        )

        self.wake_stream = None

        # Controls the lifetime of the listener.
        self.running = True

        # Indicates that JARVIS needs
        # follow-up voice input.
        self.follow_up_requested = False

        self._calibrate_microphone()

    # ==================================================
    # MICROPHONE CALIBRATION
    # ==================================================

    def _calibrate_microphone(self):
        """
        Calibrates the microphone once.
        """

        print("JARVIS: Calibrating microphone...")

        with self.microphone as source:

            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=1,
            )

        print("JARVIS: Microphone ready.")

    # ==================================================
    # WAKE WORD STREAM
    # ==================================================

    def _start_wake_stream(self):
        """
        Starts the wake-word microphone stream.
        """

        if self.wake_stream is not None:
            return

        self.wake_stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )

    def _stop_wake_stream(self):
        """
        Stops the wake-word microphone stream.
        """

        if self.wake_stream is None:
            return

        self.wake_stream.stop_stream()
        self.wake_stream.close()

        self.wake_stream = None

    def _reset_wake_model(self):
        """
        Resets the wake-word detector after activation.
        """

        self.wake_model.reset()

    # ==================================================
    # WAKE WORD DETECTION
    # ==================================================

    def listen_for_wake_word(self):
        """
        Waits for the local JARVIS wake word.
        """

        self._start_wake_stream()

        print("JARVIS: Waiting for wake word...")

        while self.running:

            # ------------------------------------------
            # FOLLOW-UP INTERRUPTION
            # ------------------------------------------

            if self.follow_up_requested:

                self.follow_up_requested = False

                self._stop_wake_stream()

                return False

            # ------------------------------------------
            # READ MICROPHONE
            # ------------------------------------------

            audio_data = self.wake_stream.read(
                CHUNK_SIZE,
                exception_on_overflow=False,
            )

            audio_frame = np.frombuffer(
                audio_data,
                dtype=np.int16,
            )

            prediction = self.wake_model.predict(audio_frame)

            score = prediction.get(
                WAKE_WORD,
                0,
            )

            if score >= WAKE_THRESHOLD:

                print(f"JARVIS: Wake word detected " f"(score: {score:.2f})")

                self._stop_wake_stream()

                self._reset_wake_model()

                return True

        return False

    # ==================================================
    # COMMAND LISTENING
    # ==================================================

    def listen_for_command(self):
        """
        Listens for a spoken command.

        JARVIS waits COMMAND_TIMEOUT seconds for the
        user to start speaking.

        Once speech begins, JARVIS listens for a
        maximum of COMMAND_PHRASE_TIME_LIMIT seconds.
        """

        if not self.running:
            return ""

        print(f"JARVIS: Listening for command " f"(timeout: {COMMAND_TIMEOUT}s)...")

        try:

            with self.microphone as source:

                audio = self.recognizer.listen(
                    source,
                    timeout=COMMAND_TIMEOUT,
                    phrase_time_limit=COMMAND_PHRASE_TIME_LIMIT,
                )

        except sr.WaitTimeoutError:

            print("JARVIS: Command timeout.")

            return ""

        if not self.running:
            return ""

        # ==========================================
        # SPEECH RECOGNITION
        # ==========================================

        try:

            text = self.recognizer.recognize_google(audio)

            text = text.lower().strip()

            print(f"You said: {text}")

            return text

        except sr.UnknownValueError:

            print("JARVIS: I couldn't understand that.")

            return ""

        except sr.RequestError:

            print("JARVIS: Speech recognition service " "is unavailable.")

            return ""

    # ==================================================
    # REQUEST FOLLOW-UP
    # ==================================================

    def request_follow_up(self):
        """
        Interrupts wake-word listening so JARVIS
        can listen for a follow-up response.
        """

        self.follow_up_requested = True

    # ==================================================
    # PREPARE FOR NEXT WAKE WORD
    # ==================================================

    def prepare_for_wake_word(self):
        """
        Prepares the wake-word detector for
        a new listening cycle.
        """

        if not self.running:
            return

        self._reset_wake_model()

        # Small cooldown prevents audio from the
        # previous interaction from immediately
        # triggering JARVIS.

        time.sleep(0.5)

    # ==================================================
    # STOP
    # ==================================================

    def stop(self):
        """
        Requests the listener to stop.
        """

        self.running = False

        self._stop_wake_stream()

    # ==================================================
    # CLOSE
    # ==================================================

    def close(self):
        """
        Releases all microphone resources.
        """

        self.running = False

        self._stop_wake_stream()

        self.audio.terminate()
