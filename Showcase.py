#!/usr/bin/env python3
"""
Showcase.py — Interactive .geo Script Showcase for Self-Organizing Systems
===========================================================================

An interactive demonstration application that teaches users how to use `.geo` 
scripts for building self-organizing systems like animation solvers and 
game terrain generators.

Features:
  - Visual demo browser with categories (Animation, Terrain, Self-Organizing)
  - Live simulation preview with playback controls
  - Script viewer with syntax highlighting
  - Export functionality (GIF, PNG sequence, JSON for terrain)
  - Tutorial mode with annotations
  - Side-by-side comparison view

Usage:
  python Showcase.py                    # Launch GUI
  python Showcase.py --demo walk_cycle  # Run specific demo
  python Showcase.py --list             # List all available demos
  python Showcase.py --export biomes --json  # Export terrain as JSON
"""

import sys
import os
import argparse
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any
from datetime import datetime

# Import from src package
from src import (
    parse_geo_script, load_geo, validate_geo,
    Node, expand_active, draw_frame, mask_quadrants,
    GATES, Y_LOOP, X_LOOP, Z_LOOP, DIAG_LOOP,
    _FAMILY_RGB, next_mask, Grid, draw_grid_frame, family_of
)

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, FancyBboxPatch
    from matplotlib.collections import PatchCollection
    from matplotlib.animation import FuncAnimation
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. GUI features disabled.")

# Try to import PIL for GIF export
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# ══════════════════════════════════════════════════════════════════════════════
# DEMO CONFIGURATIONS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class DemoInfo:
    """Information about a showcase demo."""
    geo_file: str
    title: str
    description: str
    category: str  # "animation", "terrain", "selforg"
    concepts: List[str]
    grid_mode: bool = False
    recommended_depth: int = 5
    recommended_speed: float = 3.0
    frames: int = 60
    export_types: List[str] = field(default_factory=lambda: ["gif", "png"])
    tutorial_steps: List[Dict] = field(default_factory=list)


# Animation Demos
ANIMATION_DEMOS = [
    DemoInfo(
        geo_file="examples/animation/walk_cycle.geo",
        title="Walk Cycle",
        description="8-frame character walk cycle with phase-offset limbs for natural motion.",
        category="animation",
        concepts=["Loop family cycling", "Phase offsets", "Depth layering"],
        grid_mode=False,
        recommended_depth=4,
        recommended_speed=5.0,
        frames=30,
        export_types=["gif", "png", "json"],
        tutorial_steps=[
            {"step": 1, "title": "Body Core", "text": "Depth 0 leads the 4-tick cycle using loop families.", "tick": 4},
            {"step": 2, "title": "Arm Swing", "text": "Depth 1 arms move opposite to legs for balance.", "tick": 8},
            {"step": 3, "title": "Leg Motion", "text": "Depth 2-3 legs follow with 1-tick delay.", "tick": 12},
            {"step": 4, "title": "Foot Planting", "text": "Depth 4+ feet plant and lift in sequence.", "tick": 16},
        ]
    ),
    DemoInfo(
        geo_file="examples/animation/idle_breathe.geo",
        title="Idle Breathing",
        description="Natural breathing cycle for character idle animation with chest and belly motion.",
        category="animation",
        concepts=["Cell variables", "Conditional gating", "Subtle motion"],
        grid_mode=False,
        recommended_depth=4,
        recommended_speed=4.0,
        frames=60,
        export_types=["gif", "png"],
    ),
    DemoInfo(
        geo_file="examples/animation/attack_swing.geo",
        title="Attack Swing",
        description="Melee attack animation with windup, strike, impact, and recovery phases.",
        category="animation",
        concepts=["Precise timing", "ROTATE/FLIP transforms", "Signal emission"],
        grid_mode=False,
        recommended_depth=4,
        recommended_speed=5.0,
        frames=30,
        export_types=["gif", "png", "json"],
        tutorial_steps=[
            {"step": 1, "title": "Windup Phase", "text": "Ticks 0-8: Telegraph the attack with cocking motion.", "tick": 5},
            {"step": 2, "title": "Strike Phase", "text": "Ticks 9-14: Fast forward swing with rotation.", "tick": 12},
            {"step": 3, "title": "Impact Frame", "text": "Ticks 15-20: Hit frame with shake effect.", "tick": 17},
            {"step": 4, "title": "Recovery", "text": "Ticks 21-29: Return to guard position.", "tick": 25},
        ]
    ),
    DemoInfo(
        geo_file="examples/animation/jump_arc.geo",
        title="Jump Arc",
        description="Jump animation with parabolic trajectory, squash/stretch principles.",
        category="animation",
        concepts=["Squash/stretch", "Timing", "Arc simulation"],
        grid_mode=False,
        recommended_depth=4,
        recommended_speed=5.0,
        frames=24,
        export_types=["gif", "png"],
    ),
    DemoInfo(
        geo_file="examples/animation/morph_shape.geo",
        title="Shape Morph",
        description="Smooth transformation between circle and square using depth interpolation.",
        category="animation",
        concepts=["Interpolation", "Smooth transitions", "Depth-based resolution"],
        grid_mode=False,
        recommended_depth=3,
        recommended_speed=4.0,
        frames=32,
        export_types=["gif", "png"],
    ),
]

