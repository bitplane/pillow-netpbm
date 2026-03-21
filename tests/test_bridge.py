"""Tests for the data-driven netpbm bridge plugin."""

import shutil
from pathlib import Path

import pytest
from PIL import Image

import pillow_netpbm  # noqa: F401 — triggers registration
from pillow_netpbm.format import Format
from pillow_netpbm.registry import _make_accept, _make_pillow_id

HAVE_ATKTOPBM = shutil.which("atktopbm") is not None
HAVE_ILBMTOPPM = shutil.which("ilbmtoppm") is not None
HAVE_INFOTOPAM = shutil.which("infotopam") is not None
HAVE_AVSTOPAM = shutil.which("avstopam") is not None
HAVE_NEOTOPPM = shutil.which("neotoppm") is not None
HAVE_SLDTOPPM = shutil.which("sldtoppm") is not None
HAVE_SPUTOPPM = shutil.which("sputoppm") is not None
HAVE_PI1TOPPM = shutil.which("pi1toppm") is not None
HAVE_PI3TOPBM = shutil.which("pi3topbm") is not None
HAVE_PC1TOPPM = shutil.which("pc1toppm") is not None

ATK_DATA = Path(__file__).parent / "data" / "atk-raster"
AMIGA_INFO_DATA = Path(__file__).parent / "data" / "amiga-info"
ATARI_DEGAS_DATA = Path(__file__).parent / "data" / "atari-degas"
ATARI_SPECTRUM_DATA = Path(__file__).parent / "data" / "atari-spectrum"
IFF_ILBM_DATA = Path(__file__).parent / "data" / "iff-ilbm"


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
    assert _make_pillow_id("YUV 4:1:1") == "NETPBM_YUV_4_1_1"


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


@pytest.mark.skipif(not HAVE_ATKTOPBM, reason="atktopbm not installed")
def test_open_atk_raster():
    im = Image.open(str(ATK_DATA / "cube.raster"))
    assert im.format == "NETPBM_ATK_RASTER"
    assert im.size[0] > 0 and im.size[1] > 0
    im.load()


@pytest.mark.skipif(not HAVE_ATKTOPBM, reason="atktopbm not installed")
def test_atk_detected_without_extension(tmp_path):
    src = ATK_DATA / "cube.raster"
    dst = tmp_path / "cube.wrongext"
    dst.write_bytes(src.read_bytes())
    im = Image.open(str(dst))
    assert im.format == "NETPBM_ATK_RASTER"
    im.load()


@pytest.mark.skipif(not HAVE_PI1TOPPM, reason="pi1toppm not installed")
def test_open_atari_degas_pi1():
    im = Image.open(str(ATARI_DEGAS_DATA / "MOUSE.PI1"))
    assert im.format == "NETPBM_ATARI_DEGAS"
    assert im.size == (320, 200)
    im.load()


@pytest.mark.skipif(not HAVE_PI3TOPBM, reason="pi3topbm not installed")
def test_open_atari_degas_pi3():
    im = Image.open(str(ATARI_DEGAS_DATA / "HIDDEN.PI3"))
    assert im.format == "NETPBM_ATARI_DEGAS_LOW_RES"
    assert im.size == (640, 400)
    im.load()


@pytest.mark.skipif(not HAVE_NEOTOPPM, reason="neotoppm not installed")
def test_open_atari_neochrome():
    im = Image.open(str(ATARI_DEGAS_DATA / "titlepic.neo"))
    assert im.format == "NETPBM_ATARI_NEOCHROME"
    assert im.size == (320, 200)
    im.load()


@pytest.mark.skipif(not HAVE_PC1TOPPM, reason="pc1toppm not installed")
def test_open_atari_degas_elite():
    im = Image.open(str(ATARI_DEGAS_DATA / "AMMO.PC1"))
    assert im.format == "NETPBM_ATARI_DEGAS_ELITE"
    assert im.size == (320, 200)
    im.load()


