import ctypes
import os
import subprocess
import time
from urllib.parse import quote

import numpy as np
from PIL import ImageGrab

import win32api
import win32clipboard
import win32con
import win32gui

# ==========================================
# WINDOWS DPI AWARENESS
# ==========================================

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass


# ==========================================
# CHROME CONFIGURATION
# ==========================================

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

REAL_USER_DATA = os.path.join(
    os.environ["LOCALAPPDATA"],
    "Google",
    "Chrome",
    "User Data",
)


# ==========================================
# FIND CHROME WINDOWS
# ==========================================


def get_chrome_windows():
    """
    Returns all visible Chrome windows.
    """

    windows = []

    def callback(hwnd, _):

        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd)

        if not title:
            return

        if "Chrome" in title:

            windows.append(
                (
                    hwnd,
                    title,
                )
            )

    win32gui.EnumWindows(
        callback,
        None,
    )

    return windows


# ==========================================
# GET CHROME WINDOW HANDLES
# ==========================================


def get_chrome_window_handles():
    """
    Returns all currently visible Chrome
    window handles.
    """

    return {hwnd for hwnd, _ in get_chrome_windows()}


# ==========================================
# ACTIVATE CHROME WINDOW
# ==========================================


def activate_chrome_window(hwnd):
    """
    Brings the selected Chrome window
    to the foreground.
    """

    if not hwnd:
        return False

    try:

        win32gui.ShowWindow(
            hwnd,
            win32con.SW_RESTORE,
        )

        win32gui.SetForegroundWindow(
            hwnd,
        )

        time.sleep(0.5)

        return win32gui.GetForegroundWindow() == hwnd

    except Exception as error:

        print("JARVIS: Could not activate Chrome: " f"{error}")

        return False


# ==========================================
# FIND ACTIVE CHROME
# ==========================================


def find_active_chrome_window():
    """
    Returns the foreground Chrome window.
    """

    hwnd = win32gui.GetForegroundWindow()

    if not hwnd:
        return None

    title = win32gui.GetWindowText(hwnd)

    if "Chrome" in title:
        return hwnd

    return None


# ==========================================
# OPEN REAL CHROME PROFILE
# ==========================================


def open_real_chrome_profile(
    profile_directory,
    url=None,
):
    """
    Opens the user's REAL Chrome profile.

    No temporary profile is created.
    No profile is copied.
    """

    if not profile_directory:

        print("JARVIS: No Chrome profile " "was specified.")

        return None

    profile_path = os.path.join(
        REAL_USER_DATA,
        profile_directory,
    )

    if not os.path.exists(profile_path):

        print("JARVIS: Chrome profile does " f"not exist: {profile_directory}")

        return None

    # ======================================
    # EXISTING WINDOWS
    # ======================================

    existing_windows = get_chrome_window_handles()

    # ======================================
    # COMMAND
    # ======================================

    command = [
        CHROME_PATH,
        f"--profile-directory={profile_directory}",
        "--new-window",
    ]

    if url:
        command.append(url)

    # ======================================
    # START CHROME
    # ======================================

    try:

        subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print("JARVIS: Opening real Chrome " f"profile {profile_directory}...")

    except OSError as error:

        print("JARVIS: Could not open Chrome: " f"{error}")

        return None

    # ======================================
    # FIND NEW WINDOW
    # ======================================

    start = time.time()

    while time.time() - start < 10:

        current_windows = get_chrome_window_handles()

        new_windows = current_windows - existing_windows

        if new_windows:

            for hwnd in new_windows:

                if activate_chrome_window(hwnd):

                    return hwnd

        time.sleep(0.25)

    print("JARVIS: Could not identify the " "new Chrome window.")

    return None


# ==========================================
# WAIT FOR WINDOW
# ==========================================


def wait_for_window(
    hwnd,
    timeout=10,
):
    """
    Waits until a Chrome window is visible.
    """

    start = time.time()

    while time.time() - start < timeout:

        if hwnd and win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):

            return True

        time.sleep(0.25)

    return False


# ==========================================
# CTRL + L
# ==========================================


