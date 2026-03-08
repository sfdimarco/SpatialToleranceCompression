# idle_breathe.geo — Character Idle Breathing Animation
# ======================================================
# Demonstrates: Cell variables, conditional gating, subtle motion
#
# Usage: python Playground.py --geo examples/animation/idle_breathe.geo
#
# Creates a natural breathing cycle for character idle animation:
# - Inhale (ticks 0-5): Chest expands, slight upward motion
# - Hold (ticks 6-7): Brief pause at full breath
# - Exhale (ticks 8-14): Chest contracts, relax downward
# - Pause (ticks 15-17): Brief pause before next breath
#
# Uses cell variables to track breath phase and intensity.

NAME   idle_breathe

# === BREATH CYCLE TIMING (18-tick cycle at 30fps = ~0.6 seconds) ===

# Inhale phase (ticks 0-5)
RULE   IF tick%18_in=0..5 AND depth_in=0..1  THEN INCR_VAR breath 1 AS inhale-chest
RULE   IF tick%18=5 AND depth_in=0..1        THEN GATE_ON          AS full-inhale

# Hold at top (ticks 6-7)
RULE   IF tick%18_in=6..7 AND depth_in=0..1  THEN HOLD             AS breath-hold

# Exhale phase (ticks 8-14)
RULE   IF tick%18_in=8..14 AND depth_in=0..1 THEN INCR_VAR breath -1 AS exhale-chest
RULE   IF tick%18=14 AND depth_in=0..1       THEN GATE_OFF         AS full-exhale

# Pause at bottom (ticks 15-17)
RULE   IF tick%18_in=15..17 AND depth_in=0..1 THEN HOLD            AS breath-pause

# === BELLY MOVEMENT (depth 2-4) - Subtle secondary motion ===
RULE   IF tick%18_in=0..7 AND depth_in=2..4  THEN SET 1100  AS belly-expand
RULE   IF tick%18_in=8..17 AND depth_in=2..4 THEN SET 0011  AS belly-contract

# === SHOULDER ROLL (depth 1) - Relaxed idle movement ===
RULE   IF tick%36_in=0..8   AND depth=1  THEN ROTATE_CW        AS shoulder-up
RULE   IF tick%36_in=9..17  AND depth=1  THEN ROTATE_CW        AS shoulder-back
RULE   IF tick%36_in=18..26 AND depth=1  THEN ROTATE_CW        AS shoulder-down
RULE   IF tick%36_in=27..35 AND depth=1  THEN ROTATE_CW        AS shoulder-relax

# === HEAD BOBBING (depth 0, center) - Subtle life ===
RULE   IF tick%18_in=0..5   AND depth=0  THEN SET 1000  AS head-up
RULE   IF tick%18_in=6..14  AND depth=0  THEN SET 0100  AS head-down
RULE   IF tick%18_in=15..17 AND depth=0  THEN SET 1000  AS head-neutral

# === EYES BLINK (random, depth 0) - Natural blinking ===
RULE   IF depth=0 AND tick%120=0  THEN SET 0000  AS blink-close
RULE   IF depth=0 AND tick%120=1  THEN SET 1111  AS blink-open

# === DEFAULT: Subtle idle sway ===
DEFAULT ADVANCE
