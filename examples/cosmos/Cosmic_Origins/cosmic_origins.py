#!/usr/bin/env python3
"""
Cosmic Origins - Complete 4X Space Strategy Game
=================================================
A comprehensive demonstration of .geo for complex game systems.

Features:
  - Multi-faction territory control (Player + 3 AI personalities)
  - Economic production and resource management
  - Combat resolution with battle mechanics
  - AI decision trees and behavior scripting
  - Random events (pirates, supernovae, resource booms)
  - Technology progression system
  - Special system types (shipyards, gateways, anomalies, ruins)
  - Victory conditions and scoring

Controls:
  - Left Click: Select system / Send fleets
  - Right Click: Cancel selection / Deselect
  - Space: Pause/Resume
  - R: Restart game
  - H: Toggle help overlay
  - M: Toggle minimap
  - T: Toggle tech tree
  - E: Toggle events log
  - +/-: Adjust simulation speed
  - Esc: Quit

Run: python cosmic_origins.py
"""

import sys
import os
import math
import random
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
from collections import deque
import time

# Add project root directory for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("Error: pygame required. Install with: pip install pygame")
    sys.exit(1)

# Import .geo interpreter from src package
try:
    from src import (
        parse_geo_script, load_geo, validate_geo,
        Node, expand_active, mask_quadrants,
        GATES, Y_LOOP, X_LOOP, Z_LOOP, DIAG_LOOP,
        _FAMILY_RGB, next_mask, Grid, draw_grid_frame, family_of
    )
    HAS_GEO = True
except ImportError:
    HAS_GEO = False
    print("Warning: src package not available. Running in standalone mode.")


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Window settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 60

# Faction colors (R, G, B)
FACTION_COLORS = {
    'neutral': (120, 120, 130),
    'player': (80, 140, 255),
    'ai_aggro': (255, 80, 80),
    'ai_econ': (255, 220, 80),
    'ai_defense': (80, 220, 100),
    'contested': (255, 140, 60),
    'warzone': (255, 50, 50),
    'resource': (100, 255, 180),
    'fortified': (180, 100, 255),
    'capital': (255, 215, 0),
    'shipyard': (100, 200, 255),
    'research': (180, 150, 255),
    'gateway': (0, 255, 255),
    'anomaly': (255, 0, 255),
    'ruins': (255, 180, 50),
}

# System type indicators
SYSTEM_TYPES = {
    'neutral': {'hp': 25, 'production': 3, 'ships': 5},
    'resource': {'hp': 40, 'production': 4, 'resources': 60},
    'fortified': {'hp': 200, 'production': 10, 'ships': 15},
    'capital': {'hp': 200, 'production': 15, 'ships': 30},
    'shipyard': {'hp': 150, 'production': 8, 'ship_production': 5},
    'research': {'hp': 80, 'production': 5, 'tech': 0},
    'gateway': {'hp': 100, 'production': 6},
    'anomaly': {'hp': 50, 'production': 3},
    'ruins': {'hp': 300, 'production': 20},
}

