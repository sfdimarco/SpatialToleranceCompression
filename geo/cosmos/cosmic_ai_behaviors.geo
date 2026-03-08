# cosmic_ai_behaviors.geo - Advanced AI Behavior Trees
# ================================================================================
# Modular AI behavior system for Cosmic Origins
# Import this file into your main game script with: INCLUDE cosmic_ai_behaviors.geo
#
# This module provides:
#   - Decision tree patterns for AI factions
#   - Threat assessment and response
#   - Strategic priority weighting
#   - Personality-driven behavior variations
# ================================================================================

NAME cosmic_ai_behaviors

# ═══════════════════════════════════════════════════════════════════════════════
# THREAT ASSESSMENT SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

# --- Threat Level Detection ---
DEFINE threat_critical  nb_count_gte=0001:4 AND var_hp_lt=30
DEFINE threat_high      nb_count_gte=0001:3 AND var_hp_lt=50
DEFINE threat_medium    nb_count_gte=0001:2 AND var_hp_lt=70
DEFINE threat_low       nb_count_gte=0001:1
DEFINE threat_none      nb_count8=0001:0

# --- AI Threat Responses ---
# Critical: Panic and reinforce
RULE IF threat_critical AND is_ai_aggro THEN
       SET_VAR ai_priority 100 + SET_VAR ai_action 1
       AS ai_threat_critical_aggro

RULE IF threat_critical AND is_ai_econ THEN
       SET_VAR ai_priority 100 + SET_VAR ai_action 2
       AS ai_threat_critical_econ

RULE IF threat_critical AND is_ai_defense THEN
       SET_VAR ai_priority 100 + SET_VAR ai_action 3 + INCR_VAR hp 20
       AS ai_threat_critical_defense

# High: Build up defenses
RULE IF threat_high AND is_ai_aggro THEN
       SET_VAR ai_priority 80 + SET_VAR ai_action 4
       AS ai_threat_high_aggro

RULE IF threat_high AND is_ai_econ THEN
       SET_VAR ai_priority 70 + SET_VAR ai_action 2
       AS ai_threat_high_econ

RULE IF threat_high AND is_ai_defense THEN
       SET_VAR ai_priority 90 + SET_VAR ai_action 3 + INCR_VAR hp 15
       AS ai_threat_high_defense

# Medium: Cautious expansion
RULE IF threat_medium AND is_ai_aggro THEN
       SET_VAR ai_priority 50 + SET_VAR ai_action 5
       AS ai_threat_medium_aggro

RULE IF threat_medium AND is_ai_econ THEN
       SET_VAR ai_priority 60 + SET_VAR ai_action 6
       AS ai_threat_medium_econ

RULE IF threat_medium AND is_ai_defense THEN
       SET_VAR ai_priority 70 + SET_VAR ai_action 3
       AS ai_threat_medium_defense

# Low: Normal operations
RULE IF threat_low AND is_ai_aggro THEN
       SET_VAR ai_priority 30 + SET_VAR ai_action 5
       AS ai_threat_low_aggro

RULE IF threat_low AND is_ai_econ THEN
       SET_VAR ai_priority 40 + SET_VAR ai_action 6
       AS ai_threat_low_econ

RULE IF threat_low AND is_ai_defense THEN
       SET_VAR ai_priority 50 + SET_VAR ai_action 7
       AS ai_threat_low_defense

# No Threat: Aggressive expansion
RULE IF threat_none AND is_ai_aggro THEN
       SET_VAR ai_priority 20 + SET_VAR ai_action 5
       AS ai_no_threat_aggro

RULE IF threat_none AND is_ai_econ THEN
       SET_VAR ai_priority 30 + SET_VAR ai_action 6
       AS ai_no_threat_econ

RULE IF threat_none AND is_ai_defense THEN
       SET_VAR ai_priority 40 + SET_VAR ai_action 7
       AS ai_no_threat_defense

# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGIC PRIORITIES
# ═══════════════════════════════════════════════════════════════════════════════

# Priority 100: Survival (under heavy attack)
RULE IF var_ai_priority=100 AND var_ships_gte=5 THEN
       SET_VAR ai_action 1 + INCR_VAR ships -5
       AS ai_survival_retreat

RULE IF var_ai_priority=100 AND var_hp_lt=20 THEN
       SET_VAR ai_flee_timer 30
       AS ai_survival_flee

# Priority 80-90: Defense (fortify position)
RULE IF var_ai_priority_in=80:90 AND is_ai_defense THEN
       SET 1001 + INCR_VAR hp 30
       AS ai_defense_fortify_priority

RULE IF var_ai_priority_in=80:90 AND var_ships_gte=15 THEN
       SET_VAR ai_action 3 + INCR_VAR ships -10
       AS ai_defense_reinforce

# Priority 50-70: Balanced (expand carefully)
RULE IF var_ai_priority_in=50:70 AND has_neutral_nb AND var_ships_gte=10 THEN
       SET_VAR ai_action 7 + INCR_VAR ships -8
       AS ai_balanced_expand

RULE IF var_ai_priority_in=50:70 AND has_resource_nb THEN
       SET_VAR ai_action 6
       AS ai_balanced_resource

# Priority 20-40: Growth (economic focus)
RULE IF var_ai_priority_in=20:40 AND is_ai_econ THEN
       SET_VAR ai_action 6 + INCR_VAR production 2
       AS ai_growth_economy

RULE IF var_ai_priority_in=20:40 AND has_neutral_nb THEN
       SET_VAR ai_action 7
       AS ai_growth_expand

# Priority 0-10: Aggression (all-out attack)
RULE IF var_ai_priority_in=0:10 AND is_ai_aggro AND var_ships_gte=25 THEN
       SET_VAR ai_action 5 + SET_VAR attack_intensity 100
       AS ai_aggression_full

RULE IF var_ai_priority_in=0:10 AND var_ships_gte=20 THEN
       SET_VAR ai_action 5
       AS ai_aggression_attack

# ═══════════════════════════════════════════════════════════════════════════════
# ACTION EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

# Action 1: Retreat/Regroup
RULE IF var_ai_action=1 AND has_player_nb THEN
       INCR_VAR ships -3 + INCR_VAR hp 10
       AS ai_retreat_execute

# Action 2: Economic Focus
RULE IF var_ai_action=2 AND is_resource THEN
       INCR_VAR resources 10 + INCR_VAR production 1
       AS ai_econ_focus_execute

# Action 3: Defensive Posture
RULE IF var_ai_action=3 THEN
       SET 1001 + INCR_VAR hp 20
       AS ai_defense_execute

# Action 4: Buildup
RULE IF var_ai_action=4 AND tick%10=0 THEN
       INCR_VAR ships 2 + INCR_VAR hp 5
       AS ai_buildup_execute

# Action 5: Attack Player
RULE IF var_ai_action=5 AND has_player_nb AND var_ships_gte=15 THEN
       SET 0101 + SET_VAR battle_timer 25 + INCR_VAR ships -12
       AS ai_attack_player_execute

# Action 6: Capture Resources
RULE IF var_ai_action=6 AND has_resource_nb AND var_ships_gte=8 THEN
       SET_VAR ai_claim_resource 1 + INCR_VAR ships -6
       AS ai_claim_resource_execute

# Action 7: Expand to Neutral
RULE IF var_ai_action=7 AND has_neutral_nb AND var_ships_gte=8 THEN
       INCR_VAR ships -6
       AS ai_expand_neutral_execute

# ═══════════════════════════════════════════════════════════════════════════════
# PERSONALITY MODIFIERS
# ═══════════════════════════════════════════════════════════════════════════════

# Aggressive Personality Bonuses
RULE IF is_ai_aggro AND tick%50=0 THEN
       INCR_VAR aggression_meter 5
       AS ai_aggro_personality_tick

RULE IF is_ai_aggro AND var_aggression_meter_gte=50 AND var_ships_gte=20 THEN
       SET_VAR ai_priority 10 + SET_VAR attack_intensity 80
       AS ai_aggro_rage_mode

# Economic Personality Bonuses
RULE IF is_ai_econ AND var_resources_gte=100 THEN
       INCR_VAR production 2 + INCR_VAR tech 5
       AS ai_econ_efficiency

RULE IF is_ai_econ AND is_resource THEN
       INCR_VAR resources 3
       AS ai_econ_resource_bonus

# Defensive Personality Bonuses
RULE IF is_ai_defense AND is_fortified THEN
       INCR_VAR hp 3 + INCR_VAR ships 1
       AS ai_defense_fortress_bonus

