import json
import os
import subprocess
import webbrowser
from urllib.parse import quote

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


def execute_system_command(target):
    """
    Executes a system command after user confirmation.
    """

    if target == "shutdown":
        confirmation = input(
            "JARVIS: Are you sure you want to shut down " "the computer? (yes/no): "
        )

        if confirmation.lower() == "yes":
            subprocess.Popen(["shutdown", "/s", "/t", "5"])
            return "Shutting down the computer in 5 seconds."

        return "Shutdown cancelled."

    if target == "restart":
        confirmation = input(
            "JARVIS: Are you sure you want to restart " "the computer? (yes/no): "
        )

        if confirmation.lower() == "yes":
            subprocess.Popen(["shutdown", "/r", "/t", "5"])
            return "Restarting the computer in 5 seconds."

        return "Restart cancelled."

    return f"I don't know how to perform {target}."


def get_available_drives():
    """
    Returns available Windows drives with C: searched last.
    """

    drives = []

    # Search non-system drives first.
    for drive_letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{drive_letter}:\\"

        if os.path.exists(drive):
            drives.append(drive)

    # Search C: only as a last resort.
    if os.path.exists("C:\\"):
        drives.append("C:\\")

    return drives


def find_filesystem_matches(target):
    """
    Searches for files and folders and returns their actual paths.

    Non-C drives are searched first.
    C: is searched last.
    """

    if not target:
        return [], []

    target = target.strip()

    if not target:
        return [], []

    drives = get_available_drives()

    file_matches = []
    folder_matches = []

    excluded_directories = {
        "$Recycle.Bin",
        "System Volume Information",
        "Recovery",
        "WindowsApps",
    }

    for drive in drives:

        print(f"JARVIS: Searching {drive}...")

        for root, directories, files in os.walk(
            drive, topdown=True, onerror=lambda error: None
        ):

            directories[:] = [
                directory
                for directory in directories
                if directory not in excluded_directories
                and not directory.startswith(".")
            ]

            # Search folders.
            for directory in directories:

                if directory.lower() == target.lower():
                    folder_matches.append(os.path.join(root, directory))

            # Search files.
            for file in files:

                if file.lower() == target.lower():
                    file_matches.append(os.path.join(root, file))

        # Stop searching after finding a result on
        # a non-C drive.
        if (file_matches or folder_matches) and drive != "C:\\":
            break

    return file_matches, folder_matches


def search_filesystem(target):
    """
    Searches for both files and folders and returns
    a human-readable result.
    """

    if not target:
        return "Please tell me the name of the file or folder."

    file_matches, folder_matches = find_filesystem_matches(target)

    total_matches = len(file_matches) + len(folder_matches)

    if total_matches == 0:
        return f"I couldn't find {target}."

    if total_matches == 1:

        if file_matches:
            return f"I found the file {target}.\n" f"Location: {file_matches[0]}"

        return f"I found the folder {target}.\n" f"Location: {folder_matches[0]}"

    response = f"I found {total_matches} matches for {target}:\n"

    counter = 1

    for match in file_matches:
        response += f"{counter}. [FILE] {match}\n"
        counter += 1

    for match in folder_matches:
        response += f"{counter}. [FOLDER] {match}\n"
        counter += 1

    return response.rstrip()


def open_file(path):
    """
    Opens a file using its default Windows application.
    """

    try:
        os.startfile(path)
        return f"Opening {os.path.basename(path)}."

    except OSError:
        return f"I couldn't open {os.path.basename(path)}."


def open_folder(path):
    """
    Opens a folder in Windows File Explorer.
    """

    try:
        os.startfile(path)
        return f"Opening folder {os.path.basename(path)}."

    except OSError:
        return f"I couldn't open folder {os.path.basename(path)}."


def execute(command):
    """
    Executes the command based on its intent.
    """

    intent = command["intent"]
    target = command["target"]

    if intent == "OPEN_APPLICATION":

        # Check registered applications first.
        if target == "chrome":
            return open_chrome()

        application = APPLICATIONS.get(target)

        if application:
            subprocess.Popen(application)
            return f"Opening {target}"

        # If it isn't an application, search for a
        # matching file or folder.
        file_matches, folder_matches = find_filesystem_matches(target)

        if file_matches:
            return open_file(file_matches[0])

        if folder_matches:
            return open_folder(folder_matches[0])

        return f"I couldn't find {target}."

    if intent == "WEB_SEARCH":

        if not target:
            return "What would you like me to search for?"

        search_url = "https://www.google.com/search?q=" + quote(target)

        webbrowser.open(search_url)

        return f"Searching for {target}"

    if intent == "SYSTEM_COMMAND":
        return execute_system_command(target)

    if intent == "FILE_SEARCH":
        return search_filesystem(target)

    return "I don't know how to execute that command."
