# The `.geo` Language — Reference Manual

## What is `.geo`?

`.geo` is a declarative scripting language for programming the **Binary Quad-Tree Geometric Grammar Engine**. It controls how 4-bit spatial masks evolve over time on a recursive quadtree structure, producing fractal geometry that rotates, pulses, spreads, and self-organises.

Each `.geo` script compiles into a `Program` — an ordered list of rules that fire on every tick of the simulation. The first matching rule wins. If no rule matches, a default action runs.

## Purpose

The `.geo` language exists to make the quad grammar system **data-driven**. Instead of writing Python code to define programs, you write human-readable scripts that can be:

- Authored and edited in any text editor
- Loaded from disk at runtime (`load_geo("path/to/script.geo")`)
- Shared between projects without code dependencies
- Composed together via `INCLUDE` directives
- Validated before execution with `validate_geo(text)`

## Core Concepts

### The 4-Bit Mask

Every node in the quadtree carries a 4-bit mask. Each bit maps to one quadrant:

```
  bit 3 (8) = TL    bit 2 (4) = TR
  bit 0 (1) = BL    bit 1 (2) = BR
```

Active quadrants (bit = 1) are drawn and recursively subdivided. The mask `1010` means TL and BR are active — a diagonal pattern. `1111` fills everything. `0000` is empty.

### Loop Families

The 16 possible masks are grouped into five **loop families** that cycle deterministically:

| Family | Members (binary) | Behavior |
|--------|-------------------|----------|
| **Y_LOOP** | `1000 → 0100 → 0010 → 0001` | Single quadrant rotates |
| **X_LOOP** | `1100 → 0101 → 0011 → 1010` | Adjacent pair cycles |
| **Z_LOOP** | `0111 → 1011 → 1101 → 1110` | Three-quadrant sweep |
| **DIAG_LOOP** | `1001 ↔ 0110` | Diagonal pair toggles |
| **GATE** | `0000`, `1111` | Fixed points (no change) |

`ADVANCE` steps a mask forward one position in its loop. `SWITCH Y_LOOP` jumps the mask to the first member of Y_LOOP (`1000`).

### Recursive Depth

Active quadrants subdivide recursively up to `max_depth`. Each child node carries its own mask. Rules can test `depth` to create layered effects — shallow nodes spin while deep nodes freeze.

---

## Script Structure

A `.geo` script is a sequence of **statements**, one per line. Comments start with `#`.

```geo
# This is a comment
NAME   my_program
DEFINE is_deep  depth>=3 AND family=Y_LOOP
RULE   IF tick%8=0       THEN SWITCH Y_LOOP    AS beat
RULE   IF is_deep        THEN GATE_ON          AS seal
DEFAULT ADVANCE
```

### Statement Types

| Statement | Syntax | Description |
|-----------|--------|-------------|
| `NAME` | `NAME <name>` | Set the program's display name |
| `DEFINE` | `DEFINE <alias> <condition>` | Create a reusable condition alias |
| `RULE` | `RULE IF <cond> THEN <action> [AS <label>]` | Add a conditional rule |
| `DEFAULT` | `DEFAULT <action>` | Fallback when no rule matches |
| `INCLUDE` | `INCLUDE <filepath.geo>` | Import rules from another file |

Rules are evaluated **in order** — the first matching rule fires and all others are skipped.

---

## Conditions Reference

Conditions test the current node's state, tick count, depth, neighbors, or custom variables.

### Mask & Family

| Condition | Description | Example |
|-----------|-------------|---------|
| `family=<NAME>` | Mask belongs to named loop family | `family=Y_LOOP` |
| `mask=<BITS>` | Exact mask match (binary or hex) | `mask=1010` |
| `mask_in=<A,B,...>` | Mask is one of listed values | `mask_in=1000,0100,0010` |

### Time

| Condition | Description | Example |
|-----------|-------------|---------|
| `tick>=<N>` | Tick at or above threshold | `tick>=100` |
| `tick<<N>` | Tick below threshold | `tick<50` |
| `tick%<P>=<R>` | Periodic: tick mod P equals R | `tick%8=0` |
| `tick_in=<LO>..<HI>` | Tick in inclusive range | `tick_in=10..30` |

