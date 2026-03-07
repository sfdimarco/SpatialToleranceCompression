# conway_life.geo
# Conway's Game of Life approximation using quad-mask families as alive/dead.
# Y_LOOP = alive, GATE(0000) = dead.
# Uses neighbor counting conditions on a Grid.
# Alive + 2-3 alive neighbors -> stay alive, else die.
# Dead + exactly 3 alive neighbors -> come alive.
NAME   conway_life
DEFINE alive       family=Y_LOOP
DEFINE dead        mask=0000
RULE   IF alive AND nb_count=Y_LOOP:2  THEN ADVANCE              AS survive-2
RULE   IF alive AND nb_count=Y_LOOP:3  THEN ADVANCE              AS survive-3
RULE   IF alive                        THEN GATE_OFF             AS die
RULE   IF dead AND nb_count=Y_LOOP:3   THEN SWITCH Y_LOOP        AS birth
DEFAULT HOLD
