"""
Pillow ImageFile subclass that bridges to specific netpbm converter binaries.

Each registered format gets a dynamic subclass of NetpbmImageFile with
its own Pillow format ID (e.g. NETPBM_ATK_RASTER). The FORMAT_LOOKUP
dict is populated by registry.py at import time.
"""

from __future__ import annotations

import io
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageFile

from pillow_netpbm.format import Format

FORMAT_LOOKUP: dict[str, Format] = {}


class NetpbmImageFile(ImageFile.ImageFile):
    format = "NETPBM"
    format_description = "Image via netpbm"

    _loaded_image = None

    def _open(self) -> None:
        fmt = FORMAT_LOOKUP[self.format]

        if fmt.magic is None and fmt.match is None:
            name = getattr(self.fp, "name", None) or self.filename
            ext = Path(name).suffix.lower() if name else ""
            if ext not in fmt.extensions:
                raise SyntaxError(f"not a {fmt.name} file (wrong extension)")

        converter = shutil.which(fmt.converter)
        if converter is None:
            raise SyntaxError(f"{fmt.converter} not found on PATH")

        path = self._get_path()

        try:
            result = subprocess.run(
                [converter, str(path)],
                capture_output=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            raise SyntaxError(f"{fmt.converter} timed out")
        if result.returncode != 0:
            raise SyntaxError(f"{fmt.converter} failed: " f"{result.stderr.decode(errors='replace').strip()}")

        im = Image.open(io.BytesIO(result.stdout), formats=["PPM", "PAM"])
        im.load()

        self._loaded_image = im
        self._size = im.size
        self._mode = im.mode
        self.tile = []

    def _get_path(self) -> Path:
        """Get a filesystem path for the converter. Write to tempfile if needed."""
        name = getattr(self.fp, "name", None)
        if name and Path(name).is_file():
            return Path(name)

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
