# Binary Quadrant Reference

## 4-Bit Opcode System

Each 4-bit binary number represents which quadrants are **active** in a quadtree node.

> **This page reads masks in Z order** (TL, TR, BL, BR), the same as the Go port.
> The Python runtime (`BinaryQuadTreeTest.py`) draws in **C order** (TL, TR, BR, BL: a backwards C,
> the clockwise ring), so there `0001` is BL, `1001` is the left column and `1010` is a diagonal.
> Both orders are on purpose; they serve different shapes. See `GEO_LANGUAGE.md` for the C-order shapes.

### Quadrant Mapping

| Binary | Decimal | Quadrant     | Visual | Mnemonic   |
|--------|---------|--------------|--------|------------|
| 0000   | 0       | None         | □      | Stay Off   |
| 1000   | 8       | Top-Left     | ◨      | TL         |
| 0100   | 4       | Top-Right    | ◩      | TR         |
| 0010   | 2       | Bottom-Left  | ◪      | BL         |
| 0001   | 1       | Bottom-Right | ◫      | BR         |

### Multi-Quadrant Patterns

| Binary | Decimal | Pattern        | Visual | Name     |
|--------|---------|----------------|--------|----------|
| 1100   | 12      | Top            | ▀      | Up       |
| 0011   | 3       | Bottom         | ▄      | Down     |
| 1010   | 10      | Left           | ▌      | Left     |
| 0101   | 5       | Right          | ▐      | Right    |
| 1001   | 9       | Diagonal ↘     | ⌌      | Diag-A   |
| 0110   | 6       | Diagonal ↙     | ⌋      | Diag-B   |
| 1111   | 15      | All            | █      | On/Full  |
| 1110   | 14      | All except BR  |        | Loop-Z   |
| 1101   | 13      | All except BL  |        |          |
| 1011   | 11      | All except TR  |        |          |
| 0111   | 7       | All except TL  |        |          |

## Loop Families

### Y-Loop (Single quadrant rotates)
- Sequence: `1000 → 0100 → 0010 → 0001` (TL → TR → BL → BR)
- Effect: Single active quadrant cycles through all four positions

### X-Loop (Pair cycles)
- Sequence: `1100 → 0101 → 0011 → 1010`
- Effect: Adjacent pair of active quadrants cycles

### Z-Loop (Three-quadrant sweep)
- Sequence: `0111 → 1011 → 1101 → 1110`
- Effect: Three active quadrants sweep (missing quadrant rotates)

### Gate
- Binary: `1111` (all on) or `0000` (all off)
- Effect: Toggles node visibility
- Notebook ref: "Passer/On"

### Diag (Diagonal Spread)
- Binary: `1001` or `0110`
- Effect: Activates diagonal pairs
- Notebook ref: "Diag"

## Visual Key
