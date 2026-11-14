#!/usr/bin/env python3
"""
gravity_cosmos_sim.py - Gravitational Particle Cosmos Visualizer
=================================================================

A smooth gravity simulation inspired by .geo scripts.
Features:
  - Smooth particle motion with trails
  - Gravitational attraction visualization
  - Orbital mechanics
  - Galaxy formation
  - Glow effects

Run with: python gravity_cosmos_sim.py
Controls:
  - Mouse: Add particles
  - Space: Pause
  - R: Reset
  - G: Toggle gravity visualization
  - Esc: Quit
"""

import sys
import os
import math
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import pygame
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("pygame not found. Please install: pip install pygame")
    sys.exit(1)


class Particle:
    """Represents a cosmic particle with physics properties"""

    def __init__(self, x, y, mass, particle_type):
        self.x = x
        self.y = y
        self.mass = mass
        self.type = particle_type  # "heavy", "orbiter", "light", "dark"
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.age = 0
        self.trail = []
        self.max_trail = 15
        self.alive = True
        
        # Set properties based on type
        if particle_type == "heavy":
            self.color = (255, 200, 100)
            self.radius = 8
        elif particle_type == "orbiter":
            self.color = (100, 200, 255)
            self.radius = 4
        elif particle_type == "light":
            self.color = (255, 100, 100)
            self.radius = 2
        elif particle_type == "dark":
            self.color = (150, 100, 200)
            self.radius = 5
        else:
            self.color = (200, 200, 200)
            self.radius = 3

    def update(self, dt=1.0, bounds=None):
        """Update particle position with velocity"""
        # Store position for trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        # Apply velocity
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Wrap around bounds
        if bounds:
            if self.x < 0:
                self.x = bounds[0]
            elif self.x > bounds[0]:
                self.x = 0
            if self.y < 0:
                self.y = bounds[1]
            elif self.y > bounds[1]:
                self.y = 0

        self.age += dt

    def apply_gravity(self, other, G=0.3):
        """Apply gravitational attraction from another particle"""
        dx = other.x - self.x
        dy = other.y - self.y
        dist_sq = dx * dx + dy * dy
        
        if dist_sq < 100:  # Minimum distance
            return
            
        dist = math.sqrt(dist_sq)

        # Gravitational force: F = G * m1 * m2 / r^2
        force = G * self.mass * other.mass / dist_sq
        force = min(force, 1.5)  # Cap force for stability

        # Apply force to velocity
        self.vx += (dx / dist) * force * 0.1
        self.vy += (dy / dist) * force * 0.1

    def draw_trail(self, screen):
        """Draw particle trail"""
        if len(self.trail) < 2:
            return

        for i in range(len(self.trail) - 1):
            t = i / len(self.trail)
            alpha = int(150 * t * 0.6)
            trail_color = (*self.color[:3], alpha)
            
            width = max(1, int(self.radius * t))
            pygame.draw.line(screen, trail_color, 
                           (int(self.trail[i][0]), int(self.trail[i][1])),
                           (int(self.trail[i+1][0]), int(self.trail[i+1][1])),
                           width)

    def draw(self, screen, glow=True):
        """Draw particle with glow effect"""
        x, y = int(self.x), int(self.y)
        
        # Glow effect
        if glow:
            glow_radius = int(self.radius * 2.5)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_color = (*self.color[:3], 80)
            pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (x - glow_radius, y - glow_radius))
        
        # Core
        pygame.draw.circle(screen, self.color, (x, y), self.radius)


