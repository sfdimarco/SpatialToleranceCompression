# BinaryQuadTreeTest.py  — 4-bit Quad-Mask Spatial Grammar Lab
#
# Each 4-bit mask is a "geometric opcode" describing which quadrants of a
# square are active.  Active quadrants recursively subdivide (quadtree).
# Masks advance each tick according to loop-family rules → geometry evolves.
#
# Bit layout  (matches original notes):
#   bit 3 (8) = TL   bit 2 (4) = TR   bit 1 (2) = BR   bit 0 (1) = BL
#
# Loop families:
#   Gates      : 0000, 1111          — hold steady
#   Y-loop     : 1000→0100→0010→0001 — single quadrant rotates
#   X-loop     : 1100→0101→0011→1010 — adjacent pair cycles
#   Z-loop     : 0111→1011→1101→1110 — three-quadrant sweep
#   Diag-loop  : 1001↔0110           — diagonal pair toggles

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.animation import FuncAnimation

# ── Bit constants ─────────────────────────────────────────────────────────────
TL, TR, BR, BL = 8, 4, 2, 1

# ── Loop-family definitions ───────────────────────────────────────────────────
GATES     = {0b0000, 0b1111}
Y_LOOP    = [0b1000, 0b0100, 0b0010, 0b0001]
X_LOOP    = [0b1100, 0b0101, 0b0011, 0b1010]
Z_LOOP    = [0b0111, 0b1011, 0b1101, 0b1110]
DIAG_LOOP = [0b1001, 0b0110]

def _cycle_map(seq: List[int]) -> dict:
    return {seq[i]: seq[(i + 1) % len(seq)] for i in range(len(seq))}

NEXT_MAP: dict[int, int] = {}
NEXT_MAP.update(_cycle_map(Y_LOOP))
NEXT_MAP.update(_cycle_map(X_LOOP))
NEXT_MAP.update(_cycle_map(Z_LOOP))
NEXT_MAP.update(_cycle_map(DIAG_LOOP))

def next_mask(m: int) -> int:
    if m in GATES:
        return m
    return NEXT_MAP.get(m, m)

def mask_quadrants(m: int) -> Tuple[bool, bool, bool, bool]:
    """Return (TL, TR, BR, BL) active flags for a mask."""
    return (bool(m & TL), bool(m & TR), bool(m & BR), bool(m & BL))

# ── Color palette — one hue per loop family ───────────────────────────────────
_FAMILY_RGB: dict[int, tuple] = {}
for _m in Y_LOOP:    _FAMILY_RGB[_m] = (0.95, 0.32, 0.32)  # red
for _m in X_LOOP:    _FAMILY_RGB[_m] = (0.28, 0.90, 0.42)  # green
for _m in Z_LOOP:    _FAMILY_RGB[_m] = (0.32, 0.55, 1.00)  # blue
for _m in DIAG_LOOP: _FAMILY_RGB[_m] = (1.00, 0.85, 0.18)  # gold
_FAMILY_RGB[0b1111]  = (0.82, 0.82, 0.82)
_FAMILY_RGB[0b0000]  = (0.06, 0.06, 0.06)

def _cell_color(mask: int, depth: int, max_depth: int) -> tuple:
    t = depth / max_depth if max_depth > 0 else 0.0
    brightness = 1.0 - 0.58 * t
    r, g, b = _FAMILY_RGB.get(mask, (0.55, 0.55, 0.55))
    return (r * brightness, g * brightness, b * brightness)

# ── Quadtree node ─────────────────────────────────────────────────────────────
@dataclass
class Node:
    x:        float
    y:        float
    size:     float
    depth:    int
    mask:     int
    children: Optional[List["Node"]] = field(default=None)
    vars:     dict = field(default_factory=dict)   # per-cell named variables

    def ensure_children(self) -> None:
        if self.children is not None:
            return
        h = self.size / 2.0
        self.children = [
            Node(self.x,     self.y + h, h, self.depth + 1, self.mask),  # TL
            Node(self.x + h, self.y + h, h, self.depth + 1, self.mask),  # TR
            Node(self.x + h, self.y,     h, self.depth + 1, self.mask),  # BR
            Node(self.x,     self.y,     h, self.depth + 1, self.mask),  # BL
        ]

# ── Core tree operations ──────────────────────────────────────────────────────
def expand_active(root: Node, max_depth: int) -> List[Tuple[float, float, float, int, int]]:
    """Recursively collect active-quadrant rectangles. Returns (x,y,size,depth,mask)."""
    out: List[Tuple[float, float, float, int, int]] = []

    def _rec(n: Node) -> None:
        tl_on, tr_on, br_on, bl_on = mask_quadrants(n.mask)
        h = n.size / 2.0
        if tl_on: out.append((n.x,     n.y + h, h, n.depth, n.mask))
        if tr_on: out.append((n.x + h, n.y + h, h, n.depth, n.mask))
        if br_on: out.append((n.x + h, n.y,     h, n.depth, n.mask))
        if bl_on: out.append((n.x,     n.y,     h, n.depth, n.mask))
        if n.depth >= max_depth:
            return
        n.ensure_children()
        if tl_on: _rec(n.children[0])
        if tr_on: _rec(n.children[1])
        if br_on: _rec(n.children[2])
        if bl_on: _rec(n.children[3])

    _rec(root)
    return out


def tick_masks(root: Node) -> None:
    """Advance every allocated node one step (no grammar rules)."""
    def _rec(n: Node) -> None:
        n.mask = next_mask(n.mask)
        if n.children:
            for c in n.children:
                _rec(c)
    _rec(root)

# ── Drawing ───────────────────────────────────────────────────────────────────
def draw_frame(ax, root: Node, max_depth: int, colored: bool = True) -> None:
    ax.clear()
    ax.set_aspect("equal")
    ax.set_xlim(root.x, root.x + root.size)
    ax.set_ylim(root.y, root.y + root.size)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_facecolor("#111111")
    ax.add_patch(Rectangle((root.x, root.y), root.size, root.size,
                            fill=False, linewidth=0.6, edgecolor="#333333"))
    
    rects = []
    colors = []
    for (x, y, s, d, m) in expand_active(root, max_depth):
        rects.append(Rectangle((x, y), s, s))
        if colored:
            colors.append(_cell_color(m, d, max_depth))
        else:
            shade = 0.15 + 0.75 * (1.0 - d / max_depth if max_depth > 0 else 0.0)
            colors.append((shade, shade, shade))
    
    if rects:
        ax.add_collection(PatchCollection(rects, facecolors=colors, linewidth=0))

# ── Basic demos ───────────────────────────────────────────────────────────────
def run_static_demo(root_mask: int = 0b1111, max_depth: int = 6) -> None:
    root = Node(0.0, 0.0, 1.0, 0, root_mask)
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor("#0d0d0d")
    draw_frame(ax, root, max_depth)
    ax.set_title(f"static  mask={root_mask:04b}", fontsize=11, color="white")
    plt.tight_layout(); plt.show()


def run_animated_demo(root_mask: int = 0b1000, max_depth: int = 7,
                      ticks_per_second: float = 2.0) -> None:
    root = Node(0.0, 0.0, 1.0, 0, root_mask)
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor("#0d0d0d")
    tick = [0]

    def update(_):
        tick_masks(root); tick[0] += 1
        draw_frame(ax, root, max_depth)
        ax.set_title(f"mask={root.mask:04b}  t={tick[0]}", fontsize=11, color="white")

    fig._anim = FuncAnimation(fig, update,
                               interval=int(1000 / max(ticks_per_second, 0.001)),
                               cache_frame_data=False)
    plt.tight_layout(); plt.show()


def run_lab_demo(max_depth: int = 6, ticks_per_second: float = 3.0) -> None:
    """2x3 grid showing all six loop families simultaneously."""
    configs = [
        (0b1000, "Y-loop  1000"), (0b1100, "X-loop  1100"),
        (0b0111, "Z-loop  0111"), (0b1001, "Diag    1001"),
        (0b1111, "Gate ON 1111"), (0b0000, "Gate OFF 0000"),
    ]
    roots = [Node(0.0, 0.0, 1.0, 0, m) for m, _ in configs]
    fig, axes = plt.subplots(2, 3, figsize=(13, 9))
    fig.patch.set_facecolor("#0d0d0d")
    fig.suptitle("Binary Quad Grammar — Loop Family Lab", fontsize=14, color="white")
    axes_flat = axes.flatten()
    tick = [0]

    def update(_):
        for root in roots: tick_masks(root)
        tick[0] += 1
        for i, (root, (_, label)) in enumerate(zip(roots, configs)):
            ax = axes_flat[i]
            draw_frame(ax, root, max_depth, colored=True)
            ax.set_title(f"{label}  [{root.mask:04b}]  t={tick[0]}",
                         fontsize=8, color="white")
        fig.canvas.draw_idle()

    fig._anim = FuncAnimation(fig, update,
                               interval=int(1000 / max(ticks_per_second, 0.001)),
                               cache_frame_data=False)
    plt.tight_layout(rect=[0, 0, 1, 0.95]); plt.show()


# ══════════════════════════════════════════════════════════════════════════════
# GRAMMAR LAYER
# ══════════════════════════════════════════════════════════════════════════════

# ── Family lookup ─────────────────────────────────────────────────────────────
_FAMILY_SETS = {
    "Y_LOOP":    set(Y_LOOP),
    "X_LOOP":    set(X_LOOP),
    "Z_LOOP":    set(Z_LOOP),
    "DIAG_LOOP": set(DIAG_LOOP),
    "GATE":      GATES,
}

def family_of(mask: int) -> str:
    for name, members in _FAMILY_SETS.items():
        if mask in members:
            return name
    return "UNKNOWN"

# ── Conditions ────────────────────────────────────────────────────────────────
# Sentence structure:
#   Rule( IF_family("Y_LOOP").AND(IF_tick_gte(8)),  SwitchFamily("X_LOOP") )
#   Rule( IF_depth_gte(3).BUT(IF_family("GATE")),   Advance()              )
#
# Combinators:
#   .AND(c)  — both true
#   .OR(c)   — either true
#   .BUT(c)  — self true AND other NOT  ("except when")
#   & | ~    — operator shorthand

class Cond:
    """Base condition — always True."""
    def _test(self, node: "Node", tick: int, ctx: dict) -> bool: return True
    def evaluate(self, node: "Node", tick: int, ctx: dict) -> bool: return self._test(node, tick, ctx)
    def AND(self, other: "Cond") -> "Cond":  return _AndCond(self, other)
    def OR(self,  other: "Cond") -> "Cond":  return _OrCond(self, other)
    def BUT(self, other: "Cond") -> "Cond":  return _AndCond(self, _NotCond(other))
    def __and__(self, other): return self.AND(other)
    def __or__(self,  other): return self.OR(other)
    def __invert__(self):     return _NotCond(self)

class _AndCond(Cond):
    def __init__(self, a, b): self._a, self._b = a, b
    def _test(self, n, t, c): return self._a.evaluate(n, t, c) and self._b.evaluate(n, t, c)
    def __repr__(self): return f"({self._a} AND {self._b})"

class _OrCond(Cond):
    def __init__(self, a, b): self._a, self._b = a, b
    def _test(self, n, t, c): return self._a.evaluate(n, t, c) or self._b.evaluate(n, t, c)
    def __repr__(self): return f"({self._a} OR {self._b})"

class _NotCond(Cond):
    def __init__(self, c): self._c = c
    def _test(self, n, t, c): return not self._c.evaluate(n, t, c)
    def __repr__(self): return f"NOT({self._c})"

# ── Node / tick conditions ────────────────────────────────────────────────────

def IF_family(name: str) -> Cond:
    """True when node's mask is in the named loop family."""
    class _C(Cond):
        def _test(self, n, *args): return family_of(n.mask) == name
        def __repr__(self): return f"family=={name}"
    return _C()

def IF_mask(value: int) -> Cond:
    """True when node.mask == value exactly."""
    class _C(Cond):
        def _test(self, n, *args): return n.mask == value
        def __repr__(self): return f"mask=={value:04b}"
    return _C()

def IF_tick_gte(n: int) -> Cond:
    """True when tick >= n."""
    class _C(Cond):
        def _test(self, _, tick, *args): return tick >= n
        def __repr__(self): return f"tick>={n}"
    return _C()

def IF_tick_mod(period: int, remainder: int = 0) -> Cond:
    """True when tick % period == remainder."""
    class _C(Cond):
        def _test(self, _, tick, *args): return tick % period == remainder
        def __repr__(self): return f"tick%{period}=={remainder}"
    return _C()

def IF_tick_eq(n: int) -> Cond:
    """True when tick == n (exact equality)."""
    class _C(Cond):
        def _test(self, _, tick, *args): return tick == n
        def __repr__(self): return f"tick=={n}"
    return _C()

def IF_depth_gte(n: int) -> Cond:
    """True when node.depth >= n."""
    class _C(Cond):
        def _test(self, node, *args): return node.depth >= n
        def __repr__(self): return f"depth>={n}"
    return _C()

def IF_active_count(n: int) -> Cond:
    """True when exactly n quadrants are active."""
    class _C(Cond):
        def _test(self, node, *args): return bin(node.mask).count("1") == n
        def __repr__(self): return f"active=={n}"
    return _C()

ALWAYS = Cond()

# ── Neighbor conditions (populated via ctx by Grid.step) ────────────────

def IF_neighbor_family(direction: str, name: str) -> Cond:
    """True when the cardinal neighbor in direction (N/S/E/W) is in the named family."""
    key = f"nb_{direction}"
    class _C(Cond):
        def _test(self, n, t, ctx):
            nb = ctx.get(key)
            return nb is not None and family_of(nb) == name
        def __repr__(self): return f"nb_{direction}=={name}"
    return _C()

def IF_neighbor_mask(direction: str, value: int) -> Cond:
    """True when the cardinal neighbor in direction has exactly this mask."""
    key = f"nb_{direction}"
    class _C(Cond):
        def _test(self, n, t, ctx): return ctx.get(key) == value
        def __repr__(self): return f"nb_{direction}.mask=={value:04b}"
    return _C()

def IF_neighbor_count(name: str, count: int) -> Cond:
    """True when exactly `count` of the 4 cardinal neighbors are in the named family."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            neighbor_count = sum(1 for d in ("N","S","E","W")
                    if ctx.get(f"nb_{d}") is not None
                    and family_of(ctx[f"nb_{d}"]) == name)
            return neighbor_count == count
        def __repr__(self): return f"nb_count({name})=={count}"
    return _C()

def IF_neighbor_count_lte(name: str, count: int) -> Cond:
    """True when count of 4 cardinal neighbors in the named family <= count."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            neighbor_count = sum(1 for d in ("N","S","E","W")
                    if ctx.get(f"nb_{d}") is not None
                    and family_of(ctx[f"nb_{d}"]) == name)
            return neighbor_count <= count
        def __repr__(self): return f"nb_count_lte({name})<={count}"
    return _C()

def IF_neighbor_count8(name: str, count: int) -> Cond:
    """True when exactly `count` of the 8 neighbors (including diagonals) are in the named family."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            neighbor_count = sum(1 for d in ("N","S","E","W","NE","NW","SE","SW")
                    if ctx.get(f"nb_{d}") is not None
                    and family_of(ctx[f"nb_{d}"]) == name)
            return neighbor_count == count
        def __repr__(self): return f"nb_count8({name})=={count}"
    return _C()

def IF_neighbor_count8_gte(name: str, count: int) -> Cond:
    """True when count of 8 neighbors in the named family >= count."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            neighbor_count = sum(1 for d in ("N","S","E","W","NE","NW","SE","SW")
                    if ctx.get(f"nb_{d}") is not None
                    and family_of(ctx[f"nb_{d}"]) == name)
            return neighbor_count >= count
        def __repr__(self): return f"nb_count8_gte({name})>={count}"
    return _C()

def IF_neighbor_count8_lte(name: str, count: int) -> Cond:
    """True when count of 8 neighbors in the named family <= count."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            neighbor_count = sum(1 for d in ("N","S","E","W","NE","NW","SE","SW")
                    if ctx.get(f"nb_{d}") is not None
                    and family_of(ctx[f"nb_{d}"]) == name)
            return neighbor_count <= count
        def __repr__(self): return f"nb_count8_lte({name})<={count}"
    return _C()

def IF_neighbor_mask_count(mask_value: int, count: int) -> Cond:
    """True when exactly `count` of the 4 cardinal neighbors have the specific mask value."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            neighbor_count = sum(1 for d in ("N","S","E","W")
                    if ctx.get(f"nb_{d}") is not None
                    and ctx[f"nb_{d}"] == mask_value)
            return neighbor_count == count
        def __repr__(self): return f"nb_mask_count({mask_value:04b})=={count}"
    return _C()

def IF_neighbor_mask_count8(mask_value: int, count: int) -> Cond:
    """True when exactly `count` of the 8 neighbors (including diagonals) have the specific mask value."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            neighbor_count = sum(1 for d in ("N","S","E","W","NE","NW","SE","SW")
                    if ctx.get(f"nb_{d}") is not None
                    and ctx[f"nb_{d}"] == mask_value)
            return neighbor_count == count
        def __repr__(self): return f"nb_mask_count8({mask_value:04b})=={count}"
    return _C()

def IF_any_neighbor(name: str) -> Cond:
    """True when at least one cardinal neighbor is in the named family."""
    class _C(Cond):
        def _test(self, n, t, ctx):
            return any(ctx.get(f"nb_{d}") is not None
                       and family_of(ctx[f"nb_{d}"]) == name
                       for d in ("N","S","E","W"))
        def __repr__(self): return f"any_nb=={name}"
    return _C()

# ── Program-identity conditions (populated via ctx by Grid.step) ────────

def IF_own_prog(name: str) -> Cond:
    """True when this cell's own program name matches."""
    class _C(Cond):
        def _test(self, n, t, ctx): return ctx.get("own_prog") == name
        def __repr__(self): return f"own_prog=={name}"
    return _C()

def IF_neighbor_prog(direction: str, name: str) -> Cond:
    """True when the cardinal neighbor in direction (N/S/E/W) runs the named program."""
    key = f"nb_prog_{direction}"
    class _C(Cond):
        def _test(self, n, t, ctx): return ctx.get(key) == name
        def __repr__(self): return f"nb_prog_{direction}=={name}"
    return _C()

def IF_any_neighbor_prog(name: str) -> Cond:
    """True when at least one cardinal neighbor runs the named program."""
    class _C(Cond):
        def _test(self, n, t, ctx):
            return any(ctx.get(f"nb_prog_{d}") == name
                       for d in ("N","S","E","W"))
        def __repr__(self): return f"any_nb_prog=={name}"
    return _C()

def IF_neighbor_prog_count(name: str, count: int) -> Cond:
    """True when exactly `count` cardinal neighbors run the named program."""
    class _C(Cond):
        def _test(self, n, t, ctx):
            return sum(1 for d in ("N","S","E","W")
                       if ctx.get(f"nb_prog_{d}") == name) == count
        def __repr__(self): return f"nb_prog_count({name})=={count}"
    return _C()

def IF_neighbor_prog_gte(name: str, threshold: int) -> Cond:
    """True when at least `threshold` cardinal neighbors run the named program."""
    class _C(Cond):
        def _test(self, node, t, ctx):
            return sum(1 for d in ("N","S","E","W")
                       if ctx.get(f"nb_prog_{d}") == name) >= threshold
        def __repr__(self): return f"nb_prog_gte({name},{n})"
    return _C()

# ── Extended conditions (Phase 1) ────────────────────────────────────────────

def IF_tick_lt(n: int) -> Cond:
    """True when tick < n."""
    class _C(Cond):
        def _test(self, _, tick, *args): return tick < n
        def __repr__(self): return f"tick<{n}"
    return _C()

def IF_depth_eq(n: int) -> Cond:
    """True when node.depth == n exactly."""
    class _C(Cond):
        def _test(self, node, *args): return node.depth == n
        def __repr__(self): return f"depth=={n}"
    return _C()

def IF_depth_lt(n: int) -> Cond:
    """True when node.depth < n."""
    class _C(Cond):
        def _test(self, node, *args): return node.depth < n
        def __repr__(self): return f"depth<{n}"
    return _C()

def IF_active_gte(n: int) -> Cond:
    """True when active quadrant count >= n."""
    class _C(Cond):
        def _test(self, node, *args): return bin(node.mask).count("1") >= n
        def __repr__(self): return f"active>={n}"
    return _C()

def IF_active_lte(n: int) -> Cond:
    """True when active quadrant count <= n."""
    class _C(Cond):
        def _test(self, node, *args): return bin(node.mask).count("1") <= n
        def __repr__(self): return f"active<={n}"
    return _C()

def IF_mask_in(values: List[int]) -> Cond:
    """True when node.mask is in the given set of values."""
    s = set(values)
    class _C(Cond):
        def _test(self, node, *args): return node.mask in s
        def __repr__(self): return f"mask_in({','.join(f'{v:04b}' for v in values)})"
    return _C()

def IF_random_lt(prob: float) -> Cond:
    """True with probability `prob` (0.0-1.0) each evaluation."""
    import random as _rand
    class _C(Cond):
        def _test(self, *args): return _rand.random() < prob
        def __repr__(self): return f"random<{prob}"
    return _C()

def IF_tick_between(lo: int, hi: int) -> Cond:
    """True when lo <= tick <= hi (inclusive range)."""
    class _C(Cond):
        def _test(self, _, tick, *args): return lo <= tick <= hi
        def __repr__(self): return f"tick_in({lo}..{hi})"
    return _C()

def IF_tick_mod_between(period: int, lo: int, hi: int) -> Cond:
    """True when lo <= (tick % period) <= hi (inclusive range)."""
    class _C(Cond):
        def _test(self, _, tick, *args): return lo <= (tick % period) <= hi
        def __repr__(self): return f"tick%{period}_in({lo}..{hi})"
    return _C()

def IF_depth_between(lo: int, hi: int) -> Cond:
    """True when lo <= node.depth <= hi (inclusive range)."""
    class _C(Cond):
        def _test(self, node, *args): return lo <= node.depth <= hi
        def __repr__(self): return f"depth_in({lo}..{hi})"
    return _C()

def IF_depth_mod(period: int, remainder: int = 0) -> Cond:
    """True when depth % period == remainder."""
    class _C(Cond):
        def _test(self, node, *args): return node.depth % period == remainder
        def __repr__(self): return f"depth%{period}=={remainder}"
    return _C()

def IF_var_gte(name: str, value: int) -> Cond:
    """True when cell variable `name` >= value (from ctx)."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            return ctx["vars"].get(name, 0) >= value
        def __repr__(self): return f"var_{name}>={value}"
    return _C()

def IF_var_eq(name: str, value: int) -> Cond:
    """True when cell variable `name` == value (from ctx)."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            return ctx["vars"].get(name, 0) == value
        def __repr__(self): return f"var_{name}=={value}"
    return _C()

def IF_var_lt(name: str, value: int) -> Cond:
    """True when cell variable `name` < value (from ctx)."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            return ctx["vars"].get(name, 0) < value
        def __repr__(self): return f"var_{name}<{value}"
    return _C()

def IF_var_lte(name: str, value: int) -> Cond:
    """True when cell variable `name` <= value (from ctx)."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            return ctx["vars"].get(name, 0) <= value
        def __repr__(self): return f"var_{name}<={value}"
    return _C()

def IF_var_between(name: str, lo: int, hi: int) -> Cond:
    """True when lo <= cell variable `name` <= hi (inclusive range)."""
    class _C(Cond):
        def _test(self, node, tick, ctx):
            return lo <= ctx["vars"].get(name, 0) <= hi
        def __repr__(self): return f"var_{name}_in({lo}..{hi})"
    return _C()

# ── Neighbor variable conditions ──────────────────────────────────────────────

def IF_nb_var_gte(direction: str, name: str, value: int) -> Cond:
    """True when neighbor's variable `name` >= value."""
    key = f"nb_vars_{direction}"
    class _C(Cond):
        def _test(self, node, tick, ctx):
            return ctx.get(key, {}).get(name, 0) >= value
        def __repr__(self): return f"nb_var_{direction}_{name}>={value}"
    return _C()

def IF_nb_var_lt(direction: str, name: str, value: int) -> Cond:
    """True when neighbor's variable `name` < value."""
    key = f"nb_vars_{direction}"
    class _C(Cond):
        def _test(self, node, tick, ctx):
            return ctx.get(key, {}).get(name, 0) < value
        def __repr__(self): return f"nb_var_{direction}_{name}<{value}"
    return _C()

def IF_nb_var_eq(direction: str, name: str, value: int) -> Cond:
    """True when neighbor's variable `name` == value."""
    key = f"nb_vars_{direction}"
    class _C(Cond):
        def _test(self, node, tick, ctx):
            return ctx.get(key, {}).get(name, 0) == value
        def __repr__(self): return f"nb_var_{direction}_{name}=={value}"
    return _C()

def IF_nb_var_lte(direction: str, name: str, value: int) -> Cond:
    """True when neighbor's variable `name` <= value."""
    key = f"nb_vars_{direction}"
    class _C(Cond):
        def _test(self, node, tick, ctx):
            return ctx.get(key, {}).get(name, 0) <= value
        def __repr__(self): return f"nb_var_{direction}_{name}<={value}"
    return _C()


