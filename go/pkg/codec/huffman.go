// Huffman entropy coding for the GEO delta stream.
package codec

import (
	"container/heap"
	"io"
)

type huffNode struct {
	symbol byte
	freq   int
	left   *huffNode
	right  *huffNode
	isLeaf bool
}

type huffHeap []*huffNode

func (h huffHeap) Len() int            { return len(h) }
func (h huffHeap) Less(i, j int) bool  { return h[i].freq < h[j].freq }
func (h huffHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *huffHeap) Push(x interface{}) { *h = append(*h, x.(*huffNode)) }
func (h *huffHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	old[n-1] = nil
	*h = old[:n-1]
	return x
}

type HuffmanTable struct {
	codes   [256]huffCode
	lengths [256]uint8
}

type huffCode struct {
	bits   uint32
	length uint8
}

func BuildHuffmanTable(freq [256]int) *HuffmanTable {
	h := &huffHeap{}
	heap.Init(h)
	activeSymbols := 0
	for i := 0; i < 256; i++ {
		if freq[i] > 0 {
			heap.Push(h, &huffNode{symbol: byte(i), freq: freq[i], isLeaf: true})
			activeSymbols++
		}
	}
	if activeSymbols == 0 {
		table := &HuffmanTable{}
		table.codes[0] = huffCode{bits: 0, length: 1}
		table.lengths[0] = 1
		return table
	}
	if activeSymbols == 1 {
		table := &HuffmanTable{}
		node := heap.Pop(h).(*huffNode)
		table.codes[node.symbol] = huffCode{bits: 0, length: 1}
		table.lengths[node.symbol] = 1
		return table
	}
	for h.Len() > 1 {
		left := heap.Pop(h).(*huffNode)
		right := heap.Pop(h).(*huffNode)
		parent := &huffNode{freq: left.freq + right.freq, left: left, right: right}
		heap.Push(h, parent)
	}
	root := heap.Pop(h).(*huffNode)
	table := &HuffmanTable{}
	assignCodes(root, 0, 0, table)
	return table
}

func assignCodes(node *huffNode, code uint32, depth uint8, table *HuffmanTable) {
	if node == nil { return }
	if node.isLeaf {
		table.codes[node.symbol] = huffCode{bits: code, length: depth}
		table.lengths[node.symbol] = depth
		return
	}
	assignCodes(node.left, code<<1, depth+1, table)
	assignCodes(node.right, (code<<1)|1, depth+1, table)
}

type BitWriter struct {
	w       io.Writer
	buf     byte
	count   uint8
	written int
}

func NewBitWriter(w io.Writer) *BitWriter { return &BitWriter{w: w} }

func (bw *BitWriter) WriteBits(val uint32, n uint8) error {
	for i := int(n) - 1; i >= 0; i-- {
		bit := (val >> uint(i)) & 1
		bw.buf = (bw.buf << 1) | byte(bit)
		bw.count++
		if bw.count == 8 {
			if _, err := bw.w.Write([]byte{bw.buf}); err != nil { return err }
			bw.written++
			bw.buf = 0
			bw.count = 0
		}
	}
	return nil
}

func (bw *BitWriter) Flush() error {
	if bw.count > 0 {
		bw.buf <<= (8 - bw.count)
		if _, err := bw.w.Write([]byte{bw.buf}); err != nil { return err }
		bw.written++
		bw.buf = 0
		bw.count = 0
	}
	return nil
}

func (bw *BitWriter) BytesWritten() int { return bw.written }

type BitReader struct {
	r     io.Reader
	buf   byte
	count uint8
}

func NewBitReader(r io.Reader) *BitReader { return &BitReader{r: r} }

func (br *BitReader) ReadBit() (byte, error) {
	if br.count == 0 {
		b := make([]byte, 1)
		if _, err := io.ReadFull(br.r, b); err != nil { return 0, err }
		br.buf = b[0]
		br.count = 8
	}
	br.count--
	return (br.buf >> br.count) & 1, nil
}

func (br *BitReader) ReadBits(n uint8) (uint32, error) {
	var val uint32
	for i := uint8(0); i < n; i++ {
		bit, err := br.ReadBit()
		if err != nil { return 0, err }
		val = (val << 1) | uint32(bit)
	}
	return val, nil
}

type HuffmanDecoder struct{ root *huffNode }

func BuildDecoder(table *HuffmanTable) *HuffmanDecoder {
	root := &huffNode{}
	for sym := 0; sym < 256; sym++ {
		length := table.lengths[sym]
		if length == 0 { continue }
		code := table.codes[sym]
		node := root
		for i := int(code.length) - 1; i >= 0; i-- {
			bit := (code.bits >> uint(i)) & 1
			if bit == 0 {
				if node.left == nil { node.left = &huffNode{} }
				node = node.left
			} else {
				if node.right == nil { node.right = &huffNode{} }
				node = node.right
			}
		}
		node.isLeaf = true
		node.symbol = byte(sym)
	}
	return &HuffmanDecoder{root: root}
}

func (hd *HuffmanDecoder) DecodeSymbol(br *BitReader) (byte, error) {
	node := hd.root
	for !node.isLeaf {
		bit, err := br.ReadBit()
		if err != nil { return 0, err }
		if bit == 0 { node = node.left } else { node = node.right }
		if node == nil { return 0, io.ErrUnexpectedEOF }
	}
	return node.symbol, nil
}

func SerializeTable(w io.Writer, table *HuffmanTable) error {
	count := uint16(0)
	for i := 0; i < 256; i++ {
		if table.lengths[i] > 0 { count++ }
	}
	if _, err := w.Write([]byte{byte(count >> 8), byte(count)}); err != nil { return err }
	for i := 0; i < 256; i++ {
		if table.lengths[i] > 0 {
			entry := []byte{
				byte(i), table.lengths[i],
				byte(table.codes[i].bits >> 24), byte(table.codes[i].bits >> 16),
				byte(table.codes[i].bits >> 8), byte(table.codes[i].bits),
			}
			if _, err := w.Write(entry); err != nil { return err }
		}
	}
	return nil
}

func DeserializeTable(r io.Reader) (*HuffmanTable, error) {
	countBuf := make([]byte, 2)
	if _, err := io.ReadFull(r, countBuf); err != nil { return nil, err }
	count := uint16(countBuf[0])<<8 | uint16(countBuf[1])
	table := &HuffmanTable{}
	for i := uint16(0); i < count; i++ {
		entry := make([]byte, 6)
		if _, err := io.ReadFull(r, entry); err != nil { return nil, err }
		sym := entry[0]
		length := entry[1]
		bits := uint32(entry[2])<<24 | uint32(entry[3])<<16 | uint32(entry[4])<<8 | uint32(entry[5])
		table.codes[sym] = huffCode{bits: bits, length: length}
		table.lengths[sym] = length
	}
	return table, nil
}
