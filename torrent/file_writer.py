import os


class FileWriter:

    def __init__(self, torrent):

        self.torrent = torrent

        download_dir = "downloads"

        os.makedirs(download_dir, exist_ok=True)

        self.filename = os.path.join(
            download_dir,
            torrent.name
        )

        if not os.path.exists(self.filename):

            with open(self.filename, "wb") as file:
                file.truncate(torrent.length)

            print(f"Created download file:\n{self.filename}")

        else:

            print(f"Using existing download file:\n{self.filename}")

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