NAME neural_kohonen

# ── Kohonen Self-Organizing Map (1D SOM) ─────────────────────────
#
# A 1×4 row of neurons that self-organize to respond to different
# input patterns. Demonstrates competitive learning and neighborhood
# cooperation.
#
# Grid layout (3x4):
#       col0      col1      col2      col3
# row2: [IN0]     [IN1]     [IN2]     [IN3]    - Input features
# row1: [N0]      [N1]      [N2]      [N3]     - SOM neurons
# row0: [W0]      [W1]      [W2]      [W3]     - Weight storage
#
# Each neuron has weight vector (w0, w1, w2, w3) stored in vars.
# Winner = neuron with weights closest to input (min Euclidean distance)
# Update: winner and neighbors move weights toward input
#
# Execution phases (tick%8):
#   Phase 0-1: Inputs present pattern
#   Phase 2-3: Neurons compute distance to input
#   Phase 4-5: Find winner (min distance)
#   Phase 6-7: Update weights (winner + neighborhood)

# ── Phase 0-1: Input pattern ──────────────────────────────────────
RULE IF own_prog=input AND tick%8=0
     THEN HOLD + SET_VAR feature var_target AS in_set

# ── Phase 2-3: Distance computation ───────────────────────────────
# Each neuron computes sum of squared differences
# distance = Σ(input_i - weight_i)²

RULE IF own_prog=som_neuron AND tick%8=2
     THEN HOLD + SET_VAR dist 0
          + ACCUM_VAR dist N feature 1    # From input above
          + SET_VAR diff (var_feature - var_w0)
          + INCR_VAR dist (var_diff * var_diff) AS som_dist0

RULE IF own_prog=som_neuron AND tick%8=3
     THEN HOLD + SET_VAR temp var_dist
          + SET_VAR diff (var_feature - var_w1)
          + INCR_VAR temp (var_diff * var_diff) AS som_dist1

# ── Phase 4-5: Winner selection ───────────────────────────────────
# Neuron with lowest distance wins (fires)
# Simplified: threshold-based rather than true min

RULE IF own_prog=som_neuron AND tick%8=4 AND var_dist<50
     THEN HOLD + SET_VAR winner 1 + EMIT i_am_winner AS winner_yes

RULE IF own_prog=som_neuron AND tick%8=4 AND var_dist>=50
     THEN HOLD + SET_VAR winner 0 AS winner_no

# ── Phase 6-7: Weight update ──────────────────────────────────────
# Winner updates: w_new = w_old + learning_rate * (input - w_old)
# Neighbors update with smaller learning rate

RULE IF own_prog=som_neuron AND tick%8=6 AND var_winner=1
     THEN HOLD + SET_VAR lr 10           # Learning rate = 0.1
          + SET_VAR w0 (var_w0 + var_lr * (var_feature - var_w0))
          + SET_VAR w1 (var_w1 + var_lr * (var_feature - var_w1)) AS winner_update

RULE IF own_prog=som_neuron AND tick%8=6 AND var_winner=0 AND signal=i_am_winner
     THEN HOLD + SET_VAR lr 5            # Neighbor learning rate = 0.05
          + SET_VAR w0 (var_w0 + var_lr * (var_feature - var_w0))
          + SET_VAR w1 (var_w1 + var_lr * (var_feature - var_w1)) AS neighbor_update

# ── Default ───────────────────────────────────────────────────────
DEFAULT HOLD
