class PieceManager:

    def __init__(self, torrent):

        self.torrent = torrent

        self.total_pieces = len(
            torrent.piece_hashes
        )

        self.downloaded = set()

        self.requested = set()

    def next_piece(self):

        for index in range(self.total_pieces):

            if index not in self.downloaded and \
            index not in self.requested:

                self.requested.add(index)

                return index

        return None

    def mark_downloaded(self, index):

        self.downloaded.add(index)

        self.requested.discard(index)

    def progress(self):

        return (
            len(self.downloaded),
            self.total_pieces
        )