"""
Pillow plugin that bridges to netpbm's anytopnm converter.

Registers for file extensions of formats that netpbm handles but
Pillow doesn't support natively, giving access to ~80+ obscure
image formats through the system's netpbm installation.
"""

from __future__ import annotations

import io
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageFile

ANYTOPNM = shutil.which("anytopnm")

# Extensions for formats netpbm handles that Pillow doesn't natively support.
# Sorted alphabetically. Excludes .info (handled by amigainfo package).
EXTENSIONS = [
    ".raster",  # Andrew Toolkit raster
    ".avs",  # AVS X image
    ".bie",  # JBIG (alt extension)
    ".brush",  # Xerox doodle brush
    ".cis",  # CompuServe RLE
    ".cr2",  # Canon RAW
    ".eyuv",  # Encoder YUV
    ".g3",  # Group 3 fax
    ".gem",  # GEM raster
    ".gould",  # Gould scanner
    ".hips",  # HIPS
    ".icon",  # Sun icon
    ".iff",  # Amiga IFF ILBM
    ".ilbm",  # Amiga IFF ILBM (alt extension)
    ".jbg",  # JBIG (alt extension)
    ".jbig",  # JBIG
    ".lbm",  # Amiga IFF ILBM (alt extension)
    ".leaf",  # Interleaf
    ".lsm",  # Zeiss confocal
    ".macp",  # MacPaint
    ".mda",  # Microdesign
    ".mgr",  # MGR window manager bitmap
    ".mrf",  # MRF
    ".mtv",  # MTV ray tracer
    ".nef",  # Nikon RAW
    ".neo",  # Atari Neochrome
    ".pc1",  # Atari Degas Elite
    ".pdb",  # Palm DB image
    ".pi1",  # Atari Degas
    ".pi3",  # Atari Degas low-res
    ".pj",  # HP PaintJet
    ".pk",  # TeX PK font bitmap
    ".psid",  # PostScript image data
    ".qrt",  # QRT ray tracer
    ".rla",  # Wavefront RLA
    ".rle",  # Utah RLE
    ".sbig",  # SBIG CCD camera
    ".sir",  # Solitaire
    ".sld",  # AutoCAD slide
    ".spc",  # Atari compressed Spectrum
    ".spot",  # SPOT satellite
    ".spu",  # Atari uncompressed Spectrum
    ".srf",  # Garmin SRF
    ".st4",  # SBIG ST-4 CCD camera
    ".svg",  # SVG (rasterized via svgtopam)
    ".wbmp",  # Wireless bitmap (WAP)
    ".wfa",  # Fiasco wavelet
    ".xim",  # X IMage
    ".xwd",  # X Window Dump
    ".ybm",  # Bennet Yee face file
    ".yuy2",  # YUY2 video frame
    ".yuv",  # 4:1:1 YUV
]

_EXTENSION_SET = frozenset(EXTENSIONS)


class AnytopnmImageFile(ImageFile.ImageFile):
    format = "ANYTOPNM"
    format_description = "Image via netpbm anytopnm"

    _loaded_image = None

    def _open(self) -> None:
        # Only handle files with extensions we've registered for
        name = getattr(self.fp, "name", None) or self.filename
        ext = Path(name).suffix.lower() if name else ""
        if ext not in _EXTENSION_SET:
            raise SyntaxError("not an anytopnm-registered extension")

        if ANYTOPNM is None:
            raise SyntaxError("anytopnm not found on PATH. Install netpbm: https://netpbm.sourceforge.net/")

        path = self._get_path()

        result = subprocess.run(
            [ANYTOPNM, str(path)],
            capture_output=True,
        )
        if result.returncode != 0:
            raise SyntaxError(f"anytopnm failed: {result.stderr.decode(errors='replace').strip()}")

        # Exclude our own format to prevent infinite recursion
        im = Image.open(io.BytesIO(result.stdout), formats=["PPM", "PAM"])
        im.load()

        self._loaded_image = im
        self._size = im.size
        self._mode = im.mode
        self.tile = []

    def _get_path(self) -> Path:
        """Get a filesystem path for anytopnm. Write to tempfile if needed."""
        name = getattr(self.fp, "name", None)
        if name and Path(name).is_file():
            return Path(name)

        # Stream without a file path - write to temp file
        self.fp.seek(0)
        data = self.fp.read()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".img")
        tmp.write(data)
        tmp.flush()
        tmp.close()
        self._tmp_path = Path(tmp.name)
        return self._tmp_path

    def load(self):
        if self._loaded_image is not None:
            self.im = self._loaded_image.im.copy()
            self._loaded_image = None
        return self.im

    def __del__(self):
        tmp = getattr(self, "_tmp_path", None)
        if tmp and tmp.exists():
            tmp.unlink()


Image.register_open(AnytopnmImageFile.format, AnytopnmImageFile)
for ext in EXTENSIONS:
    Image.register_extension(AnytopnmImageFile.format, ext)
