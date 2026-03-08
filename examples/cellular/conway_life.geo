# conway_life.geo - Conway's Game of Life
# ========================================
# Classic cellular automaton with Birth/Survival rules.
# Uses 8-neighbor (Moore neighborhood) counting.
#
# Cell States:
#   ALIVE  (1111)  : Living cell
#   DEAD   (0000)  : Empty cell
#
# Rules:
#   - Any live cell with 2-3 live neighbors survives
#   - Any dead cell with exactly 3 live neighbors becomes alive
#   - All other cells die or stay dead
#
# Initial pattern: Random 35% density

NAME   conway_life

# === ALIASES ===
DEFINE alive    mask=1111
DEFINE dead     mask=0000

# === CONWAY'S RULES ===
# Use nb_mask_count8=1111:N to count ALIVE neighbors (8-directional)

# Survival: Live cell with exactly 2 or 3 ALIVE neighbors stays alive
RULE IF alive AND nb_mask_count8=1111:2 THEN HOLD AS survive_2
RULE IF alive AND nb_mask_count8=1111:3 THEN HOLD AS survive_3

# Death: Live cell with 0, 1, or 4+ ALIVE neighbors dies
RULE IF alive AND nb_mask_count8=1111:0 THEN GATE_OFF AS die_0
RULE IF alive AND nb_mask_count8=1111:1 THEN GATE_OFF AS die_1
RULE IF alive THEN GATE_OFF AS die_many  # 4+ neighbors

# Birth: Dead cell with exactly 3 ALIVE neighbors comes alive
RULE IF dead AND nb_mask_count8=1111:3 THEN GATE_ON AS birth

# Stay dead (default for dead cells that don't meet birth condition)
RULE IF dead THEN HOLD AS stay_dead

# === DEFAULT ===
DEFAULT HOLD
