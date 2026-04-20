# cosmos_physics.geo
# ===================
# Gravitational physics for cosmos_infinite.py
# Uses ACCUM_VAR to sum gravitational influence from neighbors
#
# Physics Model:
#   - Each cell has: mass, temp, density, vx, vy, age
#   - Gravity: accumulate mass from neighbors, apply to velocity
#   - Pressure: dense regions resist compression
#   - Fusion: high temp + density = star formation
#   - Black holes: very high mass collapses

NAME cosmos_physics

# ═══════════════════════════════════════════════════════════════════════════════
# ALIASES
# ═══════════════════════════════════════════════════════════════════════════════

DEFINE is_star       family=Y_LOOP
DEFINE is_gas        family=X_LOOP
DEFINE is_dark       family=Z_LOOP
DEFINE is_wave       family=DIAG_LOOP
DEFINE is_blackhole  mask=1111
DEFINE is_void       mask=0000

DEFINE is_dense      var_density_gte=50
DEFINE is_hot        var_temp_gte=80
DEFINE is_massive    var_mass_gte=100
DEFINE is_cold       var_temp_lt=20

# Neighbor counts (8-directional)
DEFINE has_neighbors nb_count8_gte=1000:1
DEFINE crowded       nb_count8_gte=1000:4
DEFINE very_crowded  nb_count8_gte=1000:6

# ═══════════════════════════════════════════════════════════════════════════════
# GRAVITY - Accumulate mass from neighbors, apply to velocity
# F = G * m1 * m2 / r²  approximated by ACCUM_VAR from neighbors
# ═══════════════════════════════════════════════════════════════════════════════

# Stars: accumulate gravitational pull from neighbors
RULE IF is_star AND has_neighbors AND tick%2=0 THEN
       ACCUM_VAR vx N mass 1 + ACCUM_VAR vy N mass 1
       AS star_grav_N

RULE IF is_star AND has_neighbors AND tick%2=0 THEN
       ACCUM_VAR vx S mass 1 + ACCUM_VAR vy S mass 1
       AS star_grav_S

RULE IF is_star AND has_neighbors AND tick%2=0 THEN
       ACCUM_VAR vx E mass 1 + ACCUM_VAR vy E mass 1
       AS star_grav_E

RULE IF is_star AND has_neighbors AND tick%2=0 THEN
       ACCUM_VAR vx W mass 1 + ACCUM_VAR vy W mass 1
       AS star_grav_W

# Gas clouds: same gravity but weaker (lower density)
RULE IF is_gas AND has_neighbors AND tick%3=0 THEN
       ACCUM_VAR vx N mass 1 + ACCUM_VAR vy N mass 1
       AS gas_grav_N

RULE IF is_gas AND has_neighbors AND tick%3=0 THEN
       ACCUM_VAR vx S mass 1 + ACCUM_VAR vy S mass 1
       AS gas_grav_S

RULE IF is_gas AND has_neighbors AND tick%3=0 THEN
       ACCUM_VAR vx E mass 1 + ACCUM_VAR vy E mass 1
       AS gas_grav_E

RULE IF is_gas AND has_neighbors AND tick%3=0 THEN
       ACCUM_VAR vx W mass 1 + ACCUM_VAR vy W mass 1
       AS gas_grav_W

# Dark matter: strong gravity (holds galaxies together)
RULE IF is_dark AND crowded AND tick%2=0 THEN
       ACCUM_VAR vx N mass 2 + ACCUM_VAR vy N mass 2
       AS dark_grav_N

RULE IF is_dark AND crowded AND tick%2=0 THEN
       ACCUM_VAR vx S mass 2 + ACCUM_VAR vy S mass 2
       AS dark_grav_S

RULE IF is_dark AND crowded AND tick%2=0 THEN
       ACCUM_VAR vx E mass 2 + ACCUM_VAR vy E mass 2
       AS dark_grav_E

RULE IF is_dark AND crowded AND tick%2=0 THEN
       ACCUM_VAR vx W mass 2 + ACCUM_VAR vy W mass 2
       AS dark_grav_W

# ═══════════════════════════════════════════════════════════════════════════════
# BLACK HOLES - Intense gravity wells
# ═══════════════════════════════════════════════════════════════════════════════

