# forest_fire.geo
# A recursive forest fire simulation using cell variables and signals.
#
# - Trees are represented by the X_LOOP family (green).
# - Fire is represented by the Y_LOOP family (red).
# - Burnt-out areas are GATE_OFF (empty).
#
# The fire spreads when a 'tree' node receives a 'fire' signal from a
# 'burning' neighbor. This works recursively through the quadtree.

NAME   forest_fire

# --- Aliases for clarity ---
DEFINE is_tree      family=X_LOOP
DEFINE is_burning   family=Y_LOOP
DEFINE is_clearing  mask=0000

# --- Simulation Rules ---

# 1. On the first tick, turn all empty clearings into trees (X_LOOP).
#    Any cells that start as Y_LOOP (from the --mask argument) are the fire starters.
RULE IF tick<2 AND is_clearing THEN SWITCH X_LOOP AS plant_trees

# 2. A tree that receives a 'fire' signal from a neighbor ignites.
RULE IF is_tree AND signal=fire THEN SWITCH Y_LOOP + SET_VAR burn_time 0 AS catch_fire

# 3. After burning for 4 ticks, the tree burns out completely.
RULE IF is_burning AND var_burn_time>=4 THEN GATE_OFF AS burn_out

# 4. A burning tree emits 'fire' to its neighbors and increments its burn timer.
RULE IF is_burning THEN ADVANCE + EMIT fire + INCR_VAR burn_time 1 AS spread_fire

# 5. Trees that haven't caught fire just stay as trees (hold their state)
RULE IF is_tree THEN HOLD AS stay_tree

# --- Default Behavior ---
# Burnt-out areas stay empty
DEFAULT HOLD