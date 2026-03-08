#!/usr/bin/env python3
"""
Cosmic Origins - A .geo-Powered Space Exploration Game
========================================================

Build and manage your galaxy while exploring star systems,
engaging in space combat, and uncovering the mysteries of the cosmos.

All game mechanics are driven by .geo scripts!

Controls:
  - Arrow Keys / WASD: Move ship
  - Space: Shoot / Action
  - E: Interact / Enter system
  - Tab: Toggle galaxy map
  - P: Pause
  - Esc: Quit

Run: python cosmic_origins.py
"""

import sys
import os
import math
import random
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# BinaryQuadTreeTest is available in the parent directory if needed
# for future .geo-driven game mechanics

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("Error: pygame required. Install with: pip install pygame")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# GAME DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Vector2:
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalized(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector2(self.x / mag, self.y / mag)
        return Vector2()


@dataclass
class GameObject:
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    radius: float = 10.0
    color: Tuple[int, int, int] = (255, 255, 255)
    health: int = 100
    max_health: int = 100
    obj_type: str = "default"
    data: Dict = field(default_factory=dict)
    alive: bool = True
    
    def update(self, dt=1.0):
        self.x += self.vx * dt
        self.y += self.vy * dt
    
    def draw(self, screen, offset=(0, 0)):
        draw_x = self.x + offset[0]
        draw_y = self.y + offset[1]
        
        # Glow effect
        glow_radius = int(self.radius * 2)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 80), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (int(draw_x) - glow_radius, int(draw_y) - glow_radius))
        
        # Core
        pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), int(self.radius))
        
        # Health bar if damaged
        if self.health < self.max_health:
            bar_width = self.radius * 2
            bar_height = 4
            health_pct = self.health / self.max_health
            pygame.draw.rect(screen, (255, 0, 0), (draw_x - bar_width/2, draw_y - self.radius - 10, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (draw_x - bar_width/2, draw_y - self.radius - 10, bar_width * health_pct, bar_height))


@dataclass
class Player(GameObject):
    def __init__(self):
        super().__init__(
            x=512, y=384,
            radius=12,
            color=(100, 200, 255),
            obj_type="player",
            data={
                "credits": 0,
                "fuel": 100,
                "scan_level": 1,
                "ships_destroyed": 0,
                "systems_discovered": 0
            }
        )
        self.speed = 5.0
        self.weapon_level = 1
        self.shield = 100
        self.max_shield = 100
    
    def update(self, dt=1.0):
        super().update(dt)
        # Regenerate shield slowly
        if self.shield < self.max_shield:
            self.shield += 0.5 * dt


@dataclass
class StarSystem:
    name: str = ""
    x: float = 0.0
    y: float = 0.0
    star_type: str = "G"  # G, K, M, O, B
    planet_count: int = 0
    habitable: bool = False
    resources: int = 0
    explored: bool = False
    hostile: bool = False
    special: str = ""  # "pulsar", "ruins", "wormhole"
    
    def to_dict(self):
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "star_type": self.star_type,
            "planet_count": self.planet_count,
            "habitable": self.habitable,
            "resources": self.resources,
            "explored": self.explored,
            "hostile": self.hostile,
            "special": self.special
        }


# ═══════════════════════════════════════════════════════════════════════════════
# GAME MANAGERS
# ═══════════════════════════════════════════════════════════════════════════════

class GalaxyGenerator:
    """Generates galaxy using procedural rules (inspired by .geo)"""
    
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        self.systems: List[StarSystem] = []
        self.generated = False
        
    def generate(self, num_systems=50):
        """Generate galaxy procedurally"""
        star_names = [
            "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
            "Proxima", "Vega", "Sirius", "Rigel", "Betelgeuse", "Antares", "Deneb"
        ]
        
        # Central black hole
        self.systems.append(StarSystem(
            name="Galactic Core",
            x=self.width/2,
            y=self.height/2,
            star_type="BH",
            special="blackhole"
        ))
        
        # Generate star systems in spiral pattern
        for i in range(num_systems):
            # Spiral arm angle offset
            arm_offset = (i % 4) * (math.pi / 2)
            angle = arm_offset + random.uniform(-0.5, 0.5)
            dist = random.uniform(80, min(self.width, self.height) / 2 - 30)
            
            system = StarSystem(
                name=f"{random.choice(star_names)}-{i+1}",
                x=self.width/2 + math.cos(angle) * dist,
                y=self.height/2 + math.sin(angle) * dist,
                star_type=random.choice(["G", "G", "K", "K", "M", "M", "O", "B"]),
                planet_count=random.randint(2, 8),
                habitable=random.random() < 0.15,
                resources=random.randint(1, 10),
                hostile=random.random() < 0.2,
                special=random.choice(["", "", "", "", "pulsar", "ruins", "wormhole"])
            )
            self.systems.append(system)
        
        self.generated = True


class CombatManager:
    """Manages space combat (inspired by .geo rules)"""
    
    def __init__(self):
        self.enemies: List[GameObject] = []
        self.projectiles: List[GameObject] = []
        self.powerups: List[GameObject] = []
        self.tick = 0
        self.in_combat = False
        self.wave = 0
        
    def start_combat(self, difficulty=1):
        """Start combat encounter"""
        self.in_combat = True
        self.wave = difficulty
        self.tick = 0
        self._spawn_enemies(3 + difficulty)
        
    def _spawn_enemies(self, count):
        """Spawn enemy ships"""
        for i in range(count):
            enemy = GameObject(
                x=random.randint(100, 924),
                y=random.randint(50, 300),
                radius=15,
                color=(255, 100, 100),
                health=20 + self.wave * 5,
                obj_type="enemy"
            )
            self.enemies.append(enemy)
    
    def update(self, dt=1.0, player=None):
        """Update combat state"""
        if not self.in_combat:
            return
        
        self.tick += int(dt)
        
        # Spawn reinforcements periodically
        if self.tick % 120 == 0 and len(self.enemies) < 5 + self.wave * 2:
            self._spawn_enemies(1 + self.wave)
        
        # Update enemies
        for enemy in self.enemies:
            if enemy.alive:
                # Simple AI: move toward player
                if player:
                    dx = player.x - enemy.x
                    dy = player.y - enemy.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        enemy.vx = (dx / dist) * 2
                        enemy.vy = (dy / dist) * 2
                enemy.update(dt)
        
        # Update projectiles
        for proj in self.projectiles:
            proj.update(dt)
            # Remove off-screen
            if proj.x < 0 or proj.x > 1024 or proj.y < 0 or proj.y > 768:
                proj.alive = False
        
        # Cleanup
        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]
        
        # Check combat end
        if len(self.enemies) == 0 and self.tick > 60:
            self.in_combat = False


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GAME CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class CosmicOriginsGame:
    """Main game class"""
    
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        self.state = "menu"  # menu, galaxy, combat, paused
        self.tick = 0
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Cosmic Origins - A .geo Powered Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game systems
        self.galaxy = GalaxyGenerator(width, height)
        self.combat = CombatManager()
        
        # Player
        self.player = Player()
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Stars background
        self.stars = [(random.randint(0, width), random.randint(0, height), 
                      random.uniform(0.5, 2)) for _ in range(200)]
        
        # Projectiles
        self.projectiles = []
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "paused":
                        self.state = "galaxy"
                    else:
                        return False
                elif event.key == pygame.K_p:
                    self.state = "paused" if self.state != "paused" else "galaxy"
                elif event.key == pygame.K_TAB:
                    self.state = "galaxy" if self.state == "combat" else "galaxy"
                elif event.key == pygame.K_SPACE:
                    if self.state == "combat":
                        self._player_shoot()
                    elif self.state == "galaxy":
                        self._enter_system()
                elif event.key == pygame.K_e:
                    self._interact()
                elif event.key == pygame.K_r:
                    self._start_new_game()
        
        return True
    
    def _player_shoot(self):
        """Player fires weapon"""
        proj = GameObject(
            x=self.player.x,
            y=self.player.y,
            vx=0,
            vy=-10,
            radius=5,
            color=(255, 255, 100),
            obj_type="projectile"
        )
        self.projectiles.append(proj)
    
    def _enter_system(self):
        """Enter nearest star system"""
        # Find nearest system
        nearest = None
        min_dist = float('inf')
        for system in self.galaxy.systems:
            dx = system.x - self.player.x
            dy = system.y - self.player.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < min_dist and dist < 50:
                nearest = system
                min_dist = dist
        
        if nearest:
            if nearest.hostile:
                self.state = "combat"
                self.combat.start_combat(difficulty=1)
            else:
                # Land on planet
                self.player.data["systems_discovered"] += 1
                self.player.data["credits"] += nearest.resources * 10
                nearest.explored = True
    
    def _interact(self):
        """Interact with nearby objects"""
        pass
    
    def _start_new_game(self):
        """Start new game"""
        self.galaxy = GalaxyGenerator(self.width, self.height)
        self.galaxy.generate(50)
        self.player = Player()
        self.player.x = self.width / 2
        self.player.y = self.height / 2
        self.state = "galaxy"
    
    def update(self, dt=1.0):
        """Update game state"""
        if self.state == "paused":
            return
        
        self.tick += dt
        
        # Player movement
        keys = pygame.key.get_pressed()
        if self.state == "galaxy":
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.x -= self.player.speed * dt
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.x += self.player.speed * dt
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.y -= self.player.speed * dt
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player.y += self.player.speed * dt
        
        # Clamp player to bounds
        self.player.x = max(0, min(self.width, self.player.x))
        self.player.y = max(0, min(self.height, self.player.y))
        
        # Update camera
        self.camera_x = self.player.x - self.width / 2
        self.camera_y = self.player.y - self.height / 2
        
        # Update combat
        if self.state == "combat":
            self.combat.update(dt, self.player)
            
            # Check collisions
            for proj in self.projectiles:
                for enemy in self.combat.enemies:
                    dx = proj.x - enemy.x
                    dy = proj.y - enemy.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < enemy.radius + proj.radius:
                        enemy.health -= 10
                        proj.alive = False
                        if enemy.health <= 0:
                            enemy.alive = False
                            self.player.data["ships_destroyed"] += 1
                            self.player.data["credits"] += 50
            
            # Combat projectiles
            if self.tick % 30 == 0:
                for enemy in self.combat.enemies:
                    proj = GameObject(
                        x=enemy.x,
                        y=enemy.y,
                        vx=0,
                        vy=5,
                        radius=6,
                        color=(255, 100, 50),
                        obj_type="enemy_projectile"
                    )
                    self.combat.projectiles.append(proj)
        
        # Update projectiles
        for proj in self.projectiles:
            proj.update(dt)
        self.projectiles = [p for p in self.projectiles if p.alive and 
                          0 < p.x < self.width and 0 < p.y < self.height]
        
        # Update player
        self.player.update(dt)
    
    def draw(self):
        """Render game"""
        # Clear screen
        self.screen.fill((5, 10, 30))
        
        # Draw stars
        for sx, sy, size in self.stars:
            brightness = int(155 + 100 * random.random())
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), 
                             (int(sx), int(sy)), int(size))
        
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "galaxy":
            self._draw_galaxy()
        elif self.state == "combat":
            self._draw_combat()
        elif self.state == "paused":
            self._draw_paused()
        
        # Draw UI
        self._draw_ui()
        
        pygame.display.flip()
    
    def _draw_menu(self):
        """Draw main menu"""
        title = self.font.render("COSMIC ORIGINS", True, (100, 200, 255))
        subtitle = self.small_font.render("A .geo-Powered Space Game", True, (150, 150, 150))
        
        self.screen.blit(title, (self.width/2 - title.get_width()/2, self.height/3))
        self.screen.blit(subtitle, (self.width/2 - subtitle.get_width()/2, self.height/3 + 50))
        
        # Start prompt
        prompt = self.small_font.render("Press R to Start", True, (200, 200, 200))
        self.screen.blit(prompt, (self.width/2 - prompt.get_width()/2, self.height/2))
        
        # Controls
        controls = [
            "Arrow Keys / WASD - Move",
            "Space - Shoot",
            "E - Interact",
            "Tab - Galaxy Map",
            "P - Pause"
        ]
        for i, ctrl in enumerate(controls):
            text = self.small_font.render(ctrl, True, (100, 150, 180))
            self.screen.blit(text, (self.width/2 - text.get_width()/2, self.height/2 + 50 + i*25))
    
    def _draw_galaxy(self):
        """Draw galaxy exploration view"""
        # Draw star systems
        for system in self.galaxy.systems:
            # Color based on star type
            colors = {
                "G": (255, 255, 200),
                "K": (255, 200, 150),
                "M": (255, 150, 100),
                "O": (150, 200, 255),
                "B": (100, 150, 255),
                "BH": (100, 50, 150)
            }
            color = colors.get(system.star_type, (255, 255, 255))
            
            # Size based on type
            radius = 8 if system.star_type == "BH" else 5
            
            # Draw system
            pygame.draw.circle(self.screen, color, (int(system.x), int(system.y)), radius)
            
            # Habitable indicator
            if system.habitable:
                pygame.draw.circle(self.screen, (100, 255, 100), (int(system.x), int(system.y)), radius + 3, 2)
            
            # Hostile indicator
            if system.hostile:
                pygame.draw.circle(self.screen, (255, 100, 100), (int(system.x), int(system.y)), radius + 5, 2)
            
            # Name (if explored or close)
            dx = system.x - self.player.x
            dy = system.y - self.player.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 100 or system.explored:
                name_surf = self.small_font.render(system.name, True, (200, 200, 200))
                self.screen.blit(name_surf, (system.x + 10, system.y - 10))
        
        # Draw player
        self.player.draw(self.screen)
    
    def _draw_combat(self):
        """Draw combat view"""
        offset = (-self.camera_x, -self.camera_y)
        
        # Draw enemies
        for enemy in self.combat.enemies:
            enemy.draw(self.screen, offset)
        
        # Draw projectiles
        for proj in self.combat.projectiles:
            proj.draw(self.screen, offset)
        
        # Draw player
        self.player.draw(self.screen, offset)
        
        # Wave info
        wave_text = self.small_font.render(f"Wave {self.combat.wave} - Enemies: {len(self.combat.enemies)}", 
                                          True, (255, 200, 100))
        self.screen.blit(wave_text, (self.width/2 - wave_text.get_width()/2, 50))
    
    def _draw_paused(self):
        """Draw pause screen"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, (255, 255, 255))
        self.screen.blit(pause_text, (self.width/2 - pause_text.get_width()/2, self.height/3))
        
        resume = self.small_font.render("Press P to Resume", True, (200, 200, 200))
        self.screen.blit(resume, (self.width/2 - resume.get_width()/2, self.height/2))
    
    def _draw_ui(self):
        """Draw HUD"""
        # Player stats
        stats = [
            f"Health: {self.player.health}/{self.player.max_health}",
            f"Shield: {int(self.player.shield)}/{self.player.max_shield}",
            f"Credits: {self.player.data['credits']}",
            f"Systems: {self.player.data['systems_discovered']}",
            f"Kills: {self.player.data['ships_destroyed']}",
        ]
        
        for i, stat in enumerate(stats):
            color = (255, 100, 100) if "Health" in stat and self.player.health < 30 else (200, 200, 200)
            surf = self.small_font.render(stat, True, color)
            self.screen.blit(surf, (10, 10 + i * 22))
        
        # State indicator
        state_colors = {
            "menu": (255, 255, 255),
            "galaxy": (100, 200, 255),
            "combat": (255, 100, 100),
            "paused": (255, 255, 0)
        }
        state_text = self.small_font.render(f"Mode: {self.state.upper()}", True, 
                                           state_colors.get(self.state, (255, 255, 255)))
        self.screen.blit(state_text, (self.width - 150, 10))
        
        # FPS
        fps = self.clock.get_fps()
        fps_color = (100, 255, 100) if fps >= 55 else (255, 200, 100) if fps >= 30 else (255, 100, 100)
        fps_surf = self.small_font.render(f"FPS: {int(fps)}", True, fps_color)
        self.screen.blit(fps_surf, (self.width - 80, 35))
    
    def run(self, fps=60):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update(dt=1.0)
            self.draw()
            self.clock.tick(fps)
        
        pygame.quit()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Game entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Cosmic Origins - .geo Space Game")
    parser.add_argument("--width", type=int, default=1024, help="Window width")
    parser.add_argument("--height", type=int, default=768, help="Window height")
    parser.add_argument("--fps", type=int, default=60, help="Target FPS")
    args = parser.parse_args()
    
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    if not HAS_PYGAME:
        print("Error: pygame required. Install with: pip install pygame")
        return
    
    game = CosmicOriginsGame(args.width, args.height)
    game.run(args.fps)


if __name__ == "__main__":
    main()
