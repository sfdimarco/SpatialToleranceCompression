// geocoder is the CLI tool for encoding and decoding .geoi image files.
//
// Usage:
//
//	geocoder encode -i input.png -o output.geoi [-q quality] [--raw]
//	geocoder decode -i input.geoi -o output.png [-d maxDepth]
//	geocoder info   -i file.geoi
//	geocoder bench  -i input.png [-q quality]
package main

import (
	"bytes"
	"fmt"
	"image"
	"image/color"
	"image/jpeg"
	"image/png"
	"os"
	"strings"
	"time"

	"github.com/sfdimarco/geo/pkg/codec"
	"github.com/sfdimarco/geo/pkg/quadtree"
)

func main() {
	if len(os.Args) < 2 { printUsage(); os.Exit(1) }
	switch os.Args[1] {
	case "encode": cmdEncode()
	case "decode": cmdDecode()
	case "info":   cmdInfo()
	case "bench":  cmdBench()
	default:
		fmt.Fprintf(os.Stderr, "Unknown command: %s\n", os.Args[1])
		printUsage(); os.Exit(1)
	}
}

func printUsage() {
	fmt.Println(`geocoder - GEO image compression tool

Commands:
  encode  -i <input.png> -o <output.geoi> [-q quality] [--raw]
  decode  -i <input.geoi> -o <output.png> [-d maxDepth]
  info    -i <file.geoi>
  bench   -i <input.png> [-q quality]

Options:
  -q  Quality: 0 (max compression) to 255 (lossless). Default: 245
  -d  Max decode depth for progressive rendering. Default: 255 (full)
  --raw  Use v1 raw encoding instead of v2 Huffman`)
}

func cmdEncode() {
	input, output, quality, raw := parseEncodeArgs()
	modeStr := "v2/Huffman"
	if raw { modeStr = "v1/raw" }
	fmt.Printf("Encoding %s → %s (quality=%d, mode=%s)\n", input, output, quality, modeStr)
	start := time.Now()
	cfg := quadtree.BuildConfig{Quality: quality}
	root, width, err := quadtree.BuildFromImage(input, cfg)
	if err != nil { fmt.Fprintf(os.Stderr, "Error loading image: %v\n", err); os.Exit(1) }
	buildTime := time.Since(start)
	start = time.Now()
	f, err := os.Create(output)
	if err != nil { fmt.Fprintf(os.Stderr, "Error creating output: %v\n", err); os.Exit(1) }
	defer f.Close()
	if raw { err = codec.Encode(f, root, width, width, quality)
	} else  { err = codec.EncodeHuffman(f, root, width, width, quality) }
	if err != nil { fmt.Fprintf(os.Stderr, "Error encoding: %v\n", err); os.Exit(1) }
	encodeTime := time.Since(start)
	stat, _ := f.Stat()
	rawSize := width * width * 4
	fmt.Printf("  Image size: %dx%d\n", width, width)
	fmt.Printf("  Tree nodes: %d (leaves: %d)\n", root.NodeCount(), root.LeafCount())
	fmt.Printf("  Max depth:  %d\n", root.MaxTreeDepth())
	fmt.Printf("  File size:  %d bytes\n", stat.Size())
	fmt.Printf("  Raw pixels: %d bytes\n", rawSize)
	fmt.Printf("  Ratio:      %.2fx\n", float64(rawSize)/float64(stat.Size()))
	fmt.Printf("  Build time: %v\n", buildTime)
	fmt.Printf("  Write time: %v\n", encodeTime)
}

