# cosmos_sim.geo
# Charged-gravity inspired cosmic simulator in .geo
# Uses rotating patterns, stochastic flares, and depth layers
# to evoke orbital motion and fusion events

NAME   cosmos_sim

# --- Reusable condition aliases ---
DEFINE is_core         depth_in=0..2
DEFINE is_mid          depth_in=3..5
DEFINE is_deep         depth>=6
DEFINE is_active       family=Y_LOOP
DEFINE is_charged      family=X_LOOP
DEFINE is_void         mask=0000
DEFINE is_radiating    family=Z_LOOP
DEFINE is_diag         family=DIAG_LOOP

# --- Core behavior: slow rotation (like massive bodies) ---
RULE IF is_core AND is_active          THEN ROTATE_CW + ADVANCE 1    AS core-spin
RULE IF is_core AND is_void            THEN SWITCH Y_LOOP            AS core-ignite

# --- Mid layer: orbital cycling with periodic boosts ---
RULE IF is_mid AND tick%12=0           THEN SWITCH X_LOOP            AS orbit-boost
RULE IF is_mid AND is_charged          THEN ADVANCE 2                AS orbit-fast
RULE IF is_mid AND is_radiating        THEN FLIP_H + FLIP_V          AS orbit-flip

# --- Deep layer: stochastic flares (fusion events) ---
RULE IF is_deep AND random<0.15        THEN SET 1111                 AS flare-up
RULE IF is_deep AND is_void AND random<0.25  THEN SWITCH Z_LOOP      AS flare-ignite
RULE IF is_deep AND is_radiating       THEN ADVANCE                  AS flare-decay

# --- Periodic reset to maintain cosmic cycle ---
RULE IF tick%200=0 AND is_core         THEN SWITCH DIAG_LOOP         AS cosmic-reset
RULE IF tick%50=0 AND is_mid           THEN SWITCH Y_LOOP            AS orbit-reset

# --- Void handling: spontaneous generation (emitter) ---
RULE IF is_void AND tick%8=0           THEN SWITCH Y_LOOP            AS emit-particle
RULE IF is_void AND random<0.05        THEN SWITCH X_LOOP            AS random-spawn

# --- Radiating decay back to void (energy dissipation) ---
RULE IF is_radiating AND tick%6=0      THEN SET 0000                 AS energy-decay

# --- Diagonal loop behavior ---
RULE IF is_diag AND tick%4=0           THEN SWITCH Y_LOOP            AS diag-reset

# --- Default: gentle advancement ---
DEFAULT ADVANCE
