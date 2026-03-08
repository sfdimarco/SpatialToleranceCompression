# Showcase Application Guide

## Quick Start

```bash
# Launch the interactive GUI
python Showcase.py

# List all available demos
python Showcase.py --list

# Run a specific demo (no GUI)
python Showcase.py --demo walk_cycle

# Export terrain as JSON for game integration
python Showcase.py --export biomes --json

# Export animation as GIF
python Showcase.py --export attack_swing --gif --frames 30

# Export frames as PNG sequence
python Showcase.py --export voronoi --png --frames 80
```

---

## Features

### 🎬 Demo Browser
- **3 Categories**: Animation, Terrain, Self-Organizing
- **14 Interactive Demos**: Each with live preview
- **Visual Selection**: Click to load and run any demo

### ▶️ Playback Controls
| Control | Action |
|---------|--------|
| ▶ Play | Start animation |
| ⏸ Pause | Pause animation |
| ⏹ Stop | Reset to beginning |
| ⏭ Step | Advance one tick |

### 📖 Tutorial Mode
- Step-by-step annotations
- Explains key concepts at specific ticks
- Toggle with `T` key or Tutorial button

### 📤 Export Options
| Format | Use Case |
|--------|----------|
| **PNG** | Single frame capture |
| **GIF** | Animated preview |
| **JSON** | Game-ready terrain data |

---

## Demo Catalog

### 🎬 Animation Solver

Generate sprite sheets and animation cycles for games.

| Demo | Frames | Grid | Description |
|------|--------|------|-------------|
| **Walk Cycle** | 30 | No | 4-phase walk with arm/leg coordination |
| **Idle Breathing** | 60 | No | Natural breath cycle with secondary motion |
| **Attack Swing** | 30 | No | Melee attack with windup and impact |
| **Jump Arc** | 24 | No | Jump with squash/stretch principles |
| **Shape Morph** | 32 | No | Circle ↔ square transformation |

**Usage:**
```bash
python Showcase.py --demo walk_cycle
python Playground.py --geo examples/animation/walk_cycle.geo --depth 4
```

---

### 🏔️ Terrain Generator

Create game-ready heightmaps, biomes, caves, and dungeons.

| Demo | Ticks | Grid | Description |
|------|-------|------|-------------|
| **Heightmap** | 60 | Yes | Multi-octave noise with erosion |
| **Biomes** | 100 | Yes | Elevation + moisture assignment |
| **Caves** | 50 | Yes | Cellular automata caves |
| **Rivers** | 70 | Yes | Flow accumulation and carving |
| **Erosion** | 100 | Yes | Hydraulic erosion simulation |
| **Dungeon** | 80 | Yes | 6-phase procedural levels |

**Usage:**
```bash
python Showcase.py --demo dungeon
python Playground.py --geo examples/dungeon_generator.geo --grid --depth 3
```

**Export for Games:**
```bash
# Export dungeon as JSON
python Showcase.py --export dungeon --json

# Result: exports/dungeon.json with tile grid
```

---

### 🌀 Self-Organizing Systems

Emergent patterns from simple rules.

| Demo | Ticks | Grid | Description |
|------|-------|------|-------------|
| **Voronoi** | 80 | Yes | Region growth from seeds |
| **Maze** | 70 | Yes | Solvable maze generation |
| **Flow Field** | 100 | Yes | Vector field with particles |
| **Reaction-Diffusion** | 200 | Yes | Turing patterns (spots/stripes) |

**Usage:**
```bash
python Showcase.py --demo reaction_diffusion
python Playground.py --geo examples/selforg/reaction_diffusion.geo --grid
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `R` | Restart simulation |
| `T` | Toggle tutorial mode |
| `S` | Step forward one tick |
| `E` | Export current frame |

---

## Export Guide

### Export PNG Frame
```bash
python Showcase.py --export biomes --png
# Saves: exports/biomes_frame_60.png
```

### Export Animated GIF
```bash
python Showcase.py --export walk_cycle --gif --frames 30
# Saves: exports/walk_cycle.gif
```

### Export Terrain JSON
```bash
python Showcase.py --export caves --json
# Saves: exports/caves.json
```

**JSON Format:**
```json
{
  "demo": "caves",
  "export_time": "2026-03-07T12:00:00Z",
  "size": {"rows": 8, "cols": 8},
  "grid": [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 2, 2, 2, 0, 1],
    ...
  ],
  "legend": {
    "0": "void/empty",
    "1": "wall/solid",
    "2": "floor/walkable",
    "3": "door",
    "4": "corridor"
  }
}
```

**Using in Games:**
```python
import json

