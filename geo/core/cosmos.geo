# ═══════════════════════════════════════════════════════════════════════════════
# COSMOS — Big Bang & Emergent Universe Simulation
# ═══════════════════════════════════════════════════════════════════════════════
#
# Mask Family Encoding:
#   GATE_ON  (1111) = Black holes / singularities
#   Y_LOOP   (rotating single) = Stars / luminous matter
#   X_LOOP   (pair cycle) = Gas clouds / nebulae
#   Z_LOOP   (three-quadrant) = Dark matter / gravitational wells
#   DIAG_LOOP (toggle) = Gravitational waves / radiation
#   GATE_OFF (0000) = Void / empty space
#
# Cell Variables:
#   mass      - Total mass in cell
#   temp      - Temperature (heat from fusion, gravitational compression)
#   vx, vy    - Velocity components
#   age       - How long cell has been in current state
#   density   - Matter density (0-100)
#
# Rules:
#   - Gravity emerges from mass concentration (dark matter wells attract)
#   - Stars form in dense regions, go supernova creating black holes
#   - Gravitational waves propagate from massive events
#   - Gas clouds condense into stars over time
# ═══════════════════════════════════════════════════════════════════════════════

NAME cosmos

# ═══════════════════════════════════════════════════════════════════════════════
# ALIASES - State Definitions
# ═══════════════════════════════════════════════════════════════════════════════

DEFINE is_void       mask=0000
DEFINE is_star       family=Y_LOOP
DEFINE is_gas        family=X_LOOP
DEFINE is_dark       family=Z_LOOP
DEFINE is_wave       family=DIAG_LOOP
DEFINE is_blackhole  mask=1111

DEFINE is_dense      var_density>=50
DEFINE is_hot        var_temp>=80
DEFINE is_cold       var_temp<20
DEFINE is_massive    var_mass>=100

DEFINE has_star_nb   nb_count8=Y_LOOP:1
DEFINE has_gas_nb    nb_count8=X_LOOP:1
DEFINE has_dark_nb   nb_count8=Z_LOOP:1
DEFINE has_wave_nb   nb_count8=DIAG_LOOP:1
DEFINE crowded       nb_mask_count8=1111:4

# ═══════════════════════════════════════════════════════════════════════════════
# BIG BANG PHASE - Initial expansion from singularity
# ═══════════════════════════════════════════════════════════════════════════════

# At tick 0-10: Rapid inflation - singularity explodes outward
RULE IF tick_in=0..5 AND is_blackhole THEN
       SWITCH Y_LOOP + INCR_VAR vx 10 + INCR_VAR vy 10 + SET_VAR age 0
       AS bigbang_stars

RULE IF tick_in=0..10 AND is_blackhole AND random<0.3 THEN
       SWITCH X_LOOP + SET_VAR density 30 + SET_VAR age 0
       AS bigbang_gas

RULE IF tick_in=5..15 AND is_star AND var_age<5 THEN
       ADVANCE + INCR_VAR vx 2 + INCR_VAR vy 2
       AS inflation_stars

# ═══════════════════════════════════════════════════════════════════════════════
# STAR FORMATION - Gas condenses into stars in dense regions
# ═══════════════════════════════════════════════════════════════════════════════

# Gas cloud with enough density and neighbors collapses into star
RULE IF is_gas AND is_dense AND has_gas_nb AND tick%4=0 THEN
       SWITCH Y_LOOP + SET_VAR temp 50 + SET_VAR age 0
       AS star_formation

# Dark matter concentration triggers star formation
RULE IF is_gas AND has_dark_nb AND var_density>=30 THEN
       SWITCH Y_LOOP + SET_VAR temp 40 + SET_VAR age 0
       AS dark_trigger_formation

# Random star formation in cold gas (gravitational collapse)
RULE IF is_gas AND is_cold AND random<0.02 THEN
       SWITCH Y_LOOP + SET_VAR temp 35 + SET_VAR age 0
       AS spontaneous_stars

# ═══════════════════════════════════════════════════════════════════════════════
# STELLAR EVOLUTION - Stars age, heat up, and die
# ═══════════════════════════════════════════════════════════════════════════════

# Young stars accumulate mass and heat
RULE IF is_star AND var_age<100 THEN
       ADVANCE + INCR_VAR mass 1 + INCR_VAR temp 1 + INCR_VAR age 1
       AS star_aging

# Mature stars are stable
RULE IF is_star AND var_age>=100 AND var_age<500 AND NOT is_massive THEN
       ADVANCE + INCR_VAR age 1
       AS star_mature

# Massive stars go supernova -> black hole (SET 1111 for GATE_ON)
RULE IF is_star AND is_massive AND var_age>=200 AND random<0.05 THEN
       SET 1111 + SET_VAR temp 200 + EMIT supernova + SET_VAR age 0
       AS supernova

# Old low-mass stars fade to void (SET 0000 for GATE_OFF)
RULE IF is_star AND var_age>=800 AND random<0.1 THEN
       SET 0000 + SET_VAR age 0
       AS star_death

