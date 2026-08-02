BLOCK_SIZE = 16 * 1024      # 16384 bytes


class BlockManager:

    def __init__(self, torrent):

        self.torrent = torrent

        self.current_piece = 0

        self.current_offset = 0

    def next_request(self):

        piece_length = self.torrent.piece_length

        # Last piece can be smaller
        if self.current_piece == len(self.torrent.pieces) - 1:

            remaining = (
                self.torrent.length -
                self.current_piece * piece_length
            )

            piece_length = remaining

        if self.current_offset >= piece_length:

            self.current_piece += 1
            self.current_offset = 0

            if self.current_piece >= len(self.torrent.pieces):
                return None

            piece_length = self.torrent.piece_length

        request = (
            self.current_piece,
            self.current_offset,
            min(
                BLOCK_SIZE,
                piece_length - self.current_offset
            )
        )

        self.current_offset += BLOCK_SIZE

        return request