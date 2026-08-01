import asyncio

from torrent.handshake import Handshake
from torrent.models import Peer, TorrentMeta


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