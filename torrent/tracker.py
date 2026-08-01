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
            f"&event=started"
            f"&numwant=50"
        )

        return f"{self.torrent.announce}?{params}"

    async def announce(self):

        url = self.build_url()

        timeout = aiohttp.ClientTimeout(total=30)

        for attempt in range(3):

            try:

                print(f"\nConnecting to tracker (Attempt {attempt + 1}/3)...")

                async with aiohttp.ClientSession(timeout=timeout) as session:

                    async with session.get(url) as response:

                        print("HTTP Status:", response.status)

                        data = await response.read()

                        decoder = BencodeDecoder(data)

                        return decoder.decode()

            except asyncio.TimeoutError:

                print("Tracker timed out.")

            except aiohttp.ClientError as e:

                print(e)

        return None