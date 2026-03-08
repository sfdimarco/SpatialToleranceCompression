# ecosystem.geo - Predator/Prey/Plant Simulation
# ================================================
# A three-tier ecosystem that emerges from simple grammar rules.
#
# Species (loop families):
#   PLANT     (X_LOOP - green)  : Grows, spreads, dies of old age
#   HERBIVORE (Z_LOOP - blue)   : Eats plants, reproduces, dies of starvation
#   PREDATOR  (Y_LOOP - red)    : Hunts herbivores, reproduces, dies of starvation
#   EMPTY     (GATE_OFF - dark) : Dead/empty space
#
# Cell Variables:
#   age         - How many ticks the entity has lived
#   energy      - Current energy reserves (for animals)
#   hunger      - Ticks since last meal
#
# Signals:
#   plant_food  - Emitted by plants (attracts herbivores)
#   prey_near   - Emitted by herbivores (attracts predators)
#   danger      - Emitted by predators (herbivores flee)

NAME   ecosystem

# === ALIASES ===
DEFINE is_empty     mask=0000
DEFINE is_plant     family=X_LOOP
DEFINE is_herbivore family=Z_LOOP
DEFINE is_predator  family=Y_LOOP

DEFINE is_young     var_age<5
DEFINE is_mature    var_age>=5
DEFINE is_old       var_age>=20

DEFINE is_hungry    var_hunger>=3
DEFINE is_starving  var_hunger>=8

# === SPAWNING RULES ===

# Empty space has a small chance to spontaneously grow a plant
RULE IF is_empty AND random<0.02 THEN SWITCH X_LOOP + SET_VAR age 0 + SET_VAR energy 10 AS spontaneous_plant

# === PLANT BEHAVIOR ===

# Young plants grow (accumulate energy)
RULE IF is_plant AND is_young THEN ADVANCE + INCR_VAR age 1 + INCR_VAR energy 1 AS plant_grow

# Mature plants spread seeds to neighbors
RULE IF is_plant AND is_mature AND random<0.08 THEN EMIT plant_food + INCR_VAR age 1 AS plant_seed

# Old plants die naturally
RULE IF is_plant AND is_old THEN GATE_OFF + EMIT plant_food AS plant_death

# Plants eaten by herbivores (detected by neighbor family)
RULE IF is_plant AND nb_any=Z_LOOP THEN GATE_OFF + EMIT plant_food AS eaten

# === HERBIVORE BEHAVIOR ===

# Spawn herbivore from empty space near plants (rare)
RULE IF is_empty AND signal=plant_food AND random<0.01 THEN SWITCH Z_LOOP + SET_VAR age 0 + SET_VAR energy 15 + SET_VAR hunger 0 AS herbivore_birth

# Young herbivores mature
RULE IF is_herbivore AND is_young THEN ADVANCE + INCR_VAR age 1 + INCR_VAR hunger 1 AS herbivore_grow

# Hungry herbivores near plants eat and gain energy
RULE IF is_herbivore AND is_hungry AND nb_any=X_LOOP THEN SWITCH X_LOOP + SET_VAR energy 20 + SET_VAR hunger 0 + INCR_VAR age 1 AS herbivore_eat

# Well-fed herbivores reproduce
RULE IF is_herbivore AND is_mature AND var_energy>=12 AND random<0.05 THEN EMIT prey_near + INCR_VAR energy -5 AS herbivore_reproduce

# Herbivores flee from predators
RULE IF is_herbivore AND signal=danger THEN ROTATE_CCW + INCR_VAR hunger 1 AS herbivore_flee

# Starving herbivores die
RULE IF is_herbivore AND is_starving THEN GATE_OFF + EMIT plant_food AS herbivore_starve

# Normal herbivore behavior - move and get hungrier
RULE IF is_herbivore THEN ADVANCE + INCR_VAR age 1 + INCR_VAR hunger 1 + EMIT prey_near AS herbivore_live

# === PREDATOR BEHAVIOR ===

# Spawn predator from empty space near herbivores (very rare)
RULE IF is_empty AND signal=prey_near AND random<0.005 THEN SWITCH Y_LOOP + SET_VAR age 0 + SET_VAR energy 20 + SET_VAR hunger 0 AS predator_birth

# Young predators mature
RULE IF is_predator AND is_young THEN ADVANCE + INCR_VAR age 1 + INCR_VAR hunger 1 AS predator_grow

# Hungry predators near herbivores hunt and eat
RULE IF is_predator AND is_hungry AND nb_any=Z_LOOP THEN SWITCH Z_LOOP + SET_VAR energy 25 + SET_VAR hunger 0 + INCR_VAR age 1 + EMIT danger AS predator_hunt

# Well-fed predators reproduce
RULE IF is_predator AND is_mature AND var_energy>=15 AND random<0.04 THEN EMIT danger + INCR_VAR energy -6 AS predator_reproduce

# Starving predators die
RULE IF is_predator AND is_starving THEN GATE_OFF AS predator_starve

# Normal predator behavior - hunt and emit danger signal
RULE IF is_predator THEN ADVANCE + INCR_VAR age 1 + INCR_VAR hunger 1 + EMIT danger AS predator_live

# === DECAY ===

# Empty cells just hold
RULE IF is_empty THEN HOLD AS empty_decay

# === DEFAULT ===
DEFAULT ADVANCE
