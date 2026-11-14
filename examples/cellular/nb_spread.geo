# nb_spread.geo
# Cells that see a Y-loop neighbor switch to X-loop (usable on a Grid).
NAME   nb_spread
RULE   IF nb_any=Y_LOOP AND family=Z_LOOP  THEN SWITCH X_LOOP  AS spread
RULE   IF nb_any=X_LOOP AND family=Z_LOOP  THEN SWITCH DIAG_LOOP AS ring
DEFAULT ADVANCE