RULE IF is_ai_defense AND has_enemy_nb THEN
       SET_VAR ai_priority 60
       AS ai_defense_vigilance

# ═══════════════════════════════════════════════════════════════════════════════
# COORDINATED AI (Multi-front warfare)
# ═══════════════════════════════════════════════════════════════════════════════

# AI Alliance Detection
DEFINE ai_ally_aggro  nb_prog_N=ai_aggro OR nb_prog_any=ai_aggro
DEFINE ai_ally_econ   nb_prog_N=ai_econ OR nb_prog_any=ai_econ
DEFINE ai_ally_defense nb_prog_N=ai_defense OR nb_prog_any=ai_defense

# Coordinated Attack Signal
RULE IF is_ai_aggro AND var_attack_intensity_gte=80 AND tick%20=0 THEN
       EMIT attack_signal
       AS ai_aggro_call_support

RULE IF is_ai_econ AND signal=attack_signal AND var_ships_gte=15 THEN
       SET_VAR ai_action 5 + INCR_VAR ships -10
       AS ai_econ_support_attack

RULE IF is_ai_defense AND signal=attack_signal AND var_ships_gte=12 THEN
       SET_VAR ai_action 3 + INCR_VAR hp 25
       AS ai_defense_support

# Resource Sharing (Economic AI helps others)
RULE IF is_ai_econ AND var_resources_gte=200 AND has_enemy_nb THEN
       EMIT resource_boost
       AS ai_econ_share_resources

RULE IF signal=resource_boost AND is_ai_aggro THEN
       INCR_VAR resources 20
       AS ai_aggro_receive_resources

# ═══════════════════════════════════════════════════════════════════════════════
# ADAPTIVE LEARNING
# ═══════════════════════════════════════════════════════════════════════════════

# Track battle outcomes
RULE IF is_contested AND var_battle_timer<=0 AND has_enemy_nb THEN
       INCR_VAR ai_battle_wins 1
       AS ai_track_victory

RULE IF is_contested AND var_battle_timer<=0 AND has_player_nb THEN
       INCR_VAR ai_battle_losses 1
       AS ai_track_defeat

# Adjust strategy based on win rate
RULE IF var_ai_battle_wins_gte=5 AND var_ai_battle_losses_lt=2 THEN
       SET_VAR ai_confidence 100 + INCR_VAR aggression_meter 20
       AS ai_confident_strategy

RULE IF var_ai_battle_losses_gte=4 AND var_ai_battle_wins_lt=2 THEN
       SET_VAR ai_confidence 30 + SET_VAR ai_priority 70
       AS ai_cautious_strategy

# Confidence affects behavior
RULE IF var_ai_confidence_gte=80 AND var_ships_gte=20 THEN
       SET_VAR ai_priority 15
       AS ai_confident_attack

RULE IF var_ai_confidence_lt=40 THEN
       SET_VAR ai_priority 65 + SET_VAR ai_action 3
       AS ai_cautious_defend

# ═══════════════════════════════════════════════════════════════════════════════
# LATE GAME AI ESCALATION
# ═══════════════════════════════════════════════════════════════════════════════

# Tick-based difficulty scaling
RULE IF tick_gte=1000 AND is_ai_aggro THEN
       INCR_VAR production 2 + INCR_VAR ship_production 1
       AS ai_late_game_buff_1

RULE IF tick_gte=2000 AND is_ai_aggro THEN
       INCR_VAR production 3 + INCR_VAR hp 50
       AS ai_late_game_buff_2

RULE IF tick_gte=3000 AND is_ai_aggro THEN
       SET_VAR ai_priority 5 + SET_VAR attack_intensity 100
       AS ai_late_game_desperation

# Final stand behavior
RULE IF var_ai_system_count_lt=3 AND is_ai_aggro THEN
       SET_VAR ai_priority 10 + SET_VAR ai_action 5
       AS ai_last_stand

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE

# ═══════════════════════════════════════════════════════════════════════════════
# END OF AI BEHAVIORS MODULE
# ================================================================================
# Usage: Include this file in your main .geo script to enable advanced AI
#
# Example:
#   NAME my_game
#   INCLUDE cosmic_ai_behaviors.geo
#   [your game rules here]
# ═══════════════════════════════════════════════════════════════════════════════
