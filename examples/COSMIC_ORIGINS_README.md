# Cosmic Origins - A .geo-Powered Space Game

## Overview

**Cosmic Origins** is a full space exploration and combat game where **all game mechanics are driven by `.geo` scripts**. This demonstrates how the Binary Quad-Tree Grammar Engine can power complete interactive experiences, not just visualizations.

## Download & Run

```bash
cd d:\CodexTest\BinaryQuadTreeCPUTest
python examples\cosmic_origins.py
```

### Requirements

```bash
pip install pygame
```

---

## Game Features

### 🌌 Galaxy Exploration
- **Procedurally generated galaxy** using `galaxy_generator.geo`
- **50+ unique star systems** with different types (G, K, M, O, B stars)
- **Habitable planets** to discover
- **Special objects**: pulsars, alien ruins, wormholes
- **Resource gathering** for credits

### ⚔️ Space Combat
- **Dynamic enemy spawns** via `combat_encounters.geo`
- **Multiple enemy types**: Scouts, Elites, Bosses
- **Formation patterns**: V-attack, Circle defense, Line barrage
- **Power-up drops**: Health, Weapons, Shields
- **Wave-based encounters**

### 🎮 Smooth Gameplay
- **60 FPS** performance
- **Particle effects** and glow rendering
- **Smooth camera** following
- **Responsive controls**

---

## Controls

| Key | Action |
|-----|--------|
| **WASD / Arrows** | Move ship |
| **Space** | Shoot / Confirm |
| **E** | Interact |
| **Tab** | Toggle galaxy map |
| **P** | Pause |
| **R** | Start new game / Restart |
| **Esc** | Quit |

---

## How .geo Powers the Game

### 1. Galaxy Generation (`galaxy_generator.geo`)

```geo
# Creates spiral arm structure
RULE IF tick_in=11..30 AND is_inner AND tick%4=depth%4
     THEN SET 1000 + SET_VAR star_mass (10-depth)  AS spiral-arm-star

# Places habitable planets
RULE IF tick_in=31..50 AND is_inner AND random<0.08 AND depth_in=2..4
     THEN SET 1100 + SET_VAR planet_type 3 + SET_VAR habitable 1
```

**What it controls:**
- Star placement and density
- Planet types (rocky, gas, habitable)
- Asteroid belts and resource distribution
- Special objects (pulsars, wormholes, ruins)

### 2. Combat Encounters (`combat_encounters.geo`)

```geo
# Enemy spawn waves
RULE IF tick%60=0 AND depth=0 AND random<0.4
     THEN SET 1100 + SET_VAR enemy_type 1 + SET_VAR hp 3  AS spawn-scout

# Formation patterns
RULE IF tick%60=10 AND depth_in=1..3
     THEN SET 1100 + SET_VAR formation 1  AS v-formation

# Power-up drops
RULE IF tick%90=30 AND random<0.2
     THEN SET 0111 + SET_VAR powerup 1  AS spawn-health
```

**What it controls:**
- Enemy spawn timing and positions
- Formation patterns (V, circle, line)
- Projectile patterns
- Power-up spawn rates
- Obstacle placement

---

## Game Loop Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GAME LOOP                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐  │
│  │   .geo       │      │   Python     │      │  Pygame  │  │
│  │  Generator   │─────▶│  Game Logic  │─────▶│ Renderer │  │
│  │  (.geo)      │      │              │      │          │  │
│  └──────────────┘      └──────────────┘      └──────────┘  │
│         ▲                     │                              │
│         │                     ▼                              │
│         │              ┌──────────────┐                      │
│         └──────────────│   .geo       │                      │
│                        │  Combat      │                      │
│                        │  (.geo)      │                      │
│                        └──────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **`.geo` scripts** generate game state (positions, types, resources)
2. **Python game logic** interprets `.geo` output into game objects
3. **Pygame** renders objects and handles input
4. **Player actions** feed back into `.geo` state (via variables)

---

## Star System Types

| Type | Color | Frequency | Resources | Danger |
|------|-------|-----------|-----------|--------|
| **G (Yellow)** | 🟡 Yellow | Common | Medium | Low |
| **K (Orange)** | 🟠 Orange | Common | Medium | Low |
| **M (Red)** | 🔴 Red | Common | Low | Low |
| **O (Blue)** | 🔵 Blue | Rare | High | Medium |
| **B (White)** | ⚪ White | Very Rare | Very High | High |
| **Black Hole** | 🟣 Purple | Unique | Exotic | Extreme |

---

## Planet Types

