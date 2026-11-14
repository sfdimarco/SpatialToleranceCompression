# signal_wave.geo
# Signal-based communication between grid cells.
# Y-loop cells emit a "pulse" signal. Cells receiving the signal switch to X-loop.
# X-loop cells emit "ripple". Cells receiving ripple switch to DIAG.
NAME   signal_wave

# Emitters: Y-loop cells emit pulse signal
RULE IF family=Y_LOOP THEN ADVANCE + EMIT pulse AS send

# Reactors: Z-loop cells receiving pulse switch to X-loop
RULE IF signal=pulse AND family=Z_LOOP THEN SWITCH X_LOOP AS react

# Echo: X-loop cells emit ripple signal
RULE IF family=X_LOOP THEN ADVANCE + EMIT ripple AS echo

# Ring: Z-loop cells receiving ripple switch to DIAG
RULE IF signal=ripple AND family=Z_LOOP THEN SWITCH DIAG_LOOP AS ring

# Z-loop cells that didn't receive a signal just hold
RULE IF family=Z_LOOP THEN HOLD AS wait

# DIAG cells hold
RULE IF family=DIAG_LOOP THEN HOLD AS held

# Default
DEFAULT HOLD