# AI Personalities
class AIPersonality(Enum):
    AGGRESSIVE = "aggressive"
    ECONOMIC = "economic"
    DEFENSIVE = "defensive"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StarSystem:
    """Represents a star system in the galaxy."""
    id: int
    x: float
    y: float
    faction: str = 'neutral'
    system_type: str = 'neutral'
    hp: int = 25
    max_hp: int = 100
    ships: int = 5
    production: int = 3
    resources: int = 0
    max_resources: int = 200
    tech: int = 0
    max_tech: int = 100
    ship_production: int = 0
    age: int = 0
    battle_timer: int = 0
    battle_strength: int = 0
    expansion_timer: int = 0
    anomaly_timer: int = 0
    ruins_claimed: bool = False
    tech_tier: int = 0
    ai_state: int = 0
    score: int = 0
    radius: int = 30
    connections: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        # Set base stats based on system type
        if self.system_type in SYSTEM_TYPES:
            stats = SYSTEM_TYPES[self.system_type]
            for key, value in stats.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            if self.system_type == 'capital':
                self.max_hp = 500
            elif self.system_type == 'fortified':
                self.max_hp = 300
            elif self.system_type == 'shipyard':
                self.max_hp = 250
            elif self.system_type == 'ruins':
                self.max_hp = 400
            else:
                self.max_hp = self.hp * 2
    
    @property
    def display_color(self) -> Tuple[int, int, int]:
        """Get the display color for this system."""
        if self.battle_timer > 0:
            if self.battle_strength >= 25:
                return FACTION_COLORS['warzone']
            return FACTION_COLORS['contested']
        return FACTION_COLORS.get(self.system_type, FACTION_COLORS.get(self.faction, (255, 255, 255)))
    
    @property
    def border_color(self) -> Tuple[int, int, int]:
        """Get the border color based on faction."""
        return FACTION_COLORS.get(self.faction, (255, 255, 255))
    
    @property
    def is_owned(self) -> bool:
        """Check if system is owned by a faction."""
        return self.faction in ('player', 'ai_aggro', 'ai_econ', 'ai_defense')
    
    @property
    def is_enemy(self, current_faction: str = 'player') -> bool:
        """Check if system is owned by an enemy."""
        return self.is_owned and self.faction != current_faction
    
    def produce(self, tick: int):
        """Handle production for this system."""
        if self.faction == 'neutral':
            if tick % 30 == 0:
                self.ships = min(self.ships + 1, 10)
                self.hp = min(self.hp + 2, self.max_hp)
            return
        
        # Basic ship production
        production_rate = max(1, 60 // self.production)
        if tick % production_rate == 0:
            self.ships = min(self.ships + 1, 99)
        
        # Resource generation
        if self.system_type == 'resource' and tick % 15 == 0:
            self.resources = min(self.resources + 8, self.max_resources)
        
        # Shipyard production
        if self.system_type == 'shipyard' and tick % 10 == 0 and self.ship_production > 0:
            self.ships = min(self.ships + 3, 99)
        
        # Research generation
        if self.system_type == 'research' and tick % 20 == 0:
            self.tech = min(self.tech + 5, self.max_tech)
        
        # Capital bonus
        if self.system_type == 'capital' and tick % 8 == 0:
            self.ships = min(self.ships + 2, 99)
            self.resources = min(self.resources + 5, self.max_resources)
        
        # Fortified regeneration
        if self.system_type == 'fortified' and tick % 12 == 0 and self.hp < self.max_hp:
            self.hp = min(self.hp + 8, self.max_hp)


@dataclass
class Fleet:
    """Represents a fleet traveling between systems."""
    id: int
    x: float
    y: float
    target_x: float
    target_y: float
    ships: int
    faction: str
    target_system_id: int
    speed: float = 2.0
    source_system_id: Optional[int] = None
    
    def update(self) -> bool:
        """Update fleet position. Returns True if arrived."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist < self.speed:
            self.x = self.target_x
            self.y = self.target_y
            return True
        
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed
        return False
    
    def draw(self, screen: pygame.Surface):
        """Draw the fleet."""
        color = FACTION_COLORS.get(self.faction, (255, 255, 255))
        
        # Draw trail
        alpha = min(150, int(100 * (self.ships / 50)))
        trail_surf = pygame.Surface((int(abs(self.target_x - self.x)) + 10, 4), pygame.SRCALPHA)
        pygame.draw.line(trail_surf, (*color, alpha), (5, 2), 
                        (int(abs(self.target_x - self.x)) + 5, 2), 2)
        
        # Draw fleet ships (triangle formation)
        for i in range(min(self.ships, 15)):
            offset_x = (i % 4) * 8 - 12
            offset_y = (i // 4) * 8 - 8
            points = [
                (self.x + offset_x, self.y + offset_y - 6),
                (self.x + offset_x - 5, self.y + offset_y + 6),
                (self.x + offset_x + 5, self.y + offset_y + 6),
            ]
            pygame.draw.polygon(screen, color, points)


@dataclass
class GameEvent:
    """Represents a game event for the event log."""
    tick: int
    message: str
    event_type: str = 'info'
    
    @property
    def color(self) -> Tuple[int, int, int]:
        if self.event_type == 'combat':
            return (255, 100, 100)
        elif self.event_type == 'economy':
            return (100, 255, 100)
        elif self.event_type == 'disaster':
            return (255, 50, 50)
        elif self.event_type == 'bonus':
            return (255, 215, 0)
        return (200, 200, 200)


# ═══════════════════════════════════════════════════════════════════════════════
# GALAXY GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class GalaxyGenerator:
    """Generates galaxy maps with systems and connections."""
    
    def __init__(self, width: int, height: int, num_systems: int = 50):
        self.width = width
        self.height = height
        self.num_systems = num_systems
        self.system_id_counter = 0
    
    def generate(self, seed: Optional[int] = None) -> List[StarSystem]:
        """Generate a complete galaxy."""
        if seed is not None:
            random.seed(seed)
        
        systems = []
        self.system_id_counter = 0
        
        # Generate faction starting positions
        systems.extend(self._generate_capitals())
        
        # Generate regular systems
        systems.extend(self._generate_systems(35))
        
        # Generate special systems
        systems.extend(self._generate_special_systems())
        
        # Generate connections (hyperlanes)
        self._generate_connections(systems)
        
        return systems
    
    def _generate_capitals(self) -> List[StarSystem]:
        """Generate faction capital systems."""
        capitals = []
        positions = [
            (self.width * 0.2, self.height * 0.5, 'player'),
            (self.width * 0.8, self.height * 0.5, 'ai_aggro'),
            (self.width * 0.5, self.height * 0.2, 'ai_econ'),
            (self.width * 0.5, self.height * 0.8, 'ai_defense'),
        ]
        
        for x, y, faction in positions:
            # Add some randomness to positions
            x += random.uniform(-50, 50)
            y += random.uniform(-50, 50)
            
            system = StarSystem(
                id=self.system_id_counter,
                x=x, y=y,
                faction=faction,
                system_type='capital',
                hp=500,
                ships=50,
                production=20,
                resources=150,
                radius=45
            )
            capitals.append(system)
            self.system_id_counter += 1
        
        return capitals
    
    def _generate_systems(self, count: int) -> List[StarSystem]:
        """Generate regular star systems."""
        systems = []
        attempts = 0
        max_attempts = count * 10
        
        while len(systems) < count and attempts < max_attempts:
            x = random.uniform(self.width * 0.1, self.width * 0.9)
            y = random.uniform(self.height * 0.1, self.height * 0.9)
            
            # Check minimum distance from other systems
            too_close = False
            for s in systems:
                dist = math.hypot(x - s.x, y - s.y)
                if dist < 80:
                    too_close = True
                    break
            
            if not too_close:
                # Determine system type
                roll = random.random()
                if roll < 0.50:
                    system_type = 'neutral'
                elif roll < 0.70:
                    system_type = 'resource'
                elif roll < 0.85:
                    system_type = 'neutral'
                else:
                    system_type = 'neutral'
                
                system = StarSystem(
                    id=self.system_id_counter,
                    x=x, y=y,
                    faction='neutral',
                    system_type=system_type,
                    hp=random.randint(20, 40),
                    ships=random.randint(3, 10),
                    radius=random.randint(25, 35)
                )
                systems.append(system)
                self.system_id_counter += 1
            
            attempts += 1
        
        return systems
    
    def _generate_special_systems(self) -> List[StarSystem]:
        """Generate special system types."""
        specials = []
        
        # Fortified systems
        for _ in range(4):
            x, y = self._find_valid_position(specials, min_dist=100)
            system = StarSystem(
                id=self.system_id_counter,
                x=x, y=y,
                faction='neutral',
                system_type='fortified',
                hp=200,
                ships=15,
                radius=38
            )
            specials.append(system)
            self.system_id_counter += 1
        
        # Shipyards
        for _ in range(3):
            x, y = self._find_valid_position(specials, min_dist=120)
            system = StarSystem(
                id=self.system_id_counter,
                x=x, y=y,
                faction='neutral',
                system_type='shipyard',
                hp=150,
                ships=10,
                ship_production=5,
                radius=35
            )
            specials.append(system)
            self.system_id_counter += 1
        
        # Research stations
        for _ in range(4):
            x, y = self._find_valid_position(specials, min_dist=100)
            system = StarSystem(
                id=self.system_id_counter,
                x=x, y=y,
                faction='neutral',
                system_type='research',
                hp=80,
                radius=30
            )
            specials.append(system)
            self.system_id_counter += 1
        
        # Gateways
        for _ in range(2):
            x, y = self._find_valid_position(specials, min_dist=150)
            system = StarSystem(
                id=self.system_id_counter,
                x=x, y=y,
                faction='neutral',
                system_type='gateway',
                hp=100,
                radius=32
            )
            specials.append(system)
            self.system_id_counter += 1
        
        # Anomalies
        for _ in range(3):
            x, y = self._find_valid_position(specials, min_dist=100)
            system = StarSystem(
                id=self.system_id_counter,
                x=x, y=y,
                faction='neutral',
                system_type='anomaly',
                hp=50,
                radius=28
            )
            specials.append(system)
            self.system_id_counter += 1
        
        # Ancient ruins
        x, y = self._find_valid_position(specials, min_dist=200)
        system = StarSystem(
            id=self.system_id_counter,
            x=x, y=y,
            faction='neutral',
            system_type='ruins',
            hp=300,
            radius=40
        )
        specials.append(system)
        self.system_id_counter += 1
        
        return specials
    
    def _find_valid_position(self, systems: List[StarSystem], min_dist: float = 80) -> Tuple[float, float]:
        """Find a valid position for a new system."""
        for _ in range(100):
            x = random.uniform(self.width * 0.1, self.width * 0.9)
            y = random.uniform(self.height * 0.1, self.height * 0.9)
            
            too_close = False
            for s in systems:
                dist = math.hypot(x - s.x, y - s.y)
                if dist < min_dist:
                    too_close = True
                    break
            
            if not too_close:
                return x, y
        
        # Fallback to any position
        return (random.uniform(self.width * 0.1, self.width * 0.9),
                random.uniform(self.height * 0.1, self.height * 0.9))
    
    def _generate_connections(self, systems: List[StarSystem]):
        """Generate hyperlane connections between systems."""
        # Create minimum spanning tree-like connections
        unconnected = set(s.id for s in systems)
        connected = set()
        
        # Start from a random system
        start_id = random.choice(list(unconnected))
        connected.add(start_id)
        unconnected.remove(start_id)
        
        systems_by_id = {s.id: s for s in systems}
        
        while unconnected:
            # Find closest pair between connected and unconnected
            min_dist = float('inf')
            best_pair = None
            
            for c_id in connected:
                c_sys = systems_by_id[c_id]
                for u_id in unconnected:
                    u_sys = systems_by_id[u_id]
                    dist = math.hypot(c_sys.x - u_sys.x, c_sys.y - u_sys.y)
                    if dist < min_dist:
                        min_dist = dist
                        best_pair = (c_id, u_id)
            
            if best_pair:
                c_id, u_id = best_pair
                systems_by_id[c_id].connections.append(u_id)
                systems_by_id[u_id].connections.append(c_id)
                connected.add(u_id)
                unconnected.remove(u_id)
        
        # Add some extra connections for cycles
        extra_connections = len(systems) // 4
        for _ in range(extra_connections):
            s1 = random.choice(systems)
            s2 = random.choice(systems)
            if s1.id != s2.id and s2.id not in s1.connections:
                dist = math.hypot(s1.x - s2.x, s1.y - s2.y)
                if dist < 300:  # Only connect relatively close systems
                    s1.connections.append(s2.id)
                    s2.connections.append(s1.id)


# ═══════════════════════════════════════════════════════════════════════════════
# AI CONTROLLER
# ═══════════════════════════════════════════════════════════════════════════════

class AIController:
    """Controls AI faction behavior."""
    
    def __init__(self, faction: str, personality: AIPersonality):
        self.faction = faction
        self.personality = personality
        self.decision_cooldown = 0
        self.target_system: Optional[int] = None
        self.defense_priority: Dict[int, int] = {}
    
    def decide(self, systems: List[StarSystem], fleets: List[Fleet], tick: int) -> List[dict]:
        """Make AI decisions. Returns list of actions."""
        if self.decision_cooldown > 0:
            self.decision_cooldown -= 1
            return []
        
        actions = []
        my_systems = [s for s in systems if s.faction == self.faction]
        
        if not my_systems:
            return actions
        
        # Get enemy systems
        enemy_systems = [s for s in systems if s.is_owned and s.faction != self.faction]
        neutral_systems = [s for s in systems if s.faction == 'neutral']
        
        # Personality-based decisions
        if self.personality == AIPersonality.AGGRESSIVE:
            actions.extend(self._aggro_decision(my_systems, enemy_systems, neutral_systems, systems))
        elif self.personality == AIPersonality.ECONOMIC:
            actions.extend(self._econ_decision(my_systems, enemy_systems, neutral_systems, systems))
        elif self.personality == AIPersonality.DEFENSIVE:
            actions.extend(self._defense_decision(my_systems, enemy_systems, neutral_systems, systems))
        
        self.decision_cooldown = random.randint(20, 40)
        return actions
    
    def _aggro_decision(self, my_systems, enemy_systems, neutral_systems, all_systems) -> List[dict]:
        """Aggressive AI: prioritize attacks."""
        actions = []
        
        # Look for attack opportunities
        for sys in my_systems:
            if sys.ships >= 20:
                # Find nearby enemy
                for enemy in enemy_systems:
                    dist = math.hypot(sys.x - enemy.x, sys.y - enemy.y)
                    if dist < 200 and enemy.ships < sys.ships * 0.7:
                        actions.append({
                            'type': 'attack',
                            'source': sys.id,
                            'target': enemy.id,
                            'ships': sys.ships // 2
                        })
                        return actions
        
        # Expand to neutral
        for sys in my_systems:
            if sys.ships >= 10:
                for neutral in neutral_systems:
                    dist = math.hypot(sys.x - neutral.x, sys.y - neutral.y)
                    if dist < 150 and neutral.ships < sys.ships * 0.5:
                        actions.append({
                            'type': 'expand',
                            'source': sys.id,
                            'target': neutral.id,
                            'ships': 8
                        })
                        return actions
        
        # Build ships if no targets
        for sys in my_systems:
            if sys.ships < 15:
                actions.append({'type': 'build', 'system': sys.id})
        
        return actions
    
    def _econ_decision(self, my_systems, enemy_systems, neutral_systems, all_systems) -> List[dict]:
        """Economic AI: prioritize resources."""
        actions = []
        
        # Capture resource systems
        for sys in my_systems:
            if sys.ships >= 12:
                for neutral in neutral_systems:
                    if neutral.system_type == 'resource':
                        dist = math.hypot(sys.x - neutral.x, sys.y - neutral.y)
                        if dist < 180:
                            actions.append({
                                'type': 'expand',
                                'source': sys.id,
                                'target': neutral.id,
                                'ships': 10
                            })
                            return actions
        
        # Expand safely
        for sys in my_systems:
            if sys.ships >= 15:
                for neutral in neutral_systems:
                    dist = math.hypot(sys.x - neutral.x, sys.y - neutral.y)
                    if dist < 150 and neutral.ships < 8:
                        actions.append({
                            'type': 'expand',
                            'source': sys.id,
                            'target': neutral.id,
                            'ships': 10
                        })
                        return actions
        
        # Build economy
        for sys in my_systems:
            if sys.system_type in ('resource', 'research', 'shipyard'):
                if sys.ships < 20:
                    actions.append({'type': 'build', 'system': sys.id})
        
        return actions
    
    def _defense_decision(self, my_systems, enemy_systems, neutral_systems, all_systems) -> List[dict]:
        """Defensive AI: prioritize fortification."""
        actions = []
        
        # Fortify border systems
        for sys in my_systems:
            has_enemy_neighbor = False
            for enemy in enemy_systems:
                dist = math.hypot(sys.x - enemy.x, sys.y - enemy.y)
                if dist < 150:
                    has_enemy_neighbor = True
                    break
            
            if has_enemy_neighbor and sys.ships >= 15:
                actions.append({'type': 'fortify', 'system': sys.id, 'ships': 10})
                return actions
        
        # Safe expansion
        for sys in my_systems:
            if sys.ships >= 12:
                for neutral in neutral_systems:
                    dist = math.hypot(sys.x - neutral.x, sys.y - neutral.y)
                    # Only expand to systems not near enemies
                    safe = True
                    for enemy in enemy_systems:
                        enemy_dist = math.hypot(neutral.x - enemy.x, neutral.y - enemy.y)
                        if enemy_dist < 100:
                            safe = False
                            break
                    
                    if dist < 120 and safe and neutral.ships < 8:
                        actions.append({
                            'type': 'expand',
                            'source': sys.id,
                            'target': neutral.id,
                            'ships': 10
                        })
                        return actions
        
        # Build defense
        for sys in my_systems:
            if sys.ships < 20:
                actions.append({'type': 'build', 'system': sys.id})
        
        return actions


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GAME CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class CosmicOriginsGame:
    """Main game class."""
    
    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.systems: List[StarSystem] = []
        self.fleets: List[Fleet] = []
        self.events: deque = deque(maxlen=100)
        self.selected_system: Optional[StarSystem] = None
        self.hovered_system: Optional[StarSystem] = None
        self.paused = False
        self.tick = 0
        self.game_over = False
        self.winner = None
        self.show_help = True
        self.show_minimap = True
        self.show_tech = False
        self.show_events = True
        self.sim_speed = 1.0
        self.fleet_id_counter = 0
        self.system_id_counter = 0
        
        # AI controllers
        self.ai_controllers: Dict[str, AIController] = {
            'ai_aggro': AIController('ai_aggro', AIPersonality.AGGRESSIVE),
            'ai_econ': AIController('ai_econ', AIPersonality.ECONOMIC),
            'ai_defense': AIController('ai_defense', AIPersonality.DEFENSIVE),
        }
        
        # Game state
        self.player_resources = 0
        self.player_tech = 0
        self.global_events: Dict[str, int] = {}
        
        # .geo program (if loaded)
        self.geo_program = None
        self.use_geo = HAS_GEO
        
        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Cosmic Origins - 4X Space Strategy (.geo Demo)")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        
        # Generate galaxy
        self._new_game()
        
        # Try to load .geo script
        self._load_geo_script()
    
    def _load_geo_script(self):
        """Load the .geo script if available."""
        geo_path = os.path.join(os.path.dirname(__file__), 'cosmic_origins.geo')
        if os.path.exists(geo_path):
            try:
                with open(geo_path, 'r') as f:
                    script = f.read()
                
                errors = validate_geo(script)
                if errors:
                    self._log_event(f"Geo script has {len(errors)} warnings", 'info')
                
                self.geo_program = parse_geo_script(script)
                self._log_event("Loaded cosmic_origins.geo", 'bonus')
            except Exception as e:
                self._log_event(f"Failed to load .geo: {e}", 'info')
                self.use_geo = False
    
    def _new_game(self):
        """Start a new game."""
        generator = GalaxyGenerator(self.width, self.height, num_systems=50)
        self.systems = generator.generate()
        self.system_id_counter = len(self.systems)
        self.fleets = []
        self.events.clear()
        self.tick = 0
        self.game_over = False
        self.winner = None
        self.selected_system = None
        self.player_resources = 0
        self.player_tech = 0
        self.global_events = {}
        
        self._log_event("Galaxy generated - Conquest begins!", 'info')
    
    def _log_event(self, message: str, event_type: str = 'info'):
        """Log a game event."""
        self.events.append(GameEvent(self.tick, message, event_type))
    
    def update(self, dt: float = 1.0):
        """Update game state."""
        if self.paused or self.game_over:
            return
        
        self.tick += 1
        
        # Update systems
        for system in self.systems:
            system.produce(self.tick)
            system.age += 1
            
            # Battle timer
            if system.battle_timer > 0:
                system.battle_timer -= 1
                if system.battle_timer <= 0:
                    self._resolve_battle(system)
            
            # Anomaly effects
            if system.system_type == 'anomaly' and self.tick % 50 == 0:
                self._trigger_anomaly(system)
        
        # Update fleets
        arrived = []
        for fleet in self.fleets:
            if fleet.update():
                arrived.append(fleet)
        
        for fleet in arrived:
            self._handle_fleet_arrival(fleet)
            self.fleets.remove(fleet)
        
        # AI decisions
        if self.tick % 30 == 0:
            self._update_ai()
        
        # Random events
        self._update_global_events()
        
        # Check win condition
        self._check_win_condition()
    
    def _trigger_anomaly(self, system: StarSystem):
        """Trigger anomaly effects."""
        roll = random.random()
        if roll < 0.33:
            system.ships = min(system.ships + 20, 99)
            system.resources = min(system.resources + 50, system.max_resources)
            self._log_event(f"Anomaly bonus at system {system.id}!", 'bonus')
        elif roll < 0.66:
            system.tech = min(system.tech + 25, system.max_tech)
            system.production += 2
            self._log_event(f"Anomaly discovery at system {system.id}!", 'bonus')
        else:
            system.hp = 10
            system.ships = 0
            self._log_event(f"Anomaly disaster at system {system.id}!", 'disaster')
    
    def _resolve_battle(self, system: StarSystem):
        """Resolve battle at a system."""
        if system.hp >= 60:
            # Attacker won
            if system.faction == 'player':
                # Find attacking fleet's faction
                for fleet in self.fleets:
                    if fleet.target_system_id == system.id and fleet.faction != 'player':
                        system.faction = fleet.faction
                        system.ships = 15
                        self._log_event(f"System {system.id} lost to {fleet.faction}!", 'combat')
                        break
            else:
                system.faction = 'player'
                system.ships = 15
                self._log_event(f"System {system.id} captured!", 'bonus')
        elif system.hp <= 30:
            # Defender won or stalemate
            system.ships = max(3, system.ships // 2)
            system.hp = 20
            self._log_event(f"Battle at system {system.id} ended in stalemate", 'combat')
        else:
            system.ships = max(5, system.ships // 2)
            self._log_event(f"Battle at system {system.id} continues", 'combat')
        
        system.battle_timer = 0
        system.battle_strength = 0
    
    def _handle_fleet_arrival(self, fleet: Fleet):
        """Handle fleet arriving at target."""
        target = next((s for s in self.systems if s.id == fleet.target_system_id), None)
        if not target:
            return
        
        if target.faction == fleet.faction:
            # Reinforce
            target.ships = min(target.ships + fleet.ships, 99)
        else:
            # Attack
            damage = fleet.ships * 5
            target.hp -= damage
            target.battle_timer = 30
            target.battle_strength = max(target.battle_strength, fleet.ships)
            
            if target.hp <= 0:
                # System captured
                old_faction = target.faction
                target.faction = fleet.faction
                target.hp = target.max_hp // 2
                target.ships = fleet.ships // 2
                self._log_event(f"System {target.id} captured from {old_faction}!", 'combat')
            else:
                target.ships = max(0, target.ships - fleet.ships)
                self._log_event(f"Fleet engages at system {target.id}", 'combat')
    
    def _update_ai(self):
        """Update AI controllers."""
        for faction, controller in self.ai_controllers.items():
            actions = controller.decide(self.systems, self.fleets, self.tick)
            
            for action in actions:
                if action['type'] == 'attack':
                    self._ai_send_fleet(action['source'], action['target'], action['ships'], faction)
                elif action['type'] == 'expand':
                    self._ai_send_fleet(action['source'], action['target'], action['ships'], faction)
                elif action['type'] == 'build':
                    sys = next((s for s in self.systems if s.id == action['system']), None)
                    if sys:
                        sys.ships = min(sys.ships + 5, 99)
                elif action['type'] == 'fortify':
                    sys = next((s for s in self.systems if s.id == action['system']), None)
                    if sys:
                        sys.hp = min(sys.hp + 50, sys.max_hp)
                        sys.ships = min(sys.ships + action.get('ships', 10), 99)
    
    def _ai_send_fleet(self, source_id: int, target_id: int, ships: int, faction: str):
        """Send AI fleet."""
        source = next((s for s in self.systems if s.id == source_id), None)
        target = next((s for s in self.systems if s.id == target_id), None)
        
        if source and target and source.ships >= ships:
            source.ships -= ships
            fleet = Fleet(
                id=self.fleet_id_counter,
                x=source.x, y=source.y,
                target_x=target.x, target_y=target.y,
                ships=ships,
                faction=faction,
                target_system_id=target.id,
                source_system_id=source.id
            )
            self.fleets.append(fleet)
            self.fleet_id_counter += 1
    
    def _update_global_events(self):
        """Update global events (pirates, supernovae, etc.)."""
        # Pirate raids
        if self.tick % 200 == 100 and random.random() < 0.4:
            self.global_events['pirate'] = 50
            self._log_event("Pirate activity detected!", 'disaster')
        
        if self.global_events.get('pirate', 0) > 0:
            self.global_events['pirate'] -= 1
            if self.global_events['pirate'] == 1:
                # Apply pirate damage
                player_systems = [s for s in self.systems if s.faction == 'player']
                if player_systems and random.random() < 0.5:
                    target = random.choice(player_systems)
                    target.ships = max(0, target.ships - 10)
                    target.resources = max(0, target.resources - 30)
                    self._log_event(f"Pirates raided system {target.id}!", 'disaster')
        
        # Supernova
        if self.tick % 300 == 150 and random.random() < 0.2:
            self.global_events['supernova'] = 30
            self._log_event("Supernova imminent!", 'disaster')
        
        if self.global_events.get('supernova', 0) > 0:
            self.global_events['supernova'] -= 1
            if self.global_events['supernova'] == 1:
                # Destroy random system
                targets = [s for s in self.systems if s.faction == 'neutral']
                if targets:
                    target = random.choice(targets)
                    target.hp = 5
                    target.ships = 0
                    self._log_event(f"Supernova destroyed system {target.id}!", 'disaster')
        
        # Resource boom
        if self.tick % 250 == 100 and random.random() < 0.35:
            self.global_events['boom'] = 40
            self._log_event("Resource boom detected!", 'bonus')
        
        if self.global_events.get('boom', 0) > 0:
            self.global_events['boom'] -= 1
            resource_systems = [s for s in self.systems if s.system_type == 'resource']
            for sys in resource_systems:
                sys.resources = min(sys.resources + 15, sys.max_resources)
    
    def _check_win_condition(self):
        """Check for victory conditions."""
        player_count = sum(1 for s in self.systems if s.faction == 'player')
        ai_aggro_count = sum(1 for s in self.systems if s.faction == 'ai_aggro')
        ai_econ_count = sum(1 for s in self.systems if s.faction == 'ai_econ')
        ai_defense_count = sum(1 for s in self.systems if s.faction == 'ai_defense')
        
        if player_count == 0:
            self.game_over = True
            self.winner = 'enemy'
            self._log_event("DEFEAT - All player systems lost!", 'disaster')
        elif ai_aggro_count == 0 and ai_econ_count == 0 and ai_defense_count == 0:
            self.game_over = True
            self.winner = 'player'
            self._log_event("VICTORY - All enemies defeated!", 'bonus')
    
    def draw(self):
        """Render the game."""
        # Background
        self.screen.fill((10, 10, 30))
        
        # Draw connections (hyperlanes)
        self._draw_connections()
        
        # Draw fleets
        for fleet in self.fleets:
            fleet.draw(self.screen)
        
        # Draw systems
        for system in self.systems:
            self._draw_system(system)
        
        # Draw UI
        self._draw_ui()
        
        # Draw overlays
        if self.show_help and not self.game_over:
            self._draw_help()
        
        if self.show_minimap:
            self._draw_minimap()
        
        if self.show_tech:
            self._draw_tech()
        
        if self.show_events:
            self._draw_events()
        
        pygame.display.flip()
    
    def _draw_connections(self):
        """Draw hyperlane connections."""
        for system in self.systems:
            for conn_id in system.connections:
                conn = next((s for s in self.systems if s.id == conn_id), None)
                if conn:
                    dist = math.hypot(system.x - conn.x, system.y - conn.y)
                    alpha = int(80 * (1 - dist / 400))
                    if alpha > 0:
                        color = (min(150, alpha + 50), min(150, alpha + 50), min(200, alpha + 100))
                        pygame.draw.line(self.screen, color,
                                       (int(system.x), int(system.y)),
                                       (int(conn.x), int(conn.y)), 1)
    
    def _draw_system(self, system: StarSystem):
        """Draw a star system."""
        x, y = int(system.x), int(system.y)
        color = system.display_color
        border_color = system.border_color
        
        # Selection glow
        if system is self.selected_system:
            glow_surf = pygame.Surface((system.radius * 4, system.radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 255, 120),
                             (system.radius * 2, system.radius * 2), system.radius * 2, 4)
            self.screen.blit(glow_surf, (x - system.radius * 2, y - system.radius * 2))
        
        # Hover glow
        if system is self.hovered_system:
            glow_surf = pygame.Surface((system.radius * 3, system.radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 255, 60),
                             (int(system.radius * 1.5), int(system.radius * 1.5)), int(system.radius * 1.5), 2)
            self.screen.blit(glow_surf, (x - int(system.radius * 1.5), y - int(system.radius * 1.5)))
        
        # Main system circle
        pygame.draw.circle(self.screen, color, (x, y), system.radius)
        
        # Border
        border_width = 4 if system.system_type == 'capital' else 3
        pygame.draw.circle(self.screen, border_color, (x, y), system.radius, border_width)
        
        # System type indicator (inner circle)
        if system.system_type != 'neutral':
            inner_radius = system.radius // 3
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), inner_radius)
        
        # HP bar
        hp_pct = system.hp / system.max_hp if system.max_hp > 0 else 0
        hp_width = int(system.radius * 1.5 * hp_pct)
        pygame.draw.rect(self.screen, (80, 80, 80),
                        (x - int(system.radius * 0.75), y - system.radius - 10,
                         int(system.radius * 1.5), 5))
        pygame.draw.rect(self.screen, (0, 255, 0) if hp_pct > 0.5 else (255, 255, 0) if hp_pct > 0.25 else (255, 0, 0),
                        (x - int(system.radius * 0.75), y - system.radius - 10,
                         hp_width, 5))
        
        # Ship count
        if system.ships > 0:
            ship_text = self.font_small.render(f"{system.ships}", True, (255, 255, 255))
            self.screen.blit(ship_text, (x - ship_text.get_width()//2, y - ship_text.get_height()//2))
        
        # Battle indicator
        if system.battle_timer > 0:
            battle_text = self.font_small.render(f"⚔", True, (255, 100, 100))
            self.screen.blit(battle_text, (x + system.radius - 15, y - system.radius - 10))
    
    def _draw_ui(self):
        """Draw UI elements."""
        # Top bar stats
        player_systems = sum(1 for s in self.systems if s.faction == 'player')
        ai_systems = sum(1 for s in self.systems if s.faction in ('ai_aggro', 'ai_econ', 'ai_defense'))
        
        stats = [
            f"Tick: {self.tick}",
            f"Player: {player_systems}",
            f"Enemies: {ai_systems}",
            f"Fleets: {len(self.fleets)}",
        ]
        
        y = 10
        for stat in stats:
            surf = self.font_small.render(stat, True, (200, 200, 200))
            self.screen.blit(surf, (10, y))
            y += 24
        
        # Speed indicator
        speed_text = self.font_small.render(f"Speed: {self.sim_speed:.1f}x", True, (150, 150, 150))
        self.screen.blit(speed_text, (10, self.height - 30))
        
        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            winner_text = "VICTORY!" if self.winner == 'player' else "DEFEAT"
            color = (100, 255, 100) if self.winner == 'player' else (255, 100, 100)
            
            text = self.font_large.render(winner_text, True, color)
            text_rect = text.get_rect(center=(self.width//2, self.height//2 - 30))
            self.screen.blit(text, text_rect)
            
            restart = self.font_medium.render("Press R to Restart", True, (255, 255, 255))
            restart_rect = restart.get_rect(center=(self.width//2, self.height//2 + 20))
            self.screen.blit(restart, restart_rect)
        
        # Controls hint
        controls = "Click: Send | Right Click: Cancel | H: Help | M: Minimap | T: Tech | E: Events | +/-: Speed"
        ctrl_surf = self.font_small.render(controls, True, (120, 120, 120))
        self.screen.blit(ctrl_surf, (self.width//2 - ctrl_surf.get_width()//2, self.height - 30))
    
    def _draw_help(self):
        """Draw help overlay."""
        help_box = pygame.Rect(self.width - 300, 10, 290, 220)
        pygame.draw.rect(self.screen, (30, 30, 60), help_box)
        pygame.draw.rect(self.screen, (100, 100, 180), help_box, 2)
        
        help_text = [
            "HOW TO PLAY",
            "",
            "• Click your systems to select",
            "• Click again to send 50% of ships",
            "• Capture all enemy capitals to win",
            "",
            "SYSTEM TYPES:",
            "• Resource: Generates extra resources",
            "• Shipyard: Produces ships faster",
            "• Research: Generates technology",
            "• Fortified: Defensive bonus",
            "",
            "Press H to hide this"
        ]
        
        y = help_box.y + 10
        for line in help_text:
            color = (255, 255, 150) if line in ("HOW TO PLAY", "SYSTEM TYPES:") else (200, 200, 200)
            surf = self.font_small.render(line, True, color)
            self.screen.blit(surf, (help_box.x + 10, y))
            y += 18
    
    def _draw_minimap(self):
        """Draw minimap."""
        map_width, map_height = 200, 150
        map_x, map_y = self.width - map_width - 20, self.height - map_height - 60
        
        # Background
        pygame.draw.rect(self.screen, (20, 20, 40), (map_x, map_y, map_width, map_height))
        pygame.draw.rect(self.screen, (80, 80, 120), (map_x, map_y, map_width, map_height), 2)
        
        # Scale factor
        scale_x = map_width / self.width
        scale_y = map_height / self.height
        
        # Draw systems on minimap
        for system in self.systems:
            mx = map_x + int(system.x * scale_x)
            my = map_y + int(system.y * scale_y)
            color = FACTION_COLORS.get(system.faction, (150, 150, 150))
            pygame.draw.circle(self.screen, color, (mx, my), 2)
        
        # Draw fleets on minimap
        for fleet in self.fleets:
            mx = map_x + int(fleet.x * scale_x)
            my = map_y + int(fleet.y * scale_y)
            pygame.draw.circle(self.screen, (255, 255, 255), (mx, my), 1)
    
    def _draw_tech(self):
        """Draw tech tree panel."""
        panel_width, panel_height = 280, 200
        panel_x, panel_y = 10, self.height - panel_height - 60
        
        pygame.draw.rect(self.screen, (30, 30, 60), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 180), (panel_x, panel_y, panel_width, panel_height), 2)
        
        title = self.font_medium.render("TECHNOLOGY", True, (150, 150, 255))
        self.screen.blit(title, (panel_x + 10, panel_y + 10))
        
        # Calculate total player tech
        player_research = [s for s in self.systems if s.faction == 'player' and s.system_type == 'research']
        total_tech = sum(s.tech for s in player_research)
        
        tech_lines = [
            f"Total Research: {total_tech}",
            f"Research Stations: {len(player_research)}",
            "",
            "TIER 1: +10% production (50 tech)",
            "TIER 2: +2 ship production (100 tech)",
            "TIER 3: +50 HP (200 tech)",
        ]
        
        y = panel_y + 45
        for line in tech_lines:
            color = (200, 200, 200)
            surf = self.font_small.render(line, True, color)
            self.screen.blit(surf, (panel_x + 10, y))
            y += 20
    
    def _draw_events(self):
        """Draw event log."""
        panel_width, panel_height = 350, 180
        panel_x, panel_y = self.width // 2 - panel_width // 2, self.height - panel_height - 60
        
        pygame.draw.rect(self.screen, (30, 30, 50, 200), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 150), (panel_x, panel_y, panel_width, panel_height), 2)
        
        title = self.font_medium.render("EVENT LOG", True, (200, 200, 200))
        self.screen.blit(title, (panel_x + 10, panel_y + 10))
        
        # Show last 6 events
        y = panel_y + 35
        for event in list(self.events)[-6:]:
            surf = self.font_small.render(f"[{event.tick}] {event.message}", True, event.color)
            self.screen.blit(surf, (panel_x + 10, y))
            y += 20
    
    def handle_events(self) -> bool:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._new_game()
                    self._load_geo_script()
                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                elif event.key == pygame.K_m:
                    self.show_minimap = not self.show_minimap
                elif event.key == pygame.K_t:
                    self.show_tech = not self.show_tech
                elif event.key == pygame.K_e:
                    self.show_events = not self.show_events
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.sim_speed = min(3.0, self.sim_speed + 0.5)
                elif event.key == pygame.K_MINUS:
                    self.sim_speed = max(0.5, self.sim_speed - 0.5)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_click(event.pos)
                elif event.button == 3:  # Right click
                    self.selected_system = None
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_hover(event.pos)
        
        return True
    
    def _handle_hover(self, pos):
        """Handle mouse hover."""
        x, y = pos
        self.hovered_system = None
        
        for system in self.systems:
            dist = math.hypot(x - system.x, y - system.y)
            if dist < system.radius:
                self.hovered_system = system
                break
    
    def _handle_click(self, pos):
        """Handle mouse click."""
        x, y = pos
        
        clicked = None
        for system in self.systems:
            dist = math.hypot(x - system.x, y - system.y)
            if dist < system.radius:
                clicked = system
                break
        
        if clicked:
            if self.selected_system is None:
                if clicked.faction == 'player':
                    self.selected_system = clicked
            else:
                if clicked is not self.selected_system:
                    self._send_fleet(self.selected_system, clicked)
                self.selected_system = None
    
    def _send_fleet(self, source: StarSystem, target: StarSystem):
        """Send fleet from source to target."""
        if source.ships < 2:
            return
        
        ships_to_send = source.ships // 2
        source.ships -= ships_to_send
        
        fleet = Fleet(
            id=self.fleet_id_counter,
            x=source.x, y=source.y,
            target_x=target.x, target_y=target.y,
            ships=ships_to_send,
            faction='player',
            target_system_id=target.id,
            source_system_id=source.id
        )
        self.fleets.append(fleet)
        self.fleet_id_counter += 1
        
        self._log_event(f"Fleet sent to system {target.id}", 'info')
    
    def run(self, fps: int = FPS):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()
            self.update(dt=1.0)
            self.draw()
            self.clock.tick(fps)
        
        pygame.quit()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cosmic Origins - 4X Space Strategy")
    parser.add_argument("--width", type=int, default=WINDOW_WIDTH, help="Window width")
    parser.add_argument("--height", type=int, default=WINDOW_HEIGHT, help="Window height")
    parser.add_argument("--fps", type=int, default=FPS, help="Target FPS")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for galaxy generation")
    parser.add_argument("--no-geo", action="store_true", help="Disable .geo script loading")
    args = parser.parse_args()
    
    if args.no_geo:
        HAS_GEO = False
    
    game = CosmicOriginsGame(args.width, args.height)
    game.run(args.fps)


if __name__ == "__main__":
    main()