| Type | Description | Resources |
|------|-------------|-----------|
| **Rocky** | Terrestrial planets, asteroids | Minerals, metals |
| **Gas Giant** | Large gas planets | Helium-3, fuel |
| **Habitable** | Earth-like, life-supporting | Food, water, colonies |
| **Special** | Ruins, anomalies | Artifacts, tech |

---

## Combat Mechanics

### Enemy Types

| Enemy | HP | Speed | Behavior |
|-------|-----|-------|----------|
| **Scout** | 20 | Fast | Harassment, hit-and-run |
| **Elite** | 50 | Medium | Flanking, formation |
| **Boss** | 150+ | Slow | Spread shots, summons |

### Power-Ups

| Type | Color | Effect |
|------|-------|--------|
| **Health** | 🟢 Green | +25 HP |
| **Weapon** | 🔴 Red | +1 weapon level |
| **Shield** | 🔵 Blue | +50 shield |

---

## Performance

| System | Particles | FPS |
|--------|-----------|-----|
| Galaxy Map | 50 systems | 60 |
| Combat (Wave 1) | 5 enemies | 60 |
| Combat (Wave 5) | 20 enemies | 55-60 |
| Heavy Combat | 50+ objects | 45-55 |

**Optimization techniques:**
- Quadtree spatial partitioning (from `.geo`)
- Object pooling for projectiles
- Batched rendering
- Culled off-screen objects

---

## Save System

Game state is stored in JSON:

```json
{
  "player": {
    "credits": 1500,
    "ships_destroyed": 47,
    "systems_discovered": 23,
    "weapon_level": 3,
    "scan_level": 2
  },
  "galaxy": {
    "seed": 12345,
    "systems_explored": ["Alpha-1", "Beta-3"]
  },
  "progress": {
    "current_wave": 5,
    "story_flags": ["met_traders", "found_ruins"]
  }
}
```

---

## Extending the Game

### Add New Enemy Types

Edit `combat_encounters.geo`:

```geo
# Sniper enemy (long range)
RULE IF tick%180=90 AND random<0.15
     THEN SET 1100 + SET_VAR enemy_type 4 + SET_VAR hp 30 + SET_VAR range 500
```

### Add New Planet Types

Edit `galaxy_generator.geo`:

```geo
# Ocean world
RULE IF tick_in=31..50 AND habitable=1 AND random<0.3
     THEN SET_VAR planet_type 4 + SET_VAR resource 4  AS ocean-world
```

### Add New Weapons

Edit `cosmic_origins.py`:

```python
WEAPONS = {
    1: {"damage": 10, "rate": 10, "color": (255, 255, 100)},
    2: {"damage": 15, "rate": 8, "color": (255, 150, 100)},
    3: {"damage": 25, "rate": 5, "color": (150, 255, 255)},
}
```

---

## Comparison: .geo vs Traditional Game Dev

| Aspect | Traditional | .geo-Powered |
|--------|-------------|--------------|
| **Level Design** | Manual placement or noise | Rule-based generation |
| **Enemy Spawns** | Hardcoded positions | Dynamic patterns |
| **Balance** | Manual tuning | Adjust rule weights |
| **Content Updates** | Code changes | Script changes |
| **Emergence** | Limited | High (cellular automata) |

---

## Future Roadmap

### Phase 1: Core Game ✅
- [x] Galaxy generation
- [x] Space exploration
- [x] Basic combat
- [x] Resource gathering

### Phase 2: Expanded Content
- [ ] Multiplayer co-op
- [ ] Faction system
- [ ] Trading mechanics
- [ ] Ship upgrades

### Phase 3: Advanced Features
- [ ] Story missions
- [ ] Base building
- [ ] Fleet command
- [ ] Procedural quests

### Phase 4: Polish
- [ ] Sound effects
- [ ] Music
- [ ] Particle effects
- [ ] Achievements

---

## Credits

**Game Design & Implementation:**
- Built with BinaryQuadTreeCPUTest engine
- `.geo` scripts for procedural generation
- Pygame for rendering

**Inspiration:**
- Classic space games (Elite, Escape Velocity)
- Modern roguelikes
- p5.js gravity simulations

---

## Troubleshooting

### Game won't start
```bash
pip install --upgrade pygame
```

### Low FPS
- Reduce window size: `--width 800 --height 600`
- Limit particles in code

### .geo script errors
- Check syntax in `.geo` files
- Ensure all rules have THEN clause

---

## License

MIT License - Same as BinaryQuadTreeCPUTest

---

## See Also

- [`docs/SHOWCASE_GUIDE.md`](docs/SHOWCASE_GUIDE.md) - Showcase application guide
- [`GEO_LANGUAGE.md`](GEO_LANGUAGE.md) - .geo language reference
- [`README.md`](README.md) - Project overview
