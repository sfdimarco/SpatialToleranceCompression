#!/usr/bin/env python3
"""
Kohonen Self-Organizing Map - Color Learning Demo
==================================================
A beautiful visual demonstration of self-organization where a 2D grid
of neurons learns to organize the RGB color space into a smooth gradient.

Watch as random color preferences self-organize into a coherent color map!

Features:
  - 10×10 grid of SOM neurons (100 neurons total)
  - Each neuron has 3D weight vector (R, G, B)
  - Competitive learning with neighborhood cooperation
  - Real-time visualization of self-organization
  - Interactive color input and training

Controls:
  - SPACE: Toggle auto-training (random colors)
  - C: Click to input custom color
  - T: Toggle training mode
  - R: Reset with random weights
  - S: Save current weight map as image
  - Esc: Quit

Run: python kohonen_color_demo.py
"""

import sys
import os
import random
import math
import time

# Add parent directory to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import (
    Grid, Program, load_geo, family_of,
    X_LOOP, Z_LOOP, Y_LOOP,
)

# Define mask constants
GATE_ON = 0b1111
GATE_OFF = 0b0000


class KohonenColorSOM:
    """
    Kohonen Self-Organizing Map for RGB Color Space.
    
    Architecture:
      10×10 grid of neurons
      Each neuron has 3D weight vector (R, G, B)
      Learns to organize color space topologically
    
    Learning:
      1. Present random RGB color
      2. Find best matching neuron (minimum Euclidean distance)
      3. Update winner + neighborhood toward input color
      4. Repeat - watch self-organization emerge!
    """
    
    GRID_SIZE = 10
    WEIGHT_DIM = 3  # RGB
    
    def __init__(self):
        # Initialize weights randomly
        self.weights = {}  # (row, col) → [r, g, b] (0-255)
        self.activations = {}  # (row, col) → activation level
        self.learning_rate = 0.3
        self.neighborhood_radius = 3.0
        self.epoch = 0
        self.current_input = None
        self.winner_pos = None
        
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights randomly."""
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                self.weights[(row, col)] = [
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                ]
                self.activations[(row, col)] = 0.0
    
    def _compute_distance(self, weight, input_color):
        """Compute Euclidean distance in RGB space."""
        return math.sqrt(sum((w - i) ** 2 for w, i in zip(weight, input_color)))
    
    def _find_winner(self, input_color):
        """Find Best Matching Unit (minimum distance)."""
        min_dist = float('inf')
        winner = None
        
        for pos, weight in self.weights.items():
            dist = self._compute_distance(weight, input_color)
            if dist < min_dist:
                min_dist = dist
                winner = pos
        
        self.winner_pos = winner
        return winner, min_dist
    
    def _get_neighborhood(self, center_pos, radius):
        """Get all neurons within neighborhood radius."""
        neighbors = []
        cr, cc = center_pos
        
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                dist = math.sqrt((row - cr) ** 2 + (col - cc) ** 2)
                if dist <= radius:
                    neighbors.append(((row, col), dist))
        
        return neighbors
    
    def train_step(self, input_color):
        """
        Execute one training step.
        
        Args:
            input_color: (R, G, B) tuple (0-255)
        """
        self.current_input = input_color
        self.epoch += 1
        
        # Find winner
        winner, dist = self._find_winner(input_color)
        
        if winner is None:
            return
        
        # Get neighborhood
        neighbors = self._get_neighborhood(winner, self.neighborhood_radius)
        
        # Update weights
        for pos, dist_from_center in neighbors:
            # Gaussian neighborhood function
            influence = math.exp(-(dist_from_center ** 2) / (2 * self.neighborhood_radius ** 2))
            lr = self.learning_rate * influence
            
            # Update weight toward input
            weight = self.weights[pos]
            for i in range(3):
                weight[i] += lr * (input_color[i] - weight[i])
                weight[i] = max(0, min(255, weight[i]))  # Clamp
            
            # Update activation (for visualization)
            self.activations[pos] = influence
        
        # Decay learning parameters
        self.learning_rate = max(0.01, self.learning_rate * 0.9995)
        self.neighborhood_radius = max(1.0, self.neighborhood_radius * 0.999)
    
    def get_weight_color(self, pos):
        """Get weight as RGB tuple."""
        return tuple(int(w) for w in self.weights[pos])
    
    def get_activation(self, pos):
        """Get activation level (0-1)."""
        return self.activations.get(pos, 0.0)
    
    def reset(self):
        """Reset weights randomly."""
        self._init_weights()
        self.learning_rate = 0.3
        self.neighborhood_radius = 3.0
        self.epoch = 0
    
    def get_statistics(self):
        """Get training statistics."""
        if not self.current_input:
            return {}
        
        winner, dist = self._find_winner(self.current_input)
        
        # Compute quantization error (average distance)
        total_dist = sum(
            self._compute_distance(w, self.current_input)
            for w in self.weights.values()
        )
        avg_dist = total_dist / len(self.weights)
        
        return {
            'winner': winner,
            'distance': dist,
            'avg_distance': avg_dist,
            'learning_rate': self.learning_rate,
            'neighborhood': self.neighborhood_radius,
        }


# ── Pygame Visualizer ──────────────────────────────────────────────

def run_gui():
    try:
        import pygame
    except ImportError:
        print("pygame required. Install: pip install pygame")
        return
    
    pygame.init()
    W, H = 1200, 900
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Kohonen Self-Organizing Map - RGB Color Space Visualization")
    clock = pygame.time.Clock()
    
    # Fonts
    font_title = pygame.font.Font(None, 48)
    font_big = pygame.font.Font(None, 36)
    font_med = pygame.font.Font(None, 28)
    font_sm = pygame.font.Font(None, 22)
    
    # Colors
    BG = (10, 10, 20)
    PANEL_BG = (20, 20, 35)
    WHITE = (240, 240, 255)
    DIM = (120, 120, 140)
    
    # State
    som = KohonenColorSOM()
    auto_train = True
    training_count = 0
    status_msg = "Auto-training: ON"
    
    # Layout
    SOM_LEFT, SOM_TOP = 100, 150
    NEURON_SIZE = 50
    NEURON_GAP = 8
    
    def neuron_rect(row, col):
        x = SOM_LEFT + col * (NEURON_SIZE + NEURON_GAP)
        y = SOM_TOP + row * (NEURON_SIZE + NEURON_GAP)
        return pygame.Rect(x, y, NEURON_SIZE, NEURON_SIZE)
    
    # Color picker
    PICKER_LEFT, PICKER_TOP = SOM_LEFT + som.GRID_SIZE * (NEURON_SIZE + NEURON_GAP) + 50, SOM_TOP
    PICKER_SIZE = 150
    
    current_color = [128, 128, 128]
    color_sliders = {
        'R': {'rect': pygame.Rect(PICKER_LEFT, PICKER_TOP, 200, 30), 'value': 128},
        'G': {'rect': pygame.Rect(PICKER_LEFT, PICKER_TOP + 50, 200, 30), 'value': 128},
        'B': {'rect': pygame.Rect(PICKER_LEFT, PICKER_TOP + 100, 200, 30), 'value': 128},
    }
    dragging_slider = None
    
    # Main loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Auto-training
        if auto_train:
            for _ in range(10):  # Speed up training
                random_color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
                som.train_step(random_color)
            training_count += 1
            status_msg = f"Training: {training_count} epochs | LR: {som.learning_rate:.3f} | Neighborhood: {som.neighborhood_radius:.2f}"
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_SPACE:
                    auto_train = not auto_train
                    status_msg = f"Auto-training: {'ON' if auto_train else 'OFF'}"
                
                elif event.key == pygame.K_t:
                    if not auto_train:
                        # Manual training step
                        input_color = tuple(color_sliders[c]['value'] for c in 'RGB')
                        som.train_step(input_color)
                        training_count += 1
                        status_msg = f"Trained on current color"
                
                elif event.key == pygame.K_r:
                    som.reset()
                    training_count = 0
                    status_msg = "Weights reset"
                
                elif event.key == pygame.K_s:
                    # Save visualization
                    save_surface = pygame.Surface((som.GRID_SIZE * NEURON_SIZE, som.GRID_SIZE * NEURON_SIZE))
                    for row in range(som.GRID_SIZE):
                        for col in range(som.GRID_SIZE):
                            rect = pygame.Rect(
                                col * NEURON_SIZE,
                                row * NEURON_SIZE,
                                NEURON_SIZE, NEURON_SIZE
                            )
                            color = som.get_weight_color((row, col))
                            pygame.draw.rect(save_surface, color, rect)
                    pygame.image.save(save_surface, "kohonen_color_map.png")
                    status_msg = "Saved to kohonen_color_map.png"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                # Check color picker
                for channel, info in color_sliders.items():
                    if info['rect'].collidepoint(mx, my):
                        dragging_slider = channel
                        # Update slider value
                        rel_x = mx - info['rect'].x
                        info['value'] = int(255 * rel_x / info['rect'].width)
                        info['value'] = max(0, min(255, info['value']))
                        current_color = [color_sliders[c]['value'] for c in 'RGB']
                
                # Check SOM grid (manual input)
                for row in range(som.GRID_SIZE):
                    for col in range(som.GRID_SIZE):
                        if neuron_rect(row, col).collidepoint(mx, my):
                            # Use that neuron's weight as input
                            input_color = som.get_weight_color((row, col))
                            current_color = list(input_color)
                            for c, val in zip('RGB', input_color):
                                color_sliders[c]['value'] = val
            
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = None
            
            elif event.type == pygame.MOUSEMOTION:
                if dragging_slider:
                    mx, my = event.pos
                    info = color_sliders[dragging_slider]
                    rel_x = mx - info['rect'].x
                    info['value'] = int(255 * rel_x / info['rect'].width)
                    info['value'] = max(0, min(255, info['value']))
                    current_color = [color_sliders[c]['value'] for c in 'RGB']
        
        # Draw
        screen.fill(BG)
        
        # Title
        title = font_title.render("Kohonen Self-Organizing Map - RGB Color Space", True, WHITE)
        screen.blit(title, (W // 2 - title.get_width() // 2, 20))
        
        # Subtitle
        subtitle = font_sm.render(
            "SPACE: auto-train | T: manual train | R: reset | S: save | Click neuron to sample color",
            True, DIM
        )
        screen.blit(subtitle, (W // 2 - subtitle.get_width() // 2, 65))
        
        # Draw SOM grid
        grid_label = font_big.render("Self-Organizing Color Map (10×10)", True, WHITE)
        screen.blit(grid_label, (SOM_LEFT, SOM_TOP - 35))
        
        for row in range(som.GRID_SIZE):
            for col in range(som.GRID_SIZE):
                rect = neuron_rect(row, col)
                color = som.get_weight_color((row, col))
                
                # Draw neuron color
                pygame.draw.rect(screen, color, rect, border_radius=8)
                
                # Draw activation overlay (when winner)
                activation = som.get_activation((row, col))
                if activation > 0.1:
                    overlay = pygame.Surface((NEURON_SIZE, NEURON_SIZE), pygame.SRCALPHA)
                    alpha = int(255 * activation * 0.5)
                    pygame.draw.circle(overlay, (255, 255, 255, alpha),
                                      (NEURON_SIZE // 2, NEURON_SIZE // 2),
                                      NEURON_SIZE // 2)
                    screen.blit(overlay, (rect.x, rect.y))
                
                # Border
                if som.winner_pos == (row, col):
                    pygame.draw.rect(screen, WHITE, rect, 3, border_radius=8)
                else:
                    pygame.draw.rect(screen, DIM, rect, 1, border_radius=8)
        
        # Draw color picker
        picker_label = font_big.render("Color Input", True, WHITE)
        screen.blit(picker_label, (PICKER_LEFT, PICKER_TOP - 35))
        
        # Current color preview
        preview_rect = pygame.Rect(PICKER_LEFT, PICKER_TOP + 150, PICKER_SIZE, PICKER_SIZE)
        pygame.draw.rect(screen, tuple(current_color), preview_rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, preview_rect, 2, border_radius=8)
        
        # RGB sliders
        for channel, info in color_sliders.items():
            # Label
            label = font_med.render(channel, True, WHITE)
            screen.blit(label, (info['rect'].x - 30, info['rect'].y + 5))
            
            # Slider background
            pygame.draw.rect(screen, DIM, info['rect'], border_radius=4)
            
            # Slider value
            slider_color = (255, 0, 0) if channel == 'R' else (0, 255, 0) if channel == 'G' else (0, 128, 255)
            fill_rect = pygame.Rect(
                info['rect'].x, info['rect'].y,
                int(info['rect'].width * info['value'] / 255),
                info['rect'].height
            )
            pygame.draw.rect(screen, slider_color, fill_rect, border_radius=4)
            
            # Slider border
            pygame.draw.rect(screen, WHITE, info['rect'], 2, border_radius=4)
            
            # Value text
            value_text = font_sm.render(str(info['value']), True, WHITE)
            screen.blit(value_text, (info['rect'].right + 10, info['rect'].y + 5))
        
        # Train button
        train_btn_rect = pygame.Rect(PICKER_LEFT, PICKER_TOP + 220, 200, 40)
        train_color = (0, 200, 100) if not auto_train else (100, 100, 100)
        pygame.draw.rect(screen, train_color, train_btn_rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, train_btn_rect, 2, border_radius=8)
        train_text = font_med.render("TRAIN (T)", True, WHITE)
        screen.blit(train_text, (train_btn_rect.centerx - train_text.get_width() // 2,
                                  train_btn_rect.centery - train_text.get_height() // 2))
        
        # Info panel
        panel_x, panel_y = SOM_LEFT, H - 200
        pygame.draw.rect(screen, PANEL_BG, (panel_x, panel_y, W - SOM_LEFT - 100, 180), border_radius=12)
        pygame.draw.rect(screen, DIM, (panel_x, panel_y, W - SOM_LEFT - 100, 180), 2, border_radius=12)
        
        # Statistics
        stats = som.get_statistics()
        if stats:
            stat_lines = [
                f"Epoch: {som.epoch}",
                f"Winner: {stats.get('winner', 'N/A')}",
                f"Distance: {stats.get('distance', 0):.1f}",
                f"Avg Distance: {stats.get('avg_distance', 0):.1f}",
                f"Learning Rate: {stats.get('learning_rate', 0):.4f}",
                f"Neighborhood Radius: {stats.get('neighborhood', 0):.2f}",
            ]
        else:
            stat_lines = [
                f"Epoch: {som.epoch}",
                "Present a color to see statistics",
            ]
        
        for i, line in enumerate(stat_lines):
            text = font_sm.render(line, True, WHITE)
            screen.blit(text, (panel_x + 20, panel_y + 15 + i * 25))
        
        # Status
        status = font_med.render(status_msg, True, WHITE)
        screen.blit(status, (panel_x + 20, panel_y + 160))
        
        # Instructions
        instructions = [
            "Watch colors self-organize from random to ordered!",
            "Each neuron learns to respond to similar colors.",
            "Neighborhood cooperation creates smooth gradients.",
        ]
        for i, inst in enumerate(instructions):
            text = font_sm.render(inst, True, DIM)
            screen.blit(text, (W - 350, panel_y + 15 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Quick test
        print("Testing Kohonen Color SOM...")
        
        som = KohonenColorSOM()
        
        print(f"\nInitial weights (random):")
        print(f"  (0,0): {som.get_weight_color((0, 0))}")
        print(f"  (5,5): {som.get_weight_color((5, 5))}")
        print(f"  (9,9): {som.get_weight_color((9, 9))}")
        
        print(f"\nTraining on 1000 random colors...")
        for i in range(1000):
            random_color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            som.train_step(random_color)
            
            if i % 200 == 0:
                stats = som.get_statistics()
                print(f"  Epoch {i}: LR={stats['learning_rate']:.3f}, "
                      f"Neighborhood={stats['neighborhood']:.2f}, "
                      f"Avg Dist={stats['avg_distance']:.1f}")
        
        print(f"\nFinal weights (organized):")
        print(f"  (0,0): {som.get_weight_color((0, 0))}")
        print(f"  (5,5): {som.get_weight_color((5, 5))}")
        print(f"  (9,9): {som.get_weight_color((9, 9))}")
        
        print(f"\nTesting with specific colors:")
        test_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for color in test_colors:
            winner, dist = som._find_winner(color)
            print(f"  {color} -> Winner: {winner}, Distance: {dist:.1f}")
        
        print("\nTest complete! Run without --test for visual demo.")
    else:
        run_gui()
