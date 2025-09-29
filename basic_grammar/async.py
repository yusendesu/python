import asyncio
from time import time

async def upload():
    await asyncio.sleep(2)

async def download():
    await asyncio.sleep(2)

async def main():
    await asyncio.gather(upload(),download())

if __name__ == "__main__":
    start = time()
    asyncio.run(main())
    end = time()
    print(end - start)