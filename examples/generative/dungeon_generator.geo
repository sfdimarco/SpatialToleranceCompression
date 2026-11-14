# dungeon_generator.geo - Procedural Level Generator
# ===================================================
# Generates dungeon-like structures with rooms and corridors.
# Useful for roguelike games, maze generation, and level design.
#
# Cell States:
#   WALL      (GATE_ON - 1111)   : Solid walls (white)
#   FLOOR     (X_LOOP - green)   : Walkable floor (green)
#   DOOR      (Y_LOOP - red)     : Doorways between rooms (red)
#   CORRIDOR  (Z_LOOP - blue)    : Hallways connecting rooms (blue)
#   EMPTY     (GATE_OFF - dark)  : Unexplored/void (dark)
#
# Cell Variables:
#   room_id     - Which room this cell belongs to
#   phase       - Generation phase counter

NAME   dungeon_generator

# === ALIASES ===
DEFINE is_void      mask=0000
DEFINE is_wall      mask=1111
DEFINE is_floor     family=X_LOOP
DEFINE is_door      family=Y_LOOP
DEFINE is_corridor  family=Z_LOOP

# === PHASE 1: INITIAL NOISE (ticks 0-10) ===
# Create random noise pattern - 45% walls, 55% floor

RULE IF tick<5 AND is_void AND random<0.45 THEN GATE_ON AS seed_wall
RULE IF tick<5 AND is_void THEN SWITCH X_LOOP AS seed_floor

# Hold phase 1
RULE IF tick_in=5..10 THEN HOLD AS phase1_hold

# === PHASE 2: CELLULAR AUTOMATON SMOOTHING (ticks 11-25) ===
# Apply cellular automata rules to create cave-like structures

# Wall with 5+ wall neighbors stays wall
RULE IF tick_in=11..25 AND is_wall AND nb_count_gte=GATE:5 THEN HOLD AS wall_stay

# Floor with 5+ wall neighbors becomes wall (cave closing)
RULE IF tick_in=11..25 AND is_floor AND nb_count_gte=GATE:5 THEN GATE_ON AS floor_to_wall

# Wall with 4+ floor neighbors becomes floor (cave opening)
RULE IF tick_in=11..25 AND is_wall AND nb_count_gte=X_LOOP:4 THEN SWITCH X_LOOP AS wall_to_floor

# Continue smoothing
RULE IF tick_in=11..25 THEN ADVANCE AS smooth_continue

# === PHASE 3: ROOM EXPANSION (ticks 26-40) ===
# Expand floor areas into rooms

# Floor with 2+ floor neighbors expands
RULE IF tick_in=26..40 AND is_floor AND nb_count_gte=X_LOOP:2 THEN SWITCH X_LOOP AS room_expand

# Isolated walls inside floor areas become floor
RULE IF tick_in=26..40 AND is_wall AND nb_count_gte=X_LOOP:3 THEN SWITCH X_LOOP AS remove_internal_wall

# Continue phase 3
RULE IF tick_in=26..40 THEN ADVANCE AS phase3_continue

# === PHASE 4: CORRIDOR CARVING (ticks 41-55) ===
# Create corridors between room clusters

# Floor on edge (has wall neighbor) starts corridor
RULE IF tick_in=41..55 AND is_floor AND nb_any=GATE THEN SWITCH Z_LOOP AS corridor_start

# Corridor extends
RULE IF tick_in=41..55 AND is_corridor THEN ADVANCE AS corridor_extend

# Continue phase 4
RULE IF tick_in=41..55 THEN HOLD AS phase4_hold

# === PHASE 5: DOOR PLACEMENT (ticks 56-70) ===
# Place doors at transitions

# Floor next to corridor becomes door
RULE IF tick_in=56..70 AND is_floor AND nb_any=Z_LOOP THEN SWITCH Y_LOOP AS door_place

# Continue phase 5
RULE IF tick_in=56..70 THEN HOLD AS phase5_hold

# === PHASE 6: FINAL POLISH (ticks 71+) ===
# Clean up and stabilize

# Remove isolated single walls (pillars)
RULE IF tick>=71 AND is_wall AND nb_count_gte=X_LOOP:4 THEN SWITCH X_LOOP AS remove_pillar

# Fill isolated single floor holes
RULE IF tick>=71 AND is_floor AND nb_count_gte=GATE:4 THEN GATE_ON AS fill_hole

# Final hold
RULE IF tick>=71 THEN HOLD AS final

# === DEFAULT ===
DEFAULT ADVANCE
