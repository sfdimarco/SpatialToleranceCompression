# heat_spread.geo
# Cell variables demo: cells accumulate "heat" and change family at thresholds.
# Each tick in Y-loop increments heat. When heat >= 5, switch to X-loop and reset.
# When heat >= 10 in X-loop, switch to Z-loop.
NAME   heat_spread
RULE   IF family=Y_LOOP  THEN ADVANCE + INCR_VAR heat 1         AS warm
RULE   IF var_heat>=5 AND family=Y_LOOP  THEN SWITCH X_LOOP + SET_VAR heat 0  AS ignite
RULE   IF family=X_LOOP  THEN ADVANCE + INCR_VAR heat 2         AS burn
RULE   IF var_heat>=10   THEN SWITCH Z_LOOP + SET_VAR heat 0    AS cool
DEFAULT ADVANCE
