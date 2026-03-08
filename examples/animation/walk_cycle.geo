# walk_cycle.geo — 8-Frame Character Walk Cycle
# ================================================
# Demonstrates: Loop family cycling, phase offsets, depth-based layering
#
# Usage: python Playground.py --geo examples/animation/walk_cycle.geo
#
# This script generates a 4-phase walk cycle using loop families to represent
# different leg positions. The body (depth 0) leads the cycle, while limb
# segments (depth 1-3) follow with phase offsets for natural motion.
#
# Loop Family Mapping:
#   Y_LOOP (red)    = Left foot forward
#   X_LOOP (green)  = Both feet level
#   Z_LOOP (blue)   = Right foot forward
#   DIAG_LOOP (gold)= Mid-stride transition

NAME   walk_cycle

# === BODY CORE (depth 0) - Leads the 4-tick walk cycle ===
RULE   IF depth=0 AND tick%4=0  THEN SWITCH Y_LOOP    AS step-left
RULE   IF depth=0 AND tick%4=1  THEN SWITCH X_LOOP    AS step-level
RULE   IF depth=0 AND tick%4=2  THEN SWITCH Z_LOOP    AS step-right
RULE   IF depth=0 AND tick%4=3  THEN SWITCH DIAG_LOOP AS step-transition

# === UPPER LIMBS (depth 1) - Opposite phase for arm swing ===
RULE   IF depth=1 AND tick%4=0  THEN SWITCH Z_LOOP    AS arm-right
RULE   IF depth=1 AND tick%4=1  THEN SWITCH DIAG_LOOP AS arm-transition
RULE   IF depth=1 AND tick%4=2  THEN SWITCH Y_LOOP    AS arm-left
RULE   IF depth=1 AND tick%4=3  THEN SWITCH X_LOOP    AS arm-level

# === LOWER LIMBS (depth 2-3) - Follow body with 1-tick delay ===
RULE   IF depth_in=2..3 AND tick%4=0  THEN SWITCH DIAG_LOOP  AS leg-transition
RULE   IF depth_in=2..3 AND tick%4=1  THEN SWITCH Y_LOOP     AS leg-left
RULE   IF depth_in=2..3 AND tick%4=2  THEN SWITCH X_LOOP     AS leg-level
RULE   IF depth_in=2..3 AND tick%4=3  THEN SWITCH Z_LOOP     AS leg-right

# === FEET (depth 4+) - Plant and lift pattern ===
RULE   IF depth>=4 AND tick%4=0  THEN SET 1100  AS foot-plant-left
RULE   IF depth>=4 AND tick%4=1  THEN SET 1000  AS foot-lift-right
RULE   IF depth>=4 AND tick%4=2  THEN SET 0100  AS foot-plant-right
RULE   IF depth>=4 AND tick%4=3  THEN SET 0010  AS foot-lift-left

# === DEFAULT: Continue animation ===
DEFAULT ADVANCE
