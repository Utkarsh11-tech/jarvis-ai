import os
import shutil
import socket
import subprocess
import threading
import time
from urllib.parse import quote

import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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

JARVIS_USER_DATA = os.path.join(
    os.environ["TEMP"],
    "jarvis-chrome",
)

DEBUG_PORT_START = 9222


# ==========================================
# FIND FREE PORT
# ==========================================


def find_free_port(
    start_port=DEBUG_PORT_START,
):
    """
    Finds an available local TCP port.
    """

    port = start_port

    while True:

        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        ) as sock:

            result = sock.connect_ex(("127.0.0.1", port))

        if result != 0:

            return port

        port += 1


# ==========================================
# PREPARE CHROME PROFILE
# ==========================================


def prepare_profile(
    profile_directory,
):
    """
    Creates a JARVIS automation copy of the
    selected Chrome profile.

    The original Chrome profile is never modified.
    """

    source = os.path.join(
        REAL_USER_DATA,
        profile_directory,
    )

    destination = os.path.join(
        JARVIS_USER_DATA,
        profile_directory,
    )

    if not os.path.exists(source):

        print("JARVIS: Chrome profile was not found: " f"{profile_directory}")

        return False

    try:

        os.makedirs(
            JARVIS_USER_DATA,
            exist_ok=True,
        )

        if not os.path.exists(destination):

            print("JARVIS: Preparing Chrome profile...")

            shutil.copytree(
                source,
                destination,
                ignore=shutil.ignore_patterns(
                    "Cache",
                    "Code Cache",
                    "GPUCache",
                    "Service Worker",
                ),
            )

        return True

    except Exception as error:

        print("JARVIS: Could not prepare Chrome " f"profile: {error}")

        return False


# ==========================================
# WAIT FOR DEBUGGER
# ==========================================


def wait_for_debugger(
    port,
    timeout=15,
):
    """
    Waits until Chrome's remote debugging
    endpoint becomes available.
    """

    url = f"http://127.0.0.1:{port}" "/json/version"

    start_time = time.time()

    while time.time() - start_time < timeout:

        try:

            response = requests.get(
                url,
                timeout=1,
            )

            if response.ok:

                return True

        except requests.RequestException:

            pass

        time.sleep(0.25)

    return False


# ==========================================
# START CHROME PROFILE
# ==========================================


def start_chrome_profile(
    profile_directory,
    debug_port,
):
    """
    Starts Chrome using the JARVIS copy
    of the selected profile.
    """

    command = [
        CHROME_PATH,
        "--remote-debugging-address=127.0.0.1",
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={JARVIS_USER_DATA}",
        f"--profile-directory={profile_directory}",
        "--start-maximized",
    ]

    try:

        subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return True

    except OSError as error:

        print("JARVIS: Could not start Chrome: " f"{error}")

        return False


# ==========================================
# ATTACH SELENIUM
# ==========================================


def attach_selenium(
    debug_port,
):
    """
    Attaches Selenium to an already-running
    Chrome instance.
    """

    options = Options()

    options.add_experimental_option(
        "debuggerAddress",
        f"127.0.0.1:{debug_port}",
    )

    try:

        driver = webdriver.Chrome(options=options)

        return driver

    except Exception as error:

        print("JARVIS: Could not attach Selenium " f"to Chrome: {error}")

        return None


# ==========================================
# CREATE SELENIUM DRIVER
# ==========================================


def create_driver(
    profile_directory=None,
):
    """
    Creates a Selenium driver.

    If a Chrome profile is supplied, JARVIS
    starts its automation copy and attaches
    Selenium to it.
    """

    if not profile_directory:

        options = Options()

        options.add_argument("--start-maximized")

        try:

            return webdriver.Chrome(options=options)

        except Exception as error:

            print("JARVIS: Could not start Chrome: " f"{error}")

            return None

    # ======================================
    # PREPARE PROFILE
    # ======================================

    if not prepare_profile(profile_directory):

        return None

    # ======================================
    # FIND PORT
    # ======================================

    debug_port = find_free_port()

    print("JARVIS: Opening Chrome profile " f"{profile_directory}...")

    # ======================================
    # START CHROME
    # ======================================

    if not start_chrome_profile(
        profile_directory,
        debug_port,
    ):

        return None

    # ======================================
    # WAIT FOR DEBUGGER
    # ======================================

    if not wait_for_debugger(debug_port):

        print("JARVIS: Chrome remote debugging " "did not become available.")

        return None

    # ======================================
    # ATTACH SELENIUM
    # ======================================

    return attach_selenium(debug_port)


