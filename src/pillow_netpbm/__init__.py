"""
Pillow plugins for netpbm formats.

Importing this package registers:
- PAM (P7) format for Image.open() and Image.save()
- anytopnm bridge for obscure formats via system netpbm
"""

from importlib.metadata import version

from pillow_netpbm.anytopnm import AnytopnmImageFile
from pillow_netpbm.pam import PamImageFile

__version__ = version("pillow_netpbm")
__all__ = ["PamImageFile", "AnytopnmImageFile"]