# Terrain Demos
TERRAIN_DEMOS = [
    DemoInfo(
        geo_file="examples/terrain/heightmap.geo",
        title="Heightmap Generator",
        description="Multi-octave noise terrain with erosion smoothing and river carving.",
        category="terrain",
        concepts=["Noise seeding", "Erosion simulation", "Flow accumulation"],
        grid_mode=True,
        recommended_depth=4,
        recommended_speed=4.0,
        frames=60,
        export_types=["gif", "png", "json"],
        tutorial_steps=[
            {"step": 1, "title": "Noise Seeding", "text": "Ticks 0-15: Random elevation points placed.", "tick": 10},
            {"step": 2, "title": "Erosion", "text": "Ticks 16-40: Cellular smoothing creates natural terrain.", "tick": 30},
            {"step": 3, "title": "River Carving", "text": "Ticks 41-60: Water flows and carves channels.", "tick": 55},
        ]
    ),
    DemoInfo(
        geo_file="examples/terrain/biomes.geo",
        title="Biome Assignment",
        description="Assign biomes based on elevation and moisture with neighbor propagation.",
        category="terrain",
        concepts=["Multi-variable conditions", "Neighbor propagation", "Transition zones"],
        grid_mode=True,
        recommended_depth=4,
        recommended_speed=4.0,
        frames=100,
        export_types=["gif", "png", "json"],
        tutorial_steps=[
            {"step": 1, "title": "Moisture Spread", "text": "Water sources spread moisture to neighbors.", "tick": 30},
            {"step": 2, "title": "Biome Rules", "text": "First matching rule wins - order matters!", "tick": 50},
            {"step": 3, "title": "Final Biomes", "text": "9 biome types from ocean to snow peaks.", "tick": 80},
        ]
    ),
    DemoInfo(
        geo_file="examples/terrain/caves.geo",
        title="Cave Generator",
        description="Cellular automata cave generation with birth/survival rules.",
        category="terrain",
        concepts=["Cellular automata", "Birth/survival rules", "Feature refinement"],
        grid_mode=True,
        recommended_depth=3,
        recommended_speed=5.0,
        frames=50,
        export_types=["gif", "png", "json"],
        tutorial_steps=[
            {"step": 1, "title": "Random Noise", "text": "Ticks 0-5: 45% walls, 55% open space.", "tick": 5},
            {"step": 2, "title": "Smoothing", "text": "Ticks 6-20: Birth=5+, Survive=4+ rules.", "tick": 15},
            {"step": 3, "title": "Final Cave", "text": "Natural cave formations with pillars and pools.", "tick": 45},
        ]
    ),
    DemoInfo(
        geo_file="examples/terrain/rivers.geo",
        title="River Network",
        description="River formation through flow accumulation and watershed carving.",
        category="terrain",
        concepts=["Flow accumulation", "Watershed carving", "Delta formation"],
        grid_mode=True,
        recommended_depth=4,
        recommended_speed=4.0,
        frames=70,
        export_types=["gif", "png", "json"],
    ),
    DemoInfo(
        geo_file="examples/terrain/erosion.geo",
        title="Hydraulic Erosion",
        description="Long-term erosion simulation with sediment transport.",
        category="terrain",
        concepts=["Sediment transport", "Terrain aging", "Feature formation"],
        grid_mode=True,
        recommended_depth=4,
        recommended_speed=4.0,
        frames=100,
        export_types=["gif", "png", "json"],
    ),
    DemoInfo(
        geo_file="examples/generative/dungeon_generator.geo",
        title="Dungeon Generator",
        description="6-phase procedural level generation with rooms and corridors.",
        category="terrain",
        concepts=["Multi-phase generation", "Cellular automata", "Room/corridor logic"],
        grid_mode=True,
        recommended_depth=3,
        recommended_speed=6.0,
        frames=80,
        export_types=["gif", "png", "json"],
        tutorial_steps=[
            {"step": 1, "title": "Phase 1: Noise", "text": "Ticks 0-10: 45% random walls.", "tick": 8},
            {"step": 2, "title": "Phase 2: Smoothing", "text": "Ticks 11-25: Cellular automata caves.", "tick": 20},
            {"step": 3, "title": "Phase 3: Rooms", "text": "Ticks 26-40: Expand floor areas.", "tick": 35},
            {"step": 4, "title": "Phase 4: Corridors", "text": "Ticks 41-55: Connect room clusters.", "tick": 50},
            {"step": 5, "title": "Phase 5: Doors", "text": "Ticks 56-70: Place doorways.", "tick": 65},
            {"step": 6, "title": "Phase 6: Polish", "text": "Ticks 71+: Remove artifacts.", "tick": 75},
        ]
    ),
]

