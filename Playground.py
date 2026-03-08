#!/usr/bin/env python3
"""
Binary Quad-Tree Grammar Engine - Playground Showcase
======================================================

A comprehensive visual showcase for all .geo script files demonstrating
the capabilities of the Binary Quad-Tree Geometric Grammar Engine.

Features:
  - Browse all .geo scripts with descriptions
  - Live simulation preview with controls
  - Automatic grid mode detection for neighbor-aware scripts
  - Adjustable depth, speed, and other parameters
  - Export frames and GIFs

Usage:
    python Playground.py                    # Launch GUI showcase
    python Playground.py --list             # List all available .geo scripts
    python Playground.py --geo examples/spiral.geo  # Run specific script
    python Playground.py --demo conway_life --grid  # Run built-in demo
"""

import sys
import os
import argparse
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import random

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    from matplotlib.animation import FuncAnimation
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Error: matplotlib required. Install with: pip install matplotlib")
    sys.exit(1)

# Import from src package
from src import (
    parse_geo_script, load_geo, validate_geo, family_of, next_mask,
    Node, expand_active, draw_frame, mask_quadrants,
    GATES, Y_LOOP, X_LOOP, Z_LOOP, DIAG_LOOP,
    _FAMILY_RGB, Grid, draw_grid_frame,
    GEO_SPIRAL, GEO_PULSE_DEPTH, GEO_NB_SCRIPT, GEO_VOTE_EXAMPLE,
    GEO_ROTATE_MIRROR, GEO_STOCHASTIC, GEO_HEAT_SPREAD, GEO_SIGNAL_WAVE,
    GEO_DEPTH_LAYERS, GEO_CONWAY_LIFE, GEO_MASK_SET, GEO_COMPOSITE,
    run_script_demo, run_script_grid_demo
)

# Try to import PIL for GIF export
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# ══════════════════════════════════════════════════════════════════════════════
# .GEO SCRIPT CATALOG
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class GeoScript:
    """Metadata for a .geo script file."""
    name: str
    file_path: str
    description: str
    category: str
    grid_mode: bool
    depth: int
    speed: float
    start_mask: int
    random_seed: bool
    features: List[str]


