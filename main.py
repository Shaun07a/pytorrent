import asyncio

from torrent.parser import TorrentParser
from torrent.peer_id import PeerID
from torrent.tracker import TrackerClient


async def main():
    parser = TorrentParser(
        "sample_torrents/ubuntu-26.04-desktop-amd64.iso.torrent"
    )

    torrent = parser.parse()

    peer_id = PeerID.generate()

    tracker = TrackerClient(torrent, peer_id)

    response = await tracker.announce()

    print(response)


if __name__ == "__main__":
    asyncio.run(main())