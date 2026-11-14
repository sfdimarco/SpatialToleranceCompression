# hello_world.geo - Introduction to Binary Quad-Tree Grammar
# ==========================================================
# A simple demonstration showing depth-based pattern switching.
#
# Cell States by Depth:
#   depth=0  : Y-loop (red)   - Single quadrant rotating
#   depth=1  : X-loop (green) - Adjacent pair cycling
#   deeper   : Advance normally
#
# This creates an alternating depth pattern showcasing the grammar engine.

NAME   hello_world

# === ALIASES ===
DEFINE down_pattern  family=Y_LOOP    # depth 0 - red, rotates down
DEFINE up_pattern    family=X_LOOP    # depth 1 - green, cycles up

# === DEPTH-BASED RULES ===

# Depth 0: Use Y-loop (single quadrant rotating)
RULE IF depth=0 THEN SWITCH Y_LOOP AS set_down

# Depth 1: Use X-loop (adjacent pair cycling)
RULE IF depth=1 THEN SWITCH X_LOOP AS set_up

# Default: Just advance normally
DEFAULT ADVANCE
