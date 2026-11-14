# Neural Network Demo - Analysis & Improvement Guide

## Executive Summary

Your `neural_demo.py` is a **pygame-based visualizer** that demonstrates how `.geo` scripts can implement neural network computation using the Binary Quad-Tree Geometric Grammar Engine.

---

## How It Uses `.geo`

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    neural_demo.py                           │
│  (Pygame visualizer + Python network wrapper classes)       │
│                                                             │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │ MajorityNetwork  │    │   XORNetwork     │              │
│  │                  │    │                  │              │
│  │ Loads:           │    │ Loads:           │              │
│  │ neural_majority3 │    │ neural_xor.geo   │              │
│  │ .geo             │    │                  │              │
│  └──────────────────┘    └──────────────────┘              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    .geo Scripts                             │
│  (Declarative neural computation rules)                     │
│                                                             │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │ neural_majority3 │    │ neural_xor.geo   │              │
│  │ .geo             │    │                  │              │
│  │                  │    │                  │              │
│  │ • nb_mask_count  │    │ • ACCUM_VAR      │              │
│  │ • EMIT/signal    │    │ • CLAMP_VAR      │              │
│  │ • SWITCH family  │    │ • tick%4 phases  │              │
│  └──────────────────┘    └──────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### Current `.geo` Files

**Location:** `examples/neural/`

| File | Purpose | Key Features |
|------|---------|--------------|
| `neural/neural_majority3.geo` | 3-input majority vote | `nb_mask_count`, `EMIT`, `SWITCH` |
| `neural/neural_xor.geo` | XOR perceptron | `ACCUM_VAR`, `CLAMP_VAR`, weighted connections |
| `neural/neural_sigmoid.geo` | Sigmoid activation | Piecewise linear approximation |
| `neural/neural_perceptron.geo` | Multi-input perceptron | 4 inputs, adjustable weights |
| `neural/neural_hopfield.geo` | Hopfield memory | Associative recall |
| `neural/neural_kohonen.geo` | Kohonen SOM | Self-organizing map |
| `neural/neural_cnn_edge.geo` | CNN edge detector | Sobel filters |
| `neural/neural_lstm_cell.geo` | LSTM cell | Gated recurrent unit |

### How Networks Work

**1. Majority-3 Network** (`neural_majority3.geo`)

```
Grid Layout (3×3, plus-shaped):
      col0   col1   col2
row2: [___]  [IN0]  [___]
row1: [IN1]  [HID]  [IN2]
row0: [___]  [OUT]  [___]

Computation:
  • Inputs: GATE_ON (1111) = 1, GATE_OFF (0000) = 0
  • Hidden: X_LOOP counts active neighbors with nb_mask_count=1111:N
  • Output: Z_LOOP → Y_LOOP when receives "fire" signal

Rules:
  IF nb_mask_count=1111:3 THEN HOLD + SET_VAR act 1 + EMIT fire
  IF nb_mask_count=1111:2 THEN HOLD + SET_VAR act 1 + EMIT fire
  IF signal=fire THEN SWITCH Y_LOOP (output=1)
```

**2. XOR Network** (`neural_xor.geo`)

```
Grid Layout (3×3):
      col0     col1    col2
row2: [IN0]    [H0]    [IN1]
row1: [pad]    [OUT]   [pad]
row0: [IN0']   [H1]    [IN1']

Computation (tick%4 phased):
  Phase 0: Inputs set var "a" (100=on, 0=off)
  Phase 2: Hidden neurons accumulate weighted inputs
           H0 = OR (threshold=100)
           H1 = AND (threshold=200)
  Phase 3: Output = H0 AND NOT H1 = XOR

Rules:
  ACCUM_VAR sum W a 1     # weighted dot product
  CLAMP_VAR sum 0 200     # activation bounding
  IF var_sum>=100 THEN SET_VAR a 100  # step activation
```

---

## What Can Be Improved

### 1. **Add More Network Types** ✅ CREATED

I've created 6 new `.geo` scripts to expand your neural network system:

