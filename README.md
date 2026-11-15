---
title: Yui Hirasawa Voice Clone (平泽唯专属声音克隆引擎)
emoji: 🎸
colorFrom: pink
colorTo: yellow
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
license: mit
short_description: 基于 GPT-SoVITS v2Pro 的平泽唯专属声音克隆，走软萌可爱风，提供极速响应与 RESTful API！
---

# 🎸 平泽唯 (Hirasawa Yui) GPT-SoVITS 专属声音克隆引擎

> **放学后茶会 (After School Tea Time - HTT)** 吉他手兼主唱平泽唯专属语音合成引擎！  
> 基于 **GPT-SoVITS v2Pro** 高精度音色克隆，针对极速响应与全平台低延迟做了深度优化。

---

## ✨ 核心特性

- 🍰 **极致可爱风界面**：樱丘女子高中轻音部草莓蛋糕粉白软萌视觉，细腻卡片微交互。
- ⚡ **超低延迟响应**：预热常驻内存加载，Prompt 语义特征单例缓存，输入即可极速出声。
- 🎭 **黄金三性格一键切换**：
  - 🌸 **日常元气 / 开朗少女**：语速轻快，朝气蓬勃。
  - 🍮 **呆萌慵懒 / 地板撒娇**：软绵绵鼻音，夏天在木地板上打滚的撒娇拖音。
  - ⚡ **兴奋高亢 / 满血鸡血**：眼睛放光，庆祝与热血高能呼喊。
- 🌐 **多语言无缝切换**：支持纯日语、中文跨语言克隆、纯英文及中英日多语言混合朗读。
- 🛠️ **全开放 REST API**：同时暴露标准 FastAPI 与 Gradio Client 接口，方便第三方应用或 Bot 快速调用。

---

## 🔌 API 调用指南

### 1. HTTP GET 快速试听
```bash
curl -X GET "https://huggingface.co/spaces/YOUR_USERNAME/yui-voice-clone/api/tts?text=むぎちゃん！今日のおやつはケーキなの！？&prompt=energetic&lang=ja" --output yui.wav
```

### 2. HTTP POST 结构化请求
```bash
curl -X POST "https://huggingface.co/spaces/YOUR_USERNAME/yui-voice-clone/api/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "忧，今天的点心是什么呀？我肚子好饿哦！",
    "prompt": "lazy",
    "lang": "zh",
    "speed": 1.0
  }' --output yui_lazy.wav
```

### 3. Gradio Client (Python SDK)
```python
from gradio_client import Client

client = Client("https://huggingface.co/spaces/YOUR_USERNAME/yui-voice-clone")
result = client.predict(
    text="ギー太、今日もいい音出してるよ！",
    prompt_type="日常元气 / 开朗少女",
    language="ja",
    speed=1.0,
    api_name="/predict"
)
print("生成的音频路径:", result)
```
