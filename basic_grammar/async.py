import asyncio
from time import time
//定义携程函数
async def upload():
    //Await只能调用携程函数
    await asyncio.sleep(2)

async def download():
    await asyncio.sleep(2)

async def main():
    //将所有事件放入循环中
    await asyncio.gather(upload(),download())

if __name__ == "__main__":
    start = time()
    /
    asyncio.run(main())
    end = time()
    print(end - start)
