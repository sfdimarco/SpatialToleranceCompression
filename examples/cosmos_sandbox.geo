# cosmos_sandbox.geo - Emergent Cosmic Life with Black Hole Collisions
# =====================================================================
# A sandbox simulation featuring:
# - Charged particle gravity
# - Black hole formation and mergers
# - Gravitational wave emission
# - Recoil kicks from asymmetric mergers
# - Emergent life in habitable zones

NAME   cosmos_sandbox_bh

# ═══════════════════════════════════════════════════════════════════════════════
# ALIASES
# ═══════════════════════════════════════════════════════════════════════════════

DEFINE is_positive      family=Y_LOOP
DEFINE is_negative      family=X_LOOP
DEFINE is_neutral       family=Z_LOOP
DEFINE is_blackhole     mask=1111
DEFINE is_void          mask=0000
DEFINE is_life          family=DIAG_LOOP
DEFINE is_grav_wave     mask=1010

# ═══════════════════════════════════════════════════════════════════════════════
# PARTICLE BEHAVIORS
# ═══════════════════════════════════════════════════════════════════════════════

# Positive particles attract negatives
RULE   IF is_positive AND nb_any=X_LOOP  THEN ROTATE_CW  AS attract-negative

# Negative particles attract positives
RULE   IF is_negative AND nb_any=Y_LOOP  THEN ROTATE_CCW  AS attract-positive

# Like charges boost attraction (2.5x stronger)
RULE   IF is_positive AND nb_count_gte=Y_LOOP:2  THEN ADVANCE 2  AS like-boost-pos
RULE   IF is_negative AND nb_count_gte=X_LOOP:2  THEN ADVANCE 2  AS like-boost-neg

# ═══════════════════════════════════════════════════════════════════════════════
# FUSION RULES (E = mc^2)
# ═══════════════════════════════════════════════════════════════════════════════

# Like-charged particles fuse when close
RULE   IF is_positive AND nb_count_gte=Y_LOOP:3  THEN SET 1111 + EMIT flare  AS fusion-pos
RULE   IF is_negative AND nb_count_gte=X_LOOP:3  THEN SET 1111 + EMIT flare  AS fusion-neg

# Fusion energy release
RULE   IF signal=flare AND depth_in=1..3  THEN SET 0111  AS energy-burst

# ═══════════════════════════════════════════════════════════════════════════════
# BLACK HOLE FORMATION
# ═══════════════════════════════════════════════════════════════════════════════

# Massive particles become black holes (mass >= 400)
RULE   IF var_mass>=400 AND NOT is_blackhole  THEN SET 1111 + SET_VAR bh_age 0  AS become-bh

# Black holes attract everything gravitationally
RULE   IF is_blackhole AND NOT nb_any=GATE  THEN EMIT bh_gravity  AS bh-pull

# Black hole penumbra (blue inner, yellow outer)
RULE   IF is_blackhole AND depth_in=1..2  THEN SET 1000  AS bh-blue-halo
RULE   IF is_blackhole AND depth_in=3..4  THEN SET 0111  AS bh-yellow-penumbra

# ═══════════════════════════════════════════════════════════════════════════════
# BLACK HOLE COLLISIONS & GRAVITATIONAL WAVES
# ═══════════════════════════════════════════════════════════════════════════════

# Two black holes spiraling together (when BH neighbors present)
RULE   IF is_blackhole AND nb_count_gte=GATE:1 AND var_merge_timer<=0
       THEN SET 1111 + EMIT inspiral + SET_VAR inspiraling 1  AS bh-inspiral

# Inspiral phase - black holes orbit faster and faster
RULE   IF is_blackhole AND var_inspiraling=1
       THEN ROTATE_CW + INCR_VAR orbital_speed 1  AS bh-spiral-in

# MERGER EVENT - Two black holes merge into one
RULE   IF is_blackhole AND nb_count_gte=GATE:2 AND var_orbital_speed>=5
       THEN SET 1111 + EMIT merger + EMIT grav_wave + INCR_VAR mass 50  AS bh-merger

# Gravitational wave emission (ripples in spacetime)
RULE   IF signal=grav_wave AND depth_in=1..8
       THEN SET 1010 + SET_VAR wave_strength 10 + INCR_VAR wave_dist 1  AS grav-wave-propagate

# Gravitational waves heat surrounding space
RULE   IF is_grav_wave AND depth_in=1..5
       THEN INCR_VAR temp 5 + EMIT wave_heat  AS wave-heating

# Wave energy dissipates with distance
RULE   IF is_grav_wave AND var_wave_dist>=8
       THEN SET 0000  AS wave-dissipate

# ═══════════════════════════════════════════════════════════════════════════════
# RECOIL KICK (Asymmetric merger causes black hole to be ejected)
# ═══════════════════════════════════════════════════════════════════════════════

# Asymmetric mass ratio causes kick
RULE   IF signal=merger AND is_blackhole AND random<0.7
       THEN SET_VAR kicking 1 + SET_VAR kick_decay 0  AS bh-kick

# Black hole recoil motion
RULE   IF is_blackhole AND var_kicking=1
       THEN ROTATE_CW + INCR_VAR kick_decay 1  AS bh-recoil

# Kick decay (black hole slows due to dynamical friction)
RULE   IF is_blackhole AND var_kicking=1 AND var_kick_decay>=50
       THEN SET_VAR kicking 0  AS bh-kick-stop

# ═══════════════════════════════════════════════════════════════════════════════
# GRAVITATIONAL WAVE EFFECTS ON MATTER
# ═══════════════════════════════════════════════════════════════════════════════

# Gravitational waves perturb nearby particles
RULE   IF signal=wave_heat AND NOT is_blackhole
       THEN ROTATE_CW  AS space-distortion

# Waves can trigger star formation in gas clouds
RULE   IF signal=wave_heat AND depth_in=3..6 AND random<0.1
       THEN SET 1000 + SET_VAR mass 5  AS triggered-star-formation

# Waves disrupt habitable zones (temperature spike)
RULE   IF signal=wave_heat AND var_habitable=1
       THEN INCR_VAR temp 20 + SET_VAR habitable 0  AS habitat-disruption

# ═══════════════════════════════════════════════════════════════════════════════
# TEMPERATURE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

# Heating from nearby particles
RULE   IF nb_count_gte=Y_LOOP:4  THEN INCR_VAR temp 2  AS heat-from-pos
RULE   IF nb_count_gte=X_LOOP:4  THEN INCR_VAR temp 2  AS heat-from-neg
RULE   IF signal=flare  THEN INCR_VAR temp 15  AS heat-from-flare

# Cooling in empty space
RULE   IF var_temp>=26 AND nb_count8=GATE:8  THEN INCR_VAR temp -1  AS cool-down

# ═══════════════════════════════════════════════════════════════════════════════
# HABITABLE ZONE DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

# Goldilocks zone: temperature 20-40, moderate density
RULE   IF var_temp_in=20..40 AND nb_count_gte=Y_LOOP:2 AND NOT is_blackhole AND NOT is_grav_wave
       THEN SET_VAR habitable 1 + EMIT habitable_zone  AS goldilocks

# ═══════════════════════════════════════════════════════════════════════════════
# EMERGENT LIFE FORMS
# ═══════════════════════════════════════════════════════════════════════════════

# Simple life emerges in habitable zones
RULE   IF var_habitable=1 AND random<0.02 AND tick>=101 AND NOT is_grav_wave
       THEN SET 1001 + SET_VAR life_type 1  AS spawn-life-basic

# Complex life in stable habitable zones
RULE   IF var_habitable=1 AND var_age>=50 AND random<0.01 AND var_wave_dist=0
       THEN SET 1001 + SET_VAR life_type 2 + SET_VAR complexity 5  AS spawn-life-complex

# Life reproduction
RULE   IF is_life AND nb_count=DIAG_LOOP:1 AND random<0.03
       THEN EMIT reproduce  AS life-reproduce

RULE   IF signal=reproduce AND var_habitable=1 AND random<0.4
       THEN SET 1001 + SET_VAR life_type 1  AS new-life

# Life responds to environment
RULE   IF is_life AND var_temp<15  THEN INCR_VAR temp 1  AS life-warmth
RULE   IF is_life AND var_temp>=46  THEN INCR_VAR temp -1  AS life-cooling

# Life dies in gravitational wave events
RULE   IF is_life AND signal=wave_heat AND var_wave_strength>=5
       THEN SET 0000  AS life-extinction

# ═══════════════════════════════════════════════════════════════════════════════
# CONTINUOUS EMITTER (from center)
# ═══════════════════════════════════════════════════════════════════════════════

# Emit new particles from "cosmic source"
RULE   IF tick%45=0 AND depth=0 AND random<0.5
       THEN SET 1000 + SET_VAR mass 5  AS emit-positive
RULE   IF tick%45=0 AND depth=0 AND random<0.5
       THEN SET 1100 + SET_VAR mass 5  AS emit-negative

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNALS FOR GAME INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF signal=inspiral  THEN EMIT bh_inspiral_detected   AS signal-inspiral
RULE   IF signal=merger    THEN EMIT bh_merger_detected     AS signal-merger
RULE   IF signal=grav_wave THEN EMIT gravitational_wave     AS signal-gw
RULE   IF signal=flare     THEN EMIT fusion_event           AS signal-fusion
RULE   IF signal=habitable_zone THEN EMIT habitable_found   AS signal-habitable
RULE   IF is_life          THEN EMIT life_present           AS signal-life
RULE   IF var_kicking=1    THEN EMIT bh_recoil              AS signal-recoil
RULE   IF tick%30=0        THEN EMIT sim_update             AS signal-update

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE + INCR_VAR age 1 + INCR_VAR bh_age 1
