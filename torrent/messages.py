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

    def __init__(self, message_id, payload=b""):
        self.message_id = message_id
        self.payload = payload

    def encode(self):

        length = len(self.payload) + 1

        return (
            struct.pack(">I", length)
            + bytes([self.message_id])
            + self.payload
        )

    @classmethod
    def decode(cls, data):

        length = struct.unpack(">I", data[:4])[0]

        if length == 0:
            return None

        message_id = data[4]

        payload = data[5:]

        mapping = {
            CHOKE: Choke,
            UNCHOKE: Unchoke,
            INTERESTED: Interested,
            NOT_INTERESTED: NotInterested,
            HAVE: Have,
            BITFIELD: Bitfield,
            REQUEST: Request,
            PIECE: Piece,
            CANCEL: Cancel,
        }

        message_class = mapping.get(message_id, Message)

        return message_class(payload)


class Choke(Message):
    def __init__(self, payload=b""):
        super().__init__(CHOKE, payload)


class Unchoke(Message):
    def __init__(self, payload=b""):
        super().__init__(UNCHOKE, payload)


class Interested(Message):
    def __init__(self):
        super().__init__(INTERESTED)


class NotInterested(Message):
    def __init__(self):
        super().__init__(NOT_INTERESTED)


class Have(Message):
    def __init__(self, payload):
        super().__init__(HAVE, payload)


class Bitfield(Message):
    def __init__(self, payload):
        super().__init__(BITFIELD, payload)


class Cancel(Message):
    def __init__(self, payload):
        super().__init__(CANCEL, payload)

class Interested(Message):
    def __init__(self):
        super().__init__(
            message_id=INTERESTED,
            payload=b""
        )

class Request(Message):

    def __init__(self, index, begin, length):

        payload = struct.pack(
            ">III",
            index,
            begin,
            length
        )

        super().__init__(REQUEST, payload)

class Piece(Message):

    def __init__(self, payload):

        super().__init__(PIECE, payload)

        self.index = struct.unpack(">I", payload[:4])[0]

        self.begin = struct.unpack(">I", payload[4:8])[0]

        self.block = payload[8:]


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