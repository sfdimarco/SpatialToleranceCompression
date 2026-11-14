# Generative Art Scripts

Fractal patterns and generative art using `.geo` rules.

---

## Scripts

### `spiral.geo`
**Pattern:** Rotating fractal spiral  
**Technique:** Family cycling on tick intervals

```geo
RULE IF tick%8=0 THEN SWITCH Y_LOOP
RULE IF tick%8=2 THEN SWITCH X_LOOP
RULE IF tick%8=4 THEN SWITCH Z_LOOP
RULE IF tick%8=6 THEN SWITCH DIAG_LOOP
```

**Visual Effect:** Fractal rotates through different geometric families

---

### `pulse_depth.geo`
**Pattern:** Depth-based pulsing  
**Technique:** Tick thresholds + depth conditions

```geo
RULE IF tick%10=0 THEN GATE_ON
RULE IF depth>=5 THEN SWITCH Z_LOOP
```

**Visual Effect:** Concentric rings pulse on/off, deep layers lock to Z-loop

---

### `stochastic.geo`
**Pattern:** Random flashes and transitions  
**Technique:** Probabilistic rules

```geo
RULE IF random<0.3 THEN GATE_ON
RULE IF family=GATE AND random<0.5 THEN SWITCH Y_LOOP
```

**Visual Effect:** Unpredictable flashing patterns

---

### `rotate_mirror.geo`
**Pattern:** Rotated and mirrored geometry  
**Technique:** Transform actions

```geo
DEFINE is_deep depth>=3
RULE IF is_deep THEN ROTATE_CW + FLIP_H
```

**Visual Effect:** Symmetric patterns with rotation

---

## Usage

```bash
# Run spiral demo
python BinaryQuadTreeTest.py --geo examples/generative/spiral.geo

# Run stochastic demo
python BinaryQuadTreeTest.py --geo examples/generative/stochastic.geo
```

---

## Techniques

### Family Cycling
Switch between loop families on tick intervals to create rotation.

### Depth Stratification
Apply different rules at different depths for layered effects.

### Stochastic Rules
Use `random<probability` for unpredictable patterns.

### Geometric Transforms
Combine `ROTATE_CW`, `ROTATE_CCW`, `FLIP_H`, `FLIP_V` for symmetry.

---

## Tips

1. **Start simple** - Begin with `spiral.geo`
2. **Experiment with timing** - Change tick%N values
3. **Combine techniques** - Mix cycling, depth, and randomness
4. **Adjust max_depth** - Higher values = more detail

---

## See Also

- `geo_showcase/` - Language feature demonstrations
- `selforg/` - Self-organizing patterns
- `terrain/` - Terrain generation

---

**Create beautiful generative art with `.geo`!** 🎨✨
