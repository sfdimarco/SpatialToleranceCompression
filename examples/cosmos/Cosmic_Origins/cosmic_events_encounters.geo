# cosmic_events_encounters.geo - Random Events & Encounter System
# ================================================================================
# Modular event system for Cosmic Origins
# Provides dynamic events that create emergent gameplay moments
#
# Event Categories:
#   - Disasters (supernovae, pirate raids, plagues)
#   - Bonuses (resource booms, ancient gifts, breakthroughs)
#   - Encounters (traders, refugees, mysteries)
#   - Story Events (faction discoveries, ancient awakenings)
# ================================================================================

NAME cosmic_events_encounters

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL EVENT TIMERS & TRIGGERS
# ═══════════════════════════════════════════════════════════════════════════════

# Event cooldown tracking
DEFINE event_cooldown_active  var_global_event_cd_gte=1
DEFINE event_ready            var_global_event_cd_lt=1

# Major event triggers (roll every 100 ticks)
DEFINE roll_major_event       tick%100=0 AND random<0.30 AND event_ready
DEFINE roll_minor_event       tick%50=0 AND random<0.40 AND event_ready
DEFINE roll_personal_event    tick%30=0 AND random<0.25 AND event_ready

# ═══════════════════════════════════════════════════════════════════════════════
# DISASTER EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

# --- Supernova ---
RULE IF roll_major_event AND random<0.15 AND depth=0 THEN
       SET_VAR global_supernova_warning 30 + SET_VAR global_event_cd 100
       AS supernova_warning_start

RULE IF var_global_supernova_warning_gte=1 AND tick%10=0 THEN
       INCR_VAR global_supernova_warning -1
       AS supernova_countdown

RULE IF var_global_supernova_warning=1 AND depth=0 THEN
       SET_VAR global_supernova_active 20
       AS supernova_erupt

RULE IF var_global_supernova_active_gte=1 AND tick%5=0 THEN
       INCR_VAR global_supernova_active -1
       AS supernova_active

RULE IF var_global_supernova_active=1 AND mask_in=0000,0001,0010,0011,0100 AND random<0.40 THEN
       SET 0000 + SET_VAR hp 5 + SET_VAR ships 0 + SET_VAR production 1
       AS supernova_destroy_system

# --- Pirate Raid ---
RULE IF roll_major_event AND random<0.25 AND depth=0 THEN
       SET_VAR global_pirate_event 60 + SET_VAR global_event_cd 80
       AS pirate_fleet_spotted

RULE IF var_global_pirate_event_gte=1 AND tick%20=0 THEN
       INCR_VAR global_pirate_event -1
       AS pirate_fleet_approach

RULE IF var_global_pirate_event=30 AND is_player AND var_ships_gte=10 THEN
       INCR_VAR ships -8 + INCR_VAR resources -40
       AS pirate_raid_player_systems

RULE IF var_global_pirate_event=30 AND is_ai_aggro AND var_ships_gte=10 THEN
       INCR_VAR ships -6 + INCR_VAR resources -30
       AS pirate_raid_ai_systems

RULE IF var_global_pirate_event=1 AND depth=0 THEN
       SET_VAR global_pirate_event 0
       AS pirate_event_end

# --- Plague Outbreak ---
RULE IF roll_minor_event AND random<0.20 AND depth=0 THEN
       SET_VAR global_plague 80 + SET_VAR global_event_cd 120
       AS plague_outbreak_start

RULE IF var_global_plague_gte=1 AND tick%15=0 THEN
       INCR_VAR global_plague -1
       AS plague_spreading

RULE IF var_global_plague_gte=1 AND is_player AND random<0.15 THEN
       INCR_VAR ships -3 + INCR_VAR production -1
       AS plague_hit_player

RULE IF var_global_plague_gte=1 AND mask_in=0001,0010,0011,0100 AND random<0.20 THEN
       INCR_VAR hp -15 + INCR_VAR ships -2
       AS plague_hit_faction

RULE IF var_global_plague=1 AND depth=0 THEN
       SET_VAR global_plague 0
       AS plague_ends

# --- Economic Collapse ---
RULE IF roll_minor_event AND random<0.15 AND depth=0 THEN
       SET_VAR global_economic_crisis 100 + SET_VAR global_event_cd 150
       AS economic_crisis_start

RULE IF var_global_economic_crisis_gte=1 AND tick%20=0 THEN
       INCR_VAR global_economic_crisis -1
       AS economic_crisis_active

RULE IF var_global_economic_crisis_gte=1 AND is_resource THEN
       INCR_VAR resources -5 + INCR_VAR production -1
       AS economic_crisis_resource_penalty

RULE IF var_global_economic_crisis=1 AND depth=0 THEN
       SET_VAR global_economic_crisis 0 + SET_VAR production 2
       AS economic_recovery

# ═══════════════════════════════════════════════════════════════════════════════
# BONUS EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

