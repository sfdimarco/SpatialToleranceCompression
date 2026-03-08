# jump_arc.geo — Jump Animation with Arc Trajectory
# ==================================================
# Demonstrates: Parabolic motion simulation, squash/stretch, timing
#
# Usage: python Playground.py --geo examples/animation/jump_arc.geo
#
# Creates a 24-frame jump animation:
#   Phase 1 (0-5):   Crouch and prepare
#   Phase 2 (6-8):   Jump launch (squash)
#   Phase 3 (9-14):  Airborne arc (stretch)
#   Phase 4 (15-17): Peak hang time
#   Phase 5 (18-21): Descent and anticipation
#   Phase 6 (22-23): Landing (squash then recover)

NAME   jump_arc

# === BODY CORE (depth 0) - Main jump trajectory ===

# Crouch preparation (ticks 0-5)
RULE   IF tick%24_in=0..2   AND depth=0  THEN SET 0011  AS crouch-down
RULE   IF tick%24_in=3..5   AND depth=0  THEN SET 0011  AS crouch-hold

# Launch - explosive jump (ticks 6-8)
RULE   IF tick%24=6         AND depth=0  THEN SET 1100  AS launch-squash
RULE   IF tick%24_in=7..8   AND depth=0  THEN SET 1111  AS launch-stretch

# Ascent arc (ticks 9-14)
RULE   IF tick%24_in=9..11  AND depth=0  THEN SET 1000  AS rise-high
RULE   IF tick%24_in=12..14 AND depth=0  THEN SET 1100  AS rise-mid

# Peak hang time (ticks 15-17)
RULE   IF tick%24_in=15..17 AND depth=0  THEN SET 1010  AS peak-float

# Descent (ticks 18-21)
RULE   IF tick%24_in=18..19 AND depth=0  THEN SET 1100  AS fall-mid
RULE   IF tick%24_in=20..21 AND depth=0  THEN SET 0011  AS fall-low

# Landing (ticks 22-23)
RULE   IF tick%24=22        AND depth=0  THEN SET 0011  AS land-squash
RULE   IF tick%24=23        AND depth=0  THEN SET 1111  AS land-recover

# === LEGS (depth 1-2) - Jump mechanics ===

# Crouch and launch
RULE   IF tick%24_in=0..5   AND depth_in=1..2  THEN SET 0011  AS legs-crouch
RULE   IF tick%24_in=6..8   AND depth_in=1..2  THEN SET 0001  AS legs-push

# Airborne tuck
RULE   IF tick%24_in=9..17  AND depth_in=1..2  THEN SET 0010  AS legs-tuck

# Landing preparation
RULE   IF tick%24_in=18..21 AND depth_in=1..2  THEN SET 0001  AS legs-extend
RULE   IF tick%24_in=22..23 AND depth_in=1..2  THEN SET 0011  AS legs-absorb

# === ARMS (depth 3) - Balance and momentum ===

# Windup back (ticks 0-5)
RULE   IF tick%24_in=0..5   AND depth=3  THEN SET 0100  AS arms-back

# Swing up for momentum (ticks 6-14)
RULE   IF tick%24_in=6..10  AND depth=3  THEN ROTATE_CW        AS arms-swing-up
RULE   IF tick%24_in=11..14 AND depth=3  THEN SET 1000  AS arms-high

# Float and prepare landing (ticks 15-21)
RULE   IF tick%24_in=15..18 AND depth=3  THEN SET 1000  AS arms-float
RULE   IF tick%24_in=19..21 AND depth=3  THEN ROTATE_CCW        AS arms-prepare

# Landing swing (ticks 22-23)
RULE   IF tick%24_in=22..23 AND depth=3  THEN SET 0100  AS arms-down

# === HEAD (depth 4) - Look direction ===
RULE   IF tick%24_in=0..5   AND depth=4  THEN SET 0010  AS head-look-down
RULE   IF tick%24_in=6..17  AND depth=4  THEN SET 1000  AS head-look-up
RULE   IF tick%24_in=18..23 AND depth=4  THEN SET 0010  AS head-look-landing

# === JUMP SIGNAL (for game integration) ===
RULE   IF tick%24=6   THEN EMIT jump_start    AS signal-launch
RULE   IF tick%24=15  THEN EMIT jump_peak     AS signal-apex
RULE   IF tick%24=22  THEN EMIT jump_land     AS signal-impact

# === DEFAULT: Continue animation ===
DEFAULT ADVANCE
