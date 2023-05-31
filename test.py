import asyncio


async def loop1():
    while True:
        # 循环1的逻辑
        print("Loop 1")
        await asyncio.sleep(1)


async def loop2():
    while True:
        # 循环2的逻辑
        print("Loop 2")
        await asyncio.sleep(1)

# 创建两个异步任务
task1 = loop1()
task2 = loop2()

# 使用 asyncio.gather() 同时运行两个任务


async def main():
    await asyncio.gather(task1, task2)

asyncio.run(main())
