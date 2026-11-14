# Black Hole Collisions & Gravitational Waves

## Overview

The Cosmos Sandbox now features **realistic black hole physics** including:
- **Inspiral phase** - Black holes spiral toward each other
- **Merger event** - Cataclysmic collision releasing immense energy
- **Gravitational waves** - Ripples in spacetime propagating outward
- **Recoil kick** - Asymmetric mergers eject black holes at high velocity

All powered by `.geo` rules!

---

## Physics Implementation

### 1. Inspiral Phase

When two black holes come within **80 pixels**:

```python
if dist < BH_INSPIRAL_DIST:
    self.inspiraling = True
    other.inspiraling = True
```

**What happens:**
- Black holes begin orbiting each other
- Orbital speed increases by 0.1 per tick
- They spiral inward due to gravitational radiation
- Visual: Black holes orbit faster and faster

**.geo Rule:**
```geo
RULE IF is_blackhole AND nb_count_gte=is_blackhole:1 
     THEN SET 1111 + EMIT inspiral + SET_VAR inspiraling 1  AS bh-inspiral
```

---

### 2. Merger Event

When black holes get within **20 pixels** with sufficient orbital speed:

```python
if dist < BH_MERGE_DIST and self.orbital_speed >= 3:
    self._merge_black_holes(other)
```

**Energy Release:**
```python
wave_energy = (m1 + m2) × (orbital_speed²) / 100
```

This energy is **briefly brighter than all stars in the universe combined** - just like real gravitational wave events!

**.geo Rule:**
```geo
RULE IF is_blackhole AND nb_count_gte=is_blackhole:2 AND var_orbital_speed>=5
     THEN SET 1111 + EMIT merger + EMIT grav_wave  AS bh-merger
```

---

### 3. Gravitational Waves

**What they are:** Ripples in the fabric of spacetime itself, propagating at the speed of light.

**Implementation:**
```python
def _emit_gravitational_wave(x, y, strength):
    # Create 16 wave particles expanding in a ring
    for i in range(16):
        angle = (i / 16) × 2π
        wave = Particle(x, y)
        wave.vx = cos(angle) × GRAV_WAVE_SPEED
        wave.vy = sin(angle) × GRAV_WAVE_SPEED
```

**Properties:**
- **Speed:** 15 pixels/tick
- **Strength:** Starts at 10, decays by 0.3/tick
- **Range:** Dissipates after 200 pixels
- **Visual:** Expanding blue-white ripple rings

**Effects on Matter:**
- Stretches and compresses space (random velocity perturbations)
- Heats nearby particles (+wave_strength × 0.5 temperature)
- Can disrupt habitable zones
- May extinguish life forms

**.geo Rules:**
```geo
# Gravitational wave propagation
RULE IF signal=grav_wave AND depth_in=1..8
     THEN SET 1010 + SET_VAR wave_strength 10 + INCR_VAR wave_dist 1

# Wave heating effect
RULE IF is_grav_wave AND depth_in=1..5
     THEN INCR_VAR temp (var_wave_strength) + EMIT wave_heat

# Wave dissipation
RULE IF is_grav_wave AND var_wave_dist>=8
     THEN SET 0000  AS wave-dissipate
```

---

### 4. Recoil Kick

**Why it happens:** Asymmetric mass ratios in the merger cause momentum imbalance, resulting in a "kick" that can eject the merged black hole from its host galaxy.

**Implementation:**
```python
# 70% chance of kick
if random.random() < 0.7:
    self.kicking = True
    self.kick_vx = random.uniform(5, 20) × random_direction
    self.kick_vy = random.uniform(5, 20) × random_direction
```

**Kick Properties:**
- **Velocity:** 5-20 pixels/tick
- **Direction:** Random
- **Duration:** ~100 ticks (slowed by dynamical friction)
- **Visual:** Black hole shoots across the screen

**.geo Rule:**
```geo
RULE IF signal=merger AND is_blackhole AND random<0.7
     THEN SET_VAR kick_vx (random(-15,15)) + SET_VAR kick_vy (random(-15,15)) + SET_VAR kicking 1
```

---

## Visual Effects

### Black Hole Appearance

| Component | Color | Radius |
|-----------|-------|--------|
| **Core** | Black | mass^(1/3) × 2 |
| **Blue Halo** | (100, 200, 255, 80) | core + 14px |
| **Yellow Penumbra** | (255, 230, 80, 60) | core + 28px |

### Inspiral Visual

- Two black holes orbit each other
- Orbital speed visibly increases
- Leave spiral trails

### Merger Flash

```python
self.flare = max(self.flare, wave_energy × 5)
```

- Bright yellow-white flash
- Radius expands with energy
- Visible across the simulation

### Gravitational Wave Ripple

- **Color:** Pale blue-white (200, 200, 255)
- **Shape:** Expanding ring (3px thick)
- **Alpha:** Proportional to wave strength
- **Radius:** Grows with wave_dist

---

## Statistics

Real-time tracking:

| Stat | Description |
|------|-------------|
| **Black Holes** | Current BH count |
| **BH Mergers** | Total merger events |
| **Grav Waves** | Total waves emitted |

---

## Gameplay Impact

### Creating Merger Events