### Depth

| Condition | Description | Example |
|-----------|-------------|---------|
| `depth>=<N>` | Depth at or above threshold | `depth>=3` |
| `depth<<N>` | Depth below threshold | `depth<5` |
| `depth=<N>` | Exact depth level | `depth=2` |
| `depth_in=<LO>..<HI>` | Depth in inclusive range | `depth_in=2..4` |

### Active Count

| Condition | Description | Example |
|-----------|-------------|---------|
| `active=<N>` | Exactly N quadrants active | `active=2` |
| `active>=<N>` | At least N active | `active>=3` |
| `active<=<N>` | At most N active | `active<=1` |

### Neighbors (Grid mode)

These conditions only work when the program runs on a `Grid`, where cells have cardinal neighbors.

| Condition | Description | Example |
|-----------|-------------|---------|
| `nb_N=<FAMILY>` | North neighbor in family (also S/E/W) | `nb_N=Y_LOOP` |
| `nb_any=<FAMILY>` | Any neighbor in family | `nb_any=X_LOOP` |
| `nb_count=<FAM>:<N>` | Exactly N neighbors in family | `nb_count=Y_LOOP:2` |
| `nb_count_gte=<FAM>:<N>` | At least N neighbors in family | `nb_count_gte=Z_LOOP:3` |

### Neighbor Programs (Grid mode)

| Condition | Description | Example |
|-----------|-------------|---------|
| `nb_prog_N=<name>` | North neighbor runs named program | `nb_prog_N=zone-0` |
| `nb_prog_any=<name>` | Any neighbor runs program | `nb_prog_any=vote-1` |
| `nb_prog_count=<name>:<N>` | Exactly N neighbors run program | `nb_prog_count=vote-0:2` |
| `nb_prog_gte=<name>:<N>` | At least N neighbors run program | `nb_prog_gte=vote-1:3` |
| `own_prog=<name>` | This cell's own program name | `own_prog=zone-0` |

### Probability

| Condition | Description | Example |
|-----------|-------------|---------|
| `random<<prob>` | True with probability 0.0-1.0 | `random<0.3` |

### Cell Variables

| Condition | Description | Example |
|-----------|-------------|---------|
| `var_<name>>=<N>` | Variable >= N | `var_heat>=5` |
| `var_<name>=<N>` | Variable == N | `var_heat=0` |
| `var_<name><<N>` | Variable < N | `var_heat<10` |

### Signals

| Condition | Description | Example |
|-----------|-------------|---------|
| `signal=<name>` | Named signal received from neighbor | `signal=pulse` |

### Special

| Condition | Description |
|-----------|-------------|
| `ALWAYS` | Always true (catch-all) |

---

## Combinators

Chain conditions with boolean logic:

| Combinator | Meaning | Example |
|------------|---------|---------|
| `AND` | Both true | `family=Y_LOOP AND tick>=8` |
| `OR` | Either true | `family=Y_LOOP OR family=X_LOOP` |
| `BUT` | Left true, right false ("except") | `tick%8=0 BUT family=GATE` |
| `NOT` | Negate next condition | `NOT family=GATE` |
| `( )` | Grouping for precedence | `(family=Y_LOOP OR family=X_LOOP) AND tick>=8` |

Without parentheses, combinators evaluate left-to-right.

---

## Actions Reference

### Basic

| Action | Description |
|--------|-------------|
| `ADVANCE` | Step mask forward one position in its loop |
| `ADVANCE <N>` | Step mask forward N positions |
| `HOLD` | Keep mask unchanged |
| `GATE_ON` | Force mask to `1111` (all active) |
| `GATE_OFF` | Force mask to `0000` (all empty) |

### Family & Mask

| Action | Description |
|--------|-------------|
| `SWITCH <FAMILY>` | Jump to first member of named family |
| `SET <BITS>` | Force exact mask value (binary) |

### Transforms

| Action | Description |
|--------|-------------|
| `ROTATE_CW` | Rotate mask bits clockwise (TL→TR→BR→BL→TL) |
| `ROTATE_CCW` | Rotate mask bits counter-clockwise |
| `FLIP_H` | Mirror mask horizontally (TL↔TR, BL↔BR) |
| `FLIP_V` | Mirror mask vertically (TL↔BL, TR↔BR) |

