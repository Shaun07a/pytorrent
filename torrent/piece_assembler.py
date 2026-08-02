class PieceAssembler:

    def __init__(self):

        self.blocks = {}

    def add_block(
        self,
        piece_index,
        begin,
        block
    ):

        if piece_index not in self.blocks:
            self.blocks[piece_index] = {}

        self.blocks[piece_index][begin] = block

    def piece_size(self, piece_index):

        if piece_index not in self.blocks:
            return 0

        return sum(
            len(block)
            for block in self.blocks[piece_index].values()
        )

    def assemble_piece(self, piece_index):

        if piece_index not in self.blocks:
            return b""

        piece = b""

        for offset in sorted(
            self.blocks[piece_index]
        ):

            piece += self.blocks[piece_index][offset]

        return piece

    def clear_piece(self, piece_index):

        if piece_index in self.blocks:
            del self.blocks[piece_index]