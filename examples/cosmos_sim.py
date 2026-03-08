"""
cosmos_sim.py - Visual runner for the cosmic .geo simulation

Run with: python cosmos_sim.py
"""

import sys
import os
import math

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from BinaryQuadTreeTest import (
    Node, load_geo,
    Y_LOOP, X_LOOP, Z_LOOP, DIAG_LOOP, GATES,
    family_of
)

# Try to import pygame, fall back to ASCII if not available
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    print("pygame not found. Running ASCII mode.")


class CosmosVisualizer:
    """Visualize the .geo cosmic simulation"""
    
    def __init__(self, width=800, height=800, max_depth=7):
        self.width = width
        self.height = height
        self.max_depth = max_depth
        self.tick = 0

        # Load the cosmic script
        geo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cosmos_sim.geo")
        self.program = load_geo(geo_path)

        # Create root node with an active initial pattern
        # Start with Y_LOOP (1000) which will trigger the cosmic rules
        self.root = Node(0.0, 0.0, 1.0, 0, 0b1000)
        
        # Pre-populate some nodes at different depths for initial activity
        self._seed_initial_structure()
        
        # Color palette (cosmic theme)
        self.colors = {
            "Y_LOOP":      (255, 107, 107),    # Red - "positive charge"
            "X_LOOP":      (78, 205, 196),     # Teal - "negative charge"
            "Z_LOOP":      (255, 230, 80),     # Yellow - "radiating/flare"
            "DIAG_LOOP":   (150, 100, 255),    # Purple - "exotic"
            "GATE":        (30, 30, 50),       # Dark - "void/black hole"
        }
        
        # Glow colors for flares
        self.flare_color = (255, 240, 120)
    
    def _seed_initial_structure(self):
        """Create initial quadtree structure with varied masks"""
        import random
        self.root.ensure_children()
        
        # Set different masks for children to create initial pattern
        # TL (red/positive), TR (teal/negative), BR (yellow/radiating), BL (purple/exotic)
        masks = [0b1000, 0b1100, 0b0111, 0b1001]
        for i, child in enumerate(self.root.children):
            if child:
                child.mask = masks[i % len(masks)]
                # Recursively seed deeper levels
                self._seed_deeper(child, 1, masks)
    
    def _seed_deeper(self, node, depth, masks):
        """Recursively seed deeper levels with varied masks"""
        if depth >= self.max_depth - 2:
            return
        
        import random
        node.ensure_children()
        for i, child in enumerate(node.children):
            if child:
                # Mix of active and void cells
                if random.random() < 0.6:
                    child.mask = random.choice(masks)
                else:
                    child.mask = 0b0000  # void
                self._seed_deeper(child, depth + 1, masks)
        
    def step(self):
        """Advance simulation by one tick"""
        self.program.step_tree(self.root, self.tick)
        self.tick += 1
        
    def get_active_nodes(self):
        """Collect all active leaf nodes for rendering"""
        nodes = []
        self._collect_nodes(self.root, nodes)
        return nodes
    
    def _collect_nodes(self, node, nodes_list):
        """Recursively collect active nodes"""
        if node.mask == 0:
            return

        is_leaf = True
        if node.children is not None:
            for i, child in enumerate(node.children):
                if child is not None:
                    is_leaf = False
                    self._collect_nodes(child, nodes_list)

        if is_leaf:
            nodes_list.append(node)
    
    def draw_ascii(self, grid_size=60):
        """Draw ASCII representation"""
        grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
        nodes = self.get_active_nodes()

        # Use ASCII-safe symbols
        symbols = {
            "Y_LOOP": 'O',
            "X_LOOP": '*',
            "Z_LOOP": '+',
            "DIAG_LOOP": '#',
            "GATE": '@',
        }

        for node in nodes:
            # Convert normalized coords to grid
            gx = int((node.x + 0.5) * grid_size)
            gy = int((node.y + 0.5) * grid_size)
            if 0 <= gx < grid_size and 0 <= gy < grid_size:
                family = family_of(node.mask)
                grid[gy][gx] = symbols.get(family, '?')

        # Clear screen and draw
        print("\033[2J\033[H", end="")
        print(f"Cosmos Sim | Tick: {self.tick} | Nodes: {len(nodes)}")
        print("=" * (grid_size + 10))
        for row in grid:
            print(''.join(row))
        print("=" * (grid_size + 10))
        print("Controls: Enter to step, 'q' to quit")


