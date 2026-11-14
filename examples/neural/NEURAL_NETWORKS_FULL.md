# Neural Network Systems in `.geo`

A comprehensive framework for implementing neural networks using the Binary Quad-Tree Geometric Grammar Engine.

---

## Overview

This system demonstrates how `.geo` scripts can implement **neural computation** through:
- **Cell variables** → Neuron activations and states
- **Neighbor communication** → Weighted connections
- **Tick-synchronous updates** → Layer-by-layer propagation
- **Conditional rules** → Activation functions and gating

---

## Available Networks

### 1. **Majority-3 Vote** (`neural_majority3.geo`)
**Type:** Threshold Logic Unit  
**Complexity:** ⭐ Beginner  
**Features:** Simple threshold activation, signal broadcasting

```
Architecture:
  3 inputs → 1 hidden (threshold=2) → 1 output
  
Truth Table:
  000→0  001→0  010→0  011→1
  100→0  101→1  110→1  111→1
```

**Key Concepts:**
- `nb_mask_count` for neighbor counting
- `EMIT`/`signal` for inter-cell communication
- GATE family for binary input representation

---

### 2. **XOR Perceptron** (`neural_xor.geo`)
**Type:** 2-Layer Perceptron  
**Complexity:** ⭐⭐ Intermediate  
**Features:** Multi-layer network, excitatory/inhibitory connections

```
Architecture:
  2 inputs → [H0=OR, H1=AND] → OUT=XOR
  
Truth Table:
  00→0  01→1  10→1  11→0
```

**Key Concepts:**
- `ACCUM_VAR` for weighted dot products
- `CLAMP_VAR` for activation bounding
- `tick%4` phased execution for layer ordering
- Negative weights for inhibitory connections

---

### 3. **Sigmoid Activation** (`neural_sigmoid.geo`)
**Type:** Activation Function  
**Complexity:** ⭐⭐ Intermediate  
**Features:** Analog activation, piecewise linear approximation

```
Architecture:
  1 input → 1 sigmoid neuron → 1 output
  
Function:
  σ(x) ≈ clamp((x + 3) / 6, 0, 1)
```

**Key Concepts:**
- Piecewise linear sigmoid approximation
- Analog value representation (0-100 scale)
- Smooth activation vs. step function

---

### 4. **Multi-Input Perceptron** (`neural_perceptron.geo`)
**Type:** Single-Layer Perceptron  
**Complexity:** ⭐⭐ Intermediate  
**Features:** 4 inputs, adjustable weights, step activation

```
Architecture:
  4 inputs → weighted sum → step(threshold) → output
  
Computation:
  output = step(w0·i0 + w1·i1 + w2·i2 + w3·i3 - threshold)
```

**Key Concepts:**
- Weight storage in cell variables
- Configurable threshold
- Multi-input summation

---

### 5. **Hopfield Network** (`neural_hopfield.geo`)
**Type:** Recurrent Associative Memory  
**Complexity:** ⭐⭐⭐ Advanced  
**Features:** Pattern storage, content-addressable memory, energy minimization

```
Architecture:
  4 neurons with all-to-all recurrent connections
  
Stored Patterns:
  Pattern A: 1010 (diagonal)
  Pattern B: 0101 (anti-diagonal)
  
Recall:
  Partial input → converges to nearest stored pattern
```

**Key Concepts:**
- Recurrent connections
- Asynchronous updates
- Attractor dynamics
- Hebbian learning (weights from patterns)

---

### 6. **Kohonen Self-Organizing Map** (`neural_kohonen.geo`)
**Type:** Unsupervised Competitive Learning  
**Complexity:** ⭐⭐⭐ Advanced  
**Features:** Winner-take-all, neighborhood cooperation, self-organization

```
Architecture:
  4 inputs → 4 SOM neurons (1D map)
  
Learning:
  1. Present input pattern
  2. Find winner (min distance)
  3. Update winner + neighbors
  4. Repeat with different inputs
```

**Key Concepts:**
- Competitive learning
- Neighborhood function
- Weight adaptation
- Topological organization

---

### 7. **CNN Edge Detector** (`neural_cnn_edge.geo`)
**Type:** Convolutional Neural Network  
**Complexity:** ⭐⭐⭐ Advanced  
**Features:** Convolutional filters, Sobel edge detection, weight sharing

```
Architecture:
  5×5 input → 3×3 Sobel convolution → edge output
  
Filters:
  Sobel X: vertical edge detection
  Sobel Y: horizontal edge detection
  
Output:
  Gradient magnitude = |Gx| + |Gy|
```

**Key Concepts:**
- Local receptive fields
- Weight sharing (same kernel everywhere)
- Multi-channel convolution
- Non-maximum suppression

---

### 8. **LSTM Cell** (`neural_lstm_cell.geo`)
**Type:** Gated Recurrent Unit  
**Complexity:** ⭐⭐⭐⭐ Expert  
**Features:** Sequential memory, gating mechanisms, vanishing gradient solution

```
Architecture:
  [xt, ht-1] → [forget, input, output gates] → ct → ht
  
Gates:
  ft = σ(Wf·[ht-1, xt])  - What to forget
  it = σ(Wi·[ht-1, xt])  - What to store
  ot = σ(Wo·[ht-1, xt])  - What to output
  
Cell State:
  ct = ft·ct-1 + it·ct_cand
  
Hidden Output:
  ht = ot·tanh(ct)
```

**Key Concepts:**
- Gating mechanisms
- Cell state memory
- Sequential processing
- Gradient flow control

---

## Neural Primitives Reference

| Neural Concept | `.geo` Implementation | Example |
|----------------|----------------------|---------|
| **Neuron** | Cell with `own_prog` identity | `own_prog=neuron` |
| **Activation** | Cell variable `SET_VAR a VALUE` | `SET_VAR a 100` |
| **Weight** | Cell variable storing connection strength | `SET_VAR w 75` |
| **Synapse** | Neighbor read with `ACCUM_VAR` | `ACCUM_VAR sum N a 1` |
| **Dot Product** | Accumulate weighted inputs | `ACCUM_VAR sum DIR var weight` |
| **Threshold** | `CLAMP_VAR` + conditional | `CLAMP_VAR sum 0 200` |
| **Step Function** | `IF var_sum>=N THEN fire` | `IF var_sum>=100 THEN SWITCH Y_LOOP` |
| **Sigmoid** | Piecewise linear approximation | Multiple rules for different ranges |
| **Layer** | `tick%N` phase separation | `tick%4=0` inputs, `tick%4=2` hidden |
| **Feedforward** | Sequential phase execution | Phase 0→1→2→3 |
| **Recurrent** | Feedback via neighbor reads | `nb_var_N_state` |
| **Learning** | Update weights via `SET_VAR` | `SET_VAR w (w + lr * error)` |

---

## Execution Model

### Tick-Phased Propagation

Networks use `tick%N` to enforce layer ordering:

```
tick%4 = 0: Input layer sets activations
tick%4 = 1: (optional relay/copy)
tick%4 = 2: Hidden layer accumulates + activates
tick%4 = 3: Output layer reads hidden + decides
```

This ensures **synchronous updates** — all cells see the previous tick's state, preventing race conditions.

### Variable Naming Conventions

| Variable | Purpose | Typical Range |
|----------|---------|---------------|
| `a` | Activation | 0-100 |
| `sum` | Weighted sum | -200 to 200 |
| `w` | Weight | 0-100 (or -100 to 100) |
| `lr` | Learning rate | 1-20 (0.01-0.2 scaled) |
| `dist` | Distance metric | 0-400 |
| `ft, it, ot` | Gate values | 0-100 |
| `ct` | Cell state | -100 to 100 |
| `ht` | Hidden state | 0-100 |

---

## Usage

### Running the Visualizer

```bash
# Interactive GUI (requires pygame)
python neural_demo.py

# Console truth table tests
python neural_demo.py --test
```

### GUI Controls

| Key | Action |
|-----|--------|
| **Click** | Toggle input neurons ON/OFF |
| **TAB** | Switch between Majority and XOR demos |
| **SPACE** | Pause/resume simulation |
| **→** | Single-step (when paused) |
| **R** | Reset network |
| **T** | Print truth tables to console |
| **A** | Auto-cycle through all input combinations |
| **Esc** | Quit |

### Loading Custom Networks

To add a new network to `neural_demo.py`:

