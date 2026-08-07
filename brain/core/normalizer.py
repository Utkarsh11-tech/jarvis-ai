def normalize(command):
    """
    Cleans and standardizes user input.
    """

    command = command.strip()
    command = command.lower()
    command = " ".join(command.split())

    return command