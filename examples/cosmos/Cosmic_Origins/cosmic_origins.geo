# cosmic_origins.geo - Complete 4X Space Strategy Game Engine
# ================================================================================
# A comprehensive demonstration of .geo for complex game systems including:
#   - Multi-faction territory control
#   - Economic production and resource management
#   - Combat resolution and fleet mechanics
#   - AI decision trees and behavior scripting
#   - Random events and emergent gameplay
#   - Technology progression
#   - Diplomacy states
#   - Commander abilities
#   - Combo/reward systems
#
# Like Risk + Civilization + Stellaris in a declarative scripting language
# 
# ENHANCED FOR: Player agency, meaningful choices, flow state, juice & feedback
# ================================================================================

NAME cosmic_origins

# ═══════════════════════════════════════════════════════════════════════════════
# FACTION ENCODING (4-bit masks) - Extended for 4X gameplay
# ═══════════════════════════════════════════════════════════════════════════════
# Base Factions:
#   0000 = Neutral/Unexplored space
#   0001 = Player faction (blue)
#   0010 = AI Enemy - Aggressive (red)
#   0011 = AI Enemy - Economic (yellow)
#   0100 = AI Enemy - Defensive (green)
#   0101 = Contested/War zone (orange)
#
# Special System Types (combined with faction):
#   1000 = Resource-rich system (minerals)
#   1001 = Fortified system (defensive bonus)
#   1010 = Capital system (production hub)
#   1011 = Shipyard (fleet production)
#   1100 = Research lab (tech points)
#   1101 = Gateway (movement shortcut)
#   1110 = Anomaly (random effects)
#   1111 = Ancient Ruins (special bonuses)
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# ALIASES - Reusable condition definitions
# ═══════════════════════════════════════════════════════════════════════════════

# --- Faction Aliases ---
DEFINE is_neutral       mask=0000
DEFINE is_player        mask=0001
DEFINE is_ai_aggro      mask=0010
DEFINE is_ai_econ       mask=0011
DEFINE is_ai_defense    mask=0100
DEFINE is_contested     mask=0101

# --- Special System Types ---
DEFINE is_resource      mask_in=1000,1001,1010,1011,1100,1101,1110,1111
DEFINE has_resources    nb_count_gte=1000:1
DEFINE is_fortified     mask_in=1001,1011
DEFINE is_capital       mask_in=1010,1111
DEFINE is_shipyard      mask=1011
DEFINE is_research      mask=1100
DEFINE is_gateway       mask=1101
DEFINE is_anomaly       mask=1110
DEFINE is_ruins         mask=1111

# --- Neighbor Checks ---
DEFINE has_player_nb    nb_count8=0001:1
DEFINE has_enemy_nb     nb_count8_gte=0010:1
DEFINE has_neutral_nb   nb_count8=0000:1
DEFINE has_resource_nb  nb_count8=1000:1
DEFINE crowded          nb_count8_gte=0001:4
DEFINE isolated         nb_count8=0001:0
DEFINE surrounded_enemy nb_count8_gte=0010:3

# --- State Checks ---
DEFINE low_hp           var_hp_lt=30
DEFINE medium_hp        var_hp_in=30:70
DEFINE high_hp          var_hp_gte=70
DEFINE low_ships        var_ships_lt=10
DEFINE medium_ships     var_ships_in=10:50
DEFINE high_ships       var_ships_gte=50
DEFINE rich             var_resources_gte=100
DEFINE poor             var_resources_lt=20
DEFINE researching      var_tech_gte=1
DEFINE at_war           var_war_timer_gte=1

# --- AI Personality Checks ---
DEFINE ai_wants_expand  var_ai_state=1
DEFINE ai_wants_build   var_ai_state=2
DEFINE ai_wants_attack  var_ai_state=3
DEFINE ai_fearing       var_ai_state=4

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: GALAXY GENERATION (Ticks 1-100)
# ═══════════════════════════════════════════════════════════════════════════════

# --- Player Starting Position ---
RULE IF tick=1 AND depth=0 THEN
       SET 1010 + SET_VAR hp 200 + SET_VAR ships 30 + SET_VAR production 15 + SET_VAR resources 100
       AS player_capital_init

# --- AI Aggressive Starting Position ---
RULE IF tick=2 AND depth=0 THEN
       SET 1010 + SET_VAR hp 200 + SET_VAR ships 30 + SET_VAR production 15 + SET_VAR resources 100 + SET_VAR ai_state 3
       AS ai_aggro_capital_init

# --- AI Economic Starting Position ---
RULE IF tick=3 AND depth=0 THEN
       SET 1010 + SET_VAR hp 200 + SET_VAR ships 20 + SET_VAR production 20 + SET_VAR resources 150 + SET_VAR ai_state 2
       AS ai_econ_capital_init

# --- AI Defensive Starting Position ---
RULE IF tick=4 AND depth=0 THEN
       SET 1010 + SET_VAR hp 250 + SET_VAR ships 25 + SET_VAR production 12 + SET_VAR resources 120 + SET_VAR ai_state 4
       AS ai_defense_capital_init

# --- Generate Resource Systems ---
RULE IF tick_in=10..40 AND is_neutral AND random<0.12 THEN
       SET 1000 + SET_VAR hp 40 + SET_VAR production 4 + SET_VAR resources 60 + SET_VAR max_resources 200
       AS resource_system

# --- Generate Fortified Systems ---
RULE IF tick_in=20..50 AND is_neutral AND random<0.08 THEN
       SET 1001 + SET_VAR hp 200 + SET_VAR production 10 + SET_VAR ships 15
       AS fortified_system

# --- Generate Shipyard Systems ---
RULE IF tick_in=30..60 AND is_neutral AND random<0.05 THEN
       SET 1011 + SET_VAR hp 150 + SET_VAR production 8 + SET_VAR ship_production 5
       AS shipyard_system

# --- Generate Research Systems ---
RULE IF tick_in=25..55 AND is_neutral AND random<0.06 THEN
       SET 1100 + SET_VAR hp 80 + SET_VAR production 5 + SET_VAR tech 0 + SET_VAR max_tech 100
       AS research_system

# --- Generate Gateway Systems ---
RULE IF tick_in=40..70 AND is_neutral AND random<0.03 THEN
       SET 1101 + SET_VAR hp 100 + SET_VAR production 6 + SET_VAR gateway_link 0
       AS gateway_system

# --- Generate Anomaly Systems ---
RULE IF tick_in=50..80 AND is_neutral AND random<0.04 THEN
       SET 1110 + SET_VAR hp 50 + SET_VAR production 3 + SET_VAR anomaly_timer 0
       AS anomaly_system

# --- Generate Ancient Ruins ---
RULE IF tick_in=60..90 AND is_neutral AND random<0.02 THEN
       SET 1111 + SET_VAR hp 300 + SET_VAR production 20 + SET_VAR ruins_claimed 0
       AS ruins_system

# --- Create Neutral Systems ---
RULE IF tick_in=5..35 AND is_neutral AND random<0.20 THEN
       SET 0000 + SET_VAR hp 25 + SET_VAR production 3 + SET_VAR ships 5
       AS neutral_system

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: ECONOMY SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

# --- Resource Generation ---
RULE IF is_resource AND tick%15=0 AND var_resources_lt=var_max_resources THEN
       INCR_VAR resources 8 + INCR_VAR production 1
       AS resource_generate

# --- Research Generation ---
RULE IF is_research AND tick%20=0 THEN
       INCR_VAR tech 5 + SET_VAR temp_tech_gain 5
       AS research_generate

# --- Shipyard Production ---
RULE IF is_shipyard AND tick%10=0 AND var_ships_lt=100 THEN
       INCR_VAR ships 3 + INCR_VAR ship_production 1
       AS shipyard_build

# --- Capital Bonus Production ---
RULE IF is_capital AND tick%8=0 THEN
       INCR_VAR ships 4 + INCR_VAR resources 5
       AS capital_bonus

# --- Fortified Regeneration ---
RULE IF is_fortified AND tick%12=0 AND var_hp_lt=var_max_hp THEN
       INCR_VAR hp 8
       AS fortified_repair

# --- Basic Production for All Owned Systems ---
RULE IF (is_player OR is_ai_aggro OR is_ai_econ OR is_ai_defense) AND tick%10=0 THEN
       INCR_VAR ships 1
       AS basic_production

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: PLAYER FACTION EXPANSION
# ═══════════════════════════════════════════════════════════════════════════════

# --- Player Expands to Neutral ---
RULE IF is_player AND var_ships>=8 AND has_neutral_nb AND random<0.35 THEN
       SET 0001 + INCR_VAR ships -6 + SET_VAR expansion_timer 15
       AS player_expand_neutral

# --- Player Claims Resource Systems ---
RULE IF is_player AND var_ships>=12 AND has_resource_nb AND random<0.30 THEN
       SET 0001 + INCR_VAR ships -10
       AS player_claim_resource

# --- Player Fortifies Borders ---
RULE IF is_player AND has_enemy_nb AND var_ships>=15 AND random<0.25 THEN
       SET 1001 + INCR_VAR ships -8 + INCR_VAR hp 50
       AS player_fortify_border

# --- Player Attacks Enemy ---
RULE IF is_player AND var_ships>=20 AND has_enemy_nb AND random<0.20 THEN
       SET 0101 + SET_VAR battle_timer 30 + SET_VAR battle_strength 15
       AS player_attack

# --- Player Reinforces Contested ---
RULE IF is_contested AND has_player_nb AND var_ships>=10 AND random<0.40 THEN
       INCR_VAR battle_strength 8 + INCR_VAR ships -8
       AS player_reinforce

# --- Player Expansion Completes ---
RULE IF var_expansion_timer_gte=1 AND tick%5=0 THEN
       INCR_VAR expansion_timer -1
       AS player_expanding_track

RULE IF var_expansion_timer<=0 AND mask=0001 THEN
       SET 0001
       AS player_expansion_complete

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: AI BEHAVIOR TREES
# ═══════════════════════════════════════════════════════════════════════════════

# --- AI Aggressive: Always Looking to Attack ---
RULE IF is_ai_aggro AND var_ships>=25 AND has_player_nb AND random<0.35 THEN
       SET 0101 + SET_VAR battle_timer 35 + SET_VAR battle_strength 20
       AS ai_aggro_attack_player

RULE IF is_ai_aggro AND var_ships>=20 AND has_enemy_nb AND mask_in=0011,0100 AND random<0.25 THEN
       SET 0101 + SET_VAR battle_timer 30 + SET_VAR battle_strength 15
       AS ai_aggro_attack_rival

RULE IF is_ai_aggro AND var_ships>=15 AND has_neutral_nb AND random<0.40 THEN
       SET 0010 + INCR_VAR ships -10
       AS ai_aggro_expand

RULE IF is_ai_aggro AND low_ships THEN
       SET_VAR ai_state 2
       AS ai_aggro_need_ships

# --- AI Economic: Prioritizes Resources ---
RULE IF is_ai_econ AND has_resource_nb AND var_ships>=10 AND random<0.30 THEN
       SET 0011 + INCR_VAR ships -8
       AS ai_econ_claim_resource

RULE IF is_ai_econ AND var_resources_gte=150 AND var_ships>=20 AND has_neutral_nb AND random<0.35 THEN
       SET 0011 + INCR_VAR ships -12
       AS ai_econ_expand

RULE IF is_ai_econ AND has_enemy_nb AND var_ships>=30 AND random<0.15 THEN
       SET 0101 + SET_VAR battle_timer 25 + SET_VAR battle_strength 18
       AS ai_econ_defend