# Built-in demo scripts (embedded in BinaryQuadTreeTest.py)
BUILTIN_SCRIPTS = [
    GeoScript(
        name="Spiral",
        file_path="builtin:spiral",
        description="Cycles through all four loop families in an 8-tick cycle. Deep cells (depth>=5) get sealed as gate-on.",
        category="Visual Demo",
        grid_mode=False,
        depth=6,
        speed=3.0,
        start_mask=0b1000,
        random_seed=False,
        features=["Loop cycling", "Depth conditions", "Periodic triggers"]
    ),
    GeoScript(
        name="Pulse Depth",
        file_path="builtin:pulse_depth",
        description="Pulses gate-on every 10 ticks. Deep cells lock to Z-loop (blue).",
        category="Visual Demo",
        grid_mode=False,
        depth=6,
        speed=3.0,
        start_mask=0b1000,
        random_seed=False,
        features=["Periodic triggers", "Depth branching", "Family switching"]
    ),
    GeoScript(
        name="Stochastic",
        file_path="builtin:stochastic",
        description="Probabilistic rules for organic, non-deterministic evolution. 30% chance to gate-on each tick.",
        category="Visual Demo",
        grid_mode=False,
        depth=6,
        speed=3.0,
        start_mask=0b1000,
        random_seed=False,
        features=["Random behavior", "Depth conditions", "Probability rules"]
    ),
    GeoScript(
        name="Heat Spread",
        file_path="builtin:heat_spread",
        description="Cells accumulate 'heat' and change family at thresholds. Demonstrates cell variables.",
        category="Cell Variables",
        grid_mode=True,
        depth=4,
        speed=4.0,
        start_mask=0b1000,
        random_seed=False,
        features=["Cell variables", "Threshold triggers", "State transitions"]
    ),
    GeoScript(
        name="Signal Wave",
        file_path="builtin:signal_wave",
        description="Signal-based communication between grid cells. Y-loop emits pulse, receivers react.",
        category="Signal Propagation",
        grid_mode=True,
        depth=4,
        speed=3.0,
        start_mask=0b1000,
        random_seed=False,
        features=["Signal emission", "Signal reception", "Cell communication"]
    ),
    GeoScript(
        name="Depth Layers",
        file_path="builtin:depth_layers",
        description="Different behaviors at different depths. Shallow layers rotate, mid layers mirror, deep layers gate.",
        category="Visual Demo",
        grid_mode=False,
        depth=6,
        speed=3.0,
        start_mask=0b1000,
        random_seed=False,
        features=["Depth ranges", "Composite actions", "Layered behavior"]
    ),
    GeoScript(
        name="Conway's Life",
        file_path="builtin:conway_life",
        description="Conway's Game of Life approximation using neighbor counting. Birth with 3, survive with 2-3.",
        category="Cellular Automata",
        grid_mode=True,
        depth=3,
        speed=5.0,
        start_mask=0b1111,
        random_seed=True,
        features=["8-neighbor counting", "Birth/survival rules", "Cellular automata"]
    ),
    GeoScript(
        name="Neighbor Spread",
        file_path="builtin:nb_spread",
        description="Cells that see a Y-loop neighbor switch to X-loop. Demonstrates neighbor-aware rules.",
        category="Neighbor Interactions",
        grid_mode=True,
        depth=4,
        speed=3.0,
        start_mask=0b1000,
        random_seed=False,
        features=["Neighbor detection", "Family spreading", "Wave propagation"]
    ),
    GeoScript(
        name="Mask Set",
        file_path="builtin:mask_set",
        description="Demonstrates mask_in condition and multi-step ADVANCE. Specific masks trigger special behavior.",
        category="Visual Demo",
        grid_mode=False,
        depth=6,
        speed=3.0,
        start_mask=0b1000,
        random_seed=False,
        features=["Mask conditions", "Multi-step advance", "Pattern matching"]
    ),
    GeoScript(
        name="Composite",
        file_path="builtin:composite",
        description="Composite actions: SWITCH + EMIT + SET_VAR in a single THEN clause.",
        category="Cell Variables",
        grid_mode=True,
        depth=4,
        speed=3.0,
        start_mask=0b1000,
        random_seed=False,
        features=["Composite actions", "Signal emission", "Variable setting"]
    ),
    GeoScript(
        name="Rotate Mirror",
        file_path="builtin:rotate_mirror",
        description="Demonstrates ROTATE_CW, FLIP_H, and parenthesized conditions. Rotates then mirrors geometry.",
        category="Visual Demo",
        grid_mode=False,
        depth=6,
        speed=3.0,
        start_mask=0b1000,
        random_seed=False,
        features=["Bit rotation", "Bit mirroring", "Tick conditions"]
    ),
    GeoScript(
        name="Vote Example",
        file_path="builtin:vote_example",
        description="Demonstrates program-identity conditions and PROG/PLURALITY actions for multi-program grids.",
        category="Multi-Program",
        grid_mode=True,
        depth=4,
        speed=3.0,
        start_mask=0b1000,
        random_seed=False,
        features=["Program switching", "Plurality voting", "Multi-program grid"]
    ),
]


