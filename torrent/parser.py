from dataclasses import dataclass

from torrent.bencoding import BencodeDecoder


@dataclass
class TorrentMeta:
    announce: str
    name: str
    length: int
    piece_length: int
    pieces: bytes


class TorrentParser:
    def __init__(self, filename: str):
        self.filename = filename

    def parse(self):
        with open(self.filename, "rb") as file:
            data = file.read()

        decoder = BencodeDecoder(data)

        torrent = decoder.decode()

        print("Top-level keys:")
        for key in torrent:
            print(" ", key)

        print("\nInfo dictionary:")
        info = torrent[b"info"]

        for key, value in info.items():
            if key == b"pieces":
                print(f"{key}: <{len(value)} bytes>")
            else:
                print(f"{key}: {value}")