# Black holes pull everything nearby
RULE IF is_blackhole AND has_neighbors AND tick%1=0 THEN
       ACCUM_VAR vx N mass 5 + ACCUM_VAR vy N mass 5
       AS bh_grav_N

RULE IF is_blackhole AND has_neighbors AND tick%1=0 THEN
       ACCUM_VAR vx S mass 5 + ACCUM_VAR vy S mass 5
       AS bh_grav_S

RULE IF is_blackhole AND has_neighbors AND tick%1=0 THEN
       ACCUM_VAR vx E mass 5 + ACCUM_VAR vy E mass 5
       AS bh_grav_E

RULE IF is_blackhole AND has_neighbors AND tick%1=0 THEN
       ACCUM_VAR vx W mass 5 + ACCUM_VAR vy W mass 5
       AS bh_grav_W

# Black holes grow by absorbing
RULE IF is_blackhole AND crowded AND tick%10=0 THEN
       INCR_VAR mass 10
       AS bh_absorb

# ═══════════════════════════════════════════════════════════════════════════════
# STAR FORMATION - Gas collapses into stars
# ═══════════════════════════════════════════════════════════════════════════════

# Dense gas with neighbors forms stars
RULE IF is_gas AND is_dense AND crowded AND tick%5=0 THEN
       SWITCH Y_LOOP + SET_VAR temp 50 + SET_VAR age 0
       AS star_form

# Dark matter triggers star formation
RULE IF is_gas AND is_dense AND has_neighbors AND tick%8=0 THEN
       SWITCH Y_LOOP + SET_VAR temp 40
       AS dark_trigger_star

# ═══════════════════════════════════════════════════════════════════════════════
# STELLAR EVOLUTION - Stars age and die
# ═══════════════════════════════════════════════════════════════════════════════

# Stars accumulate mass and age
RULE IF is_star AND tick%4=0 THEN
       INCR_VAR mass 1 + INCR_VAR temp 1 + INCR_VAR age 1
       AS star_age

# Massive stars go supernova -> black hole
RULE IF is_star AND is_massive AND var_age_gte=200 AND random<0.1 THEN
       SET 1111 + SET_VAR temp 200 + INCR_VAR mass 100
       AS supernova

# Old low-mass stars fade
RULE IF is_star AND var_age_gte=800 AND random<0.05 THEN
       SET 0000
       AS star_fade

# ═══════════════════════════════════════════════════════════════════════════════
# TEMPERATURE & DENSITY
# ═══════════════════════════════════════════════════════════════════════════════

# Hot things cool down
RULE IF is_hot AND tick%16=0 THEN
       SET_VAR temp 75
       AS cool_down

# Dense things get hotter (gravitational compression)
RULE IF is_dense AND tick%8=0 THEN
       INCR_VAR temp 2
       AS compress_heat

# Gas density increases with neighbors
RULE IF is_gas AND has_neighbors AND tick%6=0 THEN
       INCR_VAR density 3
       AS gas_condense

# Dark matter accumulates
RULE IF is_dark AND tick%5=0 THEN
       INCR_VAR mass 1 + INCR_VAR age 1
       AS dark_grow

# ═══════════════════════════════════════════════════════════════════════════════
# VELOCITY DAMPING - Prevent runaway acceleration
# ═══════════════════════════════════════════════════════════════════════════════

RULE IF var_vx_gte=20 AND tick%4=0 THEN
       INCR_VAR vx -2
       AS damp_x_pos

RULE IF var_vx_lt=-20 AND tick%4=0 THEN
       INCR_VAR vx 2
       AS damp_x_neg

RULE IF var_vy_gte=20 AND tick%4=0 THEN
       INCR_VAR vy -2
       AS damp_y_pos

RULE IF var_vy_lt=-20 AND tick%4=0 THEN
       INCR_VAR vy 2
       AS damp_y_neg

# ═══════════════════════════════════════════════════════════════════════════════
# VOID - Empty space can be seeded
# ═══════════════════════════════════════════════════════════════════════════════

RULE IF is_void AND random<0.002 THEN
       SWITCH X_LOOP + SET_VAR density 5 + SET_VAR age 0
       AS quantum_fluctuation

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE
