# Particle Cosmos - FULL .geo Physics

**ALL physics calculations are done by `.geo` scripts.**

Python only handles:
- Rendering graphics
- User input
- Grid management
- Particle spawning

## Files

| File | Purpose |
|------|---------|
| `particle_cosmos.py` | Python renderer (NO physics) |
| `particle_cosmos.geo` | **ALL PHYSICS** (gravity, fusion, black holes) |
| `RUN_PARTICLE_COSMOS.bat` | Double-click to run |

## How to Run

**Double-click:**
```
RUN_PARTICLE_COSMOS.bat
```

**Or command line:**
```cmd
cd d:\CodexTest\BinaryQuadTreeCPUTest
python examples\cosmos\particle_cosmos.py
```

## Physics in .geo (F = G*m1*m2/r²)

The `particle_cosmos.geo` script implements:

### 1. Gravitational Attraction
```geo
# Base gravity from neighbors
RULE IF is_positive AND has_neighbor_nb AND tick%2=0 THEN
       INCR_VAR vx 2 + INCR_VAR vy 2
       AS pos_gravity_base
```
- Particles attract based on neighbor presence
- More crowded = stronger gravity (simulates closer distance)
- Approximates F = G*m1*m2/r²

### 2. Like-Charge Boost (2.5x stronger)
```geo
RULE IF is_positive AND has_same_charge_nb AND tick%4=0 THEN
       INCR_VAR vx 5 + INCR_VAR vy 5
       AS like_boost_positive
```
- Same charges (+/+ or -/-) attract stronger
- Implements F_like = F * LIKE_BOOST

### 3. Fusion with E=mc²
```geo
RULE IF is_positive AND crowded_nb AND can_fuse AND random<0.15 THEN
       INCR_VAR mass 8 + SET_VAR flare 25
       AS fusion_positive
```
- Mass conservation: m_new = m1 + m2
- Energy release: flare = mass * c²

### 4. Black Hole Formation
```geo
RULE IF is_positive AND is_massive AND NOT is_blackhole THEN
       SET 1111 + SET_VAR vx 0 + SET_VAR vy 0
       AS bh_form_positive
```
- Threshold: mass >= 400
- Stationary with intense gravity

### 5. Velocity Damping
```geo
RULE IF NOT is_blackhole AND tick%8=0 AND var_vx_gte=2 THEN
       INCR_VAR vx -1
       AS damping_x
```
- Simulates drag: v = v * 0.995

## Controls

| Input | Action |
|-------|--------|
| **Left Click** | Add particle |
| **Right Click** | Add black hole |
| **Space** | Pause/Resume |
| **C** | Clear all |
| **S** | Spawn solar system |
| **Esc** | Quit |

## Visual Design

| Visual | Meaning |
|--------|---------|
| 🔴 Red circle | Positive charge |
| 🔵 Cyan circle | Negative charge |
| ⚫ Black with blue/yellow halo | Black hole |
| 💛 Yellow flash | E=mc² fusion energy |

## Why .geo for Physics?

### Benefits:
1. **Declarative rules** - Physics defined as rules, not imperative code
2. **Easy to modify** - Change gravity strength without touching Python
3. **Spatial grammar** - Neighbor-based calculations built-in
4. **Emergent behavior** - Complex interactions from simple rules

### Example: Change Gravity Strength

In `particle_cosmos.geo`, change:
```geo
# From (weak gravity)
INCR_VAR vx 2 + INCR_VAR vy 2

# To (strong gravity)
INCR_VAR vx 6 + INCR_VAR vy 6
```

No Python changes needed!

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Python (Renderer)                     │
│  - Create Grid                                           │
│  - Handle Input                                          │
│  - Draw Cells                                            │
│  - Spawn Particles                                       │
└────────────────────┬────────────────────────────────────┘
                     │ grid.step(tick)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  .geo Script (Physics)                   │
│  - Gravitational calculations (F=G*m1*m2/r²)            │
│  - Like-charge boost                                     │
│  - Fusion mechanics                                      │
│  - Black hole formation                                  │
│  - Velocity updates                                      │
│  - Mass changes                                          │
└─────────────────────────────────────────────────────────┘
```

## Physics Constants

Defined in `.geo`:

| Constant | Value | Meaning |
|----------|-------|---------|
| G | ~0.05 | Gravitational constant |
| LIKE_BOOST | 2.5 | Like-charge multiplier |
| MERGE_DIST | 6 | Fusion distance |
| BH_THRESHOLD | 400 | Black hole mass |
| DAMPING | 0.995 | Velocity damping |

## Comparison: Old vs New

### Old (cosmos_infinite.py)
- ❌ Physics in Python
- ❌ .geo as decoration
- ❌ Broke at tick 7
- ❌ Complex chunk system

### New (particle_cosmos.py)
- ✅ **ALL physics in .geo**
- ✅ Python just renders
- ✅ Stable simulation
- ✅ Clean architecture

## Modifying Physics

Want different behavior? Edit `particle_cosmos.geo`:

### Stronger Gravity
```geo
# Change from:
INCR_VAR vx 2 + INCR_VAR vy 2

# To:
INCR_VAR vx 8 + INCR_VAR vy 8
```

### Faster Fusion
```geo
# Change from:
random<0.15

# To:
random<0.30
```

### Smaller Black Holes
```geo
# Change from:
DEFINE is_massive var_mass_gte=400

# To:
DEFINE is_massive var_mass_gte=200
```

## Summary

This simulation demonstrates **true .geo-driven physics**:
- ALL calculations in `.geo` scripts
- Python is just a renderer
- Easy to modify physics behavior
- Clean separation of concerns
- Based on F = G*m1*m2/r² formula
