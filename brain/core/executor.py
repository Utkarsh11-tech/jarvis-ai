import json
import os
import subprocess

APPLICATIONS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
}


def get_chrome_profiles():
    """
    Retrieves available Chrome profiles from the Chrome configuration.
    """

    local_state_path = os.path.join(
        os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data", "Local State"
    )

    try:
        with open(local_state_path, "r", encoding="utf-8") as file:
            local_state = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return {}

    profile_info = local_state.get("profile", {}).get("info_cache", {})

    return profile_info


def open_chrome():
    """
    Displays available Chrome profiles and opens the selected one.
    """

    profiles = get_chrome_profiles()

    if not profiles:
        return "No Chrome profiles were found."

    profile_list = list(profiles.items())

    print("\nAvailable Chrome profiles:")

    for index, (profile_directory, profile_data) in enumerate(profile_list, start=1):
        profile_name = profile_data.get("name", "Unknown")
        print(f"{index}. {profile_name}")

    while True:
        choice = input("JARVIS: Select a profile number: ")

        if choice.isdigit():
            choice = int(choice)

            if 1 <= choice <= len(profile_list):
                break

        print("JARVIS: Please select a valid profile number.")

    selected_directory, selected_profile = profile_list[choice - 1]
    selected_name = selected_profile.get("name", "Unknown")

    chrome_path = APPLICATIONS["chrome"]

    try:
        subprocess.Popen([chrome_path, f"--profile-directory={selected_directory}"])

        return f"Opening {selected_name}."

    except OSError:
        return f"I couldn't open {selected_name}."


def execute(command):
    """
    Executes the command based on its intent.
    """

    intent = command["intent"]
    target = command["target"]

    if intent == "OPEN_APPLICATION":

        if target == "chrome":
            return open_chrome()

        application = APPLICATIONS.get(target)

        if application:
            subprocess.Popen(application)
            return f"Opening {target}"

        return f"I don't know how to open {target}"

    return "I don't know how to execute that command."