func cmdDecode() {
	input, output, maxDepth := parseDecodeArgs()
	fmt.Printf("Decoding %s → %s (maxDepth=%d)\n", input, output, maxDepth)
	f, err := os.Open(input)
	if err != nil { fmt.Fprintf(os.Stderr, "Error opening: %v\n", err); os.Exit(1) }
	defer f.Close()
	start := time.Now()
	root, header, err := codec.Decode(f, maxDepth)
	if err != nil { fmt.Fprintf(os.Stderr, "Error decoding: %v\n", err); os.Exit(1) }
	decodeTime := time.Since(start)
	start = time.Now()
	pixels := quadtree.RenderToPixels(root, header.Width, maxDepth)
	img := image.NewRGBA(image.Rect(0, 0, int(header.Width), int(header.Width)))
	for i, px := range pixels {
		img.SetRGBA(i%int(header.Width), i/int(header.Width), px)
	}
	out, err := os.Create(output)
	if err != nil { fmt.Fprintf(os.Stderr, "Error creating output: %v\n", err); os.Exit(1) }
	defer out.Close()
	if strings.HasSuffix(output, ".jpg") || strings.HasSuffix(output, ".jpeg") {
		err = jpeg.Encode(out, img, &jpeg.Options{Quality: 95})
	} else { err = png.Encode(out, img) }
	if err != nil { fmt.Fprintf(os.Stderr, "Error writing output: %v\n", err); os.Exit(1) }
	renderTime := time.Since(start)
	versionStr := "v1/raw"
	if header.Version == codec.VersionHuffman { versionStr = "v2/Huffman" }
	fmt.Printf("  Format:     %s\n", versionStr)
	fmt.Printf("  Dimensions: %dx%d\n", header.Width, header.Height)
	fmt.Printf("  Nodes:      %d\n", root.NodeCount())
	fmt.Printf("  Decode:     %v\n", decodeTime)
	fmt.Printf("  Render:     %v\n", renderTime)
}

func cmdInfo() {
	if len(os.Args) < 4 || os.Args[2] != "-i" { fmt.Fprintln(os.Stderr, "Usage: geocoder info -i <file.geoi>"); os.Exit(1) }
	f, err := os.Open(os.Args[3])
	if err != nil { fmt.Fprintf(os.Stderr, "Error: %v\n", err); os.Exit(1) }
	defer f.Close()
	root, header, err := codec.Decode(f, 255)
	if err != nil { fmt.Fprintf(os.Stderr, "Error: %v\n", err); os.Exit(1) }
	stat, _ := os.Stat(os.Args[3])
	versionStr := "v1/raw"
	if header.Version == codec.VersionHuffman { versionStr = "v2/Huffman" }
	fmt.Printf("File:       %s\n", os.Args[3])
	fmt.Printf("Format:     %s\n", versionStr)
	fmt.Printf("Dimensions: %dx%d\n", header.Width, header.Height)
	fmt.Printf("Max Depth:  %d\n", header.MaxDepth)
	fmt.Printf("Quality:    %d\n", header.Quality)
	fmt.Printf("File Size:  %d bytes\n", stat.Size())
	fmt.Printf("Nodes:      %d\n", root.NodeCount())
	fmt.Printf("Leaves:     %d\n", root.LeafCount())
	fmt.Printf("Tree Depth: %d\n", root.MaxTreeDepth())
	rawSize := header.Width * header.Height * 4
	fmt.Printf("Raw Size:   %d bytes\n", rawSize)
	fmt.Printf("Ratio:      %.2fx\n", float64(rawSize)/float64(stat.Size()))
}

