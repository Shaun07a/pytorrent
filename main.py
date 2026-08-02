import asyncio

from torrent.parser import TorrentParser
from torrent.peer_id import PeerID
from torrent.tracker import TrackerClient
from torrent.peer_parser import PeerParser
from torrent.verifier import PieceVerifier
from torrent.peer_manager import PeerManager


async def main():

    # ----------------------------
    # Parse Torrent
    # ----------------------------

    parser = TorrentParser(
        "sample_torrents/sample.torrent"
    )

    torrent = parser.parse()

    # ----------------------------
    # Test Piece Verification
    # ----------------------------

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

    # ----------------------------
    # Piece Manager
    # ----------------------------

    from torrent.piece_manager import PieceManager

    piece_manager = PieceManager(torrent)

    print("Total Pieces:", piece_manager.total_pieces)
    print("Progress   :", piece_manager.progress())
    print()

    # ----------------------------
    # Tracker
    # ----------------------------

    peer_id = PeerID.generate()

    tracker = TrackerClient(
        torrent,
        peer_id
    )

    response = await tracker.announce()

    if response is None:
        print("Could not contact tracker.")
        return

    print("\nTracker Keys:")

    for key in response:
        print(key)

    print()

    print("Peer Bytes Length:", len(response[b"peers"]))

    # ----------------------------
    # Parse Peers
    # ----------------------------

    peers = PeerParser.parse(
        response[b"peers"]
    )

    #
    # LOCAL TESTING ONLY
    # Replace your own public IP with localhost
    #
    MY_PUBLIC_IP = "14.194.135.206"

    for peer in peers:
        if peer.ip == MY_PUBLIC_IP:
            print(
                f"Replacing {peer.ip} with localhost"
            )
            peer.ip = "127.0.0.1"

    print(f"\nFound {len(peers)} peers")

    for peer in peers:
        print(peer)

    if not peers:
        print("No peers found.")
        return

    # ----------------------------
    # Start Download
    # ----------------------------

    manager = PeerManager(
        peers,
        torrent,
        peer_id
    )

    await manager.start()

    # ----------------------------
    # Tracker Response
    # ----------------------------

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