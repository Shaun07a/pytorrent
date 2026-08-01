from dataclasses import dataclass


@dataclass
class Handshake:
    info_hash: bytes
    peer_id: bytes

    PROTOCOL = b"BitTorrent protocol"
    PSTRLEN = len(PROTOCOL)
    RESERVED = b"\x00" * 8

    def encode(self) -> bytes:
        return (
            bytes([self.PSTRLEN])
            + self.PROTOCOL
            + self.RESERVED
            + self.info_hash
            + self.peer_id
        )