# ═══════════════════════════════════════════════════════════════════════════════
# TERRITORY CONQUEST - Core Mechanics
# ═══════════════════════════════════════════════════════════════════════════════
# This .geo script controls territorial conquest behavior in Cosmic Origins.
# Each territory node uses 4-bit masks to represent control:
#   - Bit 0 (1): Player faction control
#   - Bit 1 (2): Enemy faction control  
#   - Bit 2 (4): Neutral/Contested
#   - Bit 3 (8): Resource-rich territory
#
# Loop Families repurposed for territory:
#   Y_LOOP   = Player expansion phase
#   X_LOOP   = Enemy expansion phase
#   Z_LOOP   = Contested/battle zone
#   DIAG_LOOP = Resource generation
#   GATE     = Locked/Fortified territory
# ═══════════════════════════════════════════════════════════════════════════════

NAME   territory_conquest

# ───────────────────────────────────────────────────────────────────────────────
# DEFINE aliases for common conditions
# ───────────────────────────────────────────────────────────────────────────────

DEFINE player_territory    family=Y_LOOP
DEFINE enemy_territory     family=X_LOOP
DEFINE contested           family=Z_LOOP
DEFINE resource_zone       family=DIAG_LOOP
DEFINE fortified           family=GATE

DEFINE deep_space          depth>=4
DEFINE core_space          depth<2
DEFINE frontier            depth_in=2..3

DEFINE tick_early          tick<50
DEFINE tick_mid            tick_in=50..150
DEFINE tick_late           tick>=150

# ───────────────────────────────────────────────────────────────────────────────
# PLAYER EXPANSION RULES
# ───────────────────────────────────────────────────────────────────────────────

# Player territory expands into adjacent contested zones
RULE   IF player_territory AND tick%6=0 THEN ADVANCE AS player-grow

# Player fortifies deep territory
RULE   IF player_territory AND deep_space THEN GATE_ON AS player-fortify

# ───────────────────────────────────────────────────────────────────────────────
# ENEMY EXPANSION RULES
# ───────────────────────────────────────────────────────────────────────────────

# Enemy territory expands aggressively
RULE   IF enemy_territory AND tick%5=0 THEN ADVANCE AS enemy-grow

# Enemy pushes into frontier
RULE   IF enemy_territory AND frontier THEN ROTATE_CW AS enemy-push

# ───────────────────────────────────────────────────────────────────────────────
# CONTESTED ZONE BATTLES
# ───────────────────────────────────────────────────────────────────────────────

# Contested zones cycle between factions (battle simulation)
RULE   IF contested AND tick%4=0 THEN SWITCH Y_LOOP AS battle-player

RULE   IF contested AND tick%4=2 THEN SWITCH X_LOOP AS battle-enemy

# Deep contested zones become resource zones
RULE   IF contested AND deep_space AND random<0.3 THEN SWITCH DIAG_LOOP AS resource-discover

# ───────────────────────────────────────────────────────────────────────────────
# RESOURCE GENERATION
# ───────────────────────────────────────────────────────────────────────────────

# Resource zones pulse and generate credits
RULE   IF resource_zone AND tick%16=0 THEN ADVANCE AS resource-gen

# Resource zones in core space are more valuable (fortify them)
RULE   IF resource_zone AND core_space AND random<0.2 THEN GATE_ON AS resource-lock

# ───────────────────────────────────────────────────────────────────────────────
# FORTIFIED ZONES
# ───────────────────────────────────────────────────────────────────────────────

# Fortified zones resist change but can be attacked
RULE   IF fortified AND tick%20=0 AND random<0.1 THEN SWITCH Z_LOOP AS fortification-breach

# ───────────────────────────────────────────────────────────────────────────────
# DEPTH-BASED BEHAVIORS
# ───────────────────────────────────────────────────────────────────────────────

# Deep space expands slower but is more stable
RULE   IF deep_space AND player_territory THEN HOLD AS deep-hold

# Core space is highly contested
RULE   IF core_space AND contested THEN ADVANCE 2 AS core-battle

# ───────────────────────────────────────────────────────────────────────────────
# STOCHASTIC EVENTS
# ───────────────────────────────────────────────────────────────────────────────

# Random rebel bases appear
RULE   IF deep_space AND random<0.05 THEN SWITCH X_LOOP AS rebel-spawn

# Random player discoveries
RULE   IF frontier AND random<0.08 THEN SWITCH Y_LOOP AS player-discover

# ───────────────────────────────────────────────────────────────────────────────
# DEFAULT BEHAVIOR
# ───────────────────────────────────────────────────────────────────────────────

DEFAULT ADVANCE
