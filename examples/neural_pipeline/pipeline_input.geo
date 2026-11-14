NAME neural_pipeline_input

# ── Pattern Recognition Pipeline: Input Layer ─────────────────────
#
# 5×5 grid of input neurons that encode binary patterns.
# Each neuron represents one pixel (1=ON/GATE_ON, 0=OFF/GATE_OFF).
#
# Grid layout (5×5):
#   row4: [P00] [P01] [P02] [P03] [P04]
#   row3: [P10] [P11] [P12] [P13] [P14]
#   row2: [P20] [P21] [P22] [P23] [P24]
#   row1: [P30] [P31] [P32] [P33] [P34]
#   row0: [P40] [P41] [P42] [P43] [P44]
#
# Execution phases (tick%16):
#   Phase 0-1: Read pattern and set activation
#   Phase 2-7: Hold activation for feature map processing
#   Phase 8-15: Reset for next pattern
#
# Variables:
#   var_pixel: 100=ON, 0=OFF (binary input)
#   var_active: same as pixel (for consistency)
#   var_row, var_col: position encoding

# ── Phase 0-1: Input Encoding ─────────────────────────────────────
# Set pixel value based on mask (GATE_ON=1, GATE_OFF=0)

RULE IF own_prog=input_pixel AND tick%16=0 AND mask=1111
     THEN HOLD + SET_VAR pixel 100 + SET_VAR active 100 AS in_on

RULE IF own_prog=input_pixel AND tick%16=0 AND mask=0000
     THEN HOLD + SET_VAR pixel 0 + SET_VAR active 0 AS in_off

# ── Phase 1: Position encoding (for debugging/reference) ──────────
# Store row and column in variables for reference

RULE IF own_prog=input_pixel AND tick%16=1
     THEN HOLD + SET_VAR_row var_row + SET_VAR_col var_col AS in_pos

# ── Phase 2-7: Hold activation ────────────────────────────────────
# Keep activation stable while feature map processes

RULE IF own_prog=input_pixel AND tick%16>=2 AND tick%16<=7
     THEN HOLD AS in_hold

# ── Phase 8-15: Reset/Ready for next pattern ─────────────────────
RULE IF own_prog=input_pixel AND tick%16>=8
     THEN HOLD AS in_reset

# ── Default ───────────────────────────────────────────────────────
DEFAULT HOLD
