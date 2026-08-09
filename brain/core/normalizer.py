# ==========================================
# COMMAND NORMALIZER
# ==========================================


FILLER_PHRASES = [
    "could you please ",
    "could you ",
    "can you please ",
    "can you ",
    "would you please ",
    "would you ",
    "please ",
    "i want you to ",
    "i want to ",
    "i would like you to ",
    "i would like to ",
    "i'd like you to ",
    "i'd like to ",
]


def normalize(command):
    """
    Cleans and standardizes user input.

    Removes unnecessary conversational phrases
    while preserving the actual command.
    """

    if not command:
        return ""

    # ==========================================
    # BASIC CLEANING
    # ==========================================

    command = command.strip().lower()

    # ==========================================
    # REMOVE PUNCTUATION
    # ==========================================

    punctuation = ".,!?;:"

    command = command.translate(
        str.maketrans(
            "",
            "",
            punctuation,
        )
    )

    command = " ".join(command.split())

    # ==========================================
    # REMOVE FILLER PHRASES
    # ==========================================

    for phrase in FILLER_PHRASES:

        if command.startswith(phrase):

            command = command[len(phrase) :]

            break

    # ==========================================
    # FINAL CLEANING
    # ==========================================

    command = " ".join(command.split())

    return command
