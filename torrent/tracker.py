import asyncio
from socket import timeout

import aiohttp

from urllib.parse import quote_from_bytes

from torrent.bencoding import BencodeDecoder


class TrackerClient:
    def __init__(self, torrent, peer_id):
        self.torrent = torrent
        self.peer_id = peer_id
        self.port = 6881

    def build_url(self):
        params = (
            f"info_hash={quote_from_bytes(self.torrent.info_hash)}"
            f"&peer_id={quote_from_bytes(self.peer_id)}"
            f"&port={self.port}"
            f"&uploaded=0"
            f"&downloaded=0"
            f"&left={self.torrent.length}"
            f"&compact=1"
        )

        return f"{self.torrent.announce}?{params}"

    async def announce(self):
        url = self.build_url()

        print("Tracker URL:")
        print(url)

        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                print("Connecting to tracker...")

                async with session.get(
                    url,
                    ssl=True
                ) as response:

                    print("Connected!")

                    print("HTTP Status:", response.status)

                    data = await response.read()

                    print("Downloaded response.")

                    print("HTTP Status:", response.status)

                    data = await response.read()

            except asyncio.TimeoutError:
                print("Tracker request timed out.")
                return None

            except aiohttp.ClientError as e:
                print(f"Tracker error: {e}")
                return None

        decoder = BencodeDecoder(data)

        return decoder.decode()