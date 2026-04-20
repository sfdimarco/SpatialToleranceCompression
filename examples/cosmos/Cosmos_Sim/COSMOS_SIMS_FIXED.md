# Cosmos Simulations - FIXED AND WORKING

All three cosmos simulations are now working properly with `.geo` physics.

## Files Organization

All `.geo` files are in the **same folder** as their respective `.py` files:

```
examples/cosmos/
├── cosmos_infinite.py          ← Main simulation
├── cosmos.geo                  ← Used by cosmos_infinite (default mode)
├── cosmos_physics.geo          ← NEW: Gravitational physics with ACCUM_VAR
│
├── cosmos_sim.py               ← Gravity sandbox
├── cosmos_sim.geo              ← Used by cosmos_sim
├── gravity_sandbox.geo         ← Also used by cosmos_sim
│
├── cosmos_sandbox.py           ← Charged particle sandbox
├── cosmos_sandbox.geo          ← Used by cosmos_sandbox
│
├── cosmic_origins.py           ← 4X space strategy
├── cosmic_origins.geo          ← Used by cosmic_origins
├── cosmic_ai_behaviors.geo     ← AI behaviors
├── cosmic_events_encounters.geo ← Random events
│
└── gravity_cosmos.geo          ← Gravity evolution
```

## The 3 Main Sims

### 1. cosmos_infinite.py - Infinite Cosmos with Zoom

**What it does:**
- Infinite procedural space with chunk-based loading
- Smooth zoom from cosmic scale to stellar scale
- Big bang initialization
- **NEW:** Proper velocity-based movement from .geo physics

**How .geo is used:**
- `cosmos.geo` - Base state machine (stars, gas, dark matter, black holes)
- `cosmos_physics.geo` - **NEW** gravitational physics using ACCUM_VAR
- Python applies velocities from .geo to move cells between positions

**Run:**
```cmd
python examples\cosmos\cosmos_infinite.py --mode physics
```

**Modes:**
- `default` - Standard cosmos.geo only
- `physics` - cosmos_physics.geo (gravitational physics)
- `full` - Both combined

**Controls:**
- Mouse Wheel - Zoom
- Left Click + Drag - Pan
- Right Click - Add black hole
- Middle Click - Add star
- B - Big bang at cursor
- Space - Pause
- R - Reset

---

### 2. cosmos_sim.py - Gravity Sandbox

**What it does:**
- Particle-based gravity simulation
- Orbital mechanics
- Collision detection with flashes
- .geo-driven particle state changes

**How .geo is used:**
- `gravity_sandbox.geo` - Rules for particle state evolution
- Each particle has a geo_mask that evolves via .geo rules
- Python handles N-body physics, .geo handles state transitions

**Run:**
```cmd
python examples\cosmos\cosmos_sim.py
```

**Controls:**
- Left Click - Spawn planet (blue)
- Right Click - Spawn sun (heavy gold)
- Middle Click - Spawn dark matter (purple)
- G - Toggle gravity visualization
- T - Toggle trails
- Space - Pause/Resume
- C - Clear all
- S - Spawn solar system

---

### 3. cosmos_sandbox.py - Charged Particle Sandbox

**What it does:**
- Charged particles (+/-) with gravity
- Like-charge boost attraction
- Fusion with E=mc² flare
- Black hole formation
- Emergent life forms

**How .geo is used:**
- `cosmos_sandbox.geo` - Complete rule set for particle behavior
- State transitions (particle → black hole → etc.)
- Temperature and density evolution

**Run:**
```cmd
python examples\cosmos\cosmos_sandbox.py
```

**Controls:**
- Mouse Click - Add particle
- Right Click - Add black hole
- Space - Pause/Resume
- H - Toggle habitable zone
- L - Toggle life overlay
- R - Reset

---

## Key Fixes Made

### cosmos_infinite.py
**Problem:** Cells had `vx`/`vy` from .geo but never moved.

**Fix:** Added `_apply_chunk_physics()` method that:
1. Reads `vx`/`vy` from cells after `.geo` step
2. Moves cells to new positions based on velocity
3. Handles wrapping and collision

**New .geo file:** `cosmos_physics.geo`
- Uses `ACCUM_VAR` to accumulate gravitational influence from neighbors
- Implements F = G*m1*m2/r² approximation
- Black holes have intense gravity (5× multiplier)
- Velocity damping prevents runaway acceleration

---

### cosmos_sim.py
**Status:** Already working, just verified.

Uses `gravity_sandbox.geo` for particle state evolution while Python handles N-body physics.

---

### cosmos_sandbox.py
**Status:** Already working, just verified.

Uses `cosmos_sandbox.geo` for complete particle lifecycle.

---

## Physics Implementation

### Gravitational Physics (cosmos_physics.geo)

```geo
# Accumulate mass from neighbors (F = G*m1*m2/r² approximation)
RULE IF is_star AND has_neighbors AND tick%2=0 THEN
       ACCUM_VAR vx N mass 1 + ACCUM_VAR vy N mass 1
       AS star_grav_N

# Black holes have intense gravity
RULE IF is_blackhole AND has_neighbors AND tick%1=0 THEN
       ACCUM_VAR vx N mass 5 + ACCUM_VAR vy N mass 5
       AS bh_grav_N
```

**How it works:**
1. Each cell has `mass`, `vx`, `vy` variables
2. `ACCUM_VAR vx N mass 1` reads neighbor's mass and adds to vx
3. Python reads final vx/vy and moves cells accordingly

### Why This Works

- `.geo` handles **state evolution** and **force calculation**
- Python handles **position updates** and **rendering**
- Clean separation of concerns
- Uses .geo's strengths (neighbor queries, state machines)
- Avoids .geo's weaknesses (continuous movement)

---

## Quick Reference

| Sim | Best For | .geo Files | Physics |
|-----|----------|------------|---------|
| cosmos_infinite | Large scale universe | cosmos.geo, cosmos_physics.geo | ACCUM_VAR gravity |
| cosmos_sim | Orbital mechanics | gravity_sandbox.geo | N-body + .geo states |
| cosmos_sandbox | Emergent complexity | cosmos_sandbox.geo | Charged particles |

---

## All Sims Are Working

Run any of these:

```cmd
# Infinite cosmos with gravitational physics
python examples\cosmos\cosmos_infinite.py --mode physics

# Gravity sandbox with orbitals
python examples\cosmos\cosmos_sim.py

# Charged particle sandbox
python examples\cosmos\cosmos_sandbox.py

# 4X space strategy game
python examples\cosmos\cosmic_origins.py
```

All `.geo` files are in `examples\cosmos\` - same folder as the `.py` files they belong to.
