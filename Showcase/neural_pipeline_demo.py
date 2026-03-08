#!/usr/bin/env python3
"""
Pattern Recognition Pipeline with Self-Organizing Memory
=========================================================
Interactive neural network that learns to recognize and recall patterns.

Features:
  - Self-Organizing Map (SOM) for feature extraction
  - Hopfield Network for associative memory
  - Hebbian learning for self-training
  - Interactive pattern drawing and recognition

Controls:
  - Draw: Click/drag on 5×5 input grid
  - Train: Press T to train on current pattern
  - Recall: Press R to recall from memory
  - Clear: Press C to clear input
  - Random: Press SPACE for random pattern
  - Quit: Esc

Run: python neural_pipeline_demo.py
"""

import sys
import os
import random
import time

# Add parent directory to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import (
    Grid, Program, load_geo, family_of,
    X_LOOP, Z_LOOP, Y_LOOP,
)

# Define mask constants
GATE_ON = 0b1111   # All quadrants active
GATE_OFF = 0b0000  # All quadrants inactive

# ── Pattern Definitions ────────────────────────────────────────────

PATTERNS = {
    'A': [1,0,1,0,0,  1,0,1,0,0,  1,1,1,0,0,  1,0,1,0,0,  1,0,1,0,0],
    'B': [1,1,1,0,0,  1,0,1,0,0,  1,1,1,0,0,  1,0,1,0,0,  1,1,1,0,0],
    'C': [1,1,1,0,0,  1,0,1,0,0,  1,0,1,0,0,  1,0,1,0,0,  1,1,1,0,0],
    'D': [1,1,0,0,0,  1,0,1,0,0,  1,0,1,0,0,  1,0,1,0,0,  1,1,0,0,0],
    'E': [1,1,1,0,0,  1,0,1,0,0,  1,1,1,0,0,  1,0,1,0,0,  1,1,1,0,0],
    '0': [1,1,1,0,0,  1,0,1,0,0,  1,0,1,0,0,  1,0,1,0,0,  1,1,1,0,0],
    '1': [0,1,0,0,0,  1,1,0,0,0,  0,1,0,0,0,  0,1,0,0,0,  1,1,1,0,0],
    '2': [1,1,1,0,0,  1,0,1,0,0,  0,1,1,0,0,  1,0,0,0,0,  1,1,1,0,0],
    '3': [1,1,1,0,0,  0,1,0,0,0,  1,1,1,0,0,  0,1,0,0,0,  1,1,1,0,0],
    'X': [1,0,1,0,0,  0,1,0,0,0,  0,1,0,0,0,  0,1,0,0,0,  1,0,1,0,0],
}


