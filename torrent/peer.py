import asyncio
import struct

from torrent.handshake import Handshake
from torrent.models import Peer, TorrentMeta
from torrent.messages import Interested, Message, MESSAGE_NAMES
from torrent.messages import Request



class PeerConnection:

    def __init__(
        self,
        peer: Peer,
        torrent: TorrentMeta,
        peer_id: bytes
    ):
        self.peer = peer
        self.torrent = torrent
        self.peer_id = peer_id

        self.reader = None
        self.writer = None

    async def connect(self):

        print(f"Connecting to {self.peer.ip}:{self.peer.port}")

        self.reader, self.writer = await asyncio.open_connection(
            self.peer.ip,
            self.peer.port
        )

        print("Connected!")

    async def send_handshake(self):

        handshake = Handshake(
            self.torrent.info_hash,
            self.peer_id
        )

        self.writer.write(handshake.encode())

        await self.writer.drain()

        print("Handshake sent")

    async def receive_handshake(self):

        response = await self.reader.readexactly(68)

        decoded = Handshake.decode(response)

        print("\nPeer Handshake")
        print("----------------------------")
        print("Protocol :", decoded["protocol"])
        print("Peer ID  :", decoded["peer_id"])
        print("Info Hash:", decoded["info_hash"].hex())

        if decoded["info_hash"] != self.torrent.info_hash:
            raise ValueError("Peer returned the wrong torrent!")

        return decoded

    async def handshake(self):

        await self.connect()

        await self.send_handshake()

        await self.receive_handshake()

        await self.send_interested()

        await self.send_request()

        while True:

            try:
                message = await asyncio.wait_for(
                    self.receive_message(),
                    timeout=10
                )

            except asyncio.TimeoutError:
                print("Timed out waiting for peer.")
                break

            except asyncio.IncompleteReadError:
                print("Peer closed the connection.")
                break

            if message is None:
                continue

            print("\nPeer Message")
            print("----------------------------")
            print("Type    :", MESSAGE_NAMES.get(message.message_id, "Unknown"))
            print("Payload :", len(message.payload), "bytes")

        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def receive_message(self):

        # Read the 4-byte message length
        length_bytes = await self.reader.readexactly(4)

        length = struct.unpack(">I", length_bytes)[0]

        # KeepAlive message
        if length == 0:
            print("Received KeepAlive")
            return None

        # Read the remaining bytes
        message_bytes = await self.reader.readexactly(length)

        # Decode the complete message
        message = Message.decode(length_bytes + message_bytes)

        return message

    async def send_interested(self):

        message = Interested()

        self.writer.write(message.encode())

        await self.writer.drain()

        print("Interested message sent")

    async def send_request(self):

        request = Request(
            index=0,
            begin=0,
            length=16384
        )

        self.writer.write(request.encode())

        await self.writer.drain()

        print("Requested Piece 0 (first block)")