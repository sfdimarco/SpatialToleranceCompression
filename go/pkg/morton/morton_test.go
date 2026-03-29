package morton

import (
	"testing"
)

func TestEncodeDecode_Roundtrip(t *testing.T) {
	testCases := []struct{ x, y uint32 }{
		{0, 0}, {1, 0}, {0, 1}, {1, 1}, {2, 1}, {3, 3}, {255, 255}, {1023, 1023}, {65535, 65535},
	}
	for _, tc := range testCases {
		code := Encode2D(tc.x, tc.y)
		gotX, gotY := Decode2D(code)
		if gotX != tc.x || gotY != tc.y {
			t.Errorf("Roundtrip failed: Encode(%d,%d)=%d → Decode → (%d,%d)", tc.x, tc.y, code, gotX, gotY)
		}
	}
}

func TestEncode2D_KnownValues(t *testing.T) {
	expected := [4][4]uint64{
		{0, 1, 4, 5},     // y=0
		{2, 3, 6, 7},     // y=1
		{8, 9, 12, 13},   // y=2
		{10, 11, 14, 15}, // y=3
	}
	for y := uint32(0); y < 4; y++ {
		for x := uint32(0); x < 4; x++ {
			got := Encode2D(x, y)
			want := expected[y][x]
			if got != want {
				t.Errorf("Encode2D(%d, %d) = %d, want %d", x, y, got, want)
			}
		}
	}
}

func TestEncode2D_SpecificExample(t *testing.T) {
	code := Encode2D(2, 1)
	if code != 6 {
		t.Errorf("Encode2D(2, 1) = %d, want 6", code)
	}
}

func TestChildCode(t *testing.T) {
	c := ChildCode(0, 1)
	if c != 1 {
		t.Errorf("ChildCode(0, 1) = %d, want 1", c)
	}
	c = ChildCode(1, 2)
	if c != 6 {
		t.Errorf("ChildCode(1, 2) = %d, want 6", c)
	}
}

func TestQuadrantMaskBit(t *testing.T) {
	if QuadrantMaskBit(0) != 8 { t.Errorf("QuadrantMaskBit(0) = %d, want 8", QuadrantMaskBit(0)) }
	if QuadrantMaskBit(1) != 4 { t.Errorf("QuadrantMaskBit(1) = %d, want 4", QuadrantMaskBit(1)) }
	if QuadrantMaskBit(2) != 1 { t.Errorf("QuadrantMaskBit(2) = %d, want 1", QuadrantMaskBit(2)) }
	if QuadrantMaskBit(3) != 2 { t.Errorf("QuadrantMaskBit(3) = %d, want 2", QuadrantMaskBit(3)) }
}

func TestMaskToChildren(t *testing.T) {
	children := MaskToChildren(0x0F)
	if len(children) != 4 {
		t.Fatalf("MaskToChildren(0x0F) returned %d children, want 4", len(children))
	}
	for i, want := range []uint8{0, 1, 2, 3} {
		if children[i] != want {
			t.Errorf("MaskToChildren(0x0F)[%d] = %d, want %d", i, children[i], want)
		}
	}
	children = MaskToChildren(9)
	if len(children) != 2 || children[0] != 0 || children[1] != 2 {
		t.Errorf("MaskToChildren(9) = %v, want [0, 2]", children)
	}
	children = MaskToChildren(0)
	if len(children) != 0 {
		t.Errorf("MaskToChildren(0) = %v, want []", children)
	}
}

func TestMaskBitToChild_Roundtrip(t *testing.T) {
	for childIdx := uint8(0); childIdx < 4; childIdx++ {
		maskBit := QuadrantMaskBit(childIdx)
		got := MaskBitToChild(maskBit)
		if got != childIdx {
			t.Errorf("MaskBitToChild(QuadrantMaskBit(%d)) = %d, want %d", childIdx, got, childIdx)
		}
	}
}

func BenchmarkEncode2D(b *testing.B) {
	for i := 0; i < b.N; i++ {
		Encode2D(uint32(i), uint32(i>>16))
	}
}

func BenchmarkDecode2D(b *testing.B) {
	for i := 0; i < b.N; i++ {
		Decode2D(uint64(i))
	}
}
