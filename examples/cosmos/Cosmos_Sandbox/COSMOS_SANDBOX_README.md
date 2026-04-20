# Cosmos Sandbox v2 - Emergent Cosmic Life

## Overview

A **sandbox simulation game** where you discover and nurture balanced cosmic systems that can support emergent life forms. Built with physics inspired by charged-gravity simulators and powered by `.geo` rules.

## Run

```bash
cd d:\CodexTest\BinaryQuadTreeCPUTest
python examples\cosmos_sandbox.py
```

---

## Gameplay

### Objective

Create and maintain **habitable zones** where life can emerge and thrive:

1. **Balance particle charges** (+/-) to create stable regions
2. **Manage temperature** through particle density
3. **Watch for black holes** - they disrupt habitable zones
4. **Nurture life forms** once they emerge

### Winning Condition

There is no "win" - this is a **sandbox**. Your goals:
- Maximize life forms
- Create stable multi-generational systems
- Observe emergent behaviors
- Experiment with different configurations

---

## Controls

| Input | Action |
|-------|--------|
| **Left Click** | Add particle (random charge) |
| **Right Click** | Add black hole |
| **Space** | Pause/Resume |
| **H** | Toggle habitable zone overlay (green rings) |
| **L** | Toggle life overlay |
| **R** | Reset simulation |
| **Esc** | Quit |

---

## Physics System

### Charged Particles

