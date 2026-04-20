# heat_spread.geo
# Cell variables demo: cells accumulate "heat" and change family at thresholds.
# Each tick in Y-loop increments heat. When heat >= 5, switch to X-loop and reset.
# When heat >= 10 in X-loop, switch to Z-loop.
NAME   heat_spread

# Y-loop cells warm up (accumulate heat)
RULE IF family=Y_LOOP THEN ADVANCE + INCR_VAR heat 1 AS warm

# Y-loop cells that are hot enough ignite (switch to X-loop)
RULE IF var_heat>=5 AND family=Y_LOOP THEN SWITCH X_LOOP + SET_VAR heat 0 AS ignite

# X-loop cells burn hotter (accumulate heat faster)
RULE IF family=X_LOOP THEN ADVANCE + INCR_VAR heat 2 AS burn

# X-loop cells that are very hot cool down (switch to Z-loop)
RULE IF var_heat>=10 THEN SWITCH Z_LOOP + SET_VAR heat 0 AS cool

# Z-loop cells stay cool (hold state)
RULE IF family=Z_LOOP THEN HOLD AS cooled

# Default
DEFAULT HOLD
