# Pattern Recognition Pipeline with Self-Organizing Memory

## Overview

A complete neural network system that **learns to recognize and recall patterns** using:

- **Self-Organizing Maps (SOM)** for unsupervised feature learning
- **Hopfield Networks** for associative memory storage
- **Hebbian Learning** for biological-style plasticity
- **`.geo` scripts** for declarative neural computation

---

## Quick Start

```bash
# Run interactive visualizer
python neural_pipeline_demo.py

# Run console test
python neural_pipeline_demo.py --test
```

### Interactive Controls

| Key | Action |
|-----|--------|
| **Click/Drag** | Draw on 5×5 input grid |
| **T** | Toggle training mode |
| **R** | Recall pattern from memory |
| **C** | Clear input |
| **SPACE** | Random pattern |
| **L** | Load known pattern (A-Z, 0-9) |
| **P** | Train on all patterns (10 epochs) |
| **Esc** | Quit |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT LAYER (5×5)                        │
│  25 binary pixels - user draws patterns here               │
└─────────────────────────────────────────────────────────────┘
                        ↓ (full connectivity)
┌─────────────────────────────────────────────────────────────┐
│                 FEATURE MAP (3×3 SOM)                       │
│  9 neurons, each with 25-dimensional weight vector         │
│  Learns via competitive learning + neighborhood cooperation │
└─────────────────────────────────────────────────────────────┘
                        ↓ (pattern mapping)
┌─────────────────────────────────────────────────────────────┐
│               MEMORY LAYER (10 neurons)                     │
│  Hopfield network with recurrent connections               │
│  Stores patterns as attractors via Hebbian learning        │
└─────────────────────────────────────────────────────────────┘
                        ↓ (readout)
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT                                   │
│  Recognition result + recalled pattern                     │
└─────────────────────────────────────────────────────────────┘
```

---

## How It Works

### 1. Input Encoding

User draws a 5×5 binary pattern:
```
█░█░█  →  [1,0,1,0,0,
█░█░█      1,0,1,0,0,
███░█      1,1,1,0,0,
█░█░█      1,0,1,0,0,
█░█░█]     1,0,1,0,0]
```

### 2. Feature Map (SOM) Processing

**Step 1: Distance Computation**
Each feature neuron computes distance to input:
```
distance = Σ|input[i] - weight[i]|
```

**Step 2: Winner Selection**
Neuron with minimum distance wins:
```
winner = argmin(distance)
```

**Step 3: Weight Update**
Winner and neighbors move toward input:
```
w_new = w_old + lr * (input - w_old)
```

### 3. Memory Storage (Hebbian Learning)

When training, patterns are stored via outer product rule:
```
For each pattern P:
  w_ij += P_i * P_j  (for all i≠j)
```

### 4. Pattern Recall

Memory converges to nearest stored attractor:
```
For each neuron i:
  h = Σ_j (w_ij * state_j)
  state_i = sign(h)
```

---

## .geo Scripts

### File Structure

```
examples/neural_pipeline/
├── pipeline_input.geo       # Input encoding
├── pipeline_feature_map.geo # SOM feature extraction
├── pipeline_memory.geo      # Hopfield memory
├── pipeline_training.geo    # Hebbian learning rules
├── pipeline_full.geo        # Integrated system
└── patterns/
    ├── pattern_letters.py   # A-Z patterns
    └── pattern_digits.py    # 0-9 patterns
```

### Key .geo Rules

#### Input Encoding (`pipeline_input.geo`)

```geo
RULE IF own_prog=input_pixel AND tick%16=0 AND mask=1111
     THEN HOLD + SET_VAR pixel 100 + SET_VAR active 100

RULE IF own_prog=input_pixel AND tick%16=0 AND mask=0000
     THEN HOLD + SET_VAR pixel 0 + SET_VAR active 0
```

#### SOM Distance (`pipeline_feature_map.geo`)

```geo
RULE IF own_prog=feature AND tick%16=2
     THEN HOLD + SET_VAR dist 0
          + ACCUM_VAR dist N active 1
          + ACCUM_VAR dist S active 1
          + ACCUM_VAR dist E active 1
          + ACCUM_VAR dist W active 1
