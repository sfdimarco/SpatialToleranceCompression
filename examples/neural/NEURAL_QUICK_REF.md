# Neural Network `.geo` Quick Reference

## Neural Primitives

| Concept | `.geo` Rule | Example |
|---------|-------------|---------|
| **Neuron** | Cell with `own_prog` | `own_prog=neuron` |
| **Activation** | Set variable | `SET_VAR a 100` |
| **Weight** | Store in var | `SET_VAR w 75` |
| **Synapse** | Neighbor read | `ACCUM_VAR sum N a 1` |
| **Dot Product** | Accumulate weighted | `ACCUM_VAR sum DIR var weight` |
| **Bias** | Add constant | `SET_VAR sum (var_sum + 50)` |
| **Step Activation** | Threshold check | `IF var_sum>=100 THEN SWITCH Y_LOOP` |
| **Sigmoid** | Piecewise clamp | Multiple rules for ranges |
| **ReLU** | Clamp lower bound | `CLAMP_VAR sum 0 999` |
| **Layer** | Tick phase | `tick%4=0` input, `tick%4=2` hidden |

---

## Execution Phases

### Simple Feedforward (tick%4)

```
tick%4 = 0: Input layer sets activations
tick%4 = 1: (optional relay/copy)
tick%4 = 2: Hidden layer accumulates + activates
tick%4 = 3: Output layer reads + decides
```

### Complex Network (tick%8)

```
tick%8 = 0: Inputs present pattern
tick%8 = 1-2: Compute gates / distances
tick%8 = 3-4: Accumulate weighted sums
tick%8 = 5-6: Apply activation / update
tick%8 = 7: Output + reset
```

---

## Variable Conventions

| Variable | Range | Purpose |
|----------|-------|---------|
| `a` | 0-100 | Activation |
| `sum` | -200 to 200 | Weighted sum |
| `w` | -100 to 100 | Weight |
| `lr` | 1-20 | Learning rate (scaled) |
| `error` | -100 to 100 | Error signal |
| `dist` | 0-400 | Distance metric |
| `ft, it, ot` | 0-100 | Gate values (LSTM) |
| `ct` | -100 to 100 | Cell state (LSTM) |
| `ht` | 0-100 | Hidden state |

---

## Network Templates

### Threshold Neuron

```geo
NAME threshold_neuron

# Input
RULE IF own_prog=input AND tick%2=0 AND mask=1111
     THEN HOLD + SET_VAR active 100

RULE IF own_prog=input AND tick%2=0 AND mask=0000
     THEN HOLD + SET_VAR active 0

# Neuron with threshold
RULE IF own_prog=neuron AND tick%2=1
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum W active 1
          + CLAMP_VAR sum 0 200

RULE IF own_prog=neuron AND tick%2=1 AND var_sum>=100
     THEN SWITCH Y_LOOP + SET_VAR output 1

RULE IF own_prog=neuron AND tick%2=1 AND var_sum<100
     THEN GATE_OFF + SET_VAR output 0

DEFAULT HOLD
```

### Multi-Input Perceptron

```geo
NAME perceptron_4input

# 4 inputs → weighted sum → step → output

# Inputs (phase 0)
RULE IF own_prog=input AND tick%4=0
     THEN HOLD + SET_VAR active (100 if mask=1111 else 0)

# Weights (phase 1)
RULE IF own_prog=weight AND tick%4=1
     THEN HOLD + SET_VAR contrib (var_active * var_w / 100)

# Summation (phase 2)
RULE IF own_prog=sum AND tick%4=2
     THEN HOLD + SET_VAR total 0
          + ACCUM_VAR total N contrib 1
          + ACCUM_VAR total S contrib 1
          + ACCUM_VAR total E contrib 1
          + ACCUM_VAR total W contrib 1
          + CLAMP_VAR total 0 400

# Output (phase 3)
RULE IF own_prog=output AND tick%4=3 AND var_total>=200
     THEN SWITCH Y_LOOP

RULE IF own_prog=output AND tick%4=3 AND var_total<200
     THEN GATE_OFF

DEFAULT HOLD
```

### Sigmoid Activation

```geo
NAME sigmoid_approx

# Piecewise linear sigmoid: σ(x) ≈ clamp((x+3)/6, 0, 1)

RULE IF own_prog=sigm AND tick%4=2 AND var_sum<50
     THEN HOLD + SET_VAR activation (var_sum * 0.5)

RULE IF own_prog=sigm AND tick%4=2 AND var_sum>=50 AND var_sum<=150
     THEN HOLD + SET_VAR activation (25 + (var_sum-50) * 0.75)

RULE IF own_prog=sigm AND tick%4=2 AND var_sum>150
     THEN HOLD + SET_VAR activation (100 + (var_sum-150) * 0.25)

DEFAULT HOLD
```

### Hebbian Learning

```geo
NAME hebbian_learning

# Δw = η * pre * post (correlation-based)

RULE IF tick%8=7 AND var_pre>=100 AND var_post>=100
     THEN INCR_VAR w 5
          + CLAMP_VAR w 0 200
          AS hebbian_potentiate

RULE IF tick%8=7 AND (var_pre<50 OR var_post<50)
     THEN INCR_VAR w -2
          + CLAMP_VAR w 0 200
          AS hebbian_depress

DEFAULT HOLD
```

### Delta Rule (Error-Based Learning)

