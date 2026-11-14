NAME neural_sigmoid

# ── Sigmoid Activation Neuron ──────────────────────────────────────
#
# Implements a smooth sigmoid-like activation using piecewise linear
# approximation with CLAMP_VAR. Demonstrates analog (non-binary) 
# neural computation.
#
# Grid layout (1x3 vertical strip):
#   row2: [INPUT]  - GATE_ON=1, GATE_OFF=0, sets var "input_val"
#   row1: [SIGM]   - Sigmoid neuron, outputs var "activation"
#   row0: [OUT]    - Visual display (Y_LOOP=active, Z_LOOP=inactive)
#
# Sigmoid approximation:
#   activation = 1 / (1 + exp(-x)) ≈ clamp((x + 3) / 6, 0, 1)
#   Where x = weighted input sum
#
# Execution phases (tick%4):
#   Phase 0: Input sets var "input_val" (0 or 100)
#   Phase 1: Sigmoid accumulates weighted input
#   Phase 2: Apply sigmoid clamping
#   Phase 3: Output visualizes result

# ── Phase 0: Input neuron ─────────────────────────────────────────
RULE IF own_prog=input AND mask=1111 AND tick%4=0
     THEN HOLD + SET_VAR input_val 100 + SET_VAR weighted 100 AS in_on

RULE IF own_prog=input AND mask=0000 AND tick%4=0
     THEN HOLD + SET_VAR input_val 0 + SET_VAR weighted 0 AS in_off

# ── Phase 1-2: Sigmoid computation ────────────────────────────────
# For demo simplicity: weighted = input_val (weight=1.0)
# Real use: ACCUM_VAR from multiple inputs

RULE IF own_prog=sigm AND tick%4=1
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum W weighted 1
          + CLAMP_VAR sum 0 200 AS sigm_accum

# Sigmoid: map [0,200] → [0,100] with soft curve
# Approximate with piecewise linear:
#   sum < 50:   output = sum * 0.5 (gentle slope)
#   50 <= sum <= 150: output = 25 + (sum-50) * 0.75 (steeper)
#   sum > 150:  output = 100 + (sum-150) * 0.25 (saturating)

RULE IF own_prog=sigm AND tick%4=2 AND var_sum<50
     THEN HOLD + SET_VAR activation var_sum
          + INCR_VAR activation -50 AS sigm_low

RULE IF own_prog=sigm AND tick%4=2 AND var_sum>=50 AND var_sum<=150
     THEN HOLD + SET_VAR activation 25
          + ACCUM_VAR activation W sum 0.75 AS sigm_mid

RULE IF own_prog=sigm AND tick%4=2 AND var_sum>150
     THEN HOLD + SET_VAR activation 100
          + ACCUM_VAR activation W sum 0.25 AS sigm_high

# ── Phase 3: Output visualization ─────────────────────────────────
RULE IF own_prog=output AND tick%4=3 AND nb_var_N_activation>=50
     THEN SWITCH Y_LOOP + SET_VAR out_state 1 AS out_on

RULE IF own_prog=output AND tick%4=3 AND nb_var_N_activation<50
     THEN GATE_OFF + SET_VAR out_state 0 AS out_off

# ── Default ───────────────────────────────────────────────────────
DEFAULT HOLD
