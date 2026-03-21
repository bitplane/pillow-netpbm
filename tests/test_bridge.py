"""Tests for the data-driven netpbm bridge plugin."""

import shutil
from pathlib import Path

import pytest
from PIL import Image

import pillow_netpbm  # noqa: F401 — triggers registration
from pillow_netpbm.format import Format
from pillow_netpbm.registry import _make_accept, _make_pillow_id

DATA = Path(__file__).parent / "data"

# Hand-curated test image paths (real-world files, not synthetic)
ATK_DATA = DATA / "atk-raster"
AMIGA_INFO_DATA = DATA / "amiga-info"
ATARI_DEGAS_DATA = DATA / "atari-degas"
ATARI_SPECTRUM_DATA = DATA / "atari-spectrum"
IFF_ILBM_DATA = DATA / "iff-ilbm"

# Synthetic test data: (subdir, filename, converter, expected_format_id)
SYNTHETIC_FORMATS = [
    ("cmu-wm", "test.cmuwm", "cmuwmtopbm", "NETPBM_CMU_WINDOW_MANAGER_BITMAP"),
    ("compuserve-rle", "test.cis", "cistopbm", "NETPBM_COMPUSERVE_RLE"),
    ("facesaver", "test.fs", "fstopgm", "NETPBM_USENIX_FACESAVER"),
    ("fiasco", "test.wfa", "fiascotopnm", "NETPBM_FIASCO_WAVELET"),
    ("fits", "test.fits", "fitstopnm", "NETPBM_FITS"),
    ("garmin-srf", "test.srf", "srftopam", "NETPBM_GARMIN_SRF"),
    ("gem-raster", "test.gem", "gemtopnm", "NETPBM_GEM_RASTER"),
    ("group3-fax", "test.g3", "g3topbm", "NETPBM_GROUP_3_FAX"),
    ("hp-paintjet", "test.pj", "pjtoppm", "NETPBM_HP_PAINTJET"),
    ("interleaf", "test.leaf", "leaftoppm", "NETPBM_INTERLEAF"),
    ("jbig", "test.jbig", "jbigtopnm", "NETPBM_JBIG"),
    ("lisp-machine", "test.lispm", "lispmtopgm", "NETPBM_LISP_MACHINE_BITMAP"),
    ("macpaint", "test.macp", "macptopbm", "NETPBM_MACPAINT"),
    ("mgr-bitmap", "test.mgr", "mgrtopbm", "NETPBM_MGR_BITMAP"),
    ("microdesign", "test.mda", "mdatopbm", "NETPBM_MICRODESIGN"),
    ("mrf", "test.mrf", "mrftopbm", "NETPBM_MRF"),
    ("palm-db", "test.pdb", "pdbimgtopam", "NETPBM_PALM_DB_IMAGE"),
    ("sbig", "test.sbig", "sbigtopgm", "NETPBM_SBIG_CCD_CAMERA"),
    ("sbig-st4", "test.st4", "st4topgm", "NETPBM_SBIG_ST_4_CCD_CAMERA"),
    ("solitaire", "test.sir", "sirtopnm", "NETPBM_SOLITAIRE"),
    ("sun-icon", "test.icon", "sunicontopnm", "NETPBM_SUN_ICON"),
    ("svg", "test.svg", "svgtopam", "NETPBM_SVG"),
    ("utah-rle", "test.rle", "rletopnm", "NETPBM_UTAH_RLE"),
    ("wireless-bitmap", "test.wbmp", "wbmptopbm", "NETPBM_WIRELESS_BITMAP"),
    ("xv-thumbnail", "test.xvmini", "xvminitoppm", "NETPBM_XV_THUMBNAIL"),
    ("xwd", "test.xwd", "xwdtopnm", "NETPBM_X_WINDOW_DUMP"),
    ("ybm", "test.ybm", "ybmtopbm", "NETPBM_YBM_FACE_FILE"),
]


# ---------------------------------------------------------------------------
# Unit tests for registry helpers
# ---------------------------------------------------------------------------


def test_make_accept_with_magic():
    fmt = Format(name="Test", converter="test", magic=b"\x89PNG")
    accept = _make_accept(fmt)
    assert accept is not None
    assert accept(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)
    assert not accept(b"JFIF" + b"\x00" * 12)


