#!/usr/bin/env python3
"""
Neural Network Demo - .geo Geometric Grammar as Neural Substrate
================================================================
Interactive pygame visualizer showing how .geo rules implement
threshold logic units, weighted connections, and multi-layer
forward propagation.

Two demos:
  1) Majority-3: 3-input majority vote (threshold neuron)
  2) XOR:        2-layer perceptron solving XOR (non-linearly separable)

Controls:
  Click inputs - Toggle input neurons ON/OFF
  TAB          - Switch between Majority and XOR demos
  SPACE        - Pause/resume ticking
  Right Arrow  - Single-step one tick (while paused)
  R            - Reset current network
  T            - Run truth table test (console)
  A            - Auto-cycle all input combos
  Esc          - Quit

Run:  python neural_demo.py
Test: python neural_demo.py --test
"""

import sys
import os
import math
import time

# Add parent directory to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import (
    Grid, Program, load_geo, family_of,
    X_LOOP, Z_LOOP,
)

# ---------------------------------------------------------------------------
# Network wrappers
# ---------------------------------------------------------------------------

class MajorityNetwork:
    """3-input majority vote on a plus-shaped 3x3 grid.

    Layout:
          col0   col1   col2
    row2: [___]  [IN0]  [___]
    row1: [IN1]  [HID]  [IN2]
    row0: [___]  [OUT]  [___]
    """

    INPUT_CELLS = [(2, 1), (1, 0), (1, 2)]
    HIDDEN_CELL = (1, 1)
    OUTPUT_CELL = (0, 1)
    PADDING     = [(2, 0), (2, 2), (0, 0), (0, 2)]

    def __init__(self):
        geo_path = os.path.join(os.path.dirname(__file__),
                                "..", "examples", "neural", "neural_majority3.geo")
        self.program = load_geo(geo_path)
        self.inputs = [False, False, False]
        self._build()

    def _build(self):
        def mask_fn(r, c):
            if (r, c) == self.HIDDEN_CELL:
                return X_LOOP[0]
            if (r, c) == self.OUTPUT_CELL:
                return Z_LOOP[0]
            if (r, c) in self.INPUT_CELLS:
                idx = self.INPUT_CELLS.index((r, c))
                return 0b1111 if self.inputs[idx] else 0b0000
            return 0b0000

        self.grid = Grid.make(3, 3, self.program, init_mask_fn=mask_fn)

    def set_inputs(self, vals):
        self.inputs = list(vals)
        for i, (r, c) in enumerate(self.INPUT_CELLS):
            self.grid.cells[r][c].mask = 0b1111 if self.inputs[i] else 0b0000

    def toggle_input(self, idx):
        self.inputs[idx] = not self.inputs[idx]
        r, c = self.INPUT_CELLS[idx]
        self.grid.cells[r][c].mask = 0b1111 if self.inputs[idx] else 0b0000

    def step(self, tick):
        self.grid.step(tick)

    def read_output(self):
        node = self.grid.cells[self.OUTPUT_CELL[0]][self.OUTPUT_CELL[1]]
        return family_of(node.mask) == "Y_LOOP"

    def cell_info(self, r, c):
        node = self.grid.cells[r][c]
        return {
            "mask": node.mask,
            "family": family_of(node.mask),
            "vars": dict(node.vars),
        }

    def get_role(self, r, c):
        if (r, c) in self.INPUT_CELLS:
            return "input"
        if (r, c) == self.HIDDEN_CELL:
            return "hidden"
        if (r, c) == self.OUTPUT_CELL:
            return "output"
        return "pad"

    def get_label(self, r, c):
        if (r, c) in self.INPUT_CELLS:
            return f"IN{self.INPUT_CELLS.index((r, c))}"
        if (r, c) == self.HIDDEN_CELL:
            return "HIDDEN"
        if (r, c) == self.OUTPUT_CELL:
            return "OUTPUT"
        return ""

    def get_input_idx(self, r, c):
        if (r, c) in self.INPUT_CELLS:
            return self.INPUT_CELLS.index((r, c))
        return -1

    def get_connections(self):
        """Return list of (src_rc, dst_rc, weight_label, is_inhibitory)."""
        conns = []
        for rc in self.INPUT_CELLS:
            conns.append((rc, self.HIDDEN_CELL, "w=1", False))
        conns.append((self.HIDDEN_CELL, self.OUTPUT_CELL, "signal", False))
        return conns

    def active_cells(self):
        """Return set of (r,c) that are visually 'active' right now."""
        active = set()
        for i, (r, c) in enumerate(self.INPUT_CELLS):
            if self.inputs[i]:
                active.add((r, c))
        node = self.grid.cells[self.HIDDEN_CELL[0]][self.HIDDEN_CELL[1]]
        if node.vars.get("act", 0) >= 1:
            active.add(self.HIDDEN_CELL)
        if self.read_output():
            active.add(self.OUTPUT_CELL)
        return active

    def input_count(self):
        return 3

    def all_combos(self):
        for bits in range(8):
            yield [bool(bits & 4), bool(bits & 2), bool(bits & 1)]

    def expected(self, vals):
        return sum(vals) >= 2

    @property
    def name(self):
        return "Majority-3 Vote"

    @property
    def description(self):
        return "Output = 1 when >= 2 of 3 inputs are ON"

    @property
    def arch_lines(self):
        return [
            ("Layer 1:", "3 input neurons (GATE mask)", "header"),
            ("Layer 2:", "1 hidden neuron (X_LOOP)", "header"),
            ("", "Counts neighbors with mask=1111", "detail"),
            ("", "Fires signal when count >= 2", "detail"),
            ("Layer 3:", "1 output (Z_LOOP -> Y_LOOP)", "header"),
            ("", "Receives 'fire' signal", "detail"),
            ("", "Y_LOOP = 1, Z_LOOP = 0", "detail"),
            ("", "", ""),
            (".geo:", "nb_mask_count  EMIT  SWITCH", "geo"),
        ]


