from brain.voices.listener import listen


text = listen()

if text:
    print(f"Recognized: {text}")