# Self-Organizing Demos
SELFORG_DEMOS = [
    DemoInfo(
        geo_file="examples/selforg/voronoi.geo",
        title="Voronoi Diagram",
        description="Region growth from seed points with territory competition.",
        category="selforg",
        concepts=["Region growth", "Territory competition", "Signal propagation"],
        grid_mode=True,
        recommended_depth=3,
        recommended_speed=4.0,
        frames=80,
        export_types=["gif", "png"],
        tutorial_steps=[
            {"step": 1, "title": "Seed Placement", "text": "Ticks 0-10: 4-8 random seeds placed.", "tick": 8},
            {"step": 2, "title": "Region Growth", "text": "Ticks 11-50: Each region expands outward.", "tick": 40},
            {"step": 3, "title": "Boundaries", "text": "Ticks 51-80: Stable boundaries form where regions meet.", "tick": 70},
        ]
    ),
    DemoInfo(
        geo_file="examples/selforg/maze.geo",
        title="Maze Generator",
        description="Solvable maze generation via constraint-based wall growth.",
        category="selforg",
        concepts=["Constraint-based growth", "Path connectivity", "Dead-end removal"],
        grid_mode=True,
        recommended_depth=3,
        recommended_speed=5.0,
        frames=70,
        export_types=["gif", "png", "json"],
    ),
    DemoInfo(
        geo_file="examples/selforg/flow_field.geo",
        title="Flow Field",
        description="Vector field visualization with particle following.",
        category="selforg",
        concepts=["Vector field encoding", "Particle following", "Streamlines"],
        grid_mode=True,
        recommended_depth=3,
        recommended_speed=5.0,
        frames=100,
        export_types=["gif", "png"],
    ),
    DemoInfo(
        geo_file="examples/selforg/reaction_diffusion.geo",
        title="Reaction-Diffusion",
        description="Turing pattern formation with activator-inhibitor dynamics.",
        category="selforg",
        concepts=["Activator-inhibitor", "Emergent patterns", "Turing patterns"],
        grid_mode=True,
        recommended_depth=2,
        recommended_speed=6.0,
        frames=200,
        export_types=["gif", "png"],
        tutorial_steps=[
            {"step": 1, "title": "Spots (0-49)", "text": "High feed rate creates leopard-like spots.", "tick": 40},
            {"step": 2, "title": "Stripes (50-99)", "text": "Medium parameters create zebra bands.", "tick": 80},
            {"step": 3, "title": "Labyrinth (100-149)", "text": "Low feed creates coral-like maze.", "tick": 130},
            {"step": 4, "title": "Waves (150-199)", "text": "Oscillating parameters create wave fronts.", "tick": 180},
        ]
    ),
]

# Combine all demos
ALL_DEMOS = ANIMATION_DEMOS + TERRAIN_DEMOS + SELFORG_DEMOS

# Category info
CATEGORIES = {
    "animation": {
        "title": "Animation Solver",
        "description": "Generate sprite sheets and animation cycles using .geo scripts",
        "color": "#e94560",
        "icon": "🎬",
    },
    "terrain": {
        "title": "Terrain Generator",
        "description": "Create game-ready heightmaps, biomes, caves, and dungeons",
        "color": "#00d9ff",
        "icon": "🏔️",
    },
    "selforg": {
        "title": "Self-Organizing Systems",
        "description": "Emergent patterns from simple rules - Voronoi, mazes, flow fields",
        "color": "#00ff88",
        "icon": "🌀",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# EXPORT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def export_frames(geo_path: str, output_dir: str, num_frames: int = 60,
                  depth: int = 5, speed: float = 3.0, grid_mode: bool = False,
                  fps: int = 10) -> List[str]:
    """Export simulation frames as PNG images."""
    
    # Load and parse the geo script
    with open(geo_path, 'r') as f:
        script = f.read()
    
    errors = validate_geo(script)
    if errors:
        for err in errors:
            print(f"Line {err.line}: {err.message}")
        raise ValueError("Invalid geo script")
    
    prog = parse_geo_script(script)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup simulation
    if grid_mode:
        rows, cols = 8, 8
        cell_size = 16.0
        grid = Grid.make(rows, cols, prog, 
                        init_mask_fn=lambda r, c: 0b1000 if grid_mode else 0b0000,
                        cell_size=cell_size)
    else:
        root = Node(0, 0, 1, 0, 0b1000)
        grid = None
    
    exported = []
    
    # Create figure for rendering
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("#0d0d0d")
    
    for tick in range(num_frames):
        # Step simulation
        if grid:
            grid.step(tick + 1)
            draw_grid_frame(ax, grid, depth)
        else:
            prog.step_tree(root, tick + 1)
            draw_frame(ax, root, depth, colored=True)
        
        ax.set_title(f"Frame {tick + 1}/{num_frames}", fontsize=10, color="white")
        
        # Save frame
        frame_path = os.path.join(output_dir, f"frame_{tick:04d}.png")
        plt.savefig(frame_path, facecolor="#0d0d0d", bbox_inches='tight')
        exported.append(frame_path)
        print(f"Exported frame {tick+1}/{num_frames}")
        
        # Clear for next frame
        ax.clear()
    
    plt.close(fig)
    print(f"Exported {num_frames} frames to {output_dir}")
    return exported


def export_gif(geo_path: str, output_path: str, num_frames: int = 60,
               depth: int = 5, fps: int = 10, grid_mode: bool = False) -> str:
    """Export simulation as animated GIF."""
    
    if not HAS_PIL:
        raise ImportError("PIL/Pillow required for GIF export. Install with: pip install Pillow")
    
    # First export frames
    temp_dir = "_temp_export_frames"
    frame_paths = export_frames(geo_path, temp_dir, num_frames, depth, grid_mode=grid_mode)
    
    # Create GIF from frames
    images = []
    for path in frame_paths:
        images.append(Image.open(path))
    
    # Save as GIF
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=int(1000 / fps),
        loop=0
    )
    
    # Cleanup temp frames
    for path in frame_paths:
        os.remove(path)
    os.rmdir(temp_dir)
    
    print(f"Exported GIF to {output_path}")
    return output_path


