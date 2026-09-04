import asyncio

from torrent.parser import TorrentParser
from torrent.peer_id import PeerID
from torrent.tracker import TrackerClient
from torrent.peer_parser import PeerParser
from torrent.verifier import PieceVerifier
from torrent.peer_manager import PeerManager

# ---------------------------------------------------
# Set to True when testing with your own qBittorrent
# Set to False when downloading public torrents
# ---------------------------------------------------
LOCAL_TESTING = True


async def main():

    # ----------------------------
    # Parse Torrent
    # ----------------------------

    parser = TorrentParser(
        "sample_torrents/large_sample.torrent"
    )

    torrent = parser.parse()

    print("Announce URL :", torrent.announce)
    print("Info Hash    :", torrent.info_hash.hex())
    print()

    # ----------------------------
    # Verify Piece Hash Example
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
    # Piece Information
    # ----------------------------

    from torrent.piece_manager import PieceManager

    piece_manager = PieceManager(torrent)

    print("Total Pieces:", piece_manager.total_pieces)

    download_path = "downloads/large_sample.txt"

    piece_manager.scan_existing_file(
        download_path
    )

    print(
        "Progress   :",
        piece_manager.progress()
    )

    print()
    # ----------------------------
    # Contact Tracker
    # ----------------------------

    peer_id = PeerID.generate()

    tracker = TrackerClient(
        torrent,
        peer_id,
        piece_manager
    )

    response = await tracker.announce(
    event="started"
    )

    if response is None:
        print("Could not contact tracker.")
        return

    print("\nTracker Keys:")

    for key in response:
        print(key)

    print()

    print(
        "Peer Bytes Length:",
        len(response[b"peers"])
    )

    # ----------------------------
    # Parse Peers
    # ----------------------------

    peers = PeerParser.parse(
        response[b"peers"]
    )

    # ---------------------------------------------------
    # Local Testing
    # ---------------------------------------------------

    if LOCAL_TESTING:

        MY_PUBLIC_IP = "182.72.39.9"   # update this if it changes

        print("\nLOCAL TEST MODE ENABLED\n")

        for peer in peers:

            if peer.ip == MY_PUBLIC_IP:

                print(f"Replacing {peer.ip} with localhost")

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

    if piece_manager.is_complete():

        print("\nTorrent already completely downloaded.")
        print("No peer connections required.")

        return

    manager = PeerManager(
        peers,
        torrent,
        peer_id,
        piece_manager,
        tracker
    )

    await manager.start()

    # ----------------------------
    # Tracker Statistics
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