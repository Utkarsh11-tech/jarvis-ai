"""
Proves the fast numpy icon recolouring produces byte-identical output to
the original per-pixel loops, using the real icon artwork.

The fast path and the fallback path are both run over
`assets/icons/orb_icon.png` and `assets/icons/chat_icon.png`, then the
resulting images are compared byte for byte. If this passes, switching to
numpy changed nothing a user can see.

Run from the repository root:

    python body/tests/test_icon_recolour.py

or under pytest:

    pytest body/tests/test_icon_recolour.py -v
"""

import os
import sys
import time
from pathlib import Path

# Qt must not try to open a real window just to compare pixels.
os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)

REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(REPO_ROOT),
    )

from PySide6.QtCore import Qt                       # noqa: E402
from PySide6.QtGui import QColor, QImage            # noqa: E402
from PySide6.QtWidgets import QApplication          # noqa: E402

from body.app.screens.home.home_screen import (     # noqa: E402
    MainWindow,
)


ICON_DIR = (
    REPO_ROOT
    / "body"
    / "app"
    / "assets"
    / "icons"
)

# The two tints each icon is actually rendered in.
THEME_COLOURS = {
    "chat": {
        "dark": "#00D9FF",
        "light": "#008FB8",
    },
    "orb": {
        "dark": "#00D9FF",
        "light": "#00536B",
    },
}


# ============================================================
# HARNESS
# ============================================================


class RecolourHarness:
    """
    Borrows the recolour methods off MainWindow without constructing a
    window. They only need `orb_icon_path` for their error message, so a
    bare object is enough and the test stays fast.
    """

    orb_icon_path = ICON_DIR / "orb_icon.png"
    chat_icon_path = ICON_DIR / "chat_icon.png"

    recolor_chat_pixels = MainWindow.recolor_chat_pixels
    recolor_orb_pixels = MainWindow.recolor_orb_pixels

    # ========================================================
    # REFERENCE IMPLEMENTATIONS
    # ========================================================
    #
    # The original per-pixel loops, lifted verbatim out of
    # MainWindow. They are the ground truth the numpy fast paths
    # must reproduce exactly, so they live here rather than in
    # production code: nothing ships them, but the test can still
    # prove equivalence. Do not tidy or optimise these -- their
    # only job is to be what the code used to do.
    # ========================================================

    def recolor_chat_pixels_fallback(
        self,
        source,
        icon_color,
    ):

        colored = QImage(
            source.size(),
            QImage.Format.Format_ARGB32,
        )
        colored.fill(Qt.GlobalColor.transparent)

        red = icon_color.red()
        green = icon_color.green()
        blue = icon_color.blue()

        for y in range(source.height()):
            for x in range(source.width()):
                pixel = source.pixel(x, y)

                alpha = (pixel >> 24) & 0xFF
                if alpha == 0:
                    continue

                r = (pixel >> 16) & 0xFF
                g = (pixel >> 8) & 0xFF
                b = pixel & 0xFF

                luminance = (
                    299 * r +
                    587 * g +
                    114 * b
                ) // 1000

                darkness = 255 - luminance
                final_alpha = (alpha * darkness) // 255

                if final_alpha < 8:
                    continue

                colored.setPixel(
                    x,
                    y,
                    (
                        (final_alpha << 24)
                        | (red << 16)
                        | (green << 8)
                        | blue
                    ),
                )

        return colored

    # ============================================================

    def recolor_orb_pixels_fallback(
        self,
        source,
        icon_color,
    ):

        width = source.width()
        height = source.height()

        mask = QImage(
            width,
            height,
            QImage.Format.Format_Grayscale8,
        )
        mask.fill(0)

        min_x = width
        min_y = height
        max_x = -1
        max_y = -1

        for y in range(height):
            for x in range(width):
                pixel = source.pixel(x, y)

                alpha = (pixel >> 24) & 0xFF
                if alpha == 0:
                    continue

                r = (pixel >> 16) & 0xFF
                g = (pixel >> 8) & 0xFF
                b = pixel & 0xFF

                maximum = max(r, g, b)
                minimum = min(r, g, b)
                saturation = maximum - minimum

                luminance = (
                    299 * r +
                    587 * g +
                    114 * b
                ) // 1000

                # Keep cyan/blue artwork and dark linework while
                # rejecting the pale checkerboard background.
                if (
                    saturation >= 18
                    or luminance <= 155
                ):
                    color_alpha = min(
                        255,
                        saturation * 6,
                    )

                    dark_alpha = max(
                        0,
                        min(
                            255,
                            (175 - luminance) * 5,
                        ),
                    )

                    final_alpha = max(
                        color_alpha,
                        dark_alpha,
                    )

                    if final_alpha < 25:
                        continue

                    mask.setPixel(
                        x,
                        y,
                        final_alpha,
                    )

                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

        if (
            max_x < min_x
            or max_y < min_y
        ):
            print(
                "JARVIS: ERROR - Orb icon foreground could not be detected:",
                self.orb_icon_path,
            )
            return None

        padding = max(
            2,
            int(
                min(width, height) * 0.015
            ),
        )

        min_x = max(0, min_x - padding)
        min_y = max(0, min_y - padding)
        max_x = min(width - 1, max_x + padding)
        max_y = min(height - 1, max_y + padding)

        cropped_mask = mask.copy(
            min_x,
            min_y,
            max_x - min_x + 1,
            max_y - min_y + 1,
        )

        colored = QImage(
            cropped_mask.size(),
            QImage.Format.Format_ARGB32,
        )
        colored.fill(Qt.GlobalColor.transparent)

        red = icon_color.red()
        green = icon_color.green()
        blue = icon_color.blue()

        for y in range(cropped_mask.height()):
            for x in range(cropped_mask.width()):
                final_alpha = (
                    cropped_mask.pixel(x, y) & 0xFF
                )

                if final_alpha == 0:
                    continue

                colored.setPixel(
                    x,
                    y,
                    (
                        (final_alpha << 24)
                        | (red << 16)
                        | (green << 8)
                        | blue
                    ),
                )

        return colored


