# combat_encounters.geo - Dynamic Space Combat Encounters
# ========================================================
# Generates enemy spawn patterns and tactical scenarios

NAME   combat_encounters

# --- Basic enemy spawn ---
RULE   IF tick%60=0 AND random<0.4  THEN SET 1100  AS spawn-scout

# --- Elite enemy spawn ---
RULE   IF tick%120=0 AND random<0.25  THEN SET 1100  AS spawn-elite

# --- Boss spawn (rare) ---
RULE   IF tick%300=0 AND random<0.15  THEN SET 1100  AS spawn-boss

# --- V-formation attack ---
RULE   IF tick%60=10 AND depth_in=1..3  THEN SET 1100  AS v-formation

# --- Circle formation defense ---
RULE   IF tick%60=20 AND depth_in=2..4  THEN SET 1100  AS circle-formation

# --- Line formation barrage ---
RULE   IF tick%60=30 AND depth_in=1..5  THEN SET 1100  AS line-formation

# --- Health power-up ---
RULE   IF tick%90=30 AND random<0.2  THEN SET 0111  AS spawn-health

# --- Weapon power-up ---
RULE   IF tick%120=60 AND random<0.15  THEN SET 0111  AS spawn-weapon

# --- Shield power-up ---
RULE   IF tick%100=45 AND random<0.18  THEN SET 0111  AS spawn-shield

# --- Asteroid obstacle ---
RULE   IF tick%40=15 AND depth_in=3..6  THEN SET 1001  AS asteroid

# --- Space debris ---
RULE   IF tick%30=25 AND random<0.3  THEN SET 1001  AS debris

# --- Wingman ally ---
RULE   IF tick%150=75 AND random<0.4  THEN SET 0111  AS spawn-wingman

# --- Healing drone ---
RULE   IF tick%200=100 AND random<0.25  THEN SET 0111  AS spawn-drone

# --- Default ---
DEFAULT ADVANCE
