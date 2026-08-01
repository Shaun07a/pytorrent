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

    def assemble_piece(
        self,
        piece_index
    ):

        if piece_index not in self.blocks:
            return None

        piece = b""

        for offset in sorted(
            self.blocks[piece_index]
        ):
            piece += self.blocks[piece_index][offset]

        return piece

    def remove_piece(
        self,
        piece_index
    ):

        if piece_index in self.blocks:
            del self.blocks[piece_index]