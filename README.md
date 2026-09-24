# SpatialToleranceCompression

**Two experiments in the same idea: space as a recursive language.**

> A fractal grammar engine where 4-bit masks program geometry — and a binary image codec that uses the same spatial logic for progressive, hierarchical image storage.

![GEO grammar engine — spiral.geo running at depth 6](media/geo_spiral.gif)

![Rate-distortion: .geoi vs JPEG vs PNG, quality-matched](media/rd_curves.png)

---

## What Is This?

This repo contains two separate but deeply related systems built on a single insight:
**a square can always be divided into four smaller squares, and that fact is a complete computational primitive.**

### 1. The GEO Grammar Engine *(Python — proof of concept)*

A declarative scripting language where you program **how fractal geometry evolves over time**.
Each node in a recursive quadtree carries a 4-bit mask. The mask controls which quadrants are
drawn and subdivided. Rules fire every tick to change the mask — switching loop families,
reacting to depth, time, neighbors, probability. The result is living geometry that rotates,
pulses, spreads, and self-organizes.

```geo
NAME   spiral
RULE   IF tick%8=0   THEN SWITCH Y_LOOP    AS beat-Y
RULE   IF tick%8=2   THEN SWITCH X_LOOP    AS beat-X
RULE   IF tick%8=4   THEN SWITCH Z_LOOP    AS beat-Z
RULE   IF tick%8=6   THEN SWITCH DIAG_LOOP AS beat-D
RULE   IF depth>=5   THEN GATE_ON          AS seal-deep
DEFAULT ADVANCE
```

### 2. The `.geoi` / `.geov` Compression Codec *(Go — the real product)*

A binary image and video compression format that uses the **same quadtree spatial subdivision**
as the grammar engine — but for image compression. Large uniform regions collapse to single
nodes. Only areas with actual detail get subdivided, and every node's position is its Morton
(Z-order) address.

**Measured, quality-matched (PSNR + SSIM, 9 test images — full data and method in [BENCHMARK.md](BENCHMARK.md)):**

| Content | `.geoi` size vs JPEG at the same quality |
|---|---|
| Photographs | 1.5–5.6× larger |
| UI screenshot | 1.5–2.1× larger |
| Line art, ~11% ink | 1.6–2.1× larger |
| Line art, ~1% ink | about equal by PSNR, 10–23% smaller by SSIM |

On flat graphic content, lossless PNG and WebP are smaller than every `.geoi` setting. The
ratio is not where this format wins. Its real strengths are **structural**: emptiness collapses
to almost nothing, and the Morton-ordered hierarchy gives every region an address.
*An earlier version of this README said `.geoi` beats JPEG. That was written before quality
metrics existed, and it did not hold up once they did.*

---

## The Core Idea

Every quadrant knows its address. The address *is* the data structure.

```
Z-order (Morton) curve — maps 2D position to 1D index:

  y=1:  [ 2  3  6  7 ]
  y=0:  [ 0  1  4  5 ]
          x=0 x=1 x=2 x=3

Bit-interleave (x=2, y=1):  x=10b, y=01b → Morton code 0110b = 6
```

