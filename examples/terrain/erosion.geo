# terrain_erosion.geo — Hydraulic Erosion Simulation
# ===================================================
# Demonstrates: Sediment transport, terrain aging, multi-variable simulation
#
# Usage: python Playground.py --geo examples/terrain/erosion.geo --grid
#
# Simulates long-term erosion processes:
#   Phase 1 (0-20):   Initial terrain with rainfall
#   Phase 2 (21-50):  Sediment transport and deposition
#   Phase 3 (51-80):  Valley deepening and smoothing
#   Phase 4 (81-100): Terrain maturation
#
# Cell Variables:
#   var_elev    - Elevation (0-10)
#   var_water   - Water content (0-5)
#   var_sediment - Sediment carried (0-5)
#   var_age     - Terrain age in ticks

NAME   terrain_erosion

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: INITIAL TERRAIN AND RAINFALL (ticks 0-20)
# ═══════════════════════════════════════════════════════════════════════════════

# Initial mountainous terrain (random high points)
RULE   IF tick_in=0..20 AND depth>=4 AND random<0.2
       THEN SET 1111 + SET_VAR elev 8 + SET_VAR age 0  AS init-peak

RULE   IF tick_in=0..20 AND depth_in=2..4 AND random<0.4
       THEN SET 1100 + SET_VAR elev 5 + SET_VAR age 0  AS init-hill

RULE   IF tick_in=0..20 AND depth_in=0..2 AND random<0.6
       THEN SET 1000 + SET_VAR elev 2 + SET_VAR age 0  AS init-low

# Rainfall adds water to terrain
RULE   IF tick_in=0..20 AND random<0.3 AND var_water<5
       THEN INCR_VAR water 1 + EMIT rain  AS rainfall

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: SEDIMENT TRANSPORT (ticks 21-50)
# Water picks up and carries sediment downhill
# ═══════════════════════════════════════════════════════════════════════════════

# Water picks up sediment from high elevation
RULE   IF tick_in=21..50 AND var_water>=1 AND var_elev>=5
       THEN INCR_VAR sediment 1 + INCR_VAR water -1  AS pickup-sediment

# Sediment transport downhill
RULE   IF tick_in=21..50 AND var_sediment>=1 AND var_elev>=3
       THEN INCR_VAR sediment -1 + EMIT sediment_flow  AS transport-down

# Sediment deposition in low areas
RULE   IF tick_in=21..50 AND var_sediment>=1 AND var_elev<=2
       THEN INCR_VAR elev 1 + SET_VAR sediment 0  AS deposit-sediment

# River bed formation (continuous flow carves channel)
RULE   IF tick_in=21..50 AND var_water>=3 AND var_elev>=2
       THEN INCR_VAR elev -1 + INCR_VAR sediment 1  AS carve-channel

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: VALLEY DEEPENING (ticks 51-80)
# Sustained water flow deepens valleys and creates V-shapes
# ═══════════════════════════════════════════════════════════════════════════════

# Valley deepening - water erodes elevation
RULE   IF tick_in=51..80 AND var_water>=2 AND var_elev>=3
       THEN INCR_VAR elev -1 + INCR_VAR sediment 1 + INCR_VAR age 1  AS valley-deepen

# Valley widening - erosion spreads to neighbors
RULE   IF tick_in=51..80 AND var_elev>=3 AND nb_any=GATE AND random<0.1
       THEN INCR_VAR elev -1  AS valley-widen

# Cliff formation (steep elevation changes)
RULE   IF tick_in=51..80 AND var_elev>=5 AND nb_count_lte=GATE:2
       THEN SET 1111  AS cliff-form

# Talus slope (debris at cliff base — near tall walls)
RULE   IF tick_in=51..80 AND var_elev<=3 AND nb_any=GATE
       THEN INCR_VAR elev 1  AS talus-form

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: TERRAIN MATURATION (ticks 81-100)
# Terrain reaches equilibrium, erosion slows
# ═══════════════════════════════════════════════════════════════════════════════

# Mature terrain - slow erosion rate
RULE   IF tick_in=81..100 AND var_water>=1 AND var_elev>=2 AND var_age>=50
       THEN INCR_VAR elev -1 + INCR_VAR age 1  AS mature-erosion

# Floodplain formation (flat areas near rivers)
RULE   IF tick_in=81..100 AND var_elev<=1 AND var_water>=2
       THEN SET 0011 + INCR_VAR age 1  AS floodplain

# Alluvial fan (sediment fan at mountain base)
RULE   IF tick_in=81..100 AND var_sediment>=2 AND var_elev_in=2..3
       THEN SET 0111 + SET_VAR sediment 0  AS alluvial-fan

# ═══════════════════════════════════════════════════════════════════════════════
# EROSION FEATURES
# ═══════════════════════════════════════════════════════════════════════════════

# Canyon formation (deep, narrow valley)
RULE   IF tick>=50 AND var_elev>=4 AND var_water>=4 AND nb_count=GATE:2
       THEN SET 0000 + INCR_VAR elev -2  AS canyon

# Mesa formation (isolated flat-topped hill)
RULE   IF tick>=50 AND var_elev>=5 AND nb_count_lte=GATE:1
       THEN SET 1111  AS mesa

# Butte erosion (smaller than mesa)
RULE   IF tick>=70 AND var_elev>=4 AND var_age>=40 AND nb_count=GATE:0
       THEN SET 1100  AS butte

# ═══════════════════════════════════════════════════════════════════════════════
# VEGETATION GROWTH (affected by erosion)
# ═══════════════════════════════════════════════════════════════════════════════

# Vegetation on stable slopes
RULE   IF tick>=60 AND var_elev_in=2..4 AND var_water>=2 AND var_age>=30
       THEN SET 1100  AS vegetation-slope

# Vegetation in valleys
RULE   IF tick>=60 AND var_elev_in=1..2 AND var_water>=3
       THEN SET 1000  AS vegetation-valley

# Bare rock on steep/young terrain
RULE   IF tick>=60 AND var_elev>=5 AND var_age<20
       THEN SET 1111  AS bare-rock

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNALS FOR GAME INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF tick=20  THEN EMIT phase_rainfall_complete  AS signal-phase1
RULE   IF tick=50  THEN EMIT phase_transport_complete AS signal-phase2
RULE   IF tick=80  THEN EMIT phase_valley_complete    AS signal-phase3
RULE   IF tick=100 THEN EMIT phase_mature_complete    AS signal-phase4
RULE   IF tick=100 THEN EMIT erosion_ready            AS signal-ready

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT: Continue erosion simulation
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE
