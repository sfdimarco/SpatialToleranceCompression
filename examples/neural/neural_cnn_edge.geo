NAME neural_cnn_edge

# ── Convolutional Neural Network Edge Detector ───────────────────
#
# A 3×3 convolutional filter that detects edges in binary input.
# Demonstrates CNN-style local receptive fields and weight sharing.
#
# Grid layout (5x5):
#       col0    col1    col2    col3    col4
# row4: [I00]   [I01]   [I02]   [I03]   [I04]   - Input row 0
# row3: [I10]   [I11]   [I12]   [I13]   [I14]   - Input row 1
# row2: [I20]   [I21]   [K00]   [I23]   [I24]   - Input row 2 + kernel
# row1: [I30]   [I31]   [I32]   [I33]   [I34]   - Input row 3
# row0: [I40]   [I41]   [I42]   [I43]   [I44]   - Input row 4
#
# K00: Convolution kernel (3×3 Sobel edge detector)
#      Reads 3×3 neighborhood, computes gradient magnitude
#
# Sobel X (vertical edges):
#   [-1  0  1]
#   [-2  0  2]
#   [-1  0  1]
#
# Sobel Y (horizontal edges):
#   [-1 -2 -1]
#   [ 0  0  0]
#   [ 1  2  1]
#
# Execution phases (tick%8):
#   Phase 0: Inputs set state
#   Phase 1-2: Kernel reads 3×3 region
#   Phase 3-4: Compute Sobel X gradient
#   Phase 5-6: Compute Sobel Y gradient
#   Phase 7: Combine and threshold

# ── Phase 0: Input cells ──────────────────────────────────────────
RULE IF own_prog=input AND tick%8=0 AND mask=1111
     THEN HOLD + SET_VAR pixel 100 AS in_on

RULE IF own_prog=input AND tick%8=0 AND mask=0000
     THEN HOLD + SET_VAR pixel 0 AS in_off

# ── Phase 1-2: Kernel reads neighborhood ──────────────────────────
# Store neighbor values in temp vars

RULE IF own_prog=kernel AND tick%8=1
     THEN HOLD + SET_VAR gx 0 + SET_VAR gy 0
          # Read 3×3 region centered on kernel
          + ACCUM_VAR gx NW pixel -1   # Top-left
          + ACCUM_VAR gx N pixel -2    # Top-center
          + ACCUM_VAR gx NE pixel 1    # Top-right
          + ACCUM_VAR gx W pixel -2    # Mid-left
          # + ACCUM_VAR gx E pixel 2    # Mid-right (skip center=0)
          + ACCUM_VAR gx SW pixel -1   # Bottom-left
          + ACCUM_VAR gx S pixel 0     # Bottom-center
          + ACCUM_VAR gx SE pixel 1    # Bottom-right
          AS sobel_x_accum

RULE IF own_prog=kernel AND tick%8=2
     THEN HOLD
          # Sobel Y
          + ACCUM_VAR gy NW pixel -1
          + ACCUM_VAR gy N pixel 0
          + ACCUM_VAR gy NE pixel 1
          + ACCUM_VAR gy W pixel -2
          # + ACCUM_VAR gy E pixel 2
          + ACCUM_VAR gy SW pixel 1
          + ACCUM_VAR gy S pixel 2
          + ACCUM_VAR gy SE pixel 1
          AS sobel_y_accum

# ── Phase 3-4: Compute gradient magnitude ─────────────────────────
# magnitude = |gx| + |gy| (L1 norm approximation)

RULE IF own_prog=kernel AND tick%8=3
     THEN HOLD + SET_VAR mag var_gx
          + INCR_VAR mag (var_gy if var_gy>0 else -var_gy) AS mag_approx

# ── Phase 5-6: Non-maximum suppression (simplified) ───────────────
RULE IF own_prog=kernel AND tick%8=5 AND var_mag>=150
     THEN HOLD + SET_VAR edge 100 AS edge_strong

RULE IF own_prog=kernel AND tick%8=5 AND var_mag<150 AND var_mag>=50
     THEN HOLD + SET_VAR edge 50 AS edge_weak

RULE IF own_prog=kernel AND tick%8=5 AND var_mag<50
     THEN HOLD + SET_VAR edge 0 AS no_edge

# ── Phase 7: Output visualization ─────────────────────────────────
RULE IF own_prog=kernel AND tick%8=7 AND var_edge>=100
     THEN SWITCH Y_LOOP + SET_VAR output 1 AS out_edge

RULE IF own_prog=kernel AND tick%8=7 AND var_edge<100
     THEN GATE_OFF + SET_VAR output 0 AS out_no_edge

# ── Default ───────────────────────────────────────────────────────
DEFAULT HOLD