# --- Resource Boom ---
RULE IF roll_major_event AND random<0.30 AND depth=0 THEN
       SET_VAR global_resource_boom 80 + SET_VAR global_event_cd 90
       AS resource_boom_discovered

RULE IF var_global_resource_boom_gte=1 AND tick%15=0 THEN
       INCR_VAR global_resource_boom -1
       AS resource_boom_active

RULE IF var_global_resource_boom_gte=1 AND is_resource THEN
       INCR_VAR resources 12 + INCR_VAR max_resources 30
       AS resource_boom_generate

RULE IF var_global_resource_boom_gte=1 AND is_player AND tick%30=0 THEN
       INCR_VAR resources 25
       AS resource_boom_player_bonus

# --- Technology Breakthrough ---
RULE IF roll_minor_event AND random<0.25 AND depth=0 THEN
       SET_VAR global_tech_breakthrough 60 + SET_VAR global_event_cd 100
       AS tech_breakthrough_discovered

RULE IF var_global_tech_breakthrough_gte=1 AND tick%20=0 THEN
       INCR_VAR global_tech_breakthrough -1
       AS tech_breakthrough_active

RULE IF var_global_tech_breakthrough_gte=1 AND is_research THEN
       INCR_VAR tech 8 + INCR_VAR max_tech 20
       AS tech_breakthrough_research

RULE IF var_global_tech_breakthrough_gte=1 AND is_player AND tick%40=0 THEN
       INCR_VAR tech 30
       AS tech_breakthrough_player_bonus

# --- Ancient Gift ---
RULE IF roll_major_event AND random<0.10 AND is_ruins AND var_ruins_claimed=0 THEN
       SET_VAR ancient_gift_available 1
       AS ancient_gift_appears

RULE IF var_ancient_gift_available=1 AND is_player AND random<0.20 THEN
       SET 0001 + INCR_VAR tech 75 + INCR_VAR resources 150 + INCR_VAR hp 100
       AS player_receives_ancient_gift

RULE IF var_ancient_gift_available=1 AND is_ai_aggro AND random<0.15 THEN
       SET 0010 + INCR_VAR tech 60 + INCR_VAR resources 120
       AS ai_receives_ancient_gift

# --- Fleet Reinforcement ---
RULE IF roll_personal_event AND is_player AND var_ships_lt=10 AND random<0.30 THEN
       INCR_VAR ships 12
       AS player_reinforcement_arrives

RULE IF roll_personal_event AND is_ai_defense AND var_ships_lt=15 AND random<0.25 THEN
       INCR_VAR ships 10
       AS ai_defense_reinforcement

# ═══════════════════════════════════════════════════════════════════════════════
# ENCOUNTER EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

# --- Trader Convoy ---
RULE IF roll_minor_event AND random<0.20 AND depth=0 THEN
       SET_VAR trader_event 40 + SET_VAR trader_location random
       AS trader_convoy_arrives

RULE IF var_trader_event_gte=1 AND tick%10=0 THEN
       INCR_VAR var_trader_event -1
       AS trader_convoy_traveling

RULE IF var_trader_event=20 AND is_player AND var_resources_gte=50 THEN
       INCR_VAR resources -40 + INCR_VAR ships 15 + INCR_VAR tech 10
       AS player_trades_with_convoy

RULE IF var_trader_event=20 AND is_ai_econ AND var_resources_gte=60 THEN
       INCR_VAR resources -50 + INCR_VAR production 3
       AS ai_econ_trades_with_convoy

RULE IF var_trader_event=1 AND depth=0 THEN
       SET_VAR trader_event 0
       AS trader_convoy_departs

# --- Refugee Fleet ---
RULE IF roll_minor_event AND random<0.25 AND depth=0 THEN
       SET_VAR refugee_event 50
       AS refugee_fleet_arrives

RULE IF var_refugee_event_gte=1 AND tick%15=0 THEN
       INCR_VAR var_refugee_event -1
       AS refugee_fleet_waiting

RULE IF var_refugee_event=25 AND is_player AND random<0.50 THEN
       INCR_VAR ships 8 + INCR_VAR resources 20 + SET_VAR refugee_rewarded 1
       AS player_helps_refugees

RULE IF var_refugee_event=25 AND is_ai_defense AND random<0.40 THEN
       INCR_VAR ships 6 + INCR_VAR hp 20
       AS ai_defense_helps_refugees

RULE IF var_refugee_event=1 AND NOT var_refugee_rewarded=1 THEN
       SET_VAR refugee_left 1
       AS refugee_fleet_departs

# --- Mysterious Signal ---
RULE IF roll_personal_event AND random<0.15 AND is_anomaly THEN
       SET_VAR mystery_signal 30
       AS mystery_signal_detected

RULE IF var_mystery_signal_gte=1 AND tick%10=0 THEN
       INCR_VAR var_mystery_signal -1
       AS mystery_signal_countdown

