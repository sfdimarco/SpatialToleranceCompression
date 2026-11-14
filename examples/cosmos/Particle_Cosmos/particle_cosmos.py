#!/usr/bin/env python3
"""
Particle Cosmos - FULL .geo Physics Simulation
===============================================

ALL physics calculations are done by .geo scripts.
Python only handles:
  - Rendering
  - User input
  - Grid management
  - Particle spawning

Physics in .geo:
  - F = G*m1*m2/r² (gravitational attraction)
  - Like-charge boost (2.5x stronger)
  - Fusion with E=mc² flare
  - Black hole formation
  - Velocity damping
  - Mass accumulation

Run: python examples/cosmos/particle_cosmos.py
Or:  Double-click RUN_PARTICLE_COSMOS.bat
"""

import sys
import os
import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Add project root for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("Error: pygame required. Install with: pip install pygame")
    sys.exit(1)

from src import (
    parse_geo_script, load_geo, validate_geo,
    Grid, Node,
    GATES, Y_LOOP, X_LOOP, Z_LOOP, DIAG_LOOP,
    family_of, next_mask, mask_quadrants
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Display constants
CELL_SIZE = 16.0          # Size of each grid cell in pixels
GRID_COLS = 64            # Grid width in cells
GRID_ROWS = 48            # Grid height in cells
WINDOW_WIDTH = GRID_COLS * CELL_SIZE
WINDOW_HEIGHT = GRID_ROWS * CELL_SIZE

# Physics constants (MUST MATCH .geo script)
G_CONST = 0.05            # Gravitational constant
LIKE_BOOST = 2.5          # Like-charge multiplier
MERGE_DIST = 6            # Fusion distance
BH_THRESHOLD = 400        # Black hole mass threshold
DAMPING = 0.995           # Velocity damping

# Simulation
EMIT_RATE = 30            # Frames between emissions
START_COUNT = 50          # Initial particles
FPS = 60                  # Target frame rate

# Mask encoding
MASK_POSITIVE = 0b1000    # Y_LOOP[0] - positive charge
MASK_NEGATIVE = 0b0100    # Y_LOOP[1] - negative charge
MASK_BLACKHOLE = 0b1111   # GATE_ON - black hole
MASK_DEAD = 0b0000        # GATE_OFF - dead/void


# ═══════════════════════════════════════════════════════════════════════════════
# PARTICLE CLASS (for spawning, not physics)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SpawnParticle:
    """Simple particle for spawning into grid"""
    grid_r: int
    grid_c: int
    mass: float
    charge: int  # +1 or -1


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN SIMULATION CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class ParticleCosmosGeo:
    """
    Particle cosmos with ALL physics in .geo scripts.
    
    Python responsibilities:
      - Create and manage Grid
      - Render cells based on their state
      - Handle user input
      - Spawn new particles
    
    .geo responsibilities (particle_cosmos.geo):
      - ALL physics calculations
      - Gravitational attraction
      - Fusion mechanics
      - Black hole formation
      - Velocity updates
      - Mass changes
    """
    
    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.tick = 0
        self.emit_timer = 0
        self.paused = False
        
        # Calculate grid dimensions
        self.cols = int(width // CELL_SIZE)
        self.rows = int(height // CELL_SIZE)
        
        # Statistics
        self.stats = {
            'particles': 0,
            'black_holes': 0,
            'total_mass': 0,
            'fps': 0,
        }
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Particle Cosmos - FULL .geo Physics")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Load .geo script (ALL physics is in here)
        self.geo_program = self._load_geo()
        
        # Create grid (physics state managed by .geo)
        self.grid = self._create_grid()
        
        # Seed initial particles
        self._seed_initial()
    
    def _load_geo(self):
        """Load particle_cosmos.geo - contains ALL physics rules"""
        geo_path = os.path.join(os.path.dirname(__file__), 'particle_cosmos.geo')
        
        if not os.path.exists(geo_path):
            print(f"ERROR: .geo file not found: {geo_path}")
            print("Cannot run simulation without physics rules!")
            return None
        
        with open(geo_path, 'r', encoding='utf-8') as f:
            script = f.read()
        
        errors = validate_geo(script)
        if errors:
            print(f"Warning: .geo script has issues:")
            for err in errors[:5]:
                print(f"  Line {err.line}: {err.message}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more")
        
        print(f"Loaded .geo physics: {geo_path}")
        return parse_geo_script(script)
    
    def _create_grid(self) -> Grid:
        """Create grid for .geo physics simulation"""
        if not self.geo_program:
            return None
        
        def init_mask(r, c):
            # Start with mostly empty space
            return MASK_DEAD
        
        def init_vars(r, c, node: Node):
            # Initialize cell variables for .geo physics
            node.vars.update({
                'mass': 0,
                'charge': 0,
                'vx': 0,
                'vy': 0,
                'flare': 0,
                'bh': 0,
                'fuse_cooldown': 0,
            })
        
        grid = Grid.make(
            self.rows, self.cols,
            self.geo_program,
            init_mask_fn=init_mask,
            cell_size=CELL_SIZE
        )
        
        # Initialize variables for all cells
        for r in range(grid.rows):
            for c in range(grid.cols):
                init_vars(r, c, grid.cells[r][c])
        
        return grid
    
    def _seed_initial(self):
        """Seed initial particles into grid"""
        for _ in range(START_COUNT):
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            mass = random.uniform(20, 60)
            charge = random.choice([1, -1])
            
            self._spawn_particle(r, c, mass, charge)
    
    def _spawn_particle(self, r: int, c: int, mass: float, charge: int):
        """Spawn a particle at grid position"""
        if not self.grid:
            return
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        
        cell = self.grid.cells[r][c]
        
        # Set mask based on charge
        cell.mask = MASK_POSITIVE if charge > 0 else MASK_NEGATIVE
        
        # Initialize physics variables (.geo will update these)
        cell.vars.update({
            'mass': mass,
            'charge': charge,
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'flare': 0,
            'bh': 0,
            'fuse_cooldown': 0,
        })
    
    def _emit_particle(self):
        """Emit new particle from center (continuous emitter)"""
        center_r = self.rows // 2
        center_c = self.cols // 2
        
        # Spawn in a small area around center
        r = center_r + random.randint(-3, 3)
        c = center_c + random.randint(-3, 3)
        
        mass = random.uniform(20, 40)
        charge = random.choice([1, -1])
        
        self._spawn_particle(r, c, mass, charge)
    
    def update(self, dt: float = 1.0):
        """
        Update simulation.
        
        Physics flow:
          1. .geo script processes all cells
          2. Rules update mass, velocity, flare, etc.
          3. Python reads updated state for rendering
        """
        if self.paused or not self.grid:
            return
        
        self.tick += int(dt)
        
        # Continuous emitter
        if self.emit_timer <= 0:
            self._emit_particle()
            self.emit_timer = EMIT_RATE
        self.emit_timer -= dt
        
        # STEP 1: Run .geo physics (ALL calculations happen here)
        self.grid.step(self.tick)
        
        # STEP 2: Apply velocity to position (Python handles grid wrapping)
        self._apply_movement()
        
        # STEP 3: Update statistics
        self._update_stats()
    
    def _apply_movement(self):
        """Apply velocity to particle positions (with grid wrapping)"""
        if not self.grid:
            return
        
        # Snapshot current state
        moves = []
        
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid.cells[r][c]
                if cell.mask != MASK_DEAD and cell.vars.get('bh', 0) == 0:
                    vx = cell.vars.get('vx', 0)
                    vy = cell.vars.get('vy', 0)
                    
                    if abs(vx) > 0.5 or abs(vy) > 0.5:
                        # Calculate new position
                        new_c = c + int(vx * 0.5)  # Scale for grid movement
                        new_r = r + int(vy * 0.5)
                        
                        # Wrap around
                        new_c = new_c % self.cols
                        new_r = new_r % self.rows
                        
                        if (new_r, new_c) != (r, c):
                            moves.append((r, c, new_r, new_c, cell))
        
        # Apply moves (swap cells)
        for old_r, old_c, new_r, new_c, cell in moves:
            target = self.grid.cells[new_r][new_c]
            
            # Only move if target is empty or smaller mass
            if target.mask == MASK_DEAD or target.vars.get('mass', 0) < cell.vars.get('mass', 0):
                # Swap
                target.mask = cell.mask
                target.vars = dict(cell.vars)
                cell.mask = MASK_DEAD
                cell.vars = {k: 0 for k in cell.vars}
    
    def _update_stats(self):
        """Update simulation statistics"""
        if not self.grid:
            return
        
        count = 0
        bh_count = 0
        total_mass = 0
        
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid.cells[r][c]
                if cell.mask != MASK_DEAD:
                    count += 1
                    total_mass += cell.vars.get('mass', 0)
                    if cell.mask == MASK_BLACKHOLE:
                        bh_count += 1
        
        self.stats['particles'] = count
        self.stats['black_holes'] = bh_count
        self.stats['total_mass'] = total_mass
    
    def draw(self):
        """Render simulation based on .geo state"""
        # Clear with fade effect
        fade_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        fade_surf.fill((5, 10, 25, 60))
        self.screen.blit(fade_surf, (0, 0))
        
        if not self.grid:
            pygame.display.flip()
            return
        
        # Draw all cells
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid.cells[r][c]
                if cell.mask != MASK_DEAD:
                    self._draw_cell(r, c, cell)
        
        # Draw UI
        self._draw_ui()
        
        pygame.display.flip()
    
    def _draw_cell(self, r: int, c: int, cell):
        """Draw a single cell based on .geo state"""
        x = c * CELL_SIZE + CELL_SIZE / 2
        y = r * CELL_SIZE + CELL_SIZE / 2
        
        mass = cell.vars.get('mass', 0)
        flare = cell.vars.get('flare', 0)
        is_bh = cell.mask == MASK_BLACKHOLE
        
        # Calculate radius from mass
        radius = max(3, math.pow(mass, 1/3) * 2) if mass > 0 else CELL_SIZE / 3
        
        if is_bh:
            # Black hole with blue/yellow penumbra
            pygame.draw.circle(self.screen, (0, 0, 0), (int(x), int(y)), max(6, int(radius)))
            
            # Blue halo
            blue_radius = int(radius) + 10
            blue_surf = pygame.Surface((blue_radius * 2, blue_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(blue_surf, (100, 200, 255, 80), (blue_radius, blue_radius), blue_radius)
            self.screen.blit(blue_surf, (int(x) - blue_radius, int(y) - blue_radius))
            
            # Yellow penumbra
            yellow_radius = int(radius) + 20
            yellow_surf = pygame.Surface((yellow_radius * 2, yellow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(yellow_surf, (255, 230, 80, 60), (yellow_radius, yellow_radius), yellow_radius)
            self.screen.blit(yellow_surf, (int(x) - yellow_radius, int(y) - yellow_radius))
            
        else:
            # Regular particle
            charge = cell.vars.get('charge', 1)
            color = (255, 107, 107) if charge > 0 else (78, 205, 196)
            
            pygame.draw.circle(self.screen, color, (int(x), int(y)), max(2, int(radius)))
            
            # Flare effect (E=mc²)
            if flare > 0:
                flare_radius = int(radius) + int(flare / 3)
                flare_surf = pygame.Surface((flare_radius * 2, flare_radius * 2), pygame.SRCALPHA)
                flare_alpha = min(255, int(flare * 8))
                pygame.draw.circle(flare_surf, (255, 240, 120, flare_alpha),
                                  (flare_radius, flare_radius), flare_radius)
                self.screen.blit(flare_surf, (int(x) - flare_radius, int(y) - flare_radius))
    
    def _draw_ui(self):
        """Draw UI overlay"""
        self.stats['fps'] = int(self.clock.get_fps())
        
        stats = [
            f"Particles: {self.stats['particles']}",
            f"Black Holes: {self.stats['black_holes']}",
            f"Total Mass: {self.stats['total_mass']:.0f}",
            f"FPS: {self.stats['fps']}",
        ]
        
        y = 10
        for stat in stats:
            color = (100, 255, 100) if "FPS" in stat and self.stats['fps'] >= 55 else (200, 200, 200)
            surf = self.small_font.render(stat, True, color)
            self.screen.blit(surf, (10, y))
            y += 20
        
        # Controls
        controls = [
            "Click - Add particle",
            "Right Click - Black hole",
            "Space - Pause",
            "C - Clear",
            "S - Solar system",
        ]
        
        y = 10
        for ctrl in controls:
            surf = self.small_font.render(ctrl, True, (100, 150, 180))
            self.screen.blit(surf, (self.width - 160, y))
            y += 18
        
        # Physics note
        physics_note = "Physics: 100% .geo driven"
        surf = self.small_font.render(physics_note, True, (150, 100, 200))
        self.screen.blit(surf, (self.width // 2 - 80, 10))
    
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
                elif event.key == pygame.K_c:
                    self._clear()
                elif event.key == pygame.K_s:
                    self._spawn_solar_system()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                c = int(mx // CELL_SIZE)
                r = int(my // CELL_SIZE)
                
                if event.button == 1:  # Left click - add particle
                    mass = random.uniform(30, 60)
                    charge = random.choice([1, -1])
                    self._spawn_particle(r, c, mass, charge)
                
                elif event.button == 3:  # Right click - black hole
                    self._spawn_black_hole(r, c)
        
        return True
    
    def _spawn_black_hole(self, r: int, c: int):
        """Spawn a black hole at grid position"""
        if not self.grid:
            return
        
        cell = self.grid.cells[r][c]
        cell.mask = MASK_BLACKHOLE
        cell.vars.update({
            'mass': BH_THRESHOLD + 100,
            'charge': 0,
            'vx': 0,
            'vy': 0,
            'flare': 30,
            'bh': 1,
            'fuse_cooldown': 0,
        })
    
    def _clear(self):
        """Clear all particles"""
        if not self.grid:
            return
        
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid.cells[r][c]
                cell.mask = MASK_DEAD
                cell.vars = {k: 0 for k in cell.vars}
        
        self.tick = 0
        self.emit_timer = 0
    
    def _spawn_solar_system(self):
        """Spawn a mini solar system"""
        center_r = self.rows // 2
        center_c = self.cols // 2
        
        # Central massive object (not quite a black hole)
        self._spawn_particle(center_r, center_c, 350, 1)
        
        # Orbiting planets
        for i in range(4):
            dist = 4 + i * 2
            angle = (i / 4) * math.pi * 2
            
            r = center_r + int(dist * math.sin(angle))
            c = center_c + int(dist * math.cos(angle))
            
            mass = random.uniform(15, 30)
            charge = random.choice([1, -1])
            
            self._spawn_particle(r, c, mass, charge)
    
    def run(self, fps: int = FPS):
        """Main simulation loop"""
        running = True
        
        print(f"\n{'='*60}")
        print(f"Particle Cosmos - FULL .geo Physics")
        print(f"{'='*60}")
        print(f"Grid: {self.cols}x{self.rows} cells")
        print(f"Physics: particle_cosmos.geo")
        print(f"Controls: Click=particle, Right-click=BH, Space=pause")
        print(f"{'='*60}\n")
        
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
    parser = argparse.ArgumentParser(description="Particle Cosmos - FULL .geo Physics")
    parser.add_argument("--width", type=int, default=WINDOW_WIDTH, help="Window width")
    parser.add_argument("--height", type=int, default=WINDOW_HEIGHT, help="Window height")
    parser.add_argument("--fps", type=int, default=FPS, help="Target FPS")
    args = parser.parse_args()
    
    if not HAS_PYGAME:
        print("Error: pygame required. Install with: pip install pygame")
        return
    
    sim = ParticleCosmosGeo(args.width, args.height)
    sim.run(args.fps)


if __name__ == "__main__":
    main()
