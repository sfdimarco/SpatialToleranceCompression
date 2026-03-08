# terrain_caves.geo — Cellular Automata Cave Generation
# ======================================================
# Demonstrates: Cellular automata rules, birth/survival conditions, smoothing
#
# Usage: python Playground.py --geo examples/terrain/caves.geo --grid
#
# Generates cave systems using cellular automata similar to the
# classic "Cellular Automata Cave Generator" algorithm:
#
#   Phase 1 (0-5):    Random noise seeding (45% walls)
#   Phase 2 (6-20):   Cellular smoothing (birth=5+, survive=4+)
#   Phase 3 (21-35):  Cave expansion and connection
#   Phase 4 (36-50):  Feature refinement (remove isolated walls)
#
# Output: Walkable cave floors (GATE_OFF) and solid walls (GATE_ON)
#
# Rules:
#   - A floor tile becomes a wall if 5+ neighbors are walls
#   - A wall tile becomes floor if 5+ neighbors are floor
#   - This creates natural-looking cave formations

NAME   terrain_caves

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: RANDOM NOISE SEEDING (ticks 0-5)
# Initialize grid with ~45% walls, ~55% open space
# ═══════════════════════════════════════════════════════════════════════════════

# Create initial random wall distribution
RULE   IF tick_in=0..5 AND random<0.45
       THEN SET 1111 + SET_VAR wall_age 0  AS seed-wall

# Initial open space
RULE   IF tick_in=0..5 AND random>=0.45
       THEN SET 0000  AS seed-floor

# Border walls - always solid to contain the cave
RULE   IF depth=0
       THEN SET 1111  AS border-wall

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: CELLULAR SMOOTHING (ticks 6-20)
# Apply birth/survival rules to create natural cave shapes
# ═══════════════════════════════════════════════════════════════════════════════

# ─── SURVIVAL RULE: Wall stays wall if 4+ wall neighbors ──────────────────────
RULE   IF tick_in=6..20 AND mask=1111 AND nb_count8_gte=GATE:4
       THEN SET 1111 + INCR_VAR wall_age 1  AS wall-survive

# ─── BIRTH RULE: Floor becomes wall if 5+ wall neighbors ──────────────────────
RULE   IF tick_in=6..20 AND mask=0000 AND nb_count8_gte=GATE:5
       THEN SET 1111 + SET_VAR wall_age 0  AS floor-to-wall

# ─── DEATH RULE: Wall becomes floor if 5+ floor neighbors ─────────────────────
RULE   IF tick_in=6..20 AND mask=1111 AND nb_count8_lte=GATE:3
       THEN SET 0000  AS wall-to-floor

# ─── STABILITY: Floor stays floor with few wall neighbors ─────────────────────
RULE   IF tick_in=6..20 AND mask=0000 AND nb_count8_lte=GATE:4
       THEN SET 0000  AS floor-stable

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: CAVE EXPANSION (ticks 21-35)
# Widen corridors and connect isolated chambers
# ═══════════════════════════════════════════════════════════════════════════════

# Erode single-cell protrusions (smooths walls)
RULE   IF tick_in=21..35 AND mask=1111 AND nb_count8=GATE:1
       THEN SET 0000  AS erode-protrusion

# Fill single-cell holes (smooths floors)
RULE   IF tick_in=21..35 AND mask=0000 AND nb_count8=GATE:7
       THEN SET 1111  AS fill-hole

# Expand large chambers (walls adjacent to 3+ floors become floor)
RULE   IF tick_in=21..35 AND mask=1111 AND nb_count8_lte=GATE:5 AND var_wall_age>=10
       THEN SET 0000  AS expand-chamber

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: FEATURE REFINEMENT (ticks 36-50)
# Remove small isolated regions, add cave features
# ═══════════════════════════════════════════════════════════════════════════════

# Remove isolated wall clusters (less than 4 connected walls)
RULE   IF tick_in=36..50 AND mask=1111 AND nb_count8=GATE:0
       THEN SET 0000  AS remove-isolated-wall

# Remove isolated floor pockets (less than 4 connected floors)
RULE   IF tick_in=36..50 AND mask=0000 AND nb_count8=GATE:0
       THEN SET 1111  AS remove-isolated-floor

# Create cave pillars (random tall wall columns)
RULE   IF tick_in=36..50 AND mask=1111 AND random<0.02 AND var_wall_age>=20
       THEN SET 1111 + EMIT pillar  AS create-pillar

# Create underground pools (water-filled depressions)
RULE   IF tick_in=36..50 AND mask=0000 AND nb_count8=GATE:8 AND random<0.05
       THEN SET 0011 + EMIT pool  AS create-pool

# ═══════════════════════════════════════════════════════════════════════════════
# CAVE DECORATION (ticks 51+)
# Add stalactites, stalagmites, and other features
# ═══════════════════════════════════════════════════════════════════════════════

# Stalactites on ceiling (walls above floor)
RULE   IF tick>=51 AND mask=1111 AND nb_N=GATE AND random<0.1
       THEN SET 1100  AS stalactite

# Stalagmites on floor (floor below wall)
RULE   IF tick>=51 AND mask=0000 AND nb_N=GATE AND random<0.1
       THEN SET 0011  AS stalagmite

# Cave moss (old walls gain texture)
RULE   IF tick>=51 AND var_wall_age>=30 AND random<0.05
       THEN SET 1010  AS cave-moss

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNALS FOR GAME INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF tick=5   THEN EMIT phase_seeding_complete   AS signal-phase1
RULE   IF tick=20  THEN EMIT phase_smoothing_complete AS signal-phase2
RULE   IF tick=35  THEN EMIT phase_expansion_complete AS signal-phase3
RULE   IF tick=50  THEN EMIT phase_refinement_complete AS signal-phase4
RULE   IF tick=50  THEN EMIT caves_ready              AS signal-ready

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT: Continue cave evolution
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE
