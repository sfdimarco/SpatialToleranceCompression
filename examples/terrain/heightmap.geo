# terrain_heightmap.geo — Multi-Octave Noise Terrain Generation
# ===============================================================
# Demonstrates: Noise seeding, erosion simulation, depth as elevation
#
# Usage: python Playground.py --geo examples/terrain/heightmap.geo --grid
#
# Creates a heightmap through cellular automata in 3 phases:
#   Phase 1 (0-15):   Noise seeding - Random elevation points
#   Phase 2 (16-40):  Erosion smoothing - Natural terrain formation
#   Phase 3 (41-60):  Feature carving - Rivers and valleys
#
# Elevation is encoded in depth: depth=0 (sea level) to depth=6+ (peaks)
# Cell variable 'var_elev' tracks cumulative elevation value.

NAME   terrain_heightmap

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: NOISE SEEDING (ticks 0-15)
# Create initial elevation points using stochastic placement
# ═══════════════════════════════════════════════════════════════════════════════

# Mountain peaks - rare high elevation seeds (5% chance)
RULE   IF tick_in=0..15 AND depth=0 AND random<0.05  THEN SET 1111 + INCR_VAR elev 8  AS seed-peak

# Hills - medium elevation seeds (15% chance)
RULE   IF tick_in=0..15 AND depth=0 AND random<0.15  THEN SET 1100 + INCR_VAR elev 5  AS seed-hill

# Lowlands - gentle elevation (30% chance)
RULE   IF tick_in=0..15 AND depth=0 AND random<0.30  THEN SET 1000 + INCR_VAR elev 2  AS seed-low

# Base terrain - minimal elevation (50% chance)
RULE   IF tick_in=0..15 AND depth=0 AND random<0.50  THEN SET 0100 + INCR_VAR elev 1  AS seed-base

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: EROSION SMOOTHING (ticks 16-40)
# Cellular automata rules that smooth and spread elevation
# ═══════════════════════════════════════════════════════════════════════════════

# High areas grow when surrounded by other high areas (mountain building)
RULE   IF tick_in=16..40 AND var_elev>=6 AND nb_count_gte=GATE:3  
       THEN SET 1111 + INCR_VAR elev 1  AS mountain-grow

# Medium areas spread to neighbors (hill propagation)
RULE   IF tick_in=16..40 AND var_elev_in=3..5 AND nb_count_gte=X_LOOP:2
       THEN SET 1100 + INCR_VAR elev 1  AS hill-spread

# Low areas erode when next to high areas (valley formation)
RULE   IF tick_in=16..40 AND var_elev<=2 AND nb_any=Y_LOOP
       THEN SET 0010 + INCR_VAR elev -1  AS valley-erode

# Edge smoothing - average with neighbors
RULE   IF tick_in=16..40 AND depth=0 AND nb_count_gte=GATE:1
       THEN ADVANCE + INCR_VAR elev 1  AS edge-smooth

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: RIVER CARVING (ticks 41-60)
# Water flows from high to low, carving river channels
# ═══════════════════════════════════════════════════════════════════════════════

# Rivers start at peaks and flow downhill
RULE   IF tick>=41 AND var_elev>=7 AND random<0.3
       THEN SET 0001 + INCR_VAR flow 1 + EMIT water_source  AS river-source

# Water flows to lowest neighbor
RULE   IF tick>=41 AND var_flow>=1 AND nb_any=GATE
       THEN SET 0001 + INCR_VAR flow 1 + EMIT water_flow  AS river-flow

# River carving - deepen the channel
RULE   IF tick>=41 AND var_flow>=3
       THEN SET 0000 + INCR_VAR elev -2  AS river-carve

# Lake formation - water pools in low areas
RULE   IF tick>=41 AND var_elev<=1 AND nb_count_gte=Y_LOOP:3
       THEN SET 0011 + SET_VAR flow 5  AS lake-form

# ═══════════════════════════════════════════════════════════════════════════════
# DEPTH-BASED ELEVATION VISUALIZATION
# Different depths represent different elevation bands
# ═══════════════════════════════════════════════════════════════════════════════

# Snow-capped peaks (depth 5-6)
RULE   IF depth_in=5..6 AND var_elev>=6  THEN SET 1111  AS snow-peak
RULE   IF depth_in=5..6 AND var_elev<6   THEN SET 1100  AS rock-peak

# Forest zone (depth 3-4)
RULE   IF depth_in=3..4 AND var_elev>=3  THEN SET 1100  AS forest-high
RULE   IF depth_in=3..4 AND var_elev<3   THEN SET 1000  AS forest-low

# Grassland (depth 1-2)
RULE   IF depth_in=1..2 AND var_elev>=2  THEN SET 1000  AS grass-mid
RULE   IF depth_in=1..2 AND var_elev<2   THEN SET 0100  AS grass-low

# Water level (depth 0)
RULE   IF depth=0 AND var_elev<=1        THEN SET 0011  AS water
RULE   IF depth=0 AND var_elev>=2        THEN SET 0100  AS shore

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNALS FOR GAME INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF tick=15   THEN EMIT phase_noise_complete    AS signal-phase1
RULE   IF tick=40   THEN EMIT phase_erosion_complete  AS signal-phase2
RULE   IF tick=60   THEN EMIT phase_rivers_complete   AS signal-phase3
RULE   IF tick=60   THEN EMIT terrain_ready          AS signal-ready

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT: Continue terrain evolution
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE + INCR_VAR age 1
