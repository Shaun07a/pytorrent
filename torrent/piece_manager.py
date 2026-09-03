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

        actual_size = os.path.getsize(filename)

        print(f"Existing file size: {actual_size} bytes")
        print(f"Expected file size: {self.torrent.length} bytes")

        with open(filename, "rb") as file:

            for index in range(self.total_pieces):

                piece_length = self.torrent.piece_length

                # Last piece can be smaller
                if index == self.total_pieces - 1:
                    piece_length = (
                        self.torrent.length
                        - index * self.torrent.piece_length
                    )

                offset = index * self.torrent.piece_length

                file.seek(offset)

                piece_data = file.read(piece_length)

                # Piece is incomplete
                if len(piece_data) != piece_length:

                    print(
                        f"Piece {index} incomplete "
                        f"({len(piece_data)}/{piece_length} bytes)."
                    )

                    continue

                # Verify piece hash
                if PieceVerifier.verify(
                    piece_data,
                    self.torrent.pieces[index]
                ):

                    self.downloaded.add(index)

                    print(
                        f"Piece {index} already complete and verified."
                    )

                else:

                    print(
                        f"Piece {index} verification FAILED."
                    )

        print(
            f"\nResume scan: "
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

    def downloaded_bytes(self):

        total = 0

        for piece in self.downloaded:

            if piece == self.total_pieces - 1:
                length = (
                    self.torrent.length
                    - piece * self.torrent.piece_length
                )
            else:
                length = self.torrent.piece_length

            total += length

        return total


    def remaining_bytes(self):

        return self.torrent.length - self.downloaded_bytes()