class GravityCosmos:
    """Main gravity cosmos simulation"""

    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        self.particles = []
        self.paused = False
        self.show_gravity = False
        self.tick = 0

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Gravity Cosmos - Particle Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)

        # Spawn initial particles
        self._spawn_initial()

    def _spawn_initial(self):
        """Spawn initial particle population"""
        # Create a few heavy mass centers
        for _ in range(3):
            x = random.uniform(self.width * 0.3, self.width * 0.7)
            y = random.uniform(self.height * 0.3, self.height * 0.7)
            self.particles.append(Particle(x, y, mass=50, particle_type="heavy"))

        # Create orbiters
        for _ in range(30):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            self.particles.append(Particle(x, y, mass=10, particle_type="orbiter"))

        # Create light particles
        for _ in range(50):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            self.particles.append(Particle(x, y, mass=2, particle_type="light"))

        # Create dark matter
        for _ in range(15):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            self.particles.append(Particle(x, y, mass=20, particle_type="dark"))

    def update(self, dt=1.0):
        """Update simulation state"""
        if self.paused:
            return

        self.tick += 1

        # Apply gravity between particles (optimized: only heavy masses attract)
        heavy_particles = [p for p in self.particles if p.type == "heavy"]
        
        for p in self.particles:
            for heavy in heavy_particles:
                if p is not heavy:
                    p.apply_gravity(heavy)
        
        # Update positions
        bounds = (self.width, self.height)
        for p in self.particles:
            p.update(dt, bounds)

        # Continuous spawning
        if self.tick % 30 == 0 and random.random() < 0.3:
            # Spawn new orbiter near a heavy mass
            heavy = random.choice(heavy_particles) if heavy_particles else None
            if heavy:
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(50, 150)
                x = heavy.x + math.cos(angle) * dist
                y = heavy.y + math.sin(angle) * dist
                self.particles.append(Particle(x, y, mass=10, particle_type="orbiter"))

        # Remove old particles
        self.particles = [p for p in self.particles if p.alive and p.age < 500]

    def draw(self):
        """Render simulation"""
        # Fade effect for trails
        fade_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        fade_surf.fill((10, 10, 20, 40))
        self.screen.blit(fade_surf, (0, 0))

        # Draw gravity lines if enabled
        if self.show_gravity:
            self._draw_gravity_lines()

        # Draw particles
        for p in self.particles:
            p.draw_trail(self.screen)
        
        for p in self.particles:
            p.draw(self.screen)

        # Draw UI
        self._draw_ui()

        pygame.display.flip()

    def _draw_gravity_lines(self):
        """Draw gravity influence lines"""
        heavy_particles = [p for p in self.particles if p.type == "heavy"]
        for p in self.particles:
            for heavy in heavy_particles:
                if p is not heavy:
                    dx = heavy.x - p.x
                    dy = heavy.y - p.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < 200:
                        alpha = int(100 * (1 - dist/200))
                        color = (255, 255, 255, alpha)
                        pygame.draw.line(self.screen, color,
                                       (int(p.x), int(p.y)),
                                       (int(heavy.x), int(heavy.y)), 1)

    def _draw_ui(self):
        """Draw UI overlay"""
        fps = self.clock.get_fps()
        
        stats = [
            f"FPS: {int(fps)}",
            f"Particles: {len(self.particles)}",
            f"Tick: {self.tick}",
            f"Space: Pause | G: Gravity | R: Reset | Mouse: Add",
        ]
        
        y = 10
        for stat in stats:
            surf = self.font.render(stat, True, (200, 200, 200))
            self.screen.blit(surf, (10, y))
            y += 24

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
                elif event.key == pygame.K_r:
                    self._reset()
                elif event.key == pygame.K_g:
                    self.show_gravity = not self.show_gravity

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click - add orbiter
                    self.particles.append(Particle(event.pos[0], event.pos[1], 
                                                   mass=10, particle_type="orbiter"))
                elif event.button == 3:  # Right click - add heavy mass
                    self.particles.append(Particle(event.pos[0], event.pos[1],
                                                   mass=50, particle_type="heavy"))

        return True

    def _reset(self):
        """Reset simulation"""
        self.particles = []
        self.tick = 0
        self._spawn_initial()

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
    parser = argparse.ArgumentParser(description="Gravity Cosmos - Particle Simulation")
    parser.add_argument("--width", type=int, default=1024, help="Window width")
    parser.add_argument("--height", type=int, default=768, help="Window height")
    parser.add_argument("--fps", type=int, default=60, help="Target FPS")
    args = parser.parse_args()

    sim = GravityCosmos(args.width, args.height)
    sim.run(args.fps)


if __name__ == "__main__":
    main()
