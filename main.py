# -*- coding: utf-8 -*-
import asyncio
import random
import subprocess
import logging
import os

import blivedm
from chat import send, llm

"""
初始化
"""
LOG_PATH = 'out.log'
MESSAGE_RECORD_PATH = './message.txt'

"""
日志记录
"""
logging.basicConfig(filename=LOG_PATH, level=logging.INFO)


# 直播间ID的取值看直播间URL
TEST_ROOM_IDS = [
    5007346
]


async def main():
    await run_single_client()
    await run_multi_clients()


async def run_single_client():
    """
    演示监听一个直播间
    """
    room_id = random.choice(TEST_ROOM_IDS)
    # 如果SSL验证失败就把ssl设为False，B站真的有过忘续证书的情况
    client = blivedm.BLiveClient(room_id, ssl=True)
    handler = MyHandler()
    client.add_handler(handler)

    client.start()
    try:
        # 演示5秒后停止
        await asyncio.sleep(5)
        client.stop()

        await client.join()
    finally:
        await client.stop_and_close()


async def run_multi_clients():
    """
    演示同时监听多个直播间
    """
    clients = [blivedm.BLiveClient(room_id) for room_id in TEST_ROOM_IDS]
    handler = MyHandler()
    for client in clients:
        client.add_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(
            client.join() for client in clients
        ))
    finally:
        await asyncio.gather(*(
            client.stop_and_close() for client in clients
        ))


class MyHandler(blivedm.BaseHandler):
    async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        print(f'[{client.room_id}] 当前人气值：{message.popularity}')
        logging.info(f'[{client.room_id}] 当前人气值：{message.popularity}')

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        print(f'[{client.room_id}] {message.uname}：{message.msg}')
        await voice(message.uname, message.msg, 0)

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）')

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购ß买{message.gift_name}')

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        print(
            f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')


def voice(user_name, user_message, num):
    # response = send(user_message)
    response = llm(user_message)
    print(response)

    tts_full_message = f"观众{user_name}问：{user_message}。{response}"
    record_message = f"[弹幕提问{user_name}]: {user_message}\n[AI回复{user_name}]: {response}\n"
    print(record_message)

    command = f'edge-playback --voice zh-CN-XiaoyiNeural --text "{tts_full_message}"'
    subprocess.run(command, shell=True)

    if os.path.exists(MESSAGE_RECORD_PATH):
        # 对话文件存在将对话Append入文件
        with open(MESSAGE_RECORD_PATH, "a", encoding="utf-8") as f:
            f.write(record_message)
    else:
        # 对话文件不存在则新建文件
        with open(MESSAGE_RECORD_PATH, mode='w', encoding='utf-8') as f:
            f.write(record_message)


if __name__ == '__main__':
    asyncio.run(main())
