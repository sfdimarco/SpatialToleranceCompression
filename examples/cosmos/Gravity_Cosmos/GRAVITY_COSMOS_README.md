# Gravity Cosmos Simulation

## Overview

A smooth, p5.js-inspired gravitational particle simulation powered by `.geo` scripts. This creates a cosmic cosmos with:

- **Smooth particle motion** with velocity-based movement
- **Gravitational attraction** between particles
- **Orbital mechanics** simulating planetary motion
- **Particle trails** for visual flow
- **Glow effects** for massive bodies

## Files

- `gravity_cosmos.geo` - The .geo script defining cosmic behavior rules
- `gravity_cosmos_sim.py` - Pygame visualizer with smooth rendering

## Run

```bash
cd d:\CodexTest\BinaryQuadTreeCPUTest
python examples\gravity_cosmos_sim.py
```

### Options

```bash
# Custom window size
python examples\gravity_cosmos_sim.py --width 1280 --height 720

# Adjust particle count
python examples\gravity_cosmos_sim.py --particles 300

# Change FPS
python examples\gravity_cosmos_sim.py --fps 30
```

## Controls

| Key/Action | Effect |
|------------|--------|
| **Space** | Pause/Resume simulation |
| **C** | Clear all particles (except heavy masses) |
| **R** | Reset simulation |
| **G** | Toggle gravity on/off |
| **Left Click** | Add new particle at cursor |
| **Esc** | Quit |

## Particle Types

| Type | Color | Mass | Behavior |
|------|-------|------|----------|
| **Heavy** | Red | 15 | Gravitational anchors, slow moving |
| **Orbiter** | Teal | 3-6 | Orbit around heavy masses |
| **Light** | Yellow | 1-3 | Fast moving, long trails |
| **Dark Matter** | Purple | 6-10 | Invisible gravity sources |

## Physics

The simulation uses Newtonian gravity:

```
F = G * m1 * m2 / r²
```

Where:
- `G = 0.8` (gravitational constant)
- `m1, m2` = particle masses
- `r` = distance between particles

Particles also have:
- **Velocity damping** (0.995) for stability
- **Trail rendering** showing motion history
- **Glow effects** proportional to mass

## How .geo Enhances the Simulation

The `.geo` script adds emergent behavior on top of the physics:

1. **Spawn Rules** - Control where and when particles appear
2. **State Transitions** - Particles change type based on neighbors
3. **Collision Events** - Mergers and bursts trigger visual effects
4. **Galaxy Formation** - Spiral arm patterns emerge from orbital dynamics

## Comparison to p5.js Version

| Feature | p5.js Original | .geo Enhanced |
|---------|---------------|---------------|
| Motion | Manual velocity integration | Quadtree grammar + physics |
| Spawning | Random/timed | Rule-based (.geo conditions) |
| Collisions | Simple distance check | Neighbor-aware grammar rules |
| Visual Style | Canvas 2D | Pygame with glow/trails |
| Emergence | Limited | High (cellular automata) |

## Tips

1. **Watch spiral formation** - Particles naturally form orbital patterns
2. **Add particles strategically** - Click near heavies to create orbiters
3. **Toggle gravity** - Press G to see particles drift freely
4. **Adjust G value** - Edit `self.G` in code for stronger/weaker gravity

## Screenshots

When running locally, you'll see:
- Red glowing centers (heavy masses)
- Teal particles orbiting in curved paths
- Yellow streaks (light particles with long trails)
- Subtle purple glows (dark matter influence)

## Export

To capture the simulation:

```bash
# Add video capture code or use screen recording
# Recommended: OBS Studio at 60fps
```

## Future Enhancements

- [ ] GIF/MP4 export
- [ ] Multiple galaxy presets
- [ ] Black hole visualization
- [ ] Sound synthesis from particle motion
- [ ] VR/3D mode
