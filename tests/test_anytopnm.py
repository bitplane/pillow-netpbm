"""Tests for anytopnm bridge plugin."""

import io
import shutil

import pytest
from PIL import Image

import pillow_netpbm  # noqa: F401 — triggers registration

HAVE_ANYTOPNM = shutil.which("anytopnm") is not None


@pytest.mark.skipif(not HAVE_ANYTOPNM, reason="anytopnm not installed")
def test_open_ppm_via_anytopnm(tmp_path):
    """Write a PPM file with an anytopnm-registered extension, open it through the bridge."""
    # Create a PPM and save with .xwd extension won't work since xwd has its own format
    # Instead, create a raw PPM file and use anytopnm directly
    im = Image.new("RGB", (4, 4), (255, 0, 0))
    ppm_path = tmp_path / "test.ppm"
    im.save(str(ppm_path))

    # anytopnm can convert PPM (it's a passthrough)
    from pillow_netpbm.anytopnm import ANYTOPNM

    import subprocess

    result = subprocess.run([ANYTOPNM, str(ppm_path)], capture_output=True)
    assert result.returncode == 0

    im2 = Image.open(io.BytesIO(result.stdout))
    assert im2.size == (4, 4)
    assert im2.mode == "RGB"


@pytest.mark.skipif(not HAVE_ANYTOPNM, reason="anytopnm not installed")
def test_anytopnm_bad_file(tmp_path):
    """anytopnm should fail on garbage data."""
    bad_path = tmp_path / "garbage.rle"
    bad_path.write_bytes(b"this is not an image")
    with pytest.raises(Exception):
        Image.open(str(bad_path))


def test_extensions_registered():
    exts = Image.registered_extensions()
    for ext in [".xwd", ".rle", ".jbig", ".svg", ".cr2", ".nef", ".yuy2", ".wfa", ".pdb", ".icon"]:
        assert exts.get(ext) == "ANYTOPNM", f"{ext} not registered"
