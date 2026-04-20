# Neural Networks in .geo

Using the Binary Quad-Tree Geometric Grammar Engine as a neural computation substrate.

## Overview

The `.geo` language's tick-synchronous grid updates, cell variables, neighbor reads, and signal broadcasting map naturally to neural network primitives:

| Neural Concept | .geo Primitive |
|---|---|
| Neuron activation | Cell variable (`SET_VAR a 100`) |
| Weighted connection | `ACCUM_VAR sum DIR source weight` |
| Threshold / ReLU | `CLAMP_VAR name lo hi` + conditional (`var_sum>=100`) |
| Layer propagation | `tick%4` phased execution |
| Neuron identity | `own_prog=` (multi-program grid) or `family=` |
| Output signal | `EMIT` / `signal=` or family switch (`SWITCH Y_LOOP`) |
| Spatial topology | Cardinal neighbor layout (N/S/E/W) |

## Demos

### 1. Majority-3 Vote (`neural_majority3.geo`)

A **Threshold Logic Unit** that outputs 1 when at least 2 of 3 inputs are ON.

```
Grid layout (3x3, plus-shaped):

      col0   col1   col2
row2: [___]  [IN0]  [___]
row1: [IN1]  [HID]  [IN2]
row0: [___]  [OUT]  [___]
```

**How it works:**
- Inputs are GATE cells: `mask=1111` (ON) or `mask=0000` (OFF)
- Hidden neuron (X_LOOP) counts active neighbors using `nb_mask_count=1111:N`
- When count >= 2, it emits a `fire` signal
- Output neuron (Z_LOOP) switches to Y_LOOP upon receiving the signal

**Key rules:**
```
RULE IF family=X_LOOP AND nb_mask_count=1111:2
     THEN HOLD + SET_VAR act 1 + EMIT fire

RULE IF family=Z_LOOP AND signal=fire
     THEN SWITCH Y_LOOP
```

**No engine modifications needed** - works with the base `.geo` feature set.

### 2. XOR Perceptron (`neural_xor.geo`)

A **2-layer perceptron** solving XOR, the classic non-linearly-separable problem.

```
Grid layout (3x3):

      col0     col1    col2
row2: [IN0]    [H0]    [IN1]
row1: [pad]    [OUT]   [pad]
row0: [IN0']   [H1]    [IN1']
```

**Architecture:**
- **Layer 1**: IN0, IN1 (and relay copies IN0', IN1') store activation in variable `a`
- **Layer 2**:
  - H0 = OR gate (threshold=100): fires when either input is ON
  - H1 = AND gate (threshold=200): fires only when both inputs are ON
- **Layer 3**: OUT = H0 AND NOT H1 = XOR
  - Excitatory connection from H0 (weight +1)
  - Inhibitory connection from H1 (weight -1)

**Key rules:**
```
# Hidden neuron accumulates weighted inputs (dot product)
RULE IF own_prog=h0 AND tick%4=2
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum W a 1
          + ACCUM_VAR sum E a 1
          + CLAMP_VAR sum 0 200

# Threshold activation
RULE IF own_prog=h0 AND tick%4=3 AND var_sum>=100
     THEN HOLD + SET_VAR a 100

# Output: excitatory + inhibitory connections
RULE IF own_prog=output AND tick%4=0
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum N a 1    # H0 (excitatory)
          + ACCUM_VAR sum S a -1   # H1 (inhibitory)
          + CLAMP_VAR sum -100 100
```

**Requires engine additions**: `ACCUM_VAR`, `CLAMP_VAR`, neighbor variable reads.

## Engine Extensions for Neural Computation

Three features were added to `BinaryQuadTreeTest.py`:

### `ACCUM_VAR target direction source [weight]`
Reads a neighbor cell's variable and accumulates it into a local variable with an optional weight multiplier. This is the fundamental **dot product** operation of neural networks.

```
ACCUM_VAR sum W a 1     # sum += west_neighbor.a * 1
ACCUM_VAR sum S a -1    # sum += south_neighbor.a * (-1)  (inhibitory)
```

### `CLAMP_VAR name lo hi`
Bounds a variable to a range. Acts as a **saturation/activation function** (ReLU when lo=0, or bounded for stability).

```
CLAMP_VAR sum 0 200     # sum = max(0, min(200, sum))
```

### Neighbor variable conditions
Read a neighbor cell's variable for threshold checks:

```
nb_var_N_activation>=50   # north neighbor's "activation" var >= 50
nb_var_S_sum<100          # south neighbor's "sum" var < 100
```

## Running the Demo

```bash
# Interactive GUI (pygame)
python neural_demo.py

# Console truth table tests
python neural_demo.py --test
```

**GUI Controls:**
- **Click** input cells to toggle ON/OFF
- **TAB** to switch between Majority and XOR demos
- **SPACE** to pause/resume
- **T** to print truth tables to console
- **R** to reset

## Truth Tables

### Majority-3
```
IN0  IN1  IN2  |  OUT
 0    0    0   |   0
 0    0    1   |   0
 0    1    0   |   0
 0    1    1   |   1
 1    0    0   |   0
 1    0    1   |   1
 1    1    0   |   1
 1    1    1   |   1
```

### XOR
```
IN0  IN1  |  OUT
 0    0   |   0
 0    1   |   1
 1    0   |   1
 1    1   |   0
```

## Why This Matters

1. **ACCUM_VAR is a dot product** - the same operation at the core of every neural network, from perceptrons to transformers. The `.geo` engine performs it in massively parallel, spatially-local steps.

2. **Spatial computation** - neurons are physical cells on a grid. Connectivity is determined by adjacency, not abstract weight matrices. This mirrors biological neural tissue and neuromorphic hardware.

3. **Tick-synchronous snapshots** - all cells see the previous tick's state, enabling clean layer-by-layer propagation without race conditions. This is equivalent to synchronous digital circuit simulation.

4. **Composability** - the same `.geo` rule syntax that drives cellular automata, ecosystem simulations, and territory games also implements neural logic. One engine, many paradigms.
