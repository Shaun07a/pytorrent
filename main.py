import asyncio

from torrent.parser import TorrentParser
from torrent.peer_id import PeerID
from torrent.tracker import TrackerClient
from torrent.peer_parser import PeerParser


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