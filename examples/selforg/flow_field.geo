# selforg_flow_field.geo — Flow Field Visualization
# ===================================================
# Demonstrates: Vector field encoding, particle following, emergent patterns
#
# Usage: python Playground.py --geo examples/selforg/flow_field.geo --grid
#
# Creates a flow field where each cell encodes a direction.
# Particles (depth 1+) follow the flow, creating emergent stream patterns.
#
# Direction Encoding (loop families):
#   Y_LOOP (red)    = Flow North (up)
#   X_LOOP (green)  = Flow East (right)
#   Z_LOOP (blue)   = Flow South (down)
#   DIAG_LOOP (gold)= Flow West (left)
#
# Applications:
#   - Wind/water current visualization
#   - Crowd simulation steering
#   - Particle system guidance
#   - Terrain erosion direction

NAME   selforg_flow_field

# ═══════════════════════════════════════════════════════════════════════════════
# FLOW FIELD GENERATION (depth 0)
# Create a dynamic vector field using mathematical patterns
# ═══════════════════════════════════════════════════════════════════════════════

# ─── VORTEX PATTERN (circular flow) ────────────────────────────────────────────
# Center of vortex at grid center
RULE   IF depth=0 AND tick%100<50
       THEN SET 1000  AS vortex-top
RULE   IF depth=0 AND tick%100_in=50..74
       THEN SET 0100  AS vortex-right
RULE   IF depth=0 AND tick%100_in=75..87
       THEN SET 0010  AS vortex-bottom
RULE   IF depth=0 AND tick%100_in=88..99
       THEN SET 0001  AS vortex-left

# ─── WAVE PATTERN (sinusoidal flow) ────────────────────────────────────────────
RULE   IF depth=0 AND tick%20_in=0..4
       THEN SET 0100  AS wave-right
RULE   IF depth=0 AND tick%20_in=5..9
       THEN SET 1000  AS wave-up
RULE   IF depth=0 AND tick%20_in=10..14
       THEN SET 0001  AS wave-left
RULE   IF depth=0 AND tick%20_in=15..19
       THEN SET 0010  AS wave-down

# ─── DIVERGENCE (flow from center) ─────────────────────────────────────────────
RULE   IF depth=0 AND tick%40_in=0..9
       THEN SET 1000  AS diverge-north
RULE   IF depth=0 AND tick%40_in=10..19
       THEN SET 0100  AS diverge-east
RULE   IF depth=0 AND tick%40_in=20..29
       THEN SET 0010  AS diverge-south
RULE   IF depth=0 AND tick%40_in=30..39
       THEN SET 0001  AS diverge-west

# ─── CONVERGENCE (flow to center) ──────────────────────────────────────────────
RULE   IF depth=0 AND tick%40_in=0..9
       THEN SET 0010  AS converge-south
RULE   IF depth=0 AND tick%40_in=10..19
       THEN SET 0001  AS converge-west
RULE   IF depth=0 AND tick%40_in=20..29
       THEN SET 1000  AS converge-north
RULE   IF depth=0 AND tick%40_in=30..39
       THEN SET 0100  AS converge-east

# ═══════════════════════════════════════════════════════════════════════════════
# PARTICLE FOLLOWING (depth 1+)
# Particles move according to the flow field
# ═══════════════════════════════════════════════════════════════════════════════

# Particle moves North following flow
RULE   IF depth>=1 AND nb_S=Y_LOOP
       THEN SET 1000 + INCR_VAR steps 1  AS particle-move-north

# Particle moves East following flow
RULE   IF depth>=1 AND nb_W=X_LOOP
       THEN SET 0100 + INCR_VAR steps 1  AS particle-move-east

# Particle moves South following flow
RULE   IF depth>=1 AND nb_N=Z_LOOP
       THEN SET 0010 + INCR_VAR steps 1  AS particle-move-south

# Particle moves West following flow
RULE   IF depth>=1 AND nb_E=DIAG_LOOP
       THEN SET 0001 + INCR_VAR steps 1  AS particle-move-west

# Particle spawn at random locations
RULE   IF depth>=1 AND random<0.01
       THEN SET 1111 + SET_VAR steps 0 + SET_VAR age 0  AS particle-spawn

# Particle aging
RULE   IF depth>=1
       THEN INCR_VAR age 1  AS particle-age

# Particle fade after many steps
RULE   IF depth>=1 AND var_steps>=20
       THEN SET 0111  AS particle-fade

# ═══════════════════════════════════════════════════════════════════════════════
# FLOW VISUALIZATION
# Show flow direction and magnitude
# ═══════════════════════════════════════════════════════════════════════════════

# Strong flow (many cells with same direction)
RULE   IF depth=0 AND nb_count=Y_LOOP:3
       THEN SET 1111  AS flow-strong-north
RULE   IF depth=0 AND nb_count=X_LOOP:3
       THEN SET 1111  AS flow-strong-east
RULE   IF depth=0 AND nb_count=Z_LOOP:3
       THEN SET 1111  AS flow-strong-south
RULE   IF depth=0 AND nb_count=DIAG_LOOP:3
       THEN SET 1111  AS flow-strong-west

# Flow transition zones (mixed directions)
RULE   IF depth=0 AND nb_any=Y_LOOP AND nb_any=X_LOOP
       THEN SET 1010  AS flow-transition

# ═══════════════════════════════════════════════════════════════════════════════
# STREAMLINE FORMATION
# Particles leave trails showing flow paths
# ═══════════════════════════════════════════════════════════════════════════════

# Trail left by particles
RULE   IF depth>=1 AND var_steps>=1 AND var_steps<10
       THEN SET 1000 + INCR_VAR trail 1  AS trail-north
RULE   IF depth>=1 AND var_steps>=1 AND var_steps<10
       THEN SET 0100 + INCR_VAR trail 1  AS trail-east
RULE   IF depth>=1 AND var_steps>=1 AND var_steps<10
       THEN SET 0010 + INCR_VAR trail 1  AS trail-south
RULE   IF depth>=1 AND var_steps>=1 AND var_steps<10
       THEN SET 0001 + INCR_VAR trail 1  AS trail-west

# Trail fades over time
RULE   IF var_trail>=1 AND tick%5=0
       THEN INCR_VAR trail -1  AS trail-fade

# ═══════════════════════════════════════════════════════════════════════════════
# FLOW FIELD PATTERNS (preset configurations)
# ═══════════════════════════════════════════════════════════════════════════════

# Define pattern regions using depth/position
RULE   IF depth_in=0..2 AND tick%80_in=0..19
       THEN SET 1000  AS pattern-vortex-1
RULE   IF depth_in=3..5 AND tick%80_in=0..19
       THEN SET 0100  AS pattern-vortex-2

RULE   IF depth_in=0..2 AND tick%80_in=20..39
       THEN SET 0100  AS pattern-wave-1
RULE   IF depth_in=3..5 AND tick%80_in=20..39
       THEN SET 0010  AS pattern-wave-2

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNALS FOR GAME INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF tick%20=0   THEN EMIT flow_update      AS signal-flow-tick
RULE   IF tick%100=0  THEN EMIT pattern_change    AS signal-pattern-change
RULE   IF tick>=100   THEN EMIT flow_field_ready  AS signal-ready

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT: Continue flow simulation
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE
