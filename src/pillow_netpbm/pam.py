"""
PAM (P7) image format plugin for Pillow.

Adds read/write support for the Portable Arbitrary Map format,
the generalized netpbm format that supports alpha channels.
"""

from __future__ import annotations

from typing import IO

from PIL import Image, ImageFile


TUPLTYPE_TO_MODE = {
    "BLACKANDWHITE": "1",
    "GRAYSCALE": "L",
    "RGB": "RGB",
    "BLACKANDWHITE_ALPHA": "LA",
    "GRAYSCALE_ALPHA": "LA",
    "RGB_ALPHA": "RGBA",
}

MODE_TO_PAM = {
    "1": ("BLACKANDWHITE", 1, 1),
    "L": ("GRAYSCALE", 1, 255),
    "LA": ("GRAYSCALE_ALPHA", 2, 255),
    "I": ("GRAYSCALE", 1, 65535),
    "RGB": ("RGB", 3, 255),
    "RGBA": ("RGB_ALPHA", 4, 255),
}


def _accept(prefix: bytes) -> bool:
    return prefix[:3] in (b"P7\n", b"P7 ")


def _parse_header(fp) -> dict:
    """Parse a PAM header, returning a dict with WIDTH, HEIGHT, DEPTH, MAXVAL, TUPLTYPE."""
    magic = fp.readline().strip()
    if magic != b"P7":
        raise SyntaxError("not a PAM file")

    header = {}
    tupltype_parts = []

    while True:
        line = fp.readline()
        if not line:
            raise SyntaxError("unexpected end of PAM header")

        line = line.strip()
        if not line or line.startswith(b"#"):
            continue

        if line == b"ENDHDR":
            break

        parts = line.split(None, 1)
        if len(parts) != 2:
            raise SyntaxError(f"malformed PAM header line: {line!r}")

        key = parts[0].decode("ascii")
        value = parts[1].decode("ascii")

        if key == "TUPLTYPE":
            tupltype_parts.append(value)
        elif key in ("WIDTH", "HEIGHT", "DEPTH", "MAXVAL"):
            header[key] = int(value)
        # ignore unknown keys per spec

    for required in ("WIDTH", "HEIGHT", "DEPTH", "MAXVAL"):
        if required not in header:
            raise SyntaxError(f"missing required PAM header field: {required}")

    if tupltype_parts:
        header["TUPLTYPE"] = " ".join(tupltype_parts)
    else:
        header["TUPLTYPE"] = _infer_tupltype(header["DEPTH"], header["MAXVAL"])

    return header


def _infer_tupltype(depth: int, maxval: int) -> str:
    """Infer TUPLTYPE from DEPTH when not specified in header."""
    if depth == 1:
        return "BLACKANDWHITE" if maxval == 1 else "GRAYSCALE"
    if depth == 2:
        return "GRAYSCALE_ALPHA"
    if depth == 3:
        return "RGB"
    if depth == 4:
        return "RGB_ALPHA"
    raise SyntaxError(f"cannot infer TUPLTYPE for depth {depth}")


def _determine_mode(tupltype: str, maxval: int) -> str:
    """Map TUPLTYPE + MAXVAL to a PIL image mode."""
    mode = TUPLTYPE_TO_MODE.get(tupltype)
    if mode is None:
        raise SyntaxError(f"unsupported PAM TUPLTYPE: {tupltype}")
    if mode == "L" and maxval > 255:
        return "I"
    return mode


