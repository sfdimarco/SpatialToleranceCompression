# 🎮 Neural Network Showcase

A curated collection of **runnable neural network demos** and visualizations.

---

## 🚀 Quick Start

### Run the Unified Showcase (Recommended)

```bash
python Showcase/neural_showcase.py
```

This gives you a menu to choose from all available demos!

### Run Individual Demos

```bash
# Neural network visualizer (Majority-3 & XOR)
python Showcase/neural_demo.py

# Pattern recognition pipeline
python Showcase/neural_pipeline_demo.py

# Kohonen color self-organizing map
python Showcase/kohonen_color_demo.py
```

---

## 📁 What's In Here

### Runnable Demos ✅

| File | Description | Requirements |
|------|-------------|--------------|
| `neural_demo.py` | Interactive visualizer for Majority-3 and XOR networks | `pygame` |
| `neural_pipeline_demo.py` | Pattern recognition with SOM + Hopfield memory | `pygame` |
| `kohonen_color_demo.py` | 10×10 color map self-organization | `pygame` |
| `neural_showcase.py` | **Unified runner** - menu for all demos | None |

### Test Mode (No GUI)

All demos support `--test` flag for console testing:

```bash
python Showcase/neural_demo.py --test
python Showcase/neural_pipeline_demo.py --test
python Showcase/kohonen_color_demo.py --test
```

---

## 🎯 What Can You Run

### ✅ CAN RUN (Interactive GUI)

These have full pygame visualizations:

1. **`neural_demo.py`**
   - Visualize 2 neural networks
   - Toggle inputs, watch propagation
   - Truth table testing
   
2. **`neural_pipeline_demo.py`**
   - Draw patterns on 5×5 grid
   - Train self-organizing feature map
   - Recall from associative memory
   
3. **`kohonen_color_demo.py`**
   - Watch colors self-organize
   - Interactive color training
   - Save color maps as PNG

### ✅ CAN RUN (Console Test)

All demos work with `--test` flag:

```bash
python Showcase/neural_demo.py --test
# Output: Truth table results

python Showcase/neural_pipeline_demo.py --test
# Output: Pattern recognition test

python Showcase/kohonen_color_demo.py --test
# Output: Color SOM training stats
```

### ❌ CANNOT RUN Directly

These are **supporting files**, not runnable:

- `examples/neural/*.geo` - `.geo` scripts (loaded by Python demos)
- `examples/neural_pipeline/*.geo` - Pipeline rules (loaded by Python)
- `examples/neural_pipeline/patterns/*.py` - Pattern data (imported)
- `NEURAL_*.md` - Documentation files

---

## 📋 Demo Details

### 1. Neural Network Visualizer

**File:** `neural_demo.py`

**What It Does:**
- Visualizes 2 neural networks implemented in `.geo`
- Majority-3: 3-input threshold logic unit
- XOR: 2-layer perceptron solving XOR

**Controls:**
- Click inputs to toggle ON/OFF
- TAB to switch networks
- SPACE to pause/resume
- T to run truth table tests

**Requirements:** `pygame`

---

### 2. Pattern Recognition Pipeline

**File:** `neural_pipeline_demo.py`

**What It Does:**
- Self-organizing feature map (SOM)
- Hopfield associative memory
- Pattern completion from partial cues

**Controls:**
- Click/drag to draw 5×5 patterns
- T: Toggle training
- R: Recall from memory
- P: Train on all patterns

**Requirements:** `pygame`

---

### 3. Kohonen Color SOM

**File:** `kohonen_color_demo.py`

**What It Does:**
- 10×10 grid of color neurons
- Self-organizes RGB color space
- Creates beautiful color gradients

**Controls:**
- SPACE: Toggle auto-training
- T: Manual training step
- R: Reset weights
- S: Save color map as PNG

**Requirements:** `pygame`

---

## 🔧 Installation

### Required Dependencies

```bash
pip install pygame matplotlib
```

### Optional (for development)

```bash
pip install numpy
```

---

## 📂 Directory Structure

