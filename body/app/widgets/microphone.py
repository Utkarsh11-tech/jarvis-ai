import numpy as np
import sounddevice as sd

from PySide6.QtCore import QObject, Signal


class Microphone(QObject):
    level_changed = Signal(float)

    def __init__(self):
        super().__init__()

        self.stream = None

    def start(self):
        if self.stream is not None:
            return

        self.stream = sd.InputStream(
            channels=1,
            samplerate=44100,
            blocksize=1024,
            dtype="float32",
            callback=self._audio_callback
        )

        self.stream.start()

    def stop(self):
        if self.stream is None:
            return

        self.stream.stop()
        self.stream.close()

        self.stream = None

    def _audio_callback(
        self,
        indata,
        frames,
        time,
        status
    ):
        if status:
            print(status)

        audio = indata[:, 0]

        # Calculate RMS volume
        rms = np.sqrt(
            np.mean(
                np.square(audio)
            )
        )

        # Convert microphone volume
        # to a 0.0 - 1.0 range
        level = min(
            1.0,
            rms * 8
        )

        self.level_changed.emit(
            float(level)
        )