def export_terrain_json(geo_path: str, output_path: str, depth: int = 4, 
                        grid_mode: bool = True) -> str:
    """Export terrain as JSON for game integration."""
    
    # Load and parse the geo script
    with open(geo_path, 'r') as f:
        script = f.read()
    
    prog = parse_geo_script(script)
    
    # Run simulation to completion (100 ticks for terrain)
    rows, cols = 8, 8
    cell_size = 16.0
    grid = Grid.make(rows, cols, prog, 
                    init_mask_fn=lambda r, c: 0b0000,
                    cell_size=cell_size)
    
    # Run simulation
    for tick in range(100):
        grid.step(tick + 1)
    
    # Extract terrain data
    terrain_data = {
        "demo": os.path.basename(geo_path).replace('.geo', ''),
        "export_time": datetime.now().isoformat(),
        "size": {"rows": rows, "cols": cols},
        "grid": [],
        "legend": {
            "0": "void/empty",
            "1": "wall/solid",
            "2": "floor/walkable",
            "3": "door",
            "4": "corridor",
            "5": "water",
            "6": "forest",
            "7": "desert",
            "8": "snow"
        },
        "cell_variables": {}
    }
    
    # Convert grid to tile IDs
    for r in range(rows):
        row_data = []
        for c in range(cols):
            cell = grid.cells[r][c]
            mask = cell.mask
            
            # Convert mask to tile type
            if mask == 0b0000:
                tile_id = 0  # void
            elif mask == 0b1111:
                tile_id = 1  # wall
            elif mask in X_LOOP:
                tile_id = 2  # floor
            elif mask in Y_LOOP:
                tile_id = 3  # door
            elif mask in Z_LOOP:
                tile_id = 4  # corridor
            else:
                tile_id = 1  # default to wall
            
            row_data.append(tile_id)
            
            # Store cell variables
            if cell.vars:
                key = f"{r}_{c}"
                terrain_data["cell_variables"][key] = cell.vars
        
        terrain_data["grid"].append(row_data)
    
    # Save JSON
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(terrain_data, f, indent=2)
    
    print(f"Exported terrain JSON to {output_path}")
    return output_path


