from torrent.bencoding import BencodeDecoder
from torrent.models import TorrentMeta
from torrent.encoder import BencodeEncoder
from torrent.utils import sha1


class TorrentParser:
    def __init__(self, filename: str):
        self.filename = filename

    def parse(self):
        with open(self.filename, "rb") as file:
            data = file.read()

        decoder = BencodeDecoder(data)
        torrent = decoder.decode()

        info = torrent[b"info"]

        encoder = BencodeEncoder()

        encoded_info = encoder.encode(info)

        info_hash = sha1(encoded_info)

        

        return TorrentMeta(
            announce=torrent[b"announce"].decode(),
            name=info[b"name"].decode(),
            length=info[b"length"],
            piece_length=info[b"piece length"],
            pieces=info[b"pieces"],
            info_hash=info_hash,
        )