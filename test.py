#!/usr/bin/env python3

"""
Basic example of edge_tts usage.
"""

import asyncio
from playsound import playsound
import edge_tts


TEXT = "最近在搞一个基于python的语音聊天机器人，因为采用的百度AI平台中的语音合成功能，输出的MP3的格式，需要用到Python播放MP3的功能，但是在网上找了好久，都没有找到合适的解决方案，原来比较好的mp3Play库只支持Python2，比较多种方式后，目前采用play_mp3，为了方便以后使用，现将结果记录如下："
VOICE = "zh-CN-shaanxi-XiaoniNeural"
OUTPUT_FILE = "test.mp3"


async def _main() -> None:
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)
    await playsound(OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(_main())