# ═══════════════════════════════════════════════════════════════════════════════
# BLACK HOLES - Gravitational singularities
# ═══════════════════════════════════════════════════════════════════════════════

# Black holes absorb nearby matter
RULE IF is_blackhole AND has_star_nb AND random<0.3 THEN
       INCR_VAR mass 10 + EMIT absorb
       AS bh_eat_star

RULE IF is_blackhole AND has_gas_nb AND random<0.5 THEN
       INCR_VAR mass 5 + INCR_VAR density 10
       AS bh_eat_gas

# Black holes emit gravitational waves
RULE IF is_blackhole AND is_massive AND tick%8=0 THEN
       EMIT gravwave
       AS bh_waves

# Very massive black holes spawn jets (convert to waves)
RULE IF is_blackhole AND var_mass>=500 AND random<0.02 THEN
       SWITCH DIAG_LOOP + SET_VAR age 0
       AS bh_jet

# ═══════════════════════════════════════════════════════════════════════════════
# GRAVITATIONAL WAVES - Propagate energy through space
# ═══════════════════════════════════════════════════════════════════════════════

# Waves propagate outward
RULE IF is_wave AND var_age<20 THEN
       SWITCH DIAG_LOOP + INCR_VAR age 1 + EMIT wave_continue
       AS wave_propagate

# Waves heat matter they pass through
RULE IF is_wave AND has_star_nb THEN
       INCR_VAR temp 5
       AS wave_heat_star

RULE IF is_wave AND has_gas_nb THEN
       INCR_VAR temp 3 + INCR_VAR density 2
       AS wave_compress_gas

# Waves dissipate (SET 0000)
RULE IF is_wave AND var_age>=20 THEN
       SET 0000
       AS wave_dissipate

# ═══════════════════════════════════════════════════════════════════════════════
# DARK MATTER - Gravitational wells that structure the universe
# ═══════════════════════════════════════════════════════════════════════════════

# Dark matter accumulates slowly
RULE IF is_dark THEN
       ADVANCE + INCR_VAR mass 1 + INCR_VAR age 1
       AS dark_grow

# Dense dark matter attracts gas
RULE IF is_dark AND is_dense AND has_gas_nb AND random<0.1 THEN
       INCR_VAR density 5
       AS dark_pull_gas

# Dark matter can form from concentrated mass
RULE IF is_gas AND var_density>=80 AND random<0.05 THEN
       SWITCH Z_LOOP + SET_VAR mass 50 + SET_VAR age 0
       AS dark_formation

# ═══════════════════════════════════════════════════════════════════════════════
# GAS CLOUDS - Nebulae that birth stars
# ═══════════════════════════════════════════════════════════════════════════════

# Gas clouds spread
RULE IF is_gas AND NOT is_dense AND random<0.3 THEN
       ADVANCE + INCR_VAR age 1
       AS gas_spread

# Gas clouds condense (increase density)
RULE IF is_gas AND has_gas_nb THEN
       INCR_VAR density 2
       AS gas_condense

# Gas heated by stars expands
RULE IF is_gas AND has_star_nb AND random<0.2 THEN
       INCR_VAR temp 2
       AS gas_heat_expand

# ═══════════════════════════════════════════════════════════════════════════════
# VOID - Empty space can be seeded
# ═══════════════════════════════════════════════════════════════════════════════

# Random quantum fluctuations in void
RULE IF is_void AND random<0.001 THEN
       SWITCH X_LOOP + SET_VAR density 5 + SET_VAR age 0
       AS quantum_fluctuation

# Void near waves may become waves
RULE IF is_void AND has_wave_nb AND random<0.1 THEN
       SWITCH DIAG_LOOP + SET_VAR age 0
       AS void_excited

# ═══════════════════════════════════════════════════════════════════════════════
# TEMPERATURE & DENSITY REGULATION
# ═══════════════════════════════════════════════════════════════════════════════

# Hot things cool down (use SET_VAR for decrement)
RULE IF is_hot AND tick%16=0 THEN
       SET_VAR temp 75
       AS cooling

# Cold things stay cold
RULE IF is_cold AND tick%32=0 THEN
       INCR_VAR temp 1
       AS ambient_warmth

# Dense things get hotter (gravitational compression)
RULE IF is_dense AND tick%8=0 THEN
       INCR_VAR temp 1
       AS compression_heat

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNAL RESPONSES - React to emitted events
# ═══════════════════════════════════════════════════════════════════════════════

RULE IF signal=supernova AND NOT is_blackhole THEN
       SWITCH DIAG_LOOP + SET_VAR temp 150 + SET_VAR age 0
       AS supernova_shock

RULE IF signal=gravwave AND is_wave THEN
       INCR_VAR age 5
       AS wave_amplify

RULE IF signal=absorb AND is_void AND random<0.3 THEN
       SWITCH X_LOOP + SET_VAR density 10 + SET_VAR age 0
       AS accretion_disk

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT BEHAVIOR
# ═══════════════════════════════════════════════════════════════════════════════

# Most things just continue their cycle
DEFAULT ADVANCE
