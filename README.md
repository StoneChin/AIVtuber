# AIVtuber
## 进度
- [x] 获取bilibili直播间弹幕等信息
- [x] 连接语言模型进行对话
- [x] 使用tts实现文本转语音
- [x] 连接Vtube studio
- [x] 数据集获取
- [x] 模型微调
- [x] 礼物感谢单独展示｜问题回答
- [x] 对话subtitle展示 
- [x] 屏蔽词功能
- [x] 直播测试
- [ ] 代码补充
- [ ] 产出整理（代码、数据集、模型）
- [ ] 完善文档

## 关联项目
* **获取bilibili弹幕**: [blivedm](https://github.com/xfgryujk/blivedm)
* **Text-to-Speech**: [edge-tts](https://github.com/rany2/edge-tts)
* **Chat**: [ChatGLM](https://github.com/THUDM/ChatGLM-6B) ｜ [ChatGPT](https://platform.openai.com/docs/api-reference/authentication)
* **Filter**：[wordfilter](https://github.com/dariusk/wordfilter)

## 使用说明

### 1. 下载并进入文件夹
    ```sh
    git clone https://github.com/StoneChin/AIVtuber
    cd AIVtuber
    ```
### 2. 安装依赖
    ```sh
    pip install -r requirements.txt
    ```
### 3. 配置环境变量
    ```sh
    cp .env.example .env
    ```
    进入 **.env**文件中配置对应的变量
    **OPENAI_API_KEY**中填入你的openai api key
### 4. 配置直播信息
   进入**main.py**文件中的**TEST_ROOM_IDS**填入相关直播间号，可以参考bilibili直播间url的末尾数字，目前只会回答弹幕字数>=8的问题，可以在main.py中进行调整，后续会更改到系统变量中调整
### 5. 运行
    ```sh
    python main3.py
    ```
