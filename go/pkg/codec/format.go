// Package codec implements the .geoi binary file format encoder/decoder.
package codec

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"io"

	"github.com/sfdimarco/geo/pkg/quadtree"
)

var MagicGEOI = [4]byte{'G', 'E', 'O', 'i'}
var MagicGEOV = [4]byte{'G', 'E', 'O', 'v'}

const (
	HeaderSize     = 16
	VersionRaw     = 1
	VersionHuffman = 2
	ColorModeYCbCr = 0
	ColorModeRGB   = 1
)

type Header struct {
	Magic     [4]byte
	Version   uint8
	MaxDepth  uint8
	ColorMode uint8
	Quality   uint8
	Width     uint32
	Height    uint32
}

func WriteHeader(w io.Writer, h Header) error {
	return binary.Write(w, binary.BigEndian, h)
}

func ReadHeader(r io.Reader) (Header, error) {
	var h Header
	err := binary.Read(r, binary.BigEndian, &h)
	if err != nil { return h, err }
	if h.Magic != MagicGEOI {
		return h, fmt.Errorf("not a .geoi file: magic bytes %v", h.Magic)
	}
	if h.Version != VersionRaw && h.Version != VersionHuffman {
		return h, fmt.Errorf("unsupported version %d", h.Version)
	}
	return h, nil
}

// Encode writes a quadtree to a v1 (raw) .geoi bitstream.
func Encode(w io.Writer, root *quadtree.QuadNode, width, height uint32, quality uint8) error {
	h := Header{Magic: MagicGEOI, Version: VersionRaw, MaxDepth: root.MaxTreeDepth(),
		ColorMode: ColorModeYCbCr, Quality: quality, Width: width, Height: height}
	if err := WriteHeader(w, h); err != nil { return fmt.Errorf("write header: %w", err) }
	return encodeNodeV1(w, root, true)
}

func encodeNodeV1(w io.Writer, n *quadtree.QuadNode, isRoot bool) error {
	if isRoot {
		if _, err := w.Write([]byte{n.Color.Y, n.Color.Cb, n.Color.Cr, n.Color.A}); err != nil { return err }
	} else {
		if _, err := w.Write([]byte{byte(n.Delta.DY), byte(n.Delta.DCb), byte(n.Delta.DCr), byte(n.Delta.DA)}); err != nil { return err }
	}
	if _, err := w.Write([]byte{n.Mask}); err != nil { return err }
	if !n.IsLeaf() {
		for i := uint8(0); i < 4; i++ {
			if n.HasChild(i) && n.Children[i] != nil {
				if err := encodeNodeV1(w, n.Children[i], false); err != nil { return err }
			}
		}
	}
	return nil
}

// Decode reads a .geoi bitstream (v1 or v2) and reconstructs the quadtree.
func Decode(r io.Reader, maxDecodeDepth uint8) (*quadtree.QuadNode, Header, error) {
	h, err := ReadHeader(r)
	if err != nil { return nil, h, err }
	switch h.Version {
	case VersionRaw:
		root, err := decodeNodeV1(r, nil, 0, maxDecodeDepth, true)
		if err != nil { return nil, h, fmt.Errorf("decode v1: %w", err) }
		return root, h, nil
	case VersionHuffman:
		root, err := decodeV2(r, maxDecodeDepth)
		if err != nil { return nil, h, fmt.Errorf("decode v2: %w", err) }
		return root, h, nil
	default:
		return nil, h, fmt.Errorf("unsupported version %d", h.Version)
	}
}

func decodeNodeV1(r io.Reader, parent *quadtree.QuadNode, depth uint8, maxDepth uint8, isRoot bool) (*quadtree.QuadNode, error) {
	node := &quadtree.QuadNode{Depth: depth}
	colorBuf := make([]byte, 4)
	if _, err := io.ReadFull(r, colorBuf); err != nil { return nil, err }
	if isRoot {
		node.Color = quadtree.Color{Y: colorBuf[0], Cb: colorBuf[1], Cr: colorBuf[2], A: colorBuf[3]}
	} else {
		node.Delta = quadtree.ColorDelta{DY: int8(colorBuf[0]), DCb: int8(colorBuf[1]), DCr: int8(colorBuf[2]), DA: int8(colorBuf[3])}
		node.Color = quadtree.Color{
			Y:  uint8(int16(parent.Color.Y) + int16(node.Delta.DY)),
			Cb: uint8(int16(parent.Color.Cb) + int16(node.Delta.DCb)),
			Cr: uint8(int16(parent.Color.Cr) + int16(node.Delta.DCr)),
			A:  uint8(int16(parent.Color.A) + int16(node.Delta.DA)),
		}
	}
	maskBuf := make([]byte, 1)
	if _, err := io.ReadFull(r, maskBuf); err != nil { return nil, err }
	node.Mask = maskBuf[0]
	if depth >= maxDepth { node.Mask = 0; return node, nil }
	if !node.IsLeaf() {
		for i := uint8(0); i < 4; i++ {
			if node.HasChild(i) {
				child, err := decodeNodeV1(r, node, depth+1, maxDepth, false)
				if err != nil { return nil, err }
				child.Code = (node.Code << 2) | uint64(i)
				node.Children[i] = child
			}
		}
	}
	return node, nil
}

