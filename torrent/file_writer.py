import os


class FileWriter:

    def __init__(self, torrent):

        self.torrent = torrent

        self.filename = torrent.name

        # Create an empty file of the correct size
        with open(self.filename, "wb") as file:
            file.truncate(torrent.length)

    def write_piece(
        self,
        piece_index,
        data
    ):

        offset = piece_index * self.torrent.piece_length

        with open(self.filename, "r+b") as file:

            file.seek(offset)

            file.write(data)

        print(
            f"Wrote Piece {piece_index} "
            f"({len(data)} bytes)"
        )