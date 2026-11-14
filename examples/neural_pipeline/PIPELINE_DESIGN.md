# Pattern Recognition Pipeline with Self-Organizing Memory

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT LAYER (5×5 pixels)                     │
│  [P00] [P01] [P02] [P03] [P04]                                 │
│  [P10] [P11] [P12] [P13] [P14]                                 │
│  [P20] [P21] [P22] [P23] [P24]   ← 25 binary input neurons     │
│  [P30] [P31] [P32] [P33] [P34]                                 │
│  [P40] [P41] [P42] [P43] [P44]                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓ (weighted connections)
┌─────────────────────────────────────────────────────────────────┐
│                  FEATURE MAP (3×3 SOM neurons)                  │
│  [F00] [F01] [F02]                                             │
│  [F10] [F11] [F12]   ← Each learns to recognize patterns       │
│  [F20] [F21] [F22]                                             │
│                                                                 │
│  Competition: Winner-take-all + neighborhood cooperation       │
│  Learning: Hebbian (weights move toward input pattern)         │
└─────────────────────────────────────────────────────────────────┘
                            ↓ (connections)
┌─────────────────────────────────────────────────────────────────┐
│                 ASSOCIATIVE MEMORY (Hopfield)                   │
│  [M0] [M1] [M2] [M3] [M4]                                      │
│  [M5] [M6] [M7] [M8] [M9]   ← Stores learned patterns          │
│                                                                 │
│  Recall: Partial input → Complete pattern                      │
│  Dynamics: Energy minimization                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓ (readout)
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER (Classification)                │
│  [C0] [C1] [C2] [C3] [C4]   ← Class probabilities              │
│                                                                 │
│  Winner = recognized pattern class                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Execution Phases (tick%16)

| Phase | Layer | Operation |
|-------|-------|-----------|
| 0-1 | Input | Present pattern, encode as activations |
| 2-3 | Feature Map | Compute distances to weight vectors |
| 4-5 | Feature Map | Find winner (minimum distance) |
| 6-7 | Feature Map | Update winner + neighborhood weights |
| 8-9 | Memory | Map features to Hopfield pattern |
| 10-11 | Memory | Recurrent dynamics (energy minimization) |
| 12-13 | Memory | Converge to stored pattern |
| 14-15 | Output | Read classification, reset |

---

## Learning Rules

### 1. Competitive Learning (Feature Map)

```
Winner: w_new = w_old + η * (input - w_old)
Neighbors: w_new = w_old + η_neighbor * (input - w_old)
```

### 2. Hebbian Learning (Memory Connections)

```
Δw_ij = η * state_i * state_j
(Strengthens connections between co-active neurons)
```

### 3. Pattern Storage (Outer Product Rule)

```
For each pattern P:
  w_ij += P_i * P_j  (for all i≠j)
```

---

## File Structure

```
examples/
├── neural_pipeline/
│   ├── pipeline_input.geo       # Input encoding (5×5 pixels)
│   ├── pipeline_feature_map.geo # SOM feature extraction
│   ├── pipeline_memory.geo      # Hopfield associative memory
│   ├── pipeline_output.geo      # Classification readout
│   ├── pipeline_training.geo    # Hebbian learning rules
│   └── pipeline_full.geo        # Complete integrated system
├── patterns/
│   ├── pattern_letters.geo      # Letter patterns (A, B, C, D, E)
│   ├── pattern_digits.geo       # Digit patterns (0-9)
│   └── pattern_shapes.geo       # Simple shapes
└── neural_pipeline.md           # Documentation
```

---

## Training Modes

### Mode 1: Unsupervised (Self-Organizing)

```
Loop:
  1. Present random input pattern
  2. Feature map finds winner
  3. Update weights toward input
  4. Repeat with different patterns
```

**Result:** Feature map self-organizes to recognize input statistics

### Mode 2: Supervised (Pattern Storage)

```
For each training pattern:
  1. Present pattern to memory layer
  2. Store via Hebbian learning
  3. Verify recall with partial cue
```

**Result:** Memory stores patterns for later recall

### Mode 3: Hybrid (Feature → Memory)

```
Loop:
  1. Present pattern → feature map
  2. Feature winner activates memory
  3. Memory stores feature→pattern association
  4. Test recall with novel input
```

**Result:** System learns to classify and recall patterns

---

## Usage Examples

### Training Mode

```python
from neural_pipeline import PatternPipeline

pipeline = PatternPipeline()

# Training phase
patterns = [
    # 5×5 binary patterns (example: letters)
    [1,0,1,0,0,  1,0,1,0,0,  1,1,1,0,0,  1,0,1,0,0,  1,0,1,0,0],  # A
    [1,1,1,0,0,  1,0,0,0,0,  1,1,1,0,0,  1,0,0,0,0,  1,1,1,0,0],  # B
    [1,1,1,0,0,  1,0,0,0,0,  1,0,0,0,0,  1,0,0,0,0,  1,1,1,0,0],  # C
]

print("Training feature map...")
for epoch in range(100):
    for pattern in patterns:
        pipeline.train(pattern)

print("Storing patterns in memory...")
for i, pattern in enumerate(patterns):
    pipeline.store_pattern(i, pattern)

print("Training complete!")
```

### Recognition Mode

```python
# Test with noisy/partial patterns
test_pattern = [1,0,1,0,0,  1,0,1,0,0,  1,1,1,0,0,  1,0,0,0,0,  1,0,1,0,0]  # Noisy A

result = pipeline.recognize(test_pattern)
print(f"Recognized as pattern {result['class']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Recalled pattern: {result['recalled']}")
```

---

## Key Parameters

| Parameter | Symbol | Default | Description |
|-----------|--------|---------|-------------|
| Learning rate (feature) | η_f | 0.1 | How fast feature map learns |
| Learning rate (memory) | η_m | 0.05 | How fast memory stores patterns |
| Neighborhood radius | σ | 1.0 | Size of SOM neighborhood |
| Competition strength | κ | 2.0 | Winner-take-all aggressiveness |
| Memory capacity | N_p | 5 | Max patterns to store |

---

## Expected Results

### After Training

1. **Feature Map Self-Organization**
   - Different neurons respond to different pattern features
   - Topological ordering emerges (similar features cluster together)
   - Weight vectors converge to prototype patterns

2. **Memory Storage**
   - Patterns stored as attractors
   - Partial cues recall complete patterns
   - Noise tolerance increases with training

3. **Classification**
   - Novel patterns classified by similarity
   - Confidence reflects match quality
   - Generalization to unseen variations

---

## Advanced Features

### Pattern Completion

```
Input:  █░█░█
        █░█░█   (partial/noisy)
        ███░█
        █░█░█
        █░█░█

Memory Recall:
        █░█░█
        █░█░█   (complete pattern)
        ███░█
        █░█░█
        █░█░█
```

### Noise Tolerance

```
Input:  █▓█░█   (▓ = flipped pixel, noise)
        █░█░█
        ███░█
        █░█░█
        █░█░█

Output: █░█░█   (noise removed)
        █░█░█
        ███░█
        █░█░█
        █░█░█
```

### Pattern Interpolation

```
Train on: Pattern A and Pattern B
Present:  50% A + 50% B (morphed)
Result:   System settles to nearest stored attractor
```

---

## Implementation Notes

### Weight Representation

Weights stored as cell variables:
```geo
# Feature neuron at (r,c) has weight vector
var_w0, var_w1, ..., var_w24  (25 weights for 5×5 input)
```

### Distance Computation

Manhattan distance (simplified):
```geo
ACCUM_VAR dist N input_i 1
INCR_VAR dist -var_wi  # dist += |input - weight|
```

### Winner Selection

Threshold-based competition:
```geo
RULE IF var_dist<50 AND NOT signal=winner_found
     THEN HOLD + SET_VAR winner 1 + EMIT winner_found
```

---

## Troubleshooting

### Problem: Feature map doesn't self-organize

**Solutions:**
- Increase learning rate (η_f = 0.1 → 0.2)
- Increase neighborhood radius (σ = 1.0 → 2.0)
- Present more diverse training patterns
- Train for more epochs

### Problem: Memory doesn't recall patterns

**Solutions:**
- Check patterns are sufficiently different (orthogonal)
- Reduce number of stored patterns (capacity limit)
- Increase recurrent connection weights
- Verify Hebbian learning rule implementation

### Problem: Classification accuracy low

**Solutions:**
- Train feature map longer
- Adjust competition strength (κ)
- Use more feature neurons (3×3 → 5×5)
- Normalize input patterns

---

## Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Recognition accuracy | >90% | Correct classifications / total |
| Noise tolerance | 20% flipped pixels | Accuracy with noise |
| Pattern completion | 50% → 100% | Recall from partial cue |
| Training convergence | <100 epochs | When weights stabilize |
| Memory capacity | 5-7 patterns | Max storable patterns |

---

## Next Steps

1. **Implement core .geo scripts** (following this design)
2. **Create Python wrapper** for training and testing
3. **Build visualizer** to watch self-organization
4. **Test with letter/digit patterns**
5. **Experiment with parameters** for optimal performance

---

**This system combines:**
- Self-organizing maps (unsupervised feature learning)
- Hopfield networks (associative memory)
- Hebbian learning (biological plasticity)
- Competitive dynamics (winner-take-all)

**All implemented in `.geo` — one unified spatial computation framework!** 🧠✨
