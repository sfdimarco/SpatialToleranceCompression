// Package quadtree implements the hierarchical spatial data structure
// used by the GEO compression format.
//
// Unlike the Python GEO engine (which stores explicit x,y coordinates),
// nodes here are addressed by their Morton code — a Z-order curve index
// that implicitly encodes position. This makes serialization to a
// progressive bitstream natural: reading more bytes = more detail.
package quadtree

import "github.com/sfdimarco/geo/pkg/morton"

// Color represents a pixel in YCbCr color space with alpha.
//
// YCbCr is used instead of RGB because:
//   - Luminance (Y) separates from chrominance (Cb, Cr)
//   - Human eyes are more sensitive to brightness than color
//   - We can compress chroma channels more aggressively (like JPEG does)
//   - Delta encoding on Y channel is more efficient
type Color struct {
	Y  uint8 // Luminance (brightness) — most perceptually important
	Cb uint8 // Blue-difference chroma
	Cr uint8 // Red-difference chroma
	A  uint8 // Alpha (transparency)
}

// RGBToYCbCr converts an RGB pixel to YCbCr color space.
// Uses the JFIF/JPEG conversion formula.
func RGBToYCbCr(r, g, b uint8) Color {
	rf, gf, bf := float64(r), float64(g), float64(b)
	y := 0.299*rf + 0.587*gf + 0.114*bf
	cb := 128.0 - 0.168736*rf - 0.331264*gf + 0.5*bf
	cr := 128.0 + 0.5*rf - 0.418688*gf - 0.081312*bf
	return Color{
		Y:  clampU8(y),
		Cb: clampU8(cb),
		Cr: clampU8(cr),
		A:  255,
	}
}

// YCbCrToRGB converts back to RGB for display.
func YCbCrToRGB(c Color) (r, g, b uint8) {
	yf := float64(c.Y)
	cbf := float64(c.Cb) - 128.0
	crf := float64(c.Cr) - 128.0
	r = clampU8(yf + 1.402*crf)
	g = clampU8(yf - 0.344136*cbf - 0.714136*crf)
	b = clampU8(yf + 1.772*cbf)
	return
}

func clampU8(v float64) uint8 {
	if v < 0 {
		return 0
	}
	if v > 255 {
		return 255
	}
	return uint8(v + 0.5) // round
}

// ColorDelta stores the difference between a child's color and its parent's
// average. Small deltas = fewer bits needed = better compression.
type ColorDelta struct {
	DY  int8 // Luminance delta (most important)
	DCb int8 // Chroma-blue delta
	DCr int8 // Chroma-red delta
	DA  int8 // Alpha delta
}

// QuadNode is a single node in the compression quadtree.
//
// Each node represents a square region of the image. The region's position
// is implicitly encoded by the Morton code — no (x,y) fields needed.
//
// Leaf nodes (Mask == 0): represent a uniform-color region.
// Internal nodes (Mask != 0): have children that subdivide the region.
type QuadNode struct {
	Code  uint64
	Depth uint8
	Mask  uint8
	Color Color
	Delta ColorDelta
	Children [4]*QuadNode
}

// IsLeaf returns true if this node has no children (uniform color region).
func (n *QuadNode) IsLeaf() bool {
	return n.Mask == 0
}

// HasChild checks if a specific Morton child index (0-3) has a child node.
func (n *QuadNode) HasChild(childIdx uint8) bool {
	maskBit := morton.QuadrantMaskBit(childIdx)
	return n.Mask&maskBit != 0
}

// NodeCount recursively counts all nodes in this subtree.
func (n *QuadNode) NodeCount() int {
	if n == nil {
		return 0
	}
	count := 1
	for _, child := range n.Children {
		count += child.NodeCount()
	}
	return count
}

// LeafCount recursively counts all leaf nodes in this subtree.
func (n *QuadNode) LeafCount() int {
	if n == nil {
		return 0
	}
	if n.IsLeaf() {
		return 1
	}
	count := 0
	for _, child := range n.Children {
		count += child.LeafCount()
	}
	return count
}

// MaxTreeDepth returns the deepest level in this subtree.
func (n *QuadNode) MaxTreeDepth() uint8 {
	if n == nil || n.IsLeaf() {
		return n.Depth
	}
	maxD := n.Depth
	for _, child := range n.Children {
		if child != nil {
			d := child.MaxTreeDepth()
			if d > maxD {
				maxD = d
			}
		}
	}
	return maxD
}

// MaxDepthForResolution returns the quadtree depth needed for a given
// image dimension. The image must be square and a power of 2.
func MaxDepthForResolution(width uint32) uint8 {
	depth := uint8(0)
	w := width
	for w > 1 {
		w >>= 1
		depth++
	}
	return depth
}