def IF_random_gte(prob: float) -> Cond:
    """True with probability (1.0 - prob) each evaluation."""
    import random as _rand
    class _C(Cond):
        def _test(self, *args): return _rand.random() >= prob
        def __repr__(self): return f"random>={prob}"
    return _C()

def IF_signal(name: str) -> Cond:
    """True when the named signal was received this tick."""
    class _C(Cond):
        def _test(self, n, t, ctx):
            signals = ctx.get("signals", set())  # Read-only input signals
            return name in signals
        def __repr__(self): return f"signal={name}"
    return _C()

def IF_neighbor_count_gte(family_name: str, n: int) -> Cond:
    """True when at least n cardinal neighbors are in the named family."""
    class _C(Cond):
        def _test(self, n, t, ctx):
            return sum(1 for d in ("N","S","E","W")
                       if ctx.get(f"nb_{d}") is not None
                       and family_of(ctx[f"nb_{d}"]) == family_name) >= n
        def __repr__(self): return f"nb_count_gte({family_name},{n})"
    return _C()

# ── Actions ───────────────────────────────────────────────────────────────────

class Action:
    def apply(self, node: "Node", ctx: dict) -> None: pass
    def label(self) -> str: return "action"

class Advance(Action):
    """Step mask forward in its current loop family (default)."""
    def apply(self, node, ctx): node.mask = next_mask(node.mask)
    def label(self): return "ADVANCE"

class Hold(Action):
    """Keep current mask unchanged."""
    def apply(self, node, ctx): pass
    def label(self): return "HOLD"

class GateOn(Action):
    def apply(self, node, ctx): node.mask = 0b1111
    def label(self): return "GATE_ON"

class GateOff(Action):
    def apply(self, node, ctx): node.mask = 0b0000
    def label(self): return "GATE_OFF"

class SwitchFamily(Action):
    """Jump to the first member of a named loop family."""
    _FIRSTS = {"Y_LOOP": Y_LOOP[0], "X_LOOP": X_LOOP[0],
               "Z_LOOP": Z_LOOP[0], "DIAG_LOOP": DIAG_LOOP[0]}
    def __init__(self, family_name: str):
        self._name  = family_name
        self._first = self._FIRSTS[family_name]
    def apply(self, node, ctx): node.mask = self._first
    def label(self): return f"SWITCH({self._name})"

class SetMask(Action):
    """Force a specific 4-bit mask value."""
    def __init__(self, mask: int): self._mask = mask
    def apply(self, node, ctx): node.mask = self._mask
    def label(self): return f"SET({self._mask:04b})"

class SwitchProgram(Action):
    """Advance mask AND signal an unconditional program switch for this cell.
    Grid.step() applies the switch after the full cell step completes."""
    def __init__(self, prog_name: str): self._prog_name = prog_name
    def apply(self, node, ctx):
        node.mask = next_mask(node.mask)
        ctx["_pending_switch"][0] = self._prog_name
    def label(self): return f"PROG({self._prog_name})"

class SwitchToPluralityNeighbor(Action):
    """Advance mask AND adopt the most common neighboring program when it
    appears at least `threshold` times among cardinal neighbors that differ
    from the cell's own program.  If no threshold is met, just advance."""
    def __init__(self, threshold: int = 2): self._threshold = threshold
    def apply(self, node, ctx):
        node.mask = next_mask(node.mask)
        own = ctx.get("own_prog")
        counts: dict = {}
        for d in ("N", "S", "E", "W"):
            p = ctx.get(f"nb_prog_{d}")
            if p is not None and p != own:
                counts[p] = counts.get(p, 0) + 1
        if not counts:
            return
        best, best_n = max(counts.items(), key=lambda kv: kv[1])
        if best_n >= self._threshold:
            ctx["_pending_switch"][0] = best
    def label(self): return f"PLURALITY({self._threshold})"

class CallProgram(Action):
    """Invoke a registered sub-program on this node for the current tick."""
    def __init__(self, name: str): self._name = name
    def apply(self, node, ctx):
        sub = PROGRAM_REGISTRY.get(self._name)
        if sub:
            # Pass context down, ensuring tick is available
            sub.step_node(node, ctx.get("tick", 0), ctx)
    def label(self): return f"CALL({self._name})"

# ── Extended actions (Phase 2/3) ─────────────────────────────────────────────

class RotateCW(Action):
    """Rotate mask bits clockwise: TL->TR->BR->BL->TL."""
    def apply(self, node, ctx):
        m = node.mask
        tl = (m >> 3) & 1; tr = (m >> 2) & 1
        br = (m >> 1) & 1; bl = m & 1
        node.mask = (bl << 3) | (tl << 2) | (tr << 1) | br
    def label(self): return "ROTATE_CW"

class RotateCCW(Action):
    """Rotate mask bits counter-clockwise: TL->BL->BR->TR->TL."""
    def apply(self, node, ctx):
        m = node.mask
        tl = (m >> 3) & 1; tr = (m >> 2) & 1
        br = (m >> 1) & 1; bl = m & 1
        node.mask = (tr << 3) | (br << 2) | (bl << 1) | tl
    def label(self): return "ROTATE_CCW"

class FlipH(Action):
    """Mirror mask horizontally: TL<->TR, BL<->BR."""
    def apply(self, node, ctx):
        m = node.mask
        tl = (m >> 3) & 1; tr = (m >> 2) & 1
        br = (m >> 1) & 1; bl = m & 1
        node.mask = (tr << 3) | (tl << 2) | (bl << 1) | br
    def label(self): return "FLIP_H"

class FlipV(Action):
    """Mirror mask vertically: TL<->BL, TR<->BR."""
    def apply(self, node, ctx):
        m = node.mask
        tl = (m >> 3) & 1; tr = (m >> 2) & 1
        br = (m >> 1) & 1; bl = m & 1
        node.mask = (bl << 3) | (br << 2) | (tr << 1) | tl
    def label(self): return "FLIP_V"

class SetVar(Action):
    """Set a named cell variable to a value (stored in shared ctx['vars'])."""
    def __init__(self, name: str, value: int):
        self._name = name; self._value = value
    def apply(self, node, ctx):
        ctx["vars"][self._name] = self._value
    def label(self): return f"SET_VAR({self._name},{self._value})"

class IncrVar(Action):
    """Increment a named cell variable by delta."""
    def __init__(self, name: str, delta: int = 1):
        self._name = name; self._delta = delta
    def apply(self, node, ctx):
        ctx["vars"][self._name] = ctx["vars"].get(self._name, 0) + self._delta
    def label(self): return f"INCR_VAR({self._name},{self._delta})"

class Emit(Action):
    """Broadcast a named signal to cardinal neighbors (picked up next tick)."""
    def __init__(self, signal_name: str): self._signal = signal_name
    def apply(self, node, ctx):
        ctx["pending_signals"].add(self._signal)
    def label(self): return f"EMIT({self._signal})"

class AccumVar(Action):
    """Read a neighbor's variable and accumulate it into a local variable.

    ACCUM_VAR target direction source [weight]
    e.g. ACCUM_VAR sum S activation 3  →  my.sum += south.activation * 3
    """
    def __init__(self, target: str, direction: str, source: str, weight: int = 1):
        self._target = target
        self._dir = direction
        self._source = source
        self._weight = weight
    def apply(self, node, ctx):
        nb_vars = ctx.get(f"nb_vars_{self._dir}", {})
        val = nb_vars.get(self._source, 0)
        ctx["vars"][self._target] = ctx["vars"].get(self._target, 0) + val * self._weight
    def label(self): return f"ACCUM({self._target},{self._dir},{self._source},w={self._weight})"

class ClampVar(Action):
    """Clamp a cell variable to [lo, hi] range. Acts as ReLU (lo=0) or saturation.

    CLAMP_VAR name lo hi
    e.g. CLAMP_VAR act 0 100
    """
    def __init__(self, name: str, lo: int, hi: int):
        self._name = name
        self._lo = lo
        self._hi = hi
    def apply(self, node, ctx):
        v = ctx["vars"].get(self._name, 0)
        ctx["vars"][self._name] = max(self._lo, min(self._hi, v))
    def label(self): return f"CLAMP({self._name},{self._lo},{self._hi})"


class CompositeAction(Action):
    """Execute multiple actions in sequence."""
    def __init__(self, actions: List[Action]):
        self._actions = actions
    def apply(self, node, ctx):
        for a in self._actions:
            a.apply(node, ctx)
    def label(self): return "+".join(a.label() for a in self._actions)

class AdvanceN(Action):
    """Step mask forward N times in its loop family."""
    def __init__(self, n: int = 2): self._n = n
    def apply(self, node, ctx):
        for _ in range(self._n):
            node.mask = next_mask(node.mask)
    def label(self): return f"ADVANCE({self._n})"

# Named program registry — populate with register(); CallProgram looks up from here.
PROGRAM_REGISTRY: dict = {}

def register(name: str, prog: "Program") -> "Program":
    """Register a program by name so CallProgram can invoke it."""
    PROGRAM_REGISTRY[name] = prog
    if not prog.name:
        prog.name = name
    return prog

# ── Rules and Programs ────────────────────────────────────────────────────────

@dataclass
class Rule:
    """One IF → THEN statement in the geo grammar."""
    condition: Cond
    action:    Action
    name:      str = ""

    def matches(self, node: "Node", tick: int, ctx: dict) -> bool:
        return self.condition.evaluate(node, tick, ctx)

    def fire(self, node: "Node", ctx: dict) -> None:
        self.action.apply(node, ctx)


class Program:
    """
    An ordered list of Rules that drives mask evolution each tick.

    First matching rule fires; if none match, `default` action runs (Advance).

    Usage (replaces tick_masks):
        prog.step_tree(root, tick)
        prog.step_tree(root, tick, ctx)
    """
    def __init__(self, rules: List[Rule], default: Action = None, name: str = ""):
        self.rules   = rules
        self.default = default if default is not None else Advance()
        self.name    = name

    def step_node(self, node: "Node", tick: int, ctx: dict = None) -> str:
        """Apply first matching rule to one node. Returns rule name."""
        if ctx is None: ctx = {}
        ctx.setdefault("tick", tick)
        # Ensure mutable output containers exist for standalone runs
        ctx.setdefault("vars", {})
        ctx.setdefault("pending_signals", set())
        ctx.setdefault("_pending_switch", [None])
        
        for rule in self.rules:
            if rule.matches(node, tick, ctx):
                rule.fire(node, ctx)
                return rule.name or rule.action.label()
        self.default.apply(node, ctx)
        return "."

    def step_tree(self, root: "Node", tick: int, ctx: dict = None) -> str:
        """Apply rules to every allocated node. Returns rule name fired at root."""
        if ctx is None: ctx = {}
        
        def _get_child(n: Optional["Node"], idx: int) -> Optional["Node"]:
            return n.children[idx] if (n and n.children) else None

        root_fired = ["."]
        
        def _rec(n: "Node", current_ctx: dict, is_root: bool = False) -> None:
            # 1. Update neighbor mask values in context based on neighbor nodes
            #    (This overrides the root-level masks passed from Grid for deep nodes)
            if not is_root:
                for d in ("N", "S", "E", "W"):
                    nb_node = current_ctx.get(f"nb_node_{d}")
                    if nb_node:
                        current_ctx[f"nb_{d}"] = nb_node.mask
                    else:
                        current_ctx[f"nb_{d}"] = None
                    # Clear neighbor program info for deep nodes
                    current_ctx[f"nb_prog_{d}"] = None

            # 2. Step this node
            fired = self.step_node(n, tick, current_ctx)
            if is_root:
                root_fired[0] = fired
            
            # 3. Recurse with updated neighbor contexts
            if n.children:
                nb_N = current_ctx.get("nb_node_N")
                nb_S = current_ctx.get("nb_node_S")
                nb_E = current_ctx.get("nb_node_E")
                nb_W = current_ctx.get("nb_node_W")

                def make_ctx(nn, ns, ne, nw):
                    c = current_ctx.copy()
                    c["nb_node_N"], c["nb_node_S"] = nn, ns
                    c["nb_node_E"], c["nb_node_W"] = ne, nw
                    return c

                # TL(0): N=nb_N->BL(3), S=self->BL(3), E=self->TR(1), W=nb_W->TR(1)
                _rec(n.children[0], make_ctx(_get_child(nb_N, 3), n.children[3], 
                                             n.children[1], _get_child(nb_W, 1)))
                # TR(1): N=nb_N->BR(2), S=self->BR(2), E=nb_E->TL(0), W=self->TL(0)
                _rec(n.children[1], make_ctx(_get_child(nb_N, 2), n.children[2], 
                                             _get_child(nb_E, 0), n.children[0]))
                # BR(2): N=self->TR(1), S=nb_S->TR(1), E=nb_E->BL(3), W=self->BL(3)
                _rec(n.children[2], make_ctx(n.children[1], _get_child(nb_S, 1), 
                                             _get_child(nb_E, 3), n.children[3]))
                # BL(3): N=self->TL(0), S=nb_S->TL(0), E=self->BR(2), W=nb_W->BR(2)
                _rec(n.children[3], make_ctx(n.children[0], _get_child(nb_S, 0), 
                                             n.children[2], _get_child(nb_W, 2)))

        _rec(root, ctx, True)
        return root_fired[0]

