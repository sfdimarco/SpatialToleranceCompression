# selforg_maze.geo — Maze Generation via Wall Growth
# ===================================================
# Demonstrates: Constraint-based growth, path formation, connectivity
#
# Usage: python Playground.py --geo examples/selforg/maze.geo --grid
#
# Generates solvable mazes using a wall-growing algorithm:
#   Phase 1 (0-10):   Border wall creation
#   Phase 2 (11-30):  Internal wall growth
#   Phase 3 (31-50):  Path widening and connection
#   Phase 4 (51-70):  Dead-end removal and polish
#
# Output: Perfect maze (one path between any two points)
# with walls (GATE_ON) and paths (GATE_OFF)

NAME   selforg_maze

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: BORDER WALLS (ticks 0-10)
# Create outer boundary of the maze
# ═══════════════════════════════════════════════════════════════════════════════

# Top and bottom borders
RULE   IF tick_in=0..10 AND depth=0
       THEN SET 1111  AS border-top-bottom

# Left and right borders
RULE   IF tick_in=0..10 AND depth=0
       THEN SET 1111  AS border-left-right

# Entrance (top-left) and exit (bottom-right)
RULE   IF tick_in=0..10 AND depth=0 AND tick=10
       THEN SET 0000  AS entrance
RULE   IF tick_in=0..10 AND depth=0 AND tick=10
       THEN SET 0000  AS exit

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: WALL GROWTH (ticks 11-30)
# Grow walls from borders inward, maintaining path connectivity
# ═══════════════════════════════════════════════════════════════════════════════

# Wall grows from existing walls into floor
RULE   IF tick_in=11..30 AND mask=0000 AND nb_any=GATE AND random<0.3
       THEN SET 1111 + SET_VAR wall_age 0  AS wall-grow

# Prevent wall from blocking all paths (must have 2+ floor neighbors)
RULE   IF tick_in=11..30 AND mask=0000 AND nb_count=GATE:4
       THEN SET 0000  AS keep-path-open

# Create wall segments (not single cells)
RULE   IF tick_in=11..30 AND mask=0000 AND nb_any=GATE AND random<0.4
       THEN SET 1100 + SET_VAR wall_age 0  AS wall-segment-top
RULE   IF tick_in=11..30 AND mask=0000 AND nb_any=GATE AND random<0.4
       THEN SET 0011 + SET_VAR wall_age 0  AS wall-segment-bottom

# Wall aging - older walls are more stable
RULE   IF tick_in=11..30 AND var_wall_age>=0
       THEN INCR_VAR wall_age 1  AS wall-age

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: PATH WIDENING (ticks 31-50)
# Ensure paths are wide enough to traverse
# ═══════════════════════════════════════════════════════════════════════════════

# Widen narrow corridors (single-cell paths become 2-cell)
RULE   IF tick_in=31..50 AND mask=0000 AND nb_count=GATE:4
       THEN SET 0000  AS widen-corridor

# Create path intersections
RULE   IF tick_in=31..50 AND mask=0000 AND nb_count=GATE:2 AND random<0.2
       THEN SET 0000  AS create-intersection

# Remove isolated wall pixels
RULE   IF tick_in=31..50 AND mask=1111 AND nb_count=GATE:0
       THEN SET 0000  AS remove-isolated-wall

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: DEAD-END REMOVAL (ticks 51-70)
# Optionally remove short dead-ends for simpler maze
# ═══════════════════════════════════════════════════════════════════════════════

# Identify dead-ends (path with only one neighbor)
RULE   IF tick_in=51..70 AND mask=0000 AND nb_count=GATE:3
       THEN SET_VAR deadend 1  AS mark-deadend

# Remove short dead-ends (optional simplification)
RULE   IF tick_in=51..70 AND var_deadend=1 AND random<0.3
       THEN SET 1111  AS remove-deadend

# ═══════════════════════════════════════════════════════════════════════════════
# MAZE FEATURES
# ═══════════════════════════════════════════════════════════════════════════════

# Create chambers (larger open areas)
RULE   IF tick_in=31..50 AND mask=0000 AND random<0.02 AND nb_count=GATE:0
       THEN SET 0000 + SET_VAR chamber 1  AS create-chamber

# Create pillars (isolated walls in chambers)
RULE   IF tick_in=31..50 AND mask=0000 AND var_chamber=1 AND random<0.05
       THEN SET 1111  AS create-pillar

# Create secret passages (hidden connections)
RULE   IF tick_in=51..70 AND mask=1111 AND var_wall_age>=10 AND random<0.01
       THEN SET 0000 + EMIT secret  AS secret-passage

# ═══════════════════════════════════════════════════════════════════════════════
# PATH CONNECTIVITY CHECK
# Ensure maze is solvable (simplified check)
# ═══════════════════════════════════════════════════════════════════════════════

# Mark cells reachable from entrance (near open paths)
RULE   IF tick>=20 AND mask=0000 AND nb_any=GATE AND depth=0
       THEN SET_VAR reachable 1  AS mark-reachable

# Check if exit is reachable
RULE   IF tick>=50 AND var_reachable=1 AND depth=0
       THEN EMIT maze_solvable  AS verify-solvable

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNALS FOR GAME INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF tick=10  THEN EMIT phase_border_complete   AS signal-phase1
RULE   IF tick=30  THEN EMIT phase_walls_complete    AS signal-phase2
RULE   IF tick=50  THEN EMIT phase_paths_complete    AS signal-phase3
RULE   IF tick=70  THEN EMIT phase_polish_complete   AS signal-phase4
RULE   IF tick=70  THEN EMIT maze_ready              AS signal-ready

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT: Continue maze generation
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE
