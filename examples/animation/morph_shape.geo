# morph_shape.geo — Shape Morphing Animation (Circle to Square)
# ==============================================================
# Demonstrates: Gradual transformation, interpolation, smooth transitions
#
# Usage: python Playground.py --geo examples/animation/morph_shape.geo
#
# Creates a 32-frame morph animation between geometric shapes:
#   Circle (8 frames) → Rounded Square (8 frames) → Square (8 frames) → Circle
#
# Uses depth layers to create the illusion of smooth shape interpolation.
# Each depth ring represents a different "resolution" of the shape.

NAME   morph_shape

# === MORPH CYCLE (32 frames total, 8 frames per shape phase) ===

# PHASE 1: CIRCLE (ticks 0-7)
# All quadrants active, rotating to suggest roundness
RULE   IF tick%32_in=0..7 AND depth=0  THEN SWITCH Y_LOOP  AS circle-outer
RULE   IF tick%32_in=0..7 AND depth=1  THEN SWITCH X_LOOP  AS circle-mid
RULE   IF tick%32_in=0..7 AND depth=2  THEN SWITCH Z_LOOP  AS circle-inner
RULE   IF tick%32_in=0..7 AND depth>=3 THEN SWITCH DIAG_LOOP AS circle-core

# PHASE 2: ROUNDED SQUARE (ticks 8-15)
# Corners begin to form, edges soften
RULE   IF tick%32_in=8..11 AND depth=0  THEN SET 1111  AS rsolid-start
RULE   IF tick%32_in=12..15 AND depth=0 THEN SET 1111  AS rsolid-hold
RULE   IF tick%32_in=8..15 AND depth=1  THEN SET 1100  AS rtop-form
RULE   IF tick%32_in=8..15 AND depth=2  THEN SET 0011  AS rbottom-form
RULE   IF tick%32_in=8..15 AND depth>=3 THEN ROTATE_CW  AS rcore-spin

# PHASE 3: SQUARE (ticks 16-23)
# Sharp corners, stable form
RULE   IF tick%32_in=16..19 AND depth=0  THEN SET 1111  AS square-solid
RULE   IF tick%32_in=20..23 AND depth=0  THEN SET 1111  AS square-hold
RULE   IF tick%32_in=16..23 AND depth=1  THEN SET 1111  AS square-fill
RULE   IF tick%32_in=16..23 AND depth=2  THEN SET 1100  AS square-top
RULE   IF tick%32_in=16..23 AND depth>=3 THEN SET 0011  AS square-bottom

# PHASE 4: SQUARE TO CIRCLE MORPH (ticks 24-31)
# Gradual softening back to circle
RULE   IF tick%32_in=24..26 AND depth=0  THEN ROTATE_CW  AS morph-start
RULE   IF tick%32_in=27..29 AND depth=0  THEN ROTATE_CW  AS morph-mid
RULE   IF tick%32_in=30..31 AND depth=0  THEN SWITCH Y_LOOP AS morph-complete
RULE   IF tick%32_in=24..31 AND depth=1  THEN SWITCH X_LOOP AS morph-outer
RULE   IF tick%32_in=24..31 AND depth=2  THEN SWITCH Z_LOOP AS morph-inner
RULE   IF tick%32_in=24..31 AND depth>=3 THEN SWITCH DIAG_LOOP AS morph-core

# === EDGE SOFTENING (simulated via depth-based patterns) ===
# Outer edges (depth 0-1) change slower for smooth appearance
RULE   IF depth_in=0..1 AND tick%64_in=0..31  THEN ADVANCE  AS soft-outer

# Inner details (depth 2-3) change faster for detail
RULE   IF depth_in=2..3 AND tick%32_in=0..15  THEN ADVANCE 2 AS detailed-inner

# === MORPH SIGNALS (for game integration) ===
RULE   IF tick%32=0   THEN EMIT morph_circle      AS signal-circle
RULE   IF tick%32=8   THEN EMIT morph_roundedsq   AS signal-roundedsq
RULE   IF tick%32=16  THEN EMIT morph_square       AS signal-square
RULE   IF tick%32=24  THEN EMIT morph_transition   AS signal-morphing

# === DEFAULT: Continue morph cycle ===
DEFAULT ADVANCE