# ── Built-in example programs ─────────────────────────────────────────────────

PROG_FREE = Program(rules=[], name="free advance")

PROG_SEQUENCE = Program([
    Rule(IF_tick_mod(32,  0), SwitchFamily("Y_LOOP"),    "->Y"),
    Rule(IF_tick_mod(32,  8), SwitchFamily("X_LOOP"),    "->X"),
    Rule(IF_tick_mod(32, 16), SwitchFamily("Z_LOOP"),    "->Z"),
    Rule(IF_tick_mod(32, 24), SwitchFamily("DIAG_LOOP"), "->D"),
], name="Y > X > Z > Diag")

PROG_DEPTH_BRANCH = Program([
    Rule(IF_depth_gte(3).AND(IF_family("Y_LOOP")), SwitchFamily("X_LOOP"), "deep>X"),
    Rule(IF_depth_gte(3).AND(IF_family("X_LOOP")), SwitchFamily("Z_LOOP"), "deep>Z"),
], name="depth branch Y/X/Z")

PROG_PULSE = Program([
    Rule(IF_tick_mod(8, 0).BUT(IF_family("GATE")), GateOn(),               "ON"),
    Rule(IF_family("GATE").AND(IF_tick_mod(8, 2)), SwitchFamily("Y_LOOP"), "off"),
], name="pulse gate")

# ── Grammar demo ──────────────────────────────────────────────────────────────

def run_grammar_demo(ticks_per_second: float = 2.5, max_depth: int = 6) -> None:
    """2x2 grid comparing four programs from the same Y-loop start."""
    programs   = [PROG_FREE, PROG_SEQUENCE, PROG_DEPTH_BRANCH, PROG_PULSE]
    roots      = [Node(0.0, 0.0, 1.0, 0, 0b1000) for _ in programs]
    tick       = [0]
    last_fired = [""] * 4

    fig, axes = plt.subplots(2, 2, figsize=(11, 11))
    fig.patch.set_facecolor("#0d0d0d")
    fig.suptitle("Quad Grammar — Rule Programs", fontsize=13, color="white")
    axes_flat = axes.flatten()

    def update(_):
        for i, (root, prog) in enumerate(zip(roots, programs)):
            last_fired[i] = prog.step_tree(root, tick[0])
        tick[0] += 1
        for i, (root, prog) in enumerate(zip(roots, programs)):
            ax = axes_flat[i]
            draw_frame(ax, root, max_depth, colored=True)
            ax.set_title(f"{prog.name}\n[{root.mask:04b}]  {family_of(root.mask)}"
                         f"  t={tick[0]}\nrule: {last_fired[i]}",
                         fontsize=8, color="white")
        fig.canvas.draw_idle()

    fig._anim = FuncAnimation(fig, update,
                               interval=int(1000 / max(ticks_per_second, 0.001)),
                               cache_frame_data=False)
    plt.tight_layout(rect=[0, 0, 1, 0.95]); plt.show()


# ══════════════════════════════════════════════════════════════════════════════
# GRID  — neighbor-aware cellular automaton layer
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Grid:
    """
    N×M grid of quadtree roots.  Each cell carries its own Program, enabling
    multi-zone layouts where different spatial regions run different rule sets.

    Before stepping each cell, its four cardinal neighbor root-masks are loaded
    into _step_ctx so IF_neighbor_* / IF_any_neighbor conditions work.

    All cells are snapshotted before any step fires — same-tick semantics.
    """
    rows:      int
    cols:      int
    cell_size: float
    cells:     List[List[Node]]
    programs:  List[List[Program]]   # one Program per cell

    @classmethod
    def make(cls, rows: int, cols: int, program: "Program",
             init_mask_fn=None, cell_size: float = 1.0) -> "Grid":
        """Uniform grid — every cell runs the same Program."""
        if init_mask_fn is None:
            init_mask_fn = lambda *_: Y_LOOP[0]
        cells    = [[Node(c * cell_size, r * cell_size, cell_size, 0,
                          init_mask_fn(r, c))
                     for c in range(cols)] for r in range(rows)]
        programs = [[program for _ in range(cols)] for _ in range(rows)]
        return cls(rows, cols, cell_size, cells, programs)

    @classmethod
    def make_multi(cls, rows: int, cols: int,
                   program_fn,        # (r, c) -> Program
                   init_mask_fn=None, # (r, c) -> int mask
                   cell_size: float = 1.0) -> "Grid":
        """Multi-program grid — program_fn(r, c) assigns a Program to each cell."""
        if init_mask_fn is None:
            init_mask_fn = lambda *_: Y_LOOP[0]
        cells    = [[Node(c * cell_size, r * cell_size, cell_size, 0,
                          init_mask_fn(r, c))
                     for c in range(cols)] for r in range(rows)]
        programs = [[program_fn(r, c) for c in range(cols)] for r in range(rows)]
        return cls(rows, cols, cell_size, cells, programs)

    def set_program(self, r: int, c: int, prog: "Program") -> None:
        """Hot-swap the program on a single cell at runtime."""
        self.programs[r][c] = prog

    def step(self, tick: int) -> None:
        # Snapshot masks AND program names so every cell sees same-tick state.
        snap_masks = [[self.cells[r][c].mask        for c in range(self.cols)]
                      for r in range(self.rows)]
        snap_progs = [[self.programs[r][c].name     for c in range(self.cols)]
                      for r in range(self.rows)]
        # Snapshot cell variables for same-tick reads.
        snap_vars  = [[dict(self.cells[r][c].vars)  for c in range(self.cols)]
                      for r in range(self.rows)]
        # Snapshot signals from previous tick (emitted signals become neighbor reads).
        snap_sigs  = [[set(self.cells[r][c].vars.get("_signals", set()))
                       for c in range(self.cols)] for r in range(self.rows)]
        switches: dict = {}   # (r, c) -> new Program object
        emitted_signals: dict = {}  # (r, c) -> set of signal names
        for r in range(self.rows):
            for c in range(self.cols):
                # Collect signals received from cardinal neighbors.
                received = set()
                if r + 1 < self.rows: received |= snap_sigs[r + 1][c]
                if r > 0:             received |= snap_sigs[r - 1][c]
                if c + 1 < self.cols: received |= snap_sigs[r][c + 1]
                if c > 0:             received |= snap_sigs[r][c - 1]
                
                # Cardinal neighbors
                nb_N = snap_masks[r + 1][c] if r + 1 < self.rows else None
                nb_S = snap_masks[r - 1][c] if r > 0             else None
                nb_E = snap_masks[r][c + 1] if c + 1 < self.cols else None
                nb_W = snap_masks[r][c - 1] if c > 0             else None
                
                # Diagonal neighbors (for Conway's Game of Life and similar)
                nb_NE = snap_masks[r - 1][c + 1] if r > 0 and c + 1 < self.cols     else None
                nb_NW = snap_masks[r - 1][c - 1] if r > 0 and c > 0                 else None
                nb_SE = snap_masks[r + 1][c + 1] if r + 1 < self.rows and c + 1 < self.cols else None
                nb_SW = snap_masks[r + 1][c - 1] if r + 1 < self.rows and c > 0     else None
                
                nb = {
                    "nb_N":      nb_N,
                    "nb_S":      nb_S,
                    "nb_E":      nb_E,
                    "nb_W":      nb_W,
                    "nb_NE":     nb_NE,
                    "nb_NW":     nb_NW,
                    "nb_SE":     nb_SE,
                    "nb_SW":     nb_SW,
                    "nb_prog_N": snap_progs[r + 1][c] if r + 1 < self.rows else None,
                    "nb_prog_S": snap_progs[r - 1][c] if r > 0             else None,
                    "nb_prog_E": snap_progs[r][c + 1] if c + 1 < self.cols else None,
                    "nb_prog_W": snap_progs[r][c - 1] if c > 0             else None,
                    "own_prog":  snap_progs[r][c],
                    "nb_node_N": self.cells[r + 1][c] if r + 1 < self.rows else None,
                    "nb_node_S": self.cells[r - 1][c] if r > 0             else None,
                    "nb_node_E": self.cells[r][c + 1] if c + 1 < self.cols else None,
                    "nb_node_W": self.cells[r][c - 1] if c > 0             else None,
                    "signals":   received,
                    # Neighbor variable snapshots (for neural / accumulation reads)
                    "nb_vars_N": snap_vars[r + 1][c] if r + 1 < self.rows else {},
                    "nb_vars_S": snap_vars[r - 1][c] if r > 0             else {},
                    "nb_vars_E": snap_vars[r][c + 1] if c + 1 < self.cols else {},
                    "nb_vars_W": snap_vars[r][c - 1] if c > 0             else {},
                    # Mutable containers shared down the tree:
                    "vars":            {k: v for k, v in snap_vars[r][c].items()
                                        if not k.startswith("_")},
                    "pending_signals": set(),
                    "_pending_switch": [None],
                }
                
                self.programs[r][c].step_tree(self.cells[r][c], tick, nb)

                # Collect variable writes back to node.
                for k, v in nb["vars"].items():
                    self.cells[r][c].vars[k] = v

                # Collect emitted signals.
                if nb["pending_signals"]:
                    emitted_signals[(r, c)] = set(nb["pending_signals"])
                if nb["_pending_switch"][0] is not None:
                    new_prog = PROGRAM_REGISTRY.get(nb["_pending_switch"][0])
                    if new_prog is not None:
                        switches[(r, c)] = new_prog
        # Apply all program switches together (post-step, snapshot semantics).
        for (r, c), prog in switches.items():
            self.programs[r][c] = prog
        # Store emitted signals on cells for next tick's snapshot.
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c].vars["_signals"] = emitted_signals.get((r, c), set())


def draw_grid_frame(ax, grid: Grid, max_depth: int,
                    zone_palette: dict = None) -> None:
    """
    Render the grid.  zone_palette maps program-name -> (r,g,b) tint colour;
    when provided, each cell gets a faint zone background before its geometry.
    """
    ax.clear()
    ax.set_xlim(0, grid.cols * grid.cell_size)
    ax.set_ylim(0, grid.rows * grid.cell_size)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_facecolor("#111111")
    
    rects = []
    colors = []
    cs = grid.cell_size
    for r in range(grid.rows):
        for c in range(grid.cols):
            root = grid.cells[r][c]
            # Optional zone background tint
            if zone_palette is not None:
                zc = zone_palette.get(grid.programs[r][c].name, (0.15, 0.15, 0.15))
                ax.add_patch(Rectangle((root.x, root.y), cs, cs,
                                       facecolor=(*zc, 0.18), linewidth=0))
            
            for (x, y, s, d, m) in expand_active(root, max_depth):
                rects.append(Rectangle((x, y), s, s))
                colors.append(_cell_color(m, d, max_depth))

    if rects:
        ax.add_collection(PatchCollection(rects, facecolors=colors, linewidth=0))

    for i in range(grid.rows + 1):
        ax.axhline(i * cs, color="#2a2a2a", linewidth=0.5)
    for j in range(grid.cols + 1):
        ax.axvline(j * cs, color="#2a2a2a", linewidth=0.5)


