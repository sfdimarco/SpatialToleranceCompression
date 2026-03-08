# ═══════════════════════════════════════════════════════════════════════════════
# FACTION WARS - Advanced Faction Behavior
# ═══════════════════════════════════════════════════════════════════════════════
# This .geo script handles faction-specific mechanics for the conquest game.
# Variables track:
#   - var_strength: Military power (0-10)
#   - var_supply: Resource supply (0-10)
#   - var_morale: Faction morale (0-10)
# ═══════════════════════════════════════════════════════════════════════════════

NAME   faction_wars

# ───────────────────────────────────────────────────────────────────────────────
# ALIASES
# ───────────────────────────────────────────────────────────────────────────────

DEFINE strong      var_strength>=7
DEFINE weak        var_strength<3
DEFINE well_supplied  var_supply>=5
DEFINE low_supply  var_supply<2
DEFINE high_morale var_morale>=6
DEFINE broken      var_morale<2

# ───────────────────────────────────────────────────────────────────────────────
# PLAYER FACTION ECONOMY
# ───────────────────────────────────────────────────────────────────────────────

# Resource territories generate supply
RULE   IF family=Y_LOOP AND var_supply<10 AND tick%10=0 
       THEN INCR_VAR supply 1 AS player-supply

# Supply enables strength growth
RULE   IF family=Y_LOOP AND well_supplied AND var_strength<10 AND tick%15=0
       THEN INCR_VAR strength 1 AS player-build

# ───────────────────────────────────────────────────────────────────────────────
# ENEMY FACTION ECONOMY
# ───────────────────────────────────────────────────────────────────────────────

# Enemy accumulates strength over time
RULE   IF family=X_LOOP AND tick%12=0 AND var_strength<10
       THEN INCR_VAR strength 1 AS enemy-build

# Enemy consumes supply
RULE   IF family=X_LOOP AND NOT var_supply=0 AND tick%8=0
       THEN INCR_VAR supply -1 AS enemy-consume

# Enemy low on supply becomes vulnerable
RULE   IF family=X_LOOP AND low_supply AND weak
       THEN SWITCH Z_LOOP + SET_VAR strength 2 AS enemy-weakness

# ───────────────────────────────────────────────────────────────────────────────
# COMBAT MECHANICS
# ───────────────────────────────────────────────────────────────────────────────

# Strong player attacks weak enemy neighbors
RULE   IF family=Y_LOOP AND strong AND tick%6=0
       THEN INCR_VAR morale 1 AS player-offensive

# Strong enemy attacks
RULE   IF family=X_LOOP AND strong AND tick%5=0
       THEN INCR_VAR morale 1 AS enemy-offensive

# Attack reduces supply
RULE   IF family=Y_LOOP AND var_supply>=2 AND tick%6=0
       THEN INCR_VAR supply -1 AS player-supply-cost

# ───────────────────────────────────────────────────────────────────────────────
# MORALE SYSTEM
# ───────────────────────────────────────────────────────────────────────────────

# Winning battles boosts morale
RULE   IF family=Y_LOOP AND strong AND high_morale AND tick%20=0
       THEN INCR_VAR strength 1 AS player-momentum

# Losing breaks morale
RULE   IF family=X_LOOP AND weak AND broken AND random<0.3
       THEN SWITCH Y_LOOP + SET_VAR strength 3 AS enemy-rout

# ───────────────────────────────────────────────────────────────────────────────
# REINFORCEMENTS
# ───────────────────────────────────────────────────────────────────────────────

# Player reinforces from core territories
RULE   IF family=Y_LOOP AND depth<2 AND var_strength>=5 AND tick%25=0
       THEN HOLD AS player-reinforce

# Enemy reinforces from deep space
RULE   IF family=X_LOOP AND depth>=4 AND var_strength>=4 AND tick%20=0
       THEN HOLD AS enemy-reinforce

# ───────────────────────────────────────────────────────────────────────────────
# TERRAIN EFFECTS
# ───────────────────────────────────────────────────────────────────────────────

# Deep space (frontier) is harder to hold
RULE   IF depth>=4 AND var_strength<5 AND random<0.2
       THEN SWITCH Z_LOOP + SET_VAR supply 0 AS frontier-loss

# Core worlds are easier to defend
RULE   IF depth<2 AND var_strength>=3 AND random<0.1
       THEN GATE_ON AS core-defend

# ───────────────────────────────────────────────────────────────────────────────
# SPECIAL EVENTS
# ───────────────────────────────────────────────────────────────────────────────

# Player discovers ancient technology
RULE   IF family=Y_LOOP AND depth>=3 AND random<0.03
       THEN SET_VAR strength 10 + SET_VAR morale 10 AS ancient-tech

# Enemy ambush
RULE   IF family=X_LOOP AND depth_in=2..3 AND random<0.05 AND var_strength>=5
       THEN INCR_VAR strength 3 AS enemy-ambush

# ───────────────────────────────────────────────────────────────────────────────
# DEFAULT
# ───────────────────────────────────────────────────────────────────────────────

DEFAULT ADVANCE
