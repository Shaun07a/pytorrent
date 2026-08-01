class Bitfield:
    def __init__(self, data: bytes):
        self.data = data

    def has_piece(self, index: int) -> bool:
        byte_index = index // 8
        bit_index = 7 - (index % 8)

        if byte_index >= len(self.data):
            return False

        return bool(self.data[byte_index] & (1 << bit_index))

    def count(self) -> int:
        total = 0

        for byte in self.data:
            total += bin(byte).count("1")

        return total

    def __len__(self):
        return len(self.data)