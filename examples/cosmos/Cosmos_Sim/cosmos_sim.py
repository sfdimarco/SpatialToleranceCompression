#!/usr/bin/env python3
"""
Gravity Sandbox - Interactive Orbital Mechanics Simulator
==========================================================

A satisfying gravity sandbox where you create stars, planets, and cosmic structures.
Powered by .geo rules for emergent orbital behavior!

Features:
  - N-body gravity simulation
  - Beautiful orbital patterns
  - Collision detection with flashes
  - Particle trails and glow effects
  - .geo-driven behavior rules

Controls:
  - Left Click: Spawn planet (blue)
  - Right Click: Spawn sun (heavy gold)
  - Middle Click: Spawn dark matter (purple)
  - Shift + Click: Spawn particle swarm
  - G: Toggle gravity visualization
  - T: Toggle trails
  - Space: Pause/Resume
  - C: Clear all
  - S: Spawn solar system
  - Esc: Quit

Run: python cosmos_sim.py
"""

import sys
import os
import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

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

# Import from src package
from src import (
    parse_geo_script, load_geo, validate_geo,
    Node, Y_LOOP, X_LOOP, Z_LOOP, DIAG_LOOP, GATES,
    family_of, next_mask
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Physics
G_CONSTANT = 0.5          # Gravitational constant
SOFTENING = 5.0           # Distance softening for stability
MAX_VELOCITY = 8.0        # Maximum particle speed
FRICTION = 0.999          # Velocity damping

# Particle types
TYPE_HEAVY = 'heavy'      # Sun/black hole - gold
TYPE_NORMAL = 'normal'    # Planet - blue
TYPE_LIGHT = 'light'      # Dust/debris - red
TYPE_DARK = 'dark'        # Dark matter - purple
TYPE_FLASH = 'flash'      # Collision - white

# Colors
COLORS = {
    TYPE_HEAVY: (255, 200, 50),
    TYPE_NORMAL: (50, 150, 255),
    TYPE_LIGHT: (255, 80, 80),
    TYPE_DARK: (150, 80, 200),
    TYPE_FLASH: (255, 255, 255),
}

# Sizes
SIZES = {
    TYPE_HEAVY: 20,
    TYPE_NORMAL: 8,
    TYPE_LIGHT: 3,
    TYPE_DARK: 12,
    TYPE_FLASH: 15,
}

# Mass
MASSES = {
    TYPE_HEAVY: 500,
    TYPE_NORMAL: 50,
    TYPE_LIGHT: 5,
    TYPE_DARK: 200,
}


# ═══════════════════════════════════════════════════════════════════════════════
# PARTICLE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Particle:
    """A gravitational particle with physics and rendering"""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    mass: float = 50
    ptype: str = TYPE_NORMAL
    age: int = 0
    trail: List[Tuple[float, float]] = None
    flash: float = 0.0
    geo_mask: int = 0b1100  # X_LOOP default
    alive: bool = True
    
    def __post_init__(self):
        if self.trail is None:
            self.trail = []
        # Set properties based on type
        if self.ptype == TYPE_HEAVY:
            self.mass = MASSES[TYPE_HEAVY]
            self.geo_mask = 0b1000  # Y_LOOP
        elif self.ptype == TYPE_NORMAL:
            self.mass = MASSES[TYPE_NORMAL]
            self.geo_mask = 0b1100  # X_LOOP
        elif self.ptype == TYPE_LIGHT:
            self.mass = MASSES[TYPE_LIGHT]
            self.geo_mask = 0b0111  # Z_LOOP
        elif self.ptype == TYPE_DARK:
            self.mass = MASSES[TYPE_DARK]
            self.geo_mask = 0b1001  # DIAG_LOOP
        elif self.ptype == TYPE_FLASH:
            self.geo_mask = 0b1111  # GATE
    
    def update(self, dt: float = 1.0, bounds: Tuple[int, int] = None):
        """Update particle position"""
        # Store trail
        if self.ptype != TYPE_DARK:  # Dark matter doesn't leave trails
            self.trail.append((self.x, self.y))
            max_trail = 30 if self.ptype == TYPE_HEAVY else 15
            if len(self.trail) > max_trail:
                self.trail.pop(0)
        
        # Apply velocity
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Limit velocity
        speed = math.hypot(self.vx, self.vy)
        if speed > MAX_VELOCITY:
            scale = MAX_VELOCITY / speed
            self.vx *= scale
            self.vy *= scale
        
        # Apply friction
        self.vx *= FRICTION
        self.vy *= FRICTION
        
        # Wrap around bounds
        if bounds:
            w, h = bounds
            if self.x < 0:
                self.x = w
            elif self.x > w:
                self.x = 0
            if self.y < 0:
                self.y = h
            elif self.y > h:
                self.y = 0
        
        # Update age and flash
        self.age += int(dt)
        if self.flash > 0:
            self.flash -= dt * 2
    
    def apply_gravity(self, other: 'Particle'):
        """Apply gravitational force from another particle"""
        if self is other:
            return
        
        dx = other.x - self.x
        dy = other.y - self.y
        dist_sq = dx * dx + dy * dy
        dist = math.sqrt(dist_sq)
        
        # Softening to prevent singularity
        dist = max(dist, SOFTENING)
        
        # Gravitational force
        force = G_CONSTANT * self.mass * other.mass / dist_sq
        
        # Apply force to velocity
        fx = (dx / dist) * force
        fy = (dy / dist) * force
        
        self.vx += fx * 0.01
        self.vy += fy * 0.01
    
    def check_collision(self, other: 'Particle') -> bool:
        """Check if colliding with another particle"""
        dist = math.hypot(self.x - other.x, self.y - other.y)
        min_dist = (SIZES[self.ptype] + SIZES[other.ptype]) * 0.5
        
        if dist < min_dist:
            return True
        return False
    
    def draw_trail(self, screen: pygame.Surface):
        """Draw particle trail"""
        if len(self.trail) < 2 or self.ptype == TYPE_DARK:
            return
        
        color = COLORS.get(self.ptype, (255, 255, 255))
        
        for i in range(len(self.trail) - 1):
            t = i / len(self.trail)
            alpha = int(150 * t * 0.6)
            width = max(1, int(SIZES[self.ptype] * t * 0.5))
            
            # Trail fades
            trail_color = (
                int(color[0] * t * 0.5),
                int(color[1] * t * 0.5),
                int(color[2] * t * 0.5)
            )
            
            pygame.draw.line(
                screen, trail_color,
                (int(self.trail[i][0]), int(self.trail[i][1])),
                (int(self.trail[i+1][0]), int(self.trail[i+1][1])),
                width
            )
    
    def draw(self, screen: pygame.Surface, show_gravity: bool = False):
        """Draw particle with glow effects"""
        x, y = int(self.x), int(self.y)
        size = SIZES.get(self.ptype, 5)
        color = COLORS.get(self.ptype, (255, 255, 255))
        
        # Flash effect
        if self.flash > 0:
            glow_size = int(size * (1 + self.flash))
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            alpha = int(200 * self.flash)
            pygame.draw.circle(glow_surf, (255, 255, 255, alpha), (glow_size, glow_size), glow_size)
            screen.blit(glow_surf, (x - glow_size, y - glow_size))
        
        # Glow for heavy masses
        if self.ptype == TYPE_HEAVY:
            glow_size = int(size * 2.5)
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, 80), (glow_size, glow_size), glow_size)
            screen.blit(glow_surf, (x - glow_size, y - glow_size))
        
        # Core particle
        pygame.draw.circle(screen, color, (x, y), size)
        
        # Highlight for normal/heavy
        if self.ptype in (TYPE_HEAVY, TYPE_NORMAL):
            highlight_pos = (x - size//3, y - size//3)
            pygame.draw.circle(screen, (255, 255, 255), highlight_pos, size//3)


# ═══════════════════════════════════════════════════════════════════════════════
# GRAVITY SANDBOX CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class GravitySandbox:
    """Interactive gravity sandbox with .geo rules"""
    
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.particles: List[Particle] = []
        self.paused = False
        self.show_gravity = False
        self.show_trails = True
        self.tick = 0
        self.spawn_mode = TYPE_NORMAL
        self.swarm_mode = False
        
        # Load .geo script for behavior rules
        self.geo_program = self._load_geo()
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Gravity Sandbox - .geo Orbital Mechanics")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        
        # Spawn initial solar system
        self._spawn_solar_system()
    
    def _load_geo(self):
        """Load gravity sandbox .geo script"""
        geo_path = os.path.join(os.path.dirname(__file__), 'gravity_sandbox.geo')
        
        try:
            with open(geo_path, 'r', encoding='utf-8') as f:
                script = f.read()
            
            errors = validate_geo(script)
            if errors:
                print(f"Warning: {len(errors)} geo warnings")
            
            prog = parse_geo_script(script)
            print(f"Loaded gravity_sandbox.geo - {len(prog.rules)} rules")
            return prog
            
        except Exception as e:
            print(f"Could not load .geo: {e}")
            # Create minimal fallback
            from src import Program, Rule, IF_family, SwitchFamily
            return Program([
                Rule(IF_family("Y_LOOP"), SwitchFamily("X_LOOP"), "y>x"),
                Rule(IF_family("X_LOOP"), SwitchFamily("Z_LOOP"), "x>z"),
            ], name="fallback")
    
    def _spawn_solar_system(self):
        """Spawn a mini solar system in the center"""
        cx, cy = self.width // 2, self.height // 2
        
        # Central sun
        sun = Particle(cx, cy, ptype=TYPE_HEAVY)
        self.particles.append(sun)
        
        # Orbiting planets
        for i in range(5):
            angle = (i / 5) * math.pi * 2
            dist = 100 + i * 40
            px = cx + math.cos(angle) * dist
            py = cy + math.sin(angle) * dist
            
            planet = Particle(px, py, ptype=TYPE_NORMAL)
            
            # Orbital velocity (perpendicular to radius)
            orbital_speed = math.sqrt(G_CONSTANT * sun.mass / dist) * 0.5
            planet.vx = -math.sin(angle) * orbital_speed
            planet.vy = math.cos(angle) * orbital_speed
            
            self.particles.append(planet)
        
        # Some dust particles
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(80, 280)
            px = cx + math.cos(angle) * dist
            py = cy + math.sin(angle) * dist
            
            dust = Particle(px, py, ptype=TYPE_LIGHT)
            dust.vx = random.uniform(-1, 1)
            dust.vy = random.uniform(-1, 1)
            self.particles.append(dust)
    
    def spawn_particle(self, x: float, y: float, ptype: str = None, swarm: bool = False):
        """Spawn a particle at position"""
        if ptype is None:
            ptype = self.spawn_mode
        
        if swarm:
            # Spawn a cluster
            for _ in range(8):
                ox = x + random.uniform(-20, 20)
                oy = y + random.uniform(-20, 20)
                particle = Particle(ox, oy, ptype=ptype)
                particle.vx = random.uniform(-2, 2)
                particle.vy = random.uniform(-2, 2)
                self.particles.append(particle)
        else:
            particle = Particle(x, y, ptype=ptype)
            
            # Add some initial velocity based on spawn type
            if ptype == TYPE_NORMAL:
                # Give slight random velocity for interesting orbits
                particle.vx = random.uniform(-1, 1)
                particle.vy = random.uniform(-1, 1)
            
            self.particles.append(particle)
    
    def update(self, dt: float = 1.0):
        """Update simulation"""
        if self.paused:
            return
        
        self.tick += 1
        
        # Apply gravity between all particles (O(n²) but fine for < 200 particles)
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles):
                if i < j:
                    p1.apply_gravity(p2)
                    p2.apply_gravity(p1)
        
        # Update positions
        bounds = (self.width, self.height)
        for p in self.particles:
            p.update(dt, bounds)
        
        # Check collisions
        self._check_collisions()
        
        # Apply .geo rules to update particle states
        self._apply_geo_rules()
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.alive]
        
        # Limit particle count
        if len(self.particles) > 300:
            # Remove oldest light particles
            self.particles = sorted(self.particles, key=lambda p: p.age)
            self.particles = self.particles[-250:]
    
    def _check_collisions(self):
        """Handle particle collisions"""
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles):
                if i < j and p1.alive and p2.alive:
                    if p1.check_collision(p2):
                        self._handle_collision(p1, p2)
    
    def _handle_collision(self, p1: Particle, p2: Particle):
        """Handle collision between two particles"""
        # Merge smaller into larger
        if p1.mass >= p2.mass:
            big, small = p1, p2
        else:
            big, small = p2, p1
        
        # Create flash effect
        if big.ptype != TYPE_FLASH:
            flash = Particle(
                (p1.x + p2.x) / 2,
                (p1.y + p2.y) / 2,
                ptype=TYPE_FLASH
            )
            flash.flash = 3.0
            self.particles.append(flash)
        
        # Merge masses
        big.mass += small.mass * 0.5
        big.vx = (big.vx * big.mass + small.vx * small.mass) / (big.mass + small.mass)
        big.vy = (big.vy * big.mass + small.vy * small.mass) / (big.mass + small.mass)
        big.flash = 1.0
        
        # Remove smaller particle
        small.alive = False
    
    def _apply_geo_rules(self):
        """Apply .geo script rules to particles"""
        if not self.geo_program:
            return
        
        # Create temporary nodes for each particle
        for p in self.particles:
            # Create a node to apply geo rules
            node = Node(p.x, p.y, SIZES[p.ptype], 0, p.geo_mask)
            node.vars['age'] = p.age
            
            # Count neighbors by type
            heavy_count = sum(1 for other in self.particles 
                            if other is not p and other.ptype == TYPE_HEAVY 
                            and math.hypot(other.x - p.x, other.y - p.y) < 150)
            normal_count = sum(1 for other in self.particles 
                             if other is not p and other.ptype == TYPE_NORMAL
                             and math.hypot(other.x - p.x, other.y - p.y) < 100)
            
            # Apply geo program
            self.geo_program.step_tree(node, self.tick)
            
            # Update particle from node
            p.geo_mask = node.mask
            p.age = node.vars.get('age', p.age)
    
    def draw(self):
        """Render the sandbox"""
        # Fade effect for trails
        self.screen.fill((10, 10, 20))
        
        # Draw gravity lines if enabled
        if self.show_gravity:
            self._draw_gravity_lines()
        
        # Draw trails
        if self.show_trails:
            for p in self.particles:
                p.draw_trail(self.screen)
        
        # Draw particles
        for p in self.particles:
            p.draw(self.screen, self.show_gravity)
        
        # Draw UI
        self._draw_ui()
        
        pygame.display.flip()
    
    def _draw_gravity_lines(self):
        """Draw gravity influence lines between heavy masses"""
        heavy = [p for p in self.particles if p.ptype == TYPE_HEAVY]
        
        for p in self.particles:
            for h in heavy:
                if p is not h:
                    dist = math.hypot(p.x - h.x, p.y - h.y)
                    if dist < 200:
                        alpha = int(80 * (1 - dist/200))
                        color = (255, 200, 100, alpha)
                        pygame.draw.line(
                            self.screen, color,
                            (int(p.x), int(p.y)),
                            (int(h.x), int(h.y)), 1
                        )
    
    def _draw_ui(self):
        """Draw UI overlay"""
        fps = self.clock.get_fps()
        
        # Stats
        stats = [
            f"FPS: {int(fps)}",
            f"Particles: {len(self.particles)}",
            f"Tick: {self.tick}",
        ]
        
        y = 10
        for stat in stats:
            surf = self.small_font.render(stat, True, (200, 200, 200))
            self.screen.blit(surf, (10, y))
            y += 20
        
        # Mode indicator
        mode_text = f"Spawn: {self.spawn_mode.upper()} {'(SWARM)' if self.swarm_mode else ''}"
        mode_surf = self.small_font.render(mode_text, True, (255, 200, 100))
        self.screen.blit(mode_surf, (10, self.height - 30))
        
        # Controls
        controls = "LMB: Planet | RMB: Sun | MMB: Dark Matter | Shift: Swarm | G: Gravity | T: Trails | S: Solar System | C: Clear"
        ctrl_surf = self.small_font.render(controls, True, (150, 150, 150))
        self.screen.blit(ctrl_surf, (self.width//2 - ctrl_surf.get_width()//2, self.height - 25))
        
        # Pause overlay
        if self.paused:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.font.render("PAUSED", True, (255, 255, 255))
            self.screen.blit(pause_text, (self.width//2 - 40, self.height//2))
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_g:
                    self.show_gravity = not self.show_gravity
                elif event.key == pygame.K_t:
                    self.show_trails = not self.show_trails
                elif event.key == pygame.K_c:
                    self.particles = []
                    self.tick = 0
                elif event.key == pygame.K_s:
                    self.particles = []
                    self.tick = 0
                    self._spawn_solar_system()
                elif event.key == pygame.K_1:
                    self.spawn_mode = TYPE_NORMAL
                    self.swarm_mode = False
                elif event.key == pygame.K_2:
                    self.spawn_mode = TYPE_HEAVY
                    self.swarm_mode = False
                elif event.key == pygame.K_3:
                    self.spawn_mode = TYPE_LIGHT
                    self.swarm_mode = False
                elif event.key == pygame.K_4:
                    self.spawn_mode = TYPE_DARK
                    self.swarm_mode = False
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.swarm_mode = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.swarm_mode = True
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click - spawn planet
                    keys = pygame.key.get_pressed()
                    swarm = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                    self.spawn_particle(event.pos[0], event.pos[1], TYPE_NORMAL, swarm)
                elif event.button == 3:  # Right click - spawn sun
                    self.spawn_particle(event.pos[0], event.pos[1], TYPE_HEAVY)
                elif event.button == 2:  # Middle click - spawn dark matter
                    self.spawn_particle(event.pos[0], event.pos[1], TYPE_DARK)
        
        return True
    
    def run(self, fps=60):
        """Main loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update(dt=1.0)
            self.draw()
            self.clock.tick(fps)
        
        pygame.quit()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gravity Sandbox - Interactive Orbital Mechanics")
    parser.add_argument("--width", type=int, default=1280, help="Window width")
    parser.add_argument("--height", type=int, default=720, help="Window height")
    parser.add_argument("--fps", type=int, default=60, help="Target FPS")
    args = parser.parse_args()
    
    sandbox = GravitySandbox(args.width, args.height)
    sandbox.run(args.fps)


if __name__ == "__main__":
    main()
