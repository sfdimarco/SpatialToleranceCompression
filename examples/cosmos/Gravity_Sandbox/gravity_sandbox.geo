# gravity_sandbox.geo
# ====================
# A satisfying gravity sandbox with .geo-driven orbital mechanics
# 
# Particle Types (encoded in 4-bit masks):
#   1000 (Y_LOOP) = Heavy mass (sun/black hole) - GOLD
#   1100 (X_LOOP) = Normal mass (planet) - BLUE
#   0111 (Z_LOOP) = Light particle (dust) - RED
#   1001 (DIAG)   = Dark matter (invisible gravity) - PURPLE
#   1111 (GATE)   = Collision flash - WHITE
#   0000 (VOID)   = Empty space
#
# .geo Rules create emergent orbital behavior!

NAME gravity_sandbox

# ═══════════════════════════════════════════════════════════════════════════════
# ALIASES
# ═══════════════════════════════════════════════════════════════════════════════

DEFINE is_heavy      mask=1000
DEFINE is_normal     mask=1100
DEFINE is_light      mask=0111
DEFINE is_dark       mask=1001
DEFINE is_collision  mask=1111
DEFINE is_void       mask=0000

DEFINE is_heavy_nb   nb_count8=1000:1
DEFINE has_heavy_nb  nb_count8=1000:1
DEFINE has_normal_nb nb_count8=1100:1
DEFINE is_normal_nb  nb_count8=1100:1
DEFINE has_light_nb  nb_count8=0111:1
DEFINE is_light_nb   nb_count8=0111:1
DEFINE is_dark_nb    nb_count8=1001:1
DEFINE has_dark_nb   nb_count8=1001:1
DEFINE crowded       nb_count8_gte=GATES:3

# ═══════════════════════════════════════════════════════════════════════════════
# HEAVY MASS BEHAVIOR (Suns/Black Holes)
# ═══════════════════════════════════════════════════════════════════════════════

# Heavy masses are stable but slowly rotate (spin)
RULE IF is_heavy AND tick%30=0 THEN ROTATE_CW AS heavy_spin

# Heavy masses attract nearby matter (visualized by rotation toward center)
RULE IF is_heavy AND has_normal_nb THEN ADVANCE AS heavy_attract

# Heavy masses can merge when too close (collision)
RULE IF is_heavy AND is_heavy_nb AND random<0.05 THEN SET 1111 AS heavy_merge_flash

# After flash, become bigger heavy mass
RULE IF is_collision AND tick%5=0 THEN SET 1000 AS collision_resolve

# ═══════════════════════════════════════════════════════════════════════════════
# NORMAL MASS BEHAVIOR (Planets)
# ═══════════════════════════════════════════════════════════════════════════════

# Normal masses orbit heavy ones (rotate around)
RULE IF is_normal AND is_heavy_nb AND tick%8=0 THEN ROTATE_CW AS orbit_heavy

# Normal masses drift when isolated
RULE IF is_normal AND NOT is_heavy_nb AND tick%12=0 THEN ADVANCE AS normal_drift

# Normal masses can form rings around heavy (cycling pattern)
RULE IF is_normal AND crowded AND tick%6=0 THEN SWITCH X_LOOP AS form_ring

# ═══════════════════════════════════════════════════════════════════════════════
# LIGHT PARTICLE BEHAVIOR (Dust/Debris)
# ═══════════════════════════════════════════════════════════════════════════════

# Light particles spiral into heavy masses
RULE IF is_light AND is_heavy_nb THEN ADVANCE 2 AS light_spiral

# Light particles form accretion disks (fast rotation)
RULE IF is_light AND crowded AND tick%4=0 THEN ROTATE_CW AS accretion_spin

# Light particles can coalesce into normal mass
RULE IF is_light AND nb_count8=0111:3 AND random<0.02 THEN SET 1100 AS light_coalesce

# ═══════════════════════════════════════════════════════════════════════════════
# DARK MATTER BEHAVIOR (Invisible Gravity)
# ═══════════════════════════════════════════════════════════════════════════════

# Dark matter drifts slowly
RULE IF is_dark AND tick%15=0 THEN ADVANCE AS dark_drift

# Dark matter attracts all types
RULE IF is_dark AND nb_any=Y_LOOP THEN ROTATE_CW AS dark_pull_heavy
RULE IF is_dark AND nb_any=X_LOOP THEN ADVANCE AS dark_pull_normal

# Dark matter can clump together
RULE IF is_dark AND is_dark_nb AND random<0.03 THEN SET 1001 AS dark_clump

# ═══════════════════════════════════════════════════════════════════════════════
# COLLISION EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

# Collision flash when masses collide
RULE IF is_normal AND is_normal_nb AND random<0.1 THEN SET 1111 AS normal_collision

# Spiral collision creates beautiful pattern
RULE IF is_light AND is_heavy_nb AND random<0.05 THEN SET 1111 AS light_impact

# ═══════════════════════════════════════════════════════════════════════════════
# ORBITAL RESONANCE PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════

# Create spiral arm pattern (tick-based rotation)
RULE IF tick%100=0 AND is_heavy THEN ROTATE_CW AS spiral_trigger

# Resonance: particles sync their orbits
RULE IF tick%50=0 AND is_normal AND is_normal_nb THEN SWITCH X_LOOP AS resonance_sync

# ═══════════════════════════════════════════════════════════════════════════════
# WAVE/RIPPLE PROPAGATION
# ═══════════════════════════════════════════════════════════════════════════════

# Collision creates gravitational wave (expanding ring)
RULE IF is_collision AND tick%3=0 THEN EMIT gravity_wave AS wave_emit

# Wave affects nearby particles
RULE IF signal=gravity_wave AND is_light THEN ADVANCE 3 AS wave_push_light
RULE IF signal=gravity_wave AND is_normal THEN ADVANCE AS wave_push_normal

# ═══════════════════════════════════════════════════════════════════════════════
# SPONTANEOUS GENERATION (Sandbox Mode)
# ═══════════════════════════════════════════════════════════════════════════════

# Void can spontaneously create light particles
RULE IF is_void AND random<0.001 THEN SET 0111 AS vacuum_fluctuation

# Heavy masses occasionally spawn orbiting particles
RULE IF is_heavy AND tick%100=0 AND random<0.3 THEN EMIT spawn_planet AS heavy_spawn

# ═══════════════════════════════════════════════════════════════════════════════
# ENERGY DISSIPATION
# ═══════════════════════════════════════════════════════════════════════════════

# Old collision flashes fade
RULE IF is_collision AND var_age>=10 THEN SET 0000 AS flash_fade

# Light particles eventually fall into heavy (disappear)
RULE IF is_light AND is_heavy_nb AND var_age>=200 AND random<0.1 THEN SET 0000 AS light_absorb

# ═══════════════════════════════════════════════════════════════════════════════
# AGE TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

# All particles age
RULE IF tick%50=0 THEN INCR_VAR age 50 AS aging

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT
# ═══════════════════════════════════════════════════════════════════════════════

# Default: gentle advancement through loop families
DEFAULT ADVANCE