RULE IF var_mystery_signal=1 AND is_player AND random<0.50 THEN
       INCR_VAR tech 40 + INCR_VAR ships 10
       AS player_investigates_mystery_success

RULE IF var_mystery_signal=1 AND is_player AND random>=0.50 THEN
       INCR_VAR hp -30 + INCR_VAR ships -5
       AS player_investigates_mystery_danger

# ═══════════════════════════════════════════════════════════════════════════════
# STORY EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

# --- Ancient Gateway Awakens ---
RULE IF tick=500 AND depth=0 AND random<0.50 THEN
       SET_VAR gateway_awakening 1
       AS ancient_gateway_activates

RULE IF var_gateway_awakening=1 AND is_gateway AND tick%50=0 THEN
       INCR_VAR ships 8 + INCR_VAR tech 5
       AS gateway_powering_up

RULE IF var_gateway_awakening=1 AND tick=600 AND depth=0 THEN
       SET_VAR gateway_fully_active 1 + INCR_VAR all_gateway_ships 20
       AS gateway_fully_awakened

# --- Faction Discovery ---
RULE IF tick=800 AND depth=0 THEN
       SET_VAR faction_discovery_event 1
       AS new_faction_discovered

RULE IF var_faction_discovery_event=1 AND is_neutral AND random<0.10 THEN
       SET 0101 + SET_VAR ships 25 + SET_VAR hp 100
       AS independent_faction_appears

# --- The Great War ---
RULE IF tick=1500 AND depth=0 AND random<0.40 THEN
       SET_VAR great_war_event 200
       AS great_war_begins

RULE IF var_great_war_event_gte=1 AND tick%30=0 THEN
       INCR_VAR var_great_war_event -1
       AS great_war_active

RULE IF var_great_war_event_gte=1 AND is_contested THEN
       INCR_VAR battle_strength 15 + INCR_VAR battle_timer 10
       AS great_war_intensifies_battles

RULE IF var_great_war_event=1 AND depth=0 THEN
       SET_VAR great_war_event 0
       AS great_war_ends

# ═══════════════════════════════════════════════════════════════════════════════
# SEASONAL/CYCLICAL EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

# --- Comet Passage (every 400 ticks) ---
RULE IF tick%400=0 AND depth=0 THEN
       SET_VAR comet_passage 60
       AS comet_approaches

RULE IF var_comet_passage_gte=1 AND tick%20=0 THEN
       INCR_VAR var_comet_passage -1
       AS comet_traveling

RULE IF var_comet_passage=30 AND is_anomaly THEN
       INCR_VAR tech 20 + INCR_VAR resources 30
       AS comet_enriches_anomaly

RULE IF var_comet_passage=1 AND depth=0 THEN
       SET_VAR comet_passage 0
       AS comet_departs

# --- Nebula Drift (every 600 ticks) ---
RULE IF tick%600=0 AND depth=0 THEN
       SET_VAR nebula_drift 100
       AS nebula_arrives

RULE IF var_nebula_drift_gte=1 AND tick%25=0 THEN
       INCR_VAR var_nebula_drift -1
       AS nebula_drifting

RULE IF var_nebula_drift_gte=1 AND mask_in=0000,0001,0010,0011,0100 THEN
       INCR_VAR hp 3 + INCR_VAR production 1
       AS nebula_nourishes_systems

RULE IF var_nebula_drift=1 AND depth=0 THEN
       SET_VAR nebula_drift 0
       AS nebula_departs

# ═══════════════════════════════════════════════════════════════════════════════
# EMERGENCY EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

# --- Player Near Defeat ---
RULE IF tick_gte=300 AND is_player AND nb_count8=0001:0 AND random<0.30 THEN
       SET_VAR player_emergency 1
       AS player_near_extinction

RULE IF var_player_emergency=1 AND depth=0 THEN
       INCR_VAR player_emergency_ships 25 + INCR_VAR player_emergency_resources 75
       AS player_emergency_aid

# --- AI Faction Collapse ---
RULE IF is_ai_aggro AND nb_count8=0010:0 AND tick%100=0 THEN
       SET_VAR ai_aggro_collapse 1
       AS ai_aggro_near_defeat

RULE IF var_ai_aggro_collapse=1 AND random<0.40 THEN
       INCR_VAR ships 20 + INCR_VAR hp 50
       AS ai_aggro_last_stand

# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT ADVANCE

# ═══════════════════════════════════════════════════════════════════════════════
# END OF EVENTS & ENCOUNTERS MODULE
# ================================================================================
# Usage: Include this file in your main .geo script to enable dynamic events
#
# Events are organized by category:
#   - Disasters: Challenging events that test the player
#   - Bonuses: Positive events that reward smart play
#   - Encounters: Neutral events with choices
#   - Story: Narrative-driven milestone events
#   - Seasonal: Cyclical events that create rhythm
#   - Emergency: Catch-up mechanics for balance
# ═══════════════════════════════════════════════════════════════════════════════
