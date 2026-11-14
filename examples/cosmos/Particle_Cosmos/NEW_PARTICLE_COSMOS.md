# NEW: Particle Cosmos Simulation

## What I Created

A **new clean particle simulation** based on your p5.js `cosmos_sim_v2.js` project:

| File | Purpose |
|------|---------|
| `particle_cosmos.py` | Main Python simulation |
| `particle_cosmos.geo` | .geo physics rules |
| `RUN_PARTICLE_COSMOS.bat` | Double-click to run |

## How To Run

**Double-click this file:**
```
d:\CodexTest\BinaryQuadTreeCPUTest\examples\cosmos\RUN_PARTICLE_COSMOS.bat
```

Or from command line:
```cmd
cd d:\CodexTest\BinaryQuadTreeCPUTest
python examples\cosmos\particle_cosmos.py
```

## What It Does

This is a **smooth particle gravity simulator** with:

- ✅ Gravitational attraction between all particles
- ✅ Like-charge boost (+/+ and -/- attract stronger)
- ✅ Fusion on collision (particles merge)
- ✅ E=mc² flare effect on merge
- ✅ Black hole formation (mass >= 400)
- ✅ Black holes with blue/yellow penumbra
- ✅ Continuous particle emitter from center
- ✅ Edge wrapping for smooth orbits

## Controls

| Input | Action |
|-------|--------|
| Left Click | Add particle |
| Right Click | Add black hole |
| Space | Pause/Resume |
| C | Clear all |
| S | Spawn solar system |
| Esc | Quit |

## Visual Design

- **Red circles** = Positive charge particles
- **Cyan circles** = Negative charge particles
- **Black with blue/yellow halo** = Black hole
- **Yellow flash** = Fusion energy release

## Why This Works Better

The old `cosmos_infinite.py`:
- ❌ Broke at tick 7
- ❌ Complex chunk system caused issues
- ❌ Not based on your p5.js design

The new `particle_cosmos.py`:
- ✅ Stable, smooth simulation
- ✅ Simple particle list (no complex chunks)
- ✅ Directly based on your p5.js code
- ✅ .geo scripts handle physics rules
- ✅ All files in one organized folder

## Physics Constants

From your p5.js original:

```python
G_CONST = 0.05          # Weaker gravity for smooth motion
LIKE_BOOST = 2.5        # Extra attraction for like charges
MERGE_DIST = 6          # Fusion radius
BH_THRESHOLD = 400      # Mass for black hole
EMIT_RATE = 45          # Frames between emissions
START_COUNT = 80        # Initial particles
C_SIM = 30              # "Speed of light" for E=mc²
```

## .geo Script Integration

The `particle_cosmos.geo` file defines rules for:
1. Gravity attraction
2. Like-charge boost
3. Fusion behavior
4. Black hole formation
5. Flare decay

This means you can **modify the physics** by editing the `.geo` file without touching the Python code!

## Folder Organization

All files are in one place:
```
examples/cosmos/
├── particle_cosmos.py          ← Main simulation
├── particle_cosmos.geo         ← Physics rules
├── RUN_PARTICLE_COSMOS.bat     ← Double-click to run
└── PARTICLE_COSMOS_README.md   ← Full documentation
```

No scattered files. No confusion. Everything works together.