def test_make_accept_with_offset():
    fmt = Format(name="Test", converter="test", magic=b"MAGIC", magic_offset=4)
    accept = _make_accept(fmt)
    assert accept(b"\x00\x00\x00\x00MAGIC" + b"\x00" * 7)
    assert not accept(b"MAGIC" + b"\x00" * 11)


def test_make_accept_with_match():
    def custom(prefix):
        return prefix[0:1] == b"X"

    fmt = Format(name="Test", converter="test", match=custom)
    accept = _make_accept(fmt)
    assert accept is custom


def test_make_accept_without_magic():
    fmt = Format(name="Test", converter="test")
    assert _make_accept(fmt) is None


def test_pillow_id():
    assert _make_pillow_id("ATK Raster") == "NETPBM_ATK_RASTER"
    assert _make_pillow_id("FITS") == "NETPBM_FITS"


def test_unavailable_converter_not_registered():
    exts = Image.registered_extensions()
    fmt = Format(
        name="Fake Format",
        converter="nonexistent_converter_xyz",
        extensions=(".fakefmt",),
    )
    pillow_id = _make_pillow_id(fmt.name)
    assert pillow_id not in Image.OPEN
    assert exts.get(".fakefmt") is None


# ---------------------------------------------------------------------------
# Synthetic round-trip tests (parametrized)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "subdir, filename, converter, expected_format",
    SYNTHETIC_FORMATS,
    ids=[s[0] for s in SYNTHETIC_FORMATS],
)
def test_open_synthetic(subdir, filename, converter, expected_format):
    if shutil.which(converter) is None:
        pytest.skip(f"{converter} not installed")
    path = DATA / subdir / filename
    im = Image.open(str(path))
    assert im.format == expected_format
    im.load()
    assert im.size[0] > 0 and im.size[1] > 0


# ---------------------------------------------------------------------------
# Hand-curated format tests (real-world files)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("atktopbm"), reason="atktopbm not installed")
def test_open_atk_raster():
    im = Image.open(str(ATK_DATA / "cube.raster"))
    assert im.format == "NETPBM_ATK_RASTER"
    assert im.size[0] > 0 and im.size[1] > 0
    im.load()


@pytest.mark.skipif(not shutil.which("atktopbm"), reason="atktopbm not installed")
def test_atk_detected_without_extension(tmp_path):
    src = ATK_DATA / "cube.raster"
    dst = tmp_path / "cube.wrongext"
    dst.write_bytes(src.read_bytes())
    im = Image.open(str(dst))
    assert im.format == "NETPBM_ATK_RASTER"
    im.load()


@pytest.mark.skipif(not shutil.which("pi1toppm"), reason="pi1toppm not installed")
def test_open_atari_degas_pi1():
    im = Image.open(str(ATARI_DEGAS_DATA / "MOUSE.PI1"))
    assert im.format == "NETPBM_ATARI_DEGAS"
    assert im.size == (320, 200)
    im.load()


@pytest.mark.skipif(not shutil.which("pi3topbm"), reason="pi3topbm not installed")
def test_open_atari_degas_pi3():
    im = Image.open(str(ATARI_DEGAS_DATA / "HIDDEN.PI3"))
    assert im.format == "NETPBM_ATARI_DEGAS_LOW_RES"
    assert im.size == (640, 400)
    im.load()


@pytest.mark.skipif(not shutil.which("neotoppm"), reason="neotoppm not installed")
def test_open_atari_neochrome():
    im = Image.open(str(ATARI_DEGAS_DATA / "titlepic.neo"))
    assert im.format == "NETPBM_ATARI_NEOCHROME"
    assert im.size == (320, 200)
    im.load()


@pytest.mark.skipif(not shutil.which("pc1toppm"), reason="pc1toppm not installed")
def test_open_atari_degas_elite():
    im = Image.open(str(ATARI_DEGAS_DATA / "AMMO.PC1"))
    assert im.format == "NETPBM_ATARI_DEGAS_ELITE"
    assert im.size == (320, 200)
    im.load()