class XORNetwork:
    """2-layer perceptron solving XOR on a 3x3 grid.

    Layout:
          col0    col1   col2
    row2: [IN0]   [H0]   [IN1]
    row1: [pad]   [OUT]  [pad]
    row0: [IN0']  [H1]   [IN1']
    """

    CELL_ROLES = {
        (2, 0): "input",   (2, 1): "h0",     (2, 2): "input",
        (1, 0): "pad",     (1, 1): "output",  (1, 2): "pad",
        (0, 0): "relay",   (0, 1): "h1",     (0, 2): "relay",
    }
    LABELS = {
        (2, 0): "IN0", (2, 2): "IN1",
        (0, 0): "IN0'", (0, 2): "IN1'",
        (2, 1): "H0 (OR)", (0, 1): "H1 (AND)",
        (1, 1): "OUTPUT",
    }
    INPUT_CELLS = [(2, 0), (2, 2)]
    RELAY_CELLS = [(0, 0), (0, 2)]
    HIDDEN_CELLS = [(2, 1), (0, 1)]
    OUTPUT_CELL = (1, 1)

    def __init__(self):
        geo_path = os.path.join(os.path.dirname(__file__),
                                "..", "examples", "neural", "neural_xor.geo")
        self.base_program = load_geo(geo_path)
        self.inputs = [False, False]
        self._build()

    def _build(self):
        roles = self.CELL_ROLES
        base_rules = self.base_program.rules
        base_default = self.base_program.default

        programs = {}
        for (r, c), role in roles.items():
            programs[(r, c)] = Program(base_rules, base_default, name=role)

        def prog_fn(r, c):
            return programs.get((r, c), self.base_program)

        def mask_fn(r, c):
            role = roles.get((r, c), "pad")
            if role in ("input", "relay"):
                idx = 0 if c == 0 else 1
                return 0b1111 if self.inputs[idx] else 0b0000
            if role in ("h0", "h1"):
                return X_LOOP[0]
            if role == "output":
                return Z_LOOP[0]
            return 0b0000

        self.grid = Grid.make_multi(3, 3, prog_fn, init_mask_fn=mask_fn)

    def set_inputs(self, vals):
        self.inputs = list(vals)
        for i, ((ir, ic), (rr, rc)) in enumerate(
                zip(self.INPUT_CELLS, self.RELAY_CELLS)):
            m = 0b1111 if self.inputs[i] else 0b0000
            self.grid.cells[ir][ic].mask = m
            self.grid.cells[rr][rc].mask = m

    def toggle_input(self, idx):
        self.inputs[idx] = not self.inputs[idx]
        m = 0b1111 if self.inputs[idx] else 0b0000
        ir, ic = self.INPUT_CELLS[idx]
        rr, rc = self.RELAY_CELLS[idx]
        self.grid.cells[ir][ic].mask = m
        self.grid.cells[rr][rc].mask = m

    def step(self, tick):
        self.grid.step(tick)

    def read_output(self):
        node = self.grid.cells[self.OUTPUT_CELL[0]][self.OUTPUT_CELL[1]]
        return family_of(node.mask) == "Y_LOOP"

    def cell_info(self, r, c):
        node = self.grid.cells[r][c]
        return {
            "mask": node.mask,
            "family": family_of(node.mask),
            "vars": dict(node.vars),
            "role": self.CELL_ROLES.get((r, c), "?"),
        }

    def get_role(self, r, c):
        return self.CELL_ROLES.get((r, c), "pad")

    def get_label(self, r, c):
        return self.LABELS.get((r, c), "")

    def get_input_idx(self, r, c):
        if (r, c) in self.INPUT_CELLS:
            return self.INPUT_CELLS.index((r, c))
        return -1

    def get_connections(self):
        return [
            ((2, 0), (2, 1), "w=+1", False),
            ((2, 2), (2, 1), "w=+1", False),
            ((0, 0), (0, 1), "w=+1", False),
            ((0, 2), (0, 1), "w=+1", False),
            ((2, 1), (1, 1), "w=+1", False),
            ((0, 1), (1, 1), "w=-1", True),
        ]

    def active_cells(self):
        active = set()
        for i, (r, c) in enumerate(self.INPUT_CELLS):
            if self.inputs[i]:
                active.add((r, c))
        for i, (r, c) in enumerate(self.RELAY_CELLS):
            if self.inputs[i]:
                active.add((r, c))
        for r, c in self.HIDDEN_CELLS:
            node = self.grid.cells[r][c]
            if node.vars.get("a", 0) >= 100:
                active.add((r, c))
        if self.read_output():
            active.add(self.OUTPUT_CELL)
        return active

    def input_count(self):
        return 2

    def all_combos(self):
        for bits in range(4):
            yield [bool(bits & 2), bool(bits & 1)]

    def expected(self, vals):
        return vals[0] ^ vals[1]

    @property
    def name(self):
        return "XOR Perceptron"

    @property
    def description(self):
        return "2-layer perceptron: H0=OR, H1=AND, OUT=XOR"

    @property
    def arch_lines(self):
        return [
            ("Layer 1:", "2 inputs + 2 relays (GATE)", "header"),
            ("Layer 2:", "H0 (OR, threshold=100)", "header"),
            ("", "H1 (AND, threshold=200)", "header"),
            ("", "ACCUM_VAR sum DIR a weight", "detail"),
            ("", "CLAMP_VAR sum 0 200", "detail"),
            ("Layer 3:", "OUT = H0 AND NOT H1", "header"),
            ("", "w=+1 from H0 (excitatory)", "detail"),
            ("", "w=-1 from H1 (inhibitory)", "detail"),
            ("", "", ""),
            (".geo:", "ACCUM_VAR  CLAMP_VAR  tick%4", "geo"),
        ]


