"""
Wires Format specs to Pillow's plugin registry.

For each format whose converter binary is installed, creates a dynamic
ImageFile subclass and registers it with Pillow. Magic-based formats
are registered first so Pillow tries them before extension-only fallbacks.
"""

from __future__ import annotations

import re
import shutil
from typing import Callable

from PIL import Image

from pillow_netpbm.bridge import FORMAT_LOOKUP, NetpbmImageFile
from pillow_netpbm.format import FORMATS, Format


def _make_pillow_id(name: str) -> str:
    """Convert a format name to a Pillow format ID like NETPBM_ATK_RASTER."""
    return "NETPBM_" + re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")


def _make_accept(fmt: Format) -> Callable[[bytes], bool] | None:
    """Build an accept function from a Format's magic/match fields."""
    if fmt.match is not None:
        return fmt.match
    if fmt.magic is not None:
        offset = fmt.magic_offset
        end = offset + len(fmt.magic)
        magic = fmt.magic

        def accept(prefix: bytes) -> bool:
            return prefix[offset:end] == magic

        return accept
    return None


def _register_format(fmt: Format) -> None:
    pillow_id = _make_pillow_id(fmt.name)
    accept = _make_accept(fmt)

    cls = type(
        pillow_id,
        (NetpbmImageFile,),
        {
            "format": pillow_id,
            "format_description": f"{fmt.name} via netpbm",
        },
    )

    FORMAT_LOOKUP[pillow_id] = fmt
    Image.register_open(pillow_id, cls, accept)
    for ext in fmt.extensions:
        Image.register_extension(pillow_id, ext)
    if fmt.mime_type:
        Image.register_mime(pillow_id, fmt.mime_type)


# Two-pass: magic-based first (higher confidence), then extension-only
_magic_formats = []
_ext_formats = []

for _fmt in FORMATS:
    if shutil.which(_fmt.converter) is None:
        continue
    if _fmt.magic is not None or _fmt.match is not None:
        _magic_formats.append(_fmt)
    else:
        _ext_formats.append(_fmt)

for _fmt in _magic_formats:
    _register_format(_fmt)
for _fmt in _ext_formats:
    _register_format(_fmt)
