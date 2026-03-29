// Package morton implements Z-order curve (Morton code) encoding/decoding.
//
// Morton codes interleave the bits of 2D coordinates (x, y) into a single
// integer that preserves spatial locality. This is the foundation of the
// GEO compression format — it lets us serialize a quadtree as a flat
// bitstream where progressive resolution = just reading more bytes.
//
// Bit layout:
//
//	x-bits go to even positions (0, 2, 4, ...)
//	y-bits go to odd  positions (1, 3, 5, ...)
//
// Example: (x=2, y=1)
//
//	x = 10 binary, y = 01 binary
//	Interleaved: y1 x1 y0 x0 = 0 1 1 0 = Morton code 6
package morton

// Encode2D interleaves x and y bits into a single Morton code.
func Encode2D(x, y uint32) uint64 {
	return spread(x) | (spread(y) << 1)
}

// Decode2D extracts x and y coordinates from a Morton code.
func Decode2D(code uint64) (x, y uint32) {
	x = compact(code)
	y = compact(code >> 1)
	return
}
// spread distributes bits of a 32-bit value into even bit positions of a 64-bit value.
func spread(v uint32) uint64 {
	x := uint64(v)
	x = (x | (x << 16)) & 0x0000FFFF0000FFFF
	x = (x | (x << 8)) & 0x00FF00FF00FF00FF
	x = (x | (x << 4)) & 0x0F0F0F0F0F0F0F0F
	x = (x | (x << 2)) & 0x3333333333333333
	x = (x | (x << 1)) & 0x5555555555555555
	return x
}

// compact collects even-position bits back into a packed 32-bit value.
func compact(x uint64) uint32 {
	x = x & 0x5555555555555555
	x = (x | (x >> 1)) & 0x3333333333333333
	x = (x | (x >> 2)) & 0x0F0F0F0F0F0F0F0F
	x = (x | (x >> 4)) & 0x00FF00FF00FF00FF
	x = (x | (x >> 8)) & 0x0000FFFF0000FFFF
	x = (x | (x >> 16)) & 0x00000000FFFFFFFF
	return uint32(x)
}

// ChildIndex returns which quadrant (0-3) a Morton code falls into at a given tree level.
func ChildIndex(code uint64, maxDepth, atLevel uint) uint8 {
	shift := 2 * (maxDepth - atLevel - 1)
	return uint8((code >> shift) & 0x3)
}

// ChildCode computes the Morton code for a child node.
func ChildCode(parentCode uint64, childIdx uint8) uint64 {
	return (parentCode << 2) | uint64(childIdx)
}

// QuadrantMaskBit converts a Morton child index (0-3) to the GEO mask bit value.
// GEO mask layout: TL=8, TR=4, BL=1, BR=2
var childToMask = [4]uint8{8, 4, 1, 2}

func QuadrantMaskBit(childIdx uint8) uint8 {
	return childToMask[childIdx]
}

// MaskBitToChild converts a GEO mask bit to the Morton child index.
func MaskBitToChild(maskBit uint8) uint8 {
	switch maskBit {
	case 8:
		return 0 // TL
	case 4:
		return 1 // TR
	case 1:
		return 2 // BL
	case 2:
		return 3 // BR
	default:
		return 0xFF
	}
}

// MaskToChildren returns Morton child indices for all active bits in a GEO mask.
func MaskToChildren(mask uint8) []uint8 {
	children := make([]uint8, 0, 4)
	for _, childIdx := range []uint8{0, 1, 2, 3} {
		if mask&childToMask[childIdx] != 0 {
			children = append(children, childIdx)
		}
	}
	return children
}
