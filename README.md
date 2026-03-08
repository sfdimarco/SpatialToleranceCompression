# Binary Quad-Tree Geometric Grammar Engine

A recursive spatial grammar system where **4-bit geometric opcodes** drive fractal geometry that rotates, pulses, spreads, and self-organises — programmable via the **`.geo` scripting language**.

<!-- Replace with a captured GIF of the running demo for visual impact -->
<!-- ![demo](media/demo.gif) -->

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/BinaryQuadTreeCPUTest.git
cd BinaryQuadTreeCPUTest
pip install -r requirements.txt

python BinaryQuadTreeTest.py                         # default: self-organising grid
python BinaryQuadTreeTest.py --demo spiral           # fractal family cycling
python BinaryQuadTreeTest.py --geo examples/stochastic.geo   # load any .geo file
python BinaryQuadTreeTest.py --list                  # see all built-in demos
```

## What Is This?

Every node in a recursive quadtree carries a **4-bit mask** — each bit maps to one quadrant of a square:

```
  bit 3 (8) = TL    bit 2 (4) = TR
  bit 0 (1) = BL    bit 1 (2) = BR
```

Active quadrants (bit = 1) are drawn and recursively subdivided, producing self-similar fractal patterns. The mask `1010` creates a diagonal; `1111` fills everything; `0000` is empty.

Masks are grouped into **loop families** that cycle deterministically:

| Family | Cycle | Visual |
|--------|-------|--------|
| **Y-loop** | `1000 → 0100 → 0010 → 0001` | Single quadrant rotates |
| **X-loop** | `1100 → 0101 → 0011 → 1010` | Adjacent pair cycles |
| **Z-loop** | `0111 → 1011 → 1101 → 1110` | Three-quadrant sweep |
| **Diag** | `1001 ↔ 0110` | Diagonal pair toggles |
| **Gate** | `0000`, `1111` | Fixed points |

On every tick, the mask advances one step in its loop — geometry rotates, sweeps, or toggles. The **grammar layer** adds conditional rules that control *how* masks evolve: switching families based on depth, time, neighbor state, probability, or custom variables.

## The `.geo` Language

`.geo` is a declarative scripting language for writing grammar programs. Rules fire in order — first match wins.

```geo
# spiral.geo — cycle through all four loop families
NAME   spiral
RULE   IF tick%8=0   THEN SWITCH Y_LOOP    AS beat-Y
RULE   IF tick%8=2   THEN SWITCH X_LOOP    AS beat-X
RULE   IF tick%8=4   THEN SWITCH Z_LOOP    AS beat-Z
RULE   IF tick%8=6   THEN SWITCH DIAG_LOOP AS beat-D
RULE   IF depth>=5   THEN GATE_ON          AS seal-deep
DEFAULT ADVANCE
```

Features include:
- **30+ condition types** — family, mask, tick, depth, neighbor state, probability, cell variables, inter-cell signals
- **17 action types** — advance, hold, gate, switch family, rotate/flip bits, set variables, emit signals, composite chaining
- **DEFINE** — reusable condition aliases
- **INCLUDE** — compose scripts from files
- **Parenthesised grouping** — `(A OR B) AND C`
- **Validation** — `validate_geo(text)` catches errors with line numbers

See [GEO_LANGUAGE.md](GEO_LANGUAGE.md) for the full language reference.

## Examples

**35 example scripts** are included in the [`examples/`](examples/) folder, organized by category:

### Core Grammar Demos
| Script | Description |
|--------|-------------|
| [`spiral.geo`](examples/spiral.geo) | Beats through all four families on an 8-tick cycle |
| [`pulse_depth.geo`](examples/pulse_depth.geo) | Pulses gate-on every 10 ticks; deep cells lock to Z-loop |
| [`nb_spread.geo`](examples/nb_spread.geo) | Neighbor-aware contagion — Y-loop spreads to X-loop (Grid mode) |
| [`vote_example.geo`](examples/vote_example.geo) | Program-identity voting with PLURALITY action |
| [`rotate_mirror.geo`](examples/rotate_mirror.geo) | ROTATE_CW and FLIP_H with DEFINE aliases and parentheses |
| [`stochastic.geo`](examples/stochastic.geo) | Probabilistic rules — random flashes and family jumps |
| [`heat_spread.geo`](examples/heat_spread.geo) | Cell variables — accumulate "heat", change family at thresholds |
| [`signal_wave.geo`](examples/signal_wave.geo) | Inter-cell signals — EMIT/signal cascading waves |
| [`depth_layers.geo`](examples/depth_layers.geo) | Range conditions — different behavior per depth layer |
| [`conway_life.geo`](examples/conway_life.geo) | Conway's Game of Life approximation |
| [`mask_set.geo`](examples/mask_set.geo) | mask_in conditions and multi-step ADVANCE |
| [`composite.geo`](examples/composite.geo) | Composite actions — chain SWITCH + EMIT + SET_VAR |

### Animation Scripts
| Script | Description |
|--------|-------------|
| [`animation/idle_breathe.geo`](examples/animation/idle_breathe.geo) | Character breathing cycle with inhale/exhale phases |
| [`animation/attack_swing.geo`](examples/animation/attack_swing.geo) | Melee attack with windup, strike, impact, recovery |
| [`animation/jump_arc.geo`](examples/animation/jump_arc.geo) | Jump animation with parabolic trajectory |
| [`animation/morph_shape.geo`](examples/animation/morph_shape.geo) | Shape morphing (circle to square) |
| [`animation/walk_cycle.geo`](examples/animation/walk_cycle.geo) | Character walk cycle |

### Terrain Generation
| Script | Description |
|--------|-------------|
| [`terrain/heightmap.geo`](examples/terrain/heightmap.geo) | Multi-octave noise terrain with erosion |
| [`terrain/biomes.geo`](examples/terrain/biomes.geo) | Biome assignment by elevation and moisture |
| [`terrain/caves.geo`](examples/terrain/caves.geo) | Cellular automata cave generation |
| [`terrain/rivers.geo`](examples/terrain/rivers.geo) | River network with flow accumulation |
| [`terrain/erosion.geo`](examples/terrain/erosion.geo) | Hydraulic erosion simulation |

### Self-Organization Patterns
| Script | Description |
|--------|-------------|
| [`selforg/voronoi.geo`](examples/selforg/voronoi.geo) | Voronoi diagram generation |
| [`selforg/maze.geo`](examples/selforg/maze.geo) | Maze generation via wall growth |
| [`selforg/flow_field.geo`](examples/selforg/flow_field.geo) | Flow field visualization |
| [`selforg/reaction_diffusion.geo`](examples/selforg/reaction_diffusion.geo) | Turing patterns (spots, stripes) |

### Cosmos Simulations
| Script | Description |
|--------|-------------|
| [`cosmos_sim.geo`](examples/cosmos_sim.geo) | Cosmic evolution simulation |
| [`cosmos_sandbox.geo`](examples/cosmos_sandbox.geo) | Black hole collisions & gravitational waves |
| [`galaxy_generator.geo`](examples/galaxy_generator.geo) | Procedural galaxy generation |
| [`gravity_cosmos.geo`](examples/gravity_cosmos.geo) | Gravitational particle simulation |

### Other Examples
| Script | Description |
|--------|-------------|
| [`forest_fire.geo`](examples/forest_fire.geo) | Forest fire spread simulation |
| [`ecosystem.geo`](examples/ecosystem.geo) | Predator-prey ecosystem |
| [`dungeon_generator.geo`](examples/dungeon_generator.geo) | Rogue-like dungeon generation |
| [`combat_encounters.geo`](examples/combat_encounters.geo) | Combat encounter generation |

Run any example:

```bash
python BinaryQuadTreeTest.py --geo examples/spiral.geo
python BinaryQuadTreeTest.py --geo examples/conway_life.geo --depth 4
python BinaryQuadTreeTest.py --geo examples/terrain/caves.geo --grid
python BinaryQuadTreeTest.py --geo examples/selforg/voronoi.geo --grid
```

## All Demos

Beyond `.geo` script demos, several built-in visualisations showcase different aspects of the system:

```bash
python BinaryQuadTreeTest.py                        # self-organising zone boundaries
python BinaryQuadTreeTest.py --self-org              # same as default
python BinaryQuadTreeTest.py --grid                  # neighbor-wave propagation
python BinaryQuadTreeTest.py --multi-grid quadrants  # multi-zone phase-shifted regions
python BinaryQuadTreeTest.py --multi-grid rings      # concentric zone rings
python BinaryQuadTreeTest.py --lab                   # loop-family reference (2x3 panel)
python BinaryQuadTreeTest.py --grammar               # grammar rule comparison (2x2 panel)
```

Common flags: `--depth N` (recursion depth, default 6), `--speed N` (ticks/second, default 3.0), `--mask BITS` (starting mask, default 1000).

## How It Works

The system has three layers:

**1. Mask Engine** — 16 possible 4-bit values partitioned into five loop families. Each family forms a closed cycle. `ADVANCE` steps forward one position. Masks never escape their family unless a rule explicitly switches them.

**2. Grammar / Programs** — An ordered list of `IF condition THEN action` rules. Conditions compose with `AND`, `OR`, `BUT`, `NOT`, and parentheses. First matching rule fires. This gives Turing-complete control over geometry evolution — branching on state, time, depth, and spatial context.

**3. Grid / Cellular Automaton** — An N×M grid of quadtree roots, each with its own program. Before each cell steps, its cardinal neighbors' masks and programs are injected as context. Cells can react to neighbors, switch programs, emit signals, and accumulate variables. All cells snapshot before stepping — same-tick semantics prevent order-dependent artifacts.

The `.geo` parser compiles script text into `Program` objects via `parse_geo_script()`. Programs drive the grammar layer. The grid layer orchestrates spatial interaction. Everything is contained in a single Python file with one external dependency (matplotlib).

## Using From Python

```python
from BinaryQuadTreeTest import (
    parse_geo_script, load_geo, validate_geo,
    Node, Grid, expand_active, draw_frame
)

# Parse and run
prog = load_geo("examples/spiral.geo")
root = Node(0.0, 0.0, 1.0, 0, 0b1000)
for tick in range(100):
    prog.step_tree(root, tick)

# Validate
errors = validate_geo(open("my_script.geo").read())
for err in errors:
    print(f"Line {err.line}: {err.message}")
```

## License

[MIT](LICENSE)