| Script | Type | Features |
|--------|------|----------|
| `neural_sigmoid.geo` | Activation function | Piecewise linear sigmoid |
| `neural_perceptron.geo` | Multi-input perceptron | 4 inputs, adjustable weights |
| `neural_hopfield.geo` | Associative memory | Pattern storage, recurrent dynamics |
| `neural_kohonen.geo` | Self-organizing map | Competitive learning |
| `neural_cnn_edge.geo` | Convolutional filter | Sobel edge detection |
| `neural_lstm_cell.geo` | LSTM cell | Gated recurrent unit |

### 2. **Better Documentation** ✅ CREATED

Created `NEURAL_NETWORKS_FULL.md` with:
- Complete reference for all 8 networks
- Neural primitives mapping table
- Execution model explanation
- Design principles and advanced topics
- Troubleshooting guide

### 3. **Code Organization**

**Current Structure:**
```
neural_demo.py (928 lines)
├── MajorityNetwork class
├── XORNetwork class
├── run_truth_table_tests()
└── run_gui()
```

**Suggested Improvements:**

```
neural_demo.py
├── BaseNetwork abstract class (new)
├── MajorityNetwork extends BaseNetwork
├── XORNetwork extends BaseNetwork
├── networks/ (new directory)
│   ├── __init__.py
│   ├── majority.py
│   ├── xor.py
│   ├── sigmoid.py
│   ├── perceptron.py
│   ├── hopfield.py
│   ├── kohonen.py
│   ├── cnn.py
│   └── lstm.py
├── gui/ (new directory)
│   ├── __init__.py
│   ├── renderer.py
│   ├── controls.py
│   └── colors.py
└── tests/ (new directory)
    ├── __init__.py
    └── test_networks.py
```

### 4. **Feature Additions**

#### a) Network Loader System

```python
# Dynamic network loading from .geo files
class NetworkRegistry:
    def __init__(self):
        self.networks = {}
    
    def register(self, name, geo_path, config):
        self.networks[name] = {
            'geo_path': geo_path,
            'config': config
        }
    
    def create(self, name):
        cfg = self.networks[name]
        return load_network(cfg['geo_path'], cfg['config'])

# Usage
registry = NetworkRegistry()
registry.register('majority3', 'examples/neural_majority3.geo', {...})
registry.register('xor', 'examples/neural_xor.geo', {...})
registry.register('sigmoid', 'examples/neural_sigmoid.geo', {...})
```

#### b) Visualization Enhancements

- **Weight visualization**: Color-code connections by weight value
- **Activation heatmaps**: Show variable values as color gradients
- **Signal propagation animation**: Trace signals through the network
- **3D view**: Render grid in perspective for larger networks

#### c) Training Support

```geo
# Backpropagation example (conceptual)
RULE IF tick%8=7 AND var_error>0
     THEN SET_VAR w (var_w + var_lr * var_error * var_input)
          + CLAMP_VAR w -100 100 AS weight_update
```

```python
# Python training loop
for epoch in range(100):
    for inputs, target in training_data:
        network.set_inputs(inputs)
        for t in range(16):
            network.step(t)
        output = network.read_output()
        error = target - output
        network.backpropagate(error)  # Update weights via .geo rules
```

### 5. **Engine Extensions Needed**

To fully realize the neural network potential, consider adding to `BinaryQuadTreeTest.py`:

| Feature | Purpose | Example |
|---------|---------|---------|
| `MATRIX_MUL` | Dense layer computation | `MATRIX_MUL weights inputs` |
| `CONV2D` | 2D convolution | `CONV2D 3x3 kernel` |
| `SOFTMAX` | Probability distribution | `SOFTMAX outputs` |
| `DROPOUT` | Regularization | `DROPOUT 0.5` |
| `BATCH_NORM` | Normalization | `BATCH_NORM mean var` |

---

## Cool New Systems to Build

### 1. **Pattern Recognition Pipeline**

```
Input (5×5 pixels) → CNN Edge Detector → Feature Map → 
Hopfield Memory → Classification Output

.geo scripts:
  neural_cnn_edge.geo + neural_hopfield.geo + classifier.geo
```

### 2. **Sequence Generator**

```
LSTM Cell → Output → Feedback → Next Prediction

Uses:
  neural_lstm_cell.geo with recurrent connections
  
Applications:
  - Music generation
  - Text prediction
  - Time series forecasting
```

### 3. **Self-Organizing Feature Map**

```
2D Grid of SOM Neurons → Topological Organization

Uses:
  neural_kohonen.geo expanded to 5×5 grid
  
Visualization:
  Color-coded neurons by preferred input pattern
```