class PygameVisualizer(CosmosVisualizer):
    """Pygame-based visualizer"""
    
    def __init__(self, width=800, height=800, max_depth=7):
        super().__init__(width, height, max_depth)
        
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Cosmic .geo Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Trail effect surface
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.trail_alpha = 40
        
    def draw(self):
        """Render the simulation"""
        # Fade trail effect
        self.trail_surface.fill((5, 10, 25, self.trail_alpha))
        self.screen.blit(self.trail_surface, (0, 0))
        
        nodes = self.get_active_nodes()
        cx, cy = self.width // 2, self.height // 2
        
        for node in nodes:
            # Calculate screen position and size
            size = node.size * min(self.width, self.height)
            x = (node.x + 0.5) * self.width
            y = (node.y + 0.5) * self.height

            # Get family and color
            family = family_of(node.mask)
            base_color = self.colors.get(family, (255, 255, 255))

            # Draw with glow effect for radiating/flare states
            if family == "Z_LOOP":
                # Flare glow
                for radius in [int(size * 1.8), int(size * 1.4), int(size * 1.1)]:
                    alpha = max(30, 100 - radius)
                    glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*self.flare_color, alpha), (radius, radius), radius)
                    self.screen.blit(glow_surf, (x - radius, y - radius))

            # Core shape
            radius = max(2, int(size * 0.8))
            pygame.draw.circle(self.screen, base_color, (int(x), int(y)), radius)

            # Orbital ring for charged states
            if family == "X_LOOP" and size > 4:
                ring_radius = int(size * 1.3)
                pygame.draw.circle(self.screen, (100, 255, 255), (int(x), int(y)), ring_radius, 1)
        
        # Draw UI
        self._draw_ui()
        
        pygame.display.flip()
    
    def _draw_ui(self):
        """Draw tick counter and stats"""
        nodes = self.get_active_nodes()
        text = f"Tick: {self.tick}  |  Active Nodes: {len(nodes)}  |  Depth: {self.max_depth}"
        surf = self.font.render(text, True, (200, 200, 220))
        self.screen.blit(surf, (10, 10))
    
    def run(self, fps=30):
        """Main loop"""
        running = True
        auto_step = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        auto_step = not auto_step
                    elif event.key == pygame.K_r:
                        # Reset
                        self.root = Node(0.0, 0.0, 1.0, 0, 0b1000)
                        self._seed_initial_structure()
                        self.tick = 0
                    elif event.key == pygame.K_UP:
                        self.max_depth = min(10, self.max_depth + 1)
                    elif event.key == pygame.K_DOWN:
                        self.max_depth = max(3, self.max_depth - 1)
            
            if auto_step:
                self.step()
            
            self.draw()
            self.clock.tick(fps)
        
        pygame.quit()


def main():
    """Entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Cosmic .geo Simulation")
    parser.add_argument("--width", type=int, default=800, help="Window width")
    parser.add_argument("--height", type=int, default=800, help="Window height")
    parser.add_argument("--depth", type=int, default=7, help="Max quadtree depth")
    parser.add_argument("--ascii", action="store_true", help="Run in ASCII mode")
    args = parser.parse_args()

    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    if args.ascii or not HAS_PYGAME:
        # ASCII mode - run for limited ticks then exit
        viz = CosmosVisualizer(max_depth=args.depth)
        try:
            for _ in range(10):  # Run 10 ticks then exit
                viz.draw_ascii()
                viz.step()
                import time
                time.sleep(0.3)
        except KeyboardInterrupt:
            pass
        print("\nSimulation ended.")
    else:
        # Pygame mode
        viz = PygameVisualizer(args.width, args.height, args.depth)
        viz.run()


if __name__ == "__main__":
    main()
