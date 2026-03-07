# mask_set.geo
# Demonstrates mask_in condition and multi-step ADVANCE.
# Only specific mask values trigger special behavior.
NAME   mask_set
RULE   IF mask_in=1000,0100  THEN ADVANCE 2              AS skip-ahead
RULE   IF mask_in=0010,0001  THEN ROTATE_CCW              AS twist-back
RULE   IF mask=1111          THEN SWITCH Y_LOOP            AS break-gate
DEFAULT ADVANCE
