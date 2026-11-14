# Cosmos Infinite — .geo Powered Universe Simulation

## Overview

**Cosmos Infinite** is an infinite space cosmos simulation built on the Binary Quad-Tree Grammar Engine. It uses `.geo` declarative scripts to define the rules of cosmic evolution, from the Big Bang to emergent structure formation.

## Features

### 🌌 Infinite Space
- Procedurally generated universe using chunk-based loading
- Seamless exploration with no boundaries
- Automatic memory management (chunks unload when distant)

### 🔭 Smooth Zoom System
- Zoom from cosmic scale (galaxy clusters) to stellar scale (individual stars)
- Camera interpolation for smooth transitions
- LOD (Level of Detail) based on zoom depth

### 💥 Big Bang Simulation
- Start from an initial singularity
- Inflation phase with rapid expansion
- Natural structure formation from density fluctuations

### 🎮 .geo Rule-Based Evolution
All cosmic behavior is defined in `cosmos.geo`:
- **Stars** (Y_LOOP): Form from gas, age, go supernova
- **Gas Clouds** (X_LOOP): Condense into stars, spread through space
- **Dark Matter** (Z_LOOP): Gravitational wells that structure the universe
- **Black Holes** (GATE_ON/1111): Absorb matter, emit gravitational waves
- **Gravitational Waves** (DIAG_LOOP): Propagate energy from massive events

### 📊 Cell Variables
Each cell tracks physical properties:
- `mass` - Total mass in the region
- `temp` - Temperature (affects star color, habitability)
- `density` - Matter density (0-100)
- `age` - Time in current state
- `vx`, `vy` - Velocity components

## Installation

```bash
pip install pygame
```

## Usage

### Basic Run
```bash
python examples/cosmos_infinite.py
```

### Command Line Options
```bash
# Custom window size
python examples/cosmos_infinite.py --width 1920 --height 1080

# Custom FPS
python examples/cosmos_infinite.py --fps 30

# Custom .geo script
python examples/cosmos_infinite.py --geo my_custom_cosmos.geo
```

## Controls

| Input | Action |
|-------|--------|
| **Mouse Wheel** | Zoom in/out |
| **Left Click + Drag** | Pan camera |
| **Right Click** | Add black hole at cursor |
| **Middle Click** | Add star at cursor |
| **B** | Trigger mini Big Bang at cursor |
| **Space** | Pause/Resume simulation |
| **R** | Reset simulation |
| **1-5** | Change LOD (max simulation depth) |
| **H** | Toggle habitable zone overlay |
| **Esc** | Quit |

## Architecture

### Chunk System
The infinite world is divided into chunks (16×16 cells each):
- Only chunks near the viewport are loaded
- Old chunks are automatically unloaded (memory limit: 64 chunks)
- Each chunk runs its own `.geo` simulation

### Zoom & LOD
- **Zoom level** determines cell size on screen
- **Depth levels (1-5)** control quadtree recursion depth
- Higher depth = more detail but slower performance
- Auto-adjusts based on zoom for optimal performance

### Mask Family Encoding

| Family | Mask Pattern | Cosmic Entity |
|--------|--------------|---------------|
| `Y_LOOP` | `1000→0100→0010→0001` | Stars, luminous matter |
| `X_LOOP` | `1100→0101→0011→1010` | Gas clouds, nebulae |
| `Z_LOOP` | `0111→1011→1101→1110` | Dark matter, gravitational wells |
| `DIAG_LOOP` | `1001↔0110` | Gravitational waves, radiation |
| `GATE_ON` | `1111` | Black holes, singularities |
| `GATE_OFF` | `0000` | Void, empty space |

## cosmos.geo Rules

The simulation behavior is entirely defined in `examples/cosmos.geo`. Key rule categories:

### 1. Big Bang Phase (ticks 0-15)
```geo
RULE IF tick_in=0..5 AND is_blackhole THEN 
       SWITCH Y_LOOP + INCR_VAR vx 10 + INCR_VAR vy 10
       AS bigbang_stars
```

### 2. Star Formation
```geo
RULE IF is_gas AND is_dense AND has_gas_nb AND tick%4=0 THEN 
       SWITCH Y_LOOP + SET_VAR temp 50
       AS star_formation
```

### 3. Stellar Evolution
```geo
RULE IF is_star AND var_age<100 THEN 
       ADVANCE + INCR_VAR mass 0.5 + INCR_VAR temp 0.3
       AS star_aging
```

### 4. Black Hole Behavior
```geo
RULE IF is_blackhole AND has_star_nb AND random<0.3 THEN 
       INCR_VAR mass 10 + EMIT absorb
       AS bh_eat_star

# Note: Use SET 1111 for black holes, SET 0000 for void
# SWITCH only works with loop families (Y_LOOP, X_LOOP, Z_LOOP, DIAG_LOOP)
RULE IF is_star AND is_massive THEN 
       SET 1111 + EMIT supernova
       AS supernova
```

### 5. Gravitational Waves
```geo
RULE IF is_wave AND var_age<20 THEN 
       SWITCH DIAG_LOOP + INCR_VAR age 1 + EMIT wave_continue
       AS wave_propagate
```

## Creating Custom Cosmos Scripts

You can create your own `.geo` scripts to define different cosmic behaviors:

```geo
NAME my_universe

# Define custom aliases
DEFINE is_young_star is_star AND var_age<50
DEFINE supermassive var_mass>=500

# Custom rule: young stars form planets
RULE IF is_young_star AND random<0.1 THEN 
       INCR_VAR density 10
       AS planet_formation

# Custom rule: supermassive black holes merge
RULE IF is_blackhole AND supermassive AND has_blackhole_nb THEN 
       INCR_VAR mass 100 + EMIT merger
       AS bh_merge

DEFAULT ADVANCE
```

## Performance Tips

1. **Adjust LOD**: Press 1-3 for faster performance, 4-5 for more detail
2. **Limit zoom**: Extreme zoom levels load more chunks
3. **Reduce FPS**: Use `--fps 30` for smoother gameplay on slower systems
4. **Smaller window**: Smaller viewport = fewer chunks to simulate

## Emergent Behaviors

Watch for these emergent phenomena:

- **Galaxy Formation**: Dark matter wells attract gas, which forms stars
- **Supernova Chains**: One supernova triggers nearby stars to explode
- **Black Hole Growth**: Massive black holes dominate their regions
- **Gravitational Wave Echoes**: Waves from mergers propagate across space
- **Habitable Zones**: Stars with right temperature support potential life

## Future Enhancements

Planned features:
- [ ] Multi-body gravitational physics
- [ ] Planet formation in habitable zones
- [ ] Spiral galaxy rotation curves
- [ ] Cosmic microwave background visualization
- [ ] Export simulation frames as video
- [ ] Multi-zone program boundaries
- [ ] Save/load universe state

## Troubleshooting

### "Geo script has issues" warning
Some `.geo` constructs may not be fully supported yet. The simulation will use default rules.

### Low FPS
- Reduce LOD (press 1-2)
- Zoom out to load fewer chunks
- Lower FPS target with `--fps 30`

### Chunks popping in/out
This is normal! Chunks load as you pan and unload when distant. Increase `MAX_CHUNKS` in code for larger cache.

## Credits

Built with:
- **Binary Quad-Tree Grammar Engine** - Spatial simulation core
- **`.geo` Language** - Declarative rule scripting
- **pygame** - Rendering and input

## License

MIT License - See main repository LICENSE file
