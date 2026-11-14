# How to Run Cosmos Simulations

## ⚠️ DO NOT Double-Click the .py Files!

Double-clicking `.py` files on Windows causes the window to close immediately.

## ✅ Correct Ways to Run

### Option 1: Double-Click the .bat Files (Easiest)

In this folder, double-click:
- **`RUN_COSMOS_INFINITE.bat`** - Runs the infinite cosmos simulation
- **`RUN_COSMOS_SIM.bat`** - Runs the gravity sandbox simulation

The window will stay open and show any errors.

### Option 2: Run from Command Prompt

1. Open Command Prompt (press `Win + R`, type `cmd`, press Enter)
2. Type these commands:

```cmd
cd d:\CodexTest\BinaryQuadTreeCPUTest
python examples\cosmos\cosmos_infinite.py
```

Or for cosmos sim:

```cmd
cd d:\CodexTest\BinaryQuadTreeCPUTest
python examples\cosmos\cosmos_sim.py
```

## Controls

### Cosmos Infinite
| Control | Action |
|---------|--------|
| Mouse Wheel | Zoom in/out |
| Left Click + Drag | Pan camera |
| Right Click | Add black hole |
| Middle Click | Add star |
| B | Trigger big bang at cursor |
| Space | Pause/Resume |
| R | Reset simulation |
| H | Toggle habitable zone |
| Esc | Quit |

### Cosmos Sim
| Control | Action |
|---------|--------|
| Left Click | Spawn planet (blue) |
| Right Click | Spawn sun (gold) |
| Middle Click | Spawn dark matter (purple) |
| G | Toggle gravity visualization |
| T | Toggle trails |
| Space | Pause/Resume |
| C | Clear all |
| S | Spawn solar system |
| Esc | Quit |

## If You Still Have Issues

Run from command prompt to see error messages:

```cmd
cd d:\CodexTest\BinaryQuadTreeCPUTest
python examples\cosmos\cosmos_infinite.py
```

This will show any errors instead of the window closing immediately.
