from playwright.sync_api import (
    sync_playwright,
    TimeoutError,
)


class UIElementMonitor:
    """
    Monitors a permitted webpage for a UI element
    and interacts with it when it becomes available.
    """

    def __init__(self):

        self.playwright = None
        self.browser = None
        self.page = None

    # ==================================================
    # START BROWSER
    # ==================================================

    def start(self):

        self.playwright = (
            sync_playwright().start()
        )

        self.browser = (
            self.playwright.chromium.launch(
                headless=False
            )
        )

        self.page = (
            self.browser.new_page()
        )

    # ==================================================
    # OPEN PAGE
    # ==================================================

    def open_page(self, url):

        if self.page is None:
            self.start()

        self.page.goto(url)

    # ==================================================
    # WAIT FOR ELEMENT
    # ==================================================

    def wait_for_element(
        self,
        selector,
        timeout=0,
    ):
        """
        Waits until the requested UI element
        becomes visible.

        timeout=0 means wait indefinitely.
        """

        if self.page is None:

            raise RuntimeError(
                "Browser has not been started."
            )

        try:

            element = self.page.locator(
                selector
            )

            element.wait_for(
                state="visible",
                timeout=timeout,
            )

            return True

        except TimeoutError:

            return False

    # ==================================================
    # CLICK ELEMENT
    # ==================================================

    def click_element(self, selector):

        if self.page is None:
            return False

        try:

            self.page.locator(
                selector
            ).click()

            return True

        except Exception:

            return False

    # ==================================================
    # WAIT AND CLICK
    # ==================================================

    def wait_and_click(
        self,
        selector,
        timeout=0,
    ):
        """
        Waits for an element and clicks it
        immediately when it becomes available.
        """

        available = self.wait_for_element(
            selector,
            timeout,
        )

        if not available:
            return False

        return self.click_element(
            selector
        )

    # ==================================================
    # CLOSE
    # ==================================================

    def close(self):

        if self.browser:

            self.browser.close()

            self.browser = None

        if self.playwright:

            self.playwright.stop()

            self.playwright = None

        self.page = None

