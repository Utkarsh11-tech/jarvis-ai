# ==========================================
# COMMAND NORMALIZER
# ==========================================


FILLER_PHRASES = [
    "could you please ",
    "could you ",
    "can you please ",
    "can you ",
    "would you mind ",
    "would you please ",
    "would you ",
    "do you mind ",
    "please ",
    "i want you to ",
    "i want to ",
    "i would like you to ",
    "i would like to ",
    "i'd like you to ",
    "i'd like to ",
]


ENDING_PHRASES = [
    " for me",
    " please",
]


ACTION_FORMS = {
    # Search
    "searching for ": "search ",
    "searching ": "search ",
    "looking for ": "search ",
    "looking up ": "lookup ",
    # Opening
    "opening ": "open ",
    "launching ": "launch ",
    "starting ": "start ",
    "running ": "run ",
    "loading ": "load ",
    # Playing
    "playing ": "play ",
    "listening to ": "listen to ",
}


def normalize(command):
    """
    Cleans and standardizes user input.

    Removes conversational filler, converts
    common grammatical forms into canonical
    commands, and preserves the meaningful target.
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
    # REMOVE FILLER AT START
    # ==========================================

    for phrase in FILLER_PHRASES:

        if command.startswith(phrase):

            command = command[len(phrase) :]

            break

    # ==========================================
    # NORMALIZE ACTION FORMS
    # ==========================================

    for phrase, replacement in ACTION_FORMS.items():

        if command.startswith(phrase):

            command = replacement + command[len(phrase) :]

            break

    # ==========================================
    # REMOVE ENDING PHRASES
    # ==========================================

    for phrase in ENDING_PHRASES:

        if command.endswith(phrase):

            command = command[: -len(phrase)]

            break

    # ==========================================
    # FINAL CLEANING
    # ==========================================

    command = " ".join(command.split())

    return command
