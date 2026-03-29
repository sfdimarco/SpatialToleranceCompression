package quadtree

import (
	"testing"
)

func TestRGBToYCbCr_Roundtrip(t *testing.T) {
	testCases := []struct{ r, g, b uint8 }{
		{0, 0, 0}, {255, 255, 255}, {255, 0, 0}, {0, 255, 0}, {0, 0, 255}, {128, 128, 128}, {42, 100, 200},
	}
	for _, tc := range testCases {
		c := RGBToYCbCr(tc.r, tc.g, tc.b)
		gotR, gotG, gotB := YCbCrToRGB(c)
		dr := int(gotR) - int(tc.r)
		dg := int(gotG) - int(tc.g)
		db := int(gotB) - int(tc.b)
		if dr < -1 || dr > 1 || dg < -1 || dg > 1 || db < -1 || db > 1 {
			t.Errorf("Roundtrip (%d,%d,%d) → YCbCr → (%d,%d,%d), delta too large", tc.r, tc.g, tc.b, gotR, gotG, gotB)
		}
	}
}

func TestMaxDepthForResolution(t *testing.T) {
	tests := []struct {
		width uint32
		depth uint8
	}{
		{1, 0}, {2, 1}, {4, 2}, {8, 3}, {16, 4}, {64, 6}, {256, 8}, {1024, 10}, {4096, 12},
	}
	for _, tc := range tests {
		got := MaxDepthForResolution(tc.width)
		if got != tc.depth {
			t.Errorf("MaxDepthForResolution(%d) = %d, want %d", tc.width, got, tc.depth)
		}
	}
}

func TestBuildFromPixels_UniformColor(t *testing.T) {
	width := uint32(4)
	pixels := make([]Color, width*width)
	uniform := RGBToYCbCr(100, 150, 200)
	for i := range pixels {
		pixels[i] = uniform
	}
	cfg := BuildConfig{Quality: 128, MaxDepth: 0}
	root := BuildFromPixels(pixels, width, cfg)
	if !root.IsLeaf() {
		t.Errorf("Uniform image should collapse to a single leaf, got mask=%d", root.Mask)
	}
	if root.NodeCount() != 1 {
		t.Errorf("Uniform image should have 1 node, got %d", root.NodeCount())
	}
}

func TestBuildFromPixels_Checkerboard(t *testing.T) {
	width := uint32(4)
	pixels := make([]Color, width*width)
	black := RGBToYCbCr(0, 0, 0)
	white := RGBToYCbCr(255, 255, 255)
	for y := uint32(0); y < width; y++ {
		for x := uint32(0); x < width; x++ {
			if (x+y)%2 == 0 {
				pixels[y*width+x] = black
			} else {
				pixels[y*width+x] = white
			}
		}
	}
	cfg := BuildConfig{Quality: 255, MaxDepth: 0}
	root := BuildFromPixels(pixels, width, cfg)
	if root.IsLeaf() {
		t.Error("Lossless checkerboard should NOT collapse to a single leaf")
	}
	if root.LeafCount() != 16 {
		t.Errorf("Lossless checkerboard should have 16 leaves, got %d", root.LeafCount())
	}
	cfg2 := BuildConfig{Quality: 128, MaxDepth: 0}
	root2 := BuildFromPixels(pixels, width, cfg2)
	t.Logf("Lossy checkerboard (q=128): %d nodes, %d leaves", root2.NodeCount(), root2.LeafCount())
}

func TestNodeCount_And_LeafCount(t *testing.T) {
	root := &QuadNode{Depth: 0, Mask: 0x0F}
	for i := uint8(0); i < 4; i++ {
		root.Children[i] = &QuadNode{Depth: 1, Mask: 0}
	}
	if root.NodeCount() != 5 {
		t.Errorf("Expected 5 nodes, got %d", root.NodeCount())
	}
	if root.LeafCount() != 4 {
		t.Errorf("Expected 4 leaves, got %d", root.LeafCount())
	}
}
