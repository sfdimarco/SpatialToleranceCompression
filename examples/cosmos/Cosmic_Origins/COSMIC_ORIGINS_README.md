# Cosmic Origins - 4X Space Strategy Game

## A .geo Language Showcase

**Cosmic Origins** is a comprehensive 4X space strategy game (eXplore, eXpand, eXploit, eXterminate) that demonstrates the full power of the `.geo` declarative scripting language for complex game development.

---

## 🎮 Quick Start

### Running the Game

```bash
# Basic launch
python examples/cosmos/cosmic_origins.py

# With custom settings
python examples/cosmos/cosmic_origins.py --width 1920 --height 1080 --fps 60

# With specific random seed for reproducible galaxies
python examples/cosmos/cosmic_origins.py --seed 12345

# Without .geo script integration (standalone mode)
python examples/cosmos/cosmic_origins.py --no-geo
```

### Controls

| Key | Action |
|-----|--------|
| **Left Click** | Select system / Send fleets |
| **Right Click** | Cancel selection / Deselect |
| **Space** | Pause/Resume simulation |
| **R** | Restart game |
| **H** | Toggle help overlay |
| **M** | Toggle minimap |
| **T** | Toggle tech tree panel |
| **E** | Toggle event log |
| **+/-** | Adjust simulation speed |
| **Esc** | Quit game |

---

## 🌌 Game Overview

### Objective

Command your faction to galactic dominance by capturing all enemy capital systems. Expand your empire, manage resources, build your fleet, and outmaneuver three AI opponents—each with unique personalities and strategies.

### Factions

| Faction | Color | Personality | Strategy |
|---------|-------|-------------|----------|
| **Player** | Blue | Customizable | Your strategy! |
| **AI Aggressive** | Red | Warmonger | Constant attacks, prioritizes fleet size |
| **AI Economic** | Yellow | Trader | Focuses on resources and technology |
| **AI Defensive** | Green | Guardian | Fortifies positions, careful expansion |

---

## 🪐 System Types

### Basic Systems

| Type | Description | Bonus |
|------|-------------|-------|
| **Neutral** | Unclaimed space | None |
| **Capital** | Faction headquarters | +20 production, +500 HP |
| **Resource** | Mineral-rich systems | Generates extra resources |

### Special Systems

| Type | Description | Bonus |
|------|-------------|-------|
| **Fortified** | Defensive stronghold | +200 HP, defensive bonus |
| **Shipyard** | Fleet production | +5 ship production rate |
| **Research** | Technology hub | Generates tech points |
| **Gateway** | Hyperspace junction | Periodic ship bonuses |
| **Anomaly** | Mysterious phenomenon | Random effects (good or bad) |
| **Ancient Ruins** | Precursor artifacts | Major bonuses when claimed |

---

## 🎯 Gameplay Mechanics

### Economy

- **Production**: Determines ship generation rate
- **Resources**: Used for upgrades and events
- **Technology**: Unlocks tiers of bonuses

### Combat

1. **Send Fleet**: Click your system, then click target
2. **Fleet Travels**: Ships move along hyperlanes
3. **Battle Resolution**: 
   - Attacker wins if defender HP ≤ 0
   - Defender wins if attacker fleet destroyed
   - Stalemate if both sides weakened

### Victory Conditions

- **Domination Victory**: Capture all enemy capitals
- **Score Victory**: (Future) Most systems at tick 3000

---

## 📜 .geo Script Architecture

### Main Script: `cosmic_origins.geo`

The main game logic is entirely data-driven through the `.geo` script:

```
cosmic_origins.geo
├── Faction Encoding (4-bit masks)
├── Phase 1: Galaxy Generation (ticks 1-100)
├── Phase 2: Economy System
├── Phase 3: Player Faction Expansion
├── Phase 4: AI Behavior Trees
├── Phase 5: Combat Resolution
├── Phase 6: Special Systems Behavior
├── Phase 7: Diplomacy & Events
├── Phase 8: Technology System
├── Phase 9: Neutral System Dynamics
├── Phase 10: Age & Progression
└── Phase 11: Victory Conditions
```

### Module: `cosmic_ai_behaviors.geo`

Advanced AI decision-making:

