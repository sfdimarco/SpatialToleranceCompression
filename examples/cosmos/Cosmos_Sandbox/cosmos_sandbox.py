#!/usr/bin/env python3
"""
Cosmos Sandbox v2 - Emergent Cosmic Life Simulation
=====================================================

A sandbox simulation where players discover balanced systems
that can support emergent life forms.

Inspired by charged-gravity cosmic simulators with:
- Charged particles (+/-) with gravity
- Like-charge boost attraction
- Fusion with E=mc² flare effects
- Black hole formation with blue/yellow penumbra
- Temperature system
- Habitable zone detection
- Emergent life forms

All powered by .geo rules!

Run: python cosmos_sandbox.py
Controls:
  - Mouse Click: Add particle
  - Right Click: Add black hole
  - Space: Pause/Resume
  - R: Reset
  - H: Toggle habitable zone overlay
  - L: Toggle life overlay
  - Esc: Quit
"""

import sys
import os
import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("Error: pygame required. Install with: pip install pygame")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# TUNABLE CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

G_CONST = 0.05          # Gravitational constant (weaker for smoother motion)
LIKE_BOOST = 2.5        # Extra attraction for like charges
MERGE_DIST = 6          # Fusion radius in pixels
BH_THRESHOLD = 400      # Mass threshold for black hole formation
EMIT_RATE = 45          # Frames between emitted particles
START_COUNT = 80        # Initial particle count
C_SIM = 30              # "Speed of light" for E=mc² visualization
TEMP_MIN = 20           # Minimum habitable temperature
TEMP_MAX = 40           # Maximum habitable temperature
LIFE_CHANCE = 0.02      # Base chance for life to emerge

# Black hole collision constants
BH_INSPIRAL_DIST = 80   # Distance when BH start spiraling
BH_MERGE_DIST = 20      # Distance when BH merge
GRAV_WAVE_SPEED = 15    # Speed of gravitational wave propagation
GRAV_WAVE_STRENGTH = 10 # Initial wave strength
KICK_VELOCITY_MIN = 5   # Minimum recoil kick velocity
KICK_VELOCITY_MAX = 20  # Maximum recoil kick velocity