// EncodeHuffman writes a quadtree to a v2 (Huffman-coded) .geoi bitstream.
func EncodeHuffman(w io.Writer, root *quadtree.QuadNode, width, height uint32, quality uint8) error {
	h := Header{Magic: MagicGEOI, Version: VersionHuffman, MaxDepth: root.MaxTreeDepth(),
		ColorMode: ColorModeYCbCr, Quality: quality, Width: width, Height: height}
	var deltaY, deltaCb, deltaCr, masks []byte
	collectSymbols(root, &deltaY, &deltaCb, &deltaCr, &masks, true)
	var freqY, freqCb, freqCr, freqMask [256]int
	for _, v := range deltaY   { freqY[v]++ }
	for _, v := range deltaCb  { freqCb[v]++ }
	for _, v := range deltaCr  { freqCr[v]++ }
	for _, v := range masks    { freqMask[v]++ }
	tableY    := BuildHuffmanTable(freqY)
	tableCb   := BuildHuffmanTable(freqCb)
	tableCr   := BuildHuffmanTable(freqCr)
	tableMask := BuildHuffmanTable(freqMask)
	if err := WriteHeader(w, h); err != nil { return fmt.Errorf("write header: %w", err) }
	if _, err := w.Write([]byte{root.Color.Y, root.Color.Cb, root.Color.Cr, root.Color.A}); err != nil { return err }
	nodeCount := root.NodeCount()
	countBuf := make([]byte, 4)
	binary.BigEndian.PutUint32(countBuf, uint32(nodeCount))
	if _, err := w.Write(countBuf); err != nil { return err }
	for _, table := range []*HuffmanTable{tableY, tableCb, tableCr, tableMask} {
		if err := SerializeTable(w, table); err != nil { return fmt.Errorf("write huffman table: %w", err) }
	}
	var bitBuf bytes.Buffer
	bw := NewBitWriter(&bitBuf)
	if err := encodeNodeV2(bw, root, tableY, tableCb, tableCr, tableMask, true); err != nil { return err }
	if err := bw.Flush(); err != nil { return err }
	streamLen := uint32(bitBuf.Len())
	binary.BigEndian.PutUint32(countBuf, streamLen)
	if _, err := w.Write(countBuf); err != nil { return err }
	if _, err := w.Write(bitBuf.Bytes()); err != nil { return err }
	return nil
}

func collectSymbols(n *quadtree.QuadNode, deltaY, deltaCb, deltaCr, masks *[]byte, isRoot bool) {
	if !isRoot {
		*deltaY  = append(*deltaY,  byte(n.Delta.DY))
		*deltaCb = append(*deltaCb, byte(n.Delta.DCb))
		*deltaCr = append(*deltaCr, byte(n.Delta.DCr))
	}
	*masks = append(*masks, n.Mask)
	if !n.IsLeaf() {
		for i := uint8(0); i < 4; i++ {
			if n.HasChild(i) && n.Children[i] != nil {
				collectSymbols(n.Children[i], deltaY, deltaCb, deltaCr, masks, false)
			}
		}
	}
}

