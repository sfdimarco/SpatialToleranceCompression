#!/usr/bin/env python3
"""
Cosmos Infinite — Big Bang to Emergent Universe with .geo Rules
================================================================

An infinite space cosmos simulation powered by the Binary Quad-Tree Grammar Engine.
Features:
  - Infinite procedural space using chunk-based loading
  - Smooth zoom from cosmic scale (galaxies) to stellar scale (stars)
  - Big bang initialization with inflation and expansion
  - Emergent structure formation using .geo rules
  - LOD (Level of Detail) based on zoom level
  - Cell variables for mass, temperature, density, velocity

Controls:
  - Mouse Wheel: Zoom in/out
  - Left Click + Drag: Pan camera
  - Right Click: Add black hole at cursor
  - Middle Click: Add star at cursor
  - Space: Pause/Resume
  - B: Trigger mini big bang at cursor
  - R: Reset simulation
  - 1-5: Change max simulation depth (LOD)
  - H: Toggle habitable zone overlay
  - Esc: Quit

Run: python examples/cosmos/cosmos_infinite.py
"""

import sys
import os
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict

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
    Node, expand_active, draw_frame, mask_quadrants,
    GATES, Y_LOOP, X_LOOP, Z_LOOP, DIAG_LOOP,
    _FAMILY_RGB, next_mask, Grid, draw_grid_frame,
    family_of, PROGRAM_REGISTRY
)

# Path to geo files directory (all .geo files are in same folder as .py)
GEO_DIR = os.path.join(os.path.dirname(__file__))


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# World constants
CHUNK_SIZE = 16           # Size of each chunk in cells
CELL_SIZE_BASE = 8.0      # Base cell size at zoom level 0
MAX_CHUNKS = 64           # Maximum loaded chunks (memory limit)
CHUNK_CACHE = 32          # Chunks to keep in cache around viewport

# Zoom constants
MIN_ZOOM = 0.125          # Most zoomed out (1/8x)
MAX_ZOOM = 8.0            # Most zoomed in (8x)
ZOOM_SPEED = 1.15         # Zoom multiplier per wheel step

# Simulation constants
DEFAULT_DEPTH = 4         # Default quadtree recursion depth
TICKS_PER_FRAME = 1       # Simulation steps per render frame

# Physics constants (for visualization overlay)
G_CONST = 0.01            # Gravitational constant (visual only)
TEMP_HABITABLE_MIN = 30   # Habitable temperature range
TEMP_HABITABLE_MAX = 60

# Big bang constants
BIG_BANG_RADIUS = 50      # Initial explosion radius
BIG_BANG_MASS = 1000      # Initial singularity mass


# ═══════════════════════════════════════════════════════════════════════════════
# CAMERA / VIEWPORT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Camera:
    """Camera for viewing infinite cosmos with zoom support"""
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0
    target_zoom: float = 1.0  # For smooth zoom interpolation
    
    # Viewport dimensions (in world coordinates)
    viewport_width: float = 800.0
    viewport_height: float = 600.0
    
    def set_viewport_size(self, width: float, height: float):
        """Update viewport size based on window dimensions"""
        self.viewport_width = width
        self.viewport_height = height
    
    @property
    def world_left(self) -> float:
        return self.x - (self.viewport_width / 2) / self.zoom
    
    @property
    def world_right(self) -> float:
        return self.x + (self.viewport_width / 2) / self.zoom
    
    @property
    def world_top(self) -> float:
        return self.y - (self.viewport_height / 2) / self.zoom
    
    @property
    def world_bottom(self) -> float:
        return self.y + (self.viewport_height / 2) / self.zoom
    
    @property
    def cell_size(self) -> float:
        """Current cell size based on zoom level"""
        return CELL_SIZE_BASE / self.zoom
    
    def world_to_screen(self, wx: float, wy: float, screen_w: int, screen_h: int) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        sx = (wx - self.world_left) * self.zoom
        sy = (wy - self.world_top) * self.zoom
        return int(sx), int(sy)
    
    def screen_to_world(self, sx: int, sy: int, screen_w: int, screen_h: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        wx = self.world_left + sx / self.zoom
        wy = self.world_top + sy / self.zoom
        return wx, wy
    
    def update(self, dt: float):
        """Smooth zoom interpolation"""
        self.zoom += (self.target_zoom - self.zoom) * 5.0 * dt
        self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom))
    
    def zoom_in(self):
        """Zoom in one step"""
        self.target_zoom = min(MAX_ZOOM, self.target_zoom * ZOOM_SPEED)
    
    def zoom_out(self):
        """Zoom out one step"""
        self.target_zoom = max(MIN_ZOOM, self.target_zoom / ZOOM_SPEED)
    
    def get_visible_chunk_range(self) -> Tuple[int, int, int, int]:
        """Get chunk coordinate range visible in viewport (with padding)"""
        padding = CHUNK_SIZE * 2
        min_cx = int(math.floor(self.world_left / (CHUNK_SIZE * CELL_SIZE_BASE))) - 1
        max_cx = int(math.ceil(self.world_right / (CHUNK_SIZE * CELL_SIZE_BASE))) + 1
        min_cy = int(math.floor(self.world_top / (CHUNK_SIZE * CELL_SIZE_BASE))) - 1
        max_cy = int(math.ceil(self.world_bottom / (CHUNK_SIZE * CELL_SIZE_BASE))) + 1
        return min_cx, max_cx, min_cy, max_cy


# ═══════════════════════════════════════════════════════════════════════════════
# CHUNK MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Chunk:
    """A chunk of the infinite cosmos grid"""
    cx: int  # Chunk X coordinate (in chunk units)
    cy: int  # Chunk Y coordinate
    grid: Optional[Grid] = None
    age: int = 0
    last_accessed: int = 0
    
    @property
    def world_x(self) -> float:
        return self.cx * CHUNK_SIZE * CELL_SIZE_BASE
    
    @property
    def world_y(self) -> float:
        return self.cy * CHUNK_SIZE * CELL_SIZE_BASE


class ChunkManager:
    """Manages loading/unloading chunks for infinite space"""
    
    def __init__(self, program, max_depth: int = DEFAULT_DEPTH):
        self.program = program
        self.max_depth = max_depth
        self.chunks: Dict[Tuple[int, int], Chunk] = {}
        self.tick = 0
        self.chunk_cache: List[Tuple[int, int]] = []
    
    def get_chunk(self, cx: int, cy: int) -> Optional[Chunk]:
        """Get chunk at coordinates"""
        return self.chunks.get((cx, cy))
    
    def get_or_create_chunk(self, cx: int, cy: int) -> Chunk:
        """Get or create chunk at coordinates"""
        key = (cx, cy)
        if key not in self.chunks:
            # Create new chunk with initial void state
            chunk = Chunk(cx, cy)
            
            # Initialize grid with mostly void, occasional matter
            def init_mask(r, c):
                # Center region gets more matter (remnant of big bang)
                dist_from_center = math.sqrt((cx)**2 + (cy)**2)
                base_chance = max(0.02, 0.3 - dist_from_center * 0.02)
                
                rand = random.random()
                if rand < base_chance * 0.3:
                    return random.choice(Y_LOOP)  # Star
                elif rand < base_chance * 0.6:
                    return random.choice(X_LOOP)  # Gas
                elif rand < base_chance:
                    return random.choice(Z_LOOP)  # Dark matter
                return 0b0000  # Void
            
            chunk.grid = Grid.make(
                CHUNK_SIZE, CHUNK_SIZE, 
                self.program,
                init_mask_fn=init_mask,
                cell_size=CELL_SIZE_BASE
            )
            
            # Initialize cell variables after grid creation
            self._init_chunk_variables(chunk, cx, cy)
            
            self.chunks[key] = chunk
            self.chunk_cache.append(key)
        
        chunk = self.chunks[key]
        chunk.last_accessed = self.tick
        return chunk
    
    def _init_chunk_variables(self, chunk: Chunk, cx: int, cy: int):
        """Initialize cell variables for a chunk"""
        if not chunk.grid:
            return
        
        dist_from_center = math.sqrt((cx)**2 + (cy)**2)
        base_chance = max(0.02, 0.3 - dist_from_center * 0.02)
        
        for r in range(chunk.grid.rows):
            for c in range(chunk.grid.cols):
                cell = chunk.grid.cells[r][c]
                mask = cell.mask
                
                # Initialize variables based on cell type
                if mask != 0b0000:
                    cell.vars.update({
                        'mass': random.uniform(1, 20),
                        'temp': random.uniform(20, 40),
                        'density': random.uniform(5, 30),
                        'age': 0,
                        'vx': 0,
                        'vy': 0,
                    })
                else:
                    cell.vars.update({
                        'mass': 0,
                        'temp': 0,
                        'density': 0,
                        'age': 0,
                        'vx': 0,
                        'vy': 0,
                    })
    
    def update(self, ticks_per_frame: int = 1):
        """Update all loaded chunks and apply physics"""
        self.tick += ticks_per_frame

        # Update each chunk
        for key, chunk in self.chunks.items():
            for _ in range(ticks_per_frame):
                if chunk.grid:
                    # STEP 1: Run .geo physics (updates vx, vy, mass, etc.)
                    chunk.grid.step(self.tick)
                    
                    # STEP 2: Apply velocities to cell variables (Python handles this)
                    self._apply_chunk_physics(chunk)
                    
            chunk.age += ticks_per_frame

        # Cleanup old chunks if over limit
        if len(self.chunks) > MAX_CHUNKS:
            sorted_chunks = sorted(self.chunks.items(), key=lambda x: x[1].last_accessed)
            for key, _ in sorted_chunks[:len(self.chunks) - MAX_CHUNKS]:
                del self.chunks[key]
    
    def _apply_chunk_physics(self, chunk):
        """Apply velocity to cell positions after .geo physics step"""
        if not chunk.grid:
            return
        
        # Snapshot of movements to make
        moves = []
        
        for r in range(chunk.grid.rows):
            for c in range(chunk.grid.cols):
                cell = chunk.grid.cells[r][c]
                if cell.mask != 0b0000:  # Not void
                    vx = cell.vars.get('vx', 0)
                    vy = cell.vars.get('vy', 0)
                    
                    # Only move if velocity is significant
                    if abs(vx) > 0.5 or abs(vy) > 0.5:
                        # Calculate new position (scaled for grid movement)
                        new_c = c + int(vx * 0.3)
                        new_r = r + int(vy * 0.3)
                        
                        # Wrap around chunk
                        new_c = new_c % chunk.grid.cols
                        new_r = new_r % chunk.grid.rows
                        
                        if (new_r, new_c) != (r, c):
                            moves.append((r, c, new_r, new_c, cell))
        
        # Apply movements (swap cells)
        for old_r, old_c, new_r, new_c, cell in moves:
            target = chunk.grid.cells[new_r][new_c]
            
            # Only move if target is empty or has less mass
            if target.mask == 0b0000 or target.vars.get('mass', 0) < cell.vars.get('mass', 0):
                # Swap cell state
                target.mask = cell.mask
                target.vars = dict(cell.vars)
                cell.mask = 0b0000
                cell.vars = {k: 0 for k in cell.vars}
    
    def ensure_chunks_loaded(self, camera: Camera):
        """Ensure chunks around camera viewport are loaded"""
        min_cx, max_cx, min_cy, max_cy = camera.get_visible_chunk_range()
        
        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                self.get_or_create_chunk(cx, cy)
    
    def get_cells_in_viewport(self, camera: Camera) -> List[Tuple[float, float, Grid, int, int]]:
        """Get all cells visible in camera viewport with their world positions"""
        cells = []
        min_cx, max_cx, min_cy, max_cy = camera.get_visible_chunk_range()
        
        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                chunk = self.get_chunk(cx, cy)
                if chunk and chunk.grid:
                    chunk_world_x = cx * CHUNK_SIZE * CELL_SIZE_BASE
                    chunk_world_y = cy * CHUNK_SIZE * CELL_SIZE_BASE
                    
                    for r in range(chunk.grid.rows):
                        for c in range(chunk.grid.cols):
                            cell_x = chunk_world_x + c * CELL_SIZE_BASE
                            cell_y = chunk_world_y + r * CELL_SIZE_BASE
                            
                            # Check if cell is in viewport
                            if (camera.world_left <= cell_x <= camera.world_right and
                                camera.world_top <= cell_y <= camera.world_bottom):
                                cells.append((cell_x, cell_y, chunk.grid, r, c))
        
        return cells