This spatial locality means:
- **Progressive decode**: the tree yields a valid lower-resolution image at any depth *(the v2 bitstream order doesn't support this yet — see below)*
- **Adaptive detail**: each region gets exactly as many bits as it needs
- **No fixed 8×8 blocks**: regions are as large or small as the image demands (at low quality, variable-size blocks still show)

---

## Quick Start (Grammar Engine)

```bash
git clone https://github.com/sfdimarco/SpatialToleranceCompression.git
cd SpatialToleranceCompression
pip install -r requirements.txt

python BinaryQuadTreeTest.py                              # self-organising grid
python BinaryQuadTreeTest.py --geo examples/spiral.geo   # load a .geo script
python BinaryQuadTreeTest.py --list                       # see all built-in demos
```

## Quick Start (Go Codec)

```bash
cd go
go build ./cmd/geocoder

# Encode an image
./geocoder encode -i photo.png -o photo.geoi -q 245

# Decode (full resolution)
./geocoder decode -i photo.geoi -o photo_out.png

# Progressive decode at half resolution
./geocoder decode -i photo.geoi -o photo_thumb.png -d 7

# Full benchmark vs JPEG
./geocoder bench -i photo.png -q 245

# File info
./geocoder info -i photo.geoi
```

Run all tests:
```bash
cd go
go test ./...
```

---

## Architecture

### The Grammar Engine (Python)

Three stacked layers:

**Layer 1 — Mask Engine**: 16 possible 4-bit mask values, partitioned into five loop families.
Each family is a closed cycle. `ADVANCE` steps forward one position.

| Family | Cycle | Feel |
|--------|-------|------|
| **Y_LOOP** | `1000→0100→0010→0001` | Single quadrant orbits |
| **X_LOOP** | `1100→0101→0011→1010` | Adjacent pair cycles |
| **Z_LOOP** | `0111→1011→1101→1110` | Three-quadrant sweep |
| **DIAG_LOOP** | `1001↔0110` | Diagonal pair toggles |
| **GATE** | `0000` / `1111` | Fixed / frozen |

**Layer 2 — Grammar Programs**: Ordered `IF condition THEN action` rules. First match wins.
Conditions compose with `AND`, `OR`, `BUT`, `NOT`. Rules branch on state, time,
depth, neighbor context, probability, cell variables.

**Layer 3 — Grid / CA**: An N×M grid of quadtree roots, each with its own program. Cells read
neighbors, emit signals, vote on programs. Same-tick snapshot semantics prevent order artifacts.

### The Codec (Go)

```
PNG/JPEG input
     ↓
[BuildFromImage]  Load pixels, pad to power-of-2 square
     ↓
[buildRecursive]  Bottom-up quadtree construction
     ↓  Each region averages its 4 children's YCbCr colors
     ↓  canPrune(): if all 4 children are leaves AND colors within quality threshold → merge
     ↓  computeDelta(): child color = parent average + small delta
     ↓
[QuadNode tree]   Leaf nodes = uniform regions. Internal = subdivided.
     ↓
[EncodeHuffman]   Pass 1: collect delta distribution. Build per-channel Huffman tables.
     ↓             Pass 2: write header + root color + 4 Huffman tables + coded bitstream
     ↓
[.geoi file]      ~3-50x smaller than raw pixels (larger than JPEG at equal quality)
```

**Why YCbCr?** Separates luminance (Y) from chrominance (Cb, Cr). Human eyes are 4× less
sensitive to color than brightness — chroma channels get 2× the pruning threshold. Same trick
JPEG uses, applied to spatial quadtree deltas instead of DCT coefficients.

**Why delta encoding?** Child nodes store the difference from their parent's average, not
absolute colors. Deltas cluster near zero. Huffman codes frequent small deltas with 1-2 bits,
rare large deltas with longer codes. On typical images: v2 Huffman is 3× smaller than v1 raw.

**Progressive decode**: the goal is that `Decode(reader, maxDepth=4)` stops at depth 4 and returns a
valid 1/16-resolution image. **Not working yet for v2 streams:** nodes are written depth-first, so
stopping early desynchronises the reader (measured: 12.5 dB, vs 21.5 dB for the same tree cut
in memory). Fix: write the bitstream level by level (breadth-first), or store subtree byte
lengths so the reader can skip.

---

## Go Codec: File Structure

```
go/
├── go.mod                          # module github.com/sfdimarco/geo
├── cmd/geocoder/main.go            # CLI: encode / decode / info / bench
└── pkg/
    ├── morton/
    │   ├── morton.go               # Z-order curve encode/decode, child addressing
    │   └── morton_test.go          # 8 tests + benchmarks (~3ns/op)
    ├── quadtree/
    │   ├── node.go                 # QuadNode, Color/YCbCr, ColorDelta
    │   ├── builder.go              # BuildFromImage, adaptive pruning, RenderToPixels
    │   └── node_test.go            # uniform collapse, checkerboard, quadrant colors
    └── codec/
        ├── huffman.go              # HuffmanTable, BitWriter, BitReader, tree serialization
        ├── format.go               # .geoi header, v1 raw encoder, v2 Huffman encoder/decoder
        └── codec_test.go           # 10 tests: roundtrip v1+v2, progressive, bench
```

### File Format (v2 / Huffman)

```
┌──────────────────────────────────────────────────┐
│ HEADER (16 bytes)                                │
│   Magic[4] = 'GEOi'  Version=2  MaxDepth         │
│   ColorMode  Quality  Width(4)  Height(4)         │
├──────────────────────────────────────────────────┤
│ ROOT COLOR (4 bytes: Y Cb Cr A)                  │
├──────────────────────────────────────────────────┤
│ NODE COUNT (4 bytes)                             │
├──────────────────────────────────────────────────┤
│ HUFFMAN TABLES × 4                               │
│   [Y deltas]  [Cb deltas]  [Cr deltas]  [masks]  │
│   Each: count(2) + entries × (sym+len+code)(6)   │
├──────────────────────────────────────────────────┤
│ BITSTREAM LENGTH (4 bytes)                       │
├──────────────────────────────────────────────────┤
│ HUFFMAN-CODED BITSTREAM                          │
│   For each node in Z-order depth-first:          │
│   [DY bits] [DCb bits] [DCr bits] [mask bits]    │
└──────────────────────────────────────────────────┘
```

---

## The `.geo` Language

`.geo` is a declarative grammar language for writing quadtree animation programs.
Full reference: [GEO_LANGUAGE.md](GEO_LANGUAGE.md)

```geo
NAME   heat_spread
DEFINE hot  var.heat >= 10
DEFINE warm var.heat >= 5
RULE   IF hot  THEN SWITCH Z_LOOP AND EMIT spread   AS boiling
RULE   IF warm THEN SWITCH X_LOOP AND INC_VAR heat  AS heating
RULE   IF signal(spread) THEN INC_VAR heat          AS absorb
DEFAULT ADVANCE
```

**35+ example scripts** in [`examples/`](examples/) — terrain generation, cellular automata,
cosmos simulations, animation cycles, self-organization patterns, and more.

---

## Examples

```bash
# Grammar engine examples
python BinaryQuadTreeTest.py --geo examples/spiral.geo
python BinaryQuadTreeTest.py --geo examples/terrain/caves.geo --grid
python BinaryQuadTreeTest.py --geo examples/selforg/voronoi.geo --grid
python BinaryQuadTreeTest.py --geo examples/cosmos_sim.geo

# Codec examples
cd go
./geocoder bench -i my_photo.png -q 245        # full comparison table vs JPEG
./geocoder encode -i art.png -o art.geoi -q 255  # near-lossless (not bit-exact yet)
./geocoder decode -i art.geoi -o art_out.png -d 6  # half-res progressive
```

---

## Progressive Decode

One quadtree, four resolutions — the tree cut at each depth *(rendered from the in-memory tree; see the bitstream note above)*:

![Progressive decode — depth 5 through 9](media/progressive.png)

---

## Status

| Component | Status | Notes |
|-----------|--------|-------|
| GEO grammar engine | ✅ Complete | Python, single file, 35+ example scripts |
| GEO language spec | ✅ Complete | Full reference in GEO_LANGUAGE.md |
| GeoStudio IDE | ✅ Complete | Built-in IDE with live preview |
| Morton/Z-order codec | ✅ Complete | Go, ~3ns/op, fully tested |
| Quadtree builder (YCbCr) | ✅ Complete | Adaptive pruning, delta encoding |
| Codec v1 (raw) | ✅ Complete | Fixed 5 bytes/node, baseline |
| Codec v2 (Huffman) | ✅ Complete | Per-channel Huffman, 2-4× over v1 |
| CLI geocoder tool | ✅ Complete | encode/decode/info/bench commands |
| Decoder roundtrip | ✅ Fixed | Morton-code bug fixed; pixel-level regression test added |
| PSNR/SSIM quality metrics | ✅ Complete | `benchmarks/` — see BENCHMARK.md |
| Progressive decode | ⚠ Tree only | Bitstream needs breadth-first order |
| Bit-exact lossless (q=255) | ❌ Not yet | ~50–53 dB on photos, ~31 dB on pixel art |
| Streaming HTTP decoder | 🔜 Phase 3 | Range requests → progressive web |
| Video codec (.geov) | 🔜 Future | Inter-frame delta on quadtrees |

---

## License

[MIT](LICENSE)

---

## The STCP Hypothesis

> **Hypothesis: GEO compression and Barnes-Hut N-body gravity share the same computational structure.**

The **Spatial Tolerance Compression Principle (STCP)** is the observation that these two systems — a fractal image codec and a galaxy simulator — share an identical computational structure:

| GEO Image Codec | Barnes-Hut N-body |
|---|---|
| Subdivide until region is uniform | Subdivide until node is "far enough" |
| `pruning threshold` (quality) | `θ` parameter (0.0–1.0) |
| Leaf node = single color | Leaf node = center of mass |
| Stop recursing = compress | Stop recursing = approximate force |

Both systems ask the same question at every quadtree node: *"Is this region uniform enough to treat as a single thing?"* The answer — and the threshold — is structurally identical.

### QJL — Second-Order STCP

**QJL (Quantized Joint Leverage)** extends Barnes-Hut by quantizing the spherical coordinates (θ, φ) of accepted force interactions, enabling force vector **caching across frames**. Particles in similar positions relative to a cluster reuse previously computed force angles rather than recomputing them.

Validated result: **~45% cache hit rate** on 8,000-particle N-body simulations.

### Live Simulations

Interactive demos archived in [`research-/simulations`](https://github.com/sfdimarco/research-/tree/master/simulations):

- **[Universe1-Basic](https://github.com/sfdimarco/research-/blob/master/simulations/Universe1-Basic.html)** — Barnes-Hut N-body baseline (STCP without QJL)
- **[Universe2-Benchmark](https://github.com/sfdimarco/research-/blob/master/simulations/Universe2-Benchmark.html)** — QJL vs exact force benchmark with live timing HUD and KE drift tracking
- **[Universe3-Cache](https://github.com/sfdimarco/research-/blob/master/simulations/Universe3-Cache.html)** — Cache hit rate visualizer; validates the ~45% figure live

> Download and open any `.html` file — no server needed. Press **Q** to toggle QJL on/off, **R** to reset stats.

---

## Open Hypothesis — GEO as input structure for AI vision models

*Untested. Stated as a direction, not a result.*

Vision models read an image as a flat grid of patches, and every patch costs the same whether it
holds detail or empty space. A `.geoi` tree already knows which regions are empty and which carry
detail, and orders them by Morton address. The hypothesis: giving a model the quadtree hierarchy
(coarse to fine, detail only where it exists) could let it spend attention and tokens where the
image actually changes.

Testing it needs the progressive-bitstream fix above, a model that accepts variable-size regions,
and compute to compare task accuracy and token cost against standard patching. I don't currently
have that infrastructure. Collaboration welcome.
