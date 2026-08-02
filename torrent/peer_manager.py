import asyncio

from torrent.peer import PeerConnection
from torrent.piece_manager import PieceManager
from torrent.block_manager import BlockManager
from torrent.file_writer import FileWriter


class PeerManager:

    def __init__(
        self,
        peers,
        torrent,
        peer_id
    ):
        self.peers = peers
        self.torrent = torrent
        self.peer_id = peer_id

        # Shared across all peers
        self.piece_manager = PieceManager(torrent)
        self.block_manager = BlockManager(torrent)
        self.file_writer = FileWriter(torrent)

    async def start(self):

        if not self.peers:
            print("No peers available.")
            return

        tasks = []

        for peer in self.peers[:20]:

            connection = PeerConnection(
                peer,
                self.torrent,
                self.peer_id,
                self.piece_manager,
                self.block_manager,
                self.file_writer
            )

            tasks.append(
                asyncio.create_task(
                    connection.handshake()
                )
            )

        await asyncio.gather(
            *tasks,
            return_exceptions=True
        )