class PatternPipeline:
    """
    Pattern Recognition Pipeline with Self-Organizing Memory.
    
    Architecture:
      5×5 Input → 3×3 Feature Map (SOM) → 10-neuron Memory (Hopfield) → Output
    
    Learning:
      - SOM: Competitive learning (winner + neighborhood)
      - Memory: Hebbian learning (co-activation strengthens connections)
    """
    
    # Grid configuration
    INPUT_ROWS, INPUT_COLS = 5, 5
    FEATURE_ROWS, FEATURE_COLS = 3, 3
    MEMORY_SIZE = 10
    
    def __init__(self):
        # Load .geo programs
        pipeline_geo = os.path.join(
            os.path.dirname(__file__),
            "..", "examples", "neural_pipeline", "pipeline_full.geo"
        )
        self.base_program = load_geo(pipeline_geo)
        
        # Initialize state
        self.input_pattern = [0] * 25  # 5×5 binary input
        self.feature_weights = {}  # (fr, fc) → [w0..w24]
        self.memory_weights = {}  # (i, j) → weight
        self.memory_state = [0] * self.MEMORY_SIZE
        self.training_mode = False
        self.epoch = 0
        self.learning_rate = 0.1
        
        # Initialize feature map weights
        self._init_feature_weights()
        
        # Build grid
        self._build()
    
    def _init_feature_weights(self):
        """Initialize SOM weights randomly."""
        for fr in range(self.FEATURE_ROWS):
            for fc in range(self.FEATURE_COLS):
                self.feature_weights[(fr, fc)] = [
                    random.randint(20, 80) for _ in range(25)
                ]
    
    def _build(self):
        """Build the grid with all layers."""
        def mask_fn(r, c):
            # Input layer (rows 2-6, cols 1-5)
            if 2 <= r <= 6 and 1 <= c <= 5:
                ir, ic = r - 2, c - 1
                idx = ir * 5 + ic
                return GATE_ON if self.input_pattern[idx] else GATE_OFF
            
            # Feature map (rows 1-3, cols 7-9)
            if 1 <= r <= 3 and 7 <= c <= 9:
                return X_LOOP[0]  # Active state
            
            # Memory layer (rows 0-1, cols 11-15)
            if r <= 1 and 11 <= c <= 14:
                return Z_LOOP[0]  # Inactive initially
            
            return GATE_OFF
        
        self.grid = Grid.make(7, 16, self.base_program, init_mask_fn=mask_fn)
    
    def set_input(self, pattern):
        """Set input pattern (25-element binary list)."""
        self.input_pattern = pattern[:25]
        self._rebuild_input_layer()
    
    def _rebuild_input_layer(self):
        """Update input layer masks."""
        for r in range(self.INPUT_ROWS):
            for c in range(self.INPUT_COLS):
                idx = r * 5 + c
                mask = GATE_ON if self.input_pattern[idx] else GATE_OFF
                self.grid.cells[r + 2][c + 1].mask = mask
    
    def train_step(self):
        """Execute one training step."""
        # Find best matching unit (BMU) in feature map
        bmu = self._find_bmu()
        
        if bmu is None:
            return
        
        bmu_pos, bmu_dist = bmu
        
        # Update SOM weights
        self._update_som_weights(bmu_pos)
        
        # Store in memory (simplified)
        if self.training_mode:
            self._store_in_memory()
        
        self.epoch += 1
    
    def _find_bmu(self):
        """Find Best Matching Unit in SOM (minimum distance)."""
        min_dist = float('inf')
        bmu_pos = None
        
        for fr in range(self.FEATURE_ROWS):
            for fc in range(self.FEATURE_COLS):
                weights = self.feature_weights[(fr, fc)]
                dist = self._compute_distance(weights)
                if dist < min_dist:
                    min_dist = dist
                    bmu_pos = (fr, fc)
        
        return (bmu_pos, min_dist) if bmu_pos else None
    
    def _compute_distance(self, weights):
        """Compute Manhattan distance between input and weights."""
        dist = 0
        for i in range(25):
            dist += abs(self.input_pattern[i] * 100 - weights[i])
        return dist
    
    def _update_som_weights(self, bmu_pos):
        """Update SOM weights (winner + neighborhood)."""
        lr = self.learning_rate
        
        for fr in range(self.FEATURE_ROWS):
            for fc in range(self.FEATURE_COLS):
                # Compute distance from BMU
                dist_from_bmu = abs(fr - bmu_pos[0]) + abs(fc - bmu_pos[1])
                
                # Neighborhood function (Gaussian-like)
                if dist_from_bmu <= 1:  # Within neighborhood
                    neighborhood_lr = lr * (0.5 if dist_from_bmu == 1 else 1.0)
                    
                    # Update weights
                    weights = self.feature_weights[(fr, fc)]
                    for i in range(25):
                        weights[i] += neighborhood_lr * (
                            self.input_pattern[i] * 100 - weights[i]
                        )
                        # Clamp to valid range
                        weights[i] = max(0, min(100, weights[i]))
    
    def _store_in_memory(self):
        """Store current pattern in Hopfield memory (Hebbian learning)."""
        # Simplified: store as outer product
        for i in range(self.MEMORY_SIZE):
            for j in range(self.MEMORY_SIZE):
                if i != j:
                    # Hebbian: Δw = pre * post
                    pre = self.input_pattern[i % 25]
                    post = self.input_pattern[j % 25]
                    
                    key = (i, j)
                    if key not in self.memory_weights:
                        self.memory_weights[key] = 0
                    
                    self.memory_weights[key] += (pre * 2 - 1) * (post * 2 - 1)
    
    def recall(self):
        """Recall pattern from memory (async update)."""
        # Initialize from input
        for i in range(self.MEMORY_SIZE):
            self.memory_state[i] = self.input_pattern[i % 25] * 2 - 1
        
        # Async update (multiple iterations)
        for _ in range(5):
            for i in range(self.MEMORY_SIZE):
                h = sum(
                    self.memory_weights.get((i, j), 0) * self.memory_state[j]
                    for j in range(self.MEMORY_SIZE)
                    if i != j
                )
                self.memory_state[i] = 1 if h > 0 else -1
        
        # Convert back to binary
        recalled = [(s + 1) // 2 for s in self.memory_state[:25]]
        return recalled
    
    def recognize(self, pattern=None):
        """
        Recognize input pattern.
        
        Returns:
          dict with 'class', 'confidence', 'bmu'
        """
        if pattern:
            self.set_input(pattern)
        
        bmu_result = self._find_bmu()
        if bmu_result is None:
            return {'class': '?', 'confidence': 0, 'bmu': None}
        
        bmu_pos, dist = bmu_result
        
        # Compute confidence (inverse distance)
        max_dist = 25 * 100  # Maximum possible distance
        confidence = 1.0 - (dist / max_dist)
        
        # Map BMU to class (simplified: use position as class index)
        class_idx = bmu_pos[0] * 3 + bmu_pos[1]
        class_labels = list(PATTERNS.keys())
        class_label = class_labels[class_idx % len(class_labels)]
        
        return {
            'class': class_label,
            'confidence': confidence,
            'bmu': bmu_pos,
        }
    
    def step(self, tick):
        """Advance simulation by one tick."""
        self.grid.step(tick)
    
    def clear(self):
        """Clear input pattern."""
        self.input_pattern = [0] * 25
        self._rebuild_input_layer()
    
    def random_pattern(self):
        """Generate random input pattern."""
        self.input_pattern = [random.randint(0, 1) for _ in range(25)]
        self._rebuild_input_layer()
    
    def get_feature_weights(self, pos):
        """Get weight vector for feature neuron."""
        return self.feature_weights.get(pos, [0] * 25)


# ── Pygame Visualizer ──────────────────────────────────────────────

def run_gui():
    try:
        import pygame
    except ImportError:
        print("pygame required. Install: pip install pygame")
        return
    
    pygame.init()
    W, H = 1400, 900
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Pattern Recognition Pipeline - Self-Organizing Memory")
    clock = pygame.time.Clock()
    
    # Fonts
    font_title = pygame.font.Font(None, 44)
    font_big = pygame.font.Font(None, 32)
    font_med = pygame.font.Font(None, 26)
    font_sm = pygame.font.Font(None, 22)
    
    # Colors
    BG = (14, 14, 28)
    PANEL_BG = (22, 22, 40)
    WHITE = (220, 220, 235)
    DIM = (130, 130, 155)
    GREEN = (60, 210, 110)
    RED = (240, 70, 70)
    BLUE = (80, 140, 255)
    ORANGE = (255, 170, 50)
    CYAN = (80, 220, 240)
    
    # State
    pipeline = PatternPipeline()
    tick = 0
    drawing = False
    last_draw_idx = -1
    status_msg = "Draw a pattern (click/drag)"
    show_recall = False
    recalled_pattern = None
    
    # Layout
    INPUT_LEFT, INPUT_TOP = 100, 150
    CELL_SIZE = 60
    CELL_GAP = 8
    
    def input_rect(row, col):
        x = INPUT_LEFT + col * (CELL_SIZE + CELL_GAP)
        y = INPUT_TOP + row * (CELL_SIZE + CELL_GAP)
        return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    
    # Main loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_t:
                    pipeline.training_mode = not pipeline.training_mode
                    status_msg = f"Training: {'ON' if pipeline.training_mode else 'OFF'}"
                
                elif event.key == pygame.K_r:
                    recalled_pattern = pipeline.recall()
                    show_recall = not show_recall
                    status_msg = "Pattern recalled from memory"
                
                elif event.key == pygame.K_c:
                    pipeline.clear()
                    status_msg = "Input cleared"
                    show_recall = False
                
                elif event.key == pygame.K_SPACE:
                    pipeline.random_pattern()
                    status_msg = "Random pattern generated"
                    show_recall = False
                
                elif event.key == pygame.K_l:
                    # Load a known pattern
                    pattern_key = random.choice(list(PATTERNS.keys()))
                    pipeline.set_input(PATTERNS[pattern_key])
                    status_msg = f"Loaded pattern: {pattern_key}"
                
                elif event.key == pygame.K_p:
                    # Train on all patterns
                    for _ in range(10):
                        for pattern in PATTERNS.values():
                            pipeline.set_input(pattern)
                            pipeline.train_step()
                    status_msg = f"Trained on all patterns (epoch {pipeline.epoch})"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    drawing = True
                    # Draw on click
                    mx, my = event.pos
                    for row in range(5):
                        for col in range(5):
                            if input_rect(row, col).collidepoint(mx, my):
                                idx = row * 5 + col
                                pipeline.input_pattern[idx] = 1
                                last_draw_idx = idx
                                show_recall = False
            
            elif event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                last_draw_idx = -1
            
            elif event.type == pygame.MOUSEMOTION:
                if drawing:
                    mx, my = event.pos
                    for row in range(5):
                        for col in range(5):
                            if input_rect(row, col).collidepoint(mx, my):
                                idx = row * 5 + col
                                if idx != last_draw_idx:
                                    pipeline.input_pattern[idx] = 1
                                    last_draw_idx = idx
                                    show_recall = False
        
        # Auto-step
        pipeline.step(tick)
        tick += 1
        
        # Draw
        screen.fill(BG)
        
        # Title
        title = font_title.render("Pattern Recognition Pipeline", True, WHITE)
        screen.blit(title, (W // 2 - title.get_width() // 2, 20))
        
        # Subtitle
        subtitle = font_med.render(
            "Draw | T=train | R=recall | C=clear | SPACE=random | L=load | P=train_all",
            True, DIM
        )
        screen.blit(subtitle, (W // 2 - subtitle.get_width() // 2, 60))
        
        # Input grid
        grid_label = font_big.render("Input (5×5)", True, GREEN)
        screen.blit(grid_label, (INPUT_LEFT, INPUT_TOP - 35))
        
        for row in range(5):
            for col in range(5):
                rect = input_rect(row, col)
                idx = row * 5 + col
                active = pipeline.input_pattern[idx]
                
                color = GREEN if active else (40, 40, 60)
                pygame.draw.rect(screen, color, rect, border_radius=8)
                pygame.draw.rect(screen, WHITE if active else DIM, rect, 2, border_radius=8)
        
        # Feature map visualization
        feat_left, feat_top = INPUT_LEFT + 400, INPUT_TOP
        feat_label = font_big.render("Feature Map (3×3 SOM)", True, ORANGE)
        screen.blit(feat_label, (feat_left, feat_top - 35))
        
        for fr in range(3):
            for fc in range(3):
                rect = pygame.Rect(
                    feat_left + fc * (CELL_SIZE + CELL_GAP),
                    feat_top + fr * (CELL_SIZE + CELL_GAP),
                    CELL_SIZE, CELL_SIZE
                )
                
                # Color by weight similarity to input
                weights = pipeline.feature_weights[(fr, fc)]
                dist = pipeline._compute_distance(weights)
                similarity = 1.0 - (dist / (25 * 100))
                
                # Gradient from red (low) to green (high)
                r = int(255 * (1 - similarity))
                g = int(255 * similarity)
                color = (r, g, 50)
                
                pygame.draw.rect(screen, color, rect, border_radius=8)
                pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
                
                # Show distance
                dist_text = font_sm.render(f"{dist:.0f}", True, WHITE)
                screen.blit(dist_text, (rect.centerx - dist_text.get_width() // 2,
                                        rect.centery - 10))
        
        # Memory visualization
        mem_left, mem_top = feat_left + 400, INPUT_TOP
        mem_label = font_big.render("Memory (Hopfield)", True, BLUE)
        screen.blit(mem_label, (mem_left, mem_top - 35))
        
        for i in range(10):
            rect = pygame.Rect(
                mem_left + (i % 5) * (CELL_SIZE + CELL_GAP),
                mem_top + (i // 5) * (CELL_SIZE + CELL_GAP),
                CELL_SIZE, CELL_SIZE
            )
            
            state = pipeline.memory_state[i]
            color = GREEN if state > 0 else (40, 40, 60)
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, WHITE if state > 0 else DIM, rect, 2, border_radius=8)
        
        # Recall visualization
        if show_recall and recalled_pattern:
            recall_left, recall_top = INPUT_LEFT, INPUT_TOP + 400
            recall_label = font_big.render("Recalled Pattern", True, CYAN)
            screen.blit(recall_label, (recall_left, recall_top - 35))
            
            for row in range(5):
                for col in range(5):
                    rect = pygame.Rect(
                        recall_left + col * (CELL_SIZE + CELL_GAP),
                        recall_top + row * (CELL_SIZE + CELL_GAP),
                        CELL_SIZE, CELL_SIZE
                    )
                    idx = row * 5 + col
                    active = recalled_pattern[idx] if idx < len(recalled_pattern) else 0
                    
                    color = CYAN if active else (40, 40, 60)
                    pygame.draw.rect(screen, color, rect, border_radius=8)
                    pygame.draw.rect(screen, WHITE if active else DIM, rect, 2, border_radius=8)
        
        # Info panel
        panel_x, panel_y = INPUT_LEFT, H - 180
        pygame.draw.rect(screen, PANEL_BG, (panel_x, panel_y, W - 200, 160), border_radius=12)
        pygame.draw.rect(screen, DIM, (panel_x, panel_y, W - 200, 160), 2, border_radius=12)
        
        # Status
        status = font_med.render(f"Status: {status_msg}", True, WHITE)
        screen.blit(status, (panel_x + 20, panel_y + 15))
        
        # Training info
        train_info = font_med.render(
            f"Training: {'ON' if pipeline.training_mode else 'OFF'} | "
            f"Epoch: {pipeline.epoch} | "
            f"LR: {pipeline.learning_rate:.2f}",
            True, WHITE
        )
        screen.blit(train_info, (panel_x + 20, panel_y + 50))
        
        # Recognition result
        result = pipeline.recognize()
        recog_text = font_med.render(
            f"Recognition: Class={result['class']} | "
            f"Confidence: {result['confidence']:.1%} | "
            f"BMU: {result['bmu']}",
            True, WHITE
        )
        screen.blit(recog_text, (panel_x + 20, panel_y + 85))
        
        # Instructions
        instructions = [
            "Click/drag to draw on input grid",
            "T: Toggle training mode",
            "R: Recall pattern from memory",
            "P: Train on all patterns (10 epochs)",
            "L: Load random known pattern",
        ]
        for i, inst in enumerate(instructions):
            inst_text = font_sm.render(inst, True, DIM)
            screen.blit(inst_text, (panel_x + 20, panel_y + 120 + i * 22))
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Quick test
        pipeline = PatternPipeline()
        
        print("Testing Pattern Recognition Pipeline...")
        print("\n1. Testing with pattern A:")
        pipeline.set_input(PATTERNS['A'])
        result = pipeline.recognize()
        print(f"   Recognized: {result}")
        
        print("\n2. Training on all patterns...")
        for _ in range(5):
            for pattern in PATTERNS.values():
                pipeline.set_input(pattern)
                pipeline.train_step()
        
        print("\n3. Testing recognition after training:")
        for name, pattern in list(PATTERNS.items())[:3]:
            pipeline.set_input(pattern)
            result = pipeline.recognize()
            print(f"   {name}: {result['class']} ({result['confidence']:.1%})")
        
        print("\n4. Testing recall:")
        noisy = PATTERNS['A'].copy()
        noisy[5] = 1 - noisy[5]  # Flip one bit
        pipeline.set_input(noisy)
        recalled = pipeline.recall()
        print(f"   Recalled from noisy input: {recalled[:10]}...")
        
        print("\nTest complete!")
    else:
        run_gui()
