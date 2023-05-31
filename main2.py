# -*- coding: utf-8 -*-
import asyncio
import random
import subprocess
import logging
import os
import threading
from dotenv import load_dotenv, find_dotenv
# import deque to store the message
from collections import deque
import time

import blivedm
from chat import send, llm
from utils.subtitle import *

"""
初始化
"""
log_path = os.getenv("LOG_PATH")
message_record_path = os.getenv("MESSAGE_RECORD_PATH")
query_message = 0
# initial double-end queue
dq_danmaku = deque(maxlen=20)
dq_gift = deque()
dq_superchat = deque()

is_Speaking = False
tts_text = ""
log_text = ""

"""
log setting
"""
logging.basicConfig(filename=log_path, level=logging.INFO)


# 直播间ID的取值看直播间URL
TEST_ROOM_IDS = [
    5007346
    # 21792294
]


async def main():
    # await run_single_client()
    await asyncio.gather(run_multi_clients(), preparation())


async def run_single_client():
    """
    演示监听一个直播间
    """
    room_id = TEST_ROOM_IDS[0]
    # 如果SSL验证失败就把ssl设为False，B站真的有过忘续证书的情况
    client = blivedm.BLiveClient(room_id, ssl=True)
    handler = MyHandler()
    client.add_handler(handler)

    client.start()
    try:
        # 演示5秒后停止
        # await asyncio.sleep(5)
        # client.stop()

        client.join()
    finally:
        client.stop_and_close()


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
    global dq_danmaku, dq_gift, dq_superchat

    # [message] heartbeat
    async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        print(f'[{client.room_id}] 当前人气值：{message.popularity}')
        logging.info(f'[{client.room_id}] 当前人气值：{message.popularity}')

    # [message] danmaku 弹幕
    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        print(f'[{client.room_id}] {message.uname}：{message.msg}')
        if len(message.msg) < 3:
            return
        dq_danmaku.append(message)
        print(dq_danmaku)

    # [message] gift 礼物
    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）')
        dq_gift.append(message)

    # [message] guard 上舰
    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购买{message.gift_name}')
        dq_gift.append(message)

    # [message] super chat 付费留言
    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        print(
            f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')
        dq_superchat.append(message)


async def preparation():
    global is_Speaking, dq_danmaku, dq_gift, dq_superchat

    while True:
        if len(dq_superchat) != 0:
            superchat_answer(dq_superchat.popleft())
            asyncio.sleep(1)
            continue
        elif len(dq_gift) != 0:
            thanks(dq_gift.popleft())
            asyncio.sleep(1)
            continue
        elif len(dq_danmaku) != 0:
            danmaku_answer(dq_danmaku.popleft())
            asyncio.sleep(1)
            continue


def thanks(message):
    global tts_text, log_text
    if type(message) == blivedm.models.GiftMessage:
        tts_text = f"感谢{message.uname}赠送的{message.num}个{message.gift_name}，谢谢大冤种的支持"
        log_text = f"GIFT: [{message.uname}]: 赠送{message.num}个{message.gift_name}"
    elif type(message) == blivedm.models.GuardBuyMessage:
        tts_text = f"感谢{message.username}购买的{message.gift_name}，谢谢老板愿意上我的贼船"
        log_text = f"GUARD: [{message.username}]: 购买{message.gift_name}"
    tts(tts_text)
    with open(message_record_path, "a", encoding="utf-8") as f:
        f.write(log_text)


def superchat_answer(message):
    global tts_text, log_text
    response = llm(message=message.message)
    tts_text = f"感谢{message.uname}老板的superchat，{message.uname}说，{message.message},{response}"
    log_text = f"SUPERCHAT: [¥{message.price}{message.uname}]: {message.message}\n[AI回复]: {response}\n"
    tts(tts_text)
    with open(message_record_path, "a", encoding="utf-8") as f:
        f.write(log_text)


def danmaku_answer(message):
    global tts_text, log_text
    if (len(message.msg) < 3):
        return
    response = llm(message.msg)
    tts_text = f"观众{message.uname}说：{message.msg}。{response}"
    log_text = f"DANMU: [弹幕提问{message.uname}]: {message.msg}\n[AI回复]: {response}\n"
    tts(tts_text)
    with open(message_record_path, "a", encoding="utf-8") as f:
        f.write(log_text)


def tts(text):
    global is_Speaking

    generate_subtitle(text)
    time.sleep(1)

    command = f'edge-playback --voice zh-CN-XiaoyiNeural --text "{text}"'
    subprocess.run(command, shell=True)

    time.sleep(1)
    with open("output.txt", "w") as f:
        f.truncate(0)
    with open("chat.txt", "w") as f:
        f.truncate(0)


"""voice函数进行文本转语音

Keyword arguments:
message -- 弹幕信息，包括心跳、普通弹幕、礼物、上舰、醒目留言
Return: None
"""


def voice(message):
    if type(message) == blivedm.models.DanmakuMessage:
        if (len(message.msg) < 3):
            return
        response = llm(message.msg)
        tts_full_message = f"观众{message.uname}说：{message.msg}。{response}"
        record_message = f"DANMU: [弹幕提问{message.uname}]: {message.msg}\n[AI回复]: {response}\n"
    elif type(message) == blivedm.models.GiftMessage:
        tts_full_message = f"感谢{message.uname}赠送的{message.num}个{message.gift_name}，谢谢大冤种的支持"
        record_message = f"GIFT: [{message.uname}]: 赠送{message.num}个{message.gift_name}"
    elif type(message) == blivedm.models.GuardBuyMessage:
        tts_full_message = f"感谢{message.username}购买的{message.gift_name}，谢谢老板愿意上我的贼船"
        record_message = f"GUARD: [{message.username}]: 购买{message.gift_name}"
    elif type(message) == blivedm.models.SuperChatMessage:
        response = llm(message.message)
        tts_full_message = f"感谢{message.uname}老板的superchat，{message.uname}说，{message.message},{response}"
        record_message = f"SUPERCHAT: [¥{message.price}{message.uname}]: {message.message}\n[AI回复]: {response}\n"

        # response = send(user_message)
    print(record_message)
    command = f'edge-playback --voice zh-CN-XiaoyiNeural --text "{tts_full_message}"'
    subprocess.run(command, shell=True)

    # 对话记录写入文件
    with open(message_record_path, "a", encoding="utf-8") as f:
        f.write(record_message)


if __name__ == '__main__':
    asyncio.run(main())