```
cosmic_ai_behaviors.geo
├── Threat Assessment System
├── Strategic Priorities (0-100 scale)
├── Action Execution
├── Personality Modifiers
├── Coordinated AI (alliances)
├── Adaptive Learning
└── Late Game Escalation
```

### Module: `cosmic_events_encounters.geo`

Dynamic event system:

```
cosmic_events_encounters.geo
├── Disaster Events (supernovae, pirates, plagues)
├── Bonus Events (resource booms, breakthroughs)
├── Encounter Events (traders, refugees, mysteries)
├── Story Events (gateway awakening, great war)
├── Seasonal Events (comets, nebula drift)
└── Emergency Events (catch-up mechanics)
```

---

## 🔧 .geo Language Features Demonstrated

### 1. **Faction Encoding with 4-bit Masks**

```geo
# Base factions
0000 = Neutral
0001 = Player
0010 = AI Aggressive
0011 = AI Economic
0100 = AI Defensive
0101 = Contested

# Special types (combined)
1000 = Resource
1001 = Fortified
1010 = Capital
1011 = Shipyard
1100 = Research
1111 = Ancient Ruins
```

### 2. **Conditional Rule System**

```geo
# Complex conditions with combinators
RULE IF is_player AND var_ships>=20 AND has_enemy_nb AND random<0.20 THEN
       SET 0101 + SET_VAR battle_timer 30
       AS player_attack
```

### 3. **Variable Management**

```geo
# Setting variables
SET_VAR hp 100
SET_VAR production 15
SET_VAR ai_state 3

# Incrementing variables
INCR_VAR ships 1
INCR_VAR resources 5
INCR_VAR tech 10
```

### 4. **AI Behavior Trees**

```geo
# Threat assessment
DEFINE threat_critical  nb_count_gte=0001:4 AND var_hp_lt=30
DEFINE threat_high      nb_count_gte=0001:3 AND var_hp_lt=50

# Response rules
RULE IF threat_critical AND is_ai_aggro THEN
       SET_VAR ai_priority 100 + SET_VAR ai_action 1
       AS ai_threat_critical_aggro
```

### 5. **Event System**

```geo
# Global event timers
RULE IF tick%200=100 AND random<0.40 AND depth=0 THEN
       SET_VAR global_pirate_event 50
       AS pirate_event_start

# Event progression
RULE IF var_global_pirate_event_gte=1 AND tick%20=0 THEN
       INCR_VAR global_pirate_event -1
       AS pirate_event_active
```

### 6. **State Machines**

```geo
# AI state transitions
RULE IF (is_ai_aggro OR is_ai_econ OR is_ai_defense) AND low_hp THEN
       SET_VAR ai_state 4
       AS ai_fear_response

RULE IF (is_ai_aggro OR is_ai_econ OR is_ai_defense) AND high_ships THEN
       SET_VAR ai_state 3
       AS ai_aggression_build
```

---

## 🛠️ Modding & Extension

### Adding New System Types

1. **Define mask in cosmic_origins.geo**:
```geo
DEFINE is_black_hole  mask=1110
```

2. **Add behavior rules**:
```geo
RULE IF is_black_hole AND tick%25=0 THEN
       SET 0000 + SET_VAR ships 0
       AS black_hole_devour
```

3. **Add to Python** (`cosmic_origins.py`):
```python
SYSTEM_TYPES['black_hole'] = {'hp': 500, 'production': 0}
FACTION_COLORS['black_hole'] = (50, 0, 100)
```

### Adding New Events

1. **Create event rules** in `cosmic_events_encounters.geo`:
```geo
RULE IF tick%500=250 AND random<0.30 AND depth=0 THEN
       SET_VAR new_event 60 + SET_VAR global_event_cd 100
       AS new_event_start
```

2. **Add event effects**:
```geo
RULE IF var_new_event_gte=1 AND is_player THEN
       INCR_VAR bonus 20
       AS new_event_effect
```

### Creating AI Personalities

1. **Define personality in Python**:
```python
class AIPersonality(Enum):
    CUSTOM = "custom"
```