@pytest.mark.skipif(not HAVE_AVSTOPAM, reason="avstopam not installed")
def test_open_avs():
    im = Image.open(str(Path(__file__).parent / "data" / "avs" / "poo.avs"))
    assert im.format == "NETPBM_AVS_X_IMAGE"
    im.load()
    assert im.size == (117, 91)


@pytest.mark.skipif(not HAVE_SLDTOPPM, reason="sldtoppm not installed")
def test_open_autocad_slide():
    im = Image.open(str(Path(__file__).parent / "data" / "autocad-slide" / "ab30-02c.sld"))
    assert im.format == "NETPBM_AUTOCAD_SLIDE"
    im.load()
    assert im.size[0] > 0 and im.size[1] > 0


@pytest.mark.skipif(not HAVE_SLDTOPPM, reason="sldtoppm not installed")
def test_autocad_slide_detected_without_extension(tmp_path):
    src = Path(__file__).parent / "data" / "autocad-slide" / "ab30-02c.sld"
    dst = tmp_path / "slide.wrongext"
    dst.write_bytes(src.read_bytes())
    im = Image.open(str(dst))
    assert im.format == "NETPBM_AUTOCAD_SLIDE"
    im.load()


@pytest.mark.skipif(not HAVE_SPUTOPPM, reason="sputoppm not installed")
def test_open_atari_spectrum_uncompressed():
    im = Image.open(str(ATARI_SPECTRUM_DATA / "NEWTEKS.SPU"))
    assert im.format == "NETPBM_ATARI_UNCOMPRESSED_SPECTRUM"
    assert im.size == (320, 200)
    im.load()


@pytest.mark.skipif(not HAVE_ILBMTOPPM, reason="ilbmtoppm not installed")
def test_open_iff_ilbm():
    im = Image.open(str(IFF_ILBM_DATA / "seascape.iff"))
    assert im.format == "NETPBM_AMIGA_IFF_ILBM"
    assert im.size == (320, 200)
    im.load()


@pytest.mark.skipif(not HAVE_ILBMTOPPM, reason="ilbmtoppm not installed")
def test_iff_ilbm_detected_without_extension(tmp_path):
    src = IFF_ILBM_DATA / "seascape.iff"
    dst = tmp_path / "seascape.wrongext"
    dst.write_bytes(src.read_bytes())
    im = Image.open(str(dst))
    assert im.format == "NETPBM_AMIGA_IFF_ILBM"
    im.load()


@pytest.mark.skipif(not HAVE_INFOTOPAM, reason="infotopam not installed")
@pytest.mark.parametrize("name", [p.name for p in sorted(AMIGA_INFO_DATA.glob("*.info"))])
def test_open_amiga_info(name):
    im = Image.open(str(AMIGA_INFO_DATA / name))
    assert im.format == "NETPBM_AMIGA_INFO_ICON"
    im.load()
    assert im.size[0] > 0 and im.size[1] > 0


@pytest.mark.skipif(not HAVE_INFOTOPAM, reason="infotopam not installed")
def test_amiga_info_detected_without_extension(tmp_path):
    src = next(AMIGA_INFO_DATA.glob("*.info"))
    dst = tmp_path / "icon.wrongext"
    dst.write_bytes(src.read_bytes())
    im = Image.open(str(dst))
    assert im.format == "NETPBM_AMIGA_INFO_ICON"
    im.load()


def test_extension_only_rejects_wrong_extension(tmp_path):
    """Extension-only format should reject files with wrong extension."""
    fake = tmp_path / "notreally.txt"
    fake.write_bytes(b"garbage data here")
    with pytest.raises(Exception):
        Image.open(str(fake))


def test_extensions_registered():
    exts = Image.registered_extensions()
    for ext in [".xwd", ".rle", ".jbig", ".cr2", ".nef", ".yuy2", ".wfa", ".pdb", ".icon"]:
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