### Variables

| Action | Description |
|--------|-------------|
| `SET_VAR <name> <value>` | Set a named cell variable to an integer |
| `INCR_VAR <name> [delta]` | Increment variable by delta (default 1) |

### Communication

| Action | Description |
|--------|-------------|
| `EMIT <signal>` | Broadcast a named signal to cardinal neighbors |

### Program Control

| Action | Description |
|--------|-------------|
| `CALL <name>` | Invoke a registered sub-program |
| `PROG <name>` | Switch this cell's program (advances mask too) |
| `PLURALITY [N]` | Adopt the majority neighbor program if N+ agree |

### Composite Actions

Chain multiple actions with `+`:

```geo
RULE IF tick%8=0 THEN SWITCH Y_LOOP + EMIT beat + SET_VAR phase 0 AS multi
```

All chained actions execute in order within a single rule.

---

## DEFINE — Reusable Aliases

Create named condition fragments to avoid repetition:

```geo
DEFINE is_alive    family=Y_LOOP
DEFINE is_dead     mask=0000
DEFINE crowded     nb_count_gte=Y_LOOP:4

RULE IF is_alive AND crowded  THEN GATE_OFF  AS overcrowded
RULE IF is_dead               THEN HOLD      AS stay-dead
```

Aliases are expanded before parsing — they are textual substitution, not scoped variables.

---

## INCLUDE — File Composition

Split large programs across files:

```geo
# main.geo
NAME   combined
INCLUDE base_rules.geo
INCLUDE special_rules.geo
DEFAULT ADVANCE
```

Paths are resolved relative to the including file's directory.

---

## Loading and Validation

### From Python

```python
from BinaryQuadTreeTest import parse_geo_script, load_geo, validate_geo

# Parse inline string
prog = parse_geo_script("""
NAME   my_prog
RULE IF family=Y_LOOP THEN ADVANCE
DEFAULT HOLD
""")

# Load from file
prog = load_geo("scripts/my_prog.geo")

# Validate before running
errors = validate_geo(script_text)
for err in errors:
    print(f"Line {err.line}: {err.message}")
```

### Running

```python
from BinaryQuadTreeTest import Node, run_script_demo

# Animate a script
run_script_demo(my_script, start_mask=0b1000, max_depth=6)

# Or step manually
root = Node(0.0, 0.0, 1.0, 0, 0b1000)
for tick in range(100):
    prog.step_tree(root, tick)
```

---

## Example Scripts

### 1. Spiral — Family cycling

```geo
NAME   spiral
RULE   IF tick%8=0   THEN SWITCH Y_LOOP    AS beat-Y
RULE   IF tick%8=2   THEN SWITCH X_LOOP    AS beat-X
RULE   IF tick%8=4   THEN SWITCH Z_LOOP    AS beat-Z
RULE   IF tick%8=6   THEN SWITCH DIAG_LOOP AS beat-D
RULE   IF depth>=5   THEN GATE_ON          AS seal-deep
DEFAULT ADVANCE
```

Cycles through all four loop families every 8 ticks. Deep cells get sealed as solid blocks.

### 2. Stochastic — Random flashes

```geo
NAME   stochastic
RULE   IF random<0.3 BUT family=GATE        THEN GATE_ON          AS flash
RULE   IF family=GATE AND random<0.5         THEN SWITCH Y_LOOP    AS ungate
RULE   IF depth>=4 AND random<0.2            THEN SWITCH Z_LOOP    AS deep-z
DEFAULT ADVANCE
```

Non-deterministic evolution. 30% chance to flash on each tick, random family jumps at depth.

### 3. Depth Layers — Stratified behavior

```geo
NAME   depth_layers
RULE   IF depth_in=0..2 AND family=Y_LOOP  THEN ROTATE_CW + ADVANCE   AS shallow-spin
RULE   IF depth_in=3..4 AND family=Y_LOOP  THEN FLIP_V                AS mid-flip
RULE   IF depth>=5                         THEN GATE_ON                AS deep-seal
RULE   IF tick%12=0                        THEN SWITCH Y_LOOP          AS reset
DEFAULT ADVANCE
```