### 4. **Generative Adversarial Network**

```
Generator Network ←→ Discriminator Network
      ↑                    ↓
      └──── Competition ───┘

.geo implementation:
  generator.geo + discriminator.geo + competition_rules.geo
```

### 5. **Neural Turing Machine**

```
Controller (LSTM) → Read/Write Heads → External Memory

Components:
  neural_lstm_cell.geo + memory_matrix.geo + addressing.geo
```

---

## Quick Start Guide

### Running the Demo

```bash
# Interactive GUI
python neural_demo.py

# Console tests
python neural_demo.py --test
```

### Creating a New Network

**Step 1:** Create `.geo` script

```geo
# examples/neural/neural_mynetwork.geo
NAME neural_mynetwork

# Define your architecture
RULE IF own_prog=input AND tick%4=0
     THEN HOLD + SET_VAR activation 100

RULE IF own_prog=neuron AND tick%4=2
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum W activation 1
          + CLAMP_VAR sum 0 200

DEFAULT HOLD
```

**Step 2:** Add Python wrapper

```python
class MyNetwork:
    def __init__(self):
        geo_path = "examples/neural_mynetwork.geo"
        self.program = load_geo(geo_path)
        self._build()
    
    def _build(self):
        def mask_fn(r, c):
            # Define initial masks
            return X_LOOP[0]
        
        self.grid = Grid.make(3, 3, self.program, init_mask_fn=mask_fn)
    
    def step(self, tick):
        self.grid.step(tick)
    
    def read_output(self):
        # Read network output
        pass
```

**Step 3:** Add to GUI

```python
networks = [MajorityNetwork(), XORNetwork(), MyNetwork()]
```

---

## Recommended Next Steps

### Immediate (Week 1)
1. ✅ Review new `.geo` scripts I created
2. Test each network with modified `neural_demo.py`
3. Read `NEURAL_NETWORKS_FULL.md` for concepts

### Short-term (Month 1)
1. Refactor code into modular structure
2. Add network loader system
3. Implement 2-3 new networks from suggestions
4. Create tutorial videos

### Medium-term (3 Months)
1. Add training capabilities
2. Build pattern recognition pipeline
3. Create example gallery
4. Write comprehensive API documentation

### Long-term (6+ Months)
1. Engine extensions for matrix operations
2. GPU acceleration
3. Network composition system
4. Integration with ML frameworks (PyTorch export?)

---

## Key Insights

### Why This Approach Is Unique

1. **Spatial Computation**: Neurons are physical cells on a grid, not abstract matrix elements
2. **Massive Parallelism**: All cells update simultaneously (GPU-style)
3. **Data-Driven**: Networks defined in `.geo` scripts, not hard-coded
4. **Composability**: Same rules drive neural nets, cellular automata, terrain generation
5. **Visual Debugging**: Watch activation propagate through the network

### Neural Concepts Mapped to `.geo`

| Neural Network | `.geo` Implementation |
|----------------|----------------------|
| Neuron | Cell with `own_prog` identity |
| Activation | `SET_VAR a VALUE` |
| Weight | `ACCUM_VAR ... weight` |
| Bias | `SET_VAR sum BIAS` before accumulation |
| Layer | `tick%N` phase separation |
| Forward Prop | Sequential phase execution |
| Recurrence | Neighbor feedback loops |
| Learning | `SET_VAR w (w + delta)` |

---

## Troubleshooting

### Common Issues

**Network not firing?**
- Check `ACCUM_VAR` directions match grid layout
- Verify thresholds are reachable
- Ensure `tick%N` phases are sequenced correctly

**Weights not updating?**
- Confirm `SET_VAR` syntax (no spaces in var names)
- Check `CLAMP_VAR` bounds
- Verify learning rate is sufficient

**Visualization broken?**
- Ensure `active_cells()` matches activation logic
- Check `get_connections()` returns correct pairs
- Verify cell roles are labeled

---

## Resources

- `GEO_LANGUAGE.md` — Full `.geo` language reference
- `NEURAL_NETWORKS_FULL.md` — Neural network system documentation
- `neural_demo.py` — Interactive visualizer
- `examples/neural_*.geo` — Network implementations

---

**Ready to build the future of spatial neural computation! 🧠✨**
