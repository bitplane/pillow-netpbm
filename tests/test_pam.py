"""Tests for PAM (P7) format plugin."""

import io
import struct

import pytest
from PIL import Image

import pillow_netpbm  # noqa: F401 — triggers registration


def make_pam(width, height, depth, maxval, tupltype, pixel_data, comments=None):
    """Build a PAM file in memory."""
    lines = [b"P7"]
    if comments:
        for c in comments:
            lines.append(f"# {c}".encode("ascii"))
    lines.append(f"WIDTH {width}".encode())
    lines.append(f"HEIGHT {height}".encode())
    lines.append(f"DEPTH {depth}".encode())
    lines.append(f"MAXVAL {maxval}".encode())
    if tupltype is not None:
        lines.append(f"TUPLTYPE {tupltype}".encode())
    lines.append(b"ENDHDR")
    header = b"\n".join(lines) + b"\n"
    return header + pixel_data


def open_pam(data):
    return Image.open(io.BytesIO(data))


# --- Read tests ---


def test_read_grayscale():
    pixels = bytes([0, 128, 255, 64])
    data = make_pam(2, 2, 1, 255, "GRAYSCALE", pixels)
    im = open_pam(data)
    assert im.mode == "L"
    assert im.size == (2, 2)
    assert list(im.get_flattened_data()) == [0, 128, 255, 64]


def test_read_rgb():
    pixels = bytes([255, 0, 0, 0, 255, 0, 0, 0, 255, 128, 128, 128])
    data = make_pam(2, 2, 3, 255, "RGB", pixels)
    im = open_pam(data)
    assert im.mode == "RGB"
    assert im.size == (2, 2)
    assert list(im.get_flattened_data()) == [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]


def test_read_rgba():
    pixels = bytes([255, 0, 0, 255, 0, 255, 0, 128, 0, 0, 255, 0, 0, 0, 0, 255])
    data = make_pam(2, 2, 4, 255, "RGB_ALPHA", pixels)
    im = open_pam(data)
    assert im.mode == "RGBA"
    assert im.size == (2, 2)
    assert list(im.get_flattened_data()) == [(255, 0, 0, 255), (0, 255, 0, 128), (0, 0, 255, 0), (0, 0, 0, 255)]


def test_read_grayscale_alpha():
    pixels = bytes([200, 255, 100, 128])
    data = make_pam(2, 1, 2, 255, "GRAYSCALE_ALPHA", pixels)
    im = open_pam(data)
    assert im.mode == "LA"
    assert im.size == (2, 1)
    assert list(im.get_flattened_data()) == [(200, 255), (100, 128)]


def test_read_blackandwhite():
    # PAM: 0=black, 1=white
    pixels = bytes([0, 1, 1, 0])
    data = make_pam(2, 2, 1, 1, "BLACKANDWHITE", pixels)
    im = open_pam(data)
    assert im.mode == "1"
    assert im.size == (2, 2)
    values = list(im.get_flattened_data())
    assert values == [0, 255, 255, 0]


def test_read_blackandwhite_alpha():
    pixels = bytes([0, 255, 1, 128])
    data = make_pam(2, 1, 2, 1, "BLACKANDWHITE_ALPHA", pixels)
    im = open_pam(data)
    assert im.mode == "LA"
    assert im.size == (2, 1)


def test_read_grayscale_16bit():
    # maxval=65535, 2 bytes per sample big-endian
    pixels = struct.pack(">4H", 0, 32768, 65535, 16384)
    data = make_pam(2, 2, 1, 65535, "GRAYSCALE", pixels)
    im = open_pam(data)
    assert im.mode == "I"
    assert im.size == (2, 2)
    values = list(im.get_flattened_data())
    assert values == [0, 32768, 65535, 16384]


def test_read_non_standard_maxval():
    # maxval=100, value 50 should scale to ~128
    pixels = bytes([0, 50, 100])
    data = make_pam(3, 1, 1, 100, "GRAYSCALE", pixels)
    im = open_pam(data)
    assert im.mode == "L"
    values = list(im.get_flattened_data())
    assert values[0] == 0
    assert values[1] == 128  # round(50/100 * 255) = 128
    assert values[2] == 255


def test_read_with_comments():
    pixels = bytes([42])
    data = make_pam(1, 1, 1, 255, "GRAYSCALE", pixels, comments=["test comment", "another one"])
    im = open_pam(data)
    assert im.mode == "L"
    assert list(im.get_flattened_data()) == [42]


def test_read_infer_tupltype_grayscale():
    pixels = bytes([100])
    data = make_pam(1, 1, 1, 255, None, pixels)
    im = open_pam(data)
    assert im.mode == "L"


def test_read_infer_tupltype_rgb():
    pixels = bytes([255, 0, 0])
    data = make_pam(1, 1, 3, 255, None, pixels)
    im = open_pam(data)
    assert im.mode == "RGB"


def test_read_infer_tupltype_rgba():
    pixels = bytes([255, 0, 0, 128])
    data = make_pam(1, 1, 4, 255, None, pixels)
    im = open_pam(data)
    assert im.mode == "RGBA"


def test_read_infer_tupltype_blackandwhite():
    pixels = bytes([1])
    data = make_pam(1, 1, 1, 1, None, pixels)
    im = open_pam(data)
    assert im.mode == "1"


def test_reject_wrong_magic():
    # Not P7 - should not be opened as PAM
    data = b"P6\n1 1\n255\n\x00\x00\x00"
    im = open_pam(data)
    assert im.format != "PAM"