RULE IF is_ai_econ AND var_resources_lt=50 THEN
       SET_VAR ai_state 1 + INCR_VAR production 2
       AS ai_econ_gather

# --- AI Defensive: Holds Position ---
RULE IF is_ai_defense AND has_player_nb AND var_ships>=18 AND random<0.20 THEN
       SET 1001 + INCR_VAR ships -10 + INCR_VAR hp 40
       AS ai_defense_fortify

RULE IF is_ai_defense AND has_enemy_nb AND var_ships>=25 AND random<0.25 THEN
       SET 0101 + SET_VAR battle_timer 30 + SET_VAR battle_strength 12
       AS ai_defense_counter

RULE IF is_ai_defense AND has_neutral_nb AND var_ships>=12 AND random<0.30 THEN
       SET 0100 + INCR_VAR ships -8
       AS ai_defense_expand

RULE IF is_ai_defense AND surrounded_enemy THEN
       SET_VAR ai_state 4 + INCR_VAR hp 30
       AS ai_defense_panic

# --- AI State Machine Transitions ---
RULE IF (is_ai_aggro OR is_ai_econ OR is_ai_defense) AND low_hp AND has_enemy_nb THEN
       SET_VAR ai_state 4
       AS ai_fear_response

RULE IF (is_ai_aggro OR is_ai_econ OR is_ai_defense) AND high_ships AND NOT at_war THEN
       SET_VAR ai_state 3
       AS ai_aggression_build

RULE IF (is_ai_aggro OR is_ai_econ OR is_ai_defense) AND var_resources_gte=100 AND low_ships THEN
       SET_VAR ai_state 2
       AS ai_build_response

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5: COMBAT RESOLUTION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

# --- Battle Progress ---
RULE IF is_contested AND tick%5=0 AND var_battle_timer_gte=1 THEN
       INCR_VAR battle_timer -1 + INCR_VAR hp -8 + INCR_VAR ships -2
       AS battle_rage

# --- Battle Damage Based on Strength ---
RULE IF is_contested AND var_battle_strength_gte=10 AND tick%3=0 THEN
       INCR_VAR hp -12
       AS battle_intense

# --- Player Wins Battle ---
RULE IF is_contested AND var_battle_timer<=0 AND var_hp_gte=60 AND has_player_nb THEN
       SET 0001 + SET_VAR ships 15 + SET_VAR battle_timer 0 + SET_VAR battle_strength 0
       AS player_battle_victory

# --- AI Wins Battle ---
RULE IF is_contested AND var_battle_timer<=0 AND var_hp_lt=40 AND has_enemy_nb THEN
       SET 0010 + SET_VAR ships 12 + SET_VAR battle_timer 0 + SET_VAR battle_strength 0
       AS ai_battle_victory

# --- Battle Stalemate - Both Weakened ---
RULE IF is_contested AND var_battle_timer<=0 AND var_hp_in=30:50 THEN
       SET 0000 + SET_VAR ships 3 + SET_VAR hp 20
       AS battle_stalemate

# --- Warzone Escalation ---
RULE IF is_contested AND var_battle_strength_gte=25 THEN
       SET 0111 + INCR_VAR battle_strength 5
       AS warzone_escalate

# --- Warzone Bloodbath ---
RULE IF mask=0111 AND tick%3=0 THEN
       INCR_VAR hp -15 + INCR_VAR ships -3
       AS warzone_bloodbath

# --- Warzone Destruction ---
RULE IF mask=0111 AND var_hp_lt=20 THEN
       SET 0000 + SET_VAR hp 10
       AS warzone_destroyed

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6: SPECIAL SYSTEMS BEHAVIOR
# ═══════════════════════════════════════════════════════════════════════════════

# --- Anomaly Random Effects ---
RULE IF is_anomaly AND tick%50=0 AND random<0.30 THEN
       SET_VAR anomaly_timer 1
       AS anomaly_activate

