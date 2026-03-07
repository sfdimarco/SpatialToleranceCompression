# signal_wave.geo
# Signal-based communication between grid cells.
# Y-loop cells emit a "pulse" signal. Cells receiving the signal switch to X-loop.
# X-loop cells emit "ripple". Cells receiving ripple switch to DIAG.
NAME   signal_wave
RULE   IF family=Y_LOOP                 THEN ADVANCE + EMIT pulse     AS send
RULE   IF signal=pulse AND family=Z_LOOP THEN SWITCH X_LOOP            AS react
RULE   IF family=X_LOOP                 THEN ADVANCE + EMIT ripple    AS echo
RULE   IF signal=ripple AND family=Z_LOOP THEN SWITCH DIAG_LOOP        AS ring
DEFAULT ADVANCE
