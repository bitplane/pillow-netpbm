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
    Format(
        name="ATK Raster",
        converter="atktopbm",
        extensions=(".raster",),
        magic=b"\\begindata{rast",
    ),
    Format(
        name="Amiga Info Icon",
        converter="infotopam",
        extensions=(".info",),
        magic=b"\xe3\x10",
    ),
    Format(
        name="Amiga IFF ILBM",
        converter="ilbmtoppm",
        extensions=(".iff", ".ilbm", ".lbm"),
        match=lambda prefix: prefix[:4] == b"FORM" and prefix[8:12] == b"ILBM",
    ),
    Format(
        name="Atari Degas",
        converter="pi1toppm",
        extensions=(".pi1",),
    ),
    Format(
        name="Atari Degas Elite",
        converter="pc1toppm",
        extensions=(".pc1",),
        magic=b"\x80\x00",
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
        magic=b"AutoCAD Slide\r\n\x1a",
        mime_type="image/x-sld",
    ),
    Format(
        name="AVS X Image",
        converter="avstopam",
        extensions=(".avs",),
    ),
    # Camera RAW (cameratopam) removed: segfaults on NEF, fails on CR2
    Format(
        name="CMU Window Manager Bitmap",
        converter="cmuwmtopbm",
        magic=b"\xf1\x00\x40\xbb",
    ),
    Format(
        name="CompuServe RLE",
        converter="cistopbm",
        extensions=(".cis", ".rle"),
        match=lambda prefix: prefix[:3] in (b"\x1bGH", b"\x1bGM"),
    ),
    # Encoder YUV (eyuvtoppm) removed: headerless format, dimensions not in file
    Format(
        name="Fiasco Wavelet",
        converter="fiascotopnm",
        extensions=(".wfa", ".fco"),
        magic=b"FIASCO",
    ),
    Format(
        name="FITS",
        converter="fitstopnm",
        extensions=(".fits", ".fit", ".fts"),
        magic=b"SIMPLE",
        mime_type="image/fits",
    ),
    Format(
        name="Garmin SRF",
        converter="srftopam",
        extensions=(".srf",),
        magic=b"GARMIN BITMAP 01",
    ),
    Format(
        name="GEM Raster",
        converter="gemtopnm",
        extensions=(".gem", ".img"),
        match=lambda prefix: prefix[:4] == b"\x00\x01\x00\x08",
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
        name="HIPS",
        converter="hipstopgm",
        extensions=(".hips",),
    ),
    Format(
        name="HP PaintJet",
        converter="pjtoppm",
        extensions=(".pj",),
    ),
    # Img-whatnot (imgtoppm) removed: .img clashes with many formats, no test data, origin server defunct
    Format(
        name="Interleaf",
        converter="leaftoppm",
        extensions=(".leaf", ".iimg"),
        magic=b"\x89\x4f\x50\x53",
    ),
    Format(
        name="JBIG",
        converter="jbigtopnm",
        extensions=(".jbig", ".jbg", ".bie"),
    ),
    # Kodak Photo CD (hpcdtoppm) removed: Pillow handles PCD natively
    Format(
        name="Lisp Machine Bitmap",
        converter="lispmtopgm",
        magic=b"This is a BitMap",
    ),
    Format(
        name="MacPaint",
        converter="macptopbm",
        extensions=(".macp", ".mac", ".pntg"),
    ),
    Format(
        name="MGR Bitmap",
        converter="mgrtopbm",
        extensions=(".mgr",),
        match=lambda prefix: prefix[:2] in (b"yz", b"xz", b"zz", b"zy"),
    ),
    Format(
        name="Microdesign",
        converter="mdatopbm",
        extensions=(".mda",),
        match=lambda prefix: prefix[:4] in (b".MDA", b".MDP"),
    ),
    Format(
        name="MRF",
        converter="mrftopbm",
        extensions=(".mrf",),
        magic=b"MRF1",
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
    # PostScript Image Data (psidtopgm) removed: requires manual width/height/bps args, not a file format
    Format(
        name="QRT Ray Tracer",
        converter="qrttoppm",
        extensions=(".qrt", ".dis"),
    ),
    Format(
        name="SBIG CCD Camera",
        converter="sbigtopgm",
        extensions=(".sbig",),
        match=lambda prefix: prefix[:3] == b"ST-" and b"Image" in prefix[:16],
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
        magic=b"\x4f\x3a",
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
        converter="sunicontopnm",
        extensions=(".icon",),
        match=lambda prefix: prefix[:16] == b"/* Format_versio",
    ),
    Format(
        name="SVG",
        converter="svgtopam",
        extensions=(".svg",),
    ),
    # TeX PK Font (pktopbm) removed: writes multiple PBM files (one per glyph), not stdout
    Format(
        name="Usenix FaceSaver",
        converter="fstopgm",
        extensions=(".fs", ".face"),
        match=lambda prefix: prefix[:10] == b"FirstName:",
    ),
    Format(
        name="Utah RLE",
        converter="rletopnm",
        extensions=(".rle",),
        magic=b"\x52\xcc",
    ),
    # Wavefront RLA (rlatopam) removed: broken on 64-bit (sizeof(long) misaligns header), numChan never set
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
        match=lambda prefix: prefix[4:8] in (b"\x00\x00\x00\x06", b"\x00\x00\x00\x07"),
    ),
    Format(
        name="XV Thumbnail",
        converter="xvminitoppm",
        magic=b"P7 332",
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
        magic=b"!!",
    ),
    # YUV 4:1:1 (yuvtoppm) removed: headerless format, dimensions not in file
    # YUY2 Video Frame (yuy2topam) removed: headerless format, dimensions not in file
    # Zeiss Confocal (zeisstopnm) removed: LSM is TIFF-based, Pillow handles it natively
]
