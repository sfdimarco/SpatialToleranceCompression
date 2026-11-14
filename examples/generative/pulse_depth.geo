# pulse_depth.geo
# Pulses gate-on every 10 ticks; deep cells lock to Z-loop (blue).
NAME   pulse_depth
RULE   IF tick%10=0 BUT family=GATE    THEN GATE_ON       AS flash
RULE   IF family=GATE AND tick%10=3    THEN SWITCH Y_LOOP  AS unflash
RULE   IF depth>=3  AND family=Y_LOOP  THEN SWITCH Z_LOOP  AS deep-z
DEFAULT ADVANCE
