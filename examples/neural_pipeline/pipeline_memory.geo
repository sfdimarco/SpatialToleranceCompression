NAME neural_pipeline_memory

# ── Pattern Recognition Pipeline: Associative Memory (Hopfield) ──
#
# Hopfield network that stores and recalls patterns.
# Uses recurrent connections and energy minimization.
#
# Grid layout (5×2):
#   row1: [M0] [M1] [M2] [M3] [M4]
#   row0: [M5] [M6] [M7] [M8] [M9]
#
# Each neuron stores one bit of the pattern.
# Recurrent connections implement Hebbian learning.
#
# Storage (Outer Product Rule):
#   w_ij = sum over patterns of (p_i * p_j)
#
# Recall (Asynchronous Update):
#   state_i = sign(sum_j w_ij * state_j)
#
# Execution phases (tick%16):
#   Phase 8-9: Load pattern from feature map
#   Phase 10-11: Recurrent dynamics (energy minimization)
#   Phase 12-13: Continue convergence
#   Phase 14-15: Output result

# ── Phase 8-9: Load Pattern from Feature Map ─────────────────────
# Map feature winner to stored pattern

RULE IF own_prog=memory AND tick%16=8 AND signal=load_pattern
     THEN HOLD + SET_VAR state var_input_state
          + SET_VAR output var_state AS mem_load

RULE IF own_prog=memory AND tick%16=8 AND NOT signal=load_pattern
     THEN HOLD + SET_VAR state 0 AS mem_clear

# ── Phase 10-11: Recurrent Dynamics ───────────────────────────────
# Each neuron updates based on weighted sum from all others
# Update rule: state = +1 if sum >= 0, else -1

RULE IF own_prog=memory AND tick%16=10
     THEN HOLD + SET_VAR sum 0
          # Recurrent connections from all other neurons
          + ACCUM_VAR sum W state 1   # From west neighbor
          + ACCUM_VAR sum E state 1   # From east neighbor
          + ACCUM_VAR sum N state 1   # From north neighbor (if exists)
          + ACCUM_VAR sum S state 1   # From south neighbor (if exists)
          AS mem_accum_recurrent

# Asynchronous update (stochastic, one neuron at a time)
RULE IF own_prog=memory AND tick%16=11 AND var_sum>=0 AND random<0.5
     THEN HOLD + SET_VAR state 100 + SET_VAR output 1 AS mem_fire

RULE IF own_prog=memory AND tick%16=11 AND var_sum<0 AND random<0.5
     THEN HOLD + SET_VAR state 0 + SET_VAR output 0 AS mem_reset

# ── Phase 12-13: Continue Convergence ─────────────────────────────
# Allow multiple update cycles for stable attractor

RULE IF own_prog=memory AND tick%16=12
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum W state 1
          + ACCUM_VAR sum E state 1
          + ACCUM_VAR sum N state 1
          + ACCUM_VAR sum S state 1
          AS mem_accum_2

RULE IF own_prog=memory AND tick%16=13 AND var_sum>=50
     THEN HOLD + SET_VAR state 100 AS mem_stable_on

RULE IF own_prog=memory AND tick%16=13 AND var_sum<50
     THEN HOLD + SET_VAR state 0 AS mem_stable_off

# ── Phase 14-15: Output Result ────────────────────────────────────
# Visualize state (Y_LOOP=1, GATE_OFF=0)

RULE IF own_prog=memory AND tick%16=14 AND var_state>=100
     THEN SWITCH Y_LOOP + SET_VAR visual 1 AS mem_vis_on

RULE IF own_prog=memory AND tick%16=14 AND var_state<100
     THEN GATE_OFF + SET_VAR visual 0 AS mem_vis_off

RULE IF own_prog=memory AND tick%16=15
     THEN HOLD AS mem_hold

# ── Pattern Storage (Hebbian Learning) ───────────────────────────
# When storing a pattern, strengthen connections between co-active neurons

RULE IF own_prog=memory AND tick%16=9 AND signal=store_pattern AND var_state>=100
     THEN HOLD + INCR_VAR w_self 10
          + EMIT strengthen_connections AS hebbian_store

# ── Default ───────────────────────────────────────────────────────
DEFAULT HOLD
