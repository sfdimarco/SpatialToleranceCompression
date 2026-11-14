# composite.geo
# Composite actions: do multiple things in one rule.
# Demonstrates chaining SWITCH + EMIT + SET_VAR in a single THEN clause.
NAME   composite
RULE   IF tick%8=0    THEN SWITCH Y_LOOP + EMIT beat + SET_VAR phase 0    AS beat-start
RULE   IF tick%8=4    THEN SWITCH X_LOOP + EMIT beat + SET_VAR phase 1    AS beat-mid
RULE   IF signal=beat AND family=Z_LOOP  THEN FLIP_H + INCR_VAR react 1  AS respond
DEFAULT ADVANCE
