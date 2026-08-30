import os

from torrent.verifier import PieceVerifier


class PieceManager:

    def __init__(self, torrent):

        self.torrent = torrent

        self.total_pieces = len(torrent.pieces)

        self.downloaded = set()
        self.requested = set()

    def scan_existing_file(self, filename):

        if not os.path.exists(filename):
            print("No existing download found.")
            return

        print("\nChecking existing download...")

        with open(filename, "rb") as file:

            for index in range(self.total_pieces):

                piece_length = self.torrent.piece_length

                # Last piece can be smaller
                if index == self.total_pieces - 1:
                    piece_length = (
                        self.torrent.length
                        - index * self.torrent.piece_length
                    )

                file.seek(index * self.torrent.piece_length)

                piece_data = file.read(piece_length)

                # Don't consider incomplete pieces
                if len(piece_data) != piece_length:
                    continue

                if PieceVerifier.verify(
                    piece_data,
                    self.torrent.pieces[index]
                ):
                    self.downloaded.add(index)

                    print(
                        f"Piece {index} already complete and verified."
                    )

        print(
            f"Resume scan: "
            f"{len(self.downloaded)}/{self.total_pieces} pieces complete."
        )

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

    def is_downloaded(self, index):

        return index in self.downloaded

    def is_complete(self):

        return len(self.downloaded) == self.total_pieces

    def progress(self):

        return (
            len(self.downloaded),
            self.total_pieces
        )