```
Showcase/
├── README.md                    # This file
├── neural_showcase.py           # Unified runner (START HERE)
├── neural_demo.py               # Majority-3 & XOR visualizer
├── neural_pipeline_demo.py      # Pattern recognition pipeline
└── kohonen_color_demo.py        # Color SOM visualization

../examples/neural/
├── neural_majority3.geo         # Loaded by neural_demo.py
├── neural_xor.geo               # Loaded by neural_demo.py
├── neural_sigmoid.geo           # Reference implementation
├── neural_perceptron.geo        # Reference implementation
├── neural_hopfield.geo          # Reference implementation
├── neural_kohonen.geo           # Reference implementation
├── neural_cnn_edge.geo          # Reference implementation
└── neural_lstm_cell.geo         # Reference implementation

../examples/neural_pipeline/
├── pipeline_full.geo            # Loaded by neural_pipeline_demo.py
├── pipeline_input.geo           # Input encoding
├── pipeline_feature_map.geo     # SOM rules
├── pipeline_memory.geo          # Hopfield rules
├── pipeline_training.geo        # Learning rules
└── patterns/
    ├── pattern_letters.py       # Letter patterns
    └── pattern_digits.py        # Digit patterns
```

---

## 🎓 Learning Path

### Beginner

1. Run `neural_showcase.py`
2. Choose demo #1 (Neural Network Visualizer)
3. Watch the Majority-3 network
4. Toggle inputs, observe output

### Intermediate

1. Run `neural_showcase.py`
2. Choose demo #2 (Pattern Recognition)
3. Draw a pattern
4. Train on it (press P)
5. Test recall

### Advanced

1. Run `neural_showcase.py`
2. Choose demo #3 (Kohonen Color SOM)
3. Watch self-organization
4. Experiment with training parameters
5. Save interesting color maps

---

## 🐛 Troubleshooting

### "pygame not found"

```bash
pip install pygame
```

### "matplotlib not found"

```bash
pip install matplotlib
```

### "FileNotFoundError: examples/neural/..."

Make sure you're running from the project root:

```bash
cd d:\CodexTest\BinaryQuadTreeCPUTest
python Showcase/neural_demo.py
```

### Demo runs but shows black screen

- Check that `.geo` files exist in `examples/neural/`
- Try `--test` mode first to verify logic
- Update graphics drivers

---

## 📊 Performance

| Demo | Startup | Training | Memory |
|------|---------|----------|--------|
| `neural_demo.py` | <1s | Instant | ~50MB |
| `neural_pipeline_demo.py` | <1s | Fast | ~80MB |
| `kohonen_color_demo.py` | <1s | Medium | ~100MB |

---

## 🎨 Examples

### Neural Demo Output

```
============================================================
  .geo Neural Network Truth Table Tests
============================================================

--- Majority-3 Vote (threshold >= 2) ---
  IN0  IN1  IN2  |  OUT  Expected  Pass
  ------------------------------------------
   0   0   0   |   0    0    OK
   0   0   1   |   0    0    OK
   ...
```

### Pipeline Demo Output

```
Testing Pattern Recognition Pipeline...

1. Testing with pattern A:
   Recognized: {'class': 'A', 'confidence': 0.85, 'bmu': (2, 1)}

2. Training on all patterns...
```

### Color SOM Output

```
Testing Kohonen Color SOM...

Initial weights (random):
  (0,0): (191, 68, 91)
  (5,5): (132, 101, 95)

Training on 1000 random colors...
  Epoch 0: LR=0.300, Neighborhood=3.00, Avg Dist=160.6
```

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `../examples/neural/README.md` | Neural network overview |
| `../examples/neural/NEURAL_NETWORKS_FULL.md` | Complete reference |
| `../examples/neural/NEURAL_QUICK_REF.md` | Quick reference card |
| `../KOHONEN_QUICKSTART.md` | Color SOM guide |
| `../PIPELINE_COMPLETE.md` | Pipeline documentation |

---

## 🌟 Showcase Your Own Demos

Want to add a demo to the showcase?

1. Create your `.py` file in `Showcase/`
2. Edit `neural_showcase.py` and add to `DEMO_CATEGORIES`
3. Update this README

Example:

```python
DEMO_CATEGORIES = {
    "My Demos": [
        {
            "name": "My Awesome Demo",
            "file": "my_demo.py",
            "description": "Does something cool",
            "args": []
        }
    ]
}
```

---

## 🎯 Quick Reference

### What to Run

| Want to... | Run This |
|------------|----------|
| See neural networks in action | `neural_showcase.py` → #1 |
| Experiment with pattern recognition | `neural_showcase.py` → #2 |
| Watch colors self-organize | `neural_showcase.py` → #3 |
| Test without GUI | `*_demo.py --test` |
| See all options | `neural_showcase.py` |

### What NOT to Run

| File | Why |
|------|-----|
| `examples/neural/*.geo` | Loaded by Python, not standalone |
| `examples/neural_pipeline/*.geo` | Part of pipeline system |
| `patterns/*.py` | Data files, not executables |

---

**Enjoy exploring neural networks!** 🧠✨

*Built with the Binary Quad-Tree Geometric Grammar Engine*