with open('exports/caves.json', 'r') as f:
    terrain = json.load(f)

grid = terrain['grid']
for row in grid:
    for tile_id in row:
        if tile_id == 1:
            place_wall(x, y)
        elif tile_id == 2:
            place_floor(x, y)
        elif tile_id == 3:
            place_door(x, y)
```

---

## GUI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  BinaryQuadTree Showcase — Self-Organizing Systems              │
├──────────────┬─────────────────┬─────────────────┬──────────────┤
│              │                 │                 │              │
│  DEMO        │   SIMULATION    │     INFO        │  CONTROLS    │
│  BROWSER     │     VIEW        │    PANEL        │   PANEL      │
│              │                 │                 │              │
│  [Animation] │                 │  Title          │  ▶ ⏸ ⏹ ⏭    │
│  [Terrain]   │   [Live         │  Description    │              │
│  [SelfOrg]   │   Preview]      │  Key Concepts   │  Speed: 5   │
│              │                 │  Settings       │              │
│  • Walk      │                 │                 │  [PNG] [GIF] │
│  • Idle      │                 │  Tutorial:      │  [JSON]     │
│  • Attack    │                 │  Step 1/4       │              │
│  • Jump      │                 │  "Windup Phase" │  Keyboard:   │
│  • Morph     │                 │                 │  Space = Play│
│              │                 │                 │  R = Restart │
└──────────────┴─────────────────┴─────────────────┴──────────────┘
```

---

## Tutorial Mode

Tutorial mode provides guided explanations for complex demos.

**Example: Attack Swing Tutorial**

| Step | Tick | Concept |
|------|------|---------|
| 1 | 5 | Windup Phase - Telegraph the attack |
| 2 | 12 | Strike Phase - Fast forward swing |
| 3 | 17 | Impact Frame - Hit with shake effect |
| 4 | 25 | Recovery - Return to guard |

**Enable Tutorial:**
- Click "📖 Tutorial Mode" button
- Press `T` key

---

## Performance Tips

| Demo Type | Recommended Depth | Speed |
|-----------|-------------------|-------|
| Animation | 4-5 | 5-10 tps |
| Terrain | 3-4 | 3-6 tps |
| Self-Organizing | 2-3 | 3-6 tps |

**Optimization:**
- Lower depth for faster rendering
- Reduce speed for complex simulations
- Use grid mode only when required

---

## Troubleshooting

### Demo doesn't start
- Check if geo file exists in `examples/` folder
- Ensure `--grid` flag for terrain/selforg demos

### Export fails
- Install Pillow for GIF: `pip install Pillow`
- Check `exports/` folder permissions

### Tutorial not showing
- Some demos don't have tutorial steps
- Enable tutorial mode with `T` key

### Slow performance
- Reduce depth setting
- Lower speed (ticks per second)
- Close other applications

---

## Integration with Game Engines

### Unity
```csharp
// Load exported JSON
TextAsset terrainData = Resources.Load<TextAsset>("caves");
var data = JsonUtility.FromJson<TerrainData>(terrainData.text);

foreach (var row in data.grid) {
    foreach (var tile in row) {
        Instantiate(tilePrefabs[tile], x, y, 0);
    }
}
```

### Godot
```gdscript
var file = File.new()
file.open("res://exports/caves.json", File.READ)
var data = JSON.parse(file.get_as_text())

for row in data.grid:
    for tile in row:
        place_tile(tile, x, y)
```

### Unreal Engine
```cpp
// Parse JSON and spawn tiles
FString jsonContent;
FFileHelper::LoadFileToString(jsonContent, TEXT("exports/caves.json"));

TSharedPtr<FJsonObject> jsonObject;
TJsonReaderFactory<>::Parse(jsonContent, jsonObject);

// Iterate grid and place tiles
```

---

## Command Line Reference

```
python Showcase.py [OPTIONS]

Options:
  --demo NAME       Run specific demo (no GUI)
  --list            List all available demos
  --export NAME     Export a demo
  --json            Export as JSON (terrain)
  --gif             Export as GIF (animation)
  --png             Export as PNG sequence
  --depth N         Recursion depth (default: 5)
  --frames N        Number of frames (default: 60)
  --help            Show help message
```

---

## See Also

- [`docs/SHOWCASE_CONTENT_GUIDE.md`](docs/SHOWCASE_CONTENT_GUIDE.md) - Detailed script documentation
- [`GEO_LANGUAGE.md`](GEO_LANGUAGE.md) - .geo language reference
- [`README.md`](README.md) - Project overview