def focus_address_bar(hwnd=None):
    """
    Sends Ctrl+L to Chrome.
    """

    if hwnd is None:
        hwnd = find_active_chrome_window()

    if not hwnd:
        return False

    if not activate_chrome_window(hwnd):

        print("JARVIS: Chrome did not become " "the active window.")

        return False

    win32api.keybd_event(
        win32con.VK_CONTROL,
        0,
        0,
        0,
    )

    win32api.keybd_event(
        ord("L"),
        0,
        0,
        0,
    )

    win32api.keybd_event(
        ord("L"),
        0,
        win32con.KEYEVENTF_KEYUP,
        0,
    )

    win32api.keybd_event(
        win32con.VK_CONTROL,
        0,
        win32con.KEYEVENTF_KEYUP,
        0,
    )

    time.sleep(0.3)

    return True


# ==========================================
# PASTE TEXT
# ==========================================


def paste_text(text):
    """
    Copies text to clipboard and pastes it.
    """

    if not text:
        return False

    try:

        win32clipboard.OpenClipboard()

        win32clipboard.EmptyClipboard()

        win32clipboard.SetClipboardText(
            text,
        )

        win32clipboard.CloseClipboard()

    except Exception as error:

        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass

        print("JARVIS: Clipboard error: " f"{error}")

        return False

    win32api.keybd_event(
        win32con.VK_CONTROL,
        0,
        0,
        0,
    )

    win32api.keybd_event(
        ord("V"),
        0,
        0,
        0,
    )

    win32api.keybd_event(
        ord("V"),
        0,
        win32con.KEYEVENTF_KEYUP,
        0,
    )

    win32api.keybd_event(
        win32con.VK_CONTROL,
        0,
        win32con.KEYEVENTF_KEYUP,
        0,
    )

    return True


# ==========================================
# PRESS ENTER
# ==========================================


def press_enter():

    win32api.keybd_event(
        win32con.VK_RETURN,
        0,
        0,
        0,
    )

    win32api.keybd_event(
        win32con.VK_RETURN,
        0,
        win32con.KEYEVENTF_KEYUP,
        0,
    )


# ==========================================
# OPEN URL
# ==========================================