def scan_geo_files(examples_dir: str = "examples") -> List[GeoScript]:
    """Scan the examples directory for .geo files and create metadata."""
    scripts = []
    
    if not os.path.exists(examples_dir):
        return scripts
    
    # Category mapping based on script analysis
    category_map = {
        "ecosystem": ("Ecosystem Simulation", True, 4, 5.0, 0b1000, True),
        "dungeon_generator": ("Dungeon Generation", True, 4, 6.0, 0b0000, False),
        "conway_life": ("Cellular Automata", True, 3, 5.0, 0b1111, True),
        "forest_fire": ("Signal Propagation", True, 4, 4.0, 0b1000, False),
        "heat_spread": ("Cell Variables", True, 4, 4.0, 0b1000, False),
        "signal_wave": ("Signal Propagation", True, 4, 3.0, 0b1000, False),
        "spiral": ("Visual Demo", False, 6, 3.0, 0b1000, False),
        "stochastic": ("Visual Demo", False, 6, 3.0, 0b1000, False),
        "depth_layers": ("Visual Demo", False, 6, 3.0, 0b1000, False),
        "composite": ("Cell Variables", True, 4, 3.0, 0b1000, False),
        "rotate_mirror": ("Visual Demo", False, 6, 3.0, 0b1000, False),
        "mask_set": ("Visual Demo", False, 6, 3.0, 0b1000, False),
        "pulse_depth": ("Visual Demo", False, 6, 3.0, 0b1000, False),
        "nb_spread": ("Neighbor Interactions", True, 4, 3.0, 0b1000, False),
        "vote_example": ("Multi-Program", True, 4, 3.0, 0b1000, False),
        "hello_world": ("Basic Demo", False, 5, 3.0, 0b1000, False),
    }
    
    description_map = {
        "ecosystem": "Predator/prey/plant simulation with emergent behavior. Three-tier ecosystem using cell variables (age, energy, hunger) and signals.",
        "dungeon_generator": "Procedural level generation using cellular automata. Six phases: noise seeding, smoothing, room expansion, corridor carving, door placement, and polish.",
        "conway_life": "Classic Conway's Game of Life with Birth/Survival rules. Uses 8-neighbor (Moore neighborhood) counting.",
        "forest_fire": "Recursive forest fire simulation. Trees (green) catch fire from burning neighbors and burn out after 4 ticks.",
        "heat_spread": "Cells accumulate 'heat' and change family at thresholds. Demonstrates cell variables and state transitions.",
        "signal_wave": "Signal-based communication between grid cells. Y-loop emits pulse, receivers switch to X-loop and echo.",
        "spiral": "Cycles through all four loop families in an 8-tick cycle. Deep cells get sealed as gate-on.",
        "stochastic": "Probabilistic rules for organic, non-deterministic evolution. Random behavior based on probability thresholds.",
        "depth_layers": "Different behaviors at different recursion depths. Shallow layers rotate, mid layers mirror, deep layers gate.",
        "composite": "Demonstrates composite actions: SWITCH + EMIT + SET_VAR in a single THEN clause.",
        "rotate_mirror": "Demonstrates ROTATE_CW, FLIP_H, and parenthesized conditions. Rotates then mirrors geometry.",
        "mask_set": "Demonstrates mask_in condition and multi-step ADVANCE. Specific masks trigger special behavior.",
        "pulse_depth": "Pulses gate-on every 10 ticks. Deep cells lock to Z-loop (blue).",
        "nb_spread": "Cells that see a Y-loop neighbor switch to X-loop. Demonstrates neighbor-aware rules.",
        "vote_example": "Demonstrates program-identity conditions and PROG/PLURALITY actions for multi-program grids.",
        "hello_world": "Basic hello world demo for the Binary Quad-Tree Grammar Engine.",
    }
    
    feature_map = {
        "ecosystem": ["Cell variables", "Signal propagation", "Multi-species", "Emergent behavior"],
        "dungeon_generator": ["Cellular automata", "Multi-phase", "Procedural generation", "Neighbor counting"],
        "conway_life": ["8-neighbor counting", "Birth/survival rules", "Cellular automata", "Random seeding"],
        "forest_fire": ["Signal propagation", "Cell variables", "State machine", "Cascade effect"],
        "heat_spread": ["Cell variables", "Threshold triggers", "State transitions", "Accumulation"],
        "signal_wave": ["Signal emission", "Signal reception", "Cell communication", "Wave propagation"],
        "spiral": ["Loop cycling", "Depth conditions", "Periodic triggers", "Visual pattern"],
        "stochastic": ["Random behavior", "Probability rules", "Depth conditions", "Non-deterministic"],
        "depth_layers": ["Depth ranges", "Composite actions", "Layered behavior", "Recursive patterns"],
        "composite": ["Composite actions", "Signal emission", "Variable setting", "Multi-action"],
        "rotate_mirror": ["Bit rotation", "Bit mirroring", "Tick conditions", "Geometry transforms"],
        "mask_set": ["Mask conditions", "Multi-step advance", "Pattern matching", "Family switching"],
        "pulse_depth": ["Periodic triggers", "Depth branching", "Family switching", "Pulsing behavior"],
        "nb_spread": ["Neighbor detection", "Family spreading", "Wave propagation", "Cardinal neighbors"],
        "vote_example": ["Program switching", "Plurality voting", "Multi-program grid", "Identity conditions"],
        "hello_world": ["Basic demo", "Getting started", "Simple rules", "Introduction"],
    }
    
    # Names that are covered by builtin scripts (to avoid duplicates)
    builtin_names = {"spiral", "pulse_depth", "stochastic", "heat_spread", "signal_wave", 
                     "depth_layers", "conway_life", "nb_spread", "mask_set", "composite", 
                     "rotate_mirror", "vote_example"}
    
    for geo_file in sorted(os.listdir(examples_dir)):
        if not geo_file.endswith('.geo'):
            continue
        
        base_name = geo_file[:-4]  # Remove .geo extension
        
        # Skip if this is a builtin script (will be shown once in builtin list)
        if base_name in builtin_names:
            continue
        
        file_path = os.path.join(examples_dir, geo_file)
        
        # Get metadata from maps or use defaults
        if base_name in category_map:
            category, grid_mode, depth, speed, start_mask, random_seed = category_map[base_name]
        else:
            category = "General"
            grid_mode = False
            depth = 5
            speed = 3.0
            start_mask = 0b1000
            random_seed = False
        
        description = description_map.get(base_name, f"A .geo script demonstrating Binary Quad-Tree Grammar Engine features.")
        features = feature_map.get(base_name, ["General purpose"])
        
        scripts.append(GeoScript(
            name=base_name.replace('_', ' ').title(),
            file_path=file_path,
            description=description,
            category=category,
            grid_mode=grid_mode,
            depth=depth,
            speed=speed,
            start_mask=start_mask,
            random_seed=random_seed,
            features=features
        ))
    
    return scripts


