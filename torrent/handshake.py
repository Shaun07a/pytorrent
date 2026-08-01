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

    @classmethod
    def decode(cls, data: bytes):

        if len(data) != 68:
            raise ValueError("Invalid handshake length")

        pstrlen = data[0]

        protocol = data[1:1 + pstrlen]

        reserved = data[20:28]

        info_hash = data[28:48]

        peer_id = data[48:68]

        return {
            "protocol": protocol.decode(),
            "reserved": reserved,
            "info_hash": info_hash,
            "peer_id": peer_id.decode(errors="replace")
        }