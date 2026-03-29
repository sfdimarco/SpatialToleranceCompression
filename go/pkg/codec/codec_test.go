package codec

import (
	"bytes"
	"testing"

	"github.com/sfdimarco/geo/pkg/quadtree"
)

func TestV1_EncodeDecodeRoundtrip_SingleLeaf(t *testing.T) {
	root := &quadtree.QuadNode{Code: 0, Depth: 0, Mask: 0, Color: quadtree.Color{Y: 128, Cb: 100, Cr: 150, A: 255}}
	var buf bytes.Buffer
	if err := Encode(&buf, root, 1, 1, 128); err != nil { t.Fatalf("Encode failed: %v", err) }
	t.Logf("V1 single leaf: %d bytes", buf.Len())
	decoded, header, err := Decode(&buf, 255)
	if err != nil { t.Fatalf("Decode failed: %v", err) }
	if header.Version != VersionRaw { t.Errorf("Version = %d, want %d", header.Version, VersionRaw) }
	if decoded.Color != root.Color { t.Errorf("Color mismatch: got %+v, want %+v", decoded.Color, root.Color) }
	if !decoded.IsLeaf() { t.Error("Decoded root should be a leaf") }
}

func TestV1_EncodeDecodeRoundtrip_WithChildren(t *testing.T) {
	root, childColors := makeTestTree()
	var buf bytes.Buffer
	if err := Encode(&buf, root, 2, 2, 128); err != nil { t.Fatalf("Encode failed: %v", err) }
	t.Logf("V1 with children: %d bytes", buf.Len())
	decoded, _, err := Decode(bytes.NewReader(buf.Bytes()), 255)
	if err != nil { t.Fatalf("Decode failed: %v", err) }
	if decoded.Color != root.Color { t.Errorf("Root color: got %+v, want %+v", decoded.Color, root.Color) }
	for i := uint8(0); i < 4; i++ {
		if decoded.Children[i].Color != childColors[i] {
			t.Errorf("V1 child %d color: got %+v, want %+v", i, decoded.Children[i].Color, childColors[i])
		}
	}
}

func TestV2_EncodeDecodeRoundtrip_SingleLeaf(t *testing.T) {
	root := &quadtree.QuadNode{Code: 0, Depth: 0, Mask: 0, Color: quadtree.Color{Y: 128, Cb: 100, Cr: 150, A: 255}}
	var buf bytes.Buffer
	if err := EncodeHuffman(&buf, root, 1, 1, 128); err != nil { t.Fatalf("EncodeHuffman failed: %v", err) }
	t.Logf("V2 single leaf: %d bytes", buf.Len())
	decoded, header, err := Decode(bytes.NewReader(buf.Bytes()), 255)
	if err != nil { t.Fatalf("Decode failed: %v", err) }
	if header.Version != VersionHuffman { t.Errorf("Version = %d, want %d", header.Version, VersionHuffman) }
	if decoded.Color != root.Color { t.Errorf("Color mismatch: got %+v, want %+v", decoded.Color, root.Color) }
}

func TestV2_EncodeDecodeRoundtrip_WithChildren(t *testing.T) {
	root, childColors := makeTestTree()
	var buf bytes.Buffer
	if err := EncodeHuffman(&buf, root, 2, 2, 128); err != nil { t.Fatalf("EncodeHuffman failed: %v", err) }
	t.Logf("V2 with children: %d bytes", buf.Len())
	decoded, _, err := Decode(bytes.NewReader(buf.Bytes()), 255)
	if err != nil { t.Fatalf("Decode failed: %v", err) }
	if decoded.Color != root.Color { t.Errorf("Root color: got %+v, want %+v", decoded.Color, root.Color) }
	for i := uint8(0); i < 4; i++ {
		child := decoded.Children[i]
		if child == nil { t.Errorf("Child %d is nil", i); continue }
		if child.Color != childColors[i] { t.Errorf("V2 child %d color: got %+v, want %+v", i, child.Color, childColors[i]) }
	}
}

func TestV2_EncodeDecodeRoundtrip_FromPixels(t *testing.T) {
	width := uint32(4)
	pixels := make([]quadtree.Color, width*width)
	for y := uint32(0); y < width; y++ {
		for x := uint32(0); x < width; x++ {
			pixels[y*width+x] = quadtree.Color{Y: uint8((x + y) * 30), Cb: 128, Cr: 128, A: 255}
		}
	}
	cfg := quadtree.BuildConfig{Quality: 240}
	root := quadtree.BuildFromPixels(pixels, width, cfg)
	var bufV1, bufV2 bytes.Buffer
	Encode(&bufV1, root, width, width, cfg.Quality)
	EncodeHuffman(&bufV2, root, width, width, cfg.Quality)
	t.Logf("4x4 gradient: V1=%d bytes, V2=%d bytes (%.1f%% of V1)", bufV1.Len(), bufV2.Len(), float64(bufV2.Len())/float64(bufV1.Len())*100)
	decoded, _, err := Decode(bytes.NewReader(bufV2.Bytes()), 255)
	if err != nil { t.Fatalf("V2 decode failed: %v", err) }
	if decoded.NodeCount() != root.NodeCount() { t.Errorf("NodeCount: decoded=%d, original=%d", decoded.NodeCount(), root.NodeCount()) }
}