def run_grid_demo(rows: int = 8, cols: int = 8,
                  ticks_per_second: float = 3.0, max_depth: int = 4) -> None:
    """
    Neighbor-aware grid demo.

    Seed: Y-loop at centre, Z-loop everywhere else.
    Rules:
      Z-loop cell that touches Y-loop  →  becomes X-loop   (green ring)
      Z-loop cell that touches X-loop  →  becomes Diag     (gold ring)
      Diag cell that touches new Z-loop→  becomes Y-loop   (wave rebounds)

    Color key:  Red=Y  Green=X  Blue=Z  Gold=Diag
    """
    cx, cy = rows // 2, cols // 2

    def seed(r, c):
        return 0b1000 if (r == cx and c == cy) else 0b0111  # Y centre, Z elsewhere

    nb_wave = Program([
        Rule(IF_any_neighbor("Y_LOOP").AND(IF_family("Z_LOOP")),
             SwitchFamily("X_LOOP"),    "Z>X"),
        Rule(IF_any_neighbor("X_LOOP").AND(IF_family("Z_LOOP")),
             SwitchFamily("DIAG_LOOP"), "Z>D"),
        Rule(IF_any_neighbor("Z_LOOP").AND(IF_family("DIAG_LOOP")),
             SwitchFamily("Y_LOOP"),    "D>Y"),
    ], name="neighbor wave")

    grid = Grid.make(rows, cols, nb_wave, seed)
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("#0d0d0d")
    tick = [0]

    def update(_):
        grid.step(tick[0])
        tick[0] += 1
        draw_grid_frame(ax, grid, max_depth)
        ax.set_title(f"neighbor wave  {rows}x{cols} grid  t={tick[0]}",
                     fontsize=10, color="white")

    fig._anim = FuncAnimation(fig, update,
                               interval=int(1000 / max(ticks_per_second, 0.001)),
                               cache_frame_data=False)
    plt.tight_layout(); plt.show()


# ── Multi-program zones ───────────────────────────────────────────────────────

# Zone colour palette — background tint per program name
ZONE_PALETTE = {
    "zone-0": (0.75, 0.10, 0.10),   # red
    "zone-1": (0.10, 0.70, 0.20),   # green
    "zone-2": (0.10, 0.30, 0.90),   # blue
    "zone-3": (0.85, 0.65, 0.00),   # gold
}

def _make_zone_seq(phase: int) -> Program:
    """
    Phase-shifted sequence program.  All four zones cycle through
    Y→X→Z→Diag on a 32-tick clock, but each zone starts at a different
    family so they are always one phase apart.

      phase 0 → Y at t=0,  X at t=8,  Z at t=16, D at t=24
      phase 1 → X at t=0,  Z at t=8,  D at t=16, Y at t=24
      phase 2 → Z at t=0,  D at t=8,  Y at t=16, X at t=24
      phase 3 → D at t=0,  Y at t=8,  X at t=16, Z at t=24
    """
    fams = ["Y_LOOP", "X_LOOP", "Z_LOOP", "DIAG_LOOP"]
    f    = [fams[(phase + i) % 4] for i in range(4)]
    return Program([
        Rule(IF_tick_mod(32,  0), SwitchFamily(f[0]), "->0"),
        Rule(IF_tick_mod(32,  8), SwitchFamily(f[1]), "->1"),
        Rule(IF_tick_mod(32, 16), SwitchFamily(f[2]), "->2"),
        Rule(IF_tick_mod(32, 24), SwitchFamily(f[3]), "->3"),
    ], name=f"zone-{phase}")

# Starting masks for each phase (public — index matches zone index)
ZONE_START_MASKS = [Y_LOOP[0], X_LOOP[0], Z_LOOP[0], DIAG_LOOP[0]]
# Pre-built programs (also registered so CallProgram can invoke them)
ZONE_PROGS = [register(f"zone-{i}", _make_zone_seq(i)) for i in range(4)]


def make_zones(rows: int, cols: int, zone_map_fn, cell_size: float = 1.0) -> Grid:
    """
    Build a multi-program grid from a spatial zone map.

    zone_map_fn(r, c) -> int  maps each cell to a zone index (0-3).

    Common patterns:
      4 quadrants : lambda r,c: (r >= rows//2)*2 + (c >= cols//2)
      checkerboard: lambda r,c: (r + c) % 2
      stripes     : lambda r,c: (r * 4 // rows)
      rings       : lambda r,c: min(3, max(abs(r-rows//2), abs(c-cols//2)) * 4 // (min(rows,cols)//2))
    """
    def prog_fn(r, c): return ZONE_PROGS[zone_map_fn(r, c) % 4]
    def mask_fn(r, c): return ZONE_START_MASKS[zone_map_fn(r, c) % 4]
    return Grid.make_multi(rows, cols, prog_fn, mask_fn, cell_size)


def make_voting_zone(phase: int, vote_threshold: int = 2) -> "Program":
    """
    Build a self-organising zone program.

    Like zone-{phase}, it cycles through all four loop families on a 32-tick
    clock (phase-shifted).  On every tick that doesn't match the sequence,
    it also runs SwitchToPluralityNeighbor: if vote_threshold or more cardinal
    neighbors run a *different* program, the cell adopts that program next tick.

    Programs are registered as "vote-{phase}" so Grid.step() can look them up.
    """
    fams = ["Y_LOOP", "X_LOOP", "Z_LOOP", "DIAG_LOOP"]
    f    = [fams[(phase + i) % 4] for i in range(4)]
    name = f"vote-{phase}"
    prog = Program([
        Rule(IF_tick_mod(32,  0), SwitchFamily(f[0]),                       "->0"),
        Rule(IF_tick_mod(32,  8), SwitchFamily(f[1]),                       "->1"),
        Rule(IF_tick_mod(32, 16), SwitchFamily(f[2]),                       "->2"),
        Rule(IF_tick_mod(32, 24), SwitchFamily(f[3]),                       "->3"),
        Rule(ALWAYS,              SwitchToPluralityNeighbor(vote_threshold), "vote"),
    ], name=name)
    return register(name, prog)


def run_self_org_demo(rows: int = 10, cols: int = 10,
                      vote_threshold: int = 2,
                      ticks_per_second: float = 2.5,
                      max_depth: int = 4) -> None:
    """
    Self-organising zone boundary demo.

    Every cell starts on a randomly chosen voting program (vote-0 .. vote-3).
    On each tick, cells whose `vote_threshold` or more cardinal neighbors run a
    different program adopt the plurality neighbor program on the next tick.

    The random noise rapidly consolidates into coherent blobs; boundaries
    between zones keep negotiating as the geometry cycles underneath.

    vote_threshold=1  →  very aggressive merging (monoculture in ~5 ticks)
    vote_threshold=2  →  balanced (blobs stabilise in ~15-30 ticks)
    vote_threshold=3  →  conservative (minority pockets persist longer)
    """
    import random
    random.seed(42)

    vote_progs  = [make_voting_zone(i, vote_threshold) for i in range(4)]
    vote_palette = {
        "vote-0": (0.75, 0.10, 0.10),
        "vote-1": (0.10, 0.70, 0.20),
        "vote-2": (0.10, 0.30, 0.90),
        "vote-3": (0.85, 0.65, 0.00),
    }

    def prog_fn(*_):
        return vote_progs[random.randint(0, 3)]

    def mask_fn(*_):
        return ZONE_START_MASKS[random.randint(0, 3)]

    grid = Grid.make_multi(rows, cols, prog_fn, mask_fn)

    fig, ax = plt.subplots(figsize=(9, 9))
    fig.patch.set_facecolor("#0d0d0d")
    tick = [0]

    def update(_):
        grid.step(tick[0])
        tick[0] += 1
        draw_grid_frame(ax, grid, max_depth, zone_palette=vote_palette)
        counts: dict = {}
        for r in range(grid.rows):
            for c in range(grid.cols):
                n = grid.programs[r][c].name
                counts[n] = counts.get(n, 0) + 1
        summary = "  ".join(f"{k[-1]}:{v:3d}" for k, v in sorted(counts.items()))
        ax.set_title(
            f"self-org  {rows}x{cols}  threshold={vote_threshold}  t={tick[0]}\n{summary}",
            fontsize=9, color="white")

    fig._anim = FuncAnimation(fig, update,
                               interval=int(1000 / max(ticks_per_second, 0.001)),
                               cache_frame_data=False)
    plt.tight_layout(); plt.show()


