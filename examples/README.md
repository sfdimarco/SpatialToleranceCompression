# .geo Script Examples

A curated collection of `.geo` scripts organized by category.

---

## Directory Structure

```
examples/
├── basics/           # Hello world and introductory examples
├── animation/        # Character animations and motion
├── cellular/         # Cellular automata (Life, forest fire, etc.)
├── cosmos/           # Cosmic simulations (gravity, black holes, galaxies)
├── generative/       # Generative art and fractals
├── geo_showcase/     # Language feature demonstrations
├── neural/           # Neural network implementations
├── neural_pipeline/  # Pattern recognition with self-organizing maps
├── selforg/          # Self-organization patterns
├── simulations/      # Strategy and simulation games
└── terrain/          # Terrain generation
```

---

## Categories

### 📚 `basics/` - Getting Started
Hello world and introductory examples for learning `.geo` syntax.

**Scripts:**
- `hello_world.geo` - Your first `.geo` program

**Start here if:** You're new to `.geo` scripts

---

### 🎬 `animation/` - Character Animation
Animation sequences for games and visualizations.

**Scripts:**
- `idle_breathe.geo` - Character breathing cycle
- `attack_swing.geo` - Melee attack animation
- `jump_arc.geo` - Jump with parabolic trajectory
- `morph_shape.geo` - Shape morphing
- `walk_cycle.geo` - Character walk cycle

**Use for:** Game character animations, UI transitions

---

### 🔬 `cellular/` - Cellular Automata
Classic cellular automata and grid-based simulations.

**Scripts:**
- `conway_life.geo` - Conway's Game of Life
- `forest_fire.geo` - Forest fire simulation
- `heat_spread.geo` - Heat diffusion
- `nb_spread.geo` - Neighbor-based spread

**Use for:** Emergent behavior, simulation, pattern generation

---

### 🌌 `cosmos/` - Cosmic Simulations
Large-scale universe simulations with gravity and particles.

**Subdirectories:**
- `Cosmos/` - Main cosmos implementation
- `Cosmos_Sim/` - Simulation tools
- `Gravity_Cosmos/` - Gravity-based cosmos
- `Black Hole/` - Black hole simulations

**Documentation:**
- `COSMOS_README.md` - Cosmos overview
- `GEO_PHYSICS_IMPLEMENTATION.md` - Physics details

**Use for:** Space simulations, gravity effects, particle systems

---

### 🎨 `generative/` - Generative Art
Fractal patterns and generative art scripts.

**Scripts:**
- `spiral.geo` - Fractal spiral
- `pulse_depth.geo` - Depth-based pulsing
- `stochastic.geo` - Probabilistic patterns
- `rotate_mirror.geo` - Rotation and mirroring

**Use for:** Abstract art, backgrounds, visual effects

---

### 📖 `geo_showcase/` - Language Features
Demonstrations of specific `.geo` language features.

**Scripts:**
- `composite.geo` - Composite actions
- `depth_layers.geo` - Depth-based rules
- `mask_set.geo` - Mask set operations
- `signal_wave.geo` - Inter-cell signals
- `vote_example.geo` - Plurality voting

**Use for:** Learning specific `.geo` features

---

### 🧠 `neural/` - Neural Networks
Neural network implementations using `.geo` rules.

**Scripts:**
- `neural_majority3.geo` - 3-input majority vote
- `neural_xor.geo` - XOR perceptron
- `neural_sigmoid.geo` - Sigmoid activation
- `neural_perceptron.geo` - Multi-input perceptron
- `neural_hopfield.geo` - Hopfield associative memory
- `neural_kohonen.geo` - Kohonen self-organizing map
- `neural_cnn_edge.geo` - CNN edge detector
- `neural_lstm_cell.geo` - LSTM cell

**Documentation:**
- `NEURAL_NETWORKS_FULL.md` - Complete neural network guide
- `NEURAL_QUICK_REF.md` - Quick reference

**Use for:** Pattern recognition, machine learning, AI

---