```

#### Winner Selection (`pipeline_feature_map.geo`)

```geo
RULE IF own_prog=feature AND tick%16=4 AND var_dist<80
     THEN HOLD + SET_VAR winner 1 + EMIT winner_found
```

#### Hebbian Learning (`pipeline_training.geo`)

```geo
RULE IF tick%32=18 AND signal=hebbian_update
     THEN HOLD
          + SET_VAR delta_w (var_lr * var_pre * var_post / 10000)
          + EMIT update_weight var_delta_w
```

---

## Training Modes

### Mode 1: Unsupervised (Self-Organizing)

Feature map learns input statistics without labels:

```python
for epoch in range(100):
    for random_pattern in dataset:
        pipeline.set_input(random_pattern)
        pipeline.train_step()
```

**Result:** Feature map develops topological organization

### Mode 2: Supervised (Pattern Storage)

Store specific labeled patterns:

```python
for pattern in [A, B, C, D, E]:
    pipeline.set_input(pattern)
    pipeline.training_mode = True
    pipeline.train_step()
```

**Result:** Memory stores patterns for recall

### Mode 3: Hybrid (Feature → Memory)

Both layers learn together:

```python
pipeline.training_mode = True
for epoch in range(50):
    for pattern in dataset:
        pipeline.set_input(pattern)
        pipeline.train_step()
```

**Result:** End-to-end pattern recognition system

---

## Usage Examples

### Example 1: Basic Recognition

```python
from neural_pipeline_demo import PatternPipeline, PATTERNS

pipeline = PatternPipeline()

# Recognize pattern A
pipeline.set_input(PATTERNS['A'])
result = pipeline.recognize()

