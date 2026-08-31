BLOCK_SIZE = 16 * 1024


class BlockManager:

    def __init__(self, torrent):

        self.torrent = torrent

        self.requested = set()
        self.completed = set()

    def piece_length(self, piece):

        if piece == len(self.torrent.pieces) - 1:
            return (
                self.torrent.length
                - piece * self.torrent.piece_length
            )

        return self.torrent.piece_length

    def next_request(self):

        for piece in range(len(self.torrent.pieces)):

            length = self.piece_length(piece)

            for begin in range(0, length, BLOCK_SIZE):

                block_length = min(
                    BLOCK_SIZE,
                    length - begin
                )

                block = (piece, begin)

                if (
                    block not in self.requested
                    and block not in self.completed
                ):

                    self.requested.add(block)

                    return (
                        piece,
                        begin,
                        block_length
                    )

        return None

    def mark_completed(self, piece, begin):

        block = (piece, begin)

        self.completed.add(block)
        self.requested.discard(block)

    def is_piece_complete(self, piece):

        length = self.piece_length(piece)

        for begin in range(0, length, BLOCK_SIZE):

            if (piece, begin) not in self.completed:
                return False

        return True

    def is_complete(self):

        return len(self.completed) == sum(
            (
                self.piece_length(i) + BLOCK_SIZE - 1
            ) // BLOCK_SIZE
            for i in range(len(self.torrent.pieces))
        )