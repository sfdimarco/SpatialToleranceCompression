# Showcase Content Library Guide

## Overview

This document describes the `.geo` script content library created for the BinaryQuadTree Showcase application. The library contains **14 scripts** organized into three categories demonstrating self-organizing systems.

---

## Content Structure

```
examples/
├── animation/          # Character animation solver scripts
│   ├── walk_cycle.geo
│   ├── idle_breathe.geo
│   ├── attack_swing.geo
│   ├── jump_arc.geo
│   └── morph_shape.geo
├── terrain/            # Game terrain generation scripts
│   ├── heightmap.geo
│   ├── biomes.geo
│   ├── caves.geo
│   ├── rivers.geo
│   └── erosion.geo
└── selforg/            # Self-organizing pattern scripts
    ├── voronoi.geo
    ├── maze.geo
    ├── flow_field.geo
    └── reaction_diffusion.geo
```

---

## Animation Scripts

### walk_cycle.geo
**Purpose:** Generate 8-frame character walk cycle for sprite sheets

| Property | Value |
|----------|-------|
| **Frames** | 4 (looping) |
| **Grid Mode** | No |
| **Depth** | 4+ (body, limbs, feet) |
| **Key Concepts** | Phase offsets, depth layering, loop family cycling |

**Usage:**
```bash
python Playground.py --geo examples/animation/walk_cycle.geo --depth 4
```

**Output:** Four-phase walk cycle with:
- Body core leading the motion
- Arms swinging opposite to legs
- Legs following with 1-tick delay
- Feet planting and lifting pattern

**Game Integration:**
- Export as PNG sequence for sprite sheet
- Use `attack_hit` signal for hit detection frame

---

### idle_breathe.geo
**Purpose:** Natural character breathing for idle animation

| Property | Value |
|----------|-------|
| **Frames** | 18 (full breath cycle) |
| **Grid Mode** | No |
| **Depth** | 4 (chest, belly, shoulders, head) |
| **Key Concepts** | Cell variables, conditional gating, subtle motion |

**Usage:**
```bash
python Playground.py --geo examples/animation/idle_breathe.geo --depth 4
```

**Output:** Breathing cycle with:
- Inhale (6 frames) → Hold (2) → Exhale (8) → Pause (3)
- Belly secondary motion
- Shoulder roll relaxation
- Head bobbing
- Random eye blinking

---

### attack_swing.geo
**Purpose:** Melee attack animation with windup and follow-through

| Property | Value |
|----------|-------|
| **Frames** | 30 |
| **Grid Mode** | No |
| **Depth** | 4+ (blade, handle, arm, body) |
| **Key Concepts** | Precise timing, ROTATE/FLIP transforms, signal emission |

**Usage:**
```bash
python Playground.py --geo examples/animation/attack_swing.geo --depth 4
```

**Phases:**
1. **Windup** (0-8): Telegraph the attack
2. **Strike** (9-14): Fast forward swing
3. **Impact** (15-20): Hit frame with shake
4. **Recovery** (21-29): Return to guard

**Game Integration:**
- `attack_hit` signal emitted on contact frame (tick 14)
- Export frames 9-14 for active attack frames

---

### jump_arc.geo
**Purpose:** Jump animation with parabolic arc trajectory

| Property | Value |
|----------|-------|
| **Frames** | 24 |
| **Grid Mode** | No |
| **Depth** | 4 (body, legs, arms, head) |
| **Key Concepts** | Squash/stretch, timing, arc simulation |

**Usage:**
```bash
python Playground.py --geo examples/animation/jump_arc.geo --depth 4
```

**Phases:**
1. **Crouch** (0-5): Prepare for jump
2. **Launch** (6-8): Explosive takeoff (squash)
3. **Ascent** (9-14): Rising arc (stretch)
4. **Peak** (15-17): Hang time at apex
5. **Descent** (18-21): Falling
6. **Landing** (22-23): Impact absorption

**Signals:** `jump_start`, `jump_peak`, `jump_land`

---

### morph_shape.geo
**Purpose:** Shape transformation animation (circle ↔ square)

| Property | Value |
|----------|-------|
| **Frames** | 32 |
| **Grid Mode** | No |
| **Depth** | 3+ (outer, mid, inner rings) |
| **Key Concepts** | Interpolation, smooth transitions, depth-based resolution |

**Usage:**
```bash
python Playground.py --geo examples/animation/morph_shape.geo
```

**Phases:**
1. **Circle** (0-7): Round form
2. **Rounded Square** (8-15): Transition forming
3. **Square** (16-23): Sharp corners
4. **Morph Back** (24-31): Softening to circle

---

## Terrain Scripts

### heightmap.geo
**Purpose:** Multi-octave noise terrain with erosion

| Property | Value |
|----------|-------|
| **Ticks** | 60+ |
| **Grid Mode** | Yes (8x8+) |
| **Depth** | 0-6 (elevation bands) |
| **Key Concepts** | Noise seeding, erosion smoothing, river carving |