### 🔍 `neural_pipeline/` - Pattern Recognition
Complete pattern recognition system with self-organizing maps.

**Components:**
- `pipeline_input.geo` - Input encoding
- `pipeline_feature_map.geo` - SOM feature extraction
- `pipeline_memory.geo` - Hopfield memory
- `pipeline_training.geo` - Hebbian learning
- `pipeline_full.geo` - Integrated system

**Patterns:**
- `patterns/pattern_letters.py` - Letter patterns (A-Z)
- `patterns/pattern_digits.py` - Digit patterns (0-9)

**Demo:** Run `python neural_pipeline_demo.py`

**Use for:** Pattern recognition, associative memory, classification

---

### 🌀 `selforg/` - Self-Organization
Self-organizing patterns and emergent structures.

**Scripts:**
- `flow_field.geo` - Flow field simulation
- `maze.geo` - Maze generation
- `reaction_diffusion.geo` - Reaction-diffusion patterns
- `voronoi.geo` - Voronoi diagrams

**Use for:** Natural patterns, texture generation, procedural content

---

### 🎮 `simulations/` - Strategy & Simulation
Game-like simulations and strategy systems.

**Scripts:**
- `ecosystem.geo` - Ecosystem simulation
- `faction_wars.geo` - Faction conflict simulation
- `territory_conquest.geo` - Territory conquest
- `combat_encounters.geo` - Combat encounter generation

**Use for:** Strategy games, simulation games, procedural generation

---

### 🏔️ `terrain/` - Terrain Generation
Procedural terrain and landscape generation.

**Scripts:**
- Check directory for available terrain scripts

**Use for:** Game maps, landscapes, procedural worlds

---

## Quick Start

### Run a Demo

```bash
# List available demos
python BinaryQuadTreeTest.py --list

# Run a specific demo
python BinaryQuadTreeTest.py --geo examples/generative/spiral.geo

# Run neural network demo
python neural_pipeline_demo.py

# Run Kohonen color SOM
python kohonen_color_demo.py
```

### Load in Python

```python
from src import load_geo

# Load a .geo script
program = load_geo("examples/generative/spiral.geo")

# Use in grid
grid = Grid.make(3, 3, program)
```

---

## Contributing

### Adding New Scripts

1. **Choose the right category** - Match your script's purpose
2. **Follow naming conventions** - `snake_case.geo`
3. **Include header comments** - Explain what it does
4. **Add to this README** - Update the appropriate section
5. **Test thoroughly** - Ensure it works as expected

### Script Template

```geo
NAME my_awesome_script

# ── Description ──────────────────────────────────────────────────
# Brief explanation of what this script does
#
# Grid layout (if applicable):
#   [describe cell positions]
#
# Execution phases (if applicable):
#   tick%N=0: Phase description
#
# Variables:
#   var_name: description

# Your rules here
RULE IF condition THEN action

DEFAULT action
```

---

## Finding Scripts

### By Feature

| Feature | Look In |
|---------|---------|
| Basic syntax | `basics/` |
| Animation | `animation/` |
| Cellular automata | `cellular/` |
| Fractals | `generative/` |
| Neural networks | `neural/` |
| Self-organization | `selforg/` |
| Terrain | `terrain/` |
| Games/Simulation | `simulations/` |
| Language features | `geo_showcase/` |

### By Complexity

| Level | Scripts |
|-------|---------|
| Beginner | `basics/hello_world.geo`, `generative/spiral.geo` |
| Intermediate | `cellular/conway_life.geo`, `neural/neural_majority3.geo` |
| Advanced | `neural_pipeline/pipeline_full.geo`, `cosmos/*` |

---

## Additional Resources

- [GEO_LANGUAGE.md](../GEO_LANGUAGE.md) - Full language reference
- [README.md](../README.md) - Main project documentation
- [GEOSTUDIO.md](../GEOSTUDIO.md) - GeoStudio tool guide
- [PLAYGROUND.md](../PLAYGROUND.md) - Interactive playground

---

**Happy scripting!** 🎨✨
