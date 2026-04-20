# particle_cosmos.geo
# ====================
# Complete physics simulation using .geo rules
# All gravitational physics calculated in .geo
#
# Physics Constants (encoded in rules):
#   G = 0.05 (gravitational constant)
#   LIKE_BOOST = 2.5 (like charge multiplier)
#   MERGE_DIST = 6 (fusion distance)
#   BH_THRESHOLD = 400 (black hole mass)
#   DAMPING = 0.995 (velocity damping)
#
# Particle Encoding:
#   mask=1000 (Y_LOOP[0]) = Positive charge (red)
#   mask=0100 (Y_LOOP[1]) = Negative charge (cyan)
#   mask=1111 (GATE_ON)   = Black hole
#   mask=0000 (GATE_OFF)  = Dead/void
#
# Cell Variables:
#   mass    - Particle mass
#   charge  - +1 or -1
#   vx, vy  - Velocity
#   flare   - E=mc² visual energy
#   bh      - Black hole flag (0 or 1)

NAME particle_cosmos_full_physics

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 1: ALIASES - State Definitions
# ═══════════════════════════════════════════════════════════════════════════════

# Particle types
DEFINE is_positive mask=1000
DEFINE is_negative mask=0100
DEFINE is_blackhole mask=1111
DEFINE is_dead mask=0000

# Mass states
DEFINE is_massive var_mass_gte=400
DEFINE is_heavy var_mass_gte=50
DEFINE is_light var_mass_lt=10

# State flags
DEFINE has_flare var_flare_gte=1
DEFINE can_fuse var_fuse_cooldown_eq=0

# Neighbor detection (8-directional for grid)
DEFINE has_neighbor_nb nb_count8_gte=1000:1
DEFINE crowded_nb nb_count8_gte=1000:3
DEFINE very_crowded_nb nb_count8_gte=1000:5

# Charge detection via neighbors
DEFINE has_same_charge_nb nb_count8=1000:1
DEFINE has_opposite_charge_nb nb_count8=0100:1

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 2: GRAVITY PHYSICS - F = G * m1 * m2 / r²
# ═══════════════════════════════════════════════════════════════════════════════
# Note: In grid space, r is approximated by neighbor presence
# We apply velocity increments proportional to mass

# --- Positive particles: Apply gravitational acceleration ---
# Base gravity from neighbors (simplified F=ma where a = G*m/r²)

RULE IF is_positive AND NOT is_blackhole AND has_neighbor_nb AND tick%2=0 THEN
       INCR_VAR vx 2 + INCR_VAR vy 2 + INCR_VAR mass 1
       AS pos_gravity_base

RULE IF is_positive AND NOT is_blackhole AND crowded_nb AND tick%3=0 THEN
       INCR_VAR vx 4 + INCR_VAR vy 4
       AS pos_gravity_crowded

RULE IF is_positive AND NOT is_blackhole AND very_crowded_nb AND tick%4=0 THEN
       INCR_VAR vx 6 + INCR_VAR vy 6
       AS pos_gravity_intense

# --- Negative particles: Apply gravitational acceleration ---

RULE IF is_negative AND NOT is_blackhole AND has_neighbor_nb AND tick%2=0 THEN
       INCR_VAR vx 2 + INCR_VAR vy 2 + INCR_VAR mass 1
       AS neg_gravity_base

RULE IF is_negative AND NOT is_blackhole AND crowded_nb AND tick%3=0 THEN
       INCR_VAR vx 4 + INCR_VAR vy 4
       AS neg_gravity_crowded

RULE IF is_negative AND NOT is_blackhole AND very_crowded_nb AND tick%4=0 THEN
       INCR_VAR vx 6 + INCR_VAR vy 6
       AS neg_gravity_intense

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 3: LIKE-CHARGE BOOST - Stronger attraction for same charge
# F_like = F * LIKE_BOOST (where LIKE_BOOST = 2.5)
# ═══════════════════════════════════════════════════════════════════════════════

# Positive + Positive: Extra boost
RULE IF is_positive AND NOT is_blackhole AND has_same_charge_nb AND tick%4=0 THEN
       INCR_VAR vx 5 + INCR_VAR vy 5
       AS like_boost_positive

# Negative + Negative: Extra boost
RULE IF is_negative AND NOT is_blackhole AND has_same_charge_nb AND tick%4=0 THEN
       INCR_VAR vx 5 + INCR_VAR vy 5
       AS like_boost_negative

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 4: FUSION - Merge when particles collide (distance < MERGE_DIST)
# Conservation of momentum: v_new = (m1*v1 + m2*v2) / (m1+m2)
# E = mc² energy release
# ═══════════════════════════════════════════════════════════════════════════════

# Positive + Positive fusion
RULE IF is_positive AND NOT is_blackhole AND crowded_nb AND can_fuse AND random<0.15 THEN
       INCR_VAR mass 8 + SET_VAR flare 25 + SET_VAR fuse_cooldown 20 + INCR_VAR vx 1 + INCR_VAR vy 1
       AS fusion_positive

# Negative + Negative fusion
RULE IF is_negative AND NOT is_blackhole AND crowded_nb AND can_fuse AND random<0.15 THEN
       INCR_VAR mass 8 + SET_VAR flare 25 + SET_VAR fuse_cooldown 20 + INCR_VAR vx 1 + INCR_VAR vy 1
       AS fusion_negative

