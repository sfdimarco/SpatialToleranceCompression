# galaxy_generator.geo - Procedural Galaxy Generation
# ====================================================
# Generates complete galaxy structures with star systems,
# resource distributions, and habitable zones.
#
# Used by: Cosmic Origins game

NAME   galaxy_generator

# --- Galactic Core (depth 0) ---
RULE   IF depth=0  THEN SET 1111  AS spawn-blackhole

# --- Dense star cluster around core ---
RULE   IF depth_in=1..3 AND random<0.4  THEN SET 1000  AS core-star-dense

# --- Spiral arm pattern (4 arms) ---
# Each depth layer activates on different tick phases
RULE   IF depth_in=1..3 AND tick%4=0 AND depth%4=0  THEN SET 1000  AS spiral-arm-star
RULE   IF depth_in=1..3 AND tick%4=1 AND depth%4=1  THEN SET 1000  AS spiral-arm-star
RULE   IF depth_in=1..3 AND tick%4=2 AND depth%4=2  THEN SET 1000  AS spiral-arm-star
RULE   IF depth_in=1..3 AND tick%4=3 AND depth%4=3  THEN SET 1000  AS spiral-arm-star

# --- Inner stars ---
RULE   IF depth_in=1..3 AND random<0.3  THEN SET 1000  AS inner-star

# --- Mid-region stars ---
RULE   IF depth_in=4..6 AND random<0.2  THEN SET 1000  AS mid-star

# --- Outer stars ---
RULE   IF depth_in=7..9 AND random<0.15  THEN SET 1000  AS outer-star

# --- Asteroid belts ---
RULE   IF depth_in=4..6 AND random<0.25  THEN SET 0111  AS asteroid-belt

# --- Gas clouds ---
RULE   IF depth_in=7..9 AND random<0.2  THEN SET 1001  AS gas-cloud

# --- Nebula (star forming) ---
RULE   IF depth_in=4..6 AND random<0.08  THEN SET 1001  AS nebula

# --- Kuiper belt ---
RULE   IF depth>=10 AND random<0.35  THEN SET 0111  AS kuiper-belt

# --- Edge objects ---
RULE   IF depth>=10 AND random<0.15  THEN SET 1111  AS edge-object

# --- Default ---
DEFAULT ADVANCE
