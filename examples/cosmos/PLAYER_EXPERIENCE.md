# Cosmic Origins - Player Experience Design

## Core Vision: FTL-Style Strategic Pacing

**"Real-time movement, turn-based decisions"**

The game runs continuously, but players engage in deliberate, meaningful choices - not twitch reflexes. Think FTL: ships move in real-time, but you pause to make every important decision.

---

## 🎮 The Player Experience (Plain English)

### **1. First 30 Seconds - The Hook**

```
You see a beautiful starfield with glowing star systems.
Your capital system pulses with blue light at the bottom.
Three enemy capitals glow in different colors around the map.

A friendly voice (text tutorial) says:
"Commander, select your capital by clicking on it."

You click. Your capital glows brighter. Orbiting rings appear.
"Good. Now click that nearby neutral system to send your fleet."

You click a gray system. 
Half your ships form up and begin traveling along a bright hyperlane.
A small particle burst marks their departure.

"Your fleet is en route. While we wait, let me explain the galaxy..."

The game continues in real-time, but there's no pressure yet.
Your ships move slowly. You have time to think.
```

**Design Goal**: Wonder, not overwhelm. Beauty, not chaos.

---

### **2. First Capture - The First Dopamine Hit**

```
Your fleet arrives at the neutral system after 3-4 seconds.
The system flashes. A small particle explosion celebrates.
The system turns BLUE (your color).

"System captured! Resources +50"

You now control 2 systems. Your ship count starts growing again.
You feel: "I did that. This is MY empire now."
```

**Design Goal**: Immediate satisfaction. Clear cause → effect.

---

### **3. First Enemy Contact - Tension Without Panic**

```
You expand toward a red (enemy) system.
Your fleet arrives. The system is occupied by red ships.

COMBAT begins - but the game PAUSES automatically.

A combat panel appears:
  "Enemy Strength: 12 ships"
  "Your Strength: 15 ships"
  "Victory Chance: 78%"

You have 3 options:
  [ATTACK] - Fight with current forces
  [RETREAT] - Pull back your fleet (lose nothing)
  [ABILITY] - Use Orbital Strike first (+50 damage)

You chose ORBITAL STRIKE (press 1).
A dramatic particle beam shoots from off-screen.
The enemy system explodes with particles.
"Enemy weakened! Victory Chance: 95%"

You press ATTACK.
Game unpauses. Your fleet engages.
After 2 seconds: "VICTORY! System captured!"

Red flashes. Big explosion. Screen shakes slightly.
"First Blood! +50 resources, +15 ships"
```

**Design Goal**: Tension through choice, not speed. Player feels tactical genius.

---

### **4. Managing Your Empire - The "One More Turn" Loop**

```
You now control 4 systems. Here's your rhythm:

┌─────────────────────────────────────────────────────────┐
│  1. CHECK your systems (which need reinforcement?)     │
│  2. CHECK your fleets (where are they going?)          │
│  3. CHECK enemies (what are they doing?)               │
│  4. MAKE ONE DECISION (send fleet, use ability, etc.) │
│  5. WATCH it play out (satisfying visuals)             │
│  6. REPEAT                                              │
└─────────────────────────────────────────────────────────┘

Each cycle takes 10-20 seconds.
You're never rushed. You can pause anytime with SPACE.
The game feels like chess with animations.
```

**Design Goal**: Deliberate pacing. Each decision matters.

---

### **5. Commander Abilities - Your "Oh Crap" Buttons**

```
You overextended. Three enemy fleets converge on your system.

Your system HP is at 30% (flashing red).
You're about to lose it.

Then you remember: "I have abilities!"

Press 4: EMERGENCY SHIELD
A blue dome particle effect envelops all your systems.
"Shields activated! +100 HP"

Your system survives. Enemy fleets retreat.
You breathe again.

But now Shield is on 90-second cooldown...
Next time, you'll be more careful.
```

**Design Goal**: Abilities save you from mistakes, not replace strategy.

---

