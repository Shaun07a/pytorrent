from dataclasses import dataclass
import struct

# Message IDs
CHOKE = 0
UNCHOKE = 1
INTERESTED = 2
NOT_INTERESTED = 3
HAVE = 4
BITFIELD = 5
REQUEST = 6
PIECE = 7
CANCEL = 8


@dataclass
class Message:
    message_id: int
    payload: bytes

    def encode(self) -> bytes:
        length = 1 + len(self.payload)

        return (
            struct.pack(">I", length)
            + bytes([self.message_id])
            + self.payload
        )

    @classmethod
    def decode(cls, data: bytes):

        if len(data) < 5:
            raise ValueError("Incomplete message")

        length = struct.unpack(">I", data[:4])[0]

        if length == 0:
            return None

        message_id = data[4]
        payload = data[5:4 + length]

        return cls(message_id, payload)


class Interested(Message):
    def __init__(self):
        super().__init__(
            message_id=INTERESTED,
            payload=b""
        )


MESSAGE_NAMES = {
    CHOKE: "Choke",
    UNCHOKE: "Unchoke",
    INTERESTED: "Interested",
    NOT_INTERESTED: "Not Interested",
    HAVE: "Have",
    BITFIELD: "Bitfield",
    REQUEST: "Request",
    PIECE: "Piece",
    CANCEL: "Cancel",
}