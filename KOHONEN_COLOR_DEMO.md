# 🌈 Kohonen Self-Organizing Map - Color Space Visualization

## Overview

A **stunning visual demonstration** of self-organization where a 10×10 grid of neurons learns to organize the RGB color space into a smooth, coherent color map.

Watch as **random noise transforms into order** through the magic of competitive learning!

---

## 🎮 Quick Start

```bash
# Run the visual demo
python kohonen_color_demo.py

# Run console test
python kohonen_color_demo.py --test
```

---

## 🎨 What You'll See

### Initial State (Random)
```
┌────────────────────────────────────────┐
│ █▓░▒ █▒▓░ ▒█▓░ ░▒█▓  ← Random colors  │
│ ▓█▒░ ░▓█▒ ▓░█▒ █▓░▒                    │
│ ▒▓░█ █░▒▓ ░█▒▓ ▓█▒░                    │
│ ░▒▓█ ▓░▒█ █▓░▒ ▒█▓░                    │
└────────────────────────────────────────┘
```

### After Training (Organized)
```
┌────────────────────────────────────────┐
│ 🔴 🟠 🟡 🟢  ← Smooth color gradient   │
│ 🟣 🔵 🟤 ⚫                            │
│ ⚪ 🩶 🌸 🍑                            │
│ 🎨 Color space organized!              │
└────────────────────────────────────────┘
```

---

## 🧠 How It Works

### Architecture

```
10×10 Grid of SOM Neurons
    │
    ├─ Each neuron has 3D weight vector (R, G, B)
    │
    ├─ Weight range: 0-255 for each channel
    │
    └─ Total: 100 neurons × 3 weights = 300 parameters
```

### Learning Algorithm

**Step 1: Present Input**
```python
input_color = (R, G, B)  # e.g., (255, 128, 0)
```

**Step 2: Find Winner**
```python
# Compute Euclidean distance in RGB space
distance = √Σ(weight_i - input_i)²

# Best Matching Unit = minimum distance
winner = argmin(distance)
```

**Step 3: Update Neighborhood**
```python
# Gaussian neighborhood function
influence = exp(-distance² / (2 * radius²))

# Update weights toward input
w_new = w_old + lr * (input - w_old)

# Winner learns most, neighbors learn less
```

**Step 4: Decay Parameters**
```python
learning_rate *= 0.9995
neighborhood_radius *= 0.999
```

---

## 🎮 Interactive Controls

| Key/Button | Action |
|------------|--------|
| **SPACE** | Toggle auto-training (random colors) |
| **T** | Manual training step with current color |
| **R** | Reset weights (randomize) |
| **S** | Save color map as PNG image |
| **Click Neuron** | Sample that neuron's color |
| **Drag Sliders** | Adjust RGB input color |
| **Click TRAIN** | Train on selected color |
| **Esc** | Quit |

---

## 📊 Visualization Guide

### SOM Grid (Left)

Each square represents one neuron:
- **Color** = neuron's weight vector (R, G, B)
- **White glow** = activation level (winner influence)
- **White border** = current winner neuron

### Color Picker (Right)

- **RGB Sliders** = Input color to train
- **Preview Box** = Current selected color
- **TRAIN Button** = Manual training step

### Info Panel (Bottom)

- **Epoch** = Total training steps
- **Winner** = Best matching neuron position
- **Distance** = How close winner is to input
- **Avg Distance** = Overall map accuracy
- **Learning Rate** = Current learning speed
- **Neighborhood** = Influence radius

---

## 🔬 The Science Behind It

### Competitive Learning

Neurons **compete** to respond to input colors:
- Only the "winner" (best match) fires strongly
- Neighbors fire proportionally to their distance from winner
- Losers don't fire at all

### Neighborhood Cooperation

The winner's neighbors **cooperate** by learning together:
- Closer neighbors learn more
- Distant neighbors learn less
- Creates smooth topological organization

### Self-Organization

Through repeated exposure:
1. **Early phase**: Large neighborhood, fast learning
2. **Middle phase**: Medium neighborhood, moderate learning
3. **Late phase**: Small neighborhood, fine-tuning

Result: **Emergent structure from chaos!**

---

## 🎯 What Makes This Special

### 1. **Visual Learning**

Watch self-organization happen in **real-time**:
- Start: Random color noise
- Middle: Patches of similar colors
- End: Smooth color gradients

### 2. **Interactive**

You're not just watching - you're **teaching**:
- Choose which colors to present
- Speed up or slow down learning
- Reset and try different initial conditions

### 3. **Emergent Behavior**

No one programs the final pattern:
- The map **decides** how to organize
- Each run produces a **unique** arrangement
- Structure **emerges** from simple rules

### 4. **Mathematical Beauty**

Underlying equations create visual art:
- Euclidean distance → Color similarity
- Gaussian function → Neighborhood influence
- Exponential decay → Learning schedule

---

## 📈 Expected Results

### Training Progress

| Epochs | Learning Rate | Neighborhood | Visual Result |
|--------|---------------|--------------|---------------|
| 0 | 0.30 | 3.0 | Random noise |
| 100 | 0.28 | 2.7 | Color patches appear |
| 500 | 0.23 | 2.0 | Smooth regions form |
| 1000 | 0.18 | 1.5 | Clear gradients |
| 5000 | 0.08 | 1.1 | Refined organization |
| 10000 | 0.02 | 1.0 | Final color map |

### Typical Final State

After ~10,000 training steps:
- **Reds** cluster in one region
- **Greens** cluster in another
- **Blues** cluster in another
- **Intermediate colors** form smooth transitions
- **Quantization error**: ~30-50 (out of 442 max)

---