def load_source(path):
    """Load and scale an icon exactly as MainWindow does."""

    source = QImage(str(path))

    assert not source.isNull(), "could not load %s" % path

    return source.scaled(
        256,
        256,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.FastTransformation,
    ).convertToFormat(
        QImage.Format.Format_ARGB32
    )


def image_bytes(image):
    """Flatten a QImage to raw bytes, ignoring any row padding."""

    image = image.convertToFormat(
        QImage.Format.Format_ARGB32
    )

    width = image.width()
    stride = image.bytesPerLine()

    raw = bytes(image.constBits())

    rows = [
        raw[y * stride : y * stride + width * 4]
        for y in range(image.height())
    ]

    return b"".join(rows)


def describe_difference(fast, slow):
    """
    Explain *how* two images differ, so a failure is actionable.

    Reports whether the divergence is confined to the alpha channel, how
    many pixels moved, and the mapping from reference alpha to fast alpha.
    That mapping is the useful part: a clean linear relationship points at
    a scaling bug rather than a logic error.
    """

    import numpy as np

    from body.app.utils.helpers import qimage_to_channels

    fast_channels = qimage_to_channels(fast)
    slow_channels = qimage_to_channels(slow)

    fast_alpha, fast_r, fast_g, fast_b = fast_channels
    slow_alpha, slow_r, slow_g, slow_b = slow_channels

    lines = []

    alpha_differs = fast_alpha != slow_alpha

    rgb_differs = (
        (fast_r != slow_r)
        | (fast_g != slow_g)
        | (fast_b != slow_b)
    )

    lines.append(
        "        %d of %d pixels differ"
        % (
            int((alpha_differs | rgb_differs).sum()),
            fast_alpha.size,
        )
    )

    lines.append(
        "        alpha differs: %d   rgb differs: %d"
        % (
            int(alpha_differs.sum()),
            int(rgb_differs.sum()),
        )
    )

    lines.append(
        "        alpha range   fast %d..%d   reference %d..%d"
        % (
            int(fast_alpha.min()),
            int(fast_alpha.max()),
            int(slow_alpha.min()),
            int(slow_alpha.max()),
        )
    )

    # Sample the reference -> fast mapping at a few alpha levels.
    pairs = np.stack(
        [
            slow_alpha.ravel(),
            fast_alpha.ravel(),
        ],
        axis=1,
    )

    pairs = np.unique(
        pairs[pairs[:, 0] != 0],
        axis=0,
    )

    sample = pairs[:: max(1, len(pairs) // 6)][:6]

    lines.append(
        "        reference -> fast: %s"
        % ", ".join(
            "%d->%d" % (int(a), int(b))
            for a, b in sample
        )
    )

    return "\n".join(lines)


def compare(kind, theme, colour_hex):
    """Run both paths for one icon/theme and return a report dict."""
    harness = RecolourHarness()
    colour = QColor(colour_hex)

    path = (
        harness.orb_icon_path
        if kind == "orb"
        else harness.chat_icon_path
    )

    source = load_source(path)

    fast_method = (
        harness.recolor_orb_pixels
        if kind == "orb"
        else harness.recolor_chat_pixels
    )

    slow_method = (
        harness.recolor_orb_pixels_fallback
        if kind == "orb"
        else harness.recolor_chat_pixels_fallback
    )

    started = time.perf_counter()
    fast = fast_method(source, colour)
    fast_seconds = time.perf_counter() - started

    started = time.perf_counter()
    slow = slow_method(source, colour)
    slow_seconds = time.perf_counter() - started

    assert fast is not None, (
        "%s/%s: fast path returned None" % (kind, theme)
    )
    assert slow is not None, (
        "%s/%s: reference path returned None" % (kind, theme)
    )

    return {
        "kind": kind,
        "theme": theme,
        "size_match": fast.size() == slow.size(),
        "fast_size": (fast.width(), fast.height()),
        "slow_size": (slow.width(), slow.height()),
        "bytes_match": image_bytes(fast) == image_bytes(slow),
        "fast_seconds": fast_seconds,
        "slow_seconds": slow_seconds,
        "fast_image": fast,
        "slow_image": slow,
    }


# ============================================================
# PYTEST ENTRY POINTS
# ============================================================


def _app():
    return QApplication.instance() or QApplication([])


def test_chat_icon_identical():
    _app()
    for theme, colour in THEME_COLOURS["chat"].items():
        report = compare("chat", theme, colour)
        assert report["size_match"], report
        assert report["bytes_match"], (
            "chat/%s pixels differ from the reference" % theme
        )


def test_orb_icon_identical():
    _app()
    for theme, colour in THEME_COLOURS["orb"].items():
        report = compare("orb", theme, colour)
        assert report["size_match"], report
        assert report["bytes_match"], (
            "orb/%s pixels differ from the reference" % theme
        )


# ============================================================
# STANDALONE REPORT
# ============================================================


def main():
    _app()

    print()
    print("Comparing fast numpy recolour against the original loops")
    print("=" * 66)
    print(
        "%-6s %-7s %-9s %-11s %9s %9s %7s"
        % (
            "icon",
            "theme",
            "size",
            "pixels",
            "numpy",
            "loops",
            "faster",
        )
    )
    print("-" * 66)

    failures = 0

    for kind in ("chat", "orb"):
        for theme, colour in THEME_COLOURS[kind].items():

            report = compare(kind, theme, colour)

            ok = (
                report["size_match"]
                and report["bytes_match"]
            )

            if not ok:
                failures += 1

            speedup = (
                report["slow_seconds"] / report["fast_seconds"]
                if report["fast_seconds"] > 0
                else float("inf")
            )

            print(
                "%-6s %-7s %-9s %-11s %8.1fms %8.1fms %6.0fx"
                % (
                    kind,
                    theme,
                    "match" if report["size_match"] else "DIFFER",
                    "identical" if report["bytes_match"] else "DIFFER",
                    report["fast_seconds"] * 1000,
                    report["slow_seconds"] * 1000,
                    speedup,
                )
            )

            if not report["size_match"]:
                print(
                    "        fast=%s reference=%s"
                    % (report["fast_size"], report["slow_size"])
                )

            elif not report["bytes_match"]:
                print(
                    describe_difference(
                        report["fast_image"],
                        report["slow_image"],
                    )
                )

    print("-" * 66)

    if failures:
        print("RESULT: %d comparison(s) FAILED" % failures)
        return 1

    print("RESULT: every icon is byte-identical to the original output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
