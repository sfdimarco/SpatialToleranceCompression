# rotate_mirror.geo
# Demonstrates ROTATE_CW, FLIP_H, and parenthesised conditions.
# Rotates geometry clockwise for the first 16 ticks, then mirrors it.
# Uses DEFINE to create a reusable alias.
NAME   rotate_mirror
DEFINE is_single   (family=Y_LOOP OR family=DIAG_LOOP)
RULE   IF is_single AND tick<16   THEN ROTATE_CW           AS spin
RULE   IF is_single AND tick>=16  THEN FLIP_H              AS mirror
RULE   IF tick%20=0               THEN SWITCH Y_LOOP        AS reset
DEFAULT ADVANCE
