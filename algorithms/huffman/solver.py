import heapq
import itertools
import time


class Node:
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None


def build_frequencies(text):
    frequencies = {}
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1
    return frequencies


def build_tree(frequencies):
    counter = itertools.count()
    heap = [(freq, next(counter), Node(char, freq)) for char, freq in frequencies.items()]
    heapq.heapify(heap)

    if len(heap) == 1:
        only_freq, _, only_node = heap[0]
        return Node(None, only_freq, only_node, None)

    while len(heap) > 1:
        freq1, _, node1 = heapq.heappop(heap)
        freq2, _, node2 = heapq.heappop(heap)
        merged = Node(None, freq1 + freq2, node1, node2)
        heapq.heappush(heap, (merged.freq, next(counter), merged))

    return heap[0][2]


def build_codes(node, prefix="", codes=None):
    if codes is None:
        codes = {}
    if node is None:
        return codes
    if node.is_leaf():
        codes[node.char] = prefix or "0"
        return codes
    build_codes(node.left, prefix + "0", codes)
    build_codes(node.right, prefix + "1", codes)
    return codes


def tree_to_dict(node):
    if node is None:
        return None
    return {
        "char": node.char,
        "freq": node.freq,
        "left": tree_to_dict(node.left),
        "right": tree_to_dict(node.right),
    }


def encode(text, codes):
    return "".join(codes[char] for char in text)


def decode(bitstring, tree):
    if tree.is_leaf():
        return tree.char * len(bitstring)
    result = []
    node = tree
    for bit in bitstring:
        node = node.left if bit == "0" else node.right
        if node.is_leaf():
            result.append(node.char)
            node = tree
    return "".join(result)


def solve(text):
    start_time = time.perf_counter()

    if not text:
        raise ValueError("Texto vazio nao pode ser codificado")

    frequencies = build_frequencies(text)
    tree = build_tree(frequencies)
    codes = build_codes(tree)
    encoded = encode(text, codes)
    decoded = decode(encoded, tree)

    original_bits = len(text) * 8
    encoded_bits = len(encoded)
    compression_ratio = 1 - (encoded_bits / original_bits) if original_bits else 0
    average_code_length = sum(len(codes[char]) * freq for char, freq in frequencies.items()) / len(text)

    elapsed = time.perf_counter() - start_time

    return {
        "text": text,
        "frequencies": sorted(
            [{"char": char, "count": freq} for char, freq in frequencies.items()],
            key=lambda item: item["count"],
            reverse=True,
        ),
        "codes": [{"char": char, "code": code} for char, code in sorted(codes.items(), key=lambda item: len(item[1]))],
        "tree": tree_to_dict(tree),
        "encoded_text": encoded,
        "decoded_text": decoded,
        "decoding_matches_original": decoded == text,
        "original_bits": original_bits,
        "encoded_bits": encoded_bits,
        "average_code_length": average_code_length,
        "compression_ratio": compression_ratio,
        "criterion": "unir sempre os dois nos de menor frequencia (fila de prioridade / heap)",
        "metrics": {
            "elapsed_seconds": elapsed,
        },
    }
