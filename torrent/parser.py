from torrent.bencoding import BencodeDecoder
from torrent.models import TorrentMeta


class TorrentParser:
    def __init__(self, filename: str):
        self.filename = filename

    def parse(self):
        with open(self.filename, "rb") as file:
            data = file.read()

        decoder = BencodeDecoder(data)
        torrent = decoder.decode()

        info = torrent[b"info"]

        return TorrentMeta(
            announce=torrent[b"announce"].decode(),
            name=info[b"name"].decode(),
            length=info[b"length"],
            piece_length=info[b"piece length"],
            pieces=info[b"pieces"],
        )