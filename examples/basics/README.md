# Basics - Getting Started with `.geo`

Introductory examples for learning `.geo` script syntax.

---

## Scripts

### `hello_world.geo`
**Purpose:** Your first `.geo` program  
**Complexity:** ⭐ Absolute Beginner

The simplest working `.geo` script that demonstrates basic syntax.

```geo
NAME hello_world

# Simple rule that advances mask every tick
RULE IF family=Y_LOOP THEN ADVANCE

# Default action when no rules match
DEFAULT HOLD
```

**Learn:**
- Script structure
- NAME statement
- RULE syntax
- DEFAULT action
- Basic conditions (`family=`)
- Basic actions (`ADVANCE`, `HOLD`)

---

## Running Your First Script

```bash
# Run hello_world
python BinaryQuadTreeTest.py --geo examples/basics/hello_world.geo

# See it in action with default settings
python BinaryQuadTreeTest.py
```

---

## Understanding the Script

### Structure

```geo
NAME <program_name>     # Give your program a name

RULE IF <condition>     # When this is true...
     THEN <action>      # ...do this

DEFAULT <action>        # If no rules match, do this
```

### Key Concepts

| Concept | Example | Meaning |
|---------|---------|---------|
| Family | `family=Y_LOOP` | Check which loop family |
| Advance | `ADVANCE` | Step to next mask in family |
| Hold | `HOLD` | Keep current mask |
| Tick | `tick%8=0` | Every 8 ticks |
| Depth | `depth>=3` | At depth 3 or deeper |

---

## Your First Modifications

### 1. Change the Family

```geo
RULE IF family=X_LOOP THEN ADVANCE
```

Now it responds to X_LOOP instead of Y_LOOP.

### 2. Add Timing

```geo
RULE IF tick%4=0 THEN ADVANCE
```

Now it only advances every 4 ticks.

### 3. Add Depth Condition

```geo
RULE IF depth>=2 THEN ADVANCE
```

Now shallow layers stay still, deep layers move.

### 4. Combine Conditions

```geo
RULE IF tick%4=0 AND family=Y_LOOP THEN ADVANCE
```

Multiple conditions with `AND`.

---

## Next Steps

After mastering `hello_world.geo`:

1. **Try `generative/spiral.geo`** - See family cycling
2. **Try `cellular/conway_life.geo`** - See cellular automata
3. **Try `geo_showcase/composite.geo`** - See action chaining
4. **Read [GEO_LANGUAGE.md](../GEO_LANGUAGE.md)** - Full reference

---

## Quick Reference

### Conditions

```geo
family=Y_LOOP       # Check family
mask=1010           # Check exact mask
tick%8=0            # Check tick (every 8)
depth>=3            # Check depth
```

### Actions

```geo
ADVANCE             # Step to next mask
HOLD                # Keep current mask
GATE_ON             # Set mask to 1111
GATE_OFF            # Set mask to 0000
SWITCH Y_LOOP       # Jump to Y_LOOP family
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Forgetting `THEN` | `RULE IF cond THEN action` |
| Wrong family name | Use `Y_LOOP`, `X_LOOP`, `Z_LOOP`, `DIAG_LOOP`, `GATE` |
| Missing DEFAULT | Always add `DEFAULT <action>` |
| Typos in conditions | Check spelling: `family=`, not `famliy=` |

---

## Getting Help

- **[GEO_LANGUAGE.md](../GEO_LANGUAGE.md)** - Complete language reference
- **[README.md](../README.md)** - Main documentation
- **[PLAYGROUND.md](../PLAYGROUND.md)** - Interactive testing

---

**Welcome to `.geo` scripting!** 🎉