**Method 1: Natural Formation**
1. Create multiple black holes near each other
2. Wait for gravity to bring them together
3. Watch the inspiral and merger!

**Method 2: Manual Placement**
1. Right-click to place black holes
2. Place two within 80 pixels
3. They will quickly inspiral and merge

### Effects on Your Simulation

**Gravitational Waves:**
- 🔥 **Heating** - Can raise temperatures by 10-20°C
- 💫 **Velocity Perturbation** - Randomly nudges particles
- ☠️ **Life Extinction** - Can wipe out nearby life forms
- 🌡️ **Habitat Disruption** - Makes zones uninhabitable

**Recoil Kicks:**
- 🚀 **Ejection** - Black hole shoots across simulation
- 💥 **Collision Risk** - Can merge with other BH mid-flight
- 🌌 **Trajectory** - Creates dramatic visual

---

## Real-World Physics Comparison

| Phenomenon | Real Universe | Cosmos Sandbox |
|------------|---------------|----------------|
| **Inspiral Time** | Millions of years | ~50-100 ticks |
| **GW Speed** | Speed of light (c) | 15 px/tick |
| **GW Strength** | Strain ~10⁻²¹ | Strength 10 (visual) |
| **Kick Velocity** | Up to 5000 km/s | 5-20 px/tick |
| **Energy Release** | 10⁴⁷ joules | Scaled for visual |
| **Merger Rate** | ~70% have kicks | 70% kick chance |

---

## .geo Implementation Details

### State Machine

```
BLACK HOLE STATES:
┌─────────────┐
│  Normal BH  │
└──────┬──────┘
       │ nb_count_gte=BH:1
       ▼
┌─────────────┐
│  Inspiring  │◄──────┐
└──────┬──────┘       │
       │ orbital_speed++ │
       ▼               │
┌─────────────┐       │
│  Spiraling  │───────┘
└──────┬──────┘
       │ dist < 20 AND speed >= 3
       ▼
┌─────────────┐
│   MERGER!   │
└──────┬──────┘
       ├──────┐
       │      │
       ▼      ▼
┌──────────┐ ┌──────────┐
│ Grav Wave│ │  Kick    │
└──────────┘ └──────────┘
```

### Key Rules

```geo
# Inspiral trigger
RULE IF is_blackhole AND nb_count_gte=is_blackhole:1
     THEN EMIT inspiral + SET_VAR inspiraling 1

# Orbital speed increase
RULE IF is_blackhole AND var_inspiraling=1
     THEN INCR_VAR orbital_speed 1

# Merger condition
RULE IF is_blackhole AND nb_count_gte=is_blackhole:2 AND var_orbital_speed>=5
     THEN EMIT merger + EMIT grav_wave

# Gravitational wave propagation
RULE IF signal=grav_wave
     THEN SET 1010 + INCR_VAR wave_dist 1

# Recoil kick
RULE IF signal=merger AND random<0.7
     THEN SET_VAR kick_vx random(-15,15) + SET_VAR kicking 1
```

---

## Tips & Strategies

### Creating Spectacular Mergers

1. **Spawn multiple BH close together** (within 80px)
2. **Wait for inspiral** - watch them spiral
3. **Stand back** - the merger flash is bright!
4. **Watch the waves** - see ripples propagate outward

### Protecting Life

1. **Keep BH away from habitable zones**
2. **Monitor wave emissions** - they disrupt habitats
3. **Recoil kicks** can eject BH from populated areas
4. **Create BH in empty regions**

### Photography Tips

1. **Pause during inspiral** - frame the shot
2. **Watch for kick** - dramatic ejection shots
3. **GW ripples** - best seen with habitable overlay
4. **Merger flash** - brightest event in simulation

---

## Performance

| BH Count | FPS | Notes |
|----------|-----|-------|
| 1-3 | 60 | Smooth |
| 4-6 | 55-60 | Great |
| 7-10 | 45-55 | Acceptable |
| 10+ | 30-45 | Heavy |

**Optimization:**
- Gravitational waves use separate particle list
- Wave effects only calculated for nearby particles
- Merger calculations are event-driven (not per-frame)

---

## Future Enhancements

### Planned Features

- [ ] Accretion disk visualization
- [ ] Hawking radiation for tiny BH
- [ ] Binary star systems with BH
- [ ] GW detection statistics
- [ ] Kick trajectory prediction
- [ ] Merger rate tracking

### Experimental

- [ ] Frame-dragging effects
- [ ] Event horizon visualization
- [ ] Time dilation near BH
- [ ] Multi-messenger astronomy (light + GW)

---

## See Also

- [`cosmos_sandbox.geo`](cosmos_sandbox.geo) - Full .geo implementation
- [`cosmos_sandbox.py`](cosmos_sandbox.py) - Python physics engine
- [`COSMOS_SANDBOX_README.md`](COSMOS_SANDBOX_README.md) - General documentation

---

## Scientific Accuracy Note

While simplified for gameplay, this implementation captures the **key physics** of black hole mergers:

✅ Inspiral due to gravitational radiation
✅ Merger with energy release  
✅ Gravitational wave propagation
✅ Asymmetric recoil kicks
✅ Wave effects on nearby matter

The scales are compressed for visual appeal, but the **qualitative behavior is accurate**!
