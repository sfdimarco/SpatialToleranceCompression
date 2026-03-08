# selforg_reaction_diffusion.geo — Reaction-Diffusion Pattern Generator
# ========================================================================
# Demonstrates: Activator-inhibitor dynamics, pattern formation, Turing patterns
#
# Usage: python Playground.py --geo examples/selforg/reaction_diffusion.geo --grid
#
# Simulates a simplified reaction-diffusion system (Gray-Scott model variant):
#   - Activator (A): Self-enhancing, diffuses slowly
#   - Inhibitor (B): Suppresses activator, diffuses quickly
#
# This creates emergent patterns like:
#   - Spots (leopard-like)
#   - Stripes (zebra-like)
#   - Labyrinths (coral-like)
#   - Waves (oscillating)
#
# Pattern type depends on feed/kill rates encoded in rules.

NAME   selforg_reaction_diffusion

# ═══════════════════════════════════════════════════════════════════════════════
# CELL STATE ENCODING
# Using mask and variables to track chemical concentrations
#   var_activator (0-10): Concentration of chemical A
#   var_inhibitor (0-10): Concentration of chemical B
#   mask: Visual representation of state
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALIZATION (ticks 0-10)
# Start with mostly activator, small inhibitor perturbations
# ═══════════════════════════════════════════════════════════════════════════════

# Most cells start with high activator
RULE   IF tick_in=0..10 AND random<0.9
       THEN SET 1100 + SET_VAR activator 8 + SET_VAR inhibitor 2 + SET_VAR age 0  AS init-A

# Random inhibitor seeds (perturbations)
RULE   IF tick_in=0..10 AND random<0.1
       THEN SET 0011 + SET_VAR activator 3 + SET_VAR inhibitor 7 + SET_VAR age 0  AS init-B

# Central seed for symmetric patterns
RULE   IF tick=5 AND depth=0
       THEN SET 0011 + SET_VAR activator 2 + SET_VAR inhibitor 9  AS center-seed

# ═══════════════════════════════════════════════════════════════════════════════
# ACTIVATOR DYNAMICS
# A self-enhances and produces B
# ═══════════════════════════════════════════════════════════════════════════════

# Activator growth (autocatalysis)
RULE   IF tick>=11 AND var_activator>=5 AND var_inhibitor<=4
       THEN INCR_VAR activator 2 + SET 1100  AS activator-grow

# Activator produces inhibitor (reaction)
RULE   IF tick>=11 AND var_activator>=6
       THEN INCR_VAR inhibitor 1 + INCR_VAR activator -1  AS reaction-AB

# Activator decay
RULE   IF tick>=11 AND var_activator>=1
       THEN INCR_VAR activator -1  AS activator-decay

# Feed activator (constant input)
RULE   IF tick>=11 AND random<0.15
       THEN INCR_VAR activator 1  AS feed-A

# ═══════════════════════════════════════════════════════════════════════════════
# INHIBITOR DYNAMICS
# B suppresses A and decays over time
# ═══════════════════════════════════════════════════════════════════════════════

# Inhibitor suppresses activator
RULE   IF tick>=11 AND var_inhibitor>=6 AND var_activator>=3
       THEN INCR_VAR activator -2  AS inhibitor-suppress

# Inhibitor decay (faster than activator)
RULE   IF tick>=11 AND var_inhibitor>=1
       THEN INCR_VAR inhibitor -1  AS inhibitor-decay

# Kill inhibitor (constant removal)
RULE   IF tick>=11 AND var_inhibitor>=1 AND random<0.2
       THEN INCR_VAR inhibitor -1  AS kill-B

# ═══════════════════════════════════════════════════════════════════════════════
# DIFFUSION (simplified via neighbor averaging)
# Activator diffuses slowly, inhibitor diffuses quickly
# ═══════════════════════════════════════════════════════════════════════════════

# Activator diffusion (slow - spreads from high-A neighbors via signal)
RULE   IF tick>=11 AND var_activator<=4 AND signal=activator_wave
       THEN INCR_VAR activator 1  AS diffuse-A-in

RULE   IF tick>=11 AND var_activator>=7 AND random<0.3
       THEN INCR_VAR activator -1 + EMIT activator_wave  AS diffuse-A-out

# Inhibitor diffusion (fast - spreads to 1+ neighbors)
RULE   IF tick>=11 AND var_inhibitor>=6 AND random<0.4
       THEN EMIT inhibitor_wave  AS diffuse-B

RULE   IF tick>=11 AND signal=inhibitor_wave AND var_inhibitor<8
       THEN INCR_VAR inhibitor 2  AS receive-B

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN FORMATION
# Visual representation based on chemical state
# ═══════════════════════════════════════════════════════════════════════════════

# High A, low B = spots (active regions)
RULE   IF tick>=20 AND var_activator>=7 AND var_inhibitor<=3
       THEN SET 1111  AS pattern-spot

# Medium A, medium B = stripes (transition regions)
RULE   IF tick>=20 AND var_activator_in=4..6 AND var_inhibitor_in=4..6
       THEN SET 1100  AS pattern-stripe

# Low A, high B = background (inhibited regions)
RULE   IF tick>=20 AND var_activator<=3 AND var_inhibitor>=6
       THEN SET 0001  AS pattern-background

# Oscillating regions (wave fronts)
RULE   IF tick>=20 AND var_activator_in=5..7 AND var_inhibitor_in=5..7
       THEN ROTATE_CW  AS pattern-wave

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN TYPE SELECTION
# Different parameter regimes create different patterns
# ═══════════════════════════════════════════════════════════════════════════════

# SPOTS regime (high feed, low kill)
RULE   IF tick%200_in=0..49 AND var_activator>=6
       THEN INCR_VAR activator 1  AS regime-spots

# STRIPES regime (medium feed, medium kill)
RULE   IF tick%200_in=50..99 AND var_activator_in=4..7
       THEN SET 1100  AS regime-stripes

# LABYRINTH regime (low feed, high kill)
RULE   IF tick%200_in=100..149 AND var_activator>=5
       THEN INCR_VAR inhibitor 1  AS regime-labyrinth

# WAVES regime (oscillating parameters)
RULE   IF tick%200_in=150..199
       THEN ROTATE_CW  AS regime-waves

# ═══════════════════════════════════════════════════════════════════════════════
# STABILITY CHECK
# Monitor if pattern has stabilized
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF tick>=100 AND var_activator>=5
       THEN INCR_VAR stable_count 1  AS count-stable

RULE   IF tick>=100 AND var_stable_count>=50
       THEN EMIT pattern_stable  AS signal-stable

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNALS FOR GAME INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

RULE   IF tick=10   THEN EMIT phase_init_complete     AS signal-phase1
RULE   IF tick=50   THEN EMIT phase_reaction_complete AS signal-phase2
RULE   IF tick=100  THEN EMIT phase_diffusion_complete AS signal-phase3
RULE   IF tick=150  THEN EMIT phase_pattern_complete  AS signal-phase4
RULE   IF tick=200  THEN EMIT reaction_diffusion_ready AS signal-ready

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT: Continue reaction-diffusion
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE + INCR_VAR age 1
