# gravity_cosmos.geo - Gravitational Particle Cosmos
# ====================================================
# A cosmic particle simulation with gravity-like attraction,
# orbital mechanics, and emergent galaxy formation.

NAME   gravity_cosmos

# --- Initial spawning phase (ticks 0-20) ---
# Heavy mass centers (gravitational anchors)
RULE   IF tick_in=0..20 AND depth=0 AND random<0.03  THEN SET 1000  AS spawn-heavy

# Orbiting particles (medium mass)
RULE   IF tick_in=0..20 AND depth_in=1..3 AND random<0.15  THEN SET 1100  AS spawn-orbiter

# Light particles (fast moving)
RULE   IF tick_in=0..20 AND depth_in=2..5 AND random<0.25  THEN SET 0111  AS spawn-light

# Dark matter (rare, high gravity influence)
RULE   IF tick_in=0..20 AND depth_in=1..4 AND random<0.05  THEN SET 1001  AS spawn-dark

# --- Post-spawn behavior (tick >= 21) ---
# Heavy masses stay stable but rotate slowly
RULE   IF tick>=21 AND family=Y_LOOP AND tick%20=0  THEN ROTATE_CW  AS heavy-rotate

# Orbiters cycle around heavies
RULE   IF tick>=21 AND family=X_LOOP AND tick%8=0  THEN SWITCH X_LOOP  AS orbit-cycle

# Light particles move fast (advance multiple steps)
RULE   IF tick>=21 AND family=Z_LOOP  THEN ADVANCE 2  AS light-fast

# Dark matter drifts slowly
RULE   IF tick>=21 AND family=DIAG_LOOP AND tick%6=0  THEN ADVANCE  AS dark-drift

# --- Collision/merger events ---
# Collision flash (when too many neighbors)
RULE   IF tick>=21 AND family=X_LOOP AND nb_count8_gte=Y_LOOP:3  THEN SET 1111  AS collision-flash

# Merger creates heavy mass
RULE   IF tick>=21 AND family=Z_LOOP AND nb_count8_gte=Y_LOOP:2  THEN SET 1000  AS merge-into-heavy

# --- Continuous spawning ---
# New heavy mass occasionally
RULE   IF tick>=50 AND tick%50=0 AND random<0.2  THEN SET 1000  AS new-heavy

# Orbiters spawn near heavies
RULE   IF tick>=50 AND family=Y_LOOP AND random<0.1  THEN SET 1100  AS spawn-orbiters-near

# Light particles from void
RULE   IF tick>=50 AND depth_in=2..4 AND random<0.15 AND mask=0000  THEN SET 0111  AS spawned-light

# --- Aging and decay ---
# Old light particles fade
RULE   IF tick>=100 AND family=Z_LOOP AND random<0.02  THEN SET 0000  AS light-fade

# --- Void handling ---
RULE   IF mask=0000 AND tick%30=0 AND random<0.1  THEN SET 1100  AS void-spawn

# --- Default ---
DEFAULT ADVANCE
