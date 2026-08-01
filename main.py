import asyncio

from torrent.parser import TorrentParser
from torrent.peer_id import PeerID
from torrent.tracker import TrackerClient
from torrent.peer_parser import PeerParser
from torrent.handshake import Handshake
from torrent.peer import PeerConnection


async def main():
    parser = TorrentParser(
        "sample_torrents/ubuntu-26.04-desktop-amd64.iso.torrent"
    )

    torrent = parser.parse()

    peer_id = PeerID.generate()

    tracker = TrackerClient(torrent, peer_id)

    response = await tracker.announce()

    peers = PeerParser.parse(response[b"peers"])

    print(f"Found {len(peers)} peers")

    for peer in peers[:10]:
        print(peer)

    if peers:

        connection = PeerConnection(
        peers[0],
        torrent,
        peer_id
    )

    try:
        await connection.handshake()
    except Exception as e:
        print(f"Peer connection failed: {e}")

    else:
        print("No peers found.")

    print("\nTracker Response:\n")

    for key, value in response.items():
        print(f"{key} -> {type(value)}")

        if isinstance(value, bytes):
            print(f"Length: {len(value)} bytes")
        else:
            print(value)

        print()

    # -------- Handshake Test --------

    handshake = Handshake(
        torrent.info_hash,
        peer_id
    )

    packet = handshake.encode()

    print("Handshake Length:", len(packet))
    print(packet)


if __name__ == "__main__":
    asyncio.run(main())