func TestV2_LargerImage(t *testing.T) {
	width := uint32(64)
	pixels := make([]quadtree.Color, width*width)
	for y := uint32(0); y < width; y++ {
		for x := uint32(0); x < width; x++ {
			if y < width/2 { pixels[y*width+x] = quadtree.RGBToYCbCr(80, 130, uint8(180+y))
			} else          { pixels[y*width+x] = quadtree.RGBToYCbCr(uint8(60+x%20), uint8(120+y%30), 50) }
		}
	}
	cfg := quadtree.BuildConfig{Quality: 245}
	root := quadtree.BuildFromPixels(pixels, width, cfg)
	var bufV1, bufV2 bytes.Buffer
	Encode(&bufV1, root, width, width, cfg.Quality)
	EncodeHuffman(&bufV2, root, width, width, cfg.Quality)
	rawSize := width * width * 4
	t.Logf("64x64 scene: raw=%d V1=%d V2=%d", rawSize, bufV1.Len(), bufV2.Len())
	t.Logf("  V1 ratio: %.1fx", float64(rawSize)/float64(bufV1.Len()))
	t.Logf("  V2 ratio: %.1fx", float64(rawSize)/float64(bufV2.Len()))
	decoded, _, err := Decode(bytes.NewReader(bufV2.Bytes()), 255)
	if err != nil { t.Fatalf("V2 decode failed: %v", err) }
	if decoded.NodeCount() != root.NodeCount() { t.Errorf("NodeCount: decoded=%d, original=%d", decoded.NodeCount(), root.NodeCount()) }
}

func TestV2_ProgressiveDecode(t *testing.T) {
	width := uint32(8)
	pixels := make([]quadtree.Color, width*width)
	for i := range pixels { pixels[i] = quadtree.Color{Y: uint8(i % 256), Cb: 128, Cr: 128, A: 255} }
	cfg := quadtree.BuildConfig{Quality: 250}
	root := quadtree.BuildFromPixels(pixels, width, cfg)
	var buf bytes.Buffer
	EncodeHuffman(&buf, root, width, width, cfg.Quality)
	dec1, _, err := Decode(bytes.NewReader(buf.Bytes()), 1)
	if err != nil { t.Fatalf("Progressive V2 decode at depth 1 failed: %v", err) }
	decFull, _, _ := Decode(bytes.NewReader(buf.Bytes()), 255)
	if dec1.NodeCount() >= decFull.NodeCount() {
		t.Errorf("Progressive should have fewer nodes: depth1=%d, full=%d", dec1.NodeCount(), decFull.NodeCount())
	}
	t.Logf("V2 progressive: depth1=%d nodes, full=%d nodes", dec1.NodeCount(), decFull.NodeCount())
}

func TestHeaderValidation(t *testing.T) {
	badData := []byte("NOTi\x01\x02\x00\x80\x00\x00\x01\x00\x00\x00\x01\x00")
	_, err := ReadHeader(bytes.NewReader(badData))
	if err == nil { t.Error("Expected error for bad magic bytes") }
}

func TestHuffmanTable_BuildAndDecode(t *testing.T) {
	var freq [256]int
	freq[0] = 100; freq[1] = 50; freq[255] = 50; freq[128] = 10; freq[42] = 1
	table := BuildHuffmanTable(freq)
	if table.lengths[0] > table.lengths[128] {
		t.Errorf("Symbol 0 (freq=100) has longer code (%d) than symbol 128 (freq=10, code=%d)", table.lengths[0], table.lengths[128])
	}
	var buf bytes.Buffer
	if err := SerializeTable(&buf, table); err != nil { t.Fatalf("SerializeTable failed: %v", err) }
	table2, err := DeserializeTable(&buf)
	if err != nil { t.Fatalf("DeserializeTable failed: %v", err) }
	for i := 0; i < 256; i++ {
		if table.lengths[i] != table2.lengths[i] { t.Errorf("Symbol %d: length %d vs %d after roundtrip", i, table.lengths[i], table2.lengths[i]) }
	}
}

func TestBitWriterReader_Roundtrip(t *testing.T) {
	var buf bytes.Buffer
	bw := NewBitWriter(&buf)
	bw.WriteBits(0b101, 3); bw.WriteBits(0b1100, 4); bw.WriteBits(0b1, 1); bw.WriteBits(0b00110, 5)
	bw.Flush()
	br := NewBitReader(&buf)
	v1, _ := br.ReadBits(3); if v1 != 0b101   { t.Errorf("First 3 bits: got %03b, want 101", v1) }
	v2, _ := br.ReadBits(4); if v2 != 0b1100  { t.Errorf("Next 4 bits: got %04b, want 1100", v2) }
	v3, _ := br.ReadBits(1); if v3 != 1       { t.Errorf("Next 1 bit: got %01b, want 1", v3) }
	v4, _ := br.ReadBits(5); if v4 != 0b00110 { t.Errorf("Next 5 bits: got %05b, want 00110", v4) }
}

func makeTestTree() (*quadtree.QuadNode, [4]quadtree.Color) {
	root := &quadtree.QuadNode{Code: 0, Depth: 0, Mask: 0x0F, Color: quadtree.Color{Y: 128, Cb: 128, Cr: 128, A: 255}}
	childColors := [4]quadtree.Color{
		{Y: 100, Cb: 120, Cr: 130, A: 255}, {Y: 150, Cb: 130, Cr: 120, A: 255},
		{Y: 110, Cb: 140, Cr: 140, A: 255}, {Y: 140, Cb: 110, Cr: 110, A: 255},
	}
	for i := uint8(0); i < 4; i++ {
		root.Children[i] = &quadtree.QuadNode{Code: uint64(i), Depth: 1, Mask: 0, Color: childColors[i],
			Delta: quadtree.ColorDelta{DY: int8(int16(childColors[i].Y) - 128), DCb: int8(int16(childColors[i].Cb) - 128), DCr: int8(int16(childColors[i].Cr) - 128)}}
	}
	return root, childColors
}
