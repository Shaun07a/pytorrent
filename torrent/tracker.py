import asyncio
import aiohttp

from urllib.parse import quote_from_bytes

from torrent.bencoding import BencodeDecoder


class TrackerClient:

    def __init__(self, torrent, peer_id, piece_manager):

        self.torrent = torrent
        self.peer_id = peer_id
        self.piece_manager = piece_manager

        self.port = 6881

    def build_url(self):

        downloaded = self.piece_manager.downloaded_bytes()
        left = self.piece_manager.remaining_bytes()

        params = (
            f"info_hash={quote_from_bytes(self.torrent.info_hash)}"
            f"&peer_id={quote_from_bytes(self.peer_id)}"
            f"&port={self.port}"
            f"&uploaded=0"
            f"&downloaded={downloaded}"
            f"&left={left}"
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

                print(
                    f"\nConnecting to tracker "
                    f"(Attempt {attempt + 1}/3)..."
                )

                print("Tracker URL:")
                print(url)
                print()

                async with aiohttp.ClientSession(
                    timeout=timeout
                ) as session:

                    async with session.get(url) as response:

                        print("HTTP Status:", response.status)

                        data = await response.read()

                        decoder = BencodeDecoder(data)

                        return decoder.decode()

            except asyncio.TimeoutError:

                print("Tracker timed out.")

            except aiohttp.ClientError as e:

                print(
                    f"Client Error: "
                    f"{type(e).__name__}"
                )

                print(e)

        return None