```geo
NAME delta_rule

# Δw = η * error * input (supervised learning)

RULE IF tick%8=7
     THEN HOLD
          + SET_VAR error (var_target - var_output)
          + SET_VAR delta (var_lr * var_error * var_input)
          + SET_VAR w (var_w + var_delta)
          + CLAMP_VAR w -100 100
          AS weight_update

DEFAULT HOLD
```

---

## Grid Layouts

### 3×3 Majority Vote

```
      col0   col1   col2
row2: [___]  [IN0]  [___]
row1: [IN1]  [HID]  [IN2]
row0: [___]  [OUT]  [___]
```

### 3×3 XOR

```
      col0     col1    col2
row2: [IN0]    [H0]    [IN1]
row1: [pad]    [OUT]   [pad]
row0: [IN0']   [H1]    [IN1']
```

### 3×4 Perceptron

```
      col0      col1       col2
row2: [IN0]     [W0]       [IN1]
row1: [SUM]     [OUT]      [W1]
row0: [IN2]     [W2]       [IN3]
```

### 3×3 Hopfield

```
      col0       col1        col2
row2: [N0]       [pad]       [N1]
row1: [pad]      [CORE]      [pad]
row0: [N2]       [pad]       [N3]
```

### 3×4 SOM

```
      col0      col1      col2      col3
row2: [IN0]     [IN1]     [IN2]     [IN3]
row1: [N0]      [N1]      [N2]      [N3]
row0: [W0]      [W1]      [W2]      [W3]
```

### 5×5 CNN

```
      col0    col1    col2    col3    col4
row4: [I00]   [I01]   [I02]   [I03]   [I04]
row3: [I10]   [I11]   [I12]   [I13]   [I14]
row2: [I20]   [I21]   [K00]   [I23]   [I24]
row1: [I30]   [I31]   [I32]   [I33]   [I34]
row0: [I40]   [I41]   [I42]   [I43]   [I44]
```

### 4×3 LSTM

```
      col0       col1        col2
row3: [XT]       [pad]       [HT-1]
row2: [FT]       [IT]        [OT]
row1: [CELL]     [pad]       [CAND]
row0: [pad]      [HT]        [pad]
```

---

## Connection Patterns

### Feedforward

```geo
# Layer 1 → Layer 2 → Layer 3
RULE IF tick%4=0  # Input
     THEN HOLD + SET_VAR activation VALUE

RULE IF tick%4=2  # Hidden
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum DIR activation weight

RULE IF tick%4=3  # Output
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum DIR hidden_activation weight
```

### Recurrent

```geo
# Feedback from previous state
RULE IF tick%4=2
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum N external_input 1
          + ACCUM_VAR sum W prev_state 1  # Recurrent
          + CLAMP_VAR sum 0 200
```

### Lateral Inhibition

```geo
# Winner-take-all
RULE IF tick%8=4 AND var_dist<50  # Winner
     THEN HOLD + SET_VAR winner 1 + EMIT i_am_winner

RULE IF tick%8=5 AND signal=i_am_winner AND own_winner=0
     THEN HOLD + SET_VAR activation 0  # Suppress others
```

---

## Activation Functions

### Step

```geo
IF var_sum>=threshold THEN SWITCH Y_LOOP
ELSE GATE_OFF
```

### Sigmoid (Piecewise)

```geo
IF var_sum<50      THEN activation = var_sum * 0.5
IF 50<=sum<=150    THEN activation = 25 + (sum-50) * 0.75
IF var_sum>150     THEN activation = 100 + (sum-150) * 0.25
```

### ReLU

```geo
CLAMP_VAR sum 0 999  # Lower bound 0, no upper bound
SET_VAR activation var_sum
```

### Tanh (Approximation)

```geo
# Map [0,200] → [-100,100]
SET_VAR output (var_sum - 100)
```

---

## Common Patterns

### Copy/Relay

```geo
# Copy input activation to relay cell
RULE IF own_prog=relay AND tick%4=0
     THEN HOLD + SET_VAR a nb_var_N_a
```

### Signal Broadcasting

```geo
# Emit signal when active
RULE IF family=Y_LOOP AND tick%4=2
     THEN HOLD + EMIT fire

# Receive signal
RULE IF signal=fire AND tick%4=3
     THEN SWITCH Y_LOOP
```

### Gating

```geo
# Forget gate in LSTM
RULE IF tick%8=1
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum E ht_prev 1
          + ACCUM_VAR sum W xt 1
          + CLAMP_VAR sum 0 200

RULE IF tick%8=2 AND var_sum>=100
     THEN HOLD + SET_VAR ft 100  # Gate open

RULE IF tick%8=2 AND var_sum<100
     THEN HOLD + SET_VAR ft 0    # Gate closed
```

---

## Debugging Tips

### Check Activation Flow

```geo
# Add debug output
RULE IF tick%4=2
     THEN HOLD + SET_VAR debug_sum var_sum
          + SET_VAR debug_activation var_a
```

### Verify Weights

```geo
# Clamp to valid range
CLAMP_VAR w -100 100
```

### Trace Signals

```geo
# Log signal reception
RULE IF signal=test
     THEN HOLD + SET_VAR received_signal 1 + EMIT ack
```

---

## Performance Tips

1. **Minimize rules**: First match wins — order by likelihood
2. **Use DEFINE**: Reuse conditions, reduce duplication
3. **Phase carefully**: Ensure no race conditions with `tick%N`
4. **Clamp variables**: Prevent overflow with `CLAMP_VAR`
5. **Test incrementally**: Verify each layer before adding next

---

**For complete examples, see:** `examples/neural_*.geo`  
**For full documentation:** `NEURAL_NETWORKS_FULL.md`