@pytest.mark.skipif(not shutil.which("avstopam"), reason="avstopam not installed")
def test_open_avs():
    im = Image.open(str(DATA / "avs" / "poo.avs"))
    assert im.format == "NETPBM_AVS_X_IMAGE"
    im.load()
    assert im.size == (117, 91)


@pytest.mark.skipif(not shutil.which("sldtoppm"), reason="sldtoppm not installed")
def test_open_autocad_slide():
    im = Image.open(str(DATA / "autocad-slide" / "ab30-02c.sld"))
    assert im.format == "NETPBM_AUTOCAD_SLIDE"
    im.load()
    assert im.size[0] > 0 and im.size[1] > 0


@pytest.mark.skipif(not shutil.which("sldtoppm"), reason="sldtoppm not installed")
def test_autocad_slide_detected_without_extension(tmp_path):
    src = DATA / "autocad-slide" / "ab30-02c.sld"
    dst = tmp_path / "slide.wrongext"
    dst.write_bytes(src.read_bytes())
    im = Image.open(str(dst))
    assert im.format == "NETPBM_AUTOCAD_SLIDE"
    im.load()


@pytest.mark.skipif(not shutil.which("sputoppm"), reason="sputoppm not installed")
def test_open_atari_spectrum_uncompressed():
    im = Image.open(str(ATARI_SPECTRUM_DATA / "NEWTEKS.SPU"))
    assert im.format == "NETPBM_ATARI_UNCOMPRESSED_SPECTRUM"
    assert im.size == (320, 200)
    im.load()


@pytest.mark.skipif(not shutil.which("ilbmtoppm"), reason="ilbmtoppm not installed")
def test_open_iff_ilbm():
    im = Image.open(str(IFF_ILBM_DATA / "seascape.iff"))
    assert im.format == "NETPBM_AMIGA_IFF_ILBM"
    assert im.size == (320, 200)
    im.load()


@pytest.mark.skipif(not shutil.which("ilbmtoppm"), reason="ilbmtoppm not installed")
def test_iff_ilbm_detected_without_extension(tmp_path):
    src = IFF_ILBM_DATA / "seascape.iff"
    dst = tmp_path / "seascape.wrongext"
    dst.write_bytes(src.read_bytes())
    im = Image.open(str(dst))
    assert im.format == "NETPBM_AMIGA_IFF_ILBM"
    im.load()


@pytest.mark.skipif(not shutil.which("infotopam"), reason="infotopam not installed")
@pytest.mark.parametrize("name", [p.name for p in sorted(AMIGA_INFO_DATA.glob("*.info"))])
def test_open_amiga_info(name):
    im = Image.open(str(AMIGA_INFO_DATA / name))
    assert im.format == "NETPBM_AMIGA_INFO_ICON"
    im.load()
    assert im.size[0] > 0 and im.size[1] > 0


@pytest.mark.skipif(not shutil.which("infotopam"), reason="infotopam not installed")
def test_amiga_info_detected_without_extension(tmp_path):
    src = next(AMIGA_INFO_DATA.glob("*.info"))
    dst = tmp_path / "icon.wrongext"
    dst.write_bytes(src.read_bytes())
    im = Image.open(str(dst))
    assert im.format == "NETPBM_AMIGA_INFO_ICON"
    im.load()


# ---------------------------------------------------------------------------
# Registration and rejection tests
# ---------------------------------------------------------------------------


def test_extension_only_rejects_wrong_extension(tmp_path):
    """Extension-only format should reject files with wrong extension."""
    fake = tmp_path / "notreally.txt"
    fake.write_bytes(b"garbage data here")
    with pytest.raises(Exception):
        Image.open(str(fake))


def test_extensions_registered():
    exts = Image.registered_extensions()
    for ext in [".xwd", ".rle", ".jbig", ".wfa", ".pdb", ".icon"]:
        fmt_id = exts.get(ext)
        assert fmt_id is not None and fmt_id.startswith(
            "NETPBM_"
        ), f"{ext} not registered as NETPBM_ format (got {fmt_id})"


def test_format_pillow_id():
    """All registered netpbm formats should have NETPBM_ prefix."""
    netpbm_formats = [k for k in Image.OPEN if k.startswith("NETPBM_")]
    assert len(netpbm_formats) > 0
    for fmt_id in netpbm_formats:
        assert fmt_id.startswith("NETPBM_")
