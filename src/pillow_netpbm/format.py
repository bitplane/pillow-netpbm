"""
Format specifications for netpbm converter bridges.

Each Format maps a file format to its specific netpbm converter binary,
with optional magic-based content detection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Format:
    name: str
    converter: str
    extensions: tuple[str, ...] = ()
    magic: bytes | None = None
    magic_offset: int = 0
    mime_type: str | None = None
    match: Callable[[bytes], bool] | None = field(default=None, repr=False)


# Sorted alphabetically by name.
# Tier 1: magic known (matched by content, high confidence)
# Tier 2: extension only (magic=None, lower confidence)
FORMATS = [
    # Tier 1 — magic known
    Format(
        name="ATK Raster",
        converter="atktopbm",
        extensions=(".raster",),
        magic=b"\\begindata{rast",
    ),
    # Tier 2 — extension only
    Format(
        name="Amiga Info Icon",
        converter="infotopam",
        extensions=(".info",),
    ),
    Format(
        name="Amiga IFF ILBM",
        converter="ilbmtoppm",
        extensions=(".iff", ".ilbm", ".lbm"),
    ),
    Format(
        name="Atari Degas",
        converter="pi1toppm",
        extensions=(".pi1",),
    ),
    Format(
        name="Atari DiddleBug Sketch",
        converter="ddbugtopbm",
        extensions=(".ddbug",),
    ),
    Format(
        name="Atari Degas Elite",
        converter="pc1toppm",
        extensions=(".pc1",),
    ),
    Format(
        name="Atari Degas Low-Res",
        converter="pi3topbm",
        extensions=(".pi3",),
    ),
    Format(
        name="Atari Neochrome",
        converter="neotoppm",
        extensions=(".neo",),
    ),
    Format(
        name="Atari Compressed Spectrum",
        converter="spctoppm",
        extensions=(".spc",),
    ),
    Format(
        name="Atari Uncompressed Spectrum",
        converter="sputoppm",
        extensions=(".spu",),
    ),
    Format(
        name="AutoCAD Slide",
        converter="sldtoppm",
        extensions=(".sld",),
    ),
    Format(
        name="AVS X Image",
        converter="avstopam",
        extensions=(".avs",),
    ),
    Format(
        name="Bio-Rad Confocal",
        converter="bioradtopgm",
        extensions=(".biorad",),
    ),
    Format(
        name="Camera RAW",
        converter="cameratopam",
        extensions=(".cr2", ".nef"),
    ),
    Format(
        name="CMU Window Manager Bitmap",
        converter="cmuwmtopbm",
        extensions=(".cmuwm",),
    ),
    Format(
        name="CompuServe RLE",
        converter="cistopbm",
        extensions=(".cis",),
    ),
    Format(
        name="Encoder YUV",
        converter="eyuvtoppm",
        extensions=(".eyuv",),
    ),
    Format(
        name="Epson ESC/P2",
        converter="escp2topbm",
        extensions=(".escp2",),
    ),
    Format(
        name="Fiasco Wavelet",
        converter="fiascotopnm",
        extensions=(".wfa",),
    ),
    Format(
        name="FITS",
        converter="fitstopnm",
        extensions=(".fits", ".fit", ".fts"),
        mime_type="image/fits",
    ),
    Format(
        name="Garmin SRF",
        converter="srftopam",
        extensions=(".srf",),
    ),
    Format(
        name="GEM Raster",
        converter="gemtopnm",
        extensions=(".gem",),
    ),
    Format(
        name="Gould Scanner",
        converter="gouldtoppm",
        extensions=(".gould",),
    ),
    Format(
        name="Group 3 Fax",
        converter="g3topbm",
        extensions=(".g3",),
    ),
    Format(
        name="HP ThinkJet",
        converter="thinkjettopbm",
        extensions=(".thinkjet",),
    ),
    Format(
        name="HIPS",
        converter="hipstopgm",
        extensions=(".hips",),
    ),
    Format(
        name="HP PaintJet",
        converter="pjtoppm",
        extensions=(".pj",),
    ),
    Format(
        name="Img-whatnot",
        converter="imgtoppm",
        extensions=(".img",),
    ),
    Format(
        name="Interleaf",
        converter="leaftoppm",
        extensions=(".leaf",),
    ),
    Format(
        name="JBIG",
        converter="jbigtopnm",
        extensions=(".jbig", ".jbg", ".bie"),
    ),
    Format(
        name="Kodak Photo CD",
        converter="hpcdtoppm",
        extensions=(".pcd",),
    ),
    Format(
        name="Kodak Photo CD Overview",
        converter="pcdovtoppm",
        extensions=(".pcd_ovr",),
    ),
    Format(
        name="Lisp Machine Bitmap",
        converter="lispmtopgm",
        extensions=(".lispm",),
    ),
    Format(
        name="MacPaint",
        converter="macptopbm",
        extensions=(".macp",),
    ),
    Format(
        name="MGR Bitmap",
        converter="mgrtopbm",
        extensions=(".mgr",),
    ),
    Format(
        name="Microdesign",
        converter="mdatopbm",
        extensions=(".mda",),
    ),
    Format(
        name="MRF",
        converter="mrftopbm",
        extensions=(".mrf",),
    ),
    Format(
        name="MTV Ray Tracer",
        converter="mtvtoppm",
        extensions=(".mtv",),
    ),
    Format(
        name="Palm DB Image",
        converter="pdbimgtopam",
        extensions=(".pdb",),
    ),
    Format(
        name="PostScript Image Data",
        converter="psidtopgm",
        extensions=(".psid",),
    ),
    Format(
        name="QRT Ray Tracer",
        converter="qrttoppm",
        extensions=(".qrt",),
    ),
    Format(
        name="SBIG CCD Camera",
        converter="sbigtopgm",
        extensions=(".sbig",),
    ),
    Format(
        name="SBIG ST-4 CCD Camera",
        converter="st4topgm",
        extensions=(".st4",),
    ),
    Format(
        name="Solitaire",
        converter="sirtopnm",
        extensions=(".sir",),
    ),
    Format(
        name="Sony Mavica 411",
        converter="411toppm",
        extensions=(".411",),
    ),
    Format(
        name="SPOT Satellite",
        converter="spottopgm",
        extensions=(".spot",),
    ),
    Format(
        name="Sun Icon",
        converter="icontopbm",
        extensions=(".icon",),
    ),
    Format(
        name="Sun Icon (color)",
        converter="sunicontopnm",
        extensions=(".sunicon",),
    ),
    Format(
        name="SVG",
        converter="svgtopam",
        extensions=(".svg",),
    ),
    Format(
        name="TeX PK Font Bitmap",
        converter="pktopbm",
        extensions=(".pk",),
    ),
    Format(
        name="Usenix FaceSaver",
        converter="fstopgm",
        extensions=(".fs",),
    ),
    Format(
        name="Utah RLE",
        converter="rletopnm",
        extensions=(".rle",),
    ),
    Format(
        name="Wavefront RLA",
        converter="rlatopam",
        extensions=(".rla",),
    ),
    Format(
        name="Wireless Bitmap",
        converter="wbmptopbm",
        extensions=(".wbmp",),
    ),
    Format(
        name="X IMage",
        converter="ximtoppm",
        extensions=(".xim",),
    ),
    Format(
        name="X Window Dump",
        converter="xwdtopnm",
        extensions=(".xwd",),
    ),
    Format(
        name="XV Thumbnail",
        converter="xvminitoppm",
        extensions=(".xvmini",),
    ),
    Format(
        name="Xerox Doodle Brush",
        converter="brushtopbm",
        extensions=(".brush",),
    ),
    Format(
        name="YBM Face File",
        converter="ybmtopbm",
        extensions=(".ybm",),
    ),
    Format(
        name="YUV 4:1:1",
        converter="yuvtoppm",
        extensions=(".yuv",),
    ),
    Format(
        name="YUY2 Video Frame",
        converter="yuy2topam",
        extensions=(".yuy2",),
    ),
    Format(
        name="Zeiss Confocal",
        converter="zeisstopnm",
        extensions=(".lsm",),
    ),
]
