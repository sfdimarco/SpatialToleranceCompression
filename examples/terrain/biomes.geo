# terrain_biomes.geo — Biome Assignment by Elevation and Moisture
# ================================================================
# Demonstrates: Multi-variable conditions, biome logic, neighbor propagation
#
# Usage: python Playground.py --geo examples/terrain/biomes.geo --grid
#
# Assigns biomes based on two factors:
#   1. Elevation (encoded in depth): depth=0 (sea) to depth=6+ (peaks)
#   2. Moisture (var_wet): 0 (arid) to 10 (saturated)
#
# Biome Types:
#   Ocean (deep blue)  - Sea level, any moisture
#   Beach (sand)       - Shore transition
#   Desert (yellow)    - Low moisture, low elevation
#   Grassland (green)  - Medium moisture, low elevation
#   Forest (dark green)- High moisture, low-medium elevation
#   Swamp (teal)       - High moisture, sea level
#   Taiga (pine)       - Medium moisture, medium elevation
#   Tundra (white)     - Low moisture, high elevation
#   Snow (bright white)- Any moisture, peaks
#
# Moisture propagates from water sources via neighbor rules.

NAME   terrain_biomes

# ═══════════════════════════════════════════════════════════════════════════════
# MOISTURE PROPAGATION
# Water sources spread moisture to neighbors over time
# ═══════════════════════════════════════════════════════════════════════════════

# Ocean and lakes are moisture sources
RULE   IF depth=0 AND mask_in=0011,0111,1011,1101,1110,1111
       THEN INCR_VAR wet 1 + EMIT moisture  AS moisture-ocean

# Rivers provide moisture
RULE   IF var_flow>=1 THEN INCR_VAR wet 1 + EMIT moisture  AS moisture-river

# Moisture spreads to adjacent cells
RULE   IF nb_any=GATE AND var_wet<10
       THEN INCR_VAR wet 1  AS moisture-spread

# Rainfall effect - all cells slowly gain ambient moisture
RULE   IF tick%20=0 AND var_wet<5
       THEN INCR_VAR wet 1  AS moisture-rain

# ═══════════════════════════════════════════════════════════════════════════════
# BIOME ASSIGNMENT RULES
# First matching rule wins - order matters!
# ═══════════════════════════════════════════════════════════════════════════════

# ─── SNOW / ICE (highest elevation) ───────────────────────────────────────────
RULE   IF depth>=5 THEN SET 1111  AS biome-snow
# Bright white for permanent snow

# ─── TUNDRA (high elevation, low moisture) ────────────────────────────────────
RULE   IF depth_in=4..5 AND var_wet<=3
       THEN SET 1001  AS biome-tundra
# Pale, sparse vegetation pattern

# ─── TAIGA / BOREAL FOREST (high elevation, medium moisture) ──────────────────
RULE   IF depth_in=3..4 AND var_wet_in=4..7
       THEN SET 1100  AS biome-taiga
# Coniferous forest pattern

# ─── TEMPERATE FOREST (medium elevation, high moisture) ───────────────────────
RULE   IF depth_in=2..3 AND var_wet>=7
       THEN SET 0111  AS biome-forest
# Dense green forest

# ─── GRASSLAND / SAVANNA (low elevation, medium moisture) ─────────────────────
RULE   IF depth_in=1..2 AND var_wet_in=4..6
       THEN SET 1000  AS biome-grassland
# Open grassy plains

# ─── DESERT (low elevation, low moisture) ─────────────────────────────────────
RULE   IF depth_in=1..2 AND var_wet<=3
       THEN SET 0100  AS biome-desert
# Sandy, arid pattern

# ─── SWAMP / MARSH (sea level, high moisture) ─────────────────────────────────
RULE   IF depth=0 AND var_wet>=8
       THEN SET 0110  AS biome-swamp
# Wetland with vegetation

# ─── BEACH (sea level, medium moisture) ───────────────────────────────────────
RULE   IF depth=0 AND var_wet_in=4..7
       THEN SET 1010  AS biome-beach
# Sandy shore transition

# ─── OCEAN (sea level, any moisture) ──────────────────────────────────────────
RULE   IF depth=0
       THEN SET 0001  AS biome-ocean
# Deep water

# ═══════════════════════════════════════════════════════════════════════════════
# BIOME TRANSITION ZONES
# Smooth transitions between biomes using neighbor blending
# ═══════════════════════════════════════════════════════════════════════════════

# Forest-Desert transition (savanna) — near high-moisture areas
RULE   IF depth_in=1..2 AND var_wet=4 AND nb_count_gte=Z_LOOP:2
       THEN SET 1010  AS transition-savanna

# Grassland-Forest transition (woodland) — near dense canopy
RULE   IF depth_in=2..3 AND var_wet=6 AND nb_count_gte=Z_LOOP:1
       THEN SET 1100  AS transition-woodland

# Beach-Ocean transition (shallows) — near arid zones
RULE   IF depth=0 AND var_wet>=5 AND nb_any=Y_LOOP
       THEN SET 0011  AS transition-shallows

# ═══════════════════════════════════════════════════════════════════════════════
# SPECIAL FEATURES
# ═══════════════════════════════════════════════════════════════════════════════

# Oasis in desert (rare water source)
RULE   IF depth_in=1..2 AND var_wet<=2 AND random<0.001
       THEN SET 0011 + SET_VAR wet 10  AS feature-oasis

# Volcano on peaks (rare high-energy feature)
RULE   IF depth>=5 AND random<0.0005
       THEN SET 1111 + SET_VAR heat 10 + EMIT volcano  AS feature-volcano

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNALS FOR GAME INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF tick=50  THEN EMIT biomes_assigned    AS signal-biomes-done
RULE   IF tick=60  THEN EMIT transitions_ready   AS signal-transitions-done
RULE   IF tick=100 THEN EMIT terrain_mature      AS signal-ready

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT: Continue biome simulation
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE
