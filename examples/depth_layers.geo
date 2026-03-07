# depth_layers.geo
# Demonstrates range conditions and multi-action composites.
# Shallow layers (0-2) rotate, mid layers (3-4) mirror, deep layers (5+) gate.
NAME   depth_layers
RULE   IF depth_in=0..2 AND family=Y_LOOP  THEN ROTATE_CW + ADVANCE     AS shallow-spin
RULE   IF depth_in=3..4 AND family=Y_LOOP  THEN FLIP_V                  AS mid-flip
RULE   IF depth>=5                         THEN GATE_ON                  AS deep-seal
RULE   IF tick%12=0                        THEN SWITCH Y_LOOP            AS reset
DEFAULT ADVANCE
