# vote_example.geo
# Demonstrates program-identity conditions and PROG / PLURALITY actions.
# Designed for use on a Grid where vote-0..3 programs are registered.
#
# Rule 1: if 2+ neighbors run vote-1 AND we are currently vote-0, adopt vote-1.
# Rule 2: PLURALITY 2 fallback — adopt any program held by 2+ neighbours.
# Both rules also advance the mask each tick (PROG and PLURALITY do next_mask).
NAME   vote_example
RULE   IF nb_prog_any=vote-1 AND own_prog=vote-0  THEN PROG vote-1  AS adopt-1
RULE   IF nb_prog_any=vote-0 AND own_prog=vote-1  THEN PROG vote-0  AS adopt-0
DEFAULT PLURALITY 2
