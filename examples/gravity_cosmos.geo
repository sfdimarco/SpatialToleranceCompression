# gravity_cosmos.geo - Gravitational Particle Cosmos
# ====================================================
# A cosmic particle simulation with gravity-like attraction,
# orbital mechanics, and emergent galaxy formation.

NAME   gravity_cosmos

# --- Heavy mass centers (gravitational anchors) ---
RULE   IF tick_in=0..20 AND depth=0 AND random<0.03  THEN SET 1000  AS spawn-heavy

# --- Orbiting particles (medium mass) ---
RULE   IF tick_in=0..20 AND depth_in=1..3 AND random<0.15  THEN SET 1100  AS spawn-orbiter

# --- Light particles (fast moving) ---
RULE   IF tick_in=0..20 AND depth_in=2..5 AND random<0.25  THEN SET 0111  AS spawn-light

# --- Dark matter (rare, high gravity influence) ---
RULE   IF tick_in=0..20 AND depth_in=1..4 AND random<0.05  THEN SET 1001  AS spawn-dark

# --- Gravitational attraction ---
# Heavy masses attract orbiters
RULE   IF tick>=21 AND family=X_LOOP AND nb_any=Y_LOOP  THEN ROTATE_CW  AS gravity-pull-orbiter

# Heavy masses attract light particles  
RULE   IF tick>=21 AND family=Z_LOOP AND nb_any=Y_LOOP  THEN ADVANCE  AS gravity-pull-light

# Dark matter attracts all
RULE   IF tick>=21 AND nb_any=DIAG_LOOP AND random<0.3  THEN ADVANCE  AS dark-gravity

# --- Orbital motion ---
# Orbiters rotate around heavies
RULE   IF tick>=21 AND family=X_LOOP AND nb_count_gte=Y_LOOP:1  THEN ROTATE_CW  AS orbit-cw

# Light particles move fast
RULE   IF tick>=21 AND family=Z_LOOP  THEN ADVANCE + ROTATE_CW  AS light-zoom

# Dark matter drifts
RULE   IF tick>=21 AND family=DIAG_LOOP  THEN ADVANCE 2  AS dark-drift

# --- Collision detection ---
# Collision flash
RULE   IF tick>=21 AND family=X_LOOP AND nb_count_gte=Y_LOOP:3  THEN SET 1111  AS collision-flash

# Merger event
RULE   IF tick>=21 AND family=Z_LOOP AND nb_count_gte=Y_LOOP:2  THEN SET 1111  AS merge-into-heavy

# --- Continuous spawning ---
# New heavy mass occasionally
RULE   IF tick>=50 AND tick%50=0 AND random<0.2  THEN SET 1000  AS new-heavy

# Orbiters spawn near heavies
RULE   IF tick>=50 AND family=Y_LOOP AND random<0.1  THEN EMIT spawn_zone  AS spawn-orbiters-near

RULE   IF tick>=50 AND depth_in=2..4 AND random<0.15 AND family=GATE  THEN SET 1100  AS spawned-orbiter

# --- Trail/aging ---
RULE   IF tick>=21  THEN INCR_VAR age 1  AS aging

# --- Default ---
DEFAULT ADVANCE