func cmdBench() {
	if len(os.Args) < 4 || os.Args[2] != "-i" { fmt.Fprintln(os.Stderr, "Usage: geocoder bench -i <input.png> [-q quality]"); os.Exit(1) }
	input := os.Args[3]
	quality := uint8(245)
	for i := 4; i < len(os.Args)-1; i++ {
		if os.Args[i] == "-q" { q := 0; fmt.Sscanf(os.Args[i+1], "%d", &q); quality = uint8(q) }
	}
	fmt.Printf("═══════════════════════════════════════════════\n")
	fmt.Printf("  GEO Benchmark: %s (quality=%d)\n", input, quality)
	fmt.Printf("═══════════════════════════════════════════════\n\n")
	cfg := quadtree.BuildConfig{Quality: quality}
	start := time.Now()
	root, width, err := quadtree.BuildFromImage(input, cfg)
	if err != nil { fmt.Fprintf(os.Stderr, "Error: %v\n", err); os.Exit(1) }
	buildTime := time.Since(start)
	rawSize := int(width * width * 4)
	var bufV1 bytes.Buffer
	start = time.Now(); codec.Encode(&bufV1, root, width, width, quality); v1EncodeTime := time.Since(start)
	start = time.Now(); codec.Decode(bytes.NewReader(bufV1.Bytes()), 255);  v1DecodeTime := time.Since(start)
	var bufV2 bytes.Buffer
	start = time.Now(); codec.EncodeHuffman(&bufV2, root, width, width, quality); v2EncodeTime := time.Since(start)
	start = time.Now(); decoded, _, _ := codec.Decode(bytes.NewReader(bufV2.Bytes()), 255); v2DecodeTime := time.Since(start)
	fi, _ := os.Open(input); img, _, _ := image.Decode(fi); fi.Close()
	jpegSizes := make(map[int]int)
	for _, jq := range []int{95, 85, 75, 50} { var jbuf bytes.Buffer; jpeg.Encode(&jbuf, img, &jpeg.Options{Quality: jq}); jpegSizes[jq] = jbuf.Len() }
	start = time.Now(); quadtree.RenderToPixels(decoded, width, 255); renderTime := time.Since(start)
	fmt.Printf("Image:       %dx%d (%d raw bytes)\n", width, width, rawSize)
	fmt.Printf("Nodes:       %d total, %d leaves\n", root.NodeCount(), root.LeafCount())
	fmt.Printf("Tree depth:  %d\n", root.MaxTreeDepth())
	fmt.Printf("Build time:  %v\n\n", buildTime)
	fmt.Printf("─── Compression Results ───\n\n")
	fmt.Printf("  %-20s %10s %10s %10s %10s\n", "Format", "Size", "Ratio", "Encode", "Decode")
	fmt.Printf("  %-20s %10s %10s %10s %10s\n", "──────", "────", "─────", "──────", "──────")
	fmt.Printf("  %-20s %10d %10s %10s %10s\n", "Raw pixels", rawSize, "1.0x", "—", "—")
	fmt.Printf("  %-20s %10d %9.1fx %10v %10v\n", ".geoi v1 (raw)", bufV1.Len(), float64(rawSize)/float64(bufV1.Len()), v1EncodeTime, v1DecodeTime)
	fmt.Printf("  %-20s %10d %9.1fx %10v %10v\n", ".geoi v2 (Huffman)", bufV2.Len(), float64(rawSize)/float64(bufV2.Len()), v2EncodeTime, v2DecodeTime)
	for _, jq := range []int{95, 85, 75, 50} { fmt.Printf("  %-20s %10d %9.1fx\n", fmt.Sprintf("JPEG q=%d", jq), jpegSizes[jq], float64(rawSize)/float64(jpegSizes[jq])) }
	fmt.Printf("\n  Render time: %v\n", renderTime)
	fmt.Printf("\n─── Progressive Decode (V2) ───\n\n")
	maxD := quadtree.MaxDepthForResolution(width)
	for d := uint8(0); d <= maxD; d++ {
		dec, _, _ := codec.Decode(bytes.NewReader(bufV2.Bytes()), d)
		res := width >> (maxD - d); if res == 0 { res = 1 }
		fmt.Printf("  Depth %2d: %4dx%-4d  %d nodes\n", d, res, res, dec.NodeCount())
	}
}

func parseEncodeArgs() (input, output string, quality uint8, raw bool) {
	quality = 245
	for i := 2; i < len(os.Args); i++ {
		switch os.Args[i] {
		case "-i": i++; if i < len(os.Args) { input = os.Args[i] }
		case "-o": i++; if i < len(os.Args) { output = os.Args[i] }
		case "-q": i++; if i < len(os.Args) { q := 0; fmt.Sscanf(os.Args[i], "%d", &q); quality = uint8(q) }
		case "--raw": raw = true
		}
	}
	if input == "" || output == "" { fmt.Fprintln(os.Stderr, "Usage: geocoder encode -i <input.png> -o <output.geoi> [-q quality] [--raw]"); os.Exit(1) }
	return
}

func parseDecodeArgs() (input, output string, maxDepth uint8) {
	maxDepth = 255
	for i := 2; i < len(os.Args); i++ {
		switch os.Args[i] {
		case "-i": i++; if i < len(os.Args) { input = os.Args[i] }
		case "-o": i++; if i < len(os.Args) { output = os.Args[i] }
		case "-d": i++; if i < len(os.Args) { d := 0; fmt.Sscanf(os.Args[i], "%d", &d); maxDepth = uint8(d) }
		}
	}
	if input == "" || output == "" { fmt.Fprintln(os.Stderr, "Usage: geocoder decode -i <input.geoi> -o <output.png> [-d maxDepth]"); os.Exit(1) }
	return
}

func init() { _ = color.RGBA{} }