# ═══════════════════════════════════════════════════════════════════════════════
# COSMOS SIMULATION
# ═══════════════════════════════════════════════════════════════════════════════

class CosmosInfinite:
    """Main infinite cosmos simulation with support for complex multi-file .geo systems"""

    # Available simulation modes with their .geo file configurations
    SIM_MODES = {
        'default': {
            'name': 'Default Cosmos',
            'files': ['cosmos.geo'],
            'description': 'Standard big bang universe simulation'
        },
        'physics': {
            'name': 'Gravitational Physics',
            'files': ['cosmos_physics.geo'],
            'description': 'Full gravitational physics with ACCUM_VAR'
        },
        'origins': {
            'name': 'Cosmic Origins',
            'files': ['cosmic_origins.geo'],
            'description': 'Complete 4X space strategy engine'
        },
        'full': {
            'name': 'Full Simulation',
            'files': ['cosmos.geo', 'cosmos_physics.geo'],
            'description': 'Standard cosmos with gravitational physics'
        },
        'sandbox': {
            'name': 'Cosmos Sandbox',
            'files': ['cosmos_sandbox.geo'],
            'description': 'Charged-gravity sandbox'
        },
        'sim': {
            'name': 'Cosmos Sim',
            'files': ['cosmos_sim.geo'],
            'description': 'Orbital motion and fusion'
        },
        'gravity': {
            'name': 'Gravity Cosmos',
            'files': ['gravity_cosmos.geo'],
            'description': 'Gravity-focused evolution'
        },
        'gravity_sandbox': {
            'name': 'Gravity Sandbox',
            'files': ['gravity_sandbox.geo'],
            'description': 'Gravity sandbox with custom physics'
        },
    }

    def __init__(self, width: int = 1280, height: int = 720, geo_path: str = None, 
                 sim_mode: str = 'default', enable_events: bool = True):
        self.width = width
        self.height = height
        self.paused = False
        self.show_habitable = False
        self.tick = 0
        self.sim_mode = sim_mode
        self.enable_events = enable_events

        # Camera
        self.camera = Camera(x=0, y=0, zoom=1.0)
        self.camera.set_viewport_size(width, height)

        # Chunk manager
        self.chunk_mgr: Optional[ChunkManager] = None

        # Statistics
        self.stats = {
            'total_stars': 0,
            'total_gas': 0,
            'total_dark': 0,
            'total_blackholes': 0,
            'total_void': 0,
            'chunks_loaded': 0,
            'active_events': 0,
            'ai_decisions': 0,
        }

        # Initialize pygame
        pygame.init()
        caption = f"Cosmos Infinite — {self.SIM_MODES.get(sim_mode, {}).get('name', 'Custom')} Simulation"
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)

        # Load .geo script(s)
        self.program = self._load_geo_config(geo_path, sim_mode)
        self.chunk_mgr = ChunkManager(self.program)

        # Trigger initial big bang at center
        self._trigger_big_bang(0, 0)

        # Input state
        self.dragging = False
        self.last_mouse_pos = (0, 0)
    
    def _load_geo_config(self, path: str = None, sim_mode: str = 'default'):
        """Load and compose multiple .geo scripts for complex simulations"""
        # If explicit path provided, use it
        if path is not None:
            return self._load_geo(path)

        # Get file list from simulation mode
        mode_config = self.SIM_MODES.get(sim_mode, self.SIM_MODES['default'])
        files = mode_config.get('files', ['cosmos.geo'])

        print(f"Loading simulation mode: {mode_config['name']}")
        print(f"  Description: {mode_config['description']}")
        print(f"  Loading files: {files}")

        # Load and compose all .geo files from geo/cosmos directory
        programs = []
        for geo_file in files:
            geo_path = os.path.join(GEO_DIR, geo_file)
            if os.path.exists(geo_path):
                prog = self._load_geo(geo_path)
                programs.append(prog)
                print(f"  [OK] Loaded: {geo_file}")
            else:
                print(f"  [SKIP] Not found: {geo_file}")

        if not programs:
            print("Using default cosmos rules...")
            from src import Program, Rule, IF_family, SwitchFamily
            return Program([
                Rule(IF_family("Y_LOOP"), SwitchFamily("X_LOOP"), "y>x"),
                Rule(IF_family("X_LOOP"), SwitchFamily("Z_LOOP"), "x>z"),
                Rule(IF_family("Z_LOOP"), SwitchFamily("Y_LOOP"), "z>y"),
            ], name="default")

        # If only one program, return it directly
        if len(programs) == 1:
            return programs[0]

        # Compose multiple programs into a combined program
        # This merges all rules from all files
        return self._compose_programs(programs)

    def _compose_programs(self, programs: list) -> 'Program':
        """Compose multiple Program objects into a single combined program"""
        from src import Program, Rule
        
        all_rules = []
        for prog in programs:
            all_rules.extend(prog.rules)
        
        combined_name = "_composed_" + "_".join(p.name for p in programs)
        return Program(all_rules, name=combined_name)

    def _load_geo(self, path: str):
        """Load and parse a single .geo script"""
        if not os.path.exists(path):
            print(f"Error: Geo file not found: {path}")
            from src import Program, Rule, IF_family, SwitchFamily
            return Program([
                Rule(IF_family("Y_LOOP"), SwitchFamily("X_LOOP"), "y>x"),
                Rule(IF_family("X_LOOP"), SwitchFamily("Z_LOOP"), "x>z"),
                Rule(IF_family("Z_LOOP"), SwitchFamily("Y_LOOP"), "z>y"),
            ], name="default")

        with open(path, 'r', encoding='utf-8') as f:
            script = f.read()

        errors = validate_geo(script)
        if errors:
            print(f"Warning: Geo script '{os.path.basename(path)}' has issues:")
            for err in errors[:5]:
                print(f"  Line {err.line}: {err.message}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more errors")

        return parse_geo_script(script)
    
    def _trigger_big_bang(self, world_x: float, world_y: float):
        """Trigger a big bang event at world position"""
        # Find chunk at position
        chunk_cx = int(world_x // (CHUNK_SIZE * CELL_SIZE_BASE))
        chunk_cy = int(world_y // (CHUNK_SIZE * CELL_SIZE_BASE))
        
        chunk = self.chunk_mgr.get_or_create_chunk(chunk_cx, chunk_cy)
        
        # Get local cell coordinates
        local_x = int((world_x - chunk.world_x) / CELL_SIZE_BASE)
        local_y = int((world_y - chunk.world_y) / CELL_SIZE_BASE)
        
        if chunk.grid and 0 <= local_x < chunk.grid.cols and 0 <= local_y < chunk.grid.rows:
            # Create singularity (black hole) at center
            cell = chunk.grid.cells[local_y][local_x]
            cell.mask = 0b1111  # GATE_ON - black hole
            cell.vars['mass'] = BIG_BANG_MASS
            cell.vars['temp'] = 200
            cell.vars['density'] = 100
            cell.vars['age'] = 0
            
            # Blast outward - set surrounding cells to high-energy states
            blast_radius = int(BIG_BANG_RADIUS / CELL_SIZE_BASE)
            for dy in range(-blast_radius, blast_radius + 1):
                for dx in range(-blast_radius, blast_radius + 1):
                    dist = math.sqrt(dx*dx + dy*dy)
                    if 0 < dist <= blast_radius:
                        nx, ny = local_x + dx, local_y + dy
                        if 0 <= ny < chunk.grid.rows and 0 <= nx < chunk.grid.cols:
                            cell = chunk.grid.cells[ny][nx]
                            # Energy decreases with distance
                            energy = 1.0 - (dist / blast_radius)
                            
                            if energy > 0.7:
                                cell.mask = random.choice(Y_LOOP)  # Stars
                                cell.vars['temp'] = 100 + energy * 100
                                cell.vars['vx'] = (dx / dist) * energy * 10
                                cell.vars['vy'] = (dy / dist) * energy * 10
                            elif energy > 0.4:
                                cell.mask = random.choice(X_LOOP)  # Gas
                                cell.vars['density'] = 50 + energy * 50
                                cell.vars['vx'] = (dx / dist) * energy * 5
                                cell.vars['vy'] = (dy / dist) * energy * 5
                            else:
                                cell.mask = random.choice(Z_LOOP)  # Dark matter
                                cell.vars['mass'] = 50 + energy * 50
            
            print(f"Big bang triggered at ({world_x:.1f}, {world_y:.1f})")
    
    def update(self, dt: float):
        """Update simulation state"""
        if self.paused:
            return
        
        # Update camera
        self.camera.update(dt)
        
        # Ensure chunks are loaded
        self.chunk_mgr.ensure_chunks_loaded(self.camera)
        
        # Update chunks
        self.chunk_mgr.update(TICKS_PER_FRAME)
        self.tick += TICKS_PER_FRAME
        
        # Update statistics
        self._update_stats()
    
    def _update_stats(self):
        """Update simulation statistics"""
        counts = defaultdict(int)
        
        for key, chunk in self.chunk_mgr.chunks.items():
            if chunk.grid:
                for r in range(chunk.grid.rows):
                    for c in range(chunk.grid.cols):
                        cell = chunk.grid.cells[r][c]
                        family = family_of(cell.mask)
                        counts[family] += 1
        
        self.stats['total_stars'] = counts.get('Y_LOOP', 0)
        self.stats['total_gas'] = counts.get('X_LOOP', 0)
        self.stats['total_dark'] = counts.get('Z_LOOP', 0)
        self.stats['total_blackholes'] = counts.get('GATES', 0)  # Includes both 0000 and 1111
        self.stats['total_void'] = counts.get('GATES', 0)  # Will be refined
        self.stats['chunks_loaded'] = len(self.chunk_mgr.chunks)
    
    def draw(self):
        """Render simulation"""
        # Clear screen with deep space color
        self.screen.fill((5, 5, 15))
        
        # Draw all visible cells
        cells = self.chunk_mgr.get_cells_in_viewport(self.camera)
        
        for cell_x, cell_y, grid, r, c in cells:
            cell = grid.cells[r][c]
            self._draw_cell(cell, cell_x, cell_y)
        
        # Draw UI overlay
        self._draw_ui()
        
        pygame.display.flip()
    
    def _draw_cell(self, cell, world_x: float, world_y: float):
        """Draw a single cell based on its state"""
        # Convert to screen coordinates
        sx, sy = self.camera.world_to_screen(
            world_x, world_y, 
            self.width, self.height
        )
        
        # Cell size on screen
        cell_size = self.camera.cell_size
        
        # Skip if off screen
        if sx < -cell_size or sx > self.width + cell_size:
            return
        if sy < -cell_size or sy > self.height + cell_size:
            return
        
        # Determine color based on mask family
        mask = cell.mask
        family = family_of(mask)
        
        if family == 'Y_LOOP':  # Stars
            color = self._star_color(cell, mask)
            self._draw_star(sx, sy, cell_size, color)
        
        elif family == 'X_LOOP':  # Gas clouds
            color = self._gas_color(cell, mask)
            self._draw_gas(sx, sy, cell_size, color)
        
        elif family == 'Z_LOOP':  # Dark matter
            color = self._dark_matter_color(cell, mask)
            self._draw_dark_matter(sx, sy, cell_size, color)
        
        elif mask == 0b1111:  # Black hole
            self._draw_black_hole(sx, sy, cell_size, cell)
        
        elif family == 'DIAG_LOOP':  # Gravitational waves
            color = self._wave_color(cell, mask)
            self._draw_wave(sx, sy, cell_size, color)
        
        # Habitable zone overlay
        if self.show_habitable:
            temp = cell.vars.get('temp', 0)
            if TEMP_HABITABLE_MIN <= temp <= TEMP_HABITABLE_MAX:
                pygame.draw.rect(self.screen, (100, 255, 100),
                               (sx - cell_size/2, sy - cell_size/2, cell_size, cell_size), 1)
    
    def _star_color(self, cell, mask) -> Tuple[int, int, int]:
        """Determine star color based on temperature"""
        temp = cell.vars.get('temp', 50)
        
        # Temperature to color mapping (like real stars)
        if temp > 100:
            return (200, 220, 255)  # Blue-white (hot)
        elif temp > 80:
            return (255, 240, 220)  # White
        elif temp > 60:
            return (255, 230, 180)  # Yellow-white
        elif temp > 40:
            return (255, 200, 150)  # Orange
        else:
            return (255, 150, 100)  # Red (cool)
    
    def _draw_star(self, sx: int, sy: int, size: float, color: Tuple[int, int, int]):
        """Draw a star"""
        radius = max(2, int(size * 0.4))
        
        # Glow effect
        glow_radius = int(size * 0.8)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 80), (glow_radius, glow_radius), glow_radius)
        self.screen.blit(glow_surf, (sx - glow_radius, sy - glow_radius))
        
        # Core
        pygame.draw.circle(self.screen, color, (sx, sy), radius)
    
    def _gas_color(self, cell, mask) -> Tuple[int, int, int]:
        """Determine gas cloud color"""
        density = cell.vars.get('density', 20)
        # Nebula colors
        if density > 60:
            return (180, 120, 200)  # Dense purple nebula
        elif density > 30:
            return (150, 180, 220)  # Blue gas
        else:
            return (200, 180, 150)  # Pale dust
    
    def _draw_gas(self, sx: int, sy: int, size: float, color: Tuple[int, int, int]):
        """Draw gas cloud"""
        # Soft, diffuse appearance
        alpha = 150
        gas_surf = pygame.Surface((int(size) * 2, int(size) * 2), pygame.SRCALPHA)
        pygame.draw.circle(gas_surf, (*color, alpha), (int(size), int(size)), int(size))
        self.screen.blit(gas_surf, (sx - int(size), sy - int(size)))
    
    def _dark_matter_color(self, cell, mask) -> Tuple[int, int, int]:
        """Dark matter is invisible but we show a faint purple hint"""
        return (100, 50, 120)
    
    def _draw_dark_matter(self, sx: int, sy: int, size: float, color: Tuple[int, int, int]):
        """Draw dark matter as faint halo"""
        # Very subtle - dark matter is invisible, just hint at it
        alpha = 40
        dm_surf = pygame.Surface((int(size) * 2, int(size) * 2), pygame.SRCALPHA)
        pygame.draw.circle(dm_surf, (*color, alpha), (int(size), int(size)), int(size * 0.9))
        self.screen.blit(dm_surf, (sx - int(size), sy - int(size)))
    
    def _draw_black_hole(self, sx: int, sy: int, size: float, cell):
        """Draw black hole with accretion disk"""
        # Event horizon (black circle)
        bh_radius = max(4, int(size * 0.5))
        pygame.draw.circle(self.screen, (0, 0, 0), (sx, sy), bh_radius)
        
        # Accretion disk (bright ring)
        disk_radius = int(size * 0.8)
        disk_surf = pygame.Surface((disk_radius * 2, disk_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(disk_surf, (255, 200, 100, 150), (disk_radius, disk_radius), disk_radius, 3)
        self.screen.blit(disk_surf, (sx - disk_radius, sy - disk_radius))
        
        # Gravitational lensing effect (outer glow)
        lens_radius = int(size * 1.2)
        lens_surf = pygame.Surface((lens_radius * 2, lens_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(lens_surf, (200, 180, 255, 60), (lens_radius, lens_radius), lens_radius, 2)
        self.screen.blit(lens_surf, (sx - lens_radius, sy - lens_radius))
    
    def _wave_color(self, cell, mask) -> Tuple[int, int, int]:
        """Gravitational wave color"""
        return (200, 200, 255)
    
    def _draw_wave(self, sx: int, sy: int, size: float, color: Tuple[int, int, int]):
        """Draw gravitational wave as ripple"""
        alpha = 100
        wave_surf = pygame.Surface((int(size) * 2, int(size) * 2), pygame.SRCALPHA)
        pygame.draw.circle(wave_surf, (*color, alpha), (int(size), int(size)), int(size), 2)
        self.screen.blit(wave_surf, (sx - int(size), sy - int(size)))
    
    def _draw_ui(self):
        """Draw UI overlay"""
        fps = self.clock.get_fps()
        mode_info = self.SIM_MODES.get(self.sim_mode, {})
        mode_name = mode_info.get('name', 'Custom')

        # Statistics panel (top-left)
        stats = [
            f"FPS: {int(fps)}",
            f"Mode: {mode_name}",
            f"Zoom: {self.camera.zoom:.2f}x",
            f"Chunks: {self.stats['chunks_loaded']}",
            f"Stars: {self.stats['total_stars']}",
            f"Gas Clouds: {self.stats['total_gas']}",
            f"Dark Matter: {self.stats['total_dark']}",
            f"Black Holes: {self.stats['total_blackholes']}",
        ]

        # Add extra stats for complex simulations
        if self.stats.get('active_events', 0) > 0:
            stats.append(f"Active Events: {self.stats['active_events']}")
        if self.stats.get('ai_decisions', 0) > 0:
            stats.append(f"AI Decisions: {self.stats['ai_decisions']}")

        y = 10
        for stat in stats:
            color = (100, 255, 100) if "FPS" in stat and fps >= 55 else (200, 200, 200)
            surf = self.small_font.render(stat, True, color)
            self.screen.blit(surf, (10, y))
            y += 20

        # Controls (top-right)
        controls = [
            "Wheel - Zoom",
            "Drag - Pan",
            "Right Click - Black Hole",
            "Middle Click - Star",
            "B - Big Bang",
            "1-5 - LOD",
            "H - Habitable Zone",
            "Space - Pause",
            "R - Reset",
        ]

        y = 10
        for ctrl in controls:
            surf = self.small_font.render(ctrl, True, (150, 180, 220))
            rect = surf.get_rect(topright=(self.width - 10, y))
            self.screen.blit(surf, rect)
            y += 20

        # Status (center-top)
        status = "PAUSED" if self.paused else "RUNNING"
        status_color = (255, 200, 0) if self.paused else (100, 255, 100)
        status_surf = self.font.render(f"Status: {status} | Tick: {self.tick}", True, status_color)
        status_rect = status_surf.get_rect(centerx=self.width // 2, top=10)
        self.screen.blit(status_surf, status_rect)
    
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
                elif event.key == pygame.K_h:
                    self.show_habitable = not self.show_habitable
                elif event.key == pygame.K_b:
                    # Big bang at cursor
                    mx, my = pygame.mouse.get_pos()
                    wx, wy = self.camera.screen_to_world(mx, my, self.width, self.height)
                    self._trigger_big_bang(wx, wy)
                elif event.key == pygame.K_r:
                    self._reset()
                elif event.key == pygame.K_1:
                    self.chunk_mgr.max_depth = 3
                elif event.key == pygame.K_2:
                    self.chunk_mgr.max_depth = 4
                elif event.key == pygame.K_3:
                    self.chunk_mgr.max_depth = 5
                elif event.key == pygame.K_4:
                    self.chunk_mgr.max_depth = 6
                elif event.key == pygame.K_5:
                    self.chunk_mgr.max_depth = 7
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up - zoom in
                    self.camera.zoom_in()
                elif event.button == 5:  # Scroll down - zoom out
                    self.camera.zoom_out()
                elif event.button == 1:  # Left click - start drag
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                elif event.button == 3:  # Right click - add black hole
                    wx, wy = self.camera.screen_to_world(event.pos[0], event.pos[1], self.width, self.height)
                    self._add_black_hole(wx, wy)
                elif event.button == 2:  # Middle click - add star
                    wx, wy = self.camera.screen_to_world(event.pos[0], event.pos[1], self.width, self.height)
                    self._add_star(wx, wy)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.camera.x -= dx / self.camera.zoom
                    self.camera.y -= dy / self.camera.zoom
                    self.last_mouse_pos = event.pos
            
            elif event.type == pygame.VIDEORESIZE:
                self.width = event.w
                self.height = event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                self.camera.set_viewport_size(self.width, self.height)
        
        return True
    
    def _add_black_hole(self, world_x: float, world_y: float):
        """Add black hole at world position"""
        chunk_cx = int(world_x // (CHUNK_SIZE * CELL_SIZE_BASE))
        chunk_cy = int(world_y // (CHUNK_SIZE * CELL_SIZE_BASE))
        chunk = self.chunk_mgr.get_or_create_chunk(chunk_cx, chunk_cy)
        
        if chunk.grid:
            local_x = int((world_x - chunk.world_x) / CELL_SIZE_BASE) % CHUNK_SIZE
            local_y = int((world_y - chunk.world_y) / CELL_SIZE_BASE) % CHUNK_SIZE
            
            if 0 <= local_x < chunk.grid.cols and 0 <= local_y < chunk.grid.rows:
                cell = chunk.grid.cells[local_y][local_x]
                cell.mask = 0b1111
                cell.vars['mass'] = 200
                cell.vars['temp'] = 100
    
    def _add_star(self, world_x: float, world_y: float):
        """Add star at world position"""
        chunk_cx = int(world_x // (CHUNK_SIZE * CELL_SIZE_BASE))
        chunk_cy = int(world_y // (CHUNK_SIZE * CELL_SIZE_BASE))
        chunk = self.chunk_mgr.get_or_create_chunk(chunk_cx, chunk_cy)
        
        if chunk.grid:
            local_x = int((world_x - chunk.world_x) / CELL_SIZE_BASE) % CHUNK_SIZE
            local_y = int((world_y - chunk.world_y) / CELL_SIZE_BASE) % CHUNK_SIZE
            
            if 0 <= local_x < chunk.grid.cols and 0 <= local_y < chunk.grid.rows:
                cell = chunk.grid.cells[local_y][local_x]
                cell.mask = random.choice(Y_LOOP)
                cell.vars['mass'] = random.uniform(10, 50)
                cell.vars['temp'] = random.uniform(50, 100)
    
    def _reset(self):
        """Reset simulation"""
        self.chunk_mgr = ChunkManager(self.program)
        self.tick = 0
        self._trigger_big_bang(0, 0)
    
    def run(self, fps: int = 60):
        """Main simulation loop"""
        running = True
        dt = 0.0
        
        while running:
            dt = self.clock.tick(fps) / 1000.0
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Entry point"""
    import argparse
    parser = argparse.ArgumentParser(
        description="Cosmos Infinite — .geo Powered Universe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Simulation Modes:
  default         - Standard big bang universe (cosmos.geo)
  physics         - Gravitational physics with ACCUM_VAR (cosmos_physics.geo)
  full            - Standard cosmos + physics (cosmos.geo + cosmos_physics.geo)
  origins         - 4X space strategy (cosmic_origins.geo)
  sandbox         - Charged-gravity sandbox (cosmos_sandbox.geo)
  sim             - Orbital motion and fusion (cosmos_sim.geo)
  gravity         - Gravity-focused evolution (gravity_cosmos.geo)
  gravity_sandbox - Gravity sandbox (gravity_sandbox.geo)

Examples:
  python cosmos_infinite.py --mode full
  python cosmos_infinite.py --mode origins --width 1920 --height 1080
  python cosmos_infinite.py --geo custom_simulation.geo
        """
    )
    parser.add_argument("--width", type=int, default=1280, help="Window width")
    parser.add_argument("--height", type=int, default=720, help="Window height")
    parser.add_argument("--fps", type=int, default=60, help="Target FPS")
    parser.add_argument("--geo", type=str, help="Path to custom .geo script (overrides --mode)")
    parser.add_argument("--mode", type=str, default='default', 
                       choices=['default', 'physics', 'full', 'origins', 'sandbox', 'sim', 'gravity', 'gravity_sandbox'],
                       help="Simulation mode preset (default: default)")
    parser.add_argument("--no-events", action="store_true", 
                       help="Disable random events (for performance)")
    args = parser.parse_args()

    if not HAS_PYGAME:
        print("Error: pygame required. Install with: pip install pygame")
        return

    sim = CosmosInfinite(
        width=args.width, 
        height=args.height, 
        geo_path=args.geo,
        sim_mode=args.mode,
        enable_events=not args.no_events
    )
    sim.run(args.fps)


if __name__ == "__main__":
    main()
