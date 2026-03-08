# attack_swing.geo — Melee Attack Animation with Windup and Follow-Through
# =========================================================================
# Demonstrates: Precise timing, multi-phase animation, transform actions
#
# Usage: python Playground.py --geo examples/animation/attack_swing.geo
#
# Creates a 30-frame attack animation with distinct phases:
#   Phase 1 (0-8):   Windup - Telegraph the attack
#   Phase 2 (9-14):  Strike - Fast forward motion
#   Phase 3 (15-20): Impact - Hit frame with shake
#   Phase 4 (21-29): Recovery - Return to neutral
#
# Uses ROTATE, FLIP, and SET actions for dynamic weapon motion.

NAME   attack_swing

# === WEAPON BLADE (depth 0) - Main attack motion ===

# Windup: Pull back (ticks 0-8)
RULE   IF tick%30_in=0..2   AND depth=0  THEN SET 0100  AS windup-start
RULE   IF tick%30_in=3..5   AND depth=0  THEN ROTATE_CW          AS windup-cock
RULE   IF tick%30_in=6..8   AND depth=0  THEN ROTATE_CW          AS windup-hold

# Strike: Fast swing forward (ticks 9-14)
RULE   IF tick%30=9         AND depth=0  THEN ROTATE_CW + ROTATE_CW  AS strike-init
RULE   IF tick%30_in=10..12 AND depth=0  THEN ROTATE_CW          AS strike-mid
RULE   IF tick%30_in=13..14 AND depth=0  THEN SET 1000          AS strike-contact

# Impact: Hit frame with effect (ticks 15-20)
RULE   IF tick%30_in=15..17 AND depth=0  THEN GATE_ON           AS impact-flash
RULE   IF tick%30_in=18..20 AND depth=0  THEN FLIP_H            AS impact-shake

# Recovery: Return to guard (ticks 21-29)
RULE   IF tick%30_in=21..23 AND depth=0  THEN ROTATE_CCW        AS recover-start
RULE   IF tick%30_in=24..26 AND depth=0  THEN ROTATE_CCW        AS recover-mid
RULE   IF tick%30_in=27..29 AND depth=0  THEN SET 1100          AS recover-guard

# === WEAPON HANDLE (depth 1) - Gripped position ===
RULE   IF tick%30_in=0..8   AND depth=1  THEN SET 1100  AS grip-windup
RULE   IF tick%30_in=9..14  AND depth=1  THEN SET 1000  AS grip-strike
RULE   IF tick%30_in=15..20 AND depth=1  THEN SET 1111  AS grip-impact
RULE   IF tick%30_in=21..29 AND depth=1  THEN SET 1100  AS grip-recover

# === ARM UPPER (depth 2) - Shoulder rotation ===
RULE   IF tick%30_in=0..8   AND depth=2  THEN ROTATE_CCW        AS arm-cock
RULE   IF tick%30_in=9..14  AND depth=2  THEN ROTATE_CW + ROTATE_CW  AS arm-swing
RULE   IF tick%30_in=15..20 AND depth=2  THEN HOLD             AS arm-impact
RULE   IF tick%30_in=21..29 AND depth=2  THEN ROTATE_CCW        AS arm-recover

# === ARM LOWER (depth 3) - Elbow extension ===
RULE   IF tick%30_in=0..5   AND depth=3  THEN SET 0010  AS elbow-bent
RULE   IF tick%30_in=6..14  AND depth=3  THEN SET 0001  AS elbow-extend
RULE   IF tick%30_in=15..20 AND depth=3  THEN SET 0001  AS elbow-lock
RULE   IF tick%30_in=21..29 AND depth=3  THEN SET 0010  AS elbow-relax

# === BODY LEAN (depth 4+) - Weight transfer ===
RULE   IF tick%30_in=0..8   AND depth>=4  THEN SET 0100  AS body-back
RULE   IF tick%30_in=9..17  AND depth>=4  THEN SET 1000  AS body-forward
RULE   IF tick%30_in=18..29 AND depth>=4  THEN SET 0100  AS body-return

# === ATTACK SIGNAL (for hit detection) ===
# Emit "hit" signal on contact frame for game integration
RULE   IF tick%30=14 AND depth=0  THEN EMIT attack_hit  AS hit-frame

# === DEFAULT: Continue animation loop ===
DEFAULT ADVANCE