class PamImageFile(ImageFile.ImageFile):
    format = "PAM"
    format_description = "PAM image"

    def _open(self) -> None:
        header = _parse_header(self.fp)
        width = header["WIDTH"]
        height = header["HEIGHT"]
        depth = header["DEPTH"]
        maxval = header["MAXVAL"]
        tupltype = header["TUPLTYPE"]

        self._size = width, height
        mode = _determine_mode(tupltype, maxval)
        self._mode = mode

        data_offset = self.fp.tell()

        if maxval == 255:
            self.tile = [ImageFile._Tile("raw", (0, 0, width, height), data_offset, (mode, 0, 1))]
        elif maxval == 1 and tupltype == "BLACKANDWHITE":
            self.tile = [ImageFile._Tile("raw", (0, 0, width, height), data_offset, ("1;8", 0, 1))]
        elif maxval == 65535 and mode == "I":
            self.tile = [ImageFile._Tile("raw", (0, 0, width, height), data_offset, ("I;16B", 0, 1))]
        else:
            self.tile = [ImageFile._Tile("pam", (0, 0, width, height), data_offset, (mode, maxval, depth))]


class PamDecoder(ImageFile.PyDecoder):
    """Decoder for PAM files with non-standard maxval that need rescaling."""

    _pulls_fd = True

    def decode(self, buffer: bytes | Image.SupportsArrayInterface) -> tuple[int, int]:
        mode, maxval, depth = self.args
        in_bytes = 2 if maxval > 255 else 1
        total_samples = self.state.xsize * self.state.ysize * depth

        raw = self.fd.read(total_samples * in_bytes)
        if len(raw) < total_samples * in_bytes:
            raise ValueError("truncated PAM data")

        if mode == "I":
            out_max = 65535
            rawmode = "I;32N"
            data = bytearray(total_samples * 4)
            for i in range(total_samples):
                if in_bytes == 1:
                    value = raw[i]
                else:
                    value = int.from_bytes(raw[i * 2 : i * 2 + 2], "big")
                scaled = round(value * out_max / maxval)
                data[i * 4 : i * 4 + 4] = scaled.to_bytes(4, byteorder="little")
        elif mode == "1":
            out_max = 255
            rawmode = "L"
            data = bytearray(total_samples)
            for i in range(total_samples):
                value = raw[i] if in_bytes == 1 else int.from_bytes(raw[i * 2 : i * 2 + 2], "big")
                data[i] = 255 if round(value * out_max / maxval) > 127 else 0
        else:
            out_max = 255
            rawmode = mode
            data = bytearray(total_samples)
            for i in range(total_samples):
                if in_bytes == 1:
                    value = raw[i]
                else:
                    value = int.from_bytes(raw[i * 2 : i * 2 + 2], "big")
                data[i] = round(value * out_max / maxval)

        self.set_as_raw(bytes(data), rawmode)
        return -1, 0


# BW byte value 0=black, 1=white → PAM convention
_L_TO_BW = bytes(1 if v > 127 else 0 for v in range(256))


def _save(im: Image.Image, fp: IO[bytes], filename: str | bytes) -> None:
    if im.mode not in MODE_TO_PAM:
        raise OSError(f"cannot write mode {im.mode} as PAM")

    tupltype, depth, maxval = MODE_TO_PAM[im.mode]

    header = (
        f"P7\n"
        f"WIDTH {im.size[0]}\n"
        f"HEIGHT {im.size[1]}\n"
        f"DEPTH {depth}\n"
        f"MAXVAL {maxval}\n"
        f"TUPLTYPE {tupltype}\n"
        f"ENDHDR\n"
    )
    fp.write(header.encode("ascii"))

    if im.mode == "1":
        data = im.convert("L").tobytes("raw", "L")
        fp.write(data.translate(_L_TO_BW))
    elif im.mode == "I":
        ImageFile._save(im, fp, [ImageFile._Tile("raw", (0, 0) + im.size, 0, ("I;16B", 0, 1))])
    else:
        ImageFile._save(im, fp, [ImageFile._Tile("raw", (0, 0) + im.size, 0, (im.mode, 0, 1))])


Image.register_open(PamImageFile.format, PamImageFile, _accept)
Image.register_save(PamImageFile.format, _save)
Image.register_decoder("pam", PamDecoder)
Image.register_extensions(PamImageFile.format, [".pam"])
Image.register_mime(PamImageFile.format, "image/x-portable-arbitrarymap")