**Usage:**
```bash
python Playground.py --geo examples/terrain/heightmap.geo --grid --depth 4
```

**Phases:**
1. **Noise Seeding** (0-15): Random elevation points
2. **Erosion Smoothing** (16-40): Natural terrain formation
3. **River Carving** (41-60): Water flow channels

**Output Variables:**
- `var_elev`: Elevation (0-10)
- `var_flow`: Water flow (0+)
- `var_age`: Terrain age

**Export:** JSON heightmap with elevation data

---

### biomes.geo
**Purpose:** Biome assignment by elevation and moisture

| Property | Value |
|----------|-------|
| **Ticks** | 100+ |
| **Grid Mode** | Yes (8x8+) |
| **Depth** | 0-6 (elevation) |
| **Key Concepts** | Multi-variable conditions, neighbor propagation |

**Usage:**
```bash
python Playground.py --geo examples/terrain/biomes.geo --grid --depth 4
```

**Biome Types:**
| Biome | Conditions | Mask |
|-------|------------|------|
| Snow | depth >= 5 | 1111 |
| Tundra | depth 4-5, wet <= 3 | 1001 |
| Taiga | depth 3-4, wet 4-7 | 1100 |
| Forest | depth 2-3, wet >= 7 | 0111 |
| Grassland | depth 1-2, wet 4-6 | 1000 |
| Desert | depth 1-2, wet <= 3 | 0100 |
| Swamp | depth 0, wet >= 8 | 0110 |
| Beach | depth 0, wet 4-7 | 1010 |
| Ocean | depth 0 | 0001 |

**Export:** JSON biome map with region IDs

---

### caves.geo
**Purpose:** Cellular automata cave generation

| Property | Value |
|----------|-------|
| **Ticks** | 50+ |
| **Grid Mode** | Yes (8x8+) |
| **Depth** | 0 (border) |
| **Key Concepts** | Birth/survival rules, smoothing, feature refinement |

**Usage:**
```bash
python Playground.py --geo examples/terrain/caves.geo --grid --depth 3
```

**Phases:**
1. **Noise Seeding** (0-5): 45% walls
2. **Cellular Smoothing** (6-20): Birth=5+, Survive=4+
3. **Cave Expansion** (21-35): Widen corridors
4. **Feature Refinement** (36-50): Remove artifacts

**Output:** Walkable cave map (GATE_OFF = floor, GATE_ON = wall)

**Features:** Pillars, pools, stalactites, stalagmites

---

### rivers.geo
**Purpose:** River network with watershed carving

| Property | Value |
|----------|-------|
| **Ticks** | 70+ |
| **Grid Mode** | Yes (8x8+) |
| **Depth** | 0-6 (elevation) |
| **Key Concepts** | Flow accumulation, watershed carving, delta formation |

**Usage:**
```bash
python Playground.py --geo examples/terrain/rivers.geo --grid --depth 4
```

**Phases:**
1. **Rainfall** (0-10): Water sources at peaks
2. **Flow Accumulation** (11-30): Tributaries merge
3. **River Carving** (31-50): Channel erosion
4. **Delta Formation** (51-70): Ocean deltas

**Features:** Waterfalls, rapids, oxbow lakes, distributaries

---

### erosion.geo
**Purpose:** Hydraulic erosion simulation

| Property | Value |
|----------|-------|
| **Ticks** | 100+ |
| **Grid Mode** | Yes (8x8+) |
| **Depth** | 0-6 (elevation) |
| **Key Concepts** | Sediment transport, terrain aging, feature formation |

**Usage:**
```bash
python Playground.py --geo examples/terrain/erosion.geo --grid --depth 4
```

**Phases:**
1. **Initial Terrain** (0-20): Rainfall on mountains
2. **Sediment Transport** (21-50): Pickup and deposition
3. **Valley Deepening** (51-80): Erosion carving
4. **Maturation** (81-100): Equilibrium

**Features:** Canyons, mesas, buttes, alluvial fans, floodplains

---

## Self-Organizing Scripts

### voronoi.geo
**Purpose:** Voronoi diagram generation

| Property | Value |
|----------|-------|
| **Ticks** | 80+ |
| **Grid Mode** | Yes (8x8+) |
| **Depth** | 0 |
| **Key Concepts** | Region growth, territory competition, signal propagation |

**Usage:**
```bash
python Playground.py --geo examples/selforg/voronoi.geo --grid
```

**Process:**
1. **Seed Placement** (0-10): 4-8 random seeds
2. **Region Growth** (11-50): Signal propagation
3. **Boundary Formation** (51-80): Stable boundaries

**Regions:** A (red), B (green), C (blue), D (gold)

**Applications:** Territory maps, biome regions, influence zones

---

