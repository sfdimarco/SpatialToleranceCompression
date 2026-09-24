package codec

import (
	"bytes"
	"image"
	"image/color"
	"image/png"
	"os"
	"path/filepath"
	"testing"

	"github.com/sfdimarco/geo/pkg/quadtree"
)

// TestRoundtripPixels checks every PIXEL after encode -> decode, not just node
// counts. Regression test for the bug where decoded child Morton codes were
// assigned after their subtrees were decoded, which left 3/4 of every image
// unpainted while node counts still matched.
func TestRoundtripPixels(t *testing.T) {
	const w = 64
	img := image.NewRGBA(image.Rect(0, 0, w, w))
	for y := 0; y < w; y++ {
		for x := 0; x < w; x++ {
			c := color.RGBA{uint8(x * 4), uint8(y * 4), uint8((x ^ y) * 4), 255}
			if x > 40 && y > 40 { c = color.RGBA{250, 30, 30, 255} }
			img.Set(x, y, c)
		}
	}
	p := filepath.Join(t.TempDir(), "in.png")
	f, _ := os.Create(p); png.Encode(f, img); f.Close()

	root, width, err := quadtree.BuildFromImage(p, quadtree.BuildConfig{Quality: 255})
	if err != nil { t.Fatal(err) }
	want := quadtree.RenderToPixels(root, width, 255)

	for _, raw := range []bool{true, false} {
		var buf bytes.Buffer
		if raw { Encode(&buf, root, width, width, 255) } else { EncodeHuffman(&buf, root, width, width, 255) }
		dec, _, err := Decode(bytes.NewReader(buf.Bytes()), 255)
		if err != nil { t.Fatal(err) }
		got := quadtree.RenderToPixels(dec, width, 255)
		bad := 0
		for i := range want { if want[i] != got[i] { bad++ } }
		if bad != 0 { t.Errorf("raw=%v: %d of %d pixels differ after roundtrip", raw, bad, len(want)) }
	}
}