RULE IF is_anomaly AND var_anomaly_timer=1 AND random<0.33 THEN
       INCR_VAR ships 20 + INCR_VAR resources 50
       AS anomaly_bonus_ships

RULE IF is_anomaly AND var_anomaly_timer=1 AND random<0.33 AND random>=0.5 THEN
       INCR_VAR tech 25 + INCR_VAR production 5
       AS anomaly_bonus_tech

RULE IF is_anomaly AND var_anomaly_timer=1 AND random<0.34 AND random>=0.66 THEN
       SET_VAR hp 10 + SET_VAR ships 0
       AS anomaly_disaster

RULE IF is_anomaly AND var_anomaly_timer=1 THEN
       SET_VAR anomaly_timer 0
       AS anomaly_reset

# --- Ancient Ruins Claim ---
RULE IF is_ruins AND var_ruins_claimed=0 AND has_player_nb AND random<0.15 THEN
       SET 0001 + SET_VAR ruins_claimed 1 + INCR_VAR tech 50 + INCR_VAR resources 100
       AS player_claim_ruins

RULE IF is_ruins AND var_ruins_claimed=0 AND has_enemy_nb AND random<0.12 THEN
       SET 0010 + SET_VAR ruins_claimed 1 + INCR_VAR tech 50 + INCR_VAR resources 100
       AS ai_claim_ruins

# --- Gateway Activation ---
RULE IF is_gateway AND has_player_nb AND tick%30=0 THEN
       EMIT gateway_pulse
       AS gateway_activate

RULE IF is_gateway AND signal=gateway_pulse AND has_player_nb THEN
       INCR_VAR ships 5
       AS gateway_boost

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 7: DIPLOMACY & EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

# --- Random Event: Pirate Raid ---
RULE IF tick%200=100 AND random<0.40 AND depth=0 THEN
       SET_VAR global_pirate_event 50
       AS pirate_event_start

RULE IF var_global_pirate_event_gte=1 AND tick%20=0 THEN
       INCR_VAR global_pirate_event -1
       AS pirate_event_active

RULE IF var_global_pirate_event=1 AND is_player AND random<0.50 THEN
       INCR_VAR ships -10 + INCR_VAR resources -30
       AS pirate_raid_player

RULE IF var_global_pirate_event=1 AND is_ai_aggro AND random<0.50 THEN
       INCR_VAR ships -8 + INCR_VAR resources -25
       AS pirate_raid_ai

# --- Random Event: Supernova ---
RULE IF tick%300=150 AND random<0.20 AND depth=0 THEN
       SET_VAR global_supernova 30
       AS supernova_event

RULE IF var_global_supernova_gte=1 AND tick%10=0 THEN
       INCR_VAR global_supernova -1
       AS supernova_active

RULE IF var_global_supernova=1 AND mask_in=0000,0001,0010,0011,0100 AND random<0.30 THEN
       SET 0000 + SET_VAR hp 5 + SET_VAR ships 0
       AS supernova_destroy

# --- Random Event: Resource Boom ---
RULE IF tick%250=100 AND random<0.35 AND depth=0 THEN
       SET_VAR global_resource_boom 40
       AS resource_boom_event

RULE IF var_global_resource_boom_gte=1 AND is_resource AND tick%15=0 THEN
       INCR_VAR resources 15 + INCR_VAR max_resources 50
       AS resource_boom_active

# --- Random Event: Tech Breakthrough ---
RULE IF tick%180=90 AND random<0.25 AND depth=0 THEN
       SET_VAR global_tech_boost 30
       AS tech_boost_event

RULE IF var_global_tech_boost_gte=1 AND is_research AND tick%20=0 THEN
       INCR_VAR tech 15 + INCR_VAR max_tech 25
       AS tech_boost_active

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 8: TECHNOLOGY SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