# ---------------------------------------------------------------------------
# Console truth-table test
# ---------------------------------------------------------------------------

def run_truth_table_tests():
    print("=" * 60)
    print("  .geo Neural Network Truth Table Tests")
    print("=" * 60)

    print("\n--- Majority-3 Vote (threshold >= 2) ---")
    print("  IN0  IN1  IN2  |  OUT  Expected  Pass")
    print("  " + "-" * 42)
    maj = MajorityNetwork()
    maj_pass = True
    for bits in range(8):
        vals = [bool(bits & 4), bool(bits & 2), bool(bits & 1)]
        expected = sum(vals) >= 2
        maj.set_inputs(vals)
        for t in range(8):
            maj.step(t)
        result = maj.read_output()
        ok = result == expected
        maj_pass = maj_pass and ok
        v = lambda b: " 1 " if b else " 0 "
        print(f"  {v(vals[0])} {v(vals[1])} {v(vals[2])}  |"
              f"  {v(result)}  {v(expected)}   {'OK' if ok else 'FAIL'}")
        maj._build()

    print("\n--- XOR (2-layer perceptron) ---")
    print("  IN0  IN1  |  OUT  Expected  Pass")
    print("  " + "-" * 36)
    xor = XORNetwork()
    xor_pass = True
    for bits in range(4):
        vals = [bool(bits & 2), bool(bits & 1)]
        expected = vals[0] ^ vals[1]
        xor.set_inputs(vals)
        for t in range(16):
            xor.step(t)
        result = xor.read_output()
        ok = result == expected
        xor_pass = xor_pass and ok
        v = lambda b: " 1 " if b else " 0 "
        print(f"  {v(vals[0])} {v(vals[1])}  |"
              f"  {v(result)}  {v(expected)}   {'OK' if ok else 'FAIL'}")
        xor._build()

    print("\n" + "=" * 60)
    all_pass = maj_pass and xor_pass
    print(f"  Majority-3: {'PASS' if maj_pass else 'FAIL'}")
    print(f"  XOR:        {'PASS' if xor_pass else 'FAIL'}")
    print(f"  Overall:    {'ALL PASS' if all_pass else 'SOME FAILED'}")
    print("=" * 60)
    return all_pass


# ---------------------------------------------------------------------------
# Pygame interactive visualizer
# ---------------------------------------------------------------------------

def run_gui():
    try:
        import pygame
    except ImportError:
        print("pygame required for GUI mode. Install: pip install pygame")
        print("Running console test instead.\n")
        return run_truth_table_tests()

    pygame.init()
    W, H = 1200, 750
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Neural .geo Demo - Geometric Grammar as Neural Substrate")
    clock = pygame.time.Clock()

    font_title = pygame.font.Font(None, 40)
    font_big   = pygame.font.Font(None, 32)
    font_med   = pygame.font.Font(None, 26)
    font_sm    = pygame.font.Font(None, 22)
    font_xs    = pygame.font.Font(None, 18)

    # ── Colors ──
    BG        = (14, 14, 28)
    PANEL_BG  = (22, 22, 40)
    WHITE     = (220, 220, 235)
    DIM       = (130, 130, 155)
    GREEN     = (60, 210, 110)
    GREEN_DIM = (30, 90, 50)
    ORANGE    = (255, 170, 50)
    RED       = (240, 70, 70)
    RED_DIM   = (100, 35, 35)
    BLUE      = (80, 140, 255)
    CYAN      = (80, 220, 240)
    DARK      = (35, 35, 55)
    INHIBIT   = (255, 80, 100)
    EXCITE    = (80, 220, 140)

    ROLE_COLOR = {
        "input":  GREEN,
        "relay":  (50, 170, 95),
        "hidden": ORANGE,
        "h0":     ORANGE,
        "h1":     ORANGE,
        "output": (240, 90, 90),
        "pad":    DARK,
    }
    ROLE_COLOR_DIM = {
        "input":  GREEN_DIM,
        "relay":  (25, 75, 45),
        "hidden": (100, 70, 20),
        "h0":     (100, 70, 20),
        "h1":     (100, 70, 20),
        "output": RED_DIM,
        "pad":    (25, 25, 40),
    }

    # ── State ──
    networks = [MajorityNetwork(), XORNetwork()]
    net_idx = 0
    net = networks[net_idx]

    tick = 0
    paused = True  # start paused so user can see initial state
    tick_speed = 3  # ticks per second — slow enough to watch propagation

    auto_cycle = False
    auto_combo_idx = 0
    auto_timer = 0.0
    AUTO_SETTLE_TICKS = 16
    AUTO_DISPLAY_SEC = 1.5

    hover_cell = None  # (r, c) under mouse

    # ── Grid layout ──
    GRID_LEFT = 50
    GRID_TOP  = 100
    CELL_SZ   = 155
    CELL_GAP  = 14

    def cell_rect(r, c):
        """Screen rect for grid cell (r,c). Row 2 is top on screen."""
        x = GRID_LEFT + c * (CELL_SZ + CELL_GAP)
        y = GRID_TOP + (2 - r) * (CELL_SZ + CELL_GAP)
        return pygame.Rect(x, y, CELL_SZ, CELL_SZ)

    def cell_center(r, c):
        rc = cell_rect(r, c)
        return rc.centerx, rc.centery

    # ── Drawing helpers ──

    def draw_rounded_rect(surf, color, rect, radius=10, width=0):
        pygame.draw.rect(surf, color, rect, width, border_radius=radius)

    def draw_arrow(x1, y1, x2, y2, color, thickness=2, head_size=10):
        """Draw a proper arrow from (x1,y1) to (x2,y2)."""
        pygame.draw.line(screen, color, (int(x1), int(y1)), (int(x2), int(y2)), thickness)
        angle = math.atan2(y2 - y1, x2 - x1)
        # Two lines forming the arrowhead at ~25 degrees
        for sign in (1, -1):
            ha = angle + math.pi + sign * 0.4
            hx = x2 + math.cos(ha) * head_size
            hy = y2 + math.sin(ha) * head_size
            pygame.draw.line(screen, color, (int(x2), int(y2)), (int(hx), int(hy)), thickness)

    def edge_point(r, c, target_r, target_c):
        """Point on the edge of cell (r,c) facing toward (target_r, target_c)."""
        cx, cy = cell_center(r, c)
        tx, ty = cell_center(target_r, target_c)
        dx, dy = tx - cx, ty - cy
        dist = math.hypot(dx, dy)
        if dist < 1:
            return cx, cy
        # Find intersection with cell boundary (square)
        half = CELL_SZ // 2 + 4
        if abs(dx) > abs(dy):
            t = half / abs(dx)
        else:
            t = half / abs(dy)
        return cx + dx * t, cy + dy * t

    def draw_connections():
        """Draw weighted connection arrows edge-to-edge with animated pulse."""
        conns = net.get_connections()
        active = net.active_cells()
        t_pulse = time.time() * 3.0  # for animation

        for (sr, sc), (er, ec), label, is_inhib in conns:
            # Source and dest edge points
            sx, sy = edge_point(sr, sc, er, ec)
            ex, ey = edge_point(er, ec, sr, sc)

            # Color: bright if source is active, dim otherwise
            src_active = (sr, sc) in active
            if is_inhib:
                base_color = INHIBIT if src_active else (120, 50, 55)
            else:
                base_color = EXCITE if src_active else (45, 90, 60)

            thickness = 3 if src_active else 2
            draw_arrow(sx, sy, ex, ey, base_color, thickness, head_size=12)

            # Animated pulse dot traveling along the connection when active
            if src_active:
                frac = (t_pulse % 1.0)
                px = sx + (ex - sx) * frac
                py = sy + (ey - sy) * frac
                pulse_color = (255, 255, 255) if not is_inhib else (255, 150, 150)
                pygame.draw.circle(screen, pulse_color, (int(px), int(py)), 4)

            # Weight label at midpoint
            mx = int((sx + ex) / 2)
            my = int((sy + ey) / 2)
            lbl = font_xs.render(label, True, base_color)
            # Offset label perpendicular to the line
            angle = math.atan2(ey - sy, ex - sx)
            ox = -math.sin(angle) * 12
            oy = math.cos(angle) * 12
            screen.blit(lbl, (mx + int(ox) - lbl.get_width() // 2,
                              my + int(oy) - lbl.get_height() // 2))

    def draw_cell(r, c):
        """Draw a single grid cell with all its info."""
        role = net.get_role(r, c)
        if role == "pad":
            return  # skip pads entirely

        info = net.cell_info(r, c)
        label = net.get_label(r, c)
        rect = cell_rect(r, c)
        active = (r, c) in net.active_cells()
        clickable = net.get_input_idx(r, c) >= 0
        is_hovered = hover_cell == (r, c) and clickable

        # ── Glow behind active cells ──
        if active:
            glow_color = ROLE_COLOR.get(role, DIM)
            glow_surf = pygame.Surface((CELL_SZ + 24, CELL_SZ + 24), pygame.SRCALPHA)
            draw_rounded_rect(glow_surf, (*glow_color, 50),
                              glow_surf.get_rect(), radius=16)
            screen.blit(glow_surf, (rect.x - 12, rect.y - 12))

        # ── Cell body ──
        body_color = ROLE_COLOR.get(role, DARK) if active else ROLE_COLOR_DIM.get(role, DARK)
        draw_rounded_rect(screen, body_color, rect, radius=10)

        # ── Border ──
        border_color = WHITE if active else DIM
        if is_hovered:
            border_color = CYAN
        draw_rounded_rect(screen, border_color, rect, radius=10, width=3 if is_hovered else 2)

        # ── Hover hint ──
        if is_hovered:
            hint = font_xs.render("click to toggle", True, CYAN)
            screen.blit(hint, (rect.centerx - hint.get_width() // 2, rect.bottom - 18))

        # ── Label ──
        if label:
            lbl = font_med.render(label, True, WHITE)
            screen.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.y + 8))

        # ── Mask bits display ──
        mask = info["mask"]
        bits_y = rect.y + 32
        bit_str = f"{mask:04b}"
        bit_color = GREEN if mask == 0b1111 else (RED if mask == 0 else BLUE)
        bs = font_sm.render(bit_str, True, bit_color)
        screen.blit(bs, (rect.centerx - bs.get_width() // 2, bits_y))

        # ── Family ──
        fam = info["family"]
        fs = font_xs.render(fam, True, DIM)
        screen.blit(fs, (rect.centerx - fs.get_width() // 2, bits_y + 18))

        # ── Variables ──
        vy = bits_y + 38
        for vname, vval in sorted(info.get("vars", {}).items()):
            if vname == "a":
                vc = GREEN if vval >= 100 else RED
                vs = font_med.render(f"a={vval}", True, vc)
            elif vname == "sum":
                vc = ORANGE
                vs = font_sm.render(f"sum={vval}", True, vc)
            elif vname == "act":
                vc = GREEN if vval >= 1 else DIM
                vs = font_sm.render(f"act={vval}", True, vc)
            else:
                vc = DIM
                vs = font_sm.render(f"{vname}={vval}", True, vc)
            screen.blit(vs, (rect.centerx - vs.get_width() // 2, vy))
            vy += 20

        # ── Big ON/OFF or output state ──
        if role in ("input", "relay"):
            is_on = mask == 0b1111
            state_text = "ON" if is_on else "OFF"
            state_color = GREEN if is_on else RED
            ss = font_big.render(state_text, True, state_color)
            screen.blit(ss, (rect.centerx - ss.get_width() // 2, rect.bottom - 38))
        elif role == "output":
            out_val = family_of(info["mask"]) == "Y_LOOP"
            state_text = "1" if out_val else "0"
            state_color = GREEN if out_val else RED
            ss = font_big.render(state_text, True, state_color)
            screen.blit(ss, (rect.centerx - ss.get_width() // 2, rect.bottom - 38))

    def draw_info_panel():
        """Right-side panel with architecture + truth table."""
        px = GRID_LEFT + 3 * (CELL_SZ + CELL_GAP) + 30
        py = GRID_TOP
        pw = W - px - 20
        ph = H - py - 60

        draw_rounded_rect(screen, PANEL_BG, (px, py, pw, ph), radius=12)
        draw_rounded_rect(screen, DIM, (px, py, pw, ph), radius=12, width=1)

        # Title
        title = font_big.render(net.name, True, WHITE)
        screen.blit(title, (px + 16, py + 12))
        desc = font_sm.render(net.description, True, DIM)
        screen.blit(desc, (px + 16, py + 42))

        # Architecture
        ay = py + 75
        arch_hdr = font_med.render("Architecture", True, ORANGE)
        screen.blit(arch_hdr, (px + 16, ay))
        pygame.draw.line(screen, ORANGE, (px + 16, ay + 22), (px + pw - 16, ay + 22), 1)
        ay += 30

        for left, right, style in net.arch_lines:
            if style == "header":
                color = WHITE
                font_used = font_sm
            elif style == "detail":
                color = BLUE
                font_used = font_xs
                right = "  " + right
            elif style == "geo":
                color = CYAN
                font_used = font_sm
            else:
                ay += 6
                continue
            if left:
                ls = font_used.render(left, True, ORANGE)
                screen.blit(ls, (px + 16, ay))
                rs = font_used.render(right, True, color)
                screen.blit(rs, (px + 16 + ls.get_width() + 6, ay))
            else:
                rs = font_used.render(right, True, color)
                screen.blit(rs, (px + 28, ay))
            ay += 18

        # Truth table
        ay += 16
        tt_hdr = font_med.render("Truth Table", True, GREEN)
        screen.blit(tt_hdr, (px + 16, ay))
        pygame.draw.line(screen, GREEN, (px + 16, ay + 22), (px + pw - 16, ay + 22), 1)
        ay += 30

        combos = list(net.all_combos())
        n_inputs = net.input_count()

        # Header row
        hdrs = [f"IN{i}" for i in range(n_inputs)] + ["|", "OUT"]
        hdr_text = "  ".join(hdrs)
        screen.blit(font_sm.render(hdr_text, True, WHITE), (px + 20, ay))
        ay += 20

        for vals in combos:
            exp = net.expected(vals)
            current = (vals == net.inputs)

            parts = [str(int(v)) for v in vals]
            row_text = "   ".join(parts) + "    |    " + str(int(exp))

            if current:
                # Highlight bar
                highlight = pygame.Surface((pw - 32, 18), pygame.SRCALPHA)
                highlight.fill((80, 220, 140, 40))
                screen.blit(highlight, (px + 14, ay - 1))
                pygame.draw.rect(screen, GREEN, (px + 12, ay, 3, 16))
                color = GREEN
            else:
                color = DIM

            screen.blit(font_sm.render(row_text, True, color), (px + 20, ay))
            ay += 20

    def draw_output_banner():
        """Big output result at the bottom."""
        out_val = net.read_output()
        inputs_str = ", ".join(str(int(v)) for v in net.inputs)

        banner_y = H - 55
        if out_val:
            msg = f"OUTPUT = 1 (inputs: {inputs_str})"
            color = GREEN
        else:
            msg = f"OUTPUT = 0 (inputs: {inputs_str})"
            color = RED

        # Background glow
        glow_surf = pygame.Surface((W - 40, 50), pygame.SRCALPHA)
        draw_rounded_rect(glow_surf, (*color, 40), glow_surf.get_rect(), radius=12)
        screen.blit(glow_surf, (20, banner_y))

        text = font_big.render(msg, True, color)
        screen.blit(text, (W // 2 - text.get_width() // 2, banner_y + 12))

    def get_cell_at_mouse(mx, my):
        """Return (r, c) for mouse position, or None."""
        for r in range(3):
            for c in range(3):
                if cell_rect(r, c).collidepoint(mx, my):
                    return (r, c)
        return None

    # ── Main loop ──
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # Auto-cycle timer
        if auto_cycle:
            auto_timer += dt
            if auto_timer >= AUTO_DISPLAY_SEC:
                auto_timer = 0.0
                # Advance to next input combo
                combo_list = list(net.all_combos())
                auto_combo_idx = (auto_combo_idx + 1) % len(combo_list)
                net.set_inputs(combo_list[auto_combo_idx])
                # Reset grid to let it settle
                net._build()
                tick = 0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_TAB:
                    net_idx = (net_idx + 1) % len(networks)
                    net = networks[net_idx]
                    tick = 0
                    auto_combo_idx = 0

                elif event.key == pygame.K_SPACE:
                    paused = not paused

                elif event.key == pygame.K_RIGHT:
                    if paused:
                        net.step(tick)
                        tick += 1

                elif event.key == pygame.K_r:
                    net._build()
                    tick = 0

                elif event.key == pygame.K_t:
                    run_truth_table_tests()

                elif event.key == pygame.K_a:
                    auto_cycle = not auto_cycle
                    auto_combo_idx = 0

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mx, my = event.pos
                    cell = get_cell_at_mouse(mx, my)
                    if cell:
                        r, c = cell
                        idx = net.get_input_idx(r, c)
                        if idx >= 0:
                            net.toggle_input(idx)
                            # Rebuild to propagate
                            net._build()
                            tick = 0

        # Update hover state
        mx, my = pygame.mouse.get_pos()
        hover_cell = get_cell_at_mouse(mx, my)

        # Auto-step when not paused
        if not paused and not auto_cycle:
            step_interval = 1.0 / tick_speed
            if time.time() % step_interval < dt:
                net.step(tick)
                tick += 1

        # Draw everything
        screen.fill(BG)

        # Title
        title = font_title.render("Neural .geo Demo", True, WHITE)
        screen.blit(title, (W // 2 - title.get_width() // 2, 20))

        # Controls hint
        controls = "Click=toggle | TAB=switch | SPACE=pause | R=reset | T=test | A=auto-cycle"
        ctrl_text = font_xs.render(controls, True, DIM)
        screen.blit(ctrl_text, (W // 2 - ctrl_text.get_width() // 2, 55))

        # Grid cells
        for r in range(3):
            for c in range(3):
                draw_cell(r, c)

        # Connections
        draw_connections()

        # Info panel
        draw_info_panel()

        # Output banner
        draw_output_banner()

        pygame.display.flip()

    pygame.quit()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_truth_table_tests()
    else:
        run_gui()
