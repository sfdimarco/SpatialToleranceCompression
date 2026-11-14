# 🧠 Neural Network System - Complete Index

## Quick Start

```bash
# Run interactive visualizer
python neural_demo.py

# Run console tests
python neural_demo.py --test
```

---

## Documentation Hub

### 📚 Core Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[NEURAL_DEMO_ANALYSIS.md](NEURAL_DEMO_ANALYSIS.md)** | Complete analysis of neural_demo.py, improvements, and architecture | All users |
| **[NEURAL_NETWORK_ROADMAP.md](NEURAL_NETWORK_ROADMAP.md)** | Development plan, timeline, and future features | Contributors |
| **[examples/NEURAL_NETWORKS_FULL.md](examples/NEURAL_NETWORKS_FULL.md)** | Detailed reference for all 8 neural networks | Network designers |
| **[examples/NEURAL_QUICK_REF.md](examples/NEURAL_QUICK_REF.md)** | Quick reference card for `.geo` neural primitives | Daily use |

### 🔧 Technical References

| Document | Purpose |
|----------|---------|
| [GEO_LANGUAGE.md](GEO_LANGUAGE.md) | Full `.geo` language specification |
| [README.md](README.md) | Project overview and quick start |
| [GEOSTUDIO.md](GEOSTUDIO.md) | GeoStudio tool documentation |
| [PLAYGROUND.md](PLAYGROUND.md) | Interactive playground guide |

---

## Network Library

### ✅ Working Networks

| Network | File | Complexity | Description |
|---------|------|------------|-------------|
| **Majority-3** | `examples/neural_majority3.geo` | ⭐ Beginner | 3-input threshold logic unit |
| **XOR** | `examples/neural_xor.geo` | ⭐⭐ Intermediate | 2-layer perceptron solving XOR |

### 🆕 New Networks (Created)

| Network | File | Complexity | Description |
|---------|------|------------|-------------|
| **Sigmoid** | `examples/neural_sigmoid.geo` | ⭐⭐ Intermediate | Piecewise linear sigmoid activation |
| **Perceptron** | `examples/neural_perceptron.geo` | ⭐⭐ Intermediate | 4-input single-layer perceptron |
| **Hopfield** | `examples/neural_hopfield.geo` | ⭐⭐⭐ Advanced | Associative memory network |
| **Kohonen SOM** | `examples/neural_kohonen.geo` | ⭐⭐⭐ Advanced | Self-organizing map |
| **CNN Edge** | `examples/neural_cnn_edge.geo` | ⭐⭐⭐ Advanced | Convolutional edge detector |
| **LSTM Cell** | `examples/neural_lstm_cell.geo` | ⭐⭐⭐⭐ Expert | Gated recurrent unit |

---

## Code Structure

### Current (v1.0)

```
BinaryQuadTreeCPUTest/
├── neural_demo.py              # Main visualizer (928 lines)
├── examples/
│   ├── neural_majority3.geo    # Majority network
│   ├── neural_xor.geo          # XOR network
│   ├── neural_sigmoid.geo      # Sigmoid activation ⭐ NEW
│   ├── neural_perceptron.geo   # Multi-input perceptron ⭐ NEW
│   ├── neural_hopfield.geo     # Hopfield memory ⭐ NEW
│   ├── neural_kohonen.geo      # Kohonen SOM ⭐ NEW
│   ├── neural_cnn_edge.geo     # CNN edge detector ⭐ NEW
│   ├── neural_lstm_cell.geo    # LSTM cell ⭐ NEW
│   ├── NEURAL_NETWORKS_FULL.md # Complete docs ⭐ NEW
│   └── NEURAL_QUICK_REF.md     # Quick reference ⭐ NEW
├── NEURAL_DEMO_ANALYSIS.md     # Analysis guide ⭐ NEW
├── NEURAL_NETWORK_ROADMAP.md   # Development roadmap ⭐ NEW
└── NEURAL_INDEX.md             # This file ⭐ NEW
```

### Proposed (v2.0)

```
BinaryQuadTreeCPUTest/
├── neural/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── networks/               # Network implementations
│   │   ├── __init__.py
│   │   ├── base.py             # BaseNetwork abstract class
│   │   ├── majority.py
│   │   ├── xor.py
│   │   ├── sigmoid.py
│   │   ├── perceptron.py
│   │   ├── hopfield.py
│   │   ├── kohonen.py
│   │   ├── cnn.py
│   │   └── lstm.py
│   ├── gui/                    # Visualization
│   │   ├── __init__.py
│   │   ├── renderer.py
│   │   ├── controls.py
│   │   ├── colors.py
│   │   └── widgets.py
│   └── tests/                  # Unit tests
│       ├── __init__.py
│       └── test_networks.py
├── examples/
│   └── neural_*.geo            # .geo scripts
└── docs/
    └── neural_*.md             # Documentation
```

---

## Learning Path

### For Beginners

1. **Start Here:** [NEURAL_DEMO_ANALYSIS.md](NEURAL_DEMO_ANALYSIS.md) - Understand the concept
2. **Run Demo:** `python neural_demo.py` - Play with Majority and XOR
3. **Read Basics:** [examples/NEURAL_QUICK_REF.md](examples/NEURAL_QUICK_REF.md) - Learn `.geo` primitives
4. **Study Examples:** Examine `neural_majority3.geo` and `neural_xor.geo`
5. **Create First Network:** Follow template in Quick Reference

### For Intermediate Users

1. **Deep Dive:** [examples/NEURAL_NETWORKS_FULL.md](examples/NEURAL_NETWORKS_FULL.md) - All 8 networks explained
2. **Experiment:** Test new networks (sigmoid, perceptron, hopfield)
3. **Modify:** Edit existing `.geo` scripts, change parameters
4. **Design:** Create custom network architectures
5. **Share:** Contribute to repository

### For Advanced Users

1. **Roadmap:** [NEURAL_NETWORK_ROADMAP.md](NEURAL_NETWORK_ROADMAP.md) - See future direction
2. **Contribute:** Implement new features, fix issues
3. **Extend:** Add engine operations (MATRIX_MUL, CONV2D)
4. **Integrate:** Connect to ML frameworks
5. **Lead:** Mentor newcomers, write tutorials

---

## Neural Primitives Cheat Sheet

| Concept | `.geo` Implementation |
|---------|----------------------|
| **Neuron** | `own_prog=neuron` cell identity |
| **Activation** | `SET_VAR a 100` |
| **Weight** | `ACCUM_VAR sum DIR var weight` |
| **Bias** | `SET_VAR sum (var_sum + bias)` |
| **Threshold** | `IF var_sum>=N THEN action` |
| **Layer** | `tick%N` phase separation |
| **Feedforward** | Sequential phase execution |
| **Recurrent** | Neighbor feedback loops |
| **Learning** | `SET_VAR w (w + delta)` |

---

## Common Tasks

### Adding a New Network

**Step 1:** Create `.geo` script
```geo
# examples/neural_mynetwork.geo
NAME neural_mynetwork
RULE IF ... THEN ...
DEFAULT HOLD
```

**Step 2:** Add Python wrapper
```python
class MyNetwork:
    def __init__(self):
        self.program = load_geo("examples/neural_mynetwork.geo")
        self._build()
    
    def step(self, tick):
        self.grid.step(tick)
    
    def read_output(self):
        # Return network output
        pass
```

**Step 3:** Register in visualizer
```python
networks = [MajorityNetwork(), XORNetwork(), MyNetwork()]
```

### Testing a Network

**Console Test:**
```python
network = MyNetwork()
network.set_inputs([True, False, True])
for t in range(16):
    network.step(t)
output = network.read_output()
print(f"Output: {output}")
```

**Visual Test:**
```bash
python neural_demo.py
# TAB to switch to your network
# Click inputs to toggle
# SPACE to run simulation
```

### Debugging

**Check Variables:**
```python
node = network.grid.cells[r][c]
print(f"Mask: {node.mask:04b}")
print(f"Family: {family_of(node.mask)}")
print(f"Variables: {dict(node.vars)}")
```