1. Create `.geo` file in `examples/`
2. Add network class following `MajorityNetwork`/`XORNetwork` pattern
3. Implement required methods:
   - `__init__`: Load `.geo`, define cell positions
   - `_build`: Create grid with mask/program functions
   - `set_inputs`, `toggle_input`: Input handling
   - `step`: Advance simulation
   - `read_output`: Read network output
   - `active_cells`: Return currently active cells
   - `get_connections`: Return weighted connections for visualization
   - `all_combos`, `expected`: Truth table testing

---

## Design Principles

### 1. **Spatial Locality**
Neurons are physical cells on a grid. Connectivity is determined by adjacency (N/S/E/W neighbors), not abstract weight matrices.

### 2. **Massive Parallelism**
All cells update simultaneously each tick. This is equivalent to GPU-style parallel neural computation.

### 3. **Data-Driven**
Networks are defined in `.geo` scripts, not hard-coded Python. This enables:
- Easy experimentation with architectures
- Visual debugging via family/state changes
- Composition via `INCLUDE` directives

### 4. **Composability**
Same `.geo` rules that drive neural networks also drive:
- Cellular automata (Conway's Life)
- Terrain generation
- Animation systems
- Ecosystem simulations

---

## Advanced Topics

### Weight Representation

Weights can be stored as:
- **Cell variables**: `SET_VAR w 75` (flexible, per-cell)
- **Neighbor program identity**: `own_prog=weight-high` vs `own_prog=weight-low`
- **Family membership**: Different families represent different weight ranges

### Learning Rules

Example Hebbian learning:
```geo
RULE IF tick%8=7 AND var_pre>=100 AND var_post>=100
     THEN INCR_VAR w 5 + CLAMP_VAR w 0 200 AS hebbian
```

Example error-based update:
```geo
RULE IF tick%8=7 AND var_error>0
     THEN INCR_VAR w (var_lr * var_error) AS delta_rule
```

### Multi-Layer Networks

Stack networks by chaining phases:
```
tick%12 = 0-2:   Layer 1 (input→hidden1)
tick%12 = 3-5:   Layer 2 (hidden1→hidden2)
tick%12 = 6-8:   Layer 3 (hidden2→output)
tick%12 = 9-11:  Reset/prepare next cycle
```

### Recurrent Networks

Feedback connections via neighbor reads:
```geo
RULE IF own_prog=recurrent AND tick%4=2
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum N state 1    # External input
          + ACCUM_VAR sum W prev_state 1  # Recurrent from previous tick
```

---

## Troubleshooting

### Network Not Firing?
- Check `ACCUM_VAR` directions match your grid layout
- Verify thresholds (`var_sum>=N`) are reachable
- Ensure `tick%N` phases are properly sequenced

### Weights Not Updating?
- Confirm `SET_VAR` syntax (no spaces in var names)
- Check `CLAMP_VAR` bounds aren't preventing changes
- Verify learning rate is large enough

### Visualization Issues?
- Ensure `active_cells()` matches your network's activation logic
- Check `get_connections()` returns correct source/dest pairs
- Verify cell roles are properly labeled

---

## Future Directions

### Planned Networks
- **RBM (Restricted Boltzmann Machine)**: Generative model with visible/hidden layers
- **Transformer Attention**: Self-attention mechanism for sequences
- **GAN (Generative Adversarial Network)**: Generator vs discriminator competition
- **Neural Turing Machine**: Differentiable memory access

### Engine Enhancements
- **Matrix operations**: Native `MATRIX_MUL` for dense layers
- **Backpropagation**: Automatic gradient computation
- **Batch processing**: Parallel evaluation of multiple inputs
- **GPU acceleration**: CUDA/Metal backend for large networks

---

## References

- [GEO_LANGUAGE.md](../GEO_LANGUAGE.md) — Full `.geo` language reference
- [BinaryQuadTreeTest.py](../src/binary_quad_tree.py) — Core engine implementation
- [neural_demo.py](../neural_demo.py) — Interactive visualizer

---

## Contributing

Add your own neural `.geo` scripts! Guidelines:
1. Follow naming: `neural_<name>.geo`
2. Include header comment with architecture diagram
3. Document execution phases
4. Provide truth table or expected behavior
5. Test with `neural_demo.py --test` or custom harness

---

**Created for the Binary Quad-Tree Geometric Grammar Engine**  
*Where 4-bit spatial masks meet neural computation*
