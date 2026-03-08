# selforg_voronoi.geo — Voronoi Diagram Generation
# =================================================
# Demonstrates: Region growth, territory competition, signal propagation
#
# Usage: python Playground.py --geo examples/selforg/voronoi.geo --grid
#
# Generates a Voronoi diagram by growing colored regions from seed points.
# Each seed emits a unique "color" signal that spreads outward.
# When regions meet, they form natural boundaries.
#
# Process:
#   Phase 1 (0-10):   Random seed placement
#   Phase 2 (11-50):  Region growth via signal propagation
#   Phase 3 (51-80):  Boundary refinement
#
# Colors (loop families):
#   Y_LOOP (red)    = Region 1
#   X_LOOP (green)  = Region 2
#   Z_LOOP (blue)   = Region 3
#   DIAG_LOOP (gold)= Region 4

NAME   selforg_voronoi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: SEED PLACEMENT (ticks 0-10)
# Create 4-8 random seed points across the grid
# ═══════════════════════════════════════════════════════════════════════════════

# Seed A (red) - place 2-3 seeds
RULE   IF tick_in=0..10 AND random<0.02
       THEN SET 1000 + SET_VAR region 1 + EMIT seed_A  AS seed-A

# Seed B (green) - place 2-3 seeds
RULE   IF tick_in=0..10 AND random<0.02 AND tick%3=1
       THEN SET 1100 + SET_VAR region 2 + EMIT seed_B  AS seed-B

# Seed C (blue) - place 2-3 seeds
RULE   IF tick_in=0..10 AND random<0.02 AND tick%3=2
       THEN SET 0111 + SET_VAR region 3 + EMIT seed_C  AS seed-C

# Seed D (gold) - place 1-2 seeds
RULE   IF tick_in=0..10 AND random<0.015 AND tick%3=0
       THEN SET 1001 + SET_VAR region 4 + EMIT seed_D  AS seed-D

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: REGION GROWTH (ticks 11-50)
# Each region grows by converting empty neighbors
# ═══════════════════════════════════════════════════════════════════════════════

# Region A growth (red)
RULE   IF tick_in=11..50 AND mask=0000 AND nb_any=Y_LOOP
       THEN SET 1000 + SET_VAR region 1 + EMIT grow_A  AS grow-A

# Region B growth (green)
RULE   IF tick_in=11..50 AND mask=0000 AND nb_any=X_LOOP
       THEN SET 1100 + SET_VAR region 2 + EMIT grow_B  AS grow-B

# Region C growth (blue)
RULE   IF tick_in=11..50 AND mask=0000 AND nb_any=Z_LOOP
       THEN SET 0111 + SET_VAR region 3 + EMIT grow_C  AS grow-C

# Region D growth (gold)
RULE   IF tick_in=11..50 AND mask=0000 AND nb_any=DIAG_LOOP
       THEN SET 1001 + SET_VAR region 4 + EMIT grow_D  AS grow-D

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: BOUNDARY FORMATION (ticks 51-80)
# When regions meet, form stable boundaries
# ═══════════════════════════════════════════════════════════════════════════════

# Boundary cells (adjacent to different regions) - mark as boundary
RULE   IF tick_in=51..80 AND var_region=1 AND nb_any=X_LOOP
       THEN SET 1010 + SET_VAR boundary 1  AS boundary-AB

RULE   IF tick_in=51..80 AND var_region=1 AND nb_any=Z_LOOP
       THEN SET 1010 + SET_VAR boundary 1  AS boundary-AC

RULE   IF tick_in=51..80 AND var_region=2 AND nb_any=Z_LOOP
       THEN SET 1010 + SET_VAR boundary 1  AS boundary-BC

# Stable interior cells (surrounded by same region)
RULE   IF tick_in=51..80 AND var_region=1 AND nb_count=Y_LOOP:4
       THEN SET 1000 + SET_VAR interior 1  AS interior-A

RULE   IF tick_in=51..80 AND var_region=2 AND nb_count=X_LOOP:4
       THEN SET 1100 + SET_VAR interior 1  AS interior-B

RULE   IF tick_in=51..80 AND var_region=3 AND nb_count=Z_LOOP:4
       THEN SET 0111 + SET_VAR interior 1  AS interior-C

RULE   IF tick_in=51..80 AND var_region=4 AND nb_count=DIAG_LOOP:4
       THEN SET 1001 + SET_VAR interior 1  AS interior-D

# ═══════════════════════════════════════════════════════════════════════════════
# GROWTH COMPETITION
# When multiple regions try to grow into same cell, pick one
# ═══════════════════════════════════════════════════════════════════════════════

# Priority: A > B > C > D (first match wins)
RULE   IF tick_in=11..50 AND mask=0000 AND nb_N=Y_LOOP
       THEN SET 1000 + SET_VAR region 1  AS compete-A-wins

RULE   IF tick_in=11..50 AND mask=0000 AND nb_N=X_LOOP AND NOT nb_any=Y_LOOP
       THEN SET 1100 + SET_VAR region 2  AS compete-B-wins

RULE   IF tick_in=11..50 AND mask=0000 AND nb_N=Z_LOOP AND NOT nb_any=Y_LOOP AND NOT nb_any=X_LOOP
       THEN SET 0111 + SET_VAR region 3  AS compete-C-wins

# ═══════════════════════════════════════════════════════════════════════════════
# REGION SIZE TRACKING
# Count cells in each region for statistics
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF var_region=1 AND tick%10=0  THEN INCR_VAR size_A 1  AS count-A
RULE   IF var_region=2 AND tick%10=0  THEN INCR_VAR size_B 1  AS count-B
RULE   IF var_region=3 AND tick%10=0  THEN INCR_VAR size_C 1  AS count-C
RULE   IF var_region=4 AND tick%10=0  THEN INCR_VAR size_D 1  AS count-D

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNALS FOR GAME INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF tick=10  THEN EMIT phase_seeding_complete  AS signal-phase1
RULE   IF tick=50  THEN EMIT phase_growth_complete   AS signal-phase2
RULE   IF tick=80  THEN EMIT phase_boundary_complete AS signal-phase3
RULE   IF tick=80  THEN EMIT voronoi_ready           AS signal-ready

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT: Continue growth
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE
