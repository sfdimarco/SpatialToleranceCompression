# terrain_rivers.geo — River Network Generation with Watersheds
# ==============================================================
# Demonstrates: Flow accumulation, watershed carving, erosion simulation
#
# Usage: python Playground.py --geo examples/terrain/rivers.geo --grid
#
# Simulates river formation through flow accumulation:
#   Phase 1 (0-10):   Rainfall and initial flow
#   Phase 2 (11-30):  Flow accumulation and channel formation
#   Phase 3 (31-50):  River carving and tributary creation
#   Phase 4 (51-70):  Delta formation at ocean
#
# Uses cell variable 'var_flow' to track water volume.
# Higher flow = wider/deeper river channels.

NAME   terrain_rivers

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: RAINFALL AND INITIAL FLOW (ticks 0-10)
# Water begins at high elevation and flows downhill
# ═══════════════════════════════════════════════════════════════════════════════

# Rainfall on peaks (depth 5+) creates water sources
RULE   IF tick_in=0..10 AND depth>=5 AND random<0.3
       THEN SET_VAR flow 1 + EMIT rain  AS rainfall

# Water flows to lowest available neighbor (simulated via depth preference)
RULE   IF tick_in=0..10 AND var_flow>=1
       THEN INCR_VAR flow 1 + EMIT flow_down  AS initial-flow

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: FLOW ACCUMULATION (ticks 11-30)
# Water accumulates as tributaries merge
# ═══════════════════════════════════════════════════════════════════════════════

# Water flows downhill - accumulate from higher neighbors
RULE   IF tick_in=11..30 AND nb_any=Y_LOOP AND var_flow>=0
       THEN INCR_VAR flow 2  AS tributary-merge

# Channels form where flow accumulates (flow >= 3)
RULE   IF tick_in=11..30 AND var_flow>=3
       THEN SET 0001 + INCR_VAR channel 1  AS channel-form

# Main river forms with high flow (flow >= 6)
RULE   IF tick_in=11..30 AND var_flow>=6
       THEN SET 0011 + INCR_VAR channel 2  AS river-main

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: RIVER CARVING (ticks 31-50)
# Rivers erode terrain, creating valleys
# ═══════════════════════════════════════════════════════════════════════════════

# River carving - high flow erodes deeper channels
RULE   IF tick_in=31..50 AND var_flow>=5
       THEN SET 0000 + INCR_VAR depth_carve 1  AS river-carve

# Meander formation - rivers curve randomly
RULE   IF tick_in=31..50 AND var_flow>=4 AND random<0.1
       THEN ROTATE_CW  AS river-meander

# Tributary creation - smaller streams feed main river
RULE   IF tick_in=31..50 AND var_flow>=3 AND random<0.15
       THEN SET 0001 + EMIT tributary  AS tributary-form

# Valley widening - old rivers create wider valleys
RULE   IF tick_in=31..50 AND var_channel>=3 AND nb_any=GATE
       THEN SET 0001  AS valley-widen

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: DELTA FORMATION (ticks 51-70)
# Rivers reach ocean and form deltas
# ═══════════════════════════════════════════════════════════════════════════════

# Delta forms at ocean boundary (depth 0)
RULE   IF tick_in=51..70 AND var_flow>=4 AND depth=0
       THEN SET 0111 + EMIT delta  AS delta-form

# Sediment deposition in delta
RULE   IF tick_in=51..70 AND var_flow>=3 AND depth=0 AND nb_any=GATE
       THEN SET 0110  AS sediment-deposit

# Distributary channels in delta (river splits)
RULE   IF tick_in=51..70 AND var_flow>=5 AND depth=0 AND random<0.2
       THEN SET 0011 + ROTATE_CW  AS distributary

# ═══════════════════════════════════════════════════════════════════════════════
# WATERSHED BOUNDARIES
# Ridge lines that separate drainage basins
# ═══════════════════════════════════════════════════════════════════════════════

# Watershed ridges (high elevation, no flow)
RULE   IF depth>=4 AND var_flow=0 AND tick>=20
       THEN SET 1000  AS watershed-ridge

# Drainage basin markers (different basins get different flow patterns)
RULE   IF var_flow>=2 AND tick>=30 AND random<0.25
       THEN SET_VAR basin_id 1  AS mark-basin

# ═══════════════════════════════════════════════════════════════════════════════
# RIVER FEATURES
# ═══════════════════════════════════════════════════════════════════════════════

# Waterfalls at elevation drops
RULE   IF tick>=30 AND var_flow>=3 AND depth>=3 AND nb_N=GATE
       THEN SET 1100 + EMIT waterfall  AS waterfall

# Rapids in steep sections
RULE   IF tick>=30 AND var_flow>=2 AND depth_in=3..4
       THEN SET 0111  AS rapids

# Oxbow lakes (abandoned river meanders)
RULE   IF tick>=50 AND var_channel>=2 AND random<0.05 AND nb_count=GATE:2
       THEN SET 0011  AS oxbow-lake

# ═══════════════════════════════════════════════════════════════════════════════
# FLOW DIRECTION ENCODING
# Use loop families to indicate flow direction for visualization
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF var_flow>=1 AND tick%4=0  THEN SET 1000  AS flow-north
RULE   IF var_flow>=1 AND tick%4=1  THEN SET 0100  AS flow-east
RULE   IF var_flow>=1 AND tick%4=2  THEN SET 0010  AS flow-south
RULE   IF var_flow>=1 AND tick%4=3  THEN SET 0001  AS flow-west

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNALS FOR GAME INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF tick=10  THEN EMIT phase_rainfall_complete  AS signal-phase1
RULE   IF tick=30  THEN EMIT phase_accumulation_complete AS signal-phase2
RULE   IF tick=50  THEN EMIT phase_carving_complete   AS signal-phase3
RULE   IF tick=70  THEN EMIT phase_delta_complete     AS signal-phase4
RULE   IF tick=70  THEN EMIT rivers_ready             AS signal-ready

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT: Continue river simulation
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE
