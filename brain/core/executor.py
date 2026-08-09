import json
import os
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import quote

from brain.media.youtube_player import play_youtube
from brain.media.chrome_controller import play_youtube_music

# ==========================================
# APPLICATIONS
# ==========================================

APPLICATIONS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
}


# ==========================================
# CHROME
# ==========================================


def get_chrome_profiles():
    """
    Retrieves available Chrome profiles
    from the Chrome configuration.
    """

    local_state_path = os.path.join(
        os.environ["LOCALAPPDATA"],
        "Google",
        "Chrome",
        "User Data",
        "Local State",
    )

    try:

        with open(
            local_state_path,
            "r",
            encoding="utf-8",
        ) as file:

            local_state = json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):

        return {}

    profile_info = local_state.get(
        "profile",
        {},
    ).get(
        "info_cache",
        {},
    )

    return profile_info


def open_chrome(profile_directory):
    """
    Opens Chrome using the selected profile
    directory.
    """

    if not profile_directory:

        return "No Chrome profile was selected."

    profiles = get_chrome_profiles()

    selected_profile = profiles.get(
        profile_directory,
        {},
    )

    selected_name = selected_profile.get(
        "name",
        "Unknown",
    )

    chrome_path = APPLICATIONS["chrome"]

    try:

        subprocess.Popen(
            [
                chrome_path,
                f"--profile-directory={profile_directory}",
            ]
        )

        return f"Opening {selected_name}."

    except OSError:

        return f"I couldn't open {selected_name}."


# ==========================================
# SYSTEM COMMANDS
# ==========================================


def execute_system_command(target):
    """
    Executes a system command after
    user confirmation.
    """

    if target == "shutdown":

        confirmation = input(
            "JARVIS: Are you sure you want to shut down " "the computer? (yes/no): "
        )

        if confirmation.lower() == "yes":

            subprocess.Popen(
                [
                    "shutdown",
                    "/s",
                    "/t",
                    "5",
                ]
            )

            return "Shutting down the computer in 5 seconds."

        return "Shutdown cancelled."

    if target == "restart":

        confirmation = input(
            "JARVIS: Are you sure you want to restart " "the computer? (yes/no): "
        )

        if confirmation.lower() == "yes":

            subprocess.Popen(
                [
                    "shutdown",
                    "/r",
                    "/t",
                    "5",
                ]
            )

            return "Restarting the computer in 5 seconds."

        return "Restart cancelled."

    return f"I don't know how to perform {target}."


# ==========================================
# FILESYSTEM
# ==========================================


def get_available_drives():
    """
    Returns available Windows drives with
    C: searched last.
    """

    drives = []

    for drive_letter in "DEFGHIJKLMNOPQRSTUVWXYZ":

        drive = f"{drive_letter}:\\"

        if os.path.exists(drive):

            drives.append(drive)

    if os.path.exists("C:\\"):

        drives.append("C:\\")

    return drives


def find_filesystem_matches(target):
    """
    Searches for files and folders and returns
    their actual paths.

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
            drive,
            topdown=True,
            onerror=lambda error: None,
        ):

            directories[:] = [
                directory
                for directory in directories
                if directory not in excluded_directories
                and not directory.startswith(".")
            ]

            # -------------------------
            # SEARCH FOLDERS
            # -------------------------

            for directory in directories:

                if directory.lower() == target.lower():

                    folder_matches.append(
                        os.path.join(
                            root,
                            directory,
                        )
                    )

            # -------------------------
            # SEARCH FILES
            # -------------------------

            for file in files:

                if file.lower() == target.lower():

                    file_matches.append(
                        os.path.join(
                            root,
                            file,
                        )
                    )

        if (file_matches or folder_matches) and drive != "C:\\":

            break

    return file_matches, folder_matches


def search_filesystem(target):
    """
    Searches for both files and folders and
    returns a human-readable result.
    """

    if not target:

        return "Please tell me the name " "of the file or folder."

    file_matches, folder_matches = find_filesystem_matches(target)

    total_matches = len(file_matches) + len(folder_matches)

    if total_matches == 0:

        return f"I couldn't find {target}."

    if total_matches == 1:

        if file_matches:

            return f"I found the file {target}.\n" f"Location: {file_matches[0]}"

        return f"I found the folder {target}.\n" f"Location: {folder_matches[0]}"

    response = f"I found {total_matches} " f"matches for {target}:\n"

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
    Opens a file using its default
    Windows application.
    """

    try:

        os.startfile(path)

        return f"Opening " f"{os.path.basename(path)}."

    except OSError:

        return f"I couldn't open " f"{os.path.basename(path)}."


def open_folder(path):
    """
    Opens a folder in Windows File Explorer.
    """

    try:

        os.startfile(path)

        return f"Opening folder " f"{os.path.basename(path)}."

    except OSError:

        return f"I couldn't open folder " f"{os.path.basename(path)}."


# ==========================================
# MEDIA
# ==========================================


