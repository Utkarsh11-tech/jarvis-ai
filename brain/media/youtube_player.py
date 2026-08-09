import threading
import time
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ==========================================
# AD MONITOR
# ==========================================


def skip_youtube_ads(driver):
    """
    Continuously watches for YouTube's Skip Ad
    button and clicks it when available.
    """

    print("JARVIS: YouTube ad monitor started.")

    while True:

        try:

            # Stop monitoring if the browser
            # has been closed.
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

            # YouTube can temporarily change the
            # video DOM while ads load.
            pass

        time.sleep(0.5)


# ==========================================
# PLAY YOUTUBE
# ==========================================


def play_youtube(query):
    """
    Opens YouTube and plays the first
    search result matching the requested query.
    """

    if not query:

        return False

    search_url = "https://www.youtube.com/results?search_query=" + quote(query)

    options = Options()

    options.add_argument("--start-maximized")

    try:

        driver = webdriver.Chrome(options=options)

        # ==========================================
        # OPEN YOUTUBE SEARCH
        # ==========================================

        driver.get(search_url)

        time.sleep(3)

        # ==========================================
        # FIND VIDEO RESULTS
        # ==========================================

        videos = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")

        if not videos:

            print("JARVIS: No YouTube results found.")

            driver.quit()

            return False

        # ==========================================
        # OPEN FIRST RESULT
        # ==========================================

        first_video = videos[0]

        link = first_video.find_element(By.CSS_SELECTOR, "a#video-title")

        title = link.get_attribute("title")

        print("JARVIS: Opening YouTube video: " f"{title}")

        link.click()

        # ==========================================
        # WAIT FOR VIDEO
        # ==========================================

        time.sleep(5)

        # ==========================================
        # START AD MONITOR
        # ==========================================

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
