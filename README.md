# pillow-netpbm

A Pillow plugin that bridges netpbm converter binaries, adding read support for
dozens of legacy/obscure image formats.

## Excluded formats

The following netpbm converters are not supported by this plugin:

| Converter | Format | Reason |
|-----------|--------|--------|
| `cameratopam` | Camera RAW (NEF, CR2) | Segfaults on NEF files, "File seek failed" on CR2 |
| `ddbugtopbm` | Diddle/DiddleBug sketch DB | Reads stdin only, writes multiple `.pbm` files to CWD |
| `pcdovtoppm` | Kodak Photo CD Overview | Shell script pipeline, not a single-binary converter |
| `bioradtopgm` | Bio-Rad Confocal | Magic at byte offset 54, beyond Pillow's 16-byte prefix limit; no known extension |
| `escp2topbm` | Epson ESC/P2 raster | No fixed header magic, no known file extension |
| `thinkjettopbm` | HP ThinkJet | No fixed header magic, no known file extension |
| `eyuvtoppm` | Encoder YUV | Headerless format, dimensions not in file |
| `yuvtoppm` | YUV 4:1:1 | Headerless format, dimensions not in file |
| `yuy2topam` | YUY2 Video Frame | Headerless format, dimensions not in file |
