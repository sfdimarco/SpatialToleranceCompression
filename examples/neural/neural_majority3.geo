NAME neural_majority3

# ── 3-Input Majority-Vote Threshold Neuron ──────────────────────────
#
# Plus-shaped layout on a 3x3 grid:
#
#       col0   col1   col2
# row2: [___]  [IN0]  [___]
# row1: [IN1]  [HID]  [IN2]
# row0: [___]  [OUT]  [___]
#
# Inputs:  GATE_ON (1111) = 1,  GATE_OFF (0000) = 0
# Hidden:  X_LOOP — counts how many input neighbors are ON
#          Fires (emits "fire" signal) when >= 2 of 3 inputs active
# Output:  Z_LOOP — receives "fire" signal, switches to Y_LOOP to indicate 1
# Padding: GATE_OFF — inert
#
# This implements a Threshold Logic Unit: f(x) = 1 if sum(x) >= 2

# ── Hidden neuron (X_LOOP family) ───────────────────────────────────
# The hidden cell at (1,1) has 4 cardinal neighbors:
#   N = IN0, S = OUT, E = IN2, W = IN1
# nb_mask_count=1111:N counts how many neighbors have mask 1111 (GATE_ON).
# OUT starts as Z_LOOP (mask 0111), never 1111, so it won't be miscounted.

RULE IF family=X_LOOP AND nb_mask_count=1111:3
     THEN HOLD + SET_VAR act 1 + EMIT fire AS h_fire3

RULE IF family=X_LOOP AND nb_mask_count=1111:2
     THEN HOLD + SET_VAR act 1 + EMIT fire AS h_fire2

RULE IF family=X_LOOP AND nb_mask_count=1111:1
     THEN HOLD + SET_VAR act 0 AS h_quiet1

RULE IF family=X_LOOP AND nb_mask_count=1111:0
     THEN HOLD + SET_VAR act 0 AS h_quiet0

# ── Output neuron (Z_LOOP family → Y_LOOP when active) ─────────────
# Receives "fire" signal from hidden neuron (its north neighbor).
# Y_LOOP = network output is 1 (renders red), Z_LOOP = output is 0 (blue).

RULE IF family=Y_LOOP AND signal=fire
     THEN HOLD AS out_stay

RULE IF family=Y_LOOP AND NOT signal=fire
     THEN SWITCH Z_LOOP AS out_off

RULE IF family=Z_LOOP AND signal=fire
     THEN SWITCH Y_LOOP AS out_on

RULE IF family=Z_LOOP
     THEN HOLD AS out_wait

# ── Inputs and padding (GATE family) ───────────────────────────────
# Inputs just hold their mask. Externally set to GATE_ON or GATE_OFF.
DEFAULT HOLD
