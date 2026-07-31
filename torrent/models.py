from dataclasses import dataclass


@dataclass
class TorrentMeta:
    announce: str
    name: str
    length: int
    piece_length: int
    pieces: bytes
    info_hash: bytes

    @property
    def piece_hashes(self):
        return [
            self.pieces[i:i + 20]
            for i in range(0, len(self.pieces), 20)
        ]

    @property
    def info_hash_hex(self):
        return self.info_hash.hex()