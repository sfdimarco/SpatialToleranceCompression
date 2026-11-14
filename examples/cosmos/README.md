# Cosmos Simulations

This folder contains space-themed simulations and games built with the Binary Quad-Tree Grammar Engine.

## Simulations

### 1. Cosmos Infinite (Recommended Start)
**File:** `cosmos_infinite.py`

An infinite space cosmos simulation with smooth zoom from galactic scale to individual stars.

**Features:**
- Infinite procedural space with chunk-based loading
- Smooth zoom (mouse wheel) from cosmic to stellar scale
- Big Bang initialization with inflation
- Emergent structure formation
- Black holes, stars, gas clouds, dark matter, gravitational waves

**Run:**
```bash
python examples/cosmos/cosmos_infinite.py
```

**Controls:**
- Mouse Wheel: Zoom in/out
- Left Click + Drag: Pan camera
- Right Click: Add black hole
- Middle Click: Add star
- B: Trigger Big Bang
- Space: Pause/Resume

---

### 2. Cosmic Origins (Space Conquest Game)
**File:** `cosmic_origins.py`

A Risk/Spore-style territorial conquest game where you command fleets and capture star systems.

**Features:**
- Turn-based fleet command
- Capture neutral, resource, and enemy systems
- AI opponent
- Resource systems produce more ships
- Fortified systems and capitals

**Run:**
```bash
python examples/cosmos/cosmic_origins.py
```

**Controls:**
- Left Click: Select system / Send fleets
- Right Click: Cancel selection
- Space: Pause
- R: Restart
- H: Toggle help

**Goal:** Capture all enemy systems to win!

---

### 3. Cosmos Sim / Gravity Sandbox (RECOMMENDED!)
**File:** `cosmos_sim.py`

A satisfying interactive gravity sandbox with beautiful orbital mechanics and .geo-driven behavior.

**Features:**
- N-body gravity simulation with realistic orbits
- Spawn suns, planets, dark matter, and particle swarms
- Collision detection with flash effects
- Beautiful particle trails and glow
- .geo rules for emergent behavior patterns
- Gravity visualization mode

**Run:**
```bash
python examples/cosmos/cosmos_sim.py
```

**Controls:**
- Left Click: Spawn planet (blue)
- Right Click: Spawn sun (heavy gold)
- Middle Click: Spawn dark matter (purple)
- Shift + Click: Spawn particle swarm
- G: Toggle gravity visualization lines
- T: Toggle trails
- Space: Pause/Resume
- C: Clear all
- S: Spawn solar system preset

**Fun Things to Try:**
1. Press S to spawn a solar system
2. Add more planets with left-click
3. Create binary suns with right-click
4. Watch dark matter bend orbits (middle-click)
5. Toggle gravity lines (G) to see forces

---

### 4. Gravity Cosmos Sim
**File:** `gravity_cosmos_sim.py`

A smooth particle gravity simulation with orbital mechanics.

**Features:**
- N-body gravity simulation
- Particle trails
- Galaxy formation
- Heavy masses, orbiters, light particles, dark matter

**Run:**
```bash
python examples/cosmos/gravity_cosmos_sim.py
```

**Controls:**
- Left Click: Add orbiter particle
- Right Click: Add heavy mass
- G: Toggle gravity visualization
- Space: Pause
- R: Reset

---

## .geo Scripts

Each simulation has a corresponding `.geo` script that defines its rules:

| Script | Description |
|--------|-------------|
| `cosmos.geo` | Main infinite cosmos rules (32 rules) |
| `cosmic_origins.geo` | Territory conquest mechanics (31 rules) |
| `cosmos_sim.geo` | Quadtree visual patterns (14 rules) |
| `gravity_cosmos.geo` | Particle gravity rules (15 rules) |

## Requirements

```bash
pip install pygame
```

## Quick Start

For the best experience, start with **Cosmos Infinite**:

```bash
cd d:\CodexTest\BinaryQuadTreeCPUTest
python examples\cosmos\cosmos_infinite.py
```

Then try the **Cosmic Origins** game for strategic gameplay:

```bash
python examples\cosmos\cosmic_origins.py
```

## Architecture

All simulations use:
- **pygame** for rendering and input
- **BinaryQuadTreeTest** engine for `.geo` script execution
- **Cell variables** for state tracking (mass, temp, hp, ships, etc.)
- **Neighbor rules** for emergent behavior

## Troubleshooting

### Low FPS
- Reduce window size
- Lower recursion depth (in cosmos_sim)
- Close other applications

### Won't Start
```bash
pip install --upgrade pygame
```

### .geo Script Errors
Check syntax in `.geo` files:
- Use `SET 1111` not `GATE_ON`
- Use `SET 0000` not `GATE_OFF`
- Use `var_name>=value` not `var_name>value`

## License

MIT License - See main repository LICENSE file
