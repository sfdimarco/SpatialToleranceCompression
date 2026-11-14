#!/usr/bin/env python3
"""
Hello World Demo - Displays "HI" pattern on a grid
===================================================
Run: python hello_world.py
     python hello_world.py --export  # Export frames to exports/hello_world/
"""

from src import (
    parse_geo_script, Grid, draw_grid_frame
)
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sys
import os

# Constants
GATE_ON = 0b1111   # White/stable on
GATE_OFF = 0b0000  # Dark/stable off

# HI Pattern (7 rows x 5 cols for H, 1 space, 5 cols for I)
# H   H
# H   H
# HHHHH
# H   H
# H   H
#
#   I
#   I
#   I
#   I
#   I

HI_PATTERN = [
    # H (5x5) + space (1) + I (3x5)
    [1, 0, 0, 0, 1, 0, 0, 1, 0],  # Row 0
    [1, 0, 0, 0, 1, 0, 0, 1, 0],  # Row 1
    [1, 1, 1, 1, 1, 0, 0, 1, 0],  # Row 2
    [1, 0, 0, 0, 1, 0, 0, 1, 0],  # Row 3
    [1, 0, 0, 0, 1, 0, 0, 1, 0],  # Row 4
]

ROWS = len(HI_PATTERN)
COLS = len(HI_PATTERN[0])

def init_text_cell(r, c):
    """Initialize cell based on HI pattern."""
    pattern_row = HI_PATTERN[r % ROWS]
    pattern_col = c % COLS
    if pattern_row[pattern_col] == 1:
        return GATE_ON  # White text
    return GATE_OFF     # Dark background

def main():
    export_mode = "--export" in sys.argv

    # Load the hello_world.geo program
    prog = parse_geo_script(open("examples/basics/hello_world.geo").read())
    
    # Create grid with HI pattern
    cell_size = 16.0
    grid = Grid.make(
        rows=ROWS,
        cols=COLS,
        program=prog,
        init_mask_fn=init_text_cell,
        cell_size=cell_size
    )
    
    if export_mode:
        # Export frames
        os.makedirs("exports/hello_world", exist_ok=True)
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("#0d0d0d")
        
        for tick in range(10):
            grid.step(tick)
            draw_grid_frame(ax, grid, max_depth=3)
            ax.set_title(f"HELLO WORLD - HI Pattern  t={tick}",
                         fontsize=12, color="white")
            output_path = f"exports/hello_world/frame_{tick:04d}.png"
            fig.savefig(output_path, facecolor=fig.get_facecolor())
            print(f"Exported frame {tick+1}/10")
        
        print(f"Exported 10 frames to exports/hello_world")
    else:
        # Interactive display
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("#0d0d0d")
        tick = [0]
        
        def update(_):
            grid.step(tick[0])
            tick[0] += 1
            draw_grid_frame(ax, grid, max_depth=3)
            ax.set_title(f"HELLO WORLD - HI Pattern  t={tick[0]}",
                         fontsize=12, color="white")
        
        fig._anim = FuncAnimation(fig, update,
                                   interval=500,
                                   cache_frame_data=False)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()
