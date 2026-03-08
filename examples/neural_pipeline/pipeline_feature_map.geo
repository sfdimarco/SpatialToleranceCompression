NAME neural_pipeline_feature_map

# ── Pattern Recognition Pipeline: Feature Map (SOM) ──────────────
#
# 3×3 Self-Organizing Map that learns to recognize input patterns.
# Each neuron has a 25-dimensional weight vector (one per input pixel).
#
# Grid layout (7×5 - feature map with surrounding input routing):
#       col0    col1    col2    col3    col4
# row4: [___]   [___]   [___]   [___]   [___]   ← Input routing
# row3: [___]   [F00]   [F01]   [F02]   [___]   ← Feature neurons
# row2: [___]   [F10]   [F11]   [F12]   [___]
# row1: [___]   [F20]   [F21]   [F22]   [___]
# row0: [___]   [___]   [___]   [___]   [___]   ← Input routing
#
# Learning (Kohonen SOM):
#   1. Compute distance from input to weight vector
#   2. Find winner (minimum distance)
#   3. Update winner + neighbors toward input
#
# Execution phases (tick%16):
#   Phase 0-1: Inputs present pattern
#   Phase 2-3: Compute distances (input - weights)
#   Phase 4-5: Find winner (min distance competition)
#   Phase 6-7: Update weights (winner + neighborhood)
#   Phase 8-15: Hold/Reset
#
# Variables per feature neuron:
#   var_w0..w24: Weight vector (25 weights for 5×5 input)
#   var_dist: Distance to input pattern
#   var_winner: 1=this neuron won, 0=lost
#   var_lr: Learning rate (higher for winner, lower for neighbors)

# ── Phase 2-3: Distance Computation ───────────────────────────────
# Compute Manhattan distance: sum of |input_i - weight_i|
# Simplified: accumulate differences from visible input neurons

RULE IF own_prog=feature AND tick%16=2
     THEN HOLD + SET_VAR dist 0
          # Read from input layer (via neighbor routing or direct access)
          # Simplified for 3×3 neighborhood demo
          + ACCUM_VAR dist N active 1    # From north input
          + ACCUM_VAR dist S active 1    # From south input
          + ACCUM_VAR dist E active 1    # From east input
          + ACCUM_VAR dist W active 1    # From west input
          + SET_VAR dist_temp var_dist   AS feat_dist_read

# Subtract weight contribution (distance = |input - weight|)
RULE IF own_prog=feature AND tick%16=3
     THEN HOLD
          # For each weight, subtract from distance
          # Simplified: use sum of weights as approximation
          + SET_VAR weight_sum (var_w0 + var_w1 + var_w2 + var_w3 + var_w4)
          + INCR_VAR dist -var_weight_sum
          + CLAMP_VAR dist 0 500  # Ensure non-negative
          AS feat_dist_compute

# ── Phase 4-5: Winner Selection (Competition) ─────────────────────
# Neuron with lowest distance wins, inhibits others

RULE IF own_prog=feature AND tick%16=4 AND var_dist<100
     THEN HOLD + SET_VAR winner 1 + EMIT winner_found AS winner_yes

RULE IF own_prog=feature AND tick%16=4 AND var_dist>=100
     THEN HOLD + SET_VAR winner 0 AS winner_no

# Lateral inhibition: winner suppresses neighbors
RULE IF own_prog=feature AND tick%16=5 AND signal=winner_found AND var_winner=0
     THEN HOLD + SET_VAR dist 999 AS suppress_loser

RULE IF own_prog=feature AND tick%16=5 AND var_winner=1
     THEN HOLD + EMIT i_am_winner AS announce_winner

# ── Phase 6-7: Weight Update (Hebbian Learning) ───────────────────
# Winner: w_new = w_old + lr * (input - w_old)
# Neighbors: w_new = w_old + lr_neighbor * (input - w_old)

# Winner update (high learning rate)
RULE IF own_prog=feature AND tick%16=6 AND var_winner=1
     THEN HOLD + SET_VAR lr 20  # 0.2 scaled
          + SET_VAR delta0 (var_lr * (var_input0 - var_w0) / 100)
          + SET_VAR w0 (var_w0 + var_delta0)
          + SET_VAR delta1 (var_lr * (var_input1 - var_w1) / 100)
          + SET_VAR w1 (var_w1 + var_delta1)
          + CLAMP_VAR w0 0 100
          + CLAMP_VAR w1 0 100
          AS winner_update_weights

# Neighbor update (lower learning rate, requires signal from winner)
RULE IF own_prog=feature AND tick%16=6 AND signal=i_am_winner AND var_winner=0
     THEN HOLD + SET_VAR lr 10  # 0.1 scaled
          + SET_VAR delta0 (var_lr * (var_input0 - var_w0) / 100)
          + SET_VAR w0 (var_w0 + var_delta0)
          + CLAMP_VAR w0 0 100
          AS neighbor_update_weights

# Initialize weights randomly (or to default values)
RULE IF own_prog=feature AND tick%16=7 AND var_w0=0
     THEN HOLD + SET_VAR w0 50 + SET_VAR w1 50 + SET_VAR w2 50
          + SET_VAR w3 50 + SET_VAR w4 50 AS init_weights

# ── Phase 8-15: Hold state ────────────────────────────────────────
RULE IF own_prog=feature AND tick%16>=8
     THEN HOLD AS feat_hold

# ── Default ───────────────────────────────────────────────────────
DEFAULT HOLD