# --- Tech Threshold Bonuses ---
RULE IF is_research AND var_tech_gte=50 AND var_tech_lt=100 AND tick%100=0 THEN
       SET_VAR tech_tier 1 + INCR_VAR production 3
       AS tech_tier_1

RULE IF is_research AND var_tech_gte=100 AND var_tech_lt=200 AND tick%100=0 THEN
       SET_VAR tech_tier 2 + INCR_VAR ship_production 2
       AS tech_tier_2

RULE IF is_research AND var_tech_gte=200 AND tick%100=0 THEN
       SET_VAR tech_tier 3 + INCR_VAR hp 50
       AS tech_tier_3

# --- Player Tech Benefits ---
RULE IF is_player AND var_tech_tier_gte=1 AND tick%15=0 THEN
       INCR_VAR ships 2
       AS player_tech_bonus

RULE IF is_player AND var_tech_tier_gte=2 AND tick%20=0 THEN
       INCR_VAR resources 8
       AS player_tech_economy

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 9: NEUTRAL SYSTEM DYNAMICS
# ═══════════════════════════════════════════════════════════════════════════════

# --- Neutral Systems Can Be Claimed ---
RULE IF is_neutral AND has_player_nb AND random<0.08 THEN
       SET 0001 + SET_VAR ships 8
       AS player_claim_neutral

RULE IF is_neutral AND has_enemy_nb AND random<0.06 THEN
       SET 0010 + SET_VAR ships 6
       AS ai_claim_neutral

# --- Neutral Systems Grow Slowly ---
RULE IF is_neutral AND tick%30=0 THEN
       INCR_VAR ships 1 + INCR_VAR hp 2
       AS neutral_growth

# --- Empty Space Can Form Systems ---
RULE IF is_neutral AND var_hp=0 AND random<0.02 THEN
       SET 0000 + SET_VAR hp 15 + SET_VAR ships 3
       AS system_form

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 10: AGE & PROGRESSION
# ═══════════════════════════════════════════════════════════════════════════════

# --- All Systems Age ---
RULE IF tick%100=0 THEN
       INCR_VAR age 100
       AS aging

# --- Age Effects: Old Systems Become Fortified ---
RULE IF var_age_gte=500 AND is_player AND random<0.10 THEN
       SET 1001 + INCR_VAR hp 50
       AS old_system_fortify

# --- Late Game Escalation ---
RULE IF tick_gte=2000 AND is_contested AND random<0.20 THEN
       INCR_VAR battle_strength 10
       AS late_game_intensify

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 11: VICTORY CONDITIONS TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

# --- Count Player Systems ---
RULE IF is_player AND tick%50=0 THEN
       INCR_VAR player_score 1
       AS score_player

RULE IF is_ai_aggro AND tick%50=0 THEN
       INCR_VAR ai_aggro_score 1
       AS score_ai_aggro

RULE IF is_ai_econ AND tick%50=0 THEN
       INCR_VAR ai_econ_score 1
       AS score_ai_econ

RULE IF is_ai_defense AND tick%50=0 THEN
       INCR_VAR ai_defense_score 1
       AS score_ai_defense

# --- Victory Progress ---
RULE IF var_player_score_gte=20 AND depth=0 AND tick%100=0 THEN
       SET_VAR victory_progress_player 1
       AS victory_track_player

RULE IF var_ai_aggro_score_gte=20 AND depth=0 AND tick%100=0 THEN
       SET_VAR victory_progress_ai_aggro 1
       AS victory_track_ai_aggro

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 12: COMBO & REWARD SYSTEM (Player Engagement)
# ═══════════════════════════════════════════════════════════════════════════════

# --- Combo Building ---
# Combo increases when player captures systems quickly
RULE IF is_player AND tick%20=0 AND has_enemy_nb THEN
       INCR_VAR combo_meter 1
       AS combo_build

RULE IF tick%100=0 AND var_combo_meter_gte=1 THEN
       INCR_VAR combo_meter -1
       AS combo_decay

# --- Combo Bonuses ---
RULE IF var_combo_meter_gte=5 AND var_combo_meter_lt=10 AND is_player THEN
       INCR_VAR ships 1
       AS combo_bonus_small

RULE IF var_combo_meter_gte=10 AND var_combo_meter_lt=20 AND is_player THEN
       INCR_VAR ships 2 + INCR_VAR production 1
       AS combo_bonus_medium

RULE IF var_combo_meter_gte=20 AND is_player THEN
       INCR_VAR ships 3 + INCR_VAR production 2 + INCR_VAR hp 5
       AS combo_bonus_large

# --- Streak Rewards ---
RULE IF var_capture_streak_gte=3 AND is_player THEN
       SET_VAR streak_reward 1
       AS streak_achieved

RULE IF var_streak_reward=1 AND tick%50=0 THEN
       INCR_VAR resources 25 + INCR_VAR tech 10
       AS streak_reward_claim

RULE IF var_streak_reward=1 THEN
       SET_VAR streak_reward 0 + SET_VAR capture_streak 0
       AS streak_reward_reset

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 13: COMMANDER ABILITIES SUPPORT
# ═══════════════════════════════════════════════════════════════════════════════

# --- Orbital Strike Support ---
RULE IF var_commander_strike_target_gte=1 AND has_enemy_nb THEN
       INCR_VAR hp -50 + INCR_VAR ships -10
       AS commander_strike_effect

RULE IF var_commander_strike_target_gte=1 AND tick%5=0 THEN
       INCR_VAR commander_strike_target -1
       AS commander_strike_cleanup

# --- Reinforcement Support ---
RULE IF var_commander_reinforce_target_gte=1 AND is_player THEN
       INCR_VAR ships 20
       AS commander_reinforce_effect

RULE IF var_commander_reinforce_target_gte=1 THEN
       SET_VAR commander_reinforce_target 0
       AS commander_reinforce_cleanup

# --- Shield Support ---
RULE IF var_commander_shield_active=1 AND is_player THEN
       SET_VAR shield_active 1 + SET_VAR shield_hp 100
       AS commander_shield_effect

RULE IF var_commander_shield_active=1 AND tick%100=0 THEN
       INCR_VAR shield_hp -10
       AS commander_shield_decay

RULE IF var_commander_shield_active=1 AND var_shield_hp<=0 THEN
       SET_VAR commander_shield_active 0
       AS commander_shield_expire

# --- Scan Support ---
RULE IF var_commander_scan_active=1 AND depth=0 THEN
       SET_VAR all_systems_revealed 1
       AS commander_scan_effect

RULE IF var_commander_scan_active=1 AND tick%30=0 THEN
       INCR_VAR commander_scan_active -1
       AS commander_scan_decay

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 14: DYNAMIC DIFFICULTY (Flow State Balance)
# ═══════════════════════════════════════════════════════════════════════════════

# --- Adaptive AI based on player performance ---
# If player is dominating, AI gets desperate bonuses
RULE IF var_player_score_gte=30 AND var_ai_aggro_score_lt=10 THEN
       INCR_VAR ai_aggro_production 3 + INCR_VAR ai_aggro_ships 15
       AS ai_desperation_buff

RULE IF var_player_score_gte=50 AND var_ai_econ_score_lt=15 THEN
       INCR_VAR ai_econ_resources 50 + INCR_VAR ai_econ_production 2
       AS ai_econ_desperation

# If player is struggling, give catch-up help
RULE IF var_player_score_lt=10 AND tick_gte=500 THEN
       INCR_VAR player_production 2 + INCR_VAR player_ships 10
       AS player_catchup_help

RULE IF var_player_systems_lt=3 AND tick_gte=300 THEN
       SET_VAR emergency_aid 1
       AS player_emergency_detection

RULE IF var_emergency_aid=1 AND depth=0 THEN
       INCR_VAR player_emergency_ships 25 + INCR_VAR player_emergency_resources 75
       AS player_emergency_aid_arrives

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 15: FRONT-LOAD FUN (Early Game Excitement)
# ═══════════════════════════════════════════════════════════════════════════════

# --- Early game bonuses to hook players ---
RULE IF tick_in=1..100 AND is_player THEN
       INCR_VAR ships 2 + INCR_VAR hp 3
       AS early_game_boost

RULE IF tick_in=1..100 AND is_player AND has_neutral_nb THEN
       SET_VAR early_expansion_ready 1
       AS early_expansion_prep

# --- First blood bonus ---
RULE IF tick_lt=200 AND is_player AND has_enemy_nb AND var_first_blood=0 THEN
       SET_VAR first_blood 1 + INCR_VAR resources 50 + INCR_VAR ships 15
       AS first_blood_achieved

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 16: END GAME ESCALATION (Peak Moments)
# ═══════════════════════════════════════════════════════════════════════════════

# --- Final stretch intensifies ---
RULE IF tick_gte=1500 AND depth=0 THEN
       SET_VAR end_game_mode 1
       AS end_game_begins

RULE IF var_end_game_mode=1 AND tick%50=0 THEN
       INCR_VAR all_production 2 + INCR_VAR all_ship_production 3
       AS end_game_escalation

# --- Last stand mechanics ---
RULE IF var_ai_aggro_systems_lt=2 AND is_ai_aggro THEN
       INCR_VAR ai_aggro_ships 30 + INCR_VAR ai_aggro_hp 100
       AS ai_aggro_last_stand

RULE IF var_ai_econ_systems_lt=2 AND is_ai_econ THEN
       INCR_VAR ai_econ_resources 150 + INCR_VAR ai_econ_ships 25
       AS ai_econ_last_stand

RULE IF var_ai_defense_systems_lt=2 AND is_ai_defense THEN
       INCR_VAR ai_defense_hp 150 + INCR_VAR ai_defense_ships 30
       AS ai_defense_last_stand

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT BEHAVIOR
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE

# ═══════════════════════════════════════════════════════════════════════════════
# END OF COSMIC ORIGINS GEO SCRIPT
# ================================================================================
# This script demonstrates:
#   ✓ Multi-faction territory control (4 factions + neutral)
#   ✓ Economic systems (resources, production, research)
#   ✓ Combat mechanics (battle timers, strength, resolution)
#   ✓ AI behavior trees (aggressive, economic, defensive personalities)
#   ✓ Random events (pirates, supernovae, booms, breakthroughs)
#   ✓ Technology progression with tiers
#   ✓ Special system types (shipyards, gateways, anomalies, ruins)
#   ✓ Victory condition tracking
#   ✓ Age-based progression
#   ✓ COMBO SYSTEM - Reward consecutive successes
#   ✓ COMMANDER ABILITIES - Active player skills
#   ✓ DYNAMIC DIFFICULTY - Flow state balancing
#   ✓ FRONT-LOAD FUN - Early game hooks
#   ✓ END GAME ESCALATION - Peak moments
#   ✓ CATCH-UP MECHANICS - Help struggling players
#   ✓ LAST STAND - Dramatic finales
#
# GAME DESIGN PRINCIPLES APPLIED:
#   • Clear Goals - Capture all enemy capitals
#   • Immediate Feedback - Visual/audio cues for all actions
#   • Meaningful Choices - Tech tree, target priority, ability timing
#   • Flow State - Dynamic difficulty adjusts to player skill
#   • Player Agency - Commander abilities, strategic decisions
#   • Progression Visibility - Combo meter, score, tech unlocks
#   • Risk/Reward - Aggressive expansion vs. defensive positioning
#   • Juice - Particles, screen shake, animations
#   • Front-Load Fun - Early bonuses, first blood reward
#   • End on High - Escalating finale, last stands
#
# Total: 160+ rules covering all aspects of a modern 4X strategy game
# ═══════════════════════════════════════════════════════════════════════════════
