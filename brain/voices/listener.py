import time

import pyaudio
import numpy as np
import openwakeword

from openwakeword.model import Model
import speech_recognition as sr

WAKE_WORD = "hey_jarvis"
WAKE_THRESHOLD = 0.5

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280


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

        self.wake_model = Model(wakeword_models=[WAKE_WORD], inference_framework="onnx")

        self.wake_stream = None

        # Controls the lifetime of the listener.
        self.running = True

        self._calibrate_microphone()

    def _calibrate_microphone(self):
        """
        Calibrates the microphone once.
        """

        print("JARVIS: Calibrating microphone...")

        with self.microphone as source:

            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        print("JARVIS: Microphone ready.")

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

    def listen_for_wake_word(self):
        """
        Waits for the local JARVIS wake word.
        """

        self._start_wake_stream()

        print("JARVIS: Waiting for wake word...")

        while self.running:

            audio_data = self.wake_stream.read(CHUNK_SIZE, exception_on_overflow=False)

            audio_frame = np.frombuffer(audio_data, dtype=np.int16)

            prediction = self.wake_model.predict(audio_frame)

            score = prediction.get(WAKE_WORD, 0)

            if score >= WAKE_THRESHOLD:

                print(f"JARVIS: Wake word detected " f"(score: {score:.2f})")

                # Stop listening for the wake word
                # while JARVIS processes the command.
                self._stop_wake_stream()

                # Reset model state so old audio
                # cannot trigger it again.
                self._reset_wake_model()

                return True

        return False

    def listen_for_command(self):
        """
        Listens for a command after activation.
        """

        if not self.running:
            return ""

        with self.microphone as source:

            print("JARVIS: Listening...")

            try:

                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)

            except sr.WaitTimeoutError:

                print("JARVIS: I didn't hear a command.")

                return ""

        if not self.running:
            return ""

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

    def prepare_for_wake_word(self):
        """
        Prepares the wake-word detector for a new cycle.
        """

        if not self.running:
            return

        self._reset_wake_model()

        # Small cooldown prevents audio from the previous
        # interaction from immediately triggering JARVIS.
        time.sleep(0.5)

    def stop(self):
        """
        Requests the listener to stop.
        """

        self.running = False

    def close(self):
        """
        Releases all microphone resources.
        """

        self.running = False

        self._stop_wake_stream()

        self.audio.terminate()
