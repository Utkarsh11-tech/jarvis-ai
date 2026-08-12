import sys
import ctypes

from ctypes import wintypes

from PySide6.QtCore import (
    QThread,
    Qt,
    QAbstractNativeEventFilter,
)

from PySide6.QtWidgets import QApplication

from bridge.bridge import JarvisBridge

from brain.core.assistant_v2 import Assistant
from brain.voices.voice_worker import VoiceWorker

from body.app.screens.home.home_screen import MainWindow


# ==================================================
# WINDOWS MSG STRUCTURE
# ==================================================


class MSG(ctypes.Structure):

    _fields_ = [
        (
            "hwnd",
            wintypes.HWND,
        ),
        (
            "message",
            wintypes.UINT,
        ),
        (
            "wParam",
            wintypes.WPARAM,
        ),
        (
            "lParam",
            wintypes.LPARAM,
        ),
        (
            "time",
            wintypes.DWORD,
        ),
        (
            "pt_x",
            wintypes.LONG,
        ),
        (
            "pt_y",
            wintypes.LONG,
        ),
    ]


# ==================================================
# GLOBAL HOTKEY
# ==================================================


class GlobalHotkeyFilter(
    QAbstractNativeEventFilter
):

    WM_HOTKEY = 0x0312

    MOD_CONTROL = 0x0002

    VK_SPACE = 0x20

    HOTKEY_ID = 1

    def __init__(
        self,
        callback,
    ):

        super().__init__()

        self.callback = callback

        self.registered = False

        self.register_hotkey()

    # ==================================================
    # REGISTER
    # ==================================================

    def register_hotkey(self):

        if sys.platform != "win32":

            print(
                "JARVIS: Global hotkey is "
                "only supported on Windows."
            )

            return

        result = (
            ctypes.windll.user32.RegisterHotKey(
                None,
                self.HOTKEY_ID,
                self.MOD_CONTROL,
                self.VK_SPACE,
            )
        )

        if result:

            self.registered = True

            print(
                "JARVIS: Global shortcut registered "
                "(Ctrl + Space)"
            )

        else:

            error_code = (
                ctypes.windll.kernel32.GetLastError()
            )

            print(
                "JARVIS: Failed to register "
                "Ctrl + Space."
            )

            print(
                f"JARVIS: Windows error code: "
                f"{error_code}"
            )

    # ==================================================
    # NATIVE EVENT FILTER
    # ==================================================

    def nativeEventFilter(
        self,
        eventType,
        message,
    ):

        if sys.platform != "win32":

            return False, 0

        if eventType != "windows_generic_MSG":

            return False, 0

        try:

            msg = ctypes.cast(
                int(message),
                ctypes.POINTER(MSG),
            ).contents

        except Exception as error:

            print(
                "JARVIS: Failed to read "
                f"Windows message: {error}"
            )

            return False, 0

        if (
            msg.message
            == self.WM_HOTKEY
            and msg.wParam
            == self.HOTKEY_ID
        ):

            print(
                "JARVIS: Ctrl + Space detected."
            )

            self.callback()

            return True, 0

        return False, 0

    # ==================================================
    # UNREGISTER
    # ==================================================

    def unregister_hotkey(self):

        if (
            sys.platform == "win32"
            and self.registered
        ):

            ctypes.windll.user32.UnregisterHotKey(
                None,
                self.HOTKEY_ID,
            )

            self.registered = False

            print(
                "JARVIS: Global shortcut "
                "unregistered."
            )


# ==================================================
# MAIN
# ==================================================


def main():

    # ================================================
    # APPLICATION
    # ================================================

    app = QApplication(
        sys.argv
    )

    # ================================================
    # SHARED BRIDGE
    # ================================================

    bridge = JarvisBridge()

    # ================================================
    # BODY
    # ================================================

    window = MainWindow(
        bridge
    )

    # ================================================
    # GLOBAL HOTKEY
    # ================================================

    hotkey_filter = GlobalHotkeyFilter(
        window.toggle_listening
    )

    app.installNativeEventFilter(
        hotkey_filter
    )

    # ================================================
    # VOICE → CONVERSATION UI
    # ================================================

    bridge.transcript_received.connect(
        window.chat.add_user_message
    )

    # ================================================
    # OVERLAY STATUS
    # ================================================

    bridge.overlay_status_changed.connect(
        window.overlay.set_status
    )

    # ================================================
    # OVERLAY STATE UPDATES
    # ================================================

    def update_overlay_for_state(
        state,
    ):

        normalized = str(
            state
        ).lower()

        if normalized == "thinking":

            window.overlay.set_status(
                "Processing..."
            )

            window.show_wake_overlay()

        elif normalized == "executing":

            window.overlay.set_status(
                "Processing..."
            )

            window.show_wake_overlay()

        elif normalized == "speaking":

            window.overlay.set_status(
                "Speaking..."
            )

            window.show_wake_overlay()

        elif normalized == "error":

            window.overlay.set_status(
                "Error"
            )

            window.show_wake_overlay()

        elif normalized == "sleeping":

            window.overlay.hide_overlay()

    bridge.state_changed.connect(
        update_overlay_for_state
    )

    # ================================================
    # SHOW APPLICATION
    # ================================================

    window.show()

    # ================================================
    # BRAIN
    # ================================================

    assistant = Assistant(
        bridge
    )

    brain_thread = QThread()

    assistant.moveToThread(
        brain_thread
    )

    brain_thread.started.connect(
        assistant.run
    )

    brain_thread.start()

    # ================================================
    # VOICE WORKER
    # ================================================

    voice_worker = VoiceWorker(
        bridge
    )

    voice_thread = QThread()

    voice_worker.moveToThread(
        voice_thread
    )

    # --------------------------------
    # Voice → Bridge
    # --------------------------------

    voice_worker.command_received.connect(
        bridge.send_command
    )

    # --------------------------------
    # Bridge → Voice Worker
    # Follow-up input
    # --------------------------------

    bridge.voice_input_requested.connect(
        voice_worker.request_follow_up,
        Qt.DirectConnection,
    )

    # --------------------------------
    # Voice Worker shutdown
    # --------------------------------

    voice_worker.finished.connect(
        voice_thread.quit
    )

    voice_thread.started.connect(
        voice_worker.run
    )

    voice_thread.start()

    # ================================================
    # START APPLICATION
    # ================================================

    exit_code = app.exec()

    # ================================================
    # SHUTDOWN
    # ================================================

    hotkey_filter.unregister_hotkey()

    voice_worker.stop()

    voice_thread.quit()
    voice_thread.wait()

    brain_thread.quit()
    brain_thread.wait()

    sys.exit(
        exit_code
    )


# ==================================================
# ENTRY POINT
# ==================================================


if __name__ == "__main__":

    main()