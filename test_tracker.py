import asyncio
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://tracker.opentrackr.org:1337/announce") as r:
            print(r.status)
            print(await r.text())

asyncio.run(main())