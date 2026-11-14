#!/usr/bin/env python3
"""
GeoStudio - Visual Launcher and Export Tool for Binary Quad-Tree Grammar Engine
================================================================================

A beautiful GUI launcher with presets, live preview, and export capabilities
for the Binary Quad-Tree Geometric Grammar Engine.

Features:
  - Visual preset browser with thumbnails
  - Live simulation preview
  - Export frames as PNG images
  - Export animation as GIF
  - Custom parameter controls
  - Batch export for texture sheets

Usage:
  python GeoStudio.py                    # Launch GUI
  python GeoStudio.py --export ecosystem --frames 100  # Export 100 frames
  python GeoStudio.py --preset dungeon --gif output.gif
"""

import sys
import os
import argparse
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

# Import from local module
from .binary_quad_tree import (
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
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    from matplotlib.animation import FuncAnimation, PillowWriter
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
# PRESET CONFIGURATIONS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Preset:
    name: str
    geo_file: str
    description: str
    depth: int = 5
    speed: float = 3.0
    grid_mode: bool = False
    start_mask: int = 0b1000
    init_fn: str = "uniform"  # "uniform", "random", "forest", "signal", "dungeon", "heat"
    ticks_to_run: int = 0  # 0 = infinite


def get_init_fn(preset_name: str, geo_file: str):
    """Get the appropriate initialization function for a preset."""
    if "Conway" in preset_name:
        # Conway's Life: 35% random alive cells (GATE_ON)
        return lambda r, c: 0b1111 if random.random() < 0.35 else 0b0000
    
    elif "Dungeon" in preset_name:
        # Dungeon: Start with all void, script creates noise in phase 1
        return lambda r, c: 0b0000
    
    elif "Forest" in preset_name:
        # Forest Fire: Mostly trees (X_LOOP), few fire starters (Y_LOOP) in center
        def forest_init(r, c):
            # Create a small fire patch in the center
            center_r, center_c = 4, 4
            if abs(r - center_r) <= 1 and abs(c - center_c) <= 1:
                return 0b1000  # Y_LOOP - burning
            return 0b1100  # X_LOOP - tree
        return forest_init
    
    elif "Heat" in preset_name:
        # Heat Spread: All cells start as Y_LOOP to accumulate heat
        return lambda r, c: 0b1000  # Y_LOOP
    
    elif "Signal" in preset_name:
        # Signal Wave: Y_LOOP emitters on left, Z_LOOP receivers elsewhere
        def signal_init(r, c):
            if c == 0:  # Left column emits
                return 0b1000  # Y_LOOP
            return 0b0111  # Z_LOOP - receivers
        return signal_init
    
    elif "Ecosystem" in preset_name:
        # Ecosystem: Mix of plants, herbivores, predators, empty
        def ecosystem_init(r, c):
            rand = random.random()
            if rand < 0.60:
                return 0b1100  # X_LOOP - plants (60%)
            elif rand < 0.75:
                return 0b0111  # Z_LOOP - herbivores (15%)
            elif rand < 0.80:
                return 0b1000  # Y_LOOP - predators (5%)
            else:
                return 0b0000  # empty (20%)
        return ecosystem_init
    
    elif "Stochastic" in preset_name:
        # Stochastic: Random masks for variety
        return lambda r, c: random.choice([0b1000, 0b1100, 0b0111, 0b0000])
    
    else:
        # Default: uniform start mask
        return lambda r, c: 0b1000


PRESETS = [
    Preset(
        name="[Ecosystem]",
        geo_file="examples/ecosystem.geo",
        description="Predator/prey/plant simulation with emergent behavior",
        depth=4,
        speed=5.0,
        grid_mode=True,
        init_fn="ecosystem",
        ticks_to_run=0
    ),
    Preset(
        name="[Dungeon]",
        geo_file="examples/dungeon_generator.geo",
        description="Procedural level generation for games",
        depth=4,
        speed=6.0,
        grid_mode=True,
        init_fn="dungeon",
        ticks_to_run=0
    ),
    Preset(
        name="[Conway Life]",
        geo_file="examples/conway_life.geo",
        description="Conway's Game of Life cellular automaton",
        depth=3,
        speed=5.0,
        grid_mode=True,
        init_fn="random",
        ticks_to_run=0
    ),
    Preset(
        name="[Forest Fire]",
        geo_file="examples/forest_fire.geo",
        description="Fire spreading through forest with signal propagation",
        depth=4,
        speed=4.0,
        grid_mode=True,
        init_fn="forest",
        ticks_to_run=0
    ),
    Preset(
        name="[Spiral]",
        geo_file="examples/spiral.geo",
        description="Cycling through all loop families",
        depth=6,
        speed=3.0,
        grid_mode=False,
        init_fn="uniform",
        ticks_to_run=0
    ),
    Preset(
        name="[Heat Spread]",
        geo_file="examples/heat_spread.geo",
        description="Heat accumulation and dissipation",
        depth=4,
        speed=4.0,
        grid_mode=True,
        init_fn="heat",
        ticks_to_run=0
    ),
    Preset(
        name="[Signal Wave]",
        geo_file="examples/signal_wave.geo",
        description="Inter-cell signal cascades",
        depth=4,
        speed=3.0,
        grid_mode=True,
        init_fn="signal",
        ticks_to_run=0
    ),
    Preset(
        name="[Stochastic]",
        geo_file="examples/stochastic.geo",
        description="Probabilistic rule-based evolution",
        depth=6,
        speed=3.0,
        grid_mode=False,
        init_fn="stochastic",
        ticks_to_run=0
    ),
]


# ══════════════════════════════════════════════════════════════════════════════
# EXPORT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def export_frames(geo_path: str, output_dir: str, num_frames: int = 60,
                  depth: int = 5, speed: float = 3.0, grid_mode: bool = False,
                  start_mask: int = 0b1000, fps: int = 10) -> List[str]:
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
        
        # Determine init function based on geo file
        preset_name = os.path.basename(geo_path).replace('.geo', '').replace('_', ' ').title()
        init_fn = get_init_fn(preset_name, geo_path)
        
        grid = Grid.make(rows, cols, prog, init_mask_fn=init_fn, cell_size=cell_size)
    else:
        root = Node(0, 0, 1, 0, start_mask)
        grid = None

    exported = []

    # Create figure for rendering
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor("#0d0d0d")

    for tick in range(num_frames):
        # Step simulation
        if grid:
            grid.step(tick + 1)
            draw_grid_frame(ax, grid, depth)
        else:
            prog.step_tree(root, tick + 1)
            draw_frame(ax, root, depth, colored=True)
        
        ax.set_title(f"Tick {tick + 1}", fontsize=10, color="white")

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
               depth: int = 5, fps: int = 10, **kwargs) -> str:
    """Export simulation as animated GIF."""

    if not HAS_PIL:
        raise ImportError("PIL/Pillow required for GIF export. Install with: pip install Pillow")

    # First export frames
    temp_dir = "_temp_export_frames"
    frame_paths = export_frames(geo_path, temp_dir, num_frames, depth, **kwargs)

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


# ══════════════════════════════════════════════════════════════════════════════
# GUI APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class GeoStudioApp:
    """Main GUI application."""

    def __init__(self):
        if not HAS_MATPLOTLIB:
            print("Error: matplotlib required for GUI. Install with: pip install matplotlib")
            sys.exit(1)

        self.current_preset: Optional[Preset] = None
        self.running = False
        self.tick = 0
        self.grid = None
        self.root = None
        self.prog = None
        self.fig = None
        self.axes = None
        self.anim = None

        self.setup_gui()

    def setup_gui(self):
        """Setup the matplotlib GUI."""
        # Create figure with preset panel
        self.fig = plt.figure(figsize=(16, 10), facecolor="#1a1a2e")
        self.fig.canvas.manager.set_window_title("GeoStudio - Binary Quad-Tree Grammar Engine")

        # Create grid spec
        gs = self.fig.add_gridspec(1, 4, width_ratios=[1, 4, 4, 3], hspace=0.1, wspace=0.1)

        # Preset panel (left)
        self.preset_ax = self.fig.add_subplot(gs[0, 0])
        self.preset_ax.set_facecolor("#16213e")
        self.preset_ax.set_xticks([])
        self.preset_ax.set_yticks([])
        self.preset_ax.set_title("PRESETS", color="white", fontsize=12, fontweight='bold')

        # Main simulation view
        self.sim_ax = self.fig.add_subplot(gs[0, 1:3])
        self.sim_ax.set_facecolor("#0d0d0d")
        self.sim_ax.set_xticks([])
        self.sim_ax.set_yticks([])

        # Info panel (right)
        self.info_ax = self.fig.add_subplot(gs[0, 3])
        self.info_ax.set_facecolor("#16213e")
        self.info_ax.set_xticks([])
        self.info_ax.set_yticks([])
        self.info_ax.set_title("INFO", color="white", fontsize=12, fontweight='bold')

        # Draw preset buttons
        self.draw_preset_panel()
        self.draw_info_panel()

        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def draw_preset_panel(self):
        """Draw preset selection buttons."""
        self.preset_ax.clear()
        self.preset_ax.set_facecolor("#16213e")
        self.preset_ax.set_xticks([])
        self.preset_ax.set_yticks([])
        self.preset_ax.set_title("PRESETS", color="#00d9ff", fontsize=14, fontweight='bold', pad=10)
        self.preset_ax.set_xlim(0, 1)
        self.preset_ax.set_ylim(0, 1)

        # Draw preset buttons
        num_presets = len(PRESETS)
        btn_height = 0.85 / num_presets

        self.preset_buttons = []
        for i, preset in enumerate(PRESETS):
            y = 0.95 - (i + 0.5) * btn_height
            rect = Rectangle((0.05, y - btn_height/2 + 0.02), 0.9, btn_height - 0.03,
                           facecolor="#0f3460" if preset != self.current_preset else "#e94560",
                           edgecolor="#00d9ff", linewidth=2 if preset == self.current_preset else 1)
            self.preset_ax.add_patch(rect)
            self.preset_ax.text(0.1, y, preset.name, color="white", fontsize=10,
                              va='center', fontweight='bold')
            self.preset_buttons.append((rect, preset))

    def draw_info_panel(self):
        """Draw info panel with current state."""
        self.info_ax.clear()
        self.info_ax.set_facecolor("#16213e")
        self.info_ax.set_xticks([])
        self.info_ax.set_yticks([])
        self.info_ax.set_title("INFO", color="#00d9ff", fontsize=14, fontweight='bold', pad=10)
        self.info_ax.set_xlim(0, 1)
        self.info_ax.set_ylim(0, 1)

        if self.current_preset:
            y = 0.9
            lines = [
                ("Name:", self.current_preset.name),
                ("Depth:", str(self.current_preset.depth)),
                ("Speed:", f"{self.current_preset.speed} tps"),
                ("Grid:", "Yes" if self.current_preset.grid_mode else "No"),
                ("Tick:", str(self.tick)),
            ]

            self.info_ax.text(0.05, y, "Description:", color="#888888", fontsize=9, va='top')
            self.info_ax.text(0.05, y - 0.08, self.current_preset.description,
                            color="white", fontsize=8, va='top', wrap=True)

            for i, (label, value) in enumerate(lines):
                yy = 0.55 - i * 0.08
                self.info_ax.text(0.05, yy, label, color="#888888", fontsize=9, va='top')
                self.info_ax.text(0.35, yy, value, color="#00d9ff", fontsize=9, va='top')

        # Controls info
        self.info_ax.text(0.05, 0.15, "CONTROLS:", color="#888888", fontsize=9, va='top')
        self.info_ax.text(0.05, 0.10, "Click preset to select • Click simulation to pause/resume",
                         color="white", fontsize=7, va='top')
        self.info_ax.text(0.05, 0.05, "Press 'E' to export frame • 'G' to export GIF",
                         color="white", fontsize=7, va='top')

    def load_preset(self, preset: Preset):
        """Load a preset configuration."""
        self.current_preset = preset
        self.tick = 0
        self.grid = None
        self.root = None

        # Load geo script
        geo_path = preset.geo_file
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
        if preset.grid_mode:
            # Grid mode for neighbor-aware simulations
            rows, cols = 8, 8
            cell_size = 16.0
            
            # Get the appropriate initialization function
            init_fn = get_init_fn(preset.name, geo_path)
            
            self.grid = Grid.make(rows, cols, self.prog, init_mask_fn=init_fn, cell_size=cell_size)
        else:
            # Single node mode for non-grid simulations
            self.root = Node(0, 0, 1, 0, preset.start_mask)

        # Setup simulation axes
        self.sim_ax.clear()
        self.sim_ax.set_facecolor("#0d0d0d")
        self.sim_ax.set_xticks([])
        self.sim_ax.set_yticks([])

        # Redraw panels
        self.draw_preset_panel()
        self.draw_info_panel()

        # Start animation
        self.start_animation()

    def start_animation(self):
        """Start the simulation animation."""
        if self.anim:
            self.anim.event_source.stop()

        interval = int(1000 / self.current_preset.speed)
        self.running = True

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
                # Grid mode
                self.grid.step(self.tick)
                draw_grid_frame(self.sim_ax, self.grid, self.current_preset.depth)
                
                # Count alive cells for display
                if "conway" in self.current_preset.geo_file.lower():
                    alive_count = sum(1 for r in range(self.grid.rows) 
                                     for c in range(self.grid.cols) 
                                     if self.grid.cells[r][c].mask == 0b1111)
                    title = f"{self.current_preset.name} | Tick: {self.tick} | Alive: {alive_count}"
                else:
                    title = f"{self.current_preset.name} | Tick: {self.tick}"
            else:
                # Single node mode
                self.prog.step_tree(self.root, self.tick)
                draw_frame(self.sim_ax, self.root, self.current_preset.depth, colored=True)
                title = f"{self.current_preset.name} | Tick: {self.tick} | Mask: {self.root.mask:04b}"

            self.sim_ax.set_title(title, color="white", fontsize=11)

            # Update info panel
            self.draw_info_panel()

            self.fig.canvas.draw_idle()

        self.anim = FuncAnimation(self.fig, update, interval=interval, cache_frame_data=False)

    def on_click(self, event):
        """Handle click events."""
        if event.inaxes == self.preset_ax:
            # Check preset button clicks
            for rect, preset in self.preset_buttons:
                if rect.contains_point((event.x, event.y)):
                    self.load_preset(preset)
                    break

        elif event.inaxes == self.sim_ax:
            # Toggle pause/resume
            self.running = not self.running

        self.fig.canvas.draw_idle()

    def on_key(self, event):
        """Handle key press events."""
        if event.key == 'e':
            self.export_frame()
        elif event.key == 'g':
            self.export_gif()

    def export_frame(self):
        """Export current frame as PNG."""
        if not self.current_preset:
            return

        output_dir = "exports"
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"{self.current_preset.name.replace(' ', '_')}_{self.tick}.png")
        self.fig.savefig(path, facecolor="#1a1a2e")
        print(f"Exported frame to {path}")

    def export_gif(self):
        """Export animation as GIF."""
        if not HAS_PIL or not self.current_preset:
            return

        print("Exporting GIF... (this may take a moment)")
        output_path = f"exports/{self.current_preset.name.replace(' ', '_')}.gif"
        os.makedirs("exports", exist_ok=True)

        # Re-run simulation and capture frames
        print("GIF export requires running simulation from start. Use command line:")
        print(f"  python GeoStudio.py --export {self.current_preset.geo_file} --gif {output_path}")

    def run(self):
        """Run the application."""
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        plt.show()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="GeoStudio - Visual Launcher for Binary Quad-Tree Grammar Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python GeoStudio.py                        Launch GUI
  python GeoStudio.py --preset ecosystem     Run ecosystem preset
  python GeoStudio.py --geo examples/spiral.geo --depth 6
  python GeoStudio.py --export ecosystem --frames 100 --output my_export/
  python GeoStudio.py --geo dungeon_generator.geo --gif dungeon.gif
        """
    )

    parser.add_argument('--geo', type=str, help='Path to .geo file')
    parser.add_argument('--preset', type=str, choices=[p.name for p in PRESETS],
                       help='Run a preset by name')
    parser.add_argument('--depth', type=int, default=5, help='Recursion depth')
    parser.add_argument('--speed', type=float, default=3.0, help='Ticks per second')
    parser.add_argument('--grid', action='store_true', help='Enable grid mode')
    parser.add_argument('--random-seed', action='store_true', help='Random seeding for cellular automata')

    # Export options
    parser.add_argument('--export', type=str, help='Export mode (geo file or preset name)')
    parser.add_argument('--frames', type=int, default=60, help='Number of frames to export')
    parser.add_argument('--output', '-o', type=str, default='exports', help='Output path')
    parser.add_argument('--gif', action='store_true', help='Export as GIF')
    parser.add_argument('--fps', type=int, default=10, help='FPS for GIF export')

    # GUI options
    parser.add_argument('--no-gui', action='store_true', help='Run without GUI')

    args = parser.parse_args()

    # Export mode
    if args.export:
        # Find the geo file
        geo_file = args.export
        if not geo_file.endswith('.geo'):
            # Try to find preset
            for p in PRESETS:
                if p.name.lower() == args.export.lower():
                    geo_file = p.geo_file
                    args.depth = p.depth
                    args.speed = p.speed
                    args.grid = p.grid_mode
                    args.random_seed = p.random_seed
                    break
            else:
                geo_file = f"examples/{args.export}.geo"

        if not os.path.exists(geo_file):
            print(f"Error: Geo file not found: {geo_file}")
            sys.exit(1)

        if args.gif:
            if not HAS_PIL:
                print("Error: Pillow required for GIF export. Install with: pip install Pillow")
                sys.exit(1)
            export_gif(geo_file, args.output, num_frames=args.frames,
                      depth=args.depth, fps=args.fps, speed=args.speed, 
                      grid_mode=args.grid, random_seed=args.random_seed)
        else:
            export_frames(geo_file, args.output, num_frames=args.frames,
                         depth=args.depth, speed=args.speed, grid_mode=args.grid,
                         random_seed=args.random_seed)
        return

    # Single geo file mode (no GUI)
    if args.geo and args.no_gui:
        from .binary_quad_tree import run_script_demo, run_script_grid_demo
        with open(args.geo, 'r') as f:
            script = f.read()
        
        # Auto-detect grid mode
        use_grid = args.grid or any(kw in args.geo.lower() for kw in 
                                   ['conway', 'dungeon', 'ecosystem', 'nb_', 'heat_', 
                                    'signal_', 'forest_fire'])
        
        if use_grid:
            run_script_grid_demo(script, start_mask=0b1000,
                                ticks_per_second=args.speed,
                                max_depth=min(args.depth, 4),
                                random_seed=args.random_seed or 'conway' in args.geo.lower())
        else:
            run_script_demo(script, start_mask=0b1000, ticks_per_second=args.speed,
                           max_depth=args.depth)
        return

    # GUI mode (default)
    app = GeoStudioApp()
    app.run()


if __name__ == '__main__':
    main()
