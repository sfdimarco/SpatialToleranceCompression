# Simulations - Strategy & Game Systems

Game-like simulations and strategy systems using `.geo` rules.

---

## Scripts

### `ecosystem.geo`
**Type:** Ecosystem Simulation  
**Description:** Simulates predator-prey dynamics and resource competition

**Features:**
- Multiple species
- Resource consumption
- Population dynamics
- Birth/death rules

**Use for:** Ecological simulations, strategy games

---

### `faction_wars.geo`
**Type:** Faction Conflict  
**Description:** Simulates wars between competing factions

**Features:**
- Territory control
- Combat resolution
- Faction alliances
- Resource management

**Use for:** Strategy games, war simulations, 4X games

---

### `territory_conquest.geo`
**Type:** Territory Control  
**Description:** Models expansion and conquest mechanics

**Features:**
- Border expansion
- Conquest rules
- Defense mechanisms
- Victory conditions

**Use for:** RTS games, board games, conquest simulations

---

### `combat_encounters.geo`
**Type:** Encounter Generation  
**Description:** Procedural combat encounter generation

**Features:**
- Enemy composition
- Difficulty scaling
- Environmental factors
- Reward calculation

**Use for:** RPG encounters, roguelikes, procedural content

---

## Usage

```bash
# Run ecosystem simulation
python BinaryQuadTreeTest.py --geo examples/simulations/ecosystem.geo

# Run faction wars
python BinaryQuadTreeTest.py --geo examples/simulations/faction_wars.geo
```

---

## Common Patterns

### State Machines
```geo
RULE IF state=peace AND war_declared THEN SWITCH state=war
RULE IF state=war AND peace_treaty THEN SWITCH state=peace
```

### Resource Tracking
```geo
RULE IF tick%10=0 THEN INCR_VAR gold 5
RULE IF purchase THEN INCR_VAR gold -var_cost
```

### Combat Resolution
```geo
RULE IF attack AND var_strength>var_defense
     THEN GATE_ON + INCR_VAR casualties var_defense
```

---

## Design Tips

1. **Define clear states** - Use families or variables for game states
2. **Balance randomness** - Use `random<prob` for uncertainty
3. **Track resources** - Use `SET_VAR` / `INCR_VAR` for counters
4. **Create feedback** - Winners get stronger (or weaker for balance)
5. **End conditions** - Define clear victory/defeat states

---

## Integration

Combine with other systems:

| System | Integration |
|--------|-------------|
| `terrain/` | Generate battlefield terrain |
| `cellular/` | Model troop movements |
| `selforg/` | Emergent strategy patterns |

---

## See Also

- `cellular/` - Cellular automata for unit movement
- `terrain/` - Terrain for battlefields
- `cosmos/` - Large-scale simulations

---

**Build epic simulations!** 🎮⚔️