2. **Add behavior rules**:
```geo
RULE IF is_ai_custom AND var_ships_gte=15 THEN
       SET_VAR ai_action 8
       AS ai_custom_behavior
```

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Cosmic Origins Game                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Python GUI  │◄──►│  Game Logic  │◄──►│  AI System   │      │
│  │  (Pygame)    │    │  (Systems)   │    │  (Controllers)│     │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              .geo Script Interpreter                      │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  cosmic_origins.geo (Main Game Logic)              │  │  │
│  │  │  • Galaxy Generation                               │  │  │
│  │  │  • Economy System                                  │  │  │
│  │  │  • Combat Resolution                               │  │  │
│  │  │  • Victory Conditions                              │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  cosmic_ai_behaviors.geo (AI Module)               │  │  │
│  │  │  • Threat Assessment                               │  │  │
│  │  │  • Strategic Priorities                            │  │  │
│  │  │  • Personality System                              │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  cosmic_events_encounters.geo (Events Module)      │  │  │
│  │  │  • Disasters & Bonuses                             │  │  │
│  │  │  • Encounters & Story Events                       │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎓 Learning Objectives

This showcase demonstrates how to use `.geo` for:

1. **Data-Driven Game Design**: All game logic is scripted, not hardcoded
2. **Declarative Programming**: Rules define *what* happens, not *how*
3. **Modular Architecture**: Separate modules for AI, events, core mechanics
4. **State Management**: Variables track complex game state
5. **Event Systems**: Timed and triggered events create emergent gameplay
6. **AI Behavior Trees**: Decision trees encoded as rules
7. **Multi-Faction Systems**: 4+ factions with unique behaviors
8. **Victory Tracking**: Win conditions monitored through rules

---

## 📝 File Reference

| File | Purpose | Lines |
|------|---------|-------|
| `cosmic_origins.geo` | Main game logic | ~350 |
| `cosmic_ai_behaviors.geo` | AI decision trees | ~250 |
| `cosmic_events_encounters.geo` | Event system | ~300 |
| `cosmic_origins.py` | Python game engine | ~900 |
| `COSMIC_ORIGINS_README.md` | This documentation | - |

**Total**: ~1800 lines of game code + documentation

---

## 🚀 Performance Notes

- **Galaxy Size**: 50-60 systems recommended for smooth gameplay
- **Tick Rate**: Default 60 FPS, adjustable with +/-
- **AI Cooldown**: 20-40 ticks between decisions for performance
- **Event Frequency**: Major events every 100 ticks, minor every 50

---

## 🐛 Troubleshooting

### Game won't start
- Ensure pygame is installed: `pip install pygame`
- Check Python version: 3.7+ required

### .geo script not loading
- Verify `BinaryQuadTreeTest.py` is in project root
- Check for syntax errors in .geo files

### Performance issues
- Reduce galaxy size in `GalaxyGenerator`
- Lower FPS with `-` key
- Disable minimap/events panels (M/E keys)

---

## 📜 License

This project is provided as an educational example of .geo language capabilities.

---

## 🎮 Tips & Strategies

### For Players

1. **Early Game**: Secure nearby resource systems first
2. **Mid Game**: Fortify border systems against aggression
3. **Late Game**: Coordinate multi-front attacks on enemy capitals
4. **Economy**: Research stations provide long-term advantages
5. **Defense**: Don't overextend—keep fleets concentrated

### Understanding AI

- **Red (Aggro)**: Predictable attacks, vulnerable to counter-attacks
- **Yellow (Econ)**: Wealthy but weak militarily—pressure early
- **Green (Defense)**: Hard to dislodge—starve them instead of attacking

---

## 🔮 Future Enhancements

Potential additions to extend this showcase:

- [ ] Multiplayer support (hotseat or network)
- [ ] Additional AI personalities (tactical, diplomatic)
- [ ] More system types (starbases, mining stations)
- [ ] Technology tree UI
- [ ] Save/Load system
- [ ] Scenario editor
- [ ] Achievement system
- [ ] Tutorial campaign

---

**Cosmic Origins** demonstrates that `.geo` is capable of driving complex, multi-system games entirely through declarative scripting. The separation of game logic (in .geo) from engine code (Python) enables rapid iteration, modding, and experimentation with game mechanics.
