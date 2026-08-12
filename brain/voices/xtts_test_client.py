import json
import subprocess
import time

SERVICE_PYTHON = r"E:\Github\jarvis-ai\voice-lab\Scripts\python.exe"
SERVICE_SCRIPT = r"E:\Github\jarvis-ai\brain\voices\xtts_service.py"

OUTPUT = (
    r"E:\Github\jarvis-ai\voice-lab\jarvis voice\service_test.wav"
)

print("Starting XTTS service...")

service = subprocess.Popen(
    [
        SERVICE_PYTHON,
        SERVICE_SCRIPT,
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=None,
    text=True,
    bufsize=1,
)

# --------------------------------------------------
# WAIT FOR READY
# --------------------------------------------------

ready = service.stdout.readline().strip()

print("SERVICE:", ready)

if '"status": "ready"' not in ready:

    print("XTTS service failed to initialize.")

    service.terminate()
    raise SystemExit(1)


# --------------------------------------------------
# SEND SPEAK REQUEST
# --------------------------------------------------

request = {
    "command": "speak",
    "text": (
        "Good evening, sir. "
        "All systems are operating normally."
    ),
    "output_path": OUTPUT,
}

print("Sending speech request...")

start = time.perf_counter()

service.stdin.write(
    json.dumps(request) + "\n"
)

service.stdin.flush()

response = service.stdout.readline().strip()

elapsed = time.perf_counter() - start

print("RESPONSE:", response)
print(f"Generation time: {elapsed:.2f} seconds")


# --------------------------------------------------
# SHUTDOWN
# --------------------------------------------------

service.stdin.write(
    json.dumps({"command": "shutdown"}) + "\n"
)

service.stdin.flush()

service.wait()

print()
print("XTTS service stopped.")
print("Output:", OUTPUT)