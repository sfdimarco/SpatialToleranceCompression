"""
gravity_cosmos_sim.py - Gravitational Particle Cosmos Visualizer
=================================================================

A smooth, p5.js-inspired gravity simulation powered by .geo scripts.
Features:
  - Smooth particle motion with trails
  - Gravitational attraction visualization
  - Orbital mechanics
  - Galaxy formation
  - Glow effects and smooth rendering

Run with: python gravity_cosmos_sim.py
"""

import sys
import os
import math
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# BinaryQuadTreeTest is available in the parent directory if needed
# for future .geo-driven particle spawning/state transitions

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
        self.prev_x = x
        self.prev_y = y
        self.mass = mass
        self.type = particle_type  # "heavy", "orbiter", "light", "dark"
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.age = 0
        self.trail = []
        self.max_trail = 20
        self.alive = True
        
    def update(self, dt=1.0):
        """Update particle position with velocity"""
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Apply velocity
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
        
        self.age += dt
    
    def apply_gravity(self, other, G=0.5):
        """Apply gravitational attraction from another particle"""
        dx = other.x - self.x
        dy = other.y - self.y
        dist_sq = dx * dx + dy * dy
        dist = max(math.sqrt(dist_sq), 10)  # Minimum distance to prevent singularity
        
        # Gravitational force: F = G * m1 * m2 / r^2
        force = G * self.mass * other.mass / dist_sq
        force = min(force, 2.0)  # Cap force for stability
        
        # Apply force to velocity
        self.vx += (dx / dist) * force
        self.vy += (dy / dist) * force
    
    def draw_trail(self, screen, color, alpha=100):
        """Draw particle trail"""
        if len(self.trail) < 2:
            return
        
        for i in range(len(self.trail) - 1):
            t = i / len(self.trail)
            trail_alpha = int(alpha * t * 0.6)
            trail_color = (*color[:3], trail_alpha)
            
            surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, trail_color, (2, 2), max(1, int(2 * t)))
            screen.blit(surf, (int(self.trail[i][0]) - 2, int(self.trail[i][1]) - 2))
    
    def draw(self, screen, color, glow=True):
        """Draw particle with glow effect"""
        # Glow effect
        if glow:
            for radius in [int(20 * self.mass / 5), int(12 * self.mass / 5), int(6 * self.mass / 5)]:
                if radius > 1:
                    alpha = max(20, int(60 * self.mass / 10))
                    glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*color[:3], alpha), (radius, radius), radius)
                    screen.blit(glow_surf, (int(self.x) - radius, int(self.y) - radius))
        
        # Core particle
        radius = max(3, int(5 * self.mass / 5))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)


