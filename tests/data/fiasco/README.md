# FIASCO test data

FIASCO (Fractal Image And Sequence Codec) by Ullrich Hafner, 1999.

## Files

- `test.wfa` — synthetic test image generated with `pnmtofiasco`
- `abydos.fco` — compressed image from [Sembiance](https://sembiance.com/fileFormatSamples/)
- `monarch.fco` — monarch butterfly, 768x512 RGB at 0.187 bpp
- `lena.fco` — Lena Södergren, 512x512 greyscale at 0.041 bpp
- `fiasco.magic` — libmagic detection rules for FIASCO files

## Additional samples

Multi-frame video sequences and more still images at various bitrates:
https://web.archive.org/web/20151028025607/https://attila.kinali.ch/fiasco/fiasco-examples.tar

Video sequences (bike, football, salesman, susie) require `-o` flag to decode
as `fiascotopnm` can't write multi-frame output to stdout.