## 🎨 Creative Experiments

### Experiment 1: Limited Palette

Train only on specific colors:
```python
# Only primary colors
colors = [(255,0,0), (0,255,0), (0,0,255)]

# Result: Map divides into 3 color regions
```

### Experiment 2: Gradient Training

Train on systematic color gradient:
```python
# Sweep through hue spectrum
for hue in range(360):
    color = hsv_to_rgb(hue, 1.0, 1.0)
    train(color)

# Result: Rainbow organization
```

### Experiment 3: Natural Images

Sample colors from a photo:
```python
# Extract colors from image
for pixel in image:
    train(pixel.color)

# Result: Map learns image's color palette
```

---

## 🔧 Parameters Explained

### Learning Rate (η)

Controls how much weights change per step:
- **High (0.3+)**: Fast learning, unstable
- **Medium (0.1)**: Balanced learning
- **Low (0.01)**: Slow refinement

Default: Starts at 0.3, decays to 0.02

### Neighborhood Radius (σ)

Controls how many neighbors learn:
- **Large (3.0+)**: Global organization
- **Medium (1.5)**: Local refinement
- **Small (1.0)**: Fine-tuning only

Default: Starts at 3.0, decays to 1.0

### Decay Rate

How fast parameters decrease:
- **Fast (0.99)**: Quick convergence
- **Medium (0.999)**: Balanced
- **Slow (0.9999)**: Extended exploration

Default: 0.9995 per step

---

## 💡 Tips & Tricks

### For Fast Organization

1. Start with high learning rate (0.3)
2. Use large neighborhood (3.0)
3. Train on diverse colors
4. Let it run for 1000+ epochs

### For Fine Detail

1. Train for 5000+ epochs
2. Let learning rate decay naturally
3. Present specific colors of interest
4. Use manual training mode

### For Artistic Effects

1. Train on limited color palettes
2. Stop training at intermediate stages
3. Save multiple snapshots
4. Try different random seeds

---

## 📸 Saving Your Creation

Press **S** to save the current color map:
- Saved as: `kohonen_color_map.png`
- Resolution: 500×500 pixels (10×10 neurons × 50px)
- Format: PNG (lossless)

Perfect for:
- Art projects
- Presentations
- Social media
- Research documentation

---

## 🐛 Troubleshooting

### Problem: Map stays random

**Solutions:**
- Increase learning rate
- Increase neighborhood radius
- Train for more epochs
- Check auto-training is ON

### Problem: Map converges too slowly

**Solutions:**
- Increase learning rate decay
- Present more diverse colors
- Increase training speed (more steps per frame)

### Problem: Colors don't organize smoothly

**Solutions:**
- Start with larger neighborhood
- Slow down neighborhood decay
- Train for more epochs

---

## 🎓 Educational Applications

### For Students

- **Visualize** abstract neural network concepts
- **Experiment** with learning parameters
- **Understand** self-organization principles

### For Teachers

- **Demonstrate** unsupervised learning
- **Illustrate** emergent behavior
- **Engage** students with interactive visuals

### For Researchers

- **Prototype** SOM variations
- **Test** learning algorithms
- **Visualize** high-dimensional data

---

## 🔮 Extensions & Ideas

### Idea 1: 3D Visualization

```python
# Map neurons to 3D space
# X, Y = position
# Z = activation
# Color = weight

# Result: 3D color landscape
```

### Idea 2: Multiple Features

```python
# Extend beyond RGB
# Add: brightness, saturation, hue
# 6D weight vectors

# Result: More nuanced organization
```

### Idea 3: Hierarchical SOM

```python
# Multiple SOM layers
# Layer 1: Coarse organization
# Layer 2: Fine details

# Result: Multi-scale color map
```

---

## 📚 Mathematical Details

### Distance Metric

Euclidean distance in RGB space:

```
d(w, x) = √[(w_R - x_R)² + (w_G - x_G)² + (w_B - x_B)²]
```

### Neighborhood Function

Gaussian influence:

```
h(i) = exp(-d_i² / (2σ²))
```

Where:
- `d_i` = distance from winner
- `σ` = neighborhood radius

### Weight Update

Kohonen learning rule:

```
w(t+1) = w(t) + η(t) * h(i) * (x - w(t))
```

Where:
- `η(t)` = learning rate at time t
- `h(i)` = neighborhood influence
- `x` = input vector

---

## 🌟 Connection to Brain

This algorithm is inspired by biological neural networks:

| SOM Feature | Brain Analog |
|-------------|--------------|
| Competitive learning | Lateral inhibition |
| Neighborhood | Cortical columns |
| Topological map | Visual cortex organization |
| Self-organization | Developmental plasticity |

The brain's visual cortex organizes similarly!

---

## 📖 References

### Foundational Papers

- **Kohonen (1982)** - "Self-Organized Formation of Topologically Correct Feature Maps"
- **Kohonen (1990)** - "The Self-Organizing Map"
- **Kohonen (2001)** - "Self-Organizing Maps" (book)

### Applications

- **Color quantization** - Reduce image color palette
- **Data visualization** - Project high-D data to 2D
- **Pattern recognition** - Feature extraction
- **Image compression** - Vector quantization

---

## 🎉 Have Fun!

This demo is designed to be:
- **Beautiful** - Watch colors dance and organize
- **Educational** - Learn about neural networks
- **Interactive** - Play and experiment
- **Inspiring** - See emergence in action

**Enjoy the show!** 🌈✨

---

## 📄 License

MIT License - See [LICENSE](../LICENSE) file

---

**Created for the Binary Quad-Tree Geometric Grammar Engine**

*"Where mathematics meets art through self-organization"*
