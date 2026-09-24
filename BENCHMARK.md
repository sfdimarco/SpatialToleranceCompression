# .geoi Benchmark — quality-matched

Measured 2026-09-24 with the Go `geocoder` in this repo (after the decoder fix below).
Everything here can be regenerated with the scripts in `benchmarks/`.

![Rate-distortion curves](media/rd_curves.png)

## Headline

- **Against JPEG at equal quality, `.geoi` is larger** on photos (1.5–5.6×), UI screenshots (1.5–2.1×)
  and line art at ~11% ink (1.6–2.1×).
- **Very sparse line art (~1% ink) is the one place it holds its own:** about equal to JPEG by
  PSNR, 10–23% smaller by SSIM.
- **On flat graphic content, lossless PNG and WebP beat every `.geoi` setting**, while also being exact.
- This matches the earlier cel measurements (quadtree wins below ~5% ink, PNG wins above):
  the win is **emptiness (structure)**, not **similarity (perceptual tolerance)**.

## Method

- 9 images, all 512×512 RGB (a power of two, so no padding favours either side):
  4 centre crops from the Kodak photo set (kodim03, 05, 15, 23) and 5 generated graphics —
  flat vector illustration, 8× pixel art, UI screenshot, line art at ~11% and ~1% ink
  (`benchmarks/make_test_images.py`).
- `.geoi`: v2 Huffman, quality 50–255, encoded and decoded with `geocoder`, then compared pixel by pixel.
- JPEG: Pillow, quality 10–100, default 4:2:0 chroma.
- Metrics: PSNR (dB) and SSIM on RGB, scikit-image.
- "Same quality" = JPEG size interpolated (log-size vs metric) at the `.geoi` point's PSNR or SSIM.
  Ratio above 1 = `.geoi` is larger. "—" = outside JPEG's measured range.

## Lossy, matched quality (selected points)

| Image | .geoi q | .geoi size | PSNR | SSIM | size ÷ JPEG (same PSNR) | size ÷ JPEG (same SSIM) |
|---|---|---|---|---|---|---|
| photo_kodim03 | 250 | 130,883 B | 39.7 dB | 0.9474 | 2.65 | 3.99 |
| photo_kodim03 | 245 | 84,066 B | 35.5 dB | 0.9046 | 3.74 | 4.78 |
| photo_kodim03 | 235 | 43,512 B | 31.3 dB | 0.8396 | 4.08 | 4.21 |
| photo_kodim05 | 250 | 411,656 B | 42.7 dB | 0.9866 | 1.49 | 2.69 |
| photo_kodim05 | 245 | 324,624 B | 36.3 dB | 0.9524 | 2.74 | 4.29 |
| photo_kodim05 | 235 | 215,351 B | 30.1 dB | 0.8626 | 3.76 | 6.42 |
| photo_kodim15 | 250 | 254,060 B | 40.6 dB | 0.9587 | 2.17 | 3.04 |
| photo_kodim15 | 245 | 143,575 B | 34.2 dB | 0.8694 | 3.51 | 5.25 |
| photo_kodim23 | 250 | 154,838 B | 37.8 dB | 0.9270 | 3.51 | 5.95 |
| photo_kodim23 | 245 | 85,674 B | 32.5 dB | 0.8456 | 5.6 | 7.28 |
| ui_screenshot | 250 | 48,700 B | 56.2 dB | 1.0000 | — | — |
| ui_screenshot | 245 | 46,494 B | 44.5 dB | 0.9926 | 1.9 | 1.91 |
| ui_screenshot | 235 | 32,525 B | 34.9 dB | 0.9241 | 2.14 | 3.02 |
| lineart_cel | 250 | 90,462 B | 44.1 dB | 0.9992 | 1.6 | 1.11 |
| lineart_cel | 245 | 86,983 B | 43.5 dB | 0.9989 | 1.57 | 1.15 |
| lineart_cel | 235 | 81,026 B | 41.3 dB | 0.9986 | 1.65 | 1.13 |
| lineart_sparse | 250 | 13,157 B | 55.9 dB | 0.9999 | 0.96 | 0.79 |
| lineart_sparse | 245 | 12,774 B | 55.1 dB | 0.9999 | 0.96 | 0.77 |
| lineart_sparse | 235 | 12,309 B | 53.0 dB | 0.9998 | 1.0 | 0.78 |
| illustration_flat | 250 | 22,277 B | 49.5 dB | 0.9994 | — | — |
| illustration_flat | 245 | 20,986 B | 48.5 dB | 0.9991 | — | — |
| illustration_flat | 235 | 15,670 B | 34.3 dB | 0.9855 | 2.25 | 1.2 |
| pixelart | 250 | 5,600 B | 30.8 dB | 0.9957 | 1.0 | — |
| pixelart | 245 | 5,600 B | 30.8 dB | 0.9957 | 1.0 | — |
| pixelart | 235 | 5,600 B | 30.8 dB | 0.9957 | 1.0 | — |

Full sweep: `benchmarks/results.json`.

## Lossless and near-lossless

| Image | PNG | WebP lossless | .geoi q=255 | .geoi q=255 PSNR |
|---|---|---|---|---|
| photo_kodim03 | 349,667 B | 252,360 B | 360,852 B | 52.9 dB |
| photo_kodim05 | 556,472 B | 384,014 B | 525,725 B | 53.2 dB |
| photo_kodim15 | 445,697 B | 316,020 B | 434,414 B | 53.2 dB |
| photo_kodim23 | 392,251 B | 296,796 B | 408,837 B | 52.8 dB |
| ui_screenshot | 14,892 B | 2,178 B | 49,000 B | 56.3 dB |
| lineart_cel | 84,909 B | 35,922 B | 120,289 B | 44.6 dB |
| lineart_sparse | 14,780 B | 4,210 B | 17,672 B | 56.9 dB |
| illustration_flat | 13,279 B | 8,216 B | 34,668 B | 50.7 dB |
| pixelart | 3,516 B | 932 B | 5,600 B | 30.8 dB |

`q=255` is **not bit-exact**. Merging and YCbCr rounding shift colours (pixel art: off-by-one
palette values and blended edge pixels).

## Bug found and fixed during this benchmark

The first run scored 1–8 dB on every image: **the decoder painted only the top-left quarter.**
Both v1 and v2 decoders assigned each child's Morton code *after* decoding that child's subtree,
so every descendant was built from code 0. Node counts still matched, which is why the existing
tests passed. Fix: assign codes top-down after decoding (`assignMortonCodes` in
`go/pkg/codec/format.go`). New test `TestRoundtripPixels` compares every pixel; it fails on the
old code and passes on the fix. **Any earlier size/quality numbers from this decoder are void.**

## Known issue: progressive decode

The tree supports progressive rendering (cut at depth 5: 21.5 dB, depth 7: 26.2 dB on kodim23).
The v2 **bitstream** does not: nodes are written depth-first, so stopping at a depth leaves the
skipped children's bits in the stream and the reader desynchronises (12.5 dB). Needs a
breadth-first layout or per-subtree lengths.

## Reproduce

```
cd go && go build ./cmd/geocoder && go test ./...
cd ../benchmarks
pip install pillow numpy scikit-image
python make_test_images.py
python rd_bench.py ../go/geocoder
```
