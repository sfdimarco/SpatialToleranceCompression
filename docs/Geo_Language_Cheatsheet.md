# .geo Language Cheat Sheet

## Script Structure

```geo
NAME   my_program
DEFINE alias_name  condition_expression
RULE   IF <condition> THEN <action>  AS label
DEFAULT ADVANCE
INCLUDE other_file.geo
```

## Conditions

| Condition | Example |
|-----------|---------|
| `family=<FAM>` | `family=Y_LOOP` |
| `mask=<BITS>` | `mask=1010` |
| `mask_in=<A,B>` | `mask_in=1000,0100` |
| `tick>=N` / `tick<N` | `tick>=10` |
| `tick%P=R` | `tick%8=0` |
| `tick_in=A..B` | `tick_in=10..30` |
| `depth>=N` / `depth<N` / `depth=N` | `depth>=3` |
| `depth_in=A..B` | `depth_in=2..4` |
| `active=N` / `active>=N` / `active<=N` | `active=2` |
| `nb_N=<FAM>` (also S/E/W) | `nb_N=Y_LOOP` |
| `nb_any=<FAM>` | `nb_any=X_LOOP` |
| `nb_count=<FAM>:<N>` | `nb_count=Y_LOOP:2` |
| `nb_count_gte=<FAM>:<N>` | `nb_count_gte=Z_LOOP:3` |
| `nb_count8=<FAM>:<N>` | `nb_count8=GATE:5` |
| `nb_mask_count8=<BITS>:<N>` | `nb_mask_count8=1111:3` |
| `random<P` | `random<0.3` |
| `var_<name>>=N` / `var_<name>=N` / `var_<name><N` | `var_heat>=5` |
| `signal=<name>` | `signal=pulse` |
| `ALWAYS` | catch-all |

## Combinators

```geo
A AND B          # both true
A OR B           # either true
A BUT B          # A true, B false
NOT A            # negate
(A OR B) AND C   # grouping
```

## Actions

| Action | Example |
|--------|---------|
| `ADVANCE` / `ADVANCE N` | `ADVANCE 3` |
| `HOLD` | keep mask |
| `GATE_ON` / `GATE_OFF` | force 1111 / 0000 |
| `SWITCH <FAM>` | `SWITCH Y_LOOP` |
| `SET <BITS>` | `SET 1010` |
| `ROTATE_CW` / `ROTATE_CCW` | rotate bits |
| `FLIP_H` / `FLIP_V` | mirror bits |
| `SET_VAR <name> <val>` | `SET_VAR heat 0` |
| `INCR_VAR <name> [delta]` | `INCR_VAR heat 1` |
| `EMIT <signal>` | `EMIT pulse` |
| `PROG <name>` | switch program |
| `PLURALITY [N]` | adopt majority neighbor program |
| `action + action` | composite: `SWITCH Y_LOOP + EMIT beat` |

## Loop Families

```
                                         Python draws C order (TL,TR,BR,BL) | Z order (TL,TR,BL,BR)
Y_LOOP:    1000 -> 0100 -> 0010 -> 0001  one quadrant walks C ring          | walks the Z
X_LOOP:    1100 -> 0101 -> 0011 -> 1010  top, diag, bottom, diag            | top, right, bottom, left
Z_LOOP:    0111 -> 1011 -> 1101 -> 1110  gap walks the C ring               | gap walks the Z
DIAG_LOOP: 1001 <-> 0110                 left <-> right column              | diagonal <-> diagonal
GATE:      0000, 1111                    fixed points                       | fixed points
```

## Minimal Example

```geo
NAME   pulse
RULE   IF tick%4=0        THEN GATE_ON   AS flash
RULE   IF family=GATE     THEN SWITCH Y_LOOP  AS ungate
DEFAULT ADVANCE
```
