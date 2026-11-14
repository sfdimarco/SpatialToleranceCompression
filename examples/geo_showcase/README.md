# Geo Showcase - Language Feature Demonstrations

Examples showcasing specific `.geo` language features.

---

## Scripts by Feature

### Condition Types

#### `mask_set.geo` - Mask Operations
Demonstrates `mask_in` conditions and multi-step `ADVANCE`.

```geo
RULE IF mask_in=1000,0100,0010 THEN ADVANCE 2
```

**Learn:** How to match multiple masks, advance by N steps

---

#### `depth_layers.geo` - Depth Conditions
Shows depth-based rule layering.

```geo
RULE IF depth_in=0..2 THEN action1
RULE IF depth_in=3..4 THEN action2
RULE IF depth>=5 THEN action3
```

**Learn:** Range conditions, stratified behavior

---

### Action Types

#### `composite.geo` - Composite Actions
Demonstrates chaining multiple actions.

```geo
RULE IF tick%8=0 THEN SWITCH Y_LOOP + EMIT beat + SET_VAR phase 0
```

**Learn:** Action chaining with `+`

---

#### `signal_wave.geo` - Inter-Cell Signals
Shows `EMIT` and `signal=` communication.

```geo
RULE IF family=Y_LOOP THEN ADVANCE + EMIT pulse
RULE IF signal=pulse THEN SWITCH X_LOOP
```

**Learn:** Cell-to-cell communication

---

#### `vote_example.geo` - Plurality Voting
Demonstrates `PLURALITY` action.

```geo
RULE IF neighbor_count>=3 THEN PLURALITY 2
```

**Learn:** Adopting neighbor programs

---

## Usage

```bash
# Run a showcase demo
python BinaryQuadTreeTest.py --geo examples/geo_showcase/composite.geo

# List all demos
python BinaryQuadTreeTest.py --list
```

---

## Feature Reference

| Feature | Syntax | Example Script |
|---------|--------|----------------|
| Mask matching | `mask_in=A,B,C` | `mask_set.geo` |
| Depth ranges | `depth_in=A..B` | `depth_layers.geo` |
| Composite actions | `action1 + action2` | `composite.geo` |
| Signals | `EMIT name`, `signal=name` | `signal_wave.geo` |
| Voting | `PLURALITY [N]` | `vote_example.geo` |
| Probability | `random<prob` | `stochastic.geo` |
| Variables | `SET_VAR`, `INCR_VAR` | `heat_spread.geo` |
| Neighbor reads | `nb_N=`, `nb_count=` | `nb_spread.geo` |

---

## Learning Path

1. **Start:** `mask_set.geo` - Basic conditions
2. **Next:** `depth_layers.geo` - Depth stratification
3. **Then:** `composite.geo` - Action chaining
4. **Advanced:** `signal_wave.geo` - Communication
5. **Expert:** `vote_example.geo` - Program voting

---

## See Also

- [GEO_LANGUAGE.md](../GEO_LANGUAGE.md) - Full language reference
- `basics/` - Introductory examples
- `neural/` - Neural network implementations

---

**Master the `.geo` language!** 📖✨