# ==========================================
# AD MONITOR
# ==========================================


def skip_youtube_ads(
    driver,
):
    """
    Continuously watches for YouTube's
    Skip Ad button.
    """

    print("JARVIS: YouTube ad monitor started.")

    while True:

        try:

            if not driver.window_handles:

                break

            skip_buttons = driver.find_elements(
                By.CSS_SELECTOR,
                ".ytp-ad-skip-button, "
                ".ytp-ad-skip-button-modern, "
                ".ytp-ad-skip-button-container",
            )

            for button in skip_buttons:

                if not button.is_displayed():

                    continue

                try:

                    button.click()

                except Exception:

                    try:

                        driver.execute_script(
                            "arguments[0].click();",
                            button,
                        )

                    except Exception:

                        continue

                print("JARVIS: Advertisement skipped.")

        except Exception:

            pass

        time.sleep(0.5)


# ==========================================
# PLAY YOUTUBE
# ==========================================


def play_youtube(
    query,
    profile_directory=None,
):
    """
    Opens YouTube and plays the first
    search result.
    """

    if not query:

        return False

    driver = create_driver(profile_directory)

    if driver is None:

        return False

    try:

        search_url = "https://www.youtube.com/results" "?search_query=" + quote(query)

        print(f"JARVIS: Searching YouTube for " f"{query}...")

        driver.get(search_url)

        time.sleep(3)

        videos = driver.find_elements(
            By.CSS_SELECTOR,
            "ytd-video-renderer",
        )

        if not videos:

            print("JARVIS: No YouTube results found.")

            return False

        first_video = videos[0]

        link = first_video.find_element(
            By.CSS_SELECTOR,
            "a#video-title",
        )

        title = link.get_attribute("title")

        print("JARVIS: Opening YouTube video: " f"{title}")

        link.click()

        time.sleep(5)

        ad_thread = threading.Thread(
            target=skip_youtube_ads,
            args=(driver,),
            daemon=True,
        )

        ad_thread.start()

        print("JARVIS: YouTube playback started.")

        return True

    except Exception as error:

        print("JARVIS: YouTube playback failed: " f"{error}")

        return False


# ==========================================
# PLAY YOUTUBE MUSIC
# ==========================================


def play_youtube_music(
    query,
    profile_directory=None,
):
    """
    Opens YouTube Music and plays the first
    matching result using the selected
    Chrome profile.
    """

    if not query:

        return False

    driver = create_driver(profile_directory)

    if driver is None:

        return False

    try:

        # ======================================
        # SEARCH YOUTUBE MUSIC
        # ======================================

        search_url = "https://music.youtube.com/search?q=" + quote(query)

        print("JARVIS: Searching YouTube Music " f"for {query}...")

        driver.get(search_url)

        time.sleep(5)

        # ======================================
        # FIND MUSIC RESULTS
        # ======================================

        results = driver.find_elements(
            By.CSS_SELECTOR,
            "ytmusic-responsive-list-item-renderer",
        )

        if not results:

            results = driver.find_elements(
                By.CSS_SELECTOR,
                "ytmusic-shelf-renderer",
            )

        if not results:

            print("JARVIS: No YouTube Music " "results found.")

            return False

        # ======================================
        # FIND FIRST RESULT
        # ======================================

        first_result = results[0]

        title = first_result.text.strip()

        print("JARVIS: Opening YouTube Music: " f"{title}")

        try:

            link = first_result.find_element(By.CSS_SELECTOR, "a")

            driver.execute_script(
                "arguments[0].click();",
                link,
            )

        except Exception:

            driver.execute_script(
                "arguments[0].click();",
                first_result,
            )

        time.sleep(5)

        print("JARVIS: YouTube Music playback " "started.")

        return True

    except Exception as error:

        print("JARVIS: YouTube Music playback " f"failed: {error}")

        return False
