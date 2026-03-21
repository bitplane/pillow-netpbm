"""
Pillow plugins for netpbm formats.

Importing this package registers:
- PAM (P7) format for Image.open() and Image.save()
- Per-format netpbm converter bridges for obscure image formats
"""

from importlib.metadata import version

from pillow_netpbm.bridge import NetpbmImageFile
from pillow_netpbm.pam import PamImageFile

import pillow_netpbm.registry  # noqa: F401 — triggers registration

__version__ = version("pillow_netpbm")
__all__ = ["PamImageFile", "NetpbmImageFile"]