print(f"Class: {result['class']}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"BMU: {result['bmu']}")
```

### Example 2: Training and Recall

```python
# Train on all patterns
print("Training...")
for epoch in range(10):
    for pattern in PATTERNS.values():
        pipeline.set_input(pattern)
        pipeline.train_step()

print(f"Training complete (epoch {pipeline.epoch})")

# Test recall with noisy input
noisy_A = PATTERNS['A'].copy()
noisy_A[5] = 1 - noisy_A[5]  # Flip one bit

pipeline.set_input(noisy_A)
recalled = pipeline.recall()

print(f"Recalled from noisy input: {recalled}")
```

### Example 3: Pattern Completion

```python
# Partial pattern (only top half)
partial = [1,0,1,0,0,  1,0,1,0,0,  1,1,1,0,0,  0,0,0,0,0,  0,0,0,0,0]

pipeline.set_input(partial)
recalled = pipeline.recall()

print(f"Completed pattern: {recalled}")
# Expected: Full pattern A
```

---

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Learning rate (SOM) | 0.1 | How fast feature map learns |
| Neighborhood radius | 1 | Size of SOM neighborhood |
| Memory size | 10 | Number of storable patterns |
| Training epochs | 10-100 | Iterations for convergence |

---

## Expected Results

### After Training (10 epochs)

- **Recognition accuracy:** >80% on trained patterns
- **Noise tolerance:** Recognizes patterns with 1-2 flipped pixels
- **Pattern completion:** Recalls full patterns from 50% cues

### After Extended Training (100 epochs)

- **Feature map organization:** Similar patterns activate nearby neurons
- **Weight convergence:** Feature weights resemble prototype patterns
- **Memory capacity:** Stores 5-7 patterns reliably

---

## Visualization

### Input Grid
- **Green:** Active pixel (1)
- **Dark:** Inactive pixel (0)

### Feature Map
- **Green:** High similarity to input
- **Red:** Low similarity to input
- **Number:** Distance value

### Memory Layer
- **Green:** Active neuron (+1)
- **Dark:** Inactive neuron (-1)

### Recalled Pattern
- **Cyan:** Recalled active pixel
- **Dark:** Recalled inactive pixel

---

## Troubleshooting

### Problem: Recognition accuracy is low

**Solutions:**
1. Train for more epochs (50-100)
2. Use more distinct patterns
3. Increase learning rate (0.1 → 0.2)
4. Expand feature map (3×3 → 5×5)

### Problem: Memory doesn't recall patterns

**Solutions:**
1. Verify patterns are sufficiently different
2. Reduce number of stored patterns (capacity limit)
3. Increase recurrent connection weights
4. Check Hebbian learning implementation

### Problem: Feature map doesn't self-organize

**Solutions:**
1. Increase neighborhood radius (1 → 2)
2. Use learning rate decay schedule
3. Present more diverse training patterns
4. Initialize weights with more variance

---

## Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Recognition accuracy | >80% | Correct / total tests |
| Noise tolerance | 20% flipped | Accuracy with noise |
| Pattern completion | 50% → 100% | Recall from partial |
| Training convergence | <50 epochs | When weights stabilize |
| Memory capacity | 5-7 patterns | Max reliable storage |

---

## Advanced Features

### Pattern Interpolation

Train on patterns A and B, then present morphed input:
```
Input:  50% A + 50% B
Result: System settles to nearest attractor
```

### Noise Removal

```
Input:  █▓█░█  (▓ = noise)
        █░█░█
        ███░█
        █░█░█
        █░█░█

Output: █░█░█  (noise removed)
        █░█░█
        ███░█
        █░█░█
        █░█░█
```

### Sequential Learning

Learn patterns in sequence, test order recall:
```python
for pattern in [A, B, C, D, E]:
    pipeline.set_input(pattern)
    pipeline.train_step()

# Test: Does system remember sequence?
```

---

## Theoretical Background

### Self-Organizing Maps (Kohonen, 1982)

- **Competitive learning:** Neurons compete to respond to inputs
- **Topological ordering:** Spatially organized feature detection
- **Neighborhood function:** Cooperation between nearby neurons

### Hopfield Networks (Hopfield, 1982)

- **Recurrent dynamics:** Feedback connections create attractors
- **Energy minimization:** System converges to local minima
- **Content-addressable memory:** Partial cues recall complete patterns

### Hebbian Learning (Hebb, 1949)

- **Fire together, wire together:** Co-activation strengthens connections
- **Biological plausibility:** Matches synaptic plasticity in brains
- **Unsupervised:** No external error signal needed

---

## File Reference

| File | Purpose | Lines |
|------|---------|-------|
| `neural_pipeline_demo.py` | Main visualizer + pipeline class | ~550 |
| `pipeline_full.geo` | Integrated .geo rules | ~100 |
| `pattern_letters.py` | A-Z pattern definitions | ~150 |
| `pattern_digits.py` | 0-9 pattern definitions | ~50 |
| `PIPELINE_DESIGN.md` | Architecture documentation | ~300 |

---

## Next Steps

### Immediate Enhancements

1. **Better visualization:** Show weight vectors as mini-patterns
2. **Audio feedback:** Sound on recognition/recall
3. **Export/Import:** Save trained weights to file
4. **Batch training:** Train on multiple patterns simultaneously

### Medium-term Features

1. **Convolutional features:** Add edge detection preprocessing
2. **Multi-layer SOM:** Hierarchical feature extraction
3. **Recurrent memory:** LSTM-style gating for sequences
4. **Attention mechanism:** Focus on relevant input regions

### Long-term Vision

1. **Real-time learning:** Continual adaptation to new patterns
2. **Transfer learning:** Apply learned features to new tasks
3. **Generative capability:** Create novel patterns (not just recall)
4. **Multi-modal:** Process images, sounds, and text together

---

## Citation

If you use this in research:

```bibtex
@software{PatternPipeline2026,
  author = {Your Name},
  title = {Pattern Recognition Pipeline with Self-Organizing Memory},
  year = {2026},
  url = {https://github.com/sfdimarco/BinaryQuadTreeCPUTest}
}
```

---

## License

MIT License - See [LICENSE](../../LICENSE) file

---

## Acknowledgments

- **Tuevo Kohonen** - Self-Organizing Maps
- **John Hopfield** - Hopfield Networks
- **Donald Hebb** - Hebbian Learning theory
- **Salvatore DiMarco** - BinaryQuadTreeCPUTest framework

---

**"Where self-organization meets memory"** 🧠✨

*Built with the Binary Quad-Tree Geometric Grammar Engine*