# ═══════════════════════════════════════════════════════════════════════════════
# PARTICLE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Particle:
    """Cosmic particle with charge, mass, and temperature"""
    x: float
    y: float
    mass: float = 4.0
    charge: int = 1     # +1 or -1
    vx: float = 0.0
    vy: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    is_bh: bool = False
    flare: float = 0.0
    temperature: float = 25.0
    age: int = 0
    is_life: bool = False
    life_type: int = 0
    alive: bool = True
    
    # Black hole specific
    inspiraling: bool = False
    orbital_speed: float = 0.0
    merge_timer: int = 0
    kicking: bool = False
    kick_vx: float = 0.0
    kick_vy: float = 0.0
    kick_decay: int = 0
    bh_age: int = 0
    pending_gw_emission: tuple = None  # (x, y, energy)
    
    # Gravitational wave
    is_grav_wave: bool = False
    wave_strength: float = 0.0
    wave_dist: float = 0.0
    
    def __post_init__(self):
        self.radius = math.pow(self.mass, 1/3) * 2
    
    def apply_force(self, fx: float, fy: float):
        """Apply force to particle (F = ma)"""
        if self.is_bh:
            return
        if self.mass > 0:
            self.ax += fx / self.mass
            self.ay += fy / self.mass
    
    def physics(self, particles: List['Particle'], width: int, height: int):
        """Apply gravitational forces from all other particles"""
        # Black hole specific physics
        if self.is_bh:
            self._bh_physics(particles)
            return
        
        # Regular particle physics
        for other in particles:
            if other is self or not other.alive:
                continue

            dx = other.x - self.x
            dy = other.y - self.y
            dist_sq = max(1, min(dx*dx + dy*dy, 1e6))
            dist = math.sqrt(dist_sq)

            # Gravitational force with like-charge boost
            like_charge = (self.charge == other.charge)
            boost = LIKE_BOOST if like_charge else 1.0

            force = (G_CONST * self.mass * other.mass * boost) / dist_sq

            # Apply force direction
            fx = (dx / dist) * force
            fy = (dy / dist) * force
            self.apply_force(fx, fy)

            # Fusion for like-charged particles
            if not other.is_bh and self.charge == other.charge and dist < MERGE_DIST:
                self.merge(other)
    
    def _bh_physics(self, particles: List['Particle']):
        """Black hole specific physics including inspiral and mergers"""
        # Find other black holes
        other_bhs = [p for p in particles if p.is_bh and p is not self and p.alive]
        
        for other in other_bhs:
            dx = other.x - self.x
            dy = other.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Inspiral phase - black holes spiral toward each other
            if dist < BH_INSPIRAL_DIST and not self.inspiraling:
                self.inspiraling = True
                other.inspiraling = True
            
            if self.inspiraling:
                # Spiral inward with increasing speed
                self.orbital_speed += 0.1
                # Move toward other BH
                if dist > BH_MERGE_DIST:
                    self.x += (dx / dist) * self.orbital_speed * 0.5
                    self.y += (dy / dist) * self.orbital_speed * 0.5
            
            # Merger event!
            if dist < BH_MERGE_DIST and self.orbital_speed >= 3:
                self._merge_black_holes(other)
        
        # Handle recoil kick
        if self.kicking:
            self.x += self.kick_vx
            self.y += self.kick_vy
            self.kick_decay += 1
            
            # Dynamical friction slows the kick
            if self.kick_decay >= 100:
                self.kicking = False
                self.kick_vx = 0
                self.kick_vy = 0
    
    def _merge_black_holes(self, other: 'Particle'):
        """Merge two black holes with gravitational wave emission"""
        # Calculate wave energy from orbital kinetic energy
        wave_energy = (self.mass + other.mass) * (self.orbital_speed ** 2) / 100
        
        # Emit gravitational waves (expanding ripples in spacetime)
        # Will be processed by simulation manager
        self.pending_gw_emission = (self.x, self.y, wave_energy)
        
        # Calculate asymmetric kick (70% chance)
        if random.random() < 0.7:
            self.kicking = True
            self.kick_vx = random.uniform(KICK_VELOCITY_MIN, KICK_VELOCITY_MAX) * random.choice([-1, 1])
            self.kick_vy = random.uniform(KICK_VELOCITY_MIN, KICK_VELOCITY_MAX) * random.choice([-1, 1])
        
        # Merge properties
        self.mass = self.mass + other.mass
        self.radius = math.pow(self.mass, 1/3) * 2
        self.orbital_speed = 0
        self.inspiraling = False
        self.bh_age = 0
        
        # Massive flare from merger (brighter than all stars!)
        self.flare = max(self.flare, wave_energy * 5)
        
        # Mark other for removal
        other.alive = False
        other.is_bh = False
    
    def merge(self, other: 'Particle'):
        """Merge with another particle (conserving momentum)"""
        if other.is_bh or other is self:
            return
        
        total_mass = self.mass + other.mass
        
        # Conserve momentum
        if total_mass > 0:
            self.vx = (self.vx * self.mass + other.vx * other.mass) / total_mass
            self.vy = (self.vy * self.mass + other.vy * other.mass) / total_mass
        
        # E = mc² flare effect (visual only)
        energy_release = (other.mass * (C_SIM ** 2)) / 5000
        self.flare = max(self.flare, energy_release)
        
        # Update properties
        self.mass = total_mass
        self.radius = math.pow(self.mass, 1/3) * 2
        other.alive = False
        
        # Check for black hole formation
        if self.mass >= BH_THRESHOLD:
            self.is_bh = True
            self.vx = 0
            self.vy = 0
    
    def update(self, dt: float, width: int, height: int):
        """Update particle position and state"""
        if not self.is_bh:
            # Integrate motion
            self.vx += self.ax * dt
            self.vy += self.ay * dt
            
            # Velocity damping for stability
            self.vx *= 0.995
            self.vy *= 0.995
            
            self.x += self.vx * dt
            self.y += self.vy * dt
        
        # Reset acceleration
        self.ax = 0
        self.ay = 0
        
        # Edge wrapping for smooth orbits
        self.x = self.x % width
        self.y = self.y % height
        
        # Age and flare decay
        self.age += int(dt)
        self.flare = max(0, self.flare - 2 * dt)
        
        # Temperature regulation
        self._update_temperature(dt)
    
    def _update_temperature(self, dt: float):
        """Update particle temperature based on environment"""
        # Cool down over time
        self.temperature = max(25, self.temperature - 0.5 * dt)
        
        # Heat from flare
        if self.flare > 0:
            self.temperature += self.flare * 0.5
    
    def draw(self, screen: pygame.Surface, show_habitable: bool = False, show_life: bool = False):
        """Render particle"""
        x, y = int(self.x), int(self.y)
        
        if self.is_bh:
            # Black hole core
            pygame.draw.circle(screen, (0, 0, 0), (x, y), max(8, int(self.radius)))
            
            # Inner blue halo
            blue_radius = int(self.radius) + 14
            blue_surf = pygame.Surface((blue_radius * 2, blue_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(blue_surf, (100, 200, 255, 80), (blue_radius, blue_radius), blue_radius)
            screen.blit(blue_surf, (x - blue_radius, y - blue_radius))
            
            # Outer yellow penumbra
            yellow_radius = int(self.radius) + 28
            yellow_surf = pygame.Surface((yellow_radius * 2, yellow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(yellow_surf, (255, 230, 80, 60), (yellow_radius, yellow_radius), yellow_radius)
            screen.blit(yellow_surf, (x - yellow_radius, y - yellow_radius))
            
        elif self.is_life:
            # Life form (purple with glow)
            life_color = (180, 120, 255) if self.life_type == 1 else (220, 150, 255)
            
            # Glow
            glow_radius = int(self.radius) + 8
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*life_color, 100), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (x - glow_radius, y - glow_radius))
            
            # Core
            pygame.draw.circle(screen, life_color, (x, y), int(self.radius))
            
        else:
            # Regular particle
            color = (255, 107, 107) if self.charge > 0 else (78, 205, 196)
            pygame.draw.circle(screen, color, (x, y), max(3, int(self.radius)))
            
            # Flare effect
            if self.flare > 0:
                flare_radius = int(self.radius) + int(self.flare / 5)
                flare_surf = pygame.Surface((flare_radius * 2, flare_radius * 2), pygame.SRCALPHA)
                flare_alpha = min(255, int(self.flare * 10))
                pygame.draw.circle(flare_surf, (255, 240, 120, flare_alpha), 
                                  (flare_radius, flare_radius), flare_radius)
                screen.blit(flare_surf, (x - flare_radius, y - flare_radius))
        
        # Habitable zone overlay
        if show_habitable and TEMP_MIN <= self.temperature <= TEMP_MAX:
            pygame.draw.circle(screen, (100, 255, 100), (x, y), int(self.radius) + 12, 2)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN SIMULATION CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class CosmosSandbox:
    """Main cosmos sandbox simulation"""
    
    def __init__(self, width: int = 1024, height: int = 768):
        self.width = width
        self.height = height
        self.particles: List[Particle] = []
        self.gravitational_waves: List[Particle] = []  # Separate list for GW
        self.tick = 0
        self.emit_timer = 0
        self.paused = False
        self.show_habitable = False
        self.show_life = False
        
        # Statistics
        self.total_fusions = 0
        self.black_holes_formed = 0
        self.black_holes_merged = 0
        self.life_forms = 0
        self.habitable_count = 0
        self.gravitational_waves_emitted = 0
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Cosmos Sandbox v2 - Black Hole Collisions & Gravitational Waves")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initial seeding
        self._seed_initial()
    
    def _seed_initial(self):
        """Seed initial particle population"""
        for _ in range(START_COUNT):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            mass = random.uniform(3, 8)
            charge = 1 if random.random() < 0.5 else -1
            
            p = Particle(x, y, mass, charge)
            p.vx = random.uniform(-0.3, 0.3)
            p.vy = random.uniform(-0.3, 0.3)
            self.particles.append(p)
    
    def emit_particle(self):
        """Emit new particle from center"""
        cx, cy = self.width / 2, self.height / 2
        mass = random.uniform(3, 8)
        charge = 1 if random.random() < 0.5 else -1
        
        p = Particle(cx, cy, mass, charge)
        
        # Small radial kick outward
        angle = random.uniform(0, math.pi * 2)
        p.vx = math.cos(angle) * 0.5
        p.vy = math.sin(angle) * 0.5
        
        self.particles.append(p)
    
    def update(self, dt: float = 1.0):
        """Update simulation state"""
        if self.paused:
            return
        
        self.tick += int(dt)
        
        # Continuous emitter
        if self.emit_timer <= 0:
            self.emit_particle()
            self.emit_timer = EMIT_RATE
        self.emit_timer -= dt
        
        # Physics integration
        for p in self.particles:
            if p.alive:
                p.physics(self.particles, self.width, self.height)
        
        # Process pending gravitational wave emissions from BH mergers
        for p in self.particles:
            if p.alive and p.is_bh and hasattr(p, 'pending_gw_emission') and p.pending_gw_emission:
                x, y, energy = p.pending_gw_emission
                self._emit_gravitational_wave(x, y, energy)
                p.pending_gw_emission = None
                self.black_holes_merged += 1
        
        # Update positions
        for p in self.particles:
            if p.alive:
                p.update(dt, self.width, self.height)
        
        # Update gravitational waves
        self._update_gravitational_waves(dt)
        
        # Apply gravitational wave effects to particles
        self._apply_gravitational_wave_effects(dt)
        
        # Check for life emergence
        self._check_life_emergence()
        
        # Cleanup dead particles
        self.particles = [p for p in self.particles if p.alive]
        
        # Update statistics
        self._update_stats()
    
    def _emit_gravitational_wave(self, x: float, y: float, strength: float):
        """Emit gravitational wave from black hole merger"""
        # Create expanding ring of gravitational wave particles
        num_wave_particles = 16
        for i in range(num_wave_particles):
            angle = (i / num_wave_particles) * math.pi * 2
            wave = Particle(x, y, mass=0, charge=0)
            wave.is_grav_wave = True
            wave.wave_strength = strength
            wave.vx = math.cos(angle) * GRAV_WAVE_SPEED
            wave.vy = math.sin(angle) * GRAV_WAVE_SPEED
            wave.alive = True
            self.gravitational_waves.append(wave)
        
        self.gravitational_waves_emitted += 1
    
    def _update_gravitational_waves(self, dt: float):
        """Update gravitational wave propagation"""
        for wave in self.gravitational_waves:
            wave.x += wave.vx * dt
            wave.y += wave.vy * dt
            wave.wave_dist += GRAV_WAVE_SPEED * dt
            
            # Wave dissipates with distance
            wave.wave_strength = max(0, wave.wave_strength - 0.3 * dt)
            
            # Wave dies out after traveling far enough
            if wave.wave_dist >= 200 or wave.wave_strength <= 0:
                wave.alive = False
        
        # Cleanup
        self.gravitational_waves = [w for w in self.gravitational_waves if w.alive]
    
    def _apply_gravitational_wave_effects(self, dt: float):
        """Apply gravitational wave effects to nearby particles"""
        for wave in self.gravitational_waves:
            if not wave.alive:
                continue
            
            # Affect particles near the wave
            for p in self.particles:
                if not p.alive or p.is_bh:
                    continue
                
                dx = p.x - wave.x
                dy = p.y - wave.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Wave affects particles within range
                if dist < 50:
                    # Stretch and compress space (random velocity perturbation)
                    p.vx += random.uniform(-2, 2) * (wave.wave_strength / 10)
                    p.vy += random.uniform(-2, 2) * (wave.wave_strength / 10)
                    
                    # Heat from wave energy
                    p.temperature += wave.wave_strength * 0.5
                    
                    # Can disrupt habitable zones
                    if p.temperature > TEMP_MAX:
                        pass  # Temperature handling is in particle update
    
    def _check_life_emergence(self):
        """Check for life emergence in habitable zones"""
        for p in self.particles:
            if not p.alive or p.is_life or p.is_bh:
                continue
            
            # Check habitable conditions
            is_habitable = (
                TEMP_MIN <= p.temperature <= TEMP_MAX and
                20 <= p.mass <= 100 and
                p.age > 100
            )
            
            if is_habitable and random.random() < LIFE_CHANCE:
                p.is_life = True
                p.life_type = 1
                self.life_forms += 1
    
    def _update_stats(self):
        """Update simulation statistics"""
        self.black_holes_formed = sum(1 for p in self.particles if p.is_bh)
        self.life_forms = sum(1 for p in self.particles if p.is_life)
        self.habitable_count = sum(
            1 for p in self.particles 
            if TEMP_MIN <= p.temperature <= TEMP_MAX
        )
    
    def draw(self):
        """Render simulation"""
        # Fade trail effect
        fade_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        fade_surf.fill((5, 10, 25, 50))
        self.screen.blit(fade_surf, (0, 0))
        
        # Draw particles
        for p in self.particles:
            if p.alive:
                p.draw(self.screen, self.show_habitable, self.show_life)
        
        # Draw gravitational waves (ripples in spacetime)
        for wave in self.gravitational_waves:
            if wave.alive:
                self._draw_gravitational_wave(wave)

        # Draw UI
        self._draw_ui()

        pygame.display.flip()
    
    def _draw_gravitational_wave(self, wave: Particle):
        """Draw gravitational wave ripple"""
        x, y = int(wave.x), int(wave.y)
        alpha = int(wave.wave_strength * 25)
        
        # Ripple ring effect
        ring_radius = int(wave.wave_dist) + 10
        
        # Draw ripple as expanding ring
        if ring_radius > 5 and alpha > 0:
            ripple_surf = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(ripple_surf, (200, 200, 255, alpha), (ring_radius, ring_radius), ring_radius, 3)
            self.screen.blit(ripple_surf, (x - ring_radius, y - ring_radius))
    
    def _draw_ui(self):
        """Draw UI overlay"""
        fps = self.clock.get_fps()
        
        # Statistics panel
        stats = [
            f"Particles: {len(self.particles)}",
            f"Black Holes: {self.black_holes_formed}",
            f"BH Mergers: {self.black_holes_merged}",
            f"Grav Waves: {self.gravitational_waves_emitted}",
            f"Life Forms: {self.life_forms}",
            f"Habitable: {self.habitable_count}",
            f"FPS: {int(fps)}",
        ]
        
        y = 10
        for stat in stats:
            color = (100, 255, 100) if "FPS" in stat and fps >= 55 else (200, 200, 200)
            surf = self.small_font.render(stat, True, color)
            self.screen.blit(surf, (10, y))
            y += 22
        
        # Controls
        controls = [
            "Click - Add particle",
            "Right Click - Add black hole",
            "Space - Pause/Resume",
            "H - Toggle habitable zone",
            "L - Toggle life overlay",
            "R - Reset",
        ]
        
        y = 10
        for ctrl in controls:
            surf = self.small_font.render(ctrl, True, (100, 150, 180))
            self.screen.blit(surf, (self.width - 200, y))
            y += 20
        
        # Status
        status = "PAUSED" if self.paused else "RUNNING"
        status_color = (255, 255, 0) if self.paused else (100, 255, 100)
        status_surf = self.font.render(f"Status: {status}", True, status_color)
        self.screen.blit(status_surf, (self.width / 2 - 60, 10))
    
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
                elif event.key == pygame.K_h:
                    self.show_habitable = not self.show_habitable
                elif event.key == pygame.K_l:
                    self.show_life = not self.show_life
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click - add particle
                    mass = random.uniform(4, 12)
                    charge = 1 if random.random() < 0.5 else -1
                    p = Particle(event.pos[0], event.pos[1], mass, charge)
                    self.particles.append(p)
                
                elif event.button == 3:  # Right click - add black hole
                    p = Particle(event.pos[0], event.pos[1], BH_THRESHOLD + 50, 0)
                    p.is_bh = True
                    self.particles.append(p)
        
        return True
    
    def _reset(self):
        """Reset simulation"""
        self.particles = []
        self.gravitational_waves = []
        self.tick = 0
        self.emit_timer = 0
        self.total_fusions = 0
        self.black_holes_formed = 0
        self.black_holes_merged = 0
        self.gravitational_waves_emitted = 0
        self.habitable_count = 0
        self.life_forms = 0
        self.show_habitable = False
        self.show_life = False
        self._seed_initial()
    
    def run(self, fps: int = 60):
        """Main simulation loop"""
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
    """Entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Cosmos Sandbox v2")
    parser.add_argument("--width", type=int, default=1024, help="Window width")
    parser.add_argument("--height", type=int, default=768, help="Window height")
    parser.add_argument("--fps", type=int, default=60, help="Target FPS")
    args = parser.parse_args()
    
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    if not HAS_PYGAME:
        print("Error: pygame required. Install with: pip install pygame")
        return
    
    sim = CosmosSandbox(args.width, args.height)
    sim.run(args.fps)


if __name__ == "__main__":
    main()
