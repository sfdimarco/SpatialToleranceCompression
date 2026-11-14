NAME neural_perceptron

# ── Multi-Input Perceptron with Learning ──────────────────────────
#
# A single perceptron with 4 inputs, adjustable weights, and step activation.
# Demonstrates the core building block of neural networks.
#
# Grid layout (3x3):
#       col0      col1       col2
# row2: [IN0]     [W0]       [IN1]
# row1: [SUM]     [OUT]      [W1]
# row0: [IN2]     [W2]       [IN3]
#
# IN0-IN3: Input neurons (GATE_ON=1, GATE_OFF=0)
# W0-W3:   Weight storage (use var "w" to store weight value)
# SUM:     Accumulates weighted sum
# OUT:     Step activation (fires if sum >= threshold)
#
# Computation: output = step(w0*i0 + w1*i1 + w2*i2 + w3*i3 - threshold)
#
# Execution phases (tick%4):
#   Phase 0: Inputs set var "active" (100 or 0)
#   Phase 1: Weights multiply: var "contrib" = active * weight
#   Phase 2: SUM accumulates all contributions
#   Phase 3: OUT applies step activation

# ── Phase 0: Input neurons ────────────────────────────────────────
RULE IF own_prog=input AND tick%4=0 AND mask=1111
     THEN HOLD + SET_VAR active 100 AS in_on

RULE IF own_prog=input AND tick%4=0 AND mask=0000
     THEN HOLD + SET_VAR active 0 AS in_off

# ── Phase 1: Weight multiplication ────────────────────────────────
# Each weight cell reads its paired input and computes contribution
# Weight values stored in var "w" (e.g., w=50 for 0.5, w=100 for 1.0)

RULE IF own_prog=weight AND tick%4=1
     THEN HOLD + SET_VAR contrib 0
          + ACCUM_VAR contrib W active 1  # Read from west neighbor input
          + INCR_VAR contrib -100         # Normalize: contrib = active - 100
          + SET_VAR temp_w var_w          # Load weight
          + SET_VAR contrib (var_contrib * var_temp_w / 100) AS weight_calc
# Note: Simplified - actual weight mult needs engine support for multiplication
# For now, use fixed weights via SET_VAR

RULE IF own_prog=weight AND tick%4=1 AND var_w>=80
     THEN HOLD + SET_VAR contrib var_active AS weight_high

RULE IF own_prog=weight AND tick%4=1 AND var_w<80 AND var_w>=50
     THEN HOLD + SET_VAR contrib (var_active / 2) AS weight_med

RULE IF own_prog=weight AND tick%4=1 AND var_w<50
     THEN HOLD + SET_VAR contrib 0 AS weight_low

# ── Phase 2: Summation ────────────────────────────────────────────
RULE IF own_prog=sum AND tick%4=2
     THEN HOLD + SET_VAR total 0
          + ACCUM_VAR total N contrib 1   # From W0
          + ACCUM_VAR total S contrib 1   # From W2
          + ACCUM_VAR total E contrib 1   # From W1 (via routing)
          + ACCUM_VAR total W contrib 1   # From W3 (via routing)
          + CLAMP_VAR total 0 400 AS sum_accum

# ── Phase 3: Step activation ──────────────────────────────────────
# Threshold = 200 (fires when ≥2 of 4 inputs active with weight=100)

RULE IF own_prog=output AND tick%4=3 AND nb_var_N_total>=200
     THEN SWITCH Y_LOOP + SET_VAR fired 1 AS out_fire

RULE IF own_prog=output AND tick%4=3 AND nb_var_N_total<200
     THEN GATE_OFF + SET_VAR fired 0 AS out_quiet

# ── Default ───────────────────────────────────────────────────────
DEFAULT HOLD