### maze.geo
**Purpose:** Solvable maze generation

| Property | Value |
|----------|-------|
| **Ticks** | 70+ |
| **Grid Mode** | Yes (8x8+) |
| **Depth** | 0 (border) |
| **Key Concepts** | Constraint-based growth, path connectivity |

**Usage:**
```bash
python Playground.py --geo examples/selforg/maze.geo --grid
```

**Phases:**
1. **Border Walls** (0-10): Outer boundary
2. **Wall Growth** (11-30): Internal walls
3. **Path Widening** (31-50): Corridor formation
4. **Dead-end Removal** (51-70): Optional simplification

**Output:** Perfect maze (one path between any two points)

**Features:** Chambers, pillars, secret passages

---

### flow_field.geo
**Purpose:** Flow field visualization with particle following

| Property | Value |
|----------|-------|
| **Ticks** | 100+ |
| **Grid Mode** | Yes (8x8+) |
| **Depth** | 0 (field), 1+ (particles) |
| **Key Concepts** | Vector field encoding, particle following, streamlines |

**Usage:**
```bash
python Playground.py --geo examples/selforg/flow_field.geo --grid
```

**Flow Patterns:**
- Vortex (circular)
- Wave (sinusoidal)
- Divergence (from center)
- Convergence (to center)

**Applications:** Wind/water currents, crowd steering, erosion direction

---

### reaction_diffusion.geo
**Purpose:** Turing pattern formation

| Property | Value |
|----------|-------|
| **Ticks** | 200+ |
| **Grid Mode** | Yes (8x8+) |
| **Depth** | 0 |
| **Key Concepts** | Activator-inhibitor dynamics, emergent patterns |

**Usage:**
```bash
python Playground.py --geo examples/selforg/reaction_diffusion.geo --grid
```

**Pattern Types (cycle every 200 ticks):**
1. **Spots** (0-49): Leopard-like dots
2. **Stripes** (50-99): Zebra-like bands
3. **Labyrinth** (100-149): Coral-like maze
4. **Waves** (150-199): Oscillating fronts

**Variables:** `var_activator`, `var_inhibitor`

**Applications:** Texture synthesis, terrain detail, organic patterns

---

## Quick Reference

### By Use Case

| Use Case | Recommended Scripts |
|----------|---------------------|
| **Character Sprite Sheet** | `walk_cycle.geo`, `idle_breathe.geo`, `attack_swing.geo` |
| **Terrain Heightmap** | `heightmap.geo`, `erosion.geo` |
| **Biome Map** | `biomes.geo`, `voronoi.geo` |
| **Cave System** | `caves.geo` |
| **River Network** | `rivers.geo` |
| **Maze/Level** | `maze.geo` |
| **Organic Texture** | `reaction_diffusion.geo` |
| **Flow Visualization** | `flow_field.geo` |

### By Complexity

| Level | Scripts |
|-------|---------|
| **Beginner** | `walk_cycle.geo`, `morph_shape.geo`, `voronoi.geo` |
| **Intermediate** | `attack_swing.geo`, `jump_arc.geo`, `caves.geo`, `maze.geo` |
| **Advanced** | `heightmap.geo`, `biomes.geo`, `rivers.geo`, `erosion.geo`, `reaction_diffusion.geo` |

### By Grid Mode

| Grid Mode Required | Scripts |
|---------------------|---------|
| **Yes** | All terrain/* and selforg/* scripts |
| **No** | All animation/* scripts |

---

## Export Guidelines

### Animation Export (PNG Sequence)
```bash
python GeoStudio.py --geo examples/animation/walk_cycle.geo --frames 30 --output exports/walk/
```

### Terrain Export (JSON)
```bash
python GeoStudio.py --geo examples/terrain/biomes.geo --frames 1 --output exports/biomes.json
```

### GIF Export
```bash
python GeoStudio.py --geo examples/selforg/reaction_diffusion.geo --gif exports/reaction.gif --frames 200
```

---

## Performance Recommendations

| Script Type | Recommended Depth | Grid Size | Speed |
|-------------|-------------------|-----------|-------|
| Animation | 4-5 | N/A | 5-10 tps |
| Terrain | 3-4 | 8x8 | 3-6 tps |
| Self-Organizing | 0-1 | 8x8 | 3-6 tps |
| Reaction-Diffusion | 0 | 8x8 | 6-10 tps |

---

## Troubleshooting

### Script not loading
- Ensure you're using `--grid` flag for terrain/selforg scripts
- Check depth is appropriate (3-4 for terrain, 4-5 for animation)

### Performance issues
- Reduce depth for terrain scripts (they're grid-based)
- Lower speed (ticks per second) for complex simulations

### Patterns not forming
- Some scripts need 50+ ticks to stabilize
- Reaction-diffusion needs 200+ ticks for full patterns
- Ensure grid mode is enabled for neighbor-dependent scripts
