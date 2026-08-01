import asyncio

from torrent import tracker
from torrent.parser import TorrentParser
from torrent.peer_id import PeerID
from torrent.tracker import TrackerClient
from torrent.peer_parser import PeerParser
from torrent.peer import PeerConnection
from torrent.verifier import PieceVerifier


async def main():
    parser = TorrentParser(
        "sample_torrents/ubuntu-26.04-desktop-amd64.iso.torrent"
    )

    torrent = parser.parse()

    dummy_piece = b"Hello Torrent"

    result = PieceVerifier.verify(
        dummy_piece,
        torrent.pieces[0]
    )

    print("Verification:", result)

    print()

    print("First Piece Hash")

    print(torrent.pieces[0].hex())

    print()

    from torrent.piece_manager import PieceManager

    manager = PieceManager(torrent)

    print()

    print("Total Pieces:", manager.total_pieces)

    print("Progress   :", manager.progress())

    print()

    peer_id = PeerID.generate()

    tracker = TrackerClient(torrent, peer_id)

    response = await tracker.announce()

    if response is None:
            print("Could not contact tracker.")
            return

    peers = PeerParser.parse(response[b"peers"])

    print(f"Found {len(peers)} peers")

    for peer in peers[:10]:
        print(peer)

    if not peers:
        print("No peers found.")
        return

    connected = False

    for peer in peers:

        print(f"\nTrying peer {peer.ip}:{peer.port}")

        connection = PeerConnection(
            peer,
            torrent,
            peer_id
        )

        try:
            await connection.handshake()
            connected = True
            break

        except Exception as e:
            print(f"Failed: {e}")

    if not connected:
        print("\nCould not establish a usable peer connection.")

    print("\nTracker Response:\n")

    for key, value in response.items():
        print(f"{key} -> {type(value)}")

        if isinstance(value, bytes):
            print(f"Length: {len(value)} bytes")
        else:
            print(value)

        print()



if __name__ == "__main__":
    asyncio.run(main())