**Step-by-Step:**
```bash
# In GUI: SPACE to pause, → to single-step
# Watch variables change in real-time
```

---

## Troubleshooting

### Network Not Firing?

✅ **Checklist:**
- [ ] `ACCUM_VAR` directions match grid layout
- [ ] Thresholds are reachable with given inputs
- [ ] `tick%N` phases properly sequenced
- [ ] Initial masks set correctly

### Weights Not Updating?

✅ **Checklist:**
- [ ] `SET_VAR` syntax correct (no spaces in var names)
- [ ] `CLAMP_VAR` bounds allow changes
- [ ] Learning rate large enough
- [ ] Error signal computed correctly

### Visualization Issues?

✅ **Checklist:**
- [ ] `active_cells()` matches activation logic
- [ ] `get_connections()` returns correct pairs
- [ ] Cell roles properly labeled
- [ ] Grid layout matches network architecture

---

## Video Tutorials (Planned)

1. **Introduction to Neural `.geo`** (10 min)
   - What is the Binary Quad-Tree system?
   - How neural networks map to `.geo`
   - Running the demo

2. **Building Your First Network** (15 min)
   - Create a threshold neuron
   - Test with truth table
   - Visualize in GUI

3. **Multi-Layer Networks** (20 min)
   - XOR perceptron deep dive
   - Understanding `ACCUM_VAR` and `CLAMP_VAR`
   - Phased execution with `tick%N`

4. **Advanced Architectures** (30 min)
   - Hopfield network implementation
   - LSTM cell walkthrough
   - CNN edge detection

5. **Training Neural Networks** (25 min)
   - Supervised learning with delta rule
   - Hebbian learning
   - Competitive learning (SOM)

---

## Community Resources

### Share Your Work

- **GitHub Issues:** Report bugs, request features
- **Discussions:** Share ideas, ask questions
- **Pull Requests:** Contribute networks, fixes
- **Discord/Slack:** Real-time chat (if available)

### Example Gallery

Submit your `.geo` neural networks for inclusion:
- Novel architectures
- Practical applications
- Educational examples
- Artistic visualizations

### Challenges

Monthly neural network design challenges:
- **March 2026:** Best pattern classifier
- **April 2026:** Smallest XOR implementation
- **May 2026:** Most creative recurrent network
- **June 2026:** Best trained network

---

## Citation

If you use this system in research:

```bibtex
@software{BinaryQuadTreeCPUTest,
  author = {DiMarco, Salvatore},
  title = {Binary Quad-Tree Geometric Grammar Engine},
  year = {2026},
  url = {https://github.com/sfdimarco/BinaryQuadTreeCPUTest}
}
```

---

## Acknowledgments

- **Salvatore DiMarco** - Original BinaryQuadTreeCPUTest creator
- **Contributors** - Network implementations and documentation
- **Community** - Testing, feedback, and examples

---

## License

MIT License - See [LICENSE](LICENSE) file

---

## Quick Links

### Documentation
- 📖 [Analysis Guide](NEURAL_DEMO_ANALYSIS.md)
- 📚 [Full Network Reference](examples/NEURAL_NETWORKS_FULL.md)
- 📋 [Quick Reference Card](examples/NEURAL_QUICK_REF.md)
- 🗺️ [Development Roadmap](NEURAL_NETWORK_ROADMAP.md)

### Code
- 💻 [neural_demo.py](neural_demo.py) - Main visualizer
- 📁 [examples/neural_*.geo](examples/) - Network scripts
- 🔧 [src/binary_quad_tree.py](src/binary_quad_tree.py) - Core engine

### External
- 🌐 [GitHub Repository](https://github.com/sfdimarco/BinaryQuadTreeCPUTest)
- 📖 [GEO_LANGUAGE.md](GEO_LANGUAGE.md) - Full language spec
- 🎮 [Playground](Playground.py) - Interactive sandbox

---

**Last Updated:** March 8, 2026  
**Version:** 1.0  
**Status:** ✅ Foundation Complete, 🚧 Integration In Progress

---

**"Where 4-bit spatial masks meet neural computation"** 🧠✨