def run_multi_grid_demo(layout: str = "quadrants",
                        rows: int = 8, cols: int = 8,
                        ticks_per_second: float = 2.5,
                        max_depth: int = 4) -> None:
    """
    Multi-program zone grid demo.

    Each zone runs a phase-shifted version of the Y→X→Z→Diag sequence.
    Every 8 ticks the colour pattern rotates — each quadrant is always
    one step ahead of its neighbour, creating a sweeping wave effect.

    layout options:
      "quadrants"   — 2×2 block zones      (default)
      "checkerboard"— alternating zones per cell
      "stripes"     — 4 horizontal bands
      "rings"       — concentric zone rings from centre
    """
    zone_maps = {
        "quadrants":    lambda r, c: (r >= rows // 2) * 2 + (c >= cols // 2),
        "checkerboard": lambda r, c: (r + c) % 4,
        "stripes":      lambda r, *_: r * 4 // rows,
        "rings":        lambda r, c: min(3, max(abs(r - rows // 2),
                                                abs(c - cols // 2)) * 4
                                             // max(1, min(rows, cols) // 2)),
    }
    zone_map_fn = zone_maps.get(layout, zone_maps["quadrants"])
    grid = make_zones(rows, cols, zone_map_fn)

    fig, ax = plt.subplots(figsize=(9, 9))
    fig.patch.set_facecolor("#0d0d0d")
    tick = [0]

    def update(_):
        grid.step(tick[0])
        tick[0] += 1
        draw_grid_frame(ax, grid, max_depth, zone_palette=ZONE_PALETTE)
        families = {grid.programs[r][c].name: family_of(grid.cells[r][c].mask)
                    for r in range(grid.rows) for c in range(grid.cols)}
        sample = "  ".join(f"{k[-1]}:{v[:1]}" for k, v in sorted(families.items()))
        ax.set_title(f"multi-zone [{layout}]  t={tick[0]}\n{sample}",
                     fontsize=9, color="white")

    fig._anim = FuncAnimation(fig, update,
                               interval=int(1000 / max(ticks_per_second, 0.001)),
                               cache_frame_data=False)
    plt.tight_layout(); plt.show()


# ══════════════════════════════════════════════════════════════════════════════
# SCRIPT PARSER  —  parse_geo_script(text) -> Program
#
# .geo mini-language  (v2 — expanded)
#
# Statements:
#   NAME      <name>
#   DEFINE    <alias>  <condition expression>
#   RULE      IF <condition> THEN <action> [AS <label>]
#   DEFAULT   <action>
#   INCLUDE   <filepath.geo>
#
# Conditions (chain with AND / OR / BUT / NOT, parentheses for grouping):
#   family=<FAMILY>           mask in named family
#   mask=<1010>               exact 4-bit mask (binary string)
#   mask_in=<1000,0100,...>   mask is one of listed binary values
#   tick>=<N>                 tick at or above threshold
#   tick<<N>                  tick below threshold
#   tick%<P>=<R>              periodic trigger
#   tick_in=<lo..hi>          tick in inclusive range
#   depth>=<N>                depth at or above
#   depth<<N>                 depth below
#   depth=<N>                 exact depth
#   depth_in=<lo..hi>         depth in inclusive range
#   active=<N>                exact active quadrant count
#   active>=<N>               at least N active
#   active<=<N>               at most N active
#   nb_N=<FAMILY>             directional neighbor family (N/S/E/W)
#   nb_any=<FAMILY>           any cardinal neighbor in family
#   nb_count=<FAMILY>:<N>     exactly N neighbors in family
#   nb_count_gte=<FAM>:<N>    at least N neighbors in family
#   nb_prog_N=<name>          directional neighbor program
#   nb_prog_any=<name>        any neighbor runs program
#   nb_prog_count=<name>:<N>  exactly N neighbors run program
#   nb_prog_gte=<name>:<N>    at least N neighbors run program
#   own_prog=<name>           this cell's program name
#   random<<prob>             true with probability (0.0-1.0)
#   var_<name>>=<N>           cell variable >= N
#   var_<name>=<N>            cell variable == N
#   var_<name><<N>            cell variable < N
#   signal=<name>             named signal received this tick
#   ALWAYS                    always true (catch-all)
#
# Actions (chain with + for multi-action):
#   ADVANCE                   step mask forward in loop
#   ADVANCE <N>               step mask forward N times
#   HOLD                      freeze mask
#   GATE_ON / GATE_OFF        force all-on / all-off
#   SWITCH <FAMILY>           jump to loop family
#   SET <1010>                force exact mask (binary)
#   ROTATE_CW / ROTATE_CCW   rotate mask bits
#   FLIP_H / FLIP_V           mirror mask bits
#   SET_VAR <name> <value>    set cell variable
#   INCR_VAR <name> [delta]   increment cell variable
#   EMIT <signal_name>        broadcast signal to neighbors
#   CALL <prog_name>          invoke sub-program
#   PROG <prog_name>          switch cell's program
#   PLURALITY [N]             adopt majority neighbor program
# ══════════════════════════════════════════════════════════════════════════════

import os as _os

def parse_geo_script(text: str, base_dir: str = None) -> Program:
    """Parse a .geo script string and return a ready-to-run Program.

    base_dir is used to resolve INCLUDE paths; defaults to cwd.
    Supports multi-line rules by joining continuation lines.
    """
    rules:   List[Rule] = []
    name:    str        = "script"
    default: Action     = Advance()
    defines: dict       = {}    # alias -> token list

    if base_dir is None:
        base_dir = _os.getcwd()

    # Pre-process: join continuation lines (lines not starting with a keyword)
    valid_keywords = {"NAME", "RULE", "DEFAULT", "DEFINE", "INCLUDE"}
    continuation_keywords = {"THEN", "AS"}  # These should be joined with previous line
    lines = []
    current_line = ""
    
    for raw in text.splitlines():
        # Strip comments
        line = raw.split("#")[0].strip()
        # Also check if line is empty or only decorative characters
        is_empty = not line or all(c in "═─│┌┐└┘├┤┬┴┼═" for c in line)
        
        if is_empty:
            if current_line:
                lines.append(current_line)
                current_line = ""
            continue
        
        # Check if this starts with a keyword
        first_token = line.split()[0].upper() if line.split() else ""
        
        if first_token in valid_keywords:
            # New statement - save previous line if any
            if current_line:
                lines.append(current_line)
            current_line = line
        elif first_token in continuation_keywords:
            # Continuation keyword - always join with previous line
            if current_line:
                current_line += " " + line
            else:
                current_line = line
        else:
            # Continuation line - append to current
            if current_line:
                current_line += " " + line
            else:
                # Orphan continuation - treat as new line
                current_line = line
    
    # Don't forget the last line
    if current_line:
        lines.append(current_line)

    for line in lines:
        tokens = line.split()
        kw = tokens[0].upper()

        if kw == "NAME":
            name = " ".join(tokens[1:])
        elif kw == "DEFAULT":
            default = _parse_action(tokens[1:])
        elif kw == "DEFINE":
            alias = tokens[1]
            defines[alias] = tokens[2:]
        elif kw == "INCLUDE":
            path = " ".join(tokens[1:])
            if not _os.path.isabs(path):
                path = _os.path.join(base_dir, path)
            with open(path, "r") as f:
                inc_text = f.read()
            inc_prog = parse_geo_script(inc_text, _os.path.dirname(path))
            rules.extend(inc_prog.rules)
            if inc_prog.name != "script":
                name = inc_prog.name
        elif kw == "RULE":
            expanded = _expand_defines(tokens[1:], defines)
            rules.append(_parse_rule(expanded))

    return Program(rules, default, name)


def load_geo(filepath: str) -> Program:
    """Load a .geo script from disk and return a ready-to-run Program."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    return parse_geo_script(text, _os.path.dirname(_os.path.abspath(filepath)))


def _expand_defines(tokens: List[str], defines: dict) -> List[str]:
    """Replace alias tokens with their defined expansions."""
    out = []
    for tok in tokens:
        if tok in defines:
            out.extend(defines[tok])
        else:
            out.append(tok)
    return out


def _parse_rule(tokens: List[str]) -> Rule:
    upper = [t.upper() for t in tokens]
    try:
        then_i = upper.index("THEN")
    except ValueError:
        raise SyntaxError(f"Missing THEN in: {' '.join(tokens)!r}")

    cond_toks = tokens[1:then_i]        # after "IF"
    rest_toks = tokens[then_i + 1:]     # after "THEN"

    rule_name = ""
    upper_rest = [t.upper() for t in rest_toks]
    if "AS" in upper_rest:
        ai        = upper_rest.index("AS")
        rule_name = "_".join(rest_toks[ai + 1:])
        rest_toks = rest_toks[:ai]

    return Rule(_parse_condition(cond_toks), _parse_action(rest_toks), rule_name)


def _parse_condition(tokens: List[str]) -> Cond:
    """Parse condition tokens with support for parenthesised grouping."""
    if not tokens:
        return ALWAYS
    # Tokenize parentheses — split "(foo" into "(", "foo" etc.
    flat = _tokenize_parens(tokens)
    cond, pos = _parse_cond_expr(flat, 0)
    return cond


def _tokenize_parens(tokens: List[str]) -> List[str]:
    """Split parentheses out of tokens so '(family=X_LOOP' becomes ['(', 'family=X_LOOP']."""
    out = []
    for tok in tokens:
        while tok.startswith("("):
            out.append("(")
            tok = tok[1:]
        trail = []
        while tok.endswith(")"):
            trail.append(")")
            tok = tok[:-1]
        if tok:
            out.append(tok)
        out.extend(trail)
    return out


def _parse_cond_expr(tokens: List[str], pos: int) -> Tuple[Cond, int]:
    """Recursive descent: parse condition expression with AND/OR/BUT and parens."""
    left, pos = _parse_cond_unary(tokens, pos)
    while pos < len(tokens) and tokens[pos].upper() in ("AND", "OR", "BUT"):
        op = tokens[pos].upper()
        pos += 1
        right, pos = _parse_cond_unary(tokens, pos)
        if   op == "AND": left = left.AND(right)
        elif op == "OR":  left = left.OR(right)
        elif op == "BUT": left = left.BUT(right)
    return left, pos


def _parse_cond_unary(tokens: List[str], pos: int) -> Tuple[Cond, int]:
    """Handle NOT prefix and parenthesised groups."""
    if pos >= len(tokens):
        return ALWAYS, pos
    if tokens[pos].upper() == "NOT":
        pos += 1
        inner, pos = _parse_cond_unary(tokens, pos)
        return ~inner, pos
    if tokens[pos] == "(":
        pos += 1  # skip "("
        inner, pos = _parse_cond_expr(tokens, pos)
        if pos < len(tokens) and tokens[pos] == ")":
            pos += 1  # skip ")"
        return inner, pos
    # Single atom
    cond = _parse_atom([tokens[pos]])
    return cond, pos + 1


def _parse_atom(tokens: List[str]) -> Cond:
    if not tokens:
        return ALWAYS
    if tokens[0].upper() == "NOT":
        return ~_parse_atom(tokens[1:])
    if tokens[0].upper() == "ALWAYS":
        return ALWAYS
    tok = tokens[0]
    lo  = tok.lower()

    if lo.startswith("family="):
        return IF_family(tok.split("=", 1)[1])

    if lo.startswith("mask_in="):
        raw = tok.split("=", 1)[1]
        vals = [int(v, 2) if all(c in "01" for c in v) else int(v, 16)
                for v in raw.split(",")]
        return IF_mask_in(vals)

    if lo.startswith("mask="):
        raw = tok.split("=", 1)[1]
        return IF_mask(int(raw, 2) if all(c in "01" for c in raw) else int(raw, 16))

    if lo.startswith("tick_in="):
        raw = tok.split("=", 1)[1]
        lo_val, hi_val = raw.split("..")
        return IF_tick_between(int(lo_val), int(hi_val))

    if lo.startswith("tick>="):
        return IF_tick_gte(int(tok.split(">=", 1)[1]))

    if lo.startswith("tick<"):
        return IF_tick_lt(int(tok.split("<", 1)[1]))

    if lo.startswith("tick="):
        # tick=N → exact tick equality
        return IF_tick_eq(int(tok.split("=", 1)[1]))

    if lo.startswith("tick%"):
        rest = tok[5:]
        if "_in=" in rest:
            # tick%P_in=A..B  →  lo <= (tick % P) <= hi
            p, range_part = rest.split("_in=", 1)
            lo_val, hi_val = range_part.split("..")
            return IF_tick_mod_between(int(p), int(lo_val), int(hi_val))
        if "<" in rest and "=" not in rest:
            # tick%P<R  →  (tick % P) < R
            p, r = rest.split("<", 1)
            period = int(p)
            threshold = int(r)
            class _C(Cond):
                def _test(self, _, tick, *args): return (tick % period) < threshold
                def __repr__(self): return f"tick%{period}<{threshold}"
            return _C()
        if "=" in rest:
            p, r = rest.split("=", 1)
            return IF_tick_mod(int(p), int(r))
        return IF_tick_mod(int(rest))

    if lo.startswith("depth_in="):
        raw = tok.split("=", 1)[1]
        lo_val, hi_val = raw.split("..")
        return IF_depth_between(int(lo_val), int(hi_val))

    if lo.startswith("depth>="):
        return IF_depth_gte(int(tok.split(">=", 1)[1]))

    if lo.startswith("depth<"):
        return IF_depth_lt(int(tok.split("<", 1)[1]))

    if lo.startswith("depth="):
        return IF_depth_eq(int(tok.split("=", 1)[1]))

    if lo.startswith("depth%"):
        # depth%N=R → depth modulo N equals R
        rest = tok[6:]
        if "=" in rest:
            p, r = rest.split("=", 1)
            return IF_depth_mod(int(p), int(r))
        return IF_depth_mod(int(rest), 0)

    if lo.startswith("active>="):
        return IF_active_gte(int(tok.split(">=", 1)[1]))

    if lo.startswith("active<="):
        return IF_active_lte(int(tok.split("<=", 1)[1]))

    if lo.startswith("active="):
        return IF_active_count(int(tok.split("=", 1)[1]))

    if lo.startswith("nb_count_gte="):
        raw = tok.split("=", 1)[1]
        fam, n = raw.rsplit(":", 1)
        return IF_neighbor_count_gte(fam, int(n))

    if lo.startswith("nb_count_lte="):
        raw = tok.split("=", 1)[1]
        fam, n = raw.rsplit(":", 1)
        return IF_neighbor_count_lte(fam, int(n))

    if lo.startswith("nb_count8_gte="):
        raw = tok.split("=", 1)[1]
        fam, n = raw.rsplit(":", 1)
        return IF_neighbor_count8_gte(fam, int(n))

    if lo.startswith("nb_count8_lte="):
        raw = tok.split("=", 1)[1]
        fam, n = raw.rsplit(":", 1)
        return IF_neighbor_count8_lte(fam, int(n))

    if lo.startswith("nb_count8="):
        raw = tok.split("=", 1)[1]
        fam, n = raw.rsplit(":", 1)
        return IF_neighbor_count8(fam, int(n))

    if lo.startswith("nb_count="):
        raw = tok.split("=", 1)[1]
        fam, n = raw.rsplit(":", 1)
        return IF_neighbor_count(fam, int(n))

    if lo.startswith("nb_mask_count8="):
        raw = tok.split("=", 1)[1]
        mask_hex, n = raw.rsplit(":", 1)
        if mask_hex.startswith("0b"):
            mask_value = int(mask_hex, 2)
        elif mask_hex.startswith("0x"):
            mask_value = int(mask_hex, 16)
        else:
            mask_value = int(mask_hex, 2)
        return IF_neighbor_mask_count8(mask_value, int(n))

    if lo.startswith("nb_mask_count="):
        raw = tok.split("=", 1)[1]
        mask_hex, n = raw.rsplit(":", 1)
        # Parse mask value (supports binary like 1111 or hex like 0xF)
        if mask_hex.startswith("0b"):
            mask_value = int(mask_hex, 2)
        elif mask_hex.startswith("0x"):
            mask_value = int(mask_hex, 16)
        else:
            mask_value = int(mask_hex, 2)  # Default to binary
        return IF_neighbor_mask_count(mask_value, int(n))

    if lo.startswith("nb_any="):
        return IF_any_neighbor(tok.split("=", 1)[1])

    if lo.startswith("nb_prog_count="):
        raw = tok.split("=", 1)[1]
        prog_name, n = raw.rsplit(":", 1)
        return IF_neighbor_prog_count(prog_name, int(n))

    if lo.startswith("nb_prog_gte="):
        raw = tok.split("=", 1)[1]
        prog_name, n = raw.rsplit(":", 1)
        return IF_neighbor_prog_gte(prog_name, int(n))

    if lo.startswith("nb_prog_any="):
        return IF_any_neighbor_prog(tok.split("=", 1)[1])

    if lo.startswith("nb_prog_") and "=" in tok:
        dir_raw, prog = tok.split("=", 1)
        direction = dir_raw[8:].upper()
        if direction in ("N", "S", "E", "W"):
            return IF_neighbor_prog(direction, prog)

    if lo.startswith("own_prog="):
        return IF_own_prog(tok.split("=", 1)[1])

    if lo.startswith("random>="):
        return IF_random_gte(float(tok.split(">=", 1)[1]))

    if lo.startswith("random<"):
        return IF_random_lt(float(tok.split("<", 1)[1]))

    if lo.startswith("signal="):
        return IF_signal(tok.split("=", 1)[1])

    # Neighbor variable conditions: nb_var_N_heat>=3, nb_var_S_act<10, etc.
    # Format: nb_var_DIR_VARNAME{>=,<=,<,=}VALUE
    if lo.startswith("nb_var_") and any(op in tok for op in (">=", "<=", "<", "=")):
        # Extract direction (single char after nb_var_)
        rest = tok[7:]  # after "nb_var_"
        direction = rest[0].upper()
        if direction in ("N", "S", "E", "W"):
            varpart = rest[2:]  # skip "N_" etc.
            if ">=" in varpart:
                name_part, val = varpart.split(">=", 1)
                return IF_nb_var_gte(direction, name_part, int(val))
            elif "<=" in varpart:
                name_part, val = varpart.split("<=", 1)
                return IF_nb_var_lte(direction, name_part, int(val))
            elif "<" in varpart:
                name_part, val = varpart.split("<", 1)
                return IF_nb_var_lt(direction, name_part, int(val))
            else:
                name_part, val = varpart.split("=", 1)
                return IF_nb_var_eq(direction, name_part, int(val))

    # Cell variable conditions: var_heat>=3, var_heat<=5, var_heat=0, var_heat<5, var_heat_in=2..4
    if lo.startswith("var_") and ("_in=" in tok or ">=" in tok or "<=" in tok or "<" in tok or "=" in tok):
        if "_in=" in tok:
            name_part, range_part = tok.split("_in=", 1)
            lo_val, hi_val = range_part.split("..")
            return IF_var_between(name_part[4:], int(lo_val), int(hi_val))
        elif ">=" in tok:
            name_part, val = tok.split(">=", 1)
            return IF_var_gte(name_part[4:], int(val))
        elif "<=" in tok:
            name_part, val = tok.split("<=", 1)
            return IF_var_lte(name_part[4:], int(val))
        elif "<" in tok:
            name_part, val = tok.split("<", 1)
            return IF_var_lt(name_part[4:], int(val))
        else:
            name_part, val = tok.split("=", 1)
            return IF_var_eq(name_part[4:], int(val))

    if lo.startswith("nb_") and "=" in tok:
        dir_raw, fam = tok.split("=", 1)
        direction = dir_raw[3:].upper()
        if direction in ("N", "S", "E", "W"):
            return IF_neighbor_family(direction, fam)

    raise SyntaxError(f"Unknown condition atom: {tok!r}")


def _parse_action(tokens: List[str]) -> Action:
    """Parse action tokens. Use + to chain multiple actions."""
    if not tokens:
        return Advance()
    # Check for composite actions joined by "+"
    if "+" in tokens:
        groups = []
        current = []
        for t in tokens:
            if t == "+":
                if current:
                    groups.append(current)
                    current = []
            else:
                current.append(t)
        if current:
            groups.append(current)
        if len(groups) > 1:
            return CompositeAction([_parse_single_action(g) for g in groups])
        tokens = groups[0]
    return _parse_single_action(tokens)


def _parse_single_action(tokens: List[str]) -> Action:
    """Parse a single action (not composite)."""
    kw = tokens[0].upper()
    if kw == "ADVANCE":
        if len(tokens) > 1:
            return AdvanceN(int(tokens[1]))
        return Advance()
    if kw == "HOLD":       return Hold()
    if kw == "GATE_ON":    return GateOn()
    if kw == "GATE_OFF":   return GateOff()
    if kw == "SWITCH":     return SwitchFamily(tokens[1])
    if kw == "SET":
        raw = tokens[1]
        return SetMask(int(raw, 2) if all(c in "01" for c in raw) else int(raw, 16))
    if kw == "ROTATE_CW":   return RotateCW()
    if kw == "ROTATE_CCW":  return RotateCCW()
    if kw == "FLIP_H":      return FlipH()
    if kw == "FLIP_V":      return FlipV()
    if kw == "SET_VAR":      return SetVar(tokens[1], int(tokens[2]))
    if kw == "INCR_VAR":
        delta = int(tokens[2]) if len(tokens) > 2 else 1
        return IncrVar(tokens[1], delta)
    if kw == "EMIT":         return Emit(tokens[1])
    if kw == "CALL":         return CallProgram(tokens[1])
    if kw == "PROG":         return SwitchProgram(tokens[1])
    if kw == "PLURALITY":
        n = int(tokens[1]) if len(tokens) > 1 else 2
        return SwitchToPluralityNeighbor(n)
    if kw == "ACCUM_VAR":
        # ACCUM_VAR target direction source [weight]
        target = tokens[1]
        direction = tokens[2].upper()
        source = tokens[3]
        weight = int(tokens[4]) if len(tokens) > 4 else 1
        return AccumVar(target, direction, source, weight)
    if kw == "CLAMP_VAR":
        # CLAMP_VAR name lo hi
        return ClampVar(tokens[1], int(tokens[2]), int(tokens[3]))
    raise SyntaxError(f"Unknown action: {kw!r}")


# ── Validation ───────────────────────────────────────────────────────────────

@dataclass
class GeoError:
    """A single validation error with line number and message."""
    line: int
    message: str
    def __repr__(self): return f"L{self.line}: {self.message}"

def validate_geo(text: str) -> List[GeoError]:
    """Validate a .geo script and return a list of errors (empty = valid)."""
    errors: List[GeoError] = []
    valid_kw = {"NAME", "RULE", "DEFAULT", "DEFINE", "INCLUDE"}
    continuation_kw = {"THEN", "AS"}
    valid_families = {"Y_LOOP", "X_LOOP", "Z_LOOP", "DIAG_LOOP"}
    valid_actions = {"ADVANCE", "HOLD", "GATE_ON", "GATE_OFF", "SWITCH", "SET",
                     "ROTATE_CW", "ROTATE_CCW", "FLIP_H", "FLIP_V",
                     "SET_VAR", "INCR_VAR", "EMIT", "CALL", "PROG", "PLURALITY",
                     "ACCUM_VAR", "CLAMP_VAR"}
    has_name = False
    defines: dict = {}   # collect aliases for trial parsing

    # Pre-process: join continuation lines (same logic as parse_geo_script)
    lines = []
    current_line = ""
    line_numbers = []  # Track original line numbers for error reporting
    
    for line_num, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#")[0].strip()
        is_empty = not line or all(c in "═─│┌┐└┘├┤┬┴┼═" for c in line)
        
        if is_empty:
            if current_line:
                lines.append(current_line)
                line_numbers.append(current_line_start)
            current_line = ""
            continue
        
        first_token = line.split()[0].upper() if line.split() else ""
        
        if first_token in valid_kw:
            if current_line:
                lines.append(current_line)
                line_numbers.append(current_line_start)
            current_line = line
            current_line_start = line_num
        elif first_token in continuation_kw:
            if current_line:
                current_line += " " + line
            else:
                current_line = line
                current_line_start = line_num
        else:
            if current_line:
                current_line += " " + line
            else:
                current_line = line
                current_line_start = line_num
    
    if current_line:
        lines.append(current_line)
        line_numbers.append(current_line_start)

    # Now validate the joined lines
    for i, line in zip(line_numbers, lines):
        tokens = line.split()
        if not tokens:
            continue
        kw = tokens[0].upper()

        if kw not in valid_kw:
            errors.append(GeoError(i, f"Unknown statement: '{tokens[0]}' "
                                      f"(expected NAME/RULE/DEFAULT/DEFINE/INCLUDE)"))
            continue

        if kw == "NAME":
            if len(tokens) < 2:
                errors.append(GeoError(i, "NAME requires a value"))
            has_name = True

        elif kw == "DEFINE":
            if len(tokens) < 3:
                errors.append(GeoError(i, "DEFINE requires an alias and condition expression"))
            else:
                defines[tokens[1]] = tokens[2:]

        elif kw == "INCLUDE":
            if len(tokens) < 2:
                errors.append(GeoError(i, "INCLUDE requires a file path"))

        elif kw == "RULE":
            upper = [t.upper() for t in tokens]
            if "IF" not in upper:
                errors.append(GeoError(i, "RULE must start with IF"))
            elif "THEN" not in upper:
                errors.append(GeoError(i, "RULE missing THEN keyword"))
            else:
                then_i = upper.index("THEN")
                action_toks = tokens[then_i + 1:]
                # Strip AS label
                upper_rest = [t.upper() for t in action_toks]
                if "AS" in upper_rest:
                    action_toks = action_toks[:upper_rest.index("AS")]
                if not action_toks:
                    errors.append(GeoError(i, "RULE has no action after THEN"))
                else:
                    # Validate action keyword (check each part of composite)
                    for part in " ".join(action_toks).split("+"):
                        act_kw = part.strip().split()[0].upper() if part.strip() else ""
                        if act_kw and act_kw not in valid_actions:
                            errors.append(GeoError(i, f"Unknown action: '{act_kw}'"))
                    # Validate SWITCH has a valid family
                    if action_toks[0].upper() == "SWITCH":
                        if len(action_toks) < 2:
                            errors.append(GeoError(i, "SWITCH requires a family name"))
                        elif action_toks[1] not in valid_families:
                            errors.append(GeoError(i, f"Unknown family: '{action_toks[1]}' "
                                                      f"(expected {'/'.join(sorted(valid_families))})"))
                # Try to parse the full rule to catch deeper errors
                try:
                    _parse_rule(_expand_defines(tokens[1:], defines))
                except (SyntaxError, ValueError, IndexError) as e:
                    errors.append(GeoError(i, f"Parse error: {e}"))

        elif kw == "DEFAULT":
            if len(tokens) < 2:
                errors.append(GeoError(i, "DEFAULT requires an action"))
            else:
                act_kw = tokens[1].upper()
                if act_kw not in valid_actions:
                    errors.append(GeoError(i, f"Unknown default action: '{act_kw}'"))

    if not has_name:
        errors.insert(0, GeoError(0, "Script has no NAME statement (recommended)"))

    return errors


# ── Inline .geo scripts ───────────────────────────────────────────────────────

GEO_SPIRAL = """
# spiral.geo
# Beats through all four loop families in an 8-tick cycle.
# Deep cells (depth>=5) get sealed as gate-on.
NAME   spiral
RULE   IF tick%8=0   THEN SWITCH Y_LOOP    AS beat-Y
RULE   IF tick%8=2   THEN SWITCH X_LOOP    AS beat-X
RULE   IF tick%8=4   THEN SWITCH Z_LOOP    AS beat-Z
RULE   IF tick%8=6   THEN SWITCH DIAG_LOOP AS beat-D
RULE   IF depth>=5   THEN GATE_ON          AS seal-deep
DEFAULT ADVANCE
"""

GEO_PULSE_DEPTH = """
# pulse_depth.geo
# Pulses gate-on every 10 ticks; deep cells lock to Z-loop (blue).
NAME   pulse_depth
RULE   IF tick%10=0 BUT family=GATE    THEN GATE_ON       AS flash
RULE   IF family=GATE AND tick%10=3    THEN SWITCH Y_LOOP  AS unflash
RULE   IF depth>=3  AND family=Y_LOOP  THEN SWITCH Z_LOOP  AS deep-z
DEFAULT ADVANCE
"""

GEO_NB_SCRIPT = """
# nb_spread.geo
# Cells that see a Y-loop neighbor switch to X-loop (usable on a Grid).
NAME   nb_spread
RULE   IF nb_any=Y_LOOP AND family=Z_LOOP  THEN SWITCH X_LOOP  AS spread
RULE   IF nb_any=X_LOOP AND family=Z_LOOP  THEN SWITCH DIAG_LOOP AS ring
DEFAULT ADVANCE
"""

GEO_VOTE_EXAMPLE = """
# vote_example.geo
# Demonstrates program-identity conditions and PROG / PLURALITY actions.
# Designed for use on a Grid where vote-0..3 programs are registered.
#
# Rule 1: if 2+ neighbors run vote-1 AND we are currently vote-0, adopt vote-1.
# Rule 2: PLURALITY 2 fallback — adopt any program held by 2+ neighbours.
# Both rules also advance the mask each tick (PROG and PLURALITY do next_mask).
NAME   vote_example
RULE   IF nb_prog_any=vote-1 AND own_prog=vote-0  THEN PROG vote-1  AS adopt-1
RULE   IF nb_prog_any=vote-0 AND own_prog=vote-1  THEN PROG vote-0  AS adopt-0
DEFAULT PLURALITY 2
"""

# ── New v2 demo scripts (showcase expanded .geo features) ────────────────────

GEO_ROTATE_MIRROR = """
# rotate_mirror.geo
# Demonstrates ROTATE_CW, FLIP_H, and parenthesised conditions.
# Rotates geometry clockwise for the first 16 ticks, then mirrors it.
# Uses DEFINE to create a reusable alias.
NAME   rotate_mirror
DEFINE is_single   (family=Y_LOOP OR family=DIAG_LOOP)
RULE   IF is_single AND tick<16   THEN ROTATE_CW           AS spin
RULE   IF is_single AND tick>=16  THEN FLIP_H              AS mirror
RULE   IF tick%20=0               THEN SWITCH Y_LOOP        AS reset
DEFAULT ADVANCE
"""

GEO_STOCHASTIC = """
# stochastic.geo
# Probabilistic rules for organic, non-deterministic evolution.
# 30% chance to gate-on each tick (unless already gated).
# Deep cells randomly flip to different families.
NAME   stochastic
RULE   IF random<0.3 BUT family=GATE            THEN GATE_ON             AS flash
RULE   IF family=GATE AND random<0.5             THEN SWITCH Y_LOOP       AS ungate
RULE   IF depth>=4 AND random<0.2                THEN SWITCH Z_LOOP       AS deep-z
RULE   IF depth>=4 AND random<0.1                THEN SWITCH DIAG_LOOP    AS deep-d
DEFAULT ADVANCE
"""

GEO_HEAT_SPREAD = """
# heat_spread.geo
# Cell variables demo: cells accumulate "heat" and change family at thresholds.
# Each tick in Y-loop increments heat. When heat >= 5, switch to X-loop and reset.
# When heat >= 10 in X-loop, switch to Z-loop.
NAME   heat_spread
RULE   IF family=Y_LOOP  THEN ADVANCE + INCR_VAR heat 1         AS warm
RULE   IF var_heat>=5 AND family=Y_LOOP  THEN SWITCH X_LOOP + SET_VAR heat 0  AS ignite
RULE   IF family=X_LOOP  THEN ADVANCE + INCR_VAR heat 2         AS burn
RULE   IF var_heat>=10   THEN SWITCH Z_LOOP + SET_VAR heat 0    AS cool
DEFAULT ADVANCE
"""

GEO_SIGNAL_WAVE = """
# signal_wave.geo
# Signal-based communication between grid cells.
# Y-loop cells emit a "pulse" signal. Cells receiving the signal switch to X-loop.
# X-loop cells emit "ripple". Cells receiving ripple switch to DIAG.
NAME   signal_wave
RULE   IF family=Y_LOOP                 THEN ADVANCE + EMIT pulse     AS send
RULE   IF signal=pulse AND family=Z_LOOP THEN SWITCH X_LOOP            AS react
RULE   IF family=X_LOOP                 THEN ADVANCE + EMIT ripple    AS echo
RULE   IF signal=ripple AND family=Z_LOOP THEN SWITCH DIAG_LOOP        AS ring
DEFAULT ADVANCE
"""

GEO_DEPTH_LAYERS = """
# depth_layers.geo
# Demonstrates range conditions and multi-action composites.
# Shallow layers (0-2) rotate, mid layers (3-4) mirror, deep layers (5+) gate.
NAME   depth_layers
RULE   IF depth_in=0..2 AND family=Y_LOOP  THEN ROTATE_CW + ADVANCE     AS shallow-spin
RULE   IF depth_in=3..4 AND family=Y_LOOP  THEN FLIP_V                  AS mid-flip
RULE   IF depth>=5                         THEN GATE_ON                  AS deep-seal
RULE   IF tick%12=0                        THEN SWITCH Y_LOOP            AS reset
DEFAULT ADVANCE
"""

GEO_CONWAY_LIFE = """
# conway_life.geo
# Conway's Game of Life approximation using quad-mask families as alive/dead.
# Y_LOOP = alive, GATE(0000) = dead.
# Uses neighbor counting conditions on a Grid.
# Alive + 2-3 alive neighbors -> stay alive, else die.
# Dead + exactly 3 alive neighbors -> come alive.
NAME   conway_life
DEFINE alive       family=Y_LOOP
DEFINE dead        mask=0000
RULE   IF alive AND nb_count=Y_LOOP:2  THEN ADVANCE              AS survive-2
RULE   IF alive AND nb_count=Y_LOOP:3  THEN ADVANCE              AS survive-3
RULE   IF alive                        THEN GATE_OFF             AS die
RULE   IF dead AND nb_count=Y_LOOP:3   THEN SWITCH Y_LOOP        AS birth
DEFAULT HOLD
"""

GEO_MASK_SET = """
# mask_set.geo
# Demonstrates mask_in condition and multi-step ADVANCE.
# Only specific mask values trigger special behavior.
NAME   mask_set
RULE   IF mask_in=1000,0100  THEN ADVANCE 2              AS skip-ahead
RULE   IF mask_in=0010,0001  THEN ROTATE_CCW              AS twist-back
RULE   IF mask=1111          THEN SWITCH Y_LOOP            AS break-gate
DEFAULT ADVANCE
"""

GEO_COMPOSITE = """
# composite.geo
# Composite actions: do multiple things in one rule.
# Demonstrates chaining SWITCH + EMIT + SET_VAR in a single THEN clause.
NAME   composite
RULE   IF tick%8=0    THEN SWITCH Y_LOOP + EMIT beat + SET_VAR phase 0    AS beat-start
RULE   IF tick%8=4    THEN SWITCH X_LOOP + EMIT beat + SET_VAR phase 1    AS beat-mid
RULE   IF signal=beat AND family=Z_LOOP  THEN FLIP_H + INCR_VAR react 1  AS respond
DEFAULT ADVANCE
"""


def run_script_demo(script: str = GEO_SPIRAL,
                    start_mask: int = 0b1000,
                    ticks_per_second: float = 3.0,
                    max_depth: int = 6) -> None:
    """
    Parse a .geo script string and animate the resulting program.

    Swap `script` for GEO_PULSE_DEPTH, GEO_NB_SCRIPT, or any string
    using the .geo mini-language.
    """
    prog = parse_geo_script(script)
    root = Node(0.0, 0.0, 1.0, 0, start_mask)
    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor("#0d0d0d")
    tick = [0]

    def update(_):
        prog.step_tree(root, tick[0])
        tick[0] += 1
        draw_frame(ax, root, max_depth, colored=True)
        ax.set_title(f"{prog.name}  [{root.mask:04b}] {family_of(root.mask)}"
                     f"  t={tick[0]}", fontsize=10, color="white")

    fig._anim = FuncAnimation(fig, update,
                               interval=int(1000 / max(ticks_per_second, 0.001)),
                               cache_frame_data=False)
    plt.tight_layout(); plt.show()


def run_script_grid_demo(script: str, rows: int = 8, cols: int = 8,
                         start_mask: int = 0b1000,
                         ticks_per_second: float = 3.0,
                         max_depth: int = 3,
                         random_seed: bool = False) -> None:
    """Parse a .geo script and run it on a Grid so neighbor conditions work."""
    import random as _rng
    
    # Larger cell size for better visibility
    cell_size = 16.0
    
    prog = parse_geo_script(script)
    if random_seed:
        dead = 0b0000
        alive = start_mask
        grid = Grid.make(rows, cols, prog,
                         init_mask_fn=lambda r, c: alive if _rng.random() < 0.4 else dead,
                         cell_size=cell_size)
    else:
        # Check if this is Conway's Life - use random seeding automatically
        if prog.name and "conway" in prog.name.lower():
            dead = 0b0000
            alive = 0b1111  # Use GATE_ON for visible white cells
            grid = Grid.make(rows, cols, prog,
                             init_mask_fn=lambda r, c: alive if _rng.random() < 0.35 else dead,
                             cell_size=cell_size)
        else:
            grid = Grid.make(rows, cols, prog,
                             init_mask_fn=lambda r, c: start_mask,
                             cell_size=cell_size)
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("#0d0d0d")
    tick = [0]

    def update(_):
        grid.step(tick[0])
        tick[0] += 1
        draw_grid_frame(ax, grid, max_depth)
        ax.set_title(f"{prog.name}  {rows}x{cols} grid  t={tick[0]}",
                     fontsize=10, color="white")

    fig._anim = FuncAnimation(fig, update,
                               interval=int(1000 / max(ticks_per_second, 0.001)),
                               cache_frame_data=False)
    plt.tight_layout(); plt.show()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    import sys

    DEMOS = {
        "spiral":        GEO_SPIRAL,
        "pulse_depth":   GEO_PULSE_DEPTH,
        "nb_spread":     GEO_NB_SCRIPT,
        "vote_example":  GEO_VOTE_EXAMPLE,
        "rotate_mirror": GEO_ROTATE_MIRROR,
        "stochastic":    GEO_STOCHASTIC,
        "heat_spread":   GEO_HEAT_SPREAD,
        "signal_wave":   GEO_SIGNAL_WAVE,
        "depth_layers":  GEO_DEPTH_LAYERS,
        "conway_life":   GEO_CONWAY_LIFE,
        "mask_set":      GEO_MASK_SET,
        "composite":     GEO_COMPOSITE,
    }

    parser = argparse.ArgumentParser(
        description="Binary Quad-Tree Geometric Grammar Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  %(prog)s                              default self-organising demo
  %(prog)s --demo spiral                run a built-in .geo script
  %(prog)s --geo examples/spiral.geo    run any .geo file from disk
  %(prog)s --list                       list available built-in demos
  %(prog)s --demo spiral --depth 8      deeper recursion (more detail)
  %(prog)s --self-org --speed 4         faster tick rate
""")
    # Script demos
    parser.add_argument("--demo", choices=list(DEMOS.keys()),
                        metavar="NAME", help="run a built-in .geo demo by name")
    parser.add_argument("--geo", metavar="FILE",
                        help="run a .geo script file from disk")
    parser.add_argument("--list", action="store_true",
                        help="list available built-in demos and exit")
    # Tuning
    parser.add_argument("--depth", type=int, default=6,
                        help="max quadtree depth (default: 6)")
    parser.add_argument("--speed", type=float, default=3.0,
                        help="ticks per second (default: 3.0)")
    parser.add_argument("--mask", default="1000",
                        help="starting mask in binary (default: 1000)")
    # Grid demos
    parser.add_argument("--self-org", action="store_true",
                        help="run self-organising zone boundary demo")
    parser.add_argument("--grid", action="store_true",
                        help="run neighbor-wave grid demo")
    parser.add_argument("--multi-grid",
                        choices=["quadrants", "checkerboard", "stripes", "rings"],
                        metavar="LAYOUT", help="run multi-zone grid demo")
    # Other demos
    parser.add_argument("--lab", action="store_true",
                        help="run loop-family reference lab (2x3 panel)")
    parser.add_argument("--grammar", action="store_true",
                        help="run grammar rule comparison (2x2 panel)")
    parser.add_argument("--random-seed", action="store_true",
                        help="randomly seed alive/dead cells on grid (for Life etc.)")

    args = parser.parse_args()
    start_mask = int(args.mask, 2)

    if args.list:
        print("Available built-in demos:\n")
        for name in DEMOS:
            prog = parse_geo_script(DEMOS[name])
            print(f"  {name:20s}  {prog.name}")
        print(f"\nRun with:  python {sys.argv[0]} --demo <name>")
        sys.exit(0)

    elif args.geo:
        with open(args.geo, "r") as f:
            script_text = f.read()
        # Auto-detect grid mode for simulations that need neighbor interactions
        use_grid = args.grid or any(kw in args.geo.lower() for kw in ['conway', 'dungeon', 'ecosystem', 'nb_', 'heat_', 'signal_', 'forest_fire'])
        if use_grid:
            run_script_grid_demo(script_text, start_mask=start_mask,
                                 ticks_per_second=args.speed,
                                 max_depth=min(args.depth, 4),
                                 random_seed=args.random_seed)
        else:
            run_script_demo(script_text, start_mask=start_mask,
                            ticks_per_second=args.speed, max_depth=args.depth)

    elif args.demo:
        script_text = DEMOS[args.demo]
        if args.grid:
            run_script_grid_demo(script_text, start_mask=start_mask,
                                 ticks_per_second=args.speed,
                                 max_depth=min(args.depth, 4),
                                 random_seed=args.random_seed)
        else:
            run_script_demo(script_text, start_mask=start_mask,
                            ticks_per_second=args.speed, max_depth=args.depth)

    elif args.grid:
        run_grid_demo(rows=8, cols=8, ticks_per_second=args.speed,
                      max_depth=min(args.depth, 4))

    elif args.multi_grid:
        run_multi_grid_demo(layout=args.multi_grid, rows=8, cols=8,
                            ticks_per_second=args.speed,
                            max_depth=min(args.depth, 4))

    elif args.lab:
        run_lab_demo(max_depth=args.depth, ticks_per_second=args.speed)

    elif args.grammar:
        run_grammar_demo(ticks_per_second=args.speed, max_depth=args.depth)

    else:
        # Default: self-organising zone demo
        run_self_org_demo(rows=10, cols=10, vote_threshold=2,
                          ticks_per_second=args.speed,
                          max_depth=min(args.depth, 4))