| Property | Positive (+) | Negative (-) |
|----------|--------------|--------------|
| **Color** | Red (#ff6b6b) | Teal (#4ecdc4) |
| **Gravity** | Attracts all | Attracts all |
| **Like-charge** | +2.5x boost | +2.5x boost |
| **Behavior** | Clumps with + | Clumps with - |

### Gravity Formula

```
F = (G × m1 × m2 × boost) / r²

Where:
  G = 0.05 (gravitational constant)
  boost = 2.5 if same charge, else 1.0
```

### Fusion (E = mc²)

When **like-charged** particles get within 6 pixels:
1. They merge into one particle
2. Mass is conserved (m1 + m2)
3. Momentum is conserved
4. **Energy flare** releases: `E = m × c² / 5000`

### Black Hole Formation

Particles become black holes when:
- **Mass ≥ 400**
- They stop moving (infinite mass)
- Gain blue/yellow penumbra glow

---

## Temperature System

### Heating Sources

| Source | Temperature Increase |
|--------|---------------------|
| Nearby positive particles | +2 per 4 neighbors |
| Nearby negative particles | +2 per 4 neighbors |
| Fusion flare | +15 instant |

### Cooling

- Empty space: -1 per tick
- Minimum temp: 25°C

### Habitable Zone

Life can emerge when:
```
20 ≤ Temperature ≤ 40
20 ≤ Mass ≤ 100
Age > 100 ticks
```

---

## Emergent Life

### Life Formation

When conditions are right, particles develop life:
- **Base chance**: 2% per tick in habitable zone
- **Color**: Purple with glow
- **Behavior**: Responds to temperature

### Life Types

| Type | Color | Complexity |
|------|-------|------------|
| **Basic** | Purple (180,120,255) | 1 |
| **Complex** | Light purple (220,150,255) | 5 |

### Life Behaviors

- **Warming**: Increases local temp if too cold
- **Cooling**: Decreases local temp if too hot
- **Reproduction**: 3% chance when near other life

---

## Visual Effects

### Black Hole Penumbra

Black holes display layered glow:
1. **Core**: Black circle (radius based on mass)
2. **Inner halo**: Blue (100, 200, 255) - 14px
3. **Outer penumbra**: Yellow (255, 230, 80) - 28px

### Fusion Flare

When particles merge:
- Bright yellow flash
- Radius expands with energy
- Decays over time

### Trail Effect

- Semi-transparent fade overlay
- Creates motion trails
- 50 alpha per frame

---

## Statistics

Real-time stats displayed:

| Stat | Description |
|------|-------------|
| **Particles** | Current active count |
| **Black Holes** | Number of BH formed |
| **Life Forms** | Total living entities |
| **Habitable** | Zones in temp range |
| **FPS** | Frame rate (green if ≥55) |

---

## Strategies

### Creating Stable Systems

1. **Balanced charges** - Equal +/- creates stable orbits
2. **Spread mass** - Don't let one particle dominate
3. **Monitor temperature** - Watch for hot/cold spots
4. **Protect life zones** - Keep BH away from habitable areas

### Encouraging Life

1. Create medium-density regions
2. Maintain 20-40°C temperature
3. Avoid large fusion events near life
4. Let systems age (life needs 100+ ticks)

### Managing Black Holes

1. **Don't spam** - They disrupt orbits
2. **Place at edges** - Less disruptive
3. **Use as anchors** - Create orbiting systems
4. **Watch mass accumulation** - Remove if too big

---

## Emergent Behaviors

### Orbital Systems

Particles naturally form:
- **Binary pairs** (two particles orbiting)
- **Multi-body systems** (3+ particles)
- **Accretion disks** (around black holes)

### Spiral Arms

With enough particles:
- Spiral density waves form
- Rotate around central mass
- Create "galaxy" structures

### Life Clusters

Life tends to:
- Form colonies near each other
- Stabilize local temperature
- Self-regulate population

---

## Comparison: Original vs V2

| Feature | Original | V2 Sandbox |
|---------|----------|------------|
| **Goal** | Visual demo | Discover habitable systems |
| **Particles** | Static types | Dynamic charge/mass |
| **Physics** | Simple gravity | Charge-boosted gravity |
| **Fusion** | None | E=mc² flares |
| **Black Holes** | Visual only | Form from massive particles |
| **Temperature** | None | Full thermodynamic model |
| **Life** | None | Emergent in habitable zones |
| **Interaction** | Watch only | Click to add/manipulate |

---

## Performance

| Particle Count | FPS | Playable |
|----------------|-----|----------|
| 50-100 | 60 | ✅ Excellent |
| 100-200 | 55-60 | ✅ Great |
| 200-400 | 45-55 | ⚠️ Acceptable |
| 400+ | 30-45 | ⚠️ Challenging |

### Optimization Tips

- Keep particle count under 200 for best FPS
- Limit black holes (expensive rendering)
- Pause when not actively observing

---

## The .geo Connection

While physics is handled in Python for performance, the **design patterns come from `.geo`**:

### cosmos_sandbox.geo Rules

```geo
# Like-charge attraction boost
RULE IF is_positive AND nb_count_gte=Y_LOOP:2  
     THEN ADVANCE 2  AS like-boost-pos

# Fusion when close
RULE IF is_positive AND nb_count_gte=Y_LOOP:3  
     THEN SET 1111 + EMIT flare  AS fusion-pos

# Black hole formation
RULE IF var_mass>=400 AND NOT is_blackhole  
     THEN SET 1111  AS become-bh

# Life emergence
RULE IF habitable=1 AND random<0.02 AND tick>100
     THEN SET 1001 + SET_VAR life_type 1  AS spawn-life
```

These rules map directly to Python physics:
- `like-boost` → `LIKE_BOOST = 2.5`
- `fusion-pos` → `merge()` function
- `become-bh` → `BH_THRESHOLD = 400`
- `spawn-life` → `_check_life_emergence()`

---

## Future Enhancements

### Planned Features

- [ ] Save/load system states
- [ ] Multiple star systems
- [ ] Planetary formation
- [ ] Advanced life behaviors
- [ ] Ecosystem simulation
- [ ] Resource chains
- [ ] Victory conditions

### Experimental

- [ ] Multiplayer (shared simulation)
- [ ] VR mode
- [ ] Sound synthesis from particle motion
- [ ] Machine learning life AI
- [ ] Export to video/GIF

---

## Troubleshooting

### Low FPS

```bash
# Reduce window size
python examples\cosmos_sandbox.py --width 800 --height 600

# Or limit particles in code
START_COUNT = 40  # instead of 80
```

### Particles disappearing

- Check edge wrapping (they wrap, not vanish)
- Black holes may have consumed them
- Fusion merged them

### Life not spawning

- Check temperature (must be 20-40°C)
- Ensure particles are old enough (100+ ticks)
- Increase `LIFE_CHANCE` in code

---

## Credits

**Inspired by:**
- p5.js gravity simulations
- Conway's Game of Life
- Boids flocking simulation
- N-body physics simulators

**Built with:**
- Pygame for rendering
- `.geo` design patterns
- Newtonian physics (simplified)

---

## See Also

- [`cosmos_sim.py`](cosmos_sim.py) - Original cosmos visualizer
- [`gravity_cosmos_sim.py`](gravity_cosmos_sim.py) - Gravity-focused sim
- [`GEO_LANGUAGE.md`](../GEO_LANGUAGE.md) - .geo language reference
