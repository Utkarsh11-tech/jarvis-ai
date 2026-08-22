"""
Shared helpers for the JARVIS body.

Currently holds the bridge between QImage and numpy. Recolouring an icon
pixel by pixel in Python costs one interpreter round trip per pixel, which
on a 256x256 source is roughly 65,000 iterations per icon per theme. Doing
the same arithmetic on numpy arrays is the identical calculation expressed
as whole-array operations, so the result is byte-for-byte the same while
the cost collapses to a handful of native passes.
"""

import numpy as np

from PySide6.QtGui import QImage


# ============================================================
# QIMAGE -> NUMPY
# ============================================================


def qimage_to_channels(
    image,
):
    """
    Split a QImage into (alpha, red, green, blue) planes.

    Each plane is an int32 array of shape (height, width). int32 rather
    than uint8 so downstream arithmetic cannot silently overflow or wrap
    negative -- the luminance weights alone reach 255 * 1000.

    Returns None if the image is null.
    """

    if image.isNull():

        return None

    image = image.convertToFormat(
        QImage.Format.Format_ARGB32
    )

    height = image.height()
    width = image.width()

    # Qt pads each row to a 4-byte boundary, so the row stride can be
    # wider than width * 4. Read the real stride and crop, never assume.
    stride = image.bytesPerLine()

    raw = np.frombuffer(
        image.constBits(),
        dtype=np.uint8,
        count=stride * height,
    )

    # Viewing uint8 as uint32 keeps host byte order, which is exactly how
    # Qt stores Format_ARGB32. That avoids hard-coding a little-endian
    # B, G, R, A byte layout. The copy also detaches us from Qt's buffer.
    pixels = (
        raw.reshape(height, stride)[:, : width * 4]
        .copy()
        .view(np.uint32)
        .reshape(height, width)
    )

    alpha = ((pixels >> 24) & 0xFF).astype(np.int32)
    red = ((pixels >> 16) & 0xFF).astype(np.int32)
    green = ((pixels >> 8) & 0xFF).astype(np.int32)
    blue = (pixels & 0xFF).astype(np.int32)

    return (
        alpha,
        red,
        green,
        blue,
    )


# ============================================================
# QT QUIRK REPRODUCTION
# ============================================================


def grayscale8_roundtrip(
    value,
):
    """
    Reproduce what Qt does to a value pushed through a Grayscale8 QImage.

    `QImage.setPixel` only treats its third argument as a raw index for
    monochrome and Indexed8 images. Format_Grayscale8 is not one of those,
    so Qt reads the argument as a QRgb colour instead. An alpha of 255
    therefore arrives as 0x000000FF -- pure blue -- and Qt stores
    qGray(0, 0, 255), which is (0 * 11 + 0 * 16 + 255 * 5) / 32 = 39.

    Reading the pixel back returns that 39, not the original 255, so any
    value sent on this trip comes out scaled by 5/32. The orb recolouring
    has always relied on that, which is why its icon is far fainter than
    its alpha arithmetic suggests. Preserved deliberately: changing it
    would change how the orb button looks.
    """

    return (value * 5) // 32


# ============================================================
# NUMPY -> QIMAGE
# ============================================================


def alpha_plane_to_qimage(
    alpha,
    red,
    green,
    blue,
):
    """
    Build an ARGB32 QImage from an alpha plane and one flat RGB colour.

    Pixels whose alpha is zero are written as a pure 0x00000000 so the
    result matches an image that was filled transparent and then had only
    the visible pixels painted in.
    """

    height, width = alpha.shape

    packed = (
        (alpha.astype(np.uint32) << 24)
        | (np.uint32(red) << 16)
        | (np.uint32(green) << 8)
        | np.uint32(blue)
    )

    packed[alpha == 0] = 0

    buffer = np.ascontiguousarray(
        packed,
        dtype=np.uint32,
    ).tobytes()

    image = QImage(
        buffer,
        width,
        height,
        width * 4,
        QImage.Format.Format_ARGB32,
    )

    # QImage does not take ownership of `buffer`, and `buffer` is a local
    # that dies on return. copy() gives the QImage its own storage.
    return image.copy()