### **6. Tech Tree - Meaningful Long-Term Choices**

```
You've captured a Research station (purple system).
Tech Points start accumulating.

Press T. The Tech Tree appears:

┌──────────────────────────────────────────────────────┐
│  TIER 1 (50 points each)                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ Advanced     │ │ Fleet        │ │ Resource     │ │
│  │ Hulls        │ │ Logistics    │ │ Scanners     │ │
│  │ +25% HP      │ │ +50% Speed   │ │ +30% Gain    │ │
│  │ [UNLOCK]     │ │ [UNLOCK]     │ │ [UNLOCK]     │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ │
└──────────────────────────────────────────────────────┘

You can only afford ONE right now.

You choose FLEET LOGISTICS.
Now your fleets move visibly faster.
You feel the upgrade immediately.

"Should I get Advanced Hulls next? Or save for Tier 2?"
```

**Design Goal**: Each tech feels impactful. Choices have trade-offs.

---

### **7. Combat - Visual Clarity Over Chaos**

```
Large battle: 5 of your fleets vs 3 enemy systems.

What you see:
- Clear fleet formations (not random dots)
- Damage numbers pop up (-15, -23, -8)
- HP bars deplete visibly
- Particle effects show hits (not obscure the view)
- Battle timer counts down (30s → 0s)

What you DON'T see:
- 50 fleets crossing everywhere
- Explosions blocking the view
- Unclear who's winning

When battle ends:
- Winner gets celebration particles
- Loser fades to gray before disappearing
- Event log clearly states: "System 12 captured from Kraggon Empire"
```

**Design Goal**: Readable combat. Player always knows who's winning.

---

### **8. AI Personalities - Learning the Enemy**

```
After 5 minutes, you notice patterns:

RED (Kraggon Empire - Aggressive):
- Always attacks when they have 20+ ships
- Predictable. You can bait them into traps.
- Weak when overextended.

YELLOW (Velari Collective - Economic):
- Captures resource systems first
- Has tons of ships later
- Weak early. Rush them!

GREEN (Sylphid Alliance - Defensive):
- Fortifies border systems
- Rarely attacks first
- Hard to dislodge. Starve them.

You start playing differently against each.
"You're predictable, Red. I'm going to destroy you."
```

**Design Goal**: AI feels distinct. Player learns and adapts.

---

### **9. Events - Stories Emerge**

```
Tick 300: "⚠ PIRATE FLEET SPOTTED"

A pirate icon appears on the map.
It moves toward your richest system.

You have 30 seconds (visible countdown) before it arrives.

Options:
- Reinforce the system (press 2)
- Move your fleet to intercept
- Let it hit, then counter-attack

You reinforce. Pirates arrive, see your defense, and leave.
"Pirates deterred! +25 reputation"

Later: "☄️ SUPERNOVA WARNING"
A red circle appears around a star.
30-second countdown.
Systems in the area will be destroyed.

You evacuate your ships just in time.
The supernova explodes (GORGEOUS particle effect).
"You saved your fleet! +50 points"
```

**Design Goal**: Events create stories, not random damage.

---

### **10. Combo System - Feeling Like a Genius**

```
You capture a system. "Combo: x1.0 → x1.5"
You capture another quickly. "Combo: x1.5 → x2.0"
Another! "Combo: x2.0 → x2.5"

Now you're thinking:
"I need to keep this going. Where's my next target?"

You spot a weak enemy system.
Send fleet. Capture it.
"COMBO MAXED! x3.0"

For the next 30 seconds, everything you earn is tripled.
You play more aggressively.
"Come on, give me one more capture before it drops!"

It drops. "Combo reset. Worth it."
```

**Design Goal**: Combo rewards aggression, creates exciting moments.

---

### **11. Losing - "My Fault, Not the Game's"

```
You lost your capital.

Why?
- You sent all ships on one attack
- Left home undefended
- Enemy counter-attacked

The game shows you:
"Capital Lost - 0 defending ships"

You don't blame the game. You blame yourself.
"I should have kept 10 ships back. My mistake."

Press R. New game starts in 1 second.
"I know what I did wrong. Let me try again."
```

**Design Goal**: Losses feel fair. Player learns, not rages.

---

### **12. Victory - The Payoff**

```
Last enemy capital falls.

The screen pauses.
All enemy systems turn gray (surrendered).

"🏆 VICTORY! 🏆"

Final Score: 2,450 points
Combo Multiplier: x2.8
Time: 12 minutes
Systems Captured: 18
Abilities Used: 12

"Press R to play again"

You pause. Look at your empire spread across the map.
You feel: "I earned this."
```

**Design Goal**: Victory feels earned. Stats show your story.

---

## 🎯 Core Gameplay Loop (The "FTL Formula")

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   REAL-TIME MOVEMENT (watch fleets travel, systems grow)   │
│           ↓                                                 │
│   EVENT TRIGGERS (fleet arrives, enemy spotted, event)     │
│           ↓                                                 │
│   AUTO-PAUSE (game pauses for decision)                    │
│           ↓                                                 │
│   PLAYER DECISION (attack, retreat, ability, tech)         │
│           ↓                                                 │
│   RESUME (watch decision play out with juicy feedback)     │
│           ↓                                                 │
│   CONSEQUENCE (system captured, battle won/lost)           │
│           ↓                                                 │
│   BACK TO START                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Key Insight: Player makes 1 decision every 10-20 seconds.
Not 10 decisions per second.
```

---

## ⏱️ Pacing Breakdown

### Early Game (0-3 minutes)
- **Speed**: Slow (fleets take 4-5 seconds to travel)
- **Decisions**: 1 every 20-30 seconds
- **Focus**: Learning, expansion, first capture
- **Pressure**: Minimal (enemies ignore you)

### Mid Game (3-8 minutes)
- **Speed**: Normal (fleets take 2-3 seconds)
- **Decisions**: 1 every 10-15 seconds
- **Focus**: Multi-front management, tech choices
- **Pressure**: Moderate (enemies contest borders)

### Late Game (8-12 minutes)
- **Speed**: Fast (fleets take 1-2 seconds)
- **Decisions**: 1 every 5-10 seconds
- **Focus**: Final push, ability timing
- **Pressure**: High (AI last stands, events)

---

## 🎨 Visual Hierarchy (What Player Sees)

### Primary Focus (Always Visible)
```
1. Your selected system (bright glow, orbit rings)
2. Your fleets in transit (trailing particles)
3. Enemy systems near your borders (red pulse)
```

### Secondary Focus (Glance at Leisure)
```
4. Top bar stats (score, combo, tick)
5. Commander abilities (cooldown status)
6. Minimap (overall situation)
```

### Tertiary Focus (When Relevant)
```
7. Event log (what happened)
8. Tech tree (when researching)
9. Help panel (when learning)
```

**Design Rule**: Never more than 3 things demanding attention at once.

---

## 🔊 Feedback Layers

### Layer 1: Immediate (0-0.5 seconds)
- Click sound (selection)
- System glow (visual confirmation)
- Fleet departure particles

### Layer 2: Short-Term (0.5-5 seconds)
- Fleet travel (visible progress)
- HP bar changes (damage/healing)
- Small particle effects (minor events)

### Layer 3: Medium-Term (5-30 seconds)
- Battle resolution (capture/defeat)
- Ability cooldowns (counting down)
- Combo building (multiple captures)

### Layer 4: Long-Term (30+ seconds)
- Tech unlocks (permanent upgrades)
- Territory changes (map state)
- Score accumulation (progress)

**Design Rule**: Each layer has distinct visual language.

---

## 🎮 Player Agency Moments

### High Agency (Player Chooses)
```
✓ Which system to capture next
✓ When to use abilities
✓ Which tech to research
✓ How many ships to send (always 50% - simple!)
✓ When to pause and plan
```

### Low Agency (Game Handles)
```
✗ Fleet movement (automatic along hyperlanes)
✗ Combat resolution (automatic based on strength)
✗ Resource generation (automatic per tick)
✗ AI behavior (personality-driven, not scripted)
✗ Event timing (random but telegraphed)
```

**Design Rule**: Player chooses strategy, game handles execution.

---

## 🧠 Cognitive Load Management

### What Player Should Think About
```
• "Which target is best right now?"
• "Should I use my ability now or save it?"
• "Do I have enough defense at home?"
• "What tech fits my strategy?"
• "How do I maintain my combo?"
```

### What Player Should NOT Think About
```
✗ "How do I send my fleet?" (click twice)
✗ "What does this button do?" (clear icons)
✗ "Who's winning this battle?" (visible HP)
✗ "Where did that event come from?" (clear source)
✗ "What should I do next?" (always obvious options)
```

**Design Rule**: Reduce friction on execution, amplify strategy.

---

## 📊 Success Metrics (How We Know It's Fun)

### Quantitative
| Metric | Target | How to Measure |
|--------|--------|----------------|
| Session Length | 10-15 min | Average play time |
| Retention | 60%+ | Players who play 3+ games |
| Victory Rate | 40-60% | Balanced difficulty |
| Ability Usage | 8+ per game | Abilities feel useful |
| Tech Unlocks | 3-5 per game | Tech tree matters |

### Qualitative
- **Smile Test**: Do players smile on first capture? ✓
- **Lean Test**: Do players lean forward during battles? ✓
- **Verbal Test**: Do players say "nice!" or "damn!"? ✓
- **Return Test**: Do players say "one more game"? ✓

---

## 🎯 Summary: The Experience in One Paragraph

> Cosmic Origins is a strategic space conquest game where you command an expanding empire in real-time with pause. You make deliberate decisions every 10-20 seconds: which systems to capture, when to use your commander abilities, which technologies to research. Fleets travel visibly along hyperlanes, battles resolve with clear visual feedback, and every action is punctuated with satisfying particle effects and screen shake. The game balances challenge with your skill level, giving you catch-up help when struggling and tougher AI when dominating. You feel like a genius tactician, not a twitch gamer. Each 10-15 minute session tells a story: your rise from a single capital to galactic dominance, punctuated by dramatic moments (pirate raids, supernovae, last stands) and crowned by a victory screen that shows your final score and combo multiplier. You immediately want to play again.

---

## 🔧 Implementation Priorities

### Must-Have (Core Experience)
1. **Auto-pause on combat** - Player never caught off-guard
2. **Clear visual hierarchy** - Always know what matters
3. **Deliberate pacing** - 10-20 seconds per decision
4. **Juicy feedback** - Particles, shake, flashes for everything
5. **Simple controls** - Click to select, click to send

### Should-Have (Polish)
6. **Tech tree** - Meaningful upgrades
7. **Commander abilities** - Active skills with cooldowns
8. **AI personalities** - Distinct faction behaviors
9. **Event system** - Random but telegraphed events
10. **Combo system** - Reward consecutive success

### Nice-to-Have (Bonus)
11. **Replay system** - Watch your best games
12. **Challenge modes** - Specific scenarios
13. **Leaderboards** - Compete for high score
14. **Custom galaxies** - Player-created maps
15. **Multiplayer** - Hotseat or online

---

## 🎬 The "Movie Trailer" Moment

```
[Camera pans across beautiful starfield]
[Your capital glows blue in the distance]

NARRATOR: "Command your fleet..."

[Fleet departs with particle trail]

NARRATOR: "...conquer the galaxy..."

[Three enemy capitals glow menacingly]

NARRATOR: "...and claim your destiny."

[Orbital Strike ability fires - dramatic beam]
[Enemy system explodes]
[VICTORY screen with score]

[Press R to Restart]

COSMIC ORIGINS
"Real-time strategy, turn-based decisions"
```

---

This is the experience we're building. Not a frantic clickfest, but a **deliberate, strategic, visually stunning** 4X game that showcases .geo's power to drive complex, beautiful simulations.