func encodeNodeV2(bw *BitWriter, n *quadtree.QuadNode, tableY, tableCb, tableCr, tableMask *HuffmanTable, isRoot bool) error {
	if !isRoot {
		dy := byte(n.Delta.DY); dcb := byte(n.Delta.DCb); dcr := byte(n.Delta.DCr)
		cY := tableY.codes[dy];   if err := bw.WriteBits(cY.bits, cY.length);     err != nil { return err }
		cCb := tableCb.codes[dcb]; if err := bw.WriteBits(cCb.bits, cCb.length);  err != nil { return err }
		cCr := tableCr.codes[dcr]; if err := bw.WriteBits(cCr.bits, cCr.length);  err != nil { return err }
	}
	cm := tableMask.codes[n.Mask]; if err := bw.WriteBits(cm.bits, cm.length); err != nil { return err }
	if !n.IsLeaf() {
		for i := uint8(0); i < 4; i++ {
			if n.HasChild(i) && n.Children[i] != nil {
				if err := encodeNodeV2(bw, n.Children[i], tableY, tableCb, tableCr, tableMask, false); err != nil { return err }
			}
		}
	}
	return nil
}

func decodeV2(r io.Reader, maxDecodeDepth uint8) (*quadtree.QuadNode, error) {
	rootColor := make([]byte, 4)
	if _, err := io.ReadFull(r, rootColor); err != nil { return nil, fmt.Errorf("read root color: %w", err) }
	countBuf := make([]byte, 4)
	if _, err := io.ReadFull(r, countBuf); err != nil { return nil, fmt.Errorf("read node count: %w", err) }
	tableY,    err := DeserializeTable(r); if err != nil { return nil, fmt.Errorf("read Y table: %w", err) }
	tableCb,   err := DeserializeTable(r); if err != nil { return nil, fmt.Errorf("read Cb table: %w", err) }
	tableCr,   err := DeserializeTable(r); if err != nil { return nil, fmt.Errorf("read Cr table: %w", err) }
	tableMask, err := DeserializeTable(r); if err != nil { return nil, fmt.Errorf("read mask table: %w", err) }
	if _, err := io.ReadFull(r, countBuf); err != nil { return nil, fmt.Errorf("read stream length: %w", err) }
	streamLen := binary.BigEndian.Uint32(countBuf)
	streamData := make([]byte, streamLen)
	if _, err := io.ReadFull(r, streamData); err != nil { return nil, fmt.Errorf("read bitstream: %w", err) }
	decY := BuildDecoder(tableY); decCb := BuildDecoder(tableCb)
	decCr := BuildDecoder(tableCr); decMask := BuildDecoder(tableMask)
	br := NewBitReader(bytes.NewReader(streamData))
	return decodeNodeV2(br, nil, 0, maxDecodeDepth,
		quadtree.Color{Y: rootColor[0], Cb: rootColor[1], Cr: rootColor[2], A: rootColor[3]},
		decY, decCb, decCr, decMask, true)
}

func decodeNodeV2(br *BitReader, parent *quadtree.QuadNode, depth, maxDepth uint8,
	rootColor quadtree.Color, decY, decCb, decCr, decMask *HuffmanDecoder, isRoot bool,
) (*quadtree.QuadNode, error) {
	node := &quadtree.QuadNode{Depth: depth}
	if isRoot {
		node.Color = rootColor
	} else {
		dyByte,  err := decY.DecodeSymbol(br);  if err != nil { return nil, fmt.Errorf("decode DY at depth %d: %w", depth, err) }
		dcbByte, err := decCb.DecodeSymbol(br); if err != nil { return nil, fmt.Errorf("decode DCb at depth %d: %w", depth, err) }
		dcrByte, err := decCr.DecodeSymbol(br); if err != nil { return nil, fmt.Errorf("decode DCr at depth %d: %w", depth, err) }
		node.Delta = quadtree.ColorDelta{DY: int8(dyByte), DCb: int8(dcbByte), DCr: int8(dcrByte)}
		node.Color = quadtree.Color{
			Y:  uint8(int16(parent.Color.Y)  + int16(node.Delta.DY)),
			Cb: uint8(int16(parent.Color.Cb) + int16(node.Delta.DCb)),
			Cr: uint8(int16(parent.Color.Cr) + int16(node.Delta.DCr)),
			A:  parent.Color.A,
		}
	}
	maskByte, err := decMask.DecodeSymbol(br)
	if err != nil { return nil, fmt.Errorf("decode mask at depth %d: %w", depth, err) }
	node.Mask = maskByte
	if depth >= maxDepth { node.Mask = 0; return node, nil }
	if !node.IsLeaf() {
		for i := uint8(0); i < 4; i++ {
			if node.HasChild(i) {
				child, err := decodeNodeV2(br, node, depth+1, maxDepth, rootColor, decY, decCb, decCr, decMask, false)
				if err != nil { return nil, err }
				child.Code = (node.Code << 2) | uint64(i)
				node.Children[i] = child
			}
		}
	}
	return node, nil
}