# ══════════════════════════════════════════════════════════════════════════════
# SHOWCASE APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class GeoShowcase:
    """Interactive showcase for .geo scripts."""

    COLORS = {
        'bg': '#1a1a2e',
        'panel': '#16213e',
        'accent': '#0f3460',
        'highlight': '#e94560',
        'cyan': '#00d9ff',
        'text': '#ffffff',
        'subtext': '#888888',
    }

    def __init__(self):
        self.fig = None
        self.current_script: Optional[GeoScript] = None
        self.running = False
        self.tick = 0
        self.roots = []
        self.grid = None
        self.prog = None
        self.anim = None
        self.axes = {}
        
        # Collect all scripts
        self.scripts = BUILTIN_SCRIPTS.copy()
        self.scripts.extend(scan_geo_files())
        
        # Group by category
        self.categories = {}
        for script in self.scripts:
            if script.category not in self.categories:
                self.categories[script.category] = []
            self.categories[script.category].append(script)
        
        self.setup_gui()

    def setup_gui(self):
        """Setup the matplotlib GUI."""
        self.fig = plt.figure(figsize=(18, 11), facecolor=self.COLORS['bg'])
        self.fig.canvas.manager.set_window_title("Binary Quad-Tree Grammar Engine - Playground Showcase")

        # Create grid spec: sidebar (scripts), main view, info panel
        gs = self.fig.add_gridspec(1, 5, width_ratios=[1, 3, 3, 2, 2], hspace=0.1, wspace=0.05)

        # Script browser (left)
        self.browser_ax = self.fig.add_subplot(gs[0, 0])
        self.browser_ax.set_facecolor(self.COLORS['panel'])
        self.browser_ax.set_xticks([])
        self.browser_ax.set_yticks([])
        self.browser_ax.set_title("GEO SCRIPTS", color=self.COLORS['cyan'], fontsize=14, fontweight='bold', pad=10)

        # Main simulation view (center - larger)
        self.sim_ax = self.fig.add_subplot(gs[0, 1:3])
        self.sim_ax.set_facecolor('#0d0d0d')
        self.sim_ax.set_xticks([])
        self.sim_ax.set_yticks([])

        # Info panel (right)
        self.info_ax = self.fig.add_subplot(gs[0, 3])
        self.info_ax.set_facecolor(self.COLORS['panel'])
        self.info_ax.set_xticks([])
        self.info_ax.set_yticks([])
        self.info_ax.set_title("SCRIPT INFO", color=self.COLORS['cyan'], fontsize=12, fontweight='bold', pad=10)

        # Controls panel (far right)
        self.controls_ax = self.fig.add_subplot(gs[0, 4])
        self.controls_ax.set_facecolor(self.COLORS['panel'])
        self.controls_ax.set_xticks([])
        self.controls_ax.set_yticks([])
        self.controls_ax.set_title("CONTROLS", color=self.COLORS['cyan'], fontsize=12, fontweight='bold', pad=10)

        # Draw panels
        self.draw_browser_panel()
        self.draw_info_panel()
        self.draw_controls_panel()
        self.draw_welcome_screen()

        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        # Note: tight_layout disabled due to custom grid spec
        # plt.tight_layout()

    def draw_browser_panel(self):
        """Draw script browser with categories."""
        self.browser_ax.clear()
        self.browser_ax.set_facecolor(self.COLORS['panel'])
        self.browser_ax.set_xticks([])
        self.browser_ax.set_yticks([])
        self.browser_ax.set_title("GEO SCRIPTS", color=self.COLORS['cyan'], fontsize=14, fontweight='bold', pad=10)
        self.browser_ax.set_xlim(0, 1)
        self.browser_ax.set_ylim(0, 1)

        y = 0.92
        self.script_buttons = []
        
        for category, scripts in self.categories.items():
            # Category header
            self.browser_ax.text(0.05, y, category.upper(), 
                               color=self.COLORS['subtext'], fontsize=9, fontweight='bold', va='top')
            y -= 0.04
            
            for script in scripts:
                btn_y = y - 0.025
                is_selected = self.current_script and self.current_script.name == script.name
                rect = Rectangle((0.05, btn_y - 0.02), 0.9, 0.04,
                               facecolor=self.COLORS['highlight'] if is_selected else self.COLORS['accent'],
                               edgecolor=self.COLORS['cyan'] if is_selected else '#333333',
                               linewidth=2 if is_selected else 1)
                self.browser_ax.add_patch(rect)
                self.browser_ax.text(0.08, btn_y, script.name, 
                                   color=self.COLORS['text'], fontsize=8, va='center')
                self.script_buttons.append((rect, script))
                y -= 0.05
            
            y -= 0.02  # Extra space between categories

    def draw_info_panel(self):
        """Draw script information panel."""
        self.info_ax.clear()
        self.info_ax.set_facecolor(self.COLORS['panel'])
        self.info_ax.set_xticks([])
        self.info_ax.set_yticks([])
        self.info_ax.set_title("SCRIPT INFO", color=self.COLORS['cyan'], fontsize=12, fontweight='bold', pad=10)
        self.info_ax.set_xlim(0, 1)
        self.info_ax.set_ylim(0, 1)

        if self.current_script:
            y = 0.88
            
            # Name
            self.info_ax.text(0.05, y, self.current_script.name, 
                            color=self.COLORS['highlight'], fontsize=14, fontweight='bold', va='top')
            y -= 0.06
            
            # Category
            self.info_ax.text(0.05, y, f"Category: {self.current_script.category}", 
                            color=self.COLORS['subtext'], fontsize=9, va='top')
            y -= 0.05
            
            # Description
            self.info_ax.text(0.05, y, "Description:", 
                            color=self.COLORS['subtext'], fontsize=9, va='top')
            y -= 0.04
            self.info_ax.text(0.05, y, self.current_script.description, 
                            color=self.COLORS['text'], fontsize=8, va='top', wrap=True)
            y -= 0.15
            
            # Features
            self.info_ax.text(0.05, y, "Features:", 
                            color=self.COLORS['subtext'], fontsize=9, fontweight='bold', va='top')
            y -= 0.04
            for feature in self.current_script.features:
                self.info_ax.text(0.08, y, f"• {feature}", 
                                color=self.COLORS['text'], fontsize=8, va='top')
                y -= 0.035
            
            y -= 0.03
            
            # Settings
            self.info_ax.text(0.05, y, "Settings:", 
                            color=self.COLORS['subtext'], fontsize=9, fontweight='bold', va='top')
            y -= 0.04
            settings = [
                ("Grid Mode:", "Yes" if self.current_script.grid_mode else "No"),
                ("Depth:", str(self.current_script.depth)),
                ("Speed:", f"{self.current_script.speed} tps"),
                ("Random Seed:", "Yes" if self.current_script.random_seed else "No"),
            ]
            for label, value in settings:
                self.info_ax.text(0.05, y, label, color=self.COLORS['subtext'], fontsize=8, va='top')
                self.info_ax.text(0.45, y, value, color=self.COLORS['cyan'], fontsize=8, va='top')
                y -= 0.035
        else:
            self.info_ax.text(0.5, 0.5, "Select a script to view details", 
                            color=self.COLORS['subtext'], fontsize=10, ha='center', va='center')

    def draw_controls_panel(self):
        """Draw controls panel."""
        self.controls_ax.clear()
        self.controls_ax.set_facecolor(self.COLORS['panel'])
        self.controls_ax.set_xticks([])
        self.controls_ax.set_yticks([])
        self.controls_ax.set_title("CONTROLS", color=self.COLORS['cyan'], fontsize=12, fontweight='bold', pad=10)
        self.controls_ax.set_xlim(0, 1)
        self.controls_ax.set_ylim(0, 1)

        y = 0.85
        
        # Simulation controls
        self.controls_ax.text(0.05, y, "Simulation:", 
                            color=self.COLORS['subtext'], fontsize=9, fontweight='bold', va='top')
        y -= 0.05
        
        controls = [
            ("Click script", "Load and run"),
            ("Click sim", "Pause/Resume"),
            ("Space", "Toggle pause"),
            ("R", "Restart"),
        ]
        for key, action in controls:
            self.controls_ax.text(0.05, y, key, color=self.COLORS['cyan'], fontsize=8, va='top', fontweight='bold')
            self.controls_ax.text(0.35, y, action, color=self.COLORS['text'], fontsize=8, va='top')
            y -= 0.035
        
        y -= 0.03
        
        # Export controls
        self.controls_ax.text(0.05, y, "Export:", 
                            color=self.COLORS['subtext'], fontsize=9, fontweight='bold', va='top')
        y -= 0.05
        
        export_controls = [
            ("E", "Export frame as PNG"),
            ("G", "Export animation as GIF"),
        ]
        for key, action in export_controls:
            self.controls_ax.text(0.05, y, key, color=self.COLORS['cyan'], fontsize=8, va='top', fontweight='bold')
            self.controls_ax.text(0.35, y, action, color=self.COLORS['text'], fontsize=8, va='top')
            y -= 0.035
        
        y -= 0.03
        
        # Status
        self.controls_ax.text(0.05, y, "Status:", 
                            color=self.COLORS['subtext'], fontsize=9, fontweight='bold', va='top')
        y -= 0.05
        
        status = "Running" if self.running else "Paused"
        status_color = '#00ff00' if self.running else '#ff6600'
        self.controls_ax.text(0.05, y, status, color=status_color, fontsize=10, va='top', fontweight='bold')
        
        if self.current_script:
            self.controls_ax.text(0.05, y - 0.04, f"Tick: {self.tick}", 
                                color=self.COLORS['cyan'], fontsize=9, va='top')

    def draw_welcome_screen(self):
        """Draw welcome screen on simulation view."""
        self.sim_ax.clear()
        self.sim_ax.set_facecolor('#0d0d0d')
        self.sim_ax.set_xticks([])
        self.sim_ax.set_yticks([])
        self.sim_ax.set_xlim(0, 1)
        self.sim_ax.set_ylim(0, 1)
        
        # Title
        self.sim_ax.text(0.5, 0.6, "Binary Quad-Tree Grammar Engine", 
                        color=self.COLORS['cyan'], fontsize=18, fontweight='bold', 
                        ha='center', va='center')
        
        # Subtitle
        self.sim_ax.text(0.5, 0.5, "Playground Showcase", 
                        color=self.COLORS['text'], fontsize=14, 
                        ha='center', va='center')
        
        # Instructions
        instructions = [
            "Select a .geo script from the left panel to begin",
            "",
            "Features:",
            "  • Browse all .geo scripts with descriptions",
            "  • Watch live simulations with automatic grid detection",
            "  • Export frames (E) and GIFs (G)",
            "",
            f"Available scripts: {len(self.scripts)}",
        ]
        
        y = 0.38
        for line in instructions:
            self.sim_ax.text(0.5, y, line, 
                            color=self.COLORS['subtext'] if line else self.COLORS['text'], 
                            fontsize=10 if line else 8,
                            ha='center', va='center')
            y -= 0.05

    def load_script(self, script: GeoScript):
        """Load and run a .geo script."""
        self.current_script = script
        self.tick = 0
        self.running = True
        self.roots = []
        self.grid = None
        
        # Load the program
        if script.file_path.startswith("builtin:"):
            demo_name = script.file_path.split(":")[1]
            demo_map = {
                "spiral": GEO_SPIRAL,
                "pulse_depth": GEO_PULSE_DEPTH,
                "stochastic": GEO_STOCHASTIC,
                "heat_spread": GEO_HEAT_SPREAD,
                "signal_wave": GEO_SIGNAL_WAVE,
                "depth_layers": GEO_DEPTH_LAYERS,
                "conway_life": GEO_CONWAY_LIFE,
                "nb_spread": GEO_NB_SCRIPT,
                "mask_set": GEO_MASK_SET,
                "composite": GEO_COMPOSITE,
                "rotate_mirror": GEO_ROTATE_MIRROR,
                "vote_example": GEO_VOTE_EXAMPLE,
            }
            script_text = demo_map.get(demo_name, GEO_SPIRAL)
            self.prog = parse_geo_script(script_text)
        else:
            if os.path.exists(script.file_path):
                self.prog = load_geo(script.file_path)
            else:
                print(f"Warning: Script file not found: {script.file_path}")
                return
        
        # Setup simulation based on grid mode
        if script.grid_mode:
            # Grid mode for neighbor-aware scripts
            rows, cols = 8, 8
            cell_size = 16.0
            
            if script.random_seed:
                # Random seeding for cellular automata
                if "conway" in script.name.lower():
                    dead, alive = 0b0000, 0b1111
                    density = 0.35
                else:
                    dead, alive = 0b0000, script.start_mask
                    density = 0.4
                init_fn = lambda r, c: alive if random.random() < density else dead
            else:
                init_fn = lambda r, c: script.start_mask
            
            self.grid = Grid.make(rows, cols, self.prog, init_mask_fn=init_fn, cell_size=cell_size)
        else:
            # Single node mode
            self.roots = [[Node(0, 0, 1, 0, script.start_mask)]]
        
        # Redraw panels
        self.draw_browser_panel()
        self.draw_info_panel()
        self.draw_controls_panel()
        
        # Start animation
        self.start_animation()

    def start_animation(self):
        """Start the simulation animation."""
        if self.anim:
            self.anim.event_source.stop()
        
        interval = int(1000 / self.current_script.speed)
        
        def update(frame):
            if not self.running:
                return
            
            self.tick += 1
            
            # Step simulation
            if self.grid:
                self.grid.step(self.tick)
            else:
                for r in range(len(self.roots)):
                    for c in range(len(self.roots[0])):
                        self.prog.step_node(self.roots[r][c], self.tick, {"tick": self.tick})
            
            # Clear and redraw simulation
            self.sim_ax.clear()
            self.sim_ax.set_facecolor('#0d0d0d')
            self.sim_ax.set_xticks([])
            self.sim_ax.set_yticks([])
            
            if self.grid:
                draw_grid_frame(self.sim_ax, self.grid, self.current_script.depth)
            else:
                draw_frame(self.sim_ax, self.roots[0][0], self.current_script.depth, colored=True)
            
            mode = "GRID" if self.grid else "SINGLE"
            self.sim_ax.set_title(f"{self.current_script.name} | {mode} | Tick: {self.tick}", 
                                 color=self.COLORS['text'], fontsize=11)
            
            # Update controls panel
            self.draw_controls_panel()
            
            self.fig.canvas.draw_idle()
        
        self.anim = FuncAnimation(self.fig, update, interval=interval, cache_frame_data=False)

    def on_click(self, event):
        """Handle click events."""
        if event.inaxes == self.browser_ax:
            # Check script button clicks
            for rect, script in self.script_buttons:
                if rect.contains_point((event.x, event.y)):
                    self.load_script(script)
                    break
        
        elif event.inaxes == self.sim_ax:
            # Toggle pause/resume
            if self.current_script:
                self.running = not self.running
                self.draw_controls_panel()
        
        self.fig.canvas.draw_idle()

    def on_key(self, event):
        """Handle key press events."""
        if not self.current_script:
            return
            
        if event.key == ' ' or event.key == 'space':
            # Toggle pause
            self.running = not self.running
            self.draw_controls_panel()
        elif event.key == 'r':
            # Restart
            self.load_script(self.current_script)
        elif event.key == 'e':
            # Export frame
            self.export_frame()
        elif event.key == 'g':
            # Export GIF
            self.export_gif()
        
        self.fig.canvas.draw_idle()

    def export_frame(self):
        """Export current frame as PNG."""
        if not self.current_script:
            return
        
        output_dir = "exports"
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"{self.current_script.name.replace(' ', '_')}_tick{self.tick}.png")
        self.fig.savefig(path, facecolor=self.COLORS['bg'])
        print(f"Exported frame to {path}")

    def export_gif(self):
        """Export animation as GIF."""
        if not HAS_PIL or not self.current_script:
            print("PIL/Pillow required for GIF export. Install with: pip install Pillow")
            return
        
        print("Exporting GIF... (this may take a moment)")
        output_path = f"exports/{self.current_script.name.replace(' ', '_')}.gif"
        os.makedirs("exports", exist_ok=True)
        
        # Re-run simulation and capture frames
        print(f"GIF export requires running simulation from start.")
        print(f"Use command line for full export:")
        print(f"  python GeoStudio.py --export {self.current_script.file_path} --gif {output_path}")

    def run(self):
        """Run the application."""
        plt.show()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Binary Quad-Tree Grammar Engine - Playground Showcase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python Playground.py                      Launch GUI showcase
  python Playground.py --list               List all available .geo scripts
  python Playground.py --geo examples/spiral.geo  Run specific script
  python Playground.py --demo conway_life --grid  Run built-in demo with grid
        """
    )

    parser.add_argument('--geo', type=str, help='Path to .geo file to run')
    parser.add_argument('--demo', type=str, help='Run built-in demo by name')
    parser.add_argument('--list', action='store_true', help='List all available scripts')
    parser.add_argument('--grid', action='store_true', help='Force grid mode')
    parser.add_argument('--depth', type=int, default=5, help='Recursion depth')
    parser.add_argument('--speed', type=float, default=3.0, help='Ticks per second')

    args = parser.parse_args()

    # List mode
    if args.list:
        showcase = GeoShowcase()
        print("\n" + "=" * 70)
        print("BINARY QUAD-TREE GRAMMAR ENGINE - AVAILABLE .GEO SCRIPTS")
        print("=" * 70 + "\n")
        
        for category, scripts in showcase.categories.items():
            print(f"\n{category}")
            print("-" * len(category))
            for script in scripts:
                grid_tag = " [GRID]" if script.grid_mode else ""
                print(f"  • {script.name}{grid_tag}")
                print(f"    {script.description[:70]}...")
        
        print("\n" + "=" * 70)
        print(f"Total scripts: {len(showcase.scripts)}")
        print("=" * 70)
        return

    # Single geo file mode
    if args.geo:
        if not os.path.exists(args.geo):
            print(f"Error: Geo file not found: {args.geo}")
            sys.exit(1)
        
        script_text = Path(args.geo).read_text()
        
        # Auto-detect grid mode
        use_grid = args.grid or any(kw in args.geo.lower() for kw in 
                                   ['conway', 'dungeon', 'ecosystem', 'nb_', 'heat_', 
                                    'signal_', 'forest_fire', 'cell'])
        
        if use_grid:
            run_script_grid_demo(script_text, start_mask=0b1000,
                                ticks_per_second=args.speed,
                                max_depth=min(args.depth, 4),
                                random_seed=True)
        else:
            run_script_demo(script_text, start_mask=0b1000,
                           ticks_per_second=args.speed, max_depth=args.depth)
        return

    # Built-in demo mode
    if args.demo:
        demo_map = {
            "spiral": GEO_SPIRAL,
            "pulse_depth": GEO_PULSE_DEPTH,
            "stochastic": GEO_STOCHASTIC,
            "heat_spread": GEO_HEAT_SPREAD,
            "signal_wave": GEO_SIGNAL_WAVE,
            "depth_layers": GEO_DEPTH_LAYERS,
            "conway_life": GEO_CONWAY_LIFE,
            "nb_spread": GEO_NB_SCRIPT,
            "mask_set": GEO_MASK_SET,
            "composite": GEO_COMPOSITE,
            "rotate_mirror": GEO_ROTATE_MIRROR,
            "vote_example": GEO_VOTE_EXAMPLE,
        }
        
        if args.demo not in demo_map:
            print(f"Unknown demo: {args.demo}")
            print(f"Available: {', '.join(demo_map.keys())}")
            return
        
        script_text = demo_map[args.demo]
        use_grid = args.grid or args.demo in ['conway_life', 'heat_spread', 'signal_wave', 
                                               'nb_spread', 'composite', 'vote_example']
        
        if use_grid:
            run_script_grid_demo(script_text, start_mask=0b1000,
                                ticks_per_second=args.speed,
                                max_depth=min(args.depth, 4),
                                random_seed=args.demo == 'conway_life')
        else:
            run_script_demo(script_text, start_mask=0b1000,
                           ticks_per_second=args.speed, max_depth=args.depth)
        return

    # GUI showcase mode (default)
    app = GeoShowcase()
    app.run()


if __name__ == '__main__':
    main()