def test_reject_missing_fields():
    bad = b"P7\nWIDTH 1\nHEIGHT 1\nENDHDR\n"
    with pytest.raises(Exception):
        open_pam(bad)


def test_reject_truncated_header():
    bad = b"P7\nWIDTH 1\n"
    with pytest.raises(Exception):
        open_pam(bad)


# --- Write/read round-trip tests ---


def test_roundtrip_l():
    im = Image.new("L", (3, 2), 42)
    buf = io.BytesIO()
    im.save(buf, format="PAM")
    buf.seek(0)
    im2 = Image.open(buf)
    assert im2.mode == "L"
    assert list(im2.get_flattened_data()) == list(im.get_flattened_data())


def test_roundtrip_rgb():
    im = Image.new("RGB", (2, 2), (10, 20, 30))
    buf = io.BytesIO()
    im.save(buf, format="PAM")
    buf.seek(0)
    im2 = Image.open(buf)
    assert im2.mode == "RGB"
    assert list(im2.get_flattened_data()) == list(im.get_flattened_data())


def test_roundtrip_rgba():
    im = Image.new("RGBA", (2, 2), (10, 20, 30, 200))
    buf = io.BytesIO()
    im.save(buf, format="PAM")
    buf.seek(0)
    im2 = Image.open(buf)
    assert im2.mode == "RGBA"
    assert list(im2.get_flattened_data()) == list(im.get_flattened_data())


def test_roundtrip_la():
    im = Image.new("LA", (2, 2), (100, 200))
    buf = io.BytesIO()
    im.save(buf, format="PAM")
    buf.seek(0)
    im2 = Image.open(buf)
    assert im2.mode == "LA"
    assert list(im2.get_flattened_data()) == list(im.get_flattened_data())


def test_roundtrip_1():
    im = Image.new("1", (4, 2), 1)
    im.putpixel((0, 0), 0)
    im.putpixel((1, 1), 0)
    buf = io.BytesIO()
    im.save(buf, format="PAM")
    buf.seek(0)
    im2 = Image.open(buf)
    assert im2.mode == "1"
    # Mode "1" getdata() returns 0 or 255; compare as booleans
    assert [bool(v) for v in im2.get_flattened_data()] == [bool(v) for v in im.get_flattened_data()]


def test_roundtrip_i():
    im = Image.new("I", (2, 2), 1000)
    buf = io.BytesIO()
    im.save(buf, format="PAM")
    buf.seek(0)
    im2 = Image.open(buf)
    assert im2.mode == "I"
    assert list(im2.get_flattened_data()) == list(im.get_flattened_data())


def test_save_unsupported_mode():
    im = Image.new("CMYK", (1, 1))
    buf = io.BytesIO()
    with pytest.raises(OSError, match="cannot write mode CMYK"):
        im.save(buf, format="PAM")


# --- Multi-frame ---


def make_rgb_frame(r, g, b, width=2, height=2):
    pixels = bytes([r, g, b] * (width * height))
    return make_pam(width, height, 3, 255, "RGB", pixels)


def test_multiframe_n_frames():
    data = make_rgb_frame(255, 0, 0) + make_rgb_frame(0, 255, 0) + make_rgb_frame(0, 0, 255)
    im = open_pam(data)
    assert im.n_frames == 3
    assert im.is_animated is True


def test_multiframe_seek_and_read():
    data = make_rgb_frame(255, 0, 0) + make_rgb_frame(0, 255, 0) + make_rgb_frame(0, 0, 255)
    im = open_pam(data)
    colors = []
    for i in range(im.n_frames):
        im.seek(i)
        im.load()
        colors.append(im.getpixel((0, 0)))
    assert colors == [(255, 0, 0), (0, 255, 0), (0, 0, 255)]


def test_multiframe_seek_backwards():
    data = make_rgb_frame(255, 0, 0) + make_rgb_frame(0, 0, 255)
    im = open_pam(data)
    im.seek(1)
    im.load()
    assert im.getpixel((0, 0)) == (0, 0, 255)
    im.seek(0)
    im.load()
    assert im.getpixel((0, 0)) == (255, 0, 0)


def test_multiframe_seek_past_end():
    data = make_rgb_frame(255, 0, 0)
    im = open_pam(data)
    with pytest.raises(EOFError):
        im.seek(1)


def test_multiframe_tell():
    data = make_rgb_frame(255, 0, 0) + make_rgb_frame(0, 255, 0)
    im = open_pam(data)
    assert im.tell() == 0
    im.seek(1)
    assert im.tell() == 1


def test_single_frame_not_animated():
    data = make_rgb_frame(42, 42, 42)
    im = open_pam(data)
    assert im.n_frames == 1
    assert im.is_animated is False


def test_multiframe_different_modes():
    """Frames can have different sizes and modes."""
    frame1 = make_pam(2, 2, 4, 255, "RGB_ALPHA", bytes([255, 0, 0, 255] * 4))
    frame2 = make_pam(3, 1, 1, 255, "GRAYSCALE", bytes([128, 64, 32]))
    im = open_pam(frame1 + frame2)
    assert im.n_frames == 2

    im.seek(0)
    im.load()
    assert im.mode == "RGBA"
    assert im.size == (2, 2)

    im.seek(1)
    im.load()
    assert im.mode == "L"
    assert im.size == (3, 1)


# --- Registration ---


def test_pam_extension_registered():
    assert Image.registered_extensions().get(".pam") == "PAM"


def test_format_attribute():
    pixels = bytes([128])
    data = make_pam(1, 1, 1, 255, "GRAYSCALE", pixels)
    im = open_pam(data)
    assert im.format == "PAM"
