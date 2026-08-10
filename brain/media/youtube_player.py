import re
import time
from urllib.parse import quote

import requests

import win32api
import win32con

from brain.media.chrome_controller import (
    open_real_chrome_profile,
    wait_for_window,
    activate_chrome_window,
)

# ==========================================
# YOUTUBE CONFIGURATION
# ==========================================

YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query="

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}


# ==========================================
# FIND YOUTUBE VIDEO
# ==========================================


def find_first_youtube_video(query):
    """
    Searches YouTube and extracts the first
    available video ID.

    This does not launch Chrome.
    """

    if not query:
        return None

    search_url = YOUTUBE_SEARCH_URL + quote(query)

    print("JARVIS: Searching YouTube for " f"{query}...")

    try:

        response = requests.get(
            search_url,
            headers=REQUEST_HEADERS,
            timeout=10,
        )

        response.raise_for_status()

    except requests.RequestException as error:

        print("JARVIS: YouTube search failed: " f"{error}")

        return None

    html = response.text

    video_ids = re.findall(
        r'"videoId":"([A-Za-z0-9_-]{11})"',
        html,
    )

    unique_video_ids = []

    for video_id in video_ids:

        if video_id not in unique_video_ids:

            unique_video_ids.append(video_id)

    if not unique_video_ids:

        print("JARVIS: No YouTube videos " "were found.")

        return None

    first_video_id = unique_video_ids[0]

    video_url = "https://www.youtube.com/watch?v=" + first_video_id

    print("JARVIS: Found YouTube video: " f"{video_url}")

    return video_url


# ==========================================
# PRESS YOUTUBE PLAY / PAUSE KEY
# ==========================================


def press_youtube_play():
    """
    Sends the YouTube K keyboard shortcut.

    K toggles Play/Pause when the YouTube
    player/page has focus.
    """

    print("JARVIS: Sending YouTube Play command...")

    try:

        win32api.keybd_event(
            ord("K"),
            0,
            0,
            0,
        )

        win32api.keybd_event(
            ord("K"),
            0,
            win32con.KEYEVENTF_KEYUP,
            0,
        )

        time.sleep(2)

        print("JARVIS: YouTube Play command sent.")

        return True

    except Exception as error:

        print("JARVIS: Could not send YouTube " f"Play command: {error}")

        return False


# ==========================================
# PLAY YOUTUBE
# ==========================================


def play_youtube(
    query,
    profile_directory=None,
):
    """
    Searches YouTube and opens the first
    result in the user's REAL Chrome profile.

    Then sends the YouTube Play command.

    No temporary JARVIS Chrome profile
    is created.
    """

    if not query:

        return False

    if not profile_directory:

        print("JARVIS: No Chrome profile was " "specified for YouTube.")

        return False

    # ==========================================
    # FIND VIDEO
    # ==========================================

    video_url = find_first_youtube_video(query)

    if not video_url:

        return False

    # ==========================================
    # OPEN REAL CHROME PROFILE
    # ==========================================

    print(
        "JARVIS: Opening YouTube in the "
        f"real Chrome profile "
        f"{profile_directory}..."
    )

    hwnd = open_real_chrome_profile(
        profile_directory,
        video_url,
    )

    if not hwnd:

        print("JARVIS: Could not open YouTube " "in the selected Chrome profile.")

        return False

    # ==========================================
    # WAIT FOR CHROME
    # ==========================================

    if not wait_for_window(
        hwnd,
        timeout=10,
    ):

        print("JARVIS: YouTube Chrome window " "did not become ready.")

        return False

    # ==========================================
    # ACTIVATE REAL CHROME
    # ==========================================

    if not activate_chrome_window(hwnd):

        print("JARVIS: Could not activate " "the YouTube window.")

        return False

    # ==========================================
    # WAIT FOR VIDEO
    # ==========================================

    print("JARVIS: Waiting for YouTube " "video to load...")

    time.sleep(7)

    # ==========================================
    # PLAY
    # ==========================================

    success = press_youtube_play()

    if not success:

        return False

    print("JARVIS: YouTube playback started.")

    return True
