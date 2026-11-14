# Project Structure

Organized file structure for the Binary Quad-Tree Grammar Engine project.

## Directory Layout

```
BinaryQuadTreeCPUTest/
├── src/                          # Source code package
│   ├── __init__.py               # Package exports
│   ├── binary_quad_tree.py       # Core engine (Node, Grid, Program, Rule)
│   └── GeoStudio.py              # Visual launcher and export tool
│
├── geo/                          # Central .geo file repository
│   ├── core/                     # Core/essential .geo files
│   ├── cosmos/                   # Space/cosmos simulations
│   ├── neural/                   # Neural network demos
│   └── playground/               # Test/experimental .geo files
│
├── examples/                     # Example Python scripts
│   └── cosmos/                   # Cosmos simulations (.py + .geo together)
│       ├── cosmos_infinite.py    # Infinite space cosmos with zoom
│       ├── cosmos.geo            #   → Uses this .geo
│       ├── cosmic_origins.py     # 4X space strategy game
│       ├── cosmic_origins.geo    #   → Uses this .geo
│       ├── cosmic_ai_behaviors.geo     #   → Also uses these
│       ├── cosmic_events_encounters.geo#
│       ├── cosmos_sandbox.py     # Particle sandbox
│       ├── cosmos_sandbox.geo    #   → Uses this .geo
│       ├── cosmos_sim.py         # Gravity simulator
│       ├── cosmos_sim.geo        #   → Uses this .geo
│       ├── gravity_cosmos_sim.py # Gravity cosmos
│       ├── gravity_cosmos.geo    #   → Uses this .geo
│       └── gravity_sandbox.geo   #   → Uses this .geo
│
├── docs/                         # Documentation
├── exports/                      # Exported simulations (generated)
├── media/                        # Images, videos, assets
├── tests/                        # Test files
│
├── hello_world.py                # Quick start demo
├── hello_world.geo               #   → Uses this .geo (in examples/hello_world/)
├── Playground.py                 # Interactive playground
├── Showcase.py                   # Visual showcase application
├── neural_demo.py                # Neural network demonstration
├── README.md                     # Project overview
├── requirements.txt              # Python dependencies
├── STRUCTURE.md                  # This file
└── LICENSE                       # MIT License
```

## Key Organization Principles

### 1. .geo Files With Their .py Files
Each simulation's `.geo` file is in the **same folder** as the `.py` file that uses it:

```
examples/cosmos/
├── cosmos_infinite.py    ← Python simulation
└── cosmos.geo            ← .geo file it uses (SAME FOLDER)
```

### 2. Central Repository in geo/
The `geo/` directory serves as a **central repository** for all `.geo` files.
Files are **copied** from `geo/` to `examples/` folders where they're used.

### 3. Source Code in src/
All core engine code is in the `src/` package:
- `binary_quad_tree.py` - Core engine
- `GeoStudio.py` - Visual launcher

## Import Usage

### For Python Scripts

```python
from src import (
    Node, Grid, Program, Rule,
    GATES, Y_LOOP, X_LOOP, Z_LOOP, DIAG_LOOP,
    parse_geo_script, load_geo, validate_geo,
    family_of, next_mask, IF_family, SwitchFamily
)
```

### For .geo File Paths

```python
import os
# .geo files are in the SAME folder as the .py that uses them
GEO_PATH = os.path.join(os.path.dirname(__file__), 'cosmos.geo')
program = parse_geo_script(open(GEO_PATH).read())
```

## Running Simulations

### Cosmos Infinite
```bash
# Standard big bang universe
python examples/cosmos/cosmos_infinite.py

# With different modes (uses different .geo combinations)
python examples/cosmos/cosmos_infinite.py --mode origins
python examples/cosmos/cosmos_infinite.py --mode full
```

### Cosmos Sim (Gravity Simulator)
```bash
python examples/cosmos/cosmos_sim.py
```

### Cosmic Origins (4X Space Strategy)
```bash
python examples/cosmos/cosmic_origins.py
```

### Other Demos
```bash
python hello_world.py       # Hello World demo
python Playground.py        # Browse all .geo files
python Showcase.py          # Visual showcase
python neural_demo.py       # Neural network demo
```

## Adding New Simulations

1. **Create your .geo file** in `geo/cosmos/` (or appropriate category)

2. **Copy it** to the `examples/cosmos/` folder:
   ```bash
   copy geo\cosmos\my_simulation.geo examples\cosmos\
   ```

3. **Create your .py file** in `examples/cosmos/`:
   ```python
   import os
   from src import parse_geo_script, Grid, draw_grid_frame
   
   # Load .geo from SAME folder
   geo_path = os.path.join(os.path.dirname(__file__), 'my_simulation.geo')
   program = parse_geo_script(open(geo_path).read())
   
   # Use the program with Grid
   grid = Grid.make(rows=32, cols=32, program=program, ...)
   ```

4. **Run it**:
   ```bash
   python examples/cosmos/my_simulation.py
   ```

## File Relationships

| Python File | .geo Files Used | Description |
|-------------|-----------------|-------------|
| `cosmos_infinite.py` | `cosmos.geo`, `cosmic_origins.geo`, `cosmic_ai_behaviors.geo`, `cosmic_events_encounters.geo` | Infinite cosmos with multiple modes |
| `cosmic_origins.py` | `cosmic_origins.geo` (+ AI/events) | 4X space strategy game |
| `cosmos_sandbox.py` | `cosmos_sandbox.geo` | Charged-gravity sandbox |
| `cosmos_sim.py` | `cosmos_sim.geo`, `gravity_sandbox.geo` | Gravity simulator |
| `gravity_cosmos_sim.py` | `gravity_cosmos.geo` | Gravity-focused cosmos |
| `hello_world.py` | `examples/hello_world.geo` | Hello World demo |
| `Playground.py` | All .geo files | Interactive browser |
| `Showcase.py` | All .geo files | Visual showcase |