Shallow nodes rotate, mid-depth mirrors, deep nodes freeze. Periodic reset keeps it cycling.

### 4. Conway's Life — Cellular automaton (Grid mode)

```geo
NAME   conway_life
DEFINE alive   family=Y_LOOP
DEFINE dead    mask=0000
RULE   IF alive AND nb_count=Y_LOOP:2  THEN ADVANCE     AS survive-2
RULE   IF alive AND nb_count=Y_LOOP:3  THEN ADVANCE     AS survive-3
RULE   IF alive                        THEN GATE_OFF    AS die
RULE   IF dead AND nb_count=Y_LOOP:3   THEN SWITCH Y_LOOP AS birth
DEFAULT HOLD
```

Classic Game of Life rules using Y_LOOP as alive and empty mask as dead.

### 5. Signal Wave — Inter-cell communication (Grid mode)

```geo
NAME   signal_wave
RULE   IF family=Y_LOOP                   THEN ADVANCE + EMIT pulse     AS send
RULE   IF signal=pulse AND family=Z_LOOP   THEN SWITCH X_LOOP            AS react
RULE   IF family=X_LOOP                   THEN ADVANCE + EMIT ripple    AS echo
RULE   IF signal=ripple AND family=Z_LOOP  THEN SWITCH DIAG_LOOP        AS ring
DEFAULT ADVANCE
```

Y-loop cells emit "pulse". Z-loop neighbors receive it and switch to X-loop, which emits "ripple" to create a cascading wave.

### 6. Heat Accumulation — Cell variables

```geo
NAME   heat_spread
RULE   IF family=Y_LOOP                   THEN ADVANCE + INCR_VAR heat 1     AS warm
RULE   IF var_heat>=5 AND family=Y_LOOP    THEN SWITCH X_LOOP + SET_VAR heat 0 AS ignite
RULE   IF family=X_LOOP                   THEN ADVANCE + INCR_VAR heat 2     AS burn
RULE   IF var_heat>=10                     THEN SWITCH Z_LOOP + SET_VAR heat 0 AS cool
DEFAULT ADVANCE
```

Cells accumulate heat. At threshold 5 they ignite (Y→X). X-loop burns faster. At 10 they cool down (→Z).

---

## Quick Reference Card

```
STATEMENTS:
  NAME <name>                         — program name
  DEFINE <alias> <cond expr>          — reusable condition
  RULE IF <cond> THEN <action> [AS x] — conditional rule
  DEFAULT <action>                    — fallback action
  INCLUDE <path.geo>                  — import file

CONDITIONS:
  family= mask= mask_in=             — identity
  tick>= tick< tick%= tick_in=        — time
  depth>= depth< depth= depth_in=    — tree depth
  active= active>= active<=          — popcount
  nb_N= nb_any= nb_count= nb_count_gte=  — neighbor family
  nb_prog_N= nb_prog_any= nb_prog_count= nb_prog_gte=  — neighbor program
  own_prog=                           — self program
  random<                             — probability
  var_<n>>= var_<n>= var_<n><         — cell variables
  signal=                             — inter-cell signals
  ALWAYS                              — catch-all
  AND OR BUT NOT ( )                  — combinators

ACTIONS:
  ADVANCE [N]  HOLD  GATE_ON  GATE_OFF
  SWITCH <FAM>  SET <BITS>
  ROTATE_CW  ROTATE_CCW  FLIP_H  FLIP_V
  SET_VAR <n> <v>  INCR_VAR <n> [d]  EMIT <sig>
  CALL <prog>  PROG <prog>  PLURALITY [N]
  action + action + ...               — composite
```

## Families

```
Y_LOOP:    1000 → 0100 → 0010 → 0001 → ...   (single quadrant rotates)
X_LOOP:    1100 → 0101 → 0011 → 1010 → ...   (pair cycles)
Z_LOOP:    0111 → 1011 → 1101 → 1110 → ...   (three-quadrant sweep)
DIAG_LOOP: 1001 ↔ 0110                        (diagonal toggle)
GATE:      0000, 1111                          (fixed points)
```
