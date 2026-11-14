# .geo Game Engine Showcase - Cosmic Origins

## Demonstrating the Power of Declarative Game Scripting

This showcase demonstrates how the `.geo` language can power a complete, engaging 4X strategy game with beautiful visuals, strategic depth, and FTL-style pacing.

---

## 🎯 What This Showcase Demonstrates

### 1. **Declarative Game Logic**
All game mechanics are defined in `.geo` scripts, not hardcoded:
- Faction behaviors
- Combat resolution
- Resource generation
- AI decision trees
- Event systems
- Victory conditions

**Why it matters**: Game designers can iterate on mechanics without touching code.

---

### 2. **Complex State Management**
The `.geo` engine tracks hundreds of variables across multiple systems:
- Per-system state (HP, ships, resources, tech)
- Global state (tick, score, combo, events)
- Faction state (territory, production, bonuses)
- Battle state (timers, strength, resolution)

**Why it matters**: Shows `.geo` can handle real game complexity.

---

### 3. **Emergent Behavior**
Simple rules combine to create complex gameplay:
- AI personalities emerge from priority weights
- Combat flows from battle timer + strength rules
- Economy emerges from production + resource rules
- Events chain together for narrative moments

**Why it matters**: Demonstrates emergence from declarative rules.

---

### 4. **Visual Feedback Driven by Game State**
Every visual effect is triggered by `.geo` state changes:
- System capture → particle explosion
- Battle start → auto-pause + UI panel
- Ability use → visual effect + cooldown
- Tech unlock → permanent bonus + visual indicator

**Why it matters**: Shows `.geo` can drive both logic AND presentation.

---

### 5. **FTL-Style Pacing**
The game runs in real-time but feels turn-based:
- Fleets move slowly (deliberate pacing)
- Auto-pause on combat (decision points)
- Auto-pause on events (meaningful choices)
- Clear visual hierarchy (readable state)

**Why it matters**: Proves real-time games can have strategic depth.

---

## 📁 File Structure

```
examples/cosmos/
├── cosmic_origins.geo          # Main game logic (730 lines, 160+ rules)
├── cosmic_ai_behaviors.geo     # AI decision trees (250 lines)
├── cosmic_events_encounters.geo # Event system (300 lines)
├── cosmic_origins.py           # Python game engine (1400 lines)
├── neural_demo.py              # Enhanced FTL-style version (1200 lines)
├── PLAYER_EXPERIENCE.md        # Player experience design doc
├── GAME_DESIGN.md              # 25 game design principles applied
├── QUICK_REFERENCE.md          # Player quick reference card
└── COSMIC_ORIGINS_README.md    # Full documentation
```

---

## 🎮 Key Game Mechanics (All .geo-Driven)

### Faction System
```geo
# 4-bit mask encoding
0000 = Neutral
0001 = Player (blue)
0010 = AI Aggressive (red)
0011 = AI Economic (yellow)
0100 = AI Defensive (green)
```

**Showcases**: Bitmask encoding, faction logic

---

### Economy System
```geo
# Resource generation
RULE IF is_resource AND tick%15=0 THEN
       INCR_VAR resources 8
       AS resource_generate

# Ship production
RULE IF is_player AND tick%10=0 THEN
       INCR_VAR ships 1
       AS basic_production
```

**Showcases**: Timed events, variable management

---

### Combat System
```geo
# Battle progression
RULE IF is_contested AND tick%5=0 THEN
       INCR_VAR battle_timer -1 + INCR_VAR hp -8
       AS battle_rage

# Battle resolution
RULE IF is_contested AND var_battle_timer<=0 AND var_hp>=50 THEN
       SET 0001
       AS player_wins
```

**Showcases**: State machines, conditional resolution

---

### AI Behavior Trees
```geo
# Threat assessment
DEFINE threat_critical  nb_count_gte=0001:4 AND var_hp_lt=30

# Response
RULE IF threat_critical AND is_ai_aggro THEN
       SET_VAR ai_priority 100 + SET_VAR ai_action 1
       AS ai_threat_critical_aggro
```

**Showcases**: Complex conditions, AI decision-making

---

### Combo System
```geo
# Combo building
RULE IF is_player AND tick%20=0 AND has_enemy_nb THEN
       INCR_VAR combo_meter 1
       AS combo_build

# Combo bonuses
RULE IF var_combo_meter_gte=20 AND is_player THEN
       INCR_VAR ships 3 + INCR_VAR production 2
       AS combo_bonus_large
```

**Showcases**: Progressive rewards, player engagement

---

### Commander Abilities
```geo
# Orbital strike support
RULE IF var_commander_strike_target_gte=1 AND has_enemy_nb THEN
       INCR_VAR hp -50 + INCR_VAR ships -10
       AS commander_strike_effect
```

**Showcases**: Player agency, active skills

---

### Dynamic Difficulty
```geo
# AI desperation (player dominating)
RULE IF var_player_score_gte=30 AND var_ai_aggro_score_lt=10 THEN
       INCR_VAR ai_aggro_production 3
       AS ai_desperation_buff

# Player catch-up (player struggling)
RULE IF var_player_score_lt=10 AND tick_gte=500 THEN
       INCR_VAR player_production 2
       AS player_catchup_help
```

**Showcases**: Flow state balancing, adaptive difficulty

---

## 🎨 Visual Features (Python-Driven, .geo-Informed)

### Particle System
- Capture celebrations (40+ particles)
- Battle effects (hit markers, explosions)
- Ability activations (strikes, shields, scans)
- Screen shake on major events

### FTL-Style Pacing
- Slow fleet movement (1.5 units/tick)
- Auto-pause on combat
- Auto-pause on events
- Clear visual hierarchy

### Readable Combat
- HP bars (color-coded)
- Battle indicators (pulsing icons)
- Fleet trails (movement tracking)
- Selection rings (orbiting particles)

---

## 🧠 Game Design Principles Applied

All **25 principles** from industry-standard game design:

### Core Psychology (5/5)
✅ Clear goals, immediate feedback  
✅ Meaningful choices  
✅ Flow state balance  
✅ Player agency  
✅ Progression visibility  

### Mechanics (5/5)
✅ Easy to learn, hard to master  
✅ Risk/reward tension  
✅ Emergent gameplay  
✅ Juicy feedback  
✅ No meaningless grind  

### Experience (5/5)
✅ Designed for emotion  
✅ Surprise & delight  
✅ Respects player time  
✅ Failure teaches  
✅ Multiple play styles  

### Pacing (5/5)
✅ Front-load fun  
✅ Peaks and valleys  
✅ Teach through play  
✅ End on high note  
✅ Playtest-driven  

### Advanced (5/5)
✅ "One more turn" factor  
✅ Player expression  
✅ Social multipliers  
✅ Novelty + familiarity  
✅ Fun is a verb  

---

## 🎯 Player Experience Journey

### Minute 1: Wonder
- Beautiful starfield appears
- Clear tutorial guidance
- First selection feels impactful
- Immediate visual feedback

### Minute 2: Agency
- First fleet sent
- First system captured
- Combo system explained
- Abilities available

### Minute 3-5: Strategy
- Multiple fronts to manage
- Tech choices appear
- AI personalities emerge
- Events create stories

### Minute 5-10: Flow
- In the zone
- Making meaningful decisions
- Combo building excitement
- Abilities on perfect cooldowns

### Minute 10-15: Climax
- Final push begins
- AI last stands
- Abilities crucial
- Victory/defeat meaningful

---

## 📊 Technical Achievements

### .geo Language Features Demonstrated

| Feature | Usage Count | Example |
|---------|-------------|---------|
| Mask encoding | 20+ | `0001`, `1010`, `1111` |
| DEFINE aliases | 30+ | `DEFINE is_player mask=0001` |
| RULE conditions | 160+ | `IF tick%10=0 AND is_player` |
| Variable ops | 100+ | `SET_VAR`, `INCR_VAR` |
| Neighbor checks | 20+ | `nb_count_gte=0001:3` |
| Probability | 15+ | `random<0.30` |
| Combinators | 50+ | `AND`, `OR`, `BUT` |
| Composite actions | 40+ | `action1 + action2` |

### Python Integration

| System | Lines | Purpose |
|--------|-------|---------|
| Particle system | 150 | Visual effects |
| Galaxy generator | 200 | Map creation |
| AI controllers | 180 | Decision making |
| Fleet system | 100 | Movement/combat |
| UI rendering | 400 | Visual interface |
| Input handling | 80 | Player controls |

---

## 🚀 Running the Showcase

### Basic Launch
```bash
python neural_demo.py
```

### With Options
```bash
python neural_demo.py --width 1920 --height 1080 --fps 60
python neural_demo.py --seed 42  # Reproducible galaxy
```

### Controls
```
Left Click    - Select / Send fleet
Right Click   - Deselect
Space         - Pause/Resume (or continue from auto-pause)
1-4           - Commander abilities
T             - Tech tree
M             - Minimap
E             - Event log
H             - Help panel
R             - Restart
Esc           - Quit
```

---

## 🎓 Learning Outcomes

After studying this showcase, you should understand:

1. **How to structure .geo scripts** for complex games
2. **How to encode game state** in 4-bit masks
3. **How to write AI behavior trees** declaratively
4. **How to create emergent gameplay** from simple rules
5. **How to balance difficulty** dynamically
6. **How to design for player engagement** (combo, abilities, tech)
7. **How to integrate .geo with Python** for visuals
8. **How to apply game design principles** systematically

---

## 🔧 Extending the Showcase

### Adding New System Types
```geo
# 1. Define mask
DEFINE is_black_hole mask=1110

# 2. Add behavior
RULE IF is_black_hole AND tick%25=0 THEN
       SET 0000 + SET_VAR ships 0
       AS black_hole_devour
```

### Adding New Abilities
```python
# In neural_demo.py
COMMANDER_ABILITIES['new_ability'] = {
    'name': 'New Ability',
    'key': '5',
    'cooldown': 60,
    'effect': '...',
}
```

### Adding New Events
```geo
RULE IF tick%500=250 AND random<0.30 THEN
       SET_VAR new_event 60
       AS new_event_start
```

---

## 📈 Performance Metrics

### Target Experience
- **Session length**: 10-15 minutes
- **Decisions per minute**: 3-6 (1 every 10-20 seconds)
- **Ability uses per game**: 8-15
- **Tech unlocks per game**: 3-5
- **Victory rate**: 40-60% (balanced)

### Visual Performance
- **FPS**: 60 (target)
- **Particles**: 200+ simultaneous
- **Fleets**: 20-40 simultaneous
- **Systems**: 50-60 total

---

## 🎬 The "Showcase Moment"

```
Player clicks their capital.
Three orbiting rings appear with a soft glow.

They click a nearby neutral system.
Half their ships form up and depart, leaving a particle trail.

The fleet travels along a bright hyperlane (3 seconds).
Game auto-pauses on arrival: "⏸ PAUSED - Combat at system 12"

Player sees:
- Enemy strength: 12 ships
- Their strength: 15 ships  
- Victory chance: 78%

They press 1 (Orbital Strike).
A dramatic particle beam shoots across the screen.
Enemy HP drops. Victory chance: 95%.

Player clicks "Continue" (Space).
Battle resolves in 2 seconds.
"VICTORY! System captured!"

Explosion of blue particles.
Screen shakes slightly.
Combo: x1.0 → x1.5

Player smiles. "Nice."

This is the power of .geo.
```

---

## 🏆 Conclusion

**Cosmic Origins** demonstrates that `.geo` is not just a toy language—it's a **powerful tool for declarative game design** that can:

- Drive complex game logic (160+ rules)
- Create emergent gameplay (AI personalities, events, combos)
- Support strategic depth (tech tree, abilities, dynamic difficulty)
- Enable rapid iteration (change .geo, not code)
- Produce beautiful visuals (particle effects, smooth animations)
- Deliver engaging player experiences (FTL-style pacing, meaningful choices)

**This is the future of game scripting.**

---

*"Fun is a verb. If your game isn't doing something engaging, it isn't fun yet."*

**Cosmic Origins** makes `.geo` fun.
