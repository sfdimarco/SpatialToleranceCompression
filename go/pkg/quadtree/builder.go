package quadtree

import (
	"image"
	"image/color"
	_ "image/jpeg"
	_ "image/png"
	"math"
	"os"

	"github.com/sfdimarco/geo/pkg/morton"
)

// BuildConfig controls how aggressively the quadtree prunes.
type BuildConfig struct {
	Quality  uint8 // 0=max compression, 255=lossless
	MaxDepth uint8 // 0=auto from image size
}

func DefaultConfig() BuildConfig {
	return BuildConfig{Quality: 10, MaxDepth: 0}
}

// BuildFromImage loads an image file and constructs the quadtree.
func BuildFromImage(path string, cfg BuildConfig) (*QuadNode, uint32, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, 0, err
	}
	defer f.Close()
	img, _, err := image.Decode(f)
	if err != nil {
		return nil, 0, err
	}
	return BuildFromGoImage(img, cfg)
}

// BuildFromGoImage constructs a quadtree from a Go image.Image.
func BuildFromGoImage(img image.Image, cfg BuildConfig) (*QuadNode, uint32, error) {
	bounds := img.Bounds()
	w := bounds.Dx()
	h := bounds.Dy()
	maxDim := w
	if h > maxDim {
		maxDim = h
	}
	size := nextPow2(uint32(maxDim))
	pixels := make([]Color, size*size)
	for py := uint32(0); py < size; py++ {
		for px := uint32(0); px < size; px++ {
			if int(px) < w && int(py) < h {
				r, g, b, a := img.At(bounds.Min.X+int(px), bounds.Min.Y+int(py)).RGBA()
				c := RGBToYCbCr(uint8(r>>8), uint8(g>>8), uint8(b>>8))
				c.A = uint8(a >> 8)
				pixels[py*size+px] = c
			} else {
				pixels[py*size+px] = Color{Y: 0, Cb: 128, Cr: 128, A: 0}
			}
		}
	}
	maxDepth := MaxDepthForResolution(size)
	if cfg.MaxDepth > 0 && cfg.MaxDepth < maxDepth {
		maxDepth = cfg.MaxDepth
	}
	root := buildRecursive(pixels, size, 0, 0, maxDepth, cfg.Quality)
	return root, size, nil
}

// BuildFromPixels constructs a quadtree from a pre-built pixel array.
func BuildFromPixels(pixels []Color, width uint32, cfg BuildConfig) *QuadNode {
	maxDepth := MaxDepthForResolution(width)
	if cfg.MaxDepth > 0 && cfg.MaxDepth < maxDepth {
		maxDepth = cfg.MaxDepth
	}
	return buildRecursive(pixels, width, 0, 0, maxDepth, cfg.Quality)
}

func buildRecursive(pixels []Color, imgWidth uint32, code uint64, depth uint8, maxDepth uint8, quality uint8) *QuadNode {
	node := &QuadNode{Code: code, Depth: depth}
	if depth == maxDepth {
		x, y := morton.Decode2D(code)
		if x < imgWidth && y < imgWidth {
			node.Color = pixels[y*imgWidth+x]
		}
		node.Mask = 0
		return node
	}
	var children [4]*QuadNode
	for i := uint8(0); i < 4; i++ {
		childCode := morton.ChildCode(code, i)
		children[i] = buildRecursive(pixels, imgWidth, childCode, depth+1, maxDepth, quality)
	}
	node.Color = averageColors(children[0].Color, children[1].Color, children[2].Color, children[3].Color)
	if canPrune(node.Color, children, quality) {
		node.Mask = 0
		node.Children = [4]*QuadNode{}
		return node
	}
	node.Mask = 0x0F
	node.Children = children
	for i := uint8(0); i < 4; i++ {
		children[i].Delta = computeDelta(node.Color, children[i].Color)
	}
	return node
}

func averageColors(a, b, c, d Color) Color {
	return Color{
		Y:  uint8((uint16(a.Y) + uint16(b.Y) + uint16(c.Y) + uint16(d.Y) + 2) / 4),
		Cb: uint8((uint16(a.Cb) + uint16(b.Cb) + uint16(c.Cb) + uint16(d.Cb) + 2) / 4),
		Cr: uint8((uint16(a.Cr) + uint16(b.Cr) + uint16(c.Cr) + uint16(d.Cr) + 2) / 4),
		A:  uint8((uint16(a.A) + uint16(b.A) + uint16(c.A) + uint16(d.A) + 2) / 4),
	}
}

// canPrune checks if all 4 children are close enough to the parent average.
// CRITICAL: never prune a parent whose children have their own children —
// that would silently discard subtree detail.
func canPrune(avg Color, children [4]*QuadNode, quality uint8) bool {
	threshold := float64(255 - quality)
	chromaThreshold := threshold * 2
	for _, c := range children {
		if !c.IsLeaf() {
			return false
		}
		dy := math.Abs(float64(c.Color.Y) - float64(avg.Y))
		dcb := math.Abs(float64(c.Color.Cb) - float64(avg.Cb))
		dcr := math.Abs(float64(c.Color.Cr) - float64(avg.Cr))
		if dy > threshold || dcb > chromaThreshold || dcr > chromaThreshold {
			return false
		}
	}
	return true
}

func computeDelta(parent, child Color) ColorDelta {
	return ColorDelta{
		DY:  clampI8(int16(child.Y) - int16(parent.Y)),
		DCb: clampI8(int16(child.Cb) - int16(parent.Cb)),
		DCr: clampI8(int16(child.Cr) - int16(parent.Cr)),
		DA:  clampI8(int16(child.A) - int16(parent.A)),
	}
}

func clampI8(v int16) int8 {
	if v < -128 { return -128 }
	if v > 127  { return 127 }
	return int8(v)
}

func nextPow2(v uint32) uint32 {
	v--
	v |= v >> 1; v |= v >> 2; v |= v >> 4; v |= v >> 8; v |= v >> 16
	v++
	return v
}

// RenderToPixels reconstructs a pixel array from the quadtree.
func RenderToPixels(root *QuadNode, width uint32, maxRenderDepth uint8) []color.RGBA {
	pixels := make([]color.RGBA, width*width)
	renderNode(root, pixels, width, MaxDepthForResolution(width), maxRenderDepth)
	return pixels
}

func renderNode(n *QuadNode, pixels []color.RGBA, width uint32, treeDepth, maxRenderDepth uint8) {
	if n == nil { return }
	if n.IsLeaf() || n.Depth >= maxRenderDepth {
		fillRegion(n, pixels, width, treeDepth)
		return
	}
	for i := uint8(0); i < 4; i++ {
		if n.Children[i] != nil {
			renderNode(n.Children[i], pixels, width, treeDepth, maxRenderDepth)
		} else {
			fillQuadrant(n, i, pixels, width, treeDepth)
		}
	}
}

func fillRegion(n *QuadNode, pixels []color.RGBA, width uint32, treeDepth uint8) {
	r, g, b := YCbCrToRGB(n.Color)
	rgba := color.RGBA{R: r, G: g, B: b, A: n.Color.A}
	regionSize := width >> n.Depth
	baseX, baseY := regionTopLeft(n.Code, n.Depth, treeDepth)
	for dy := uint32(0); dy < regionSize; dy++ {
		for dx := uint32(0); dx < regionSize; dx++ {
			px, py := baseX+dx, baseY+dy
			if px < width && py < width {
				pixels[py*width+px] = rgba
			}
		}
	}
}

func fillQuadrant(parent *QuadNode, childIdx uint8, pixels []color.RGBA, width uint32, treeDepth uint8) {
	childCode := morton.ChildCode(parent.Code, childIdx)
	childDepth := parent.Depth + 1
	regionSize := width >> childDepth
	baseX, baseY := regionTopLeft(childCode, childDepth, treeDepth)
	r, g, b := YCbCrToRGB(parent.Color)
	rgba := color.RGBA{R: r, G: g, B: b, A: parent.Color.A}
	for dy := uint32(0); dy < regionSize; dy++ {
		for dx := uint32(0); dx < regionSize; dx++ {
			px, py := baseX+dx, baseY+dy
			if px < width && py < width {
				pixels[py*width+px] = rgba
			}
		}
	}
}

func regionTopLeft(code uint64, depth, treeDepth uint8) (x, y uint32) {
	fullCode := code << (2 * (treeDepth - depth))
	return morton.Decode2D(fullCode)
}
