# Neural Networks in `.geo`

Neural network implementations using the Binary Quad-Tree Geometric Grammar Engine.

---

## Overview

This directory contains `.geo` scripts that implement various neural network architectures using:
- Cell variables for activations
- Neighbor communication for weighted connections
- Tick-synchronous updates for layer propagation
- Conditional rules for activation functions

---

## Available Networks

### 1. Majority-3 Vote (`neural_majority3.geo`)
**Type:** Threshold Logic Unit  
**Complexity:** ⭐ Beginner  
**Description:** 3-input majority vote network

```
Architecture: 3 inputs → 1 hidden (threshold=2) → 1 output
```

---

### 2. XOR Perceptron (`neural_xor.geo`)
**Type:** 2-Layer Perceptron  
**Complexity:** ⭐⭐ Intermediate  
**Description:** Solves XOR problem (non-linearly separable)

```
Architecture: 2 inputs → [H0=OR, H1=AND] → OUT=XOR
```

---

### 3. Sigmoid Activation (`neural_sigmoid.geo`)
**Type:** Activation Function  
**Complexity:** ⭐⭐ Intermediate  
**Description:** Piecewise linear sigmoid approximation

```
Function: σ(x) ≈ clamp((x + 3) / 6, 0, 1)
```

---

### 4. Multi-Input Perceptron (`neural_perceptron.geo`)
**Type:** Single-Layer Perceptron  
**Complexity:** ⭐⭐ Intermediate  
**Description:** 4 inputs with adjustable weights

```
Computation: output = step(w0·i0 + w1·i1 + w2·i2 + w3·i3 - threshold)
```

---

### 5. Hopfield Network (`neural_hopfield.geo`)
**Type:** Recurrent Associative Memory  
**Complexity:** ⭐⭐⭐ Advanced  
**Description:** Pattern storage and recall

```
Features: Content-addressable memory, pattern completion
```

---

### 6. Kohonen SOM (`neural_kohonen.geo`)
**Type:** Self-Organizing Map  
**Complexity:** ⭐⭐⭐ Advanced  
**Description:** Unsupervised competitive learning

```
Features: Winner-take-all, neighborhood cooperation
```

---

### 7. CNN Edge Detector (`neural_cnn_edge.geo`)
**Type:** Convolutional Neural Network  
**Complexity:** ⭐⭐⭐ Advanced  
**Description:** Sobel edge detection

```
Filters: Sobel X (vertical), Sobel Y (horizontal)
```

---

### 8. LSTM Cell (`neural_lstm_cell.geo`)
**Type:** Gated Recurrent Unit  
**Complexity:** ⭐⭐⭐⭐ Expert  
**Description:** LSTM-style memory cell

```
Gates: Forget, Input, Output
Memory: Cell state with gating
```

---

## Interactive Demos

### Neural Network Visualizer
```bash
python neural_demo.py
```
- Visualize Majority-3 and XOR networks
- Interactive input toggling
- Real-time activation display

### Kohonen Color SOM
```bash
python kohonen_color_demo.py
```
- 10×10 color map self-organization
- Interactive training
- Beautiful visual emergence

### Pattern Recognition Pipeline
```bash
python neural_pipeline_demo.py
```
- Complete pattern recognition system
- Self-organizing feature maps
- Associative memory recall

---

## Documentation

| File | Description |
|------|-------------|
| `NEURAL_NETWORKS_FULL.md` | Complete neural network reference |
| `NEURAL_QUICK_REF.md` | Quick reference card |
| `NEURAL_NETWORKS.md` | Original documentation |

---

## Neural Primitives

| Concept | `.geo` Implementation |
|---------|----------------------|
| Neuron | `own_prog=` cell identity |
| Activation | `SET_VAR a VALUE` |
| Weight | `ACCUM_VAR ... weight` |
| Threshold | `CLAMP_VAR` + conditional |
| Layer | `tick%N` phase separation |
| Learning | `SET_VAR w (w + delta)` |

---

## Usage Example

```python
from src import load_geo, Grid

# Load a neural network
program = load_geo("neural/neural_majority3.geo")

# Create grid
grid = Grid.make(3, 3, program)

# Run simulation
for tick in range(10):
    grid.step(tick)
```

---

## Contributing

When adding new neural networks:
1. Follow naming: `neural_<name>.geo`
2. Include architecture diagram in comments
3. Document execution phases
4. Provide expected behavior
5. Test with visualizer

---

## References

- [GEO_LANGUAGE.md](../GEO_LANGUAGE.md) - Language reference
- [KOHONEN_QUICKSTART.md](../KOHONEN_QUICKSTART.md) - Color SOM guide
- [PIPELINE_COMPLETE.md](../PIPELINE_COMPLETE.md) - Pattern recognition pipeline

---

**Where 4-bit spatial masks meet neural computation!** 🧠✨