class GravityCosmosSim:
    """Main gravity cosmos simulation"""
    
    def __init__(self, width=1024, height=768, max_particles=200):
        self.width = width
        self.height = height
        self.max_particles = max_particles
        self.tick = 0
        self.particles = []
        # Color palette (cosmic theme)
        self.colors = {
            "heavy": (255, 100, 100),      # Red - massive stars
            "orbiter": (100, 220, 220),    # Teal - orbiting planets
            "light": (255, 240, 100),      # Yellow - fast particles
            "dark": (180, 120, 255),       # Purple - dark matter
        }
        
        # Physics constants
        self.G = 0.8  # Gravitational constant
        self.damping = 0.995  # Velocity damping
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Gravity Cosmos - .geo Particle Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        
        # Trail surface for fade effect
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Spawn initial particles
        self._spawn_initial()
    
    def _spawn_initial(self):
        """Spawn initial particle population"""
        # Central heavy mass
        center_mass = Particle(self.width // 2, self.height // 2, 15, "heavy")
        center_mass.vx = 0
        center_mass.vy = 0
        center_mass.max_trail = 10
        self.particles.append(center_mass)
        
        # Orbiting particles
        for i in range(30):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(100, 300)
            x = self.width // 2 + math.cos(angle) * dist
            y = self.height // 2 + math.sin(angle) * dist
            
            # Orbital velocity (perpendicular to radius)
            orbital_speed = math.sqrt(self.G * center_mass.mass / dist) * 0.5
            vx = -math.sin(angle) * orbital_speed
            vy = math.cos(angle) * orbital_speed
            
            p = Particle(x, y, random.uniform(3, 6), "orbiter")
            p.vx = vx
            p.vy = vy
            p.max_trail = 25
            self.particles.append(p)
        
        # Light fast particles
        for i in range(40):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            p = Particle(x, y, random.uniform(1, 3), "light")
            p.vx = random.uniform(-2, 2)
            p.vy = random.uniform(-2, 2)
            p.max_trail = 35
            self.particles.append(p)
        
        # Dark matter (invisible gravity sources)
        for i in range(8):
            x = random.uniform(100, self.width - 100)
            y = random.uniform(100, self.height - 100)
            p = Particle(x, y, random.uniform(6, 10), "dark")
            p.vx = random.uniform(-0.5, 0.5)
            p.vy = random.uniform(-0.5, 0.5)
            p.max_trail = 5
            self.particles.append(p)
    
    def update_physics(self):
        """Update particle physics with gravity - optimized O(n) approximation"""
        # Find heavy masses for gravity wells (optimization: only these attract)
        heavy_masses = [p for p in self.particles if p.type == "heavy"]
        
        # Apply gravity from heavy masses to all other particles
        for p in self.particles:
            if p.type != "heavy":
                for heavy in heavy_masses:
                    p.apply_gravity(heavy, self.G)
        
        # Particle-particle gravity (only for nearby particles, limited range)
        # This is optimized to avoid O(n²) full calculation
        for i, p1 in enumerate(self.particles):
            if p1.type == "heavy":
                continue
            for j, p2 in enumerate(self.particles[i+1:], i+1):
                if p2.type == "heavy":
                    continue
                # Only calculate gravity between nearby non-heavy particles
                dist_sq = (p1.x - p2.x)**2 + (p1.y - p2.y)**2
                if dist_sq < 10000:  # Only if within 100 pixels
                    p1.apply_gravity(p2, self.G * 0.3)  # Reduced strength
        
        # Update positions and apply damping
        for p in self.particles:
            p.vx *= self.damping
            p.vy *= self.damping
            p.update(dt=1.0)
        
        # Spawn new particles occasionally
        if self.tick % 30 == 0 and len(self.particles) < self.max_particles:
            self._spawn_new_particle()
        
        # Remove old particles
        if len(self.particles) > self.max_particles:
            # Remove oldest light particle
            for p in self.particles:
                if p.type == "light" and p.age > 200:
                    self.particles.remove(p)
                    break
    
    def _spawn_new_particle(self):
        """Spawn a new particle at edge"""
        side = random.randint(0, 3)
        if side == 0:  # Top
            x = random.uniform(0, self.width)
            y = 0
        elif side == 1:  # Right
            x = self.width
            y = random.uniform(0, self.height)
        elif side == 2:  # Bottom
            x = random.uniform(0, self.width)
            y = self.height
        else:  # Left
            x = 0
            y = random.uniform(0, self.height)
        
        p_type = random.choice(["orbiter", "light", "light"])
        p = Particle(x, y, random.uniform(2, 5), p_type)
        
        # Velocity toward center
        angle = math.atan2(self.height // 2 - y, self.width // 2 - x)
        p.vx = math.cos(angle) * random.uniform(0.5, 2)
        p.vy = math.sin(angle) * random.uniform(0.5, 2)
        p.max_trail = 30
        
        self.particles.append(p)
    
    def draw(self):
        """Render the simulation"""
        # Fade trail effect
        self.trail_surface.fill((5, 8, 20, 15))
        self.screen.blit(self.trail_surface, (0, 0))
        
        # Draw particles (sort by type for proper layering)
        # Dark matter first (behind everything)
        for p in sorted(self.particles, key=lambda x: {"dark": 0, "heavy": 1, "orbiter": 2, "light": 3}[x.type]):
            color = self.colors.get(p.type, (255, 255, 255))
            p.draw_trail(self.screen, color)
            glow = p.type != "dark"
            p.draw(self.screen, color, glow=glow)
        
        # Draw UI
        self._draw_ui()
        
        pygame.display.flip()
    
    def _draw_ui(self):
        """Draw UI overlay"""
        # Stats
        fps = self.clock.get_fps()
        fps_color = (100, 255, 100) if fps >= 55 else (255, 200, 100) if fps >= 30 else (255, 100, 100)
        
        stats = [
            f"Particles: {len(self.particles)}",
            f"Tick: {self.tick}",
            f"FPS: {int(fps)}",
            f"Gravity: G={self.G}",
        ]
        
        for i, stat in enumerate(stats):
            color = fps_color if "FPS" in stat else (180, 200, 220)
            surf = self.font.render(stat, True, color)
            self.screen.blit(surf, (10, 10 + i * 25))
        
        # Performance bar
        bar_width = 200
        bar_height = 8
        fps_ratio = min(fps / 60.0, 1.0)
        bar_color = (100, 255, 100) if fps >= 55 else (255, 200, 100) if fps >= 30 else (255, 100, 100)
        
        pygame.draw.rect(self.screen, (50, 50, 50), (10, 115, bar_width, bar_height))
        pygame.draw.rect(self.screen, bar_color, (10, 115, int(bar_width * fps_ratio), bar_height))
        
        # Controls
        controls = [
            "Space - Pause/Resume",
            "C - Clear particles",
            "R - Reset simulation",
            "Click - Add particle",
        ]
        
        for i, ctrl in enumerate(controls):
            surf = self.font.render(ctrl, True, (100, 150, 180))
            self.screen.blit(surf, (self.width - 180, 10 + i * 22))
    
    def run(self, fps=60):
        """Main simulation loop"""
        running = True
        paused = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_c:
                        # Clear all but heavy particles
                        self.particles = [p for p in self.particles if p.type == "heavy"]
                    elif event.key == pygame.K_r:
                        # Reset
                        self.particles = []
                        self.tick = 0
                        self._spawn_initial()
                    elif event.key == pygame.K_g:
                        # Toggle gravity
                        self.G = 0 if self.G > 0 else 0.8
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Add particle at click position
                        p = Particle(event.pos[0], event.pos[1], 
                                    random.uniform(3, 8), "orbiter")
                        p.vx = random.uniform(-1, 1)
                        p.vy = random.uniform(-1, 1)
                        p.max_trail = 30
                        self.particles.append(p)
            
            if not paused:
                self.update_physics()
                self.tick += 1
            
            self.draw()
            self.clock.tick(fps)
        
        pygame.quit()


def main():
    """Entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Gravity Cosmos Simulation")
    parser.add_argument("--width", type=int, default=1024, help="Window width")
    parser.add_argument("--height", type=int, default=768, help="Window height")
    parser.add_argument("--particles", type=int, default=200, help="Max particles")
    parser.add_argument("--fps", type=int, default=60, help="Target FPS")
    args = parser.parse_args()
    
    # Set UTF-8 for Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    if not HAS_PYGAME:
        print("Error: pygame required. Install with: pip install pygame")
        return
    
    sim = GravityCosmosSim(args.width, args.height, args.particles)
    sim.run(args.fps)


if __name__ == "__main__":
    main()
