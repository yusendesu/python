import asyncio
from time import time

# 定义协程函数
async def upload():
    # await只能调用可等待对象（如协程）
    await asyncio.sleep(2)

async def download():
    await asyncio.sleep(2)

async def main():
    # 并发执行多个协程
    await asyncio.gather(upload(), download())

if __name__ == "__main__":
    start = time()
    # 运行事件循环
    asyncio.run(main())
    end = time()
    print(end - start)