def open_url_in_chrome(
    url,
    profile_directory=None,
):
    """
    Opens a URL in the selected real
    Chrome profile.
    """

    if not url:
        return False

    if profile_directory:

        hwnd = open_real_chrome_profile(
            profile_directory,
            url,
        )

        if not hwnd:
            return False

        return wait_for_window(hwnd)

    hwnd = find_active_chrome_window()

    if not hwnd:

        try:

            subprocess.Popen(
                [
                    CHROME_PATH,
                    "--new-window",
                    url,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            time.sleep(2)

            return True

        except OSError as error:

            print("JARVIS: Could not start Chrome: " f"{error}")

            return False

    if not focus_address_bar(hwnd):
        return False

    if not paste_text(url):
        return False

    press_enter()

    return True


# ==========================================
# WAIT FOR YOUTUBE MUSIC
# ==========================================


def wait_for_youtube_music(
    hwnd,
    timeout=20,
):
    """
    Waits for YouTube Music to load.
    """

    print("JARVIS: Waiting for YouTube Music " "to become ready...")

    start = time.time()

    last_title = ""

    while time.time() - start < timeout:

        if not (hwnd and win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)):

            return False

        title = win32gui.GetWindowText(hwnd)

        if title != last_title:

            print("JARVIS: Chrome title: " f"{title}")

            last_title = title

        title_lower = title.lower()

        if "music.youtube.com" in title_lower or "youtube music" in title_lower:

            time.sleep(3)

            print("JARVIS: YouTube Music page " "detected.")

            return True

        time.sleep(0.5)

    print("JARVIS: YouTube Music did not " "become ready.")

    return False


# ==========================================
# FIND BRIGHT HORIZONTAL REGION
# ==========================================


def find_bright_regions(
    image,
):
    """
    Finds large bright regions that can
    correspond to YouTube Music's white
    Play button.
    """

    array = np.asarray(image.convert("RGB"))

    red = array[:, :, 0].astype(int)
    green = array[:, :, 1].astype(int)
    blue = array[:, :, 2].astype(int)

    # ======================================
    # WHITE / BRIGHT MASK
    # ======================================

    mask = (
        (red > 210)
        & (green > 210)
        & (blue > 210)
        & (np.abs(red - green) < 30)
        & (np.abs(red - blue) < 30)
    )

    height, width = mask.shape

    # ======================================
    # SEARCH MAIN PAGE AREA
    # ======================================

    x_start = int(width * 0.12)
    x_end = int(width * 0.75)

    y_start = int(height * 0.25)
    y_end = int(height * 0.80)

    candidates = []

    # ======================================
    # FIND HORIZONTAL WHITE RUNS
    # ======================================

    for y in range(
        y_start,
        y_end,
    ):

        row = mask[
            y,
            x_start:x_end,
        ]

        positions = np.where(row)[0]

        if len(positions) == 0:
            continue

        starts = positions[
            np.r_[
                True,
                np.diff(positions) > 1,
            ]
        ]

        ends = positions[
            np.r_[
                np.diff(positions) > 1,
                True,
            ]
        ]

        for start_x, end_x in zip(
            starts,
            ends,
        ):

            run_width = end_x - start_x + 1

            if run_width >= 60:

                candidates.append(
                    (
                        int(start_x + x_start),
                        int(end_x + x_start),
                        y,
                    )
                )

    # ======================================
    # GROUP NEARBY RUNS
    # ======================================

    groups = []

    for start_x, end_x, y in candidates:

        matched = None

        for group in groups:

            vertical_gap = y - group["last_y"]

            horizontal_overlap = not (
                end_x < group["min_x"] - 20 or start_x > group["max_x"] + 20
            )

            if 0 <= vertical_gap <= 3 and horizontal_overlap:

                matched = group
                break

        if matched:

            matched["min_x"] = min(
                matched["min_x"],
                start_x,
            )

            matched["max_x"] = max(
                matched["max_x"],
                end_x,
            )

            matched["last_y"] = y

        else:

            groups.append(
                {
                    "min_x": start_x,
                    "max_x": end_x,
                    "first_y": y,
                    "last_y": y,
                }
            )

    # ======================================
    # MERGE VERTICAL GAPS
    # ======================================

    merged = True

    while merged:

        merged = False

        for i in range(len(groups)):

            for j in range(
                i + 1,
                len(groups),
            ):

                a = groups[i]
                b = groups[j]

                gap = max(
                    b["first_y"] - a["last_y"],
                    a["first_y"] - b["last_y"],
                )

                overlap = not (
                    a["max_x"] < b["min_x"] - 20 or b["max_x"] < a["min_x"] - 20
                )

                if gap <= 20 and overlap:

                    groups[i] = {
                        "min_x": min(
                            a["min_x"],
                            b["min_x"],
                        ),
                        "max_x": max(
                            a["max_x"],
                            b["max_x"],
                        ),
                        "first_y": min(
                            a["first_y"],
                            b["first_y"],
                        ),
                        "last_y": max(
                            a["last_y"],
                            b["last_y"],
                        ),
                    }

                    groups.pop(j)

                    merged = True

                    break

            if merged:
                break

    # ======================================
    # BUILD FINAL CANDIDATES
    # ======================================

    results = []

    for group in groups:

        width = group["max_x"] - group["min_x"] + 1

        height = group["last_y"] - group["first_y"] + 1

        # Play button is typically a
        # reasonably large horizontal pill.
        if 90 <= width <= 250 and 20 <= height <= 80:

            center_x = (group["min_x"] + group["max_x"]) // 2

            center_y = (group["first_y"] + group["last_y"]) // 2

            results.append(
                (
                    width * height,
                    center_x,
                    center_y,
                    width,
                    height,
                )
            )

    # Largest likely button first.
    results.sort(reverse=True)

    return results


# ==========================================
# FIND YOUTUBE MUSIC PLAY BUTTON
# ==========================================


def find_youtube_music_play_button():
    """
    Takes a screenshot and automatically
    searches for the large white Play button.
    """

    print("JARVIS: Scanning screen for " "YouTube Music Play button...")

    try:

        screenshot = ImageGrab.grab()

    except Exception as error:

        print("JARVIS: Screenshot failed: " f"{error}")

        return None

    regions = find_bright_regions(screenshot)

    if not regions:

        print("JARVIS: Could not detect a " "possible Play button.")

        return None

    # ======================================
    # SHOW TOP CANDIDATES
    # ======================================

    for index, candidate in enumerate(
        regions[:5],
        start=1,
    ):

        _, x, y, width, height = candidate

        print("JARVIS: Candidate " f"{index}: ({x}, {y}) " f"{width}x{height}")

    # ======================================
    # BEST CANDIDATE
    # ======================================

    _, x, y, width, height = regions[0]

    print("JARVIS: Selected Play button " f"target: ({x}, {y})")

    return (
        x,
        y,
    )


# ==========================================
# REAL WINDOWS MOUSE CLICK
# ==========================================


def real_mouse_click(
    x,
    y,
):
    """
    Performs a real Windows mouse click
    using win32api.mouse_event().
    """

    win32api.SetCursorPos((x, y))

    time.sleep(0.5)

    actual_position = win32api.GetCursorPos()

    print("JARVIS: Cursor position: " f"{actual_position}")

    if actual_position != (
        x,
        y,
    ):

        print("JARVIS: Cursor failed to " "reach target.")

        return False

    print("JARVIS: Sending mouse DOWN...")

    win32api.mouse_event(
        win32con.MOUSEEVENTF_LEFTDOWN,
        0,
        0,
        0,
        0,
    )

    time.sleep(0.12)

    print("JARVIS: Sending mouse UP...")

    win32api.mouse_event(
        win32con.MOUSEEVENTF_LEFTUP,
        0,
        0,
        0,
        0,
    )

    return True


# ==========================================
# CLICK YOUTUBE MUSIC PLAY BUTTON
# ==========================================


def click_youtube_music_play_button(
    hwnd,
):
    """
    Automatically locates the Play button
    and performs a real Windows click.
    """

    if not hwnd:

        return False

    if not activate_chrome_window(hwnd):

        print("JARVIS: Could not activate " "Chrome.")

        return False

    time.sleep(1)

    # ======================================
    # LOCATE BUTTON
    # ======================================

    target = find_youtube_music_play_button()

    if not target:

        return False

    x, y = target

    # ======================================
    # CLICK
    # ======================================

    success = real_mouse_click(
        x,
        y,
    )

    if not success:

        return False

    time.sleep(4)

    print("JARVIS: YouTube Music click " "completed.")

    return True


# ==========================================
# PLAY YOUTUBE MUSIC
# ==========================================


def play_youtube_music(
    query,
    profile_directory=None,
):
    """
    Opens YouTube Music in the selected
    REAL Chrome profile and automatically
    locates and clicks the Play button.
    """

    if not query:

        return False

    search_url = "https://music.youtube.com/search?q=" + quote(query)

    print("JARVIS: Opening YouTube Music " f"for {query}...")

    # ======================================
    # OPEN REAL PROFILE
    # ======================================

    hwnd = open_real_chrome_profile(
        profile_directory,
        search_url,
    )

    if not hwnd:

        return False

    # ======================================
    # WAIT FOR WINDOW
    # ======================================

    if not wait_for_window(
        hwnd,
        timeout=10,
    ):

        return False

    # ======================================
    # WAIT FOR YOUTUBE MUSIC
    # ======================================

    if not wait_for_youtube_music(
        hwnd,
        timeout=20,
    ):

        return False

    # ======================================
    # ACTIVATE
    # ======================================

    print("JARVIS: Activating YouTube Music...")

    if not activate_chrome_window(hwnd):

        return False

    time.sleep(1)

    # ======================================
    # PLAY
    # ======================================

    print("JARVIS: Attempting YouTube Music " "playback...")

    success = click_youtube_music_play_button(hwnd)

    if not success:

        print("JARVIS: Could not click the " "YouTube Music Play button.")

        return False

    print("JARVIS: YouTube Music playback " "command completed.")

    return True