# ══════════════════════════════════════════════════════════════════════════════
# GUI APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class ShowcaseApp:
    """Main showcase GUI application."""
    
    def __init__(self):
        if not HAS_MATPLOTLIB:
            print("Error: matplotlib required for GUI. Install with: pip install matplotlib")
            sys.exit(1)
        
        self.current_demo: Optional[DemoInfo] = None
        self.selected_category: str = "animation"
        self.running = False
        self.tick = 0
        self.grid = None
        self.root = None
        self.prog = None
        self.fig = None
        self.axes = None
        self.anim = None
        self.tutorial_mode = False
        self.current_tutorial_step = 0
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the matplotlib GUI."""
        # Create figure with panels
        self.fig = plt.figure(figsize=(18, 10), facecolor="#1a1a2e")
        self.fig.canvas.manager.set_window_title("BinaryQuadTree Showcase — Self-Organizing Systems")
        
        # Create grid spec
        gs = self.fig.add_gridspec(1, 4, width_ratios=[1, 4, 4, 2], hspace=0.1, wspace=0.1)
        
        # Demo browser panel (left)
        self.browser_ax = self.fig.add_subplot(gs[0, 0])
        self.browser_ax.set_facecolor("#16213e")
        self.browser_ax.set_xticks([])
        self.browser_ax.set_yticks([])
        
        # Main simulation view (center-left)
        self.sim_ax = self.fig.add_subplot(gs[0, 1])
        self.sim_ax.set_facecolor("#0d0d0d")
        self.sim_ax.set_xticks([])
        self.sim_ax.set_yticks([])
        
        # Script/Info panel (center-right)
        self.info_ax = self.fig.add_subplot(gs[0, 2])
        self.info_ax.set_facecolor("#16213e")
        self.info_ax.set_xticks([])
        self.info_ax.set_yticks([])
        
        # Controls panel (right)
        self.controls_ax = self.fig.add_subplot(gs[0, 3])
        self.controls_ax.set_facecolor("#1a1a2e")
        self.controls_ax.set_xticks([])
        self.controls_ax.set_yticks([])
        
        # Draw panels
        self.draw_browser_panel()
        self.draw_controls_panel()
        self.draw_info_panel()
        self.draw_welcome_screen()
        
        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
    
    def draw_browser_panel(self):
        """Draw demo browser with categories."""
        self.browser_ax.clear()
        self.browser_ax.set_facecolor("#16213e")
        self.browser_ax.set_xticks([])
        self.browser_ax.set_yticks([])
        self.browser_ax.set_title("DEMO BROWSER", color="#00d9ff", fontsize=14, fontweight='bold', pad=10)
        self.browser_ax.set_xlim(0, 1)
        self.browser_ax.set_ylim(0, 1)
        
        # Category tabs
        y = 0.92
        for cat_id, cat_info in CATEGORIES.items():
            is_selected = cat_id == self.selected_category
            rect = Rectangle((0.05, y - 0.08), 0.9, 0.07,
                           facecolor=cat_info["color"] if is_selected else "#0f3460",
                           edgecolor="#ffffff" if is_selected else cat_info["color"],
                           linewidth=3 if is_selected else 1)
            self.browser_ax.add_patch(rect)
            self.browser_ax.text(0.1, y - 0.045, f"{cat_info['icon']} {cat_info['title']}", 
                               color="white", fontsize=10, va='center', fontweight='bold')
            y -= 0.10
        
        # Demo list for selected category
        y = 0.55
        demos = self.get_demos_for_category(self.selected_category)
        
        self.demo_buttons = []
        for demo in demos:
            is_selected = self.current_demo and demo.geo_file == self.current_demo.geo_file
            rect = Rectangle((0.05, y - 0.055), 0.9, 0.05,
                           facecolor="#e94560" if is_selected else "#0f3460",
                           edgecolor="#ffffff" if is_selected else "#333333",
                           linewidth=2 if is_selected else 1)
            self.browser_ax.add_patch(rect)
            self.browser_ax.text(0.1, y - 0.03, demo.title, 
                               color="white", fontsize=9, va='center')
            self.demo_buttons.append((rect, demo))
            y -= 0.065
        
        # Store category button rects
        self.category_buttons = []
        y = 0.92
        for cat_id, cat_info in CATEGORIES.items():
            rect = Rectangle((0.05, y - 0.08), 0.9, 0.07)
            self.category_buttons.append((rect, cat_id))
            y -= 0.10
    
    def draw_controls_panel(self):
        """Draw playback controls."""
        self.controls_ax.clear()
        self.controls_ax.set_facecolor("#1a1a2e")
        self.controls_ax.set_xticks([])
        self.controls_ax.set_yticks([])
        self.controls_ax.set_title("CONTROLS", color="#00d9ff", fontsize=14, fontweight='bold', pad=10)
        self.controls_ax.set_xlim(0, 1)
        self.controls_ax.set_ylim(0, 1)
        
        y = 0.85
        
        # Playback controls
        self.controls_ax.text(0.05, y, "Playback:", color="#888888", fontsize=10, va='top')
        y -= 0.08
        
        btn_width = 0.25
        buttons = [
            ("▶", "play", "#00ff88"),
            ("⏸", "pause", "#ffaa00"),
            ("⏹", "stop", "#ff4444"),
            ("⏭", "step", "#00d9ff"),
        ]
        
        self.control_buttons = []
        x = 0.05
        for label, action, color in buttons:
            rect = Rectangle((x, y - 0.05), btn_width, 0.05,
                           facecolor=color, edgecolor="#ffffff", linewidth=1)
            self.controls_ax.add_patch(rect)
            self.controls_ax.text(x + btn_width/2, y - 0.025, label,
                                color="white", fontsize=12, ha='center', va='center')
            self.control_buttons.append((rect, action))
            x += btn_width + 0.03
        
        y -= 0.12
        
        # Speed control
        self.controls_ax.text(0.05, y, f"Speed: {self.current_demo.recommended_speed if self.current_demo else 3.0} tps",
                            color="#888888", fontsize=10, va='top')
        y -= 0.08
        
        # Export options
        self.controls_ax.text(0.05, y, "Export:", color="#888888", fontsize=10, va='top')
        y -= 0.08
        
        export_buttons = [
            ("📷 PNG", "png", "#00d9ff"),
            ("🎬 GIF", "gif", "#e94560"),
            ("📄 JSON", "json", "#00ff88"),
        ]
        
        x = 0.05
        for label, action, color in export_buttons:
            if self.current_demo and action in self.current_demo.export_types:
                rect = Rectangle((x, y - 0.05), 0.25, 0.05,
                               facecolor=color, edgecolor="#ffffff", linewidth=1)
                self.controls_ax.add_patch(rect)
                self.controls_ax.text(x + 0.125, y - 0.025, label,
                                    color="white", fontsize=8, ha='center', va='center')
                self.control_buttons.append((rect, f"export_{action}"))
            x += 0.30
        
        y -= 0.12
        
        # Tutorial mode
        tutorial_color = "#ff66aa" if self.tutorial_mode else "#333333"
        rect = Rectangle((0.05, y - 0.05), 0.4, 0.05,
                        facecolor=tutorial_color, edgecolor="#ffffff", linewidth=1)
        self.controls_ax.add_patch(rect)
        self.controls_ax.text(0.25, y - 0.025, "📖 Tutorial Mode",
                            color="white", fontsize=9, ha='center', va='center')
        self.control_buttons.append((rect, "tutorial"))
        
        y -= 0.10
        
        # Keyboard shortcuts
        y = 0.15
        self.controls_ax.text(0.05, y, "Keyboard Shortcuts:", color="#888888", fontsize=9, va='top')
        shortcuts = [
            "Space - Play/Pause",
            "R - Restart",
            "T - Toggle Tutorial",
            "S - Step Forward",
            "E - Export Frame",
        ]
        for i, shortcut in enumerate(shortcuts):
            self.controls_ax.text(0.05, y - 0.025 - i*0.025, shortcut,
                                color="#aaaaaa", fontsize=7, va='top')
    
    def draw_info_panel(self):
        """Draw script info and tutorial."""
        self.info_ax.clear()
        self.info_ax.set_facecolor("#16213e")
        self.info_ax.set_xticks([])
        self.info_ax.set_yticks([])
        self.info_ax.set_title("INFO", color="#00d9ff", fontsize=14, fontweight='bold', pad=10)
        self.info_ax.set_xlim(0, 1)
        self.info_ax.set_ylim(0, 1)
        
        if not self.current_demo:
            return
        
        y = 0.9
        
        # Demo title
        self.info_ax.text(0.05, y, self.current_demo.title, color="#ffffff", 
                         fontsize=14, va='top', fontweight='bold')
        y -= 0.06
        
        # Category badge
        cat_info = CATEGORIES.get(self.current_demo.category, {})
        rect = Rectangle((0.05, y - 0.04), 0.3, 0.035,
                        facecolor=cat_info.get("color", "#333333"),
                        edgecolor="#ffffff", linewidth=1)
        self.info_ax.add_patch(rect)
        self.info_ax.text(0.2, y - 0.022, cat_info.get("title", ""),
                         color="white", fontsize=8, ha='center', va='center')
        y -= 0.06
        
        # Description
        self.info_ax.text(0.05, y, "Description:", color="#888888", fontsize=9, va='top')
        self.info_ax.text(0.05, y - 0.035, self.current_demo.description,
                         color="#cccccc", fontsize=8, va='top', wrap=True)
        y -= 0.08
        
        # Concepts
        self.info_ax.text(0.05, y, "Key Concepts:", color="#888888", fontsize=9, va='top')
        y -= 0.03
        for concept in self.current_demo.concepts:
            self.info_ax.text(0.1, y, f"• {concept}", color="#00d9ff", 
                            fontsize=8, va='top')
            y -= 0.025
        y -= 0.02
        
        # Settings
        self.info_ax.text(0.05, y, "Settings:", color="#888888", fontsize=9, va='top')
        y -= 0.03
        settings = [
            f"Depth: {self.current_demo.recommended_depth}",
            f"Speed: {self.current_demo.recommended_speed} tps",
            f"Grid Mode: {'Yes' if self.current_demo.grid_mode else 'No'}",
            f"Frames: {self.current_demo.frames}",
        ]
        for setting in settings:
            self.info_ax.text(0.1, y, setting, color="#aaaaaa", fontsize=7, va='top')
            y -= 0.02
        
        # Tutorial steps (if in tutorial mode)
        if self.tutorial_mode and self.current_demo.tutorial_steps:
            y = 0.25
            self.info_ax.text(0.05, y, f"Tutorial Step {self.current_tutorial_step + 1}/{len(self.current_demo.tutorial_steps)}",
                            color="#ff66aa", fontsize=11, va='top', fontweight='bold')
            y -= 0.05
            
            step = self.current_demo.tutorial_steps[self.current_tutorial_step]
            self.info_ax.text(0.05, y, step["title"], color="#ff66aa", 
                            fontsize=10, va='top', fontweight='bold')
            y -= 0.04
            self.info_ax.text(0.05, y, step["text"], color="#cccccc", 
                            fontsize=8, va='top', wrap=True)
    
    def draw_welcome_screen(self):
        """Draw welcome screen in simulation view."""
        self.sim_ax.clear()
        self.sim_ax.set_facecolor("#0d0d0d")
        self.sim_ax.set_xticks([])
        self.sim_ax.set_yticks([])
        self.sim_ax.set_xlim(0, 1)
        self.sim_ax.set_ylim(0, 1)
        
        y = 0.6
        self.sim_ax.text(0.5, y, "🎬 BinaryQuadTree Showcase", color="#00d9ff",
                        fontsize=20, ha='center', va='center', fontweight='bold')
        y -= 0.1
        self.sim_ax.text(0.5, y, "Self-Organizing Systems with .geo Scripts", color="#888888",
                        fontsize=12, ha='center', va='center')
        y -= 0.15
        self.sim_ax.text(0.5, y, "Select a demo from the browser to begin", color="#666666",
                        fontsize=10, ha='center', va='center')
        
        # Show category previews
        y = 0.3
        for cat_id, cat_info in CATEGORIES.items():
            self.sim_ax.text(0.5, y, f"{cat_info['icon']} {cat_info['title']}: {cat_info['description']}",
                           color="#444444", fontsize=8, ha='center', va='center')
            y -= 0.05
    
    def get_demos_for_category(self, category: str) -> List[DemoInfo]:
        """Get demos for a specific category."""
        if category == "animation":
            return ANIMATION_DEMOS
        elif category == "terrain":
            return TERRAIN_DEMOS
        elif category == "selforg":
            return SELFORG_DEMOS
        return ALL_DEMOS
    
    def load_demo(self, demo: DemoInfo):
        """Load a demo configuration."""
        self.current_demo = demo
        self.tick = 0
        self.grid = None
        self.root = None
        self.running = False
        self.tutorial_mode = False
        self.current_tutorial_step = 0
        
        # Load geo script
        geo_path = demo.geo_file
        if not os.path.exists(geo_path):
            print(f"Error: Geo file not found: {geo_path}")
            return
        
        with open(geo_path, 'r') as f:
            script = f.read()
        
        errors = validate_geo(script)
        if errors:
            print(f"Warning: Geo script has errors:")
            for err in errors[:3]:
                print(f"  Line {err.line}: {err.message}")
        
        self.prog = parse_geo_script(script)
        
        # Setup simulation based on grid mode
        if demo.grid_mode:
            rows, cols = 8, 8
            cell_size = 16.0
            self.grid = Grid.make(rows, cols, self.prog,
                                 init_mask_fn=lambda r, c: 0b0000,
                                 cell_size=cell_size)
        else:
            self.root = Node(0, 0, 1, 0, 0b1000)
        
        # Setup simulation axes
        self.sim_ax.clear()
        self.sim_ax.set_facecolor("#0d0d0d")
        self.sim_ax.set_xticks([])
        self.sim_ax.set_yticks([])
        
        # Redraw panels
        self.draw_browser_panel()
        self.draw_controls_panel()
        self.draw_info_panel()
        
        # Start animation
        self.start_animation()
    
    def start_animation(self):
        """Start the simulation animation."""
        if self.anim:
            self.anim.event_source.stop()
        
        interval = int(1000 / self.current_demo.recommended_speed)
        self.running = False  # Start paused
        
        def update(frame):
            if not self.running:
                return
            
            self.tick += 1
            
            # Clear and redraw
            self.sim_ax.clear()
            self.sim_ax.set_facecolor("#0d0d0d")
            self.sim_ax.set_xticks([])
            self.sim_ax.set_yticks([])
            
            # Step and render simulation
            if self.grid:
                self.grid.step(self.tick)
                draw_grid_frame(self.sim_ax, self.grid, self.current_demo.recommended_depth)
                title = f"{self.current_demo.title} | Tick: {self.tick}"
            else:
                self.prog.step_tree(self.root, self.tick)
                draw_frame(self.sim_ax, self.root, self.current_demo.recommended_depth, colored=True)
                title = f"{self.current_demo.title} | Tick: {self.tick} | Mask: {self.root.mask:04b}"
            
            self.sim_ax.set_title(title, color="white", fontsize=11)
            
            # Check tutorial step
            if self.tutorial_mode and self.current_demo.tutorial_steps:
                for i, step in enumerate(self.current_demo.tutorial_steps):
                    if self.tick >= step.get("tick", 0):
                        self.current_tutorial_step = i
            
            # Update info panel
            self.draw_info_panel()
            self.draw_controls_panel()
            
            self.fig.canvas.draw_idle()
        
        self.anim = FuncAnimation(self.fig, update, interval=interval, cache_frame_data=False)
    
    def on_click(self, event):
        """Handle click events."""
        # Check category clicks
        if event.inaxes == self.browser_ax:
            for rect, cat_id in self.category_buttons:
                if rect.contains_point((event.x, event.y)):
                    self.selected_category = cat_id
                    self.draw_browser_panel()
                    self.fig.canvas.draw_idle()
                    return
            
            # Check demo clicks
            for rect, demo in self.demo_buttons:
                if rect.contains_point((event.x, event.y)):
                    self.load_demo(demo)
                    return
        
        # Check control clicks
        if event.inaxes == self.controls_ax:
            for rect, action in self.control_buttons:
                if rect.contains_point((event.x, event.y)):
                    self.handle_control_action(action)
                    return
        
        # Click on simulation toggles pause
        if event.inaxes == self.sim_ax and self.current_demo:
            self.running = not self.running
        
        self.fig.canvas.draw_idle()
    
    def handle_control_action(self, action: str):
        """Handle control button action."""
        if action == "play":
            self.running = True
        elif action == "pause":
            self.running = False
        elif action == "stop":
            self.running = False
            self.tick = 0
            if self.grid:
                # Reset grid
                self.grid = Grid.make(self.grid.rows, self.grid.cols, self.prog,
                                     init_mask_fn=lambda r, c: 0b0000,
                                     cell_size=self.grid.cell_size)
            else:
                self.root = Node(0, 0, 1, 0, 0b1000)
            self.draw_welcome_screen() if not self.current_demo else None
        elif action == "step":
            self.tick += 1
            if self.grid:
                self.grid.step(self.tick)
            else:
                self.prog.step_tree(self.root, self.tick)
        elif action == "tutorial":
            self.tutorial_mode = not self.tutorial_mode
            self.current_tutorial_step = 0
        elif action.startswith("export_"):
            export_type = action.replace("export_", "")
            self.export_current_demo(export_type)
        
        self.draw_controls_panel()
        self.fig.canvas.draw_idle()
    
    def on_key(self, event):
        """Handle key press events."""
        if event.key == ' ':
            self.running = not self.running
        elif event.key in ('r', 'R'):
            self.tick = 0
            if self.grid:
                self.grid = Grid.make(self.grid.rows, self.grid.cols, self.prog,
                                     init_mask_fn=lambda r, c: 0b0000,
                                     cell_size=self.grid.cell_size)
            else:
                self.root = Node(0, 0, 1, 0, 0b1000)
        elif event.key in ('t', 'T'):
            self.tutorial_mode = not self.tutorial_mode
            self.current_tutorial_step = 0
        elif event.key in ('s', 'S'):
            self.tick += 1
            if self.grid:
                self.grid.step(self.tick)
            else:
                self.prog.step_tree(self.root, self.tick)
        elif event.key in ('e', 'E'):
            if self.current_demo:
                self.export_current_demo("png")
        
        self.draw_controls_panel()
        self.fig.canvas.draw_idle()
    
    def export_current_demo(self, export_type: str):
        """Export current demo in specified format."""
        if not self.current_demo:
            return
        
        os.makedirs("exports", exist_ok=True)
        demo_name = self.current_demo.geo_file.replace('/', '_').replace('.geo', '')
        
        if export_type == "png":
            path = f"exports/{demo_name}_frame_{self.tick}.png"
            self.fig.savefig(path, facecolor="#1a1a2e")
            print(f"Exported frame to {path}")
        
        elif export_type == "gif":
            if not HAS_PIL:
                print("PIL required for GIF export")
                return
            path = f"exports/{demo_name}.gif"
            print(f"Exporting GIF to {path}... (this may take a moment)")
            export_gif(self.current_demo.geo_file, path, 
                      num_frames=self.current_demo.frames,
                      depth=self.current_demo.recommended_depth,
                      grid_mode=self.current_demo.grid_mode)
        
        elif export_type == "json":
            path = f"exports/{demo_name}.json"
            print(f"Exporting JSON to {path}...")
            export_terrain_json(self.current_demo.geo_file, path,
                               depth=self.current_demo.recommended_depth,
                               grid_mode=self.current_demo.grid_mode)
    
    def run(self):
        """Run the application."""
        plt.show()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Showcase — Interactive .geo Script Showcase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python Showcase.py                    Launch GUI
  python Showcase.py --list             List all available demos
  python Showcase.py --demo walk_cycle  Run specific demo
  python Showcase.py --export biomes --json  Export terrain as JSON
        """
    )
    
    parser.add_argument('--demo', type=str, help='Run a specific demo by name')
    parser.add_argument('--list', action='store_true', help='List all available demos')
    parser.add_argument('--export', type=str, help='Export a demo')
    parser.add_argument('--json', action='store_true', help='Export as JSON')
    parser.add_argument('--gif', action='store_true', help='Export as GIF')
    parser.add_argument('--png', action='store_true', help='Export as PNG sequence')
    parser.add_argument('--depth', type=int, default=5, help='Recursion depth')
    parser.add_argument('--frames', type=int, default=60, help='Number of frames')
    
    args = parser.parse_args()
    
    # List demos
    if args.list:
        # Set stdout to UTF-8 for Windows
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8')
        
        print("\nBinaryQuadTree Showcase - Available Demos\n")
        for cat_id, cat_info in CATEGORIES.items():
            print(f"\n{cat_info['icon']} {cat_info['title']}")
            print(f"   {cat_info['description']}\n")
            demos = [d for d in ALL_DEMOS if d.category == cat_id]
            for demo in demos:
                grid_tag = " [GRID]" if demo.grid_mode else ""
                print(f"   - {demo.title}{grid_tag}")
                print(f"     {demo.description}")
                print(f"     Concepts: {', '.join(demo.concepts)}")
        print()
        return
    
    # Export mode
    if args.export:
        demo_name = args.export
        demo = None
        for d in ALL_DEMOS:
            if d.geo_file.find(demo_name) >= 0 or demo_name in d.title.lower():
                demo = d
                break
        
        if not demo:
            print(f"Demo not found: {demo_name}")
            return
        
        os.makedirs("exports", exist_ok=True)
        
        if args.json:
            path = f"exports/{demo_name}.json"
            export_terrain_json(demo.geo_file, path, depth=args.depth, grid_mode=demo.grid_mode)
        elif args.gif:
            path = f"exports/{demo_name}.gif"
            export_gif(demo.geo_file, path, num_frames=args.frames,
                      depth=args.depth, grid_mode=demo.grid_mode)
        else:
            # Default to PNG sequence
            output_dir = f"exports/{demo_name}_frames"
            export_frames(demo.geo_file, output_dir, num_frames=args.frames,
                         depth=args.depth, grid_mode=demo.grid_mode)
        return
    
    # Single demo mode (no GUI)
    if args.demo:
        demo = None
        for d in ALL_DEMOS:
            if d.geo_file.find(args.demo) >= 0 or args.demo in d.title.lower():
                demo = d
                break
        
        if demo:
            from src import run_script_demo, run_script_grid_demo
            with open(demo.geo_file, 'r') as f:
                script = f.read()
            
            if demo.grid_mode:
                run_script_grid_demo(script, start_mask=0b1000,
                                    ticks_per_second=demo.recommended_speed,
                                    max_depth=demo.recommended_depth)
            else:
                run_script_demo(script, start_mask=0b1000,
                               ticks_per_second=demo.recommended_speed,
                               max_depth=demo.recommended_depth)
        return
    
    # GUI mode (default)
    app = ShowcaseApp()
    app.run()


if __name__ == '__main__':
    main()
