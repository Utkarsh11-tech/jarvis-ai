import pyaudio
import numpy as np
import openwakeword
from openwakeword.model import Model

openwakeword.utils.download_models(model_names=["hey_jarvis"])

model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")

audio = pyaudio.PyAudio()

stream = audio.open(
    format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1280
)

print("JARVIS: Wake-word detector active.")
print('Say "Hey JARVIS"...')


try:

    while True:

        audio_data = stream.read(1280, exception_on_overflow=False)

        audio_frame = np.frombuffer(audio_data, dtype=np.int16)

        prediction = model.predict(audio_frame)

        score = prediction.get("hey_jarvis", 0)

        if score > 0.5:
            print(f"JARVIS: Wake word detected! " f"(score: {score:.2f})")
            break

finally:

    stream.stop_stream()
    stream.close()
    audio.terminate()
