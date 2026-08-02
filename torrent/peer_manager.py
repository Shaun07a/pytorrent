import asyncio

from torrent.peer import PeerConnection


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

    async def start(self):

        if not self.peers:
            print("No peers available.")
            return

        tasks = []

        for peer in self.peers[:20]:

            connection = PeerConnection(
                peer,
                self.torrent,
                self.peer_id
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