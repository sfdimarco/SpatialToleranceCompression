# stochastic.geo
# Probabilistic rules for organic, non-deterministic evolution.
# 30% chance to gate-on each tick (unless already gated).
# Deep cells randomly flip to different families.
NAME   stochastic
RULE   IF random<0.3 BUT family=GATE            THEN GATE_ON             AS flash
RULE   IF family=GATE AND random<0.5             THEN SWITCH Y_LOOP       AS ungate
RULE   IF depth>=4 AND random<0.2                THEN SWITCH Z_LOOP       AS deep-z
RULE   IF depth>=4 AND random<0.1                THEN SWITCH DIAG_LOOP    AS deep-d
DEFAULT ADVANCE
