NAME neural_hopfield

# ── Hopfield Network (Associative Memory) ────────────────────────
#
# A 4-neuron Hopfield network that stores and recalls patterns.
# Demonstrates recurrent connections and energy minimization.
#
# Grid layout (3x3):
#       col0       col1        col2
# row2: [N0]       [pad]       [N1]
# row1: [pad]      [CORE]      [pad]
# row0: [N2]       [pad]       [N3]
#
# N0-N3: Neurons (Y_LOOP=active/1, GATE_OFF=inactive/0)
# CORE:  Coordinates update cycles and stores pattern
#
# Stored patterns (example - 2 patterns):
#   Pattern A: N0=1, N1=0, N0=1, N3=0  (diagonal)
#   Pattern B: N0=0, N1=1, N0=0, N3=1  (other diagonal)
#
# Update rule: neuron fires if weighted sum from others >= 0
# Weights (Hebbian learning for stored patterns):
#   w_ij = sum over patterns of (state_i * state_j)
#
# Execution phases (tick%4):
#   Phase 0: Neurons read current state
#   Phase 1: CORE broadcasts pattern cue (optional)
#   Phase 2: Neurons accumulate weighted input from neighbors
#   Phase 3: Neurons update based on threshold

# ── Phase 0: Neuron state readout ─────────────────────────────────
RULE IF own_prog=neuron AND tick%4=0 AND family=Y_LOOP
     THEN HOLD + SET_VAR state 100 + SET_VAR output 1 AS neuron_on

RULE IF own_prog=neuron AND tick%4=0 AND mask=0000
     THEN HOLD + SET_VAR state 0 + SET_VAR output 0 AS neuron_off

# ── Phase 1: Core cue (optional pattern hint) ─────────────────────
RULE IF own_prog=core AND tick%4=1 AND var_cue=1
     THEN HOLD + EMIT pattern_a AS cue_a

RULE IF own_prog=core AND tick%4=1 AND var_cue=2
     THEN HOLD + EMIT pattern_b AS cue_b

# ── Phase 2: Neuron accumulation ──────────────────────────────────
# Each neuron receives input from all others (via neighbor routing)
# Simplified: neurons read cardinal neighbors only
# N0 reads N1 (E) and N2 (S)
# N1 reads N0 (W) and N3 (S)
# etc.

# N0 accumulation (at position 2,0)
RULE IF own_prog=neuron AND pos=2,0 AND tick%4=2
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum E state 1    # From N1
          + ACCUM_VAR sum S state 1    # From N2
          + CLAMP_VAR sum 0 200 AS n0_accum

# N1 accumulation (at position 2,2)
RULE IF own_prog=neuron AND pos=2,2 AND tick%4=2
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum W state 1    # From N0
          + ACCUM_VAR sum S state 1    # From N3
          + CLAMP_VAR sum 0 200 AS n1_accum

# N2 accumulation (at position 0,0)
RULE IF own_prog=neuron AND pos=0,0 AND tick%4=2
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum N state 1    # From N0
          + ACCUM_VAR sum E state 1    # From N3
          + CLAMP_VAR sum 0 200 AS n2_accum

# N3 accumulation (at position 0,2)
RULE IF own_prog=neuron AND pos=0,2 AND tick%4=2
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum N state 1    # From N1
          + ACCUM_VAR sum W state 1    # From N2
          + CLAMP_VAR sum 0 200 AS n3_accum

# ── Phase 3: Neuron update (asynchronous) ─────────────────────────
# Threshold = 100 (fires if ≥1 neighbor active)
# Stochastic update: only update if var "update_flag" is set

RULE IF own_prog=neuron AND tick%4=3 AND var_sum>=100 AND random<0.5
     THEN SWITCH Y_LOOP + SET_VAR state 100 AS neuron_fire

RULE IF own_prog=neuron AND tick%4=3 AND var_sum<100 AND random<0.5
     THEN GATE_OFF + SET_VAR state 0 AS neuron_reset

# ── Default ───────────────────────────────────────────────────────
DEFAULT HOLD