def play_media(
    target,
    profile_directory=None,
):
    """
    Plays requested media.

    Normal media uses YouTube.

    If the target explicitly mentions
    YouTube Music, the real Chrome profile
    is used with the YouTube Music controller.
    """

    if not target:

        return "What would you like me to play?"

    target_lower = target.lower().strip()

    # ======================================
    # YOUTUBE MUSIC DETECTION
    # ======================================

    youtube_music_phrases = (
        "in youtube music",
        "on youtube music",
        "using youtube music",
        "through youtube music",
    )

    youtube_music = any(phrase in target_lower for phrase in youtube_music_phrases)

    if youtube_music:

        query = target

        for phrase in youtube_music_phrases:

            query = query.lower().replace(
                phrase,
                "",
            )

        query = query.strip()

        # Remove common leading words.
        for prefix in (
            "play ",
            "listen to ",
            "put ",
        ):

            if query.startswith(prefix):

                query = query[len(prefix) :].strip()

        if not query:

            return "What would you like me " "to play on YouTube Music?"

        print("JARVIS: Playing on YouTube Music: " f"{query}")

        success = play_youtube_music(
            query,
            profile_directory,
        )

        if success:

            return f"Playing {query} " "on YouTube Music."

        return f"I couldn't play {query} " "on YouTube Music."

    # ======================================
    # NORMAL YOUTUBE
    # ======================================

    success = play_youtube(
        target,
        profile_directory,
    )

    if success:

        return f"Playing {target}."

    return f"I couldn't play {target}."


# ==========================================
# UI AUTOMATION
# ==========================================


def run_ui_automation_test():
    """
    Runs the JARVIS UI automation test.
    """

    from brain.automation.ui_monitor import (
        UIElementMonitor,
    )

    monitor = UIElementMonitor()

    try:

        html_file = (
            Path(__file__).resolve().parents[2] / "tests" / "automation_test.html"
        )

        if not html_file.exists():

            return "The UI automation test file " "could not be found."

        url = html_file.as_uri()

        monitor.open_page(url)

        success = monitor.wait_and_click("#test-button")

        if success:

            return "UI automation test " "completed successfully."

        return "UI automation test failed."

    except Exception as error:

        print("JARVIS UI Automation Error: " f"{error}")

        return "I couldn't complete the " "UI automation test."

    finally:

        monitor.close()


# ==========================================
# ACKNOWLEDGEMENT
# ==========================================


def get_acknowledgement(command):
    """
    Generates a response that JARVIS can speak
    before performing the requested action.
    """

    intent = command["intent"]
    target = command["target"]

    # ==========================================
    # OPEN APPLICATION
    # ==========================================

    if intent == "OPEN_APPLICATION":

        if target == "chrome":

            return "Opening Chrome."

        if target in APPLICATIONS:

            return f"Opening {target}."

        return f"Searching for {target}."

    # ==========================================
    # PLAY MEDIA
    # ==========================================

    if intent == "PLAY_MEDIA":

        if not target:

            return "What would you like " "me to play?"

        target_lower = target.lower()

        if "youtube music" in target_lower:

            return "Playing on YouTube Music."

        return f"Playing {target}."

    # ==========================================
    # WEB SEARCH
    # ==========================================

    if intent == "WEB_SEARCH":

        if not target:

            return "What would you like " "me to search for?"

        return f"Searching for {target}."

    # ==========================================
    # SYSTEM COMMAND
    # ==========================================

    if intent == "SYSTEM_COMMAND":

        if target == "shutdown":

            return "Preparing to shut down " "the computer."

        if target == "restart":

            return "Preparing to restart " "the computer."

        return f"Preparing to perform {target}."

    # ==========================================
    # FILE SEARCH
    # ==========================================

    if intent == "FILE_SEARCH":

        return f"Searching for {target}."

    # ==========================================
    # UI AUTOMATION
    # ==========================================

    if intent == "UI_AUTOMATION":

        return "Starting UI automation."

    # ==========================================
    # DEFAULT
    # ==========================================

    return "I'll take care of that."


# ==========================================
# MAIN EXECUTOR
# ==========================================


def execute(command):
    """
    Executes the command based on its intent.
    """

    intent = command["intent"]
    target = command["target"]

    # ==========================================
    # OPEN APPLICATION
    # ==========================================

    if intent == "OPEN_APPLICATION":

        if target == "chrome":

            return "Chrome profile selection " "required."

        application = APPLICATIONS.get(target)

        if application:

            try:

                subprocess.Popen(application)

                return f"Opening {target}."

            except OSError:

                return f"I couldn't open " f"{target}."

        file_matches, folder_matches = find_filesystem_matches(target)

        if file_matches:

            return open_file(file_matches[0])

        if folder_matches:

            return open_folder(folder_matches[0])

        return f"I couldn't find {target}."

    # ==========================================
    # PLAY MEDIA
    # ==========================================

    if intent == "PLAY_MEDIA":

        profile_directory = command.get("profile_directory")

        return play_media(
            target,
            profile_directory,
        )

    # ==========================================
    # WEB SEARCH
    # ==========================================

    if intent == "WEB_SEARCH":

        if not target:

            return "What would you like " "me to search for?"

        search_url = "https://www.google.com/search?q=" + quote(target)

        webbrowser.open(search_url)

        return f"Searching for {target}."

    # ==========================================
    # SYSTEM COMMAND
    # ==========================================

    if intent == "SYSTEM_COMMAND":

        return execute_system_command(target)

    # ==========================================
    # FILE SEARCH
    # ==========================================

    if intent == "FILE_SEARCH":

        return search_filesystem(target)

    # ==========================================
    # UI AUTOMATION
    # ==========================================

    if intent == "UI_AUTOMATION":

        return run_ui_automation_test()

    # ==========================================
    # UNKNOWN
    # ==========================================

    return "I don't know how to execute " "that command."