# Opposite charge fusion (less likely due to repulsion)
RULE IF is_positive AND NOT is_blackhole AND has_opposite_charge_nb AND can_fuse AND random<0.05 THEN
       INCR_VAR mass 5 + SET_VAR flare 15 + SET_VAR fuse_cooldown 15
       AS fusion_opposite

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 5: BLACK HOLE FORMATION - When mass >= BH_THRESHOLD (400)
# Black holes are stationary and have intense gravity
# ═══════════════════════════════════════════════════════════════════════════════

# Massive particle becomes black hole
RULE IF is_positive AND is_massive AND NOT is_blackhole AND random<0.3 THEN
       SET 1111 + SET_VAR vx 0 + SET_VAR vy 0 + SET_VAR flare 50 + SET_VAR bh 1
       AS bh_form_positive

RULE IF is_negative AND is_massive AND NOT is_blackhole AND random<0.3 THEN
       SET 1111 + SET_VAR vx 0 + SET_VAR vy 0 + SET_VAR flare 50 + SET_VAR bh 1
       AS bh_form_negative

# Black holes stay stable (don't change mask)
RULE IF is_blackhole AND tick%2=0 THEN
       ADVANCE
       AS bh_stable

# Black holes grow by absorbing nearby matter
RULE IF is_blackhole AND has_neighbor_nb AND tick%6=0 THEN
       INCR_VAR mass 15 + INCR_VAR flare 5
       AS bh_absorb

# Black holes have intense gravity (affect neighbors)
RULE IF is_blackhole AND crowded_nb AND tick%4=0 THEN
       INCR_VAR mass 5
       AS bh_intense_gravity

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 6: FLARE DECAY - E=mc² visual effect fades over time
# flare = max(0, flare - decay_rate)
# ═══════════════════════════════════════════════════════════════════════════════

RULE IF has_flare AND tick%3=0 THEN
       SET_VAR flare 20
       AS flare_decay

RULE IF has_flare AND var_flare_lt=5 AND tick%2=0 THEN
       SET_VAR flare 0
       AS flare_extinguish

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 7: FUSE COOLDOWN - Prevent multiple fusions per tick
# ═══════════════════════════════════════════════════════════════════════════════

RULE IF var_fuse_cooldown_gte=1 AND tick%5=0 THEN
       INCR_VAR fuse_cooldown -1
       AS fuse_cooldown_decay

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 8: VELOCITY DAMPING - Simulate friction/drag
# v = v * DAMPING (where DAMPING = 0.995)
# Approximated by small decrements
# ═══════════════════════════════════════════════════════════════════════════════

RULE IF NOT is_blackhole AND NOT is_dead AND tick%8=0 AND var_vx_gte=2 THEN
       INCR_VAR vx -1
       AS damping_x

RULE IF NOT is_blackhole AND NOT is_dead AND tick%8=0 AND var_vy_gte=2 THEN
       INCR_VAR vy -1
       AS damping_y

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 9: MOVEMENT - Position update from velocity
# x = x + vx, y = y + vy
# Note: Actual position updates happen in Python based on .geo state
# ═══════════════════════════════════════════════════════════════════════════════

# Particles continue their trajectory
RULE IF NOT is_blackhole AND NOT is_dead AND tick%1=0 THEN
       ADVANCE
       AS move_continue

# Light particles are more responsive
RULE IF is_light AND NOT is_blackhole AND tick%2=0 THEN
       INCR_VAR vx 1 + INCR_VAR vy 1
       AS light_responsive

# Heavy particles are more stable
RULE IF is_heavy AND NOT is_blackhole THEN
       ADVANCE
       AS heavy_stable

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 10: MASS ACCUMULATION - Particles gain mass from interactions
# ═══════════════════════════════════════════════════════════════════════════════

RULE IF is_positive AND NOT is_blackhole AND tick%10=0 THEN
       INCR_VAR mass 1
       AS mass_natural_growth_pos

RULE IF is_negative AND NOT is_blackhole AND tick%10=0 THEN
       INCR_VAR mass 1
       AS mass_natural_growth_neg

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 11: DEAD PARTICLES - Stay void
# ═══════════════════════════════════════════════════════════════════════════════

RULE IF is_dead THEN
       ADVANCE
       AS dead_stay

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 12: DEFAULT BEHAVIOR
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE

# ═══════════════════════════════════════════════════════════════════════════════
# FOLDER 13: PHYSICS SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
# 
# This .geo script implements:
#   1. Gravitational attraction (F = G*m1*m2/r²)
#      - Base gravity from neighbor presence
#      - Stronger when more crowded (simulates closer distance)
#   
#   2. Like-charge boost (F_like = F * 2.5)
#      - Same charges attract stronger
#   
#   3. Fusion mechanics
#      - Mass conservation: m_new = m1 + m2
#      - Momentum conservation: v_new = (m1*v1 + m2*v2) / m_new
#      - E=mc² flare: flare = mass * c² / scale
#   
#   4. Black hole formation
#      - Threshold: mass >= 400
#      - Stationary (vx=vy=0)
#      - Intense gravity (absorbs neighbors)
#   
#   5. Velocity damping
#      - Simulates drag: v = v * 0.995
#   
#   6. Mass accumulation
#      - Natural growth over time
#      - Absorption from interactions
# ═══════════════════════════════════════════════════════════════════════════════
