"""geotok.py - how many ViT tokens does a GEO quadtree need, vs entropy (APT-style) and a fixed grid?

Every method cuts a 512x512 image into square tokens of size 16..512 (power of two).
A ViT sees each token resized to 16x16, so "what the model sees" = each token
area-downsampled to 16x16 and blown back up. Fidelity = PSNR of that vs the original.

  GEO     : exact mirror of canPrune in go/pkg/quadtree/builder.go - bottom-up from
            single pixels in YCbCr, rounded 4-way average, merge only if all 4 children
            are leaves and |child - avg| <= 255-q on Y, 2*(255-q) on Cb/Cr.
            Token = a merged node of size >= 16, or a 16px block. Swept over q.
  ENTROPY : top-down; split a block while its 256-bin grey-level entropy > threshold
            (the APT idea: low-entropy regions get big patches). Swept over threshold.
  GRID    : fixed patches of 16, 32, 64, 128, 256 px.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image

N, FLOOR = 512, 16
LEVELS = int(np.log2(N))            # 9: block sizes 1..512


def set_size(n):
    """Any square power-of-two size >= 32. load() calls this from the image."""
    global N, LEVELS
    assert n & (n - 1) == 0 and n >= 2 * FLOOR, n
    N, LEVELS = n, int(np.log2(n))


def load(p):
    im = Image.open(p).convert("RGB")
    assert im.size[0] == im.size[1], im.size
    set_size(im.size[0])
    return np.asarray(im, dtype=np.float64), np.asarray(im.convert("YCbCr"), dtype=np.int32)


# ── GEO: bottom-up canPrune mirror ───────────────────────────────────────────
def geo_leaf_maps(ycc, q):
    """leaf[k][i,j] True if the size-2^k node at block (i,j) is a (merged) leaf."""
    thr = float(255 - q)
    col = ycc.copy()
    leaf = [np.ones(ycc.shape[:2], bool)]
    for k in range(1, LEVELS + 1):
        c = [col[0::2, 0::2], col[0::2, 1::2], col[1::2, 0::2], col[1::2, 1::2]]
        l = [leaf[-1][0::2, 0::2], leaf[-1][0::2, 1::2], leaf[-1][1::2, 0::2], leaf[-1][1::2, 1::2]]
        avg = (c[0] + c[1] + c[2] + c[3] + 2) // 4
        ok = l[0] & l[1] & l[2] & l[3]
        for ci in c:
            d = np.abs(ci - avg)
            ok &= (d[..., 0] <= thr) & (d[..., 1] <= 2 * thr) & (d[..., 2] <= 2 * thr)
        leaf.append(ok)
        col = avg
    return leaf


def tokens_from_leaf(leaf):
    """Top-down cut: a node is a token if it is a leaf or is at the 16px floor."""
    out = []
    kf = int(np.log2(FLOOR))

    def rec(k, i, j):
        if leaf[k][i, j] or k == kf:
            out.append((i << k, j << k, 1 << k))
            return
        for di in (0, 1):
            for dj in (0, 1):
                rec(k - 1, 2 * i + di, 2 * j + dj)
    rec(LEVELS, 0, 0)
    return out


# ── SHRINK: GEO's "survives the shrink" rule, read from the same tree ─────────
def tokens_shrink(leaf):
    """A node of size s is one token when the GEO tree is fully merged 4 levels
    below it: every s/16 block inside it is a leaf (or inside a bigger leaf).
    Then shrinking it to 16x16 keeps everything GEO's tolerance keeps.
    Superset of the uniform rule: a uniform leaf is always shrink-safe."""
    kf = int(np.log2(FLOOR))                      # 4
    covered = [None] * (LEVELS + 1)
    covered[LEVELS] = leaf[LEVELS].copy()
    for m in range(LEVELS - 1, -1, -1):           # covered = leaf, or inside a bigger leaf
        up = np.repeat(np.repeat(covered[m + 1], 2, 0), 2, 1)
        covered[m] = leaf[m] | up
    safe = {}
    for k in range(kf + 1, LEVELS + 1):           # all 16x16 descendants at level k-4 covered
        c = covered[k - kf]
        n = c.shape[0] // FLOOR
        safe[k] = c.reshape(n, FLOOR, n, FLOOR).all(axis=(1, 3))
    out = []

    def rec(k, i, j):
        if k == kf or safe[k][i, j]:
            out.append((i << k, j << k, 1 << k)); return
        for di in (0, 1):
            for dj in (0, 1):
                rec(k - 1, 2 * i + di, 2 * j + dj)
    rec(LEVELS, 0, 0)
    return out


# ── ENTROPY (APT-style) ──────────────────────────────────────────────────────
def entropy(block):
    h = np.bincount(block.ravel(), minlength=256).astype(np.float64)
    p = h[h > 0] / h.sum()
    return float(-(p * np.log2(p)).sum())


def tokens_entropy(grey, t):
    out = []

    def rec(y, x, s):
        if s == FLOOR or entropy(grey[y:y + s, x:x + s]) <= t:
            out.append((y, x, s)); return
        h = s // 2
        for dy in (0, h):
            for dx in (0, h):
                rec(y + dy, x + dx, h)
    rec(0, 0, N)
    return out


def tokens_grid(s):
    return [(y, x, s) for y in range(0, N, s) for x in range(0, N, s)]


# ── What the ViT sees, and PSNR ──────────────────────────────────────────────
def seen(rgb, toks):
    out = np.empty_like(rgb)
    for y, x, s in toks:
        b = rgb[y:y + s, x:x + s]
        f = s // FLOOR
        small = b.reshape(FLOOR, f, FLOOR, f, 3).mean(axis=(1, 3))   # area resize to 16x16
        out[y:y + s, x:x + s] = np.repeat(np.repeat(small, f, 0), f, 1)
    return out


def psnr(a, b):
    mse = float(((a - b) ** 2).mean())
    return 99.0 if mse < 1e-10 else min(99.0, 10 * np.log10(255.0 ** 2 / mse))


def run(path):
    rgb, ycc = load(path)
    grey = ycc[..., 0].astype(np.int64)
    res = {"geo": [], "shrink": [], "entropy": [], "grid": []}
    for q in (255, 254, 252, 250, 245, 240, 235, 225, 210, 190, 160):
        leaf = geo_leaf_maps(ycc, q)
        t = tokens_from_leaf(leaf)
        res["geo"].append({"q": q, "tokens": len(t), "psnr": psnr(rgb, seen(rgb, t))})
        t = tokens_shrink(leaf)
        res["shrink"].append({"q": q, "tokens": len(t), "psnr": psnr(rgb, seen(rgb, t))})
    for th in (0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0):
        t = tokens_entropy(grey, th)
        res["entropy"].append({"t": th, "tokens": len(t), "psnr": psnr(rgb, seen(rgb, t))})
    for s in (x for x in (16, 32, 64, 128, 256, 512) if x < N):
        t = tokens_grid(s)
        res["grid"].append({"s": s, "tokens": len(t), "psnr": psnr(rgb, seen(rgb, t))})
    return res


if __name__ == "__main__":
    imgs = sorted(Path(sys.argv[1]).glob("*.png"))
    allres = {}
    for p in imgs:
        allres[p.stem] = run(p)
        g = allres[p.stem]["geo"]
        print(f"{p.stem:<20} geo q=255 {g[0]['tokens']:>5} tok {g[0]['psnr']:5.1f} dB | "
              f"q=245 {g[4]['tokens']:>5} tok {g[4]['psnr']:5.1f} dB", flush=True)
    Path(sys.argv[2] if len(sys.argv) > 2 else "results.json").write_text(json.dumps(allres, indent=1))
