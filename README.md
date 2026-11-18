---
title: K-ON! 放学后茶会全员声音克隆引擎 (After School Tea Time Voice Clone)
emoji: 🎸
colorFrom: pink
colorTo: yellow
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
license: mit
short_description: 基于 GPT-SoVITS v2Pro (v3) 的轻音少女 7 角色纯净声音克隆与 REST API！
---

<div align="center">

<p>
  <img src="imgs/yui_small.png" alt="平泽唯" width="76" style="border-radius: 50%; margin: 0 4px;" />
  <img src="imgs/mio_small.png" alt="秋山澪" width="76" style="border-radius: 50%; margin: 0 4px;" />
  <img src="imgs/ritsu_small.png" alt="田井中律" width="76" style="border-radius: 50%; margin: 0 4px;" />
  <img src="imgs/tsumugi_small.png" alt="琴吹紬" width="76" style="border-radius: 50%; margin: 0 4px;" />
  <img src="imgs/azusa_small.png" alt="中野梓" width="76" style="border-radius: 50%; margin: 0 4px;" />
  <img src="imgs/ui_small.png" alt="平泽忧" width="76" style="border-radius: 50%; margin: 0 4px;" />
  <img src="imgs/nodoka_small.png" alt="真锅和" width="76" style="border-radius: 50%; margin: 0 4px;" />
</p>

# 🎸 《轻音少女》放学后茶会 7 角色声音克隆引擎 (v3 Pure)

> **After School Tea Time (HTT)** 全员的音色引擎！
> 基于 **GPT-SoVITS v2Pro** + PSP《放課後ライブ！！》游戏内提取纯净干音 **v3 重切分精校数据集** 微调打造。

[![GitHub Release](https://img.shields.io/badge/Release-v3.0.0-ff5e87?style=flat-square&logo=github)](https://github.com/nanguaguag/yui-voice-clone/releases/tag/v3.0.0)
[![Hugging Face Space](https://img.shields.io/badge/🤗%20Space-yui--voice--clone-ffaa2a?style=flat-square)](https://huggingface.co/spaces/nanguagua/yui-voice-clone)

</div>

---

## ✨ 核心特性

- **v3 高精重切分与校对语料**：采用 `-40dB / min_length=800ms` 精准静音切分 + `whisper-large-v3`（`vad_filter=False` + K-ON! 专有名词热词注入）逐条校对，彻底剔除机械报时与多句拼盘，消除句首漏词与尾音半音节截断。
- **全员 7 角色独立微调权重（`v3.0.0`）**：
  - 🍓 **平泽唯 (`yui`)**：集成 5 项情绪预设（元气活力 / 日常开朗 / 呆萌撒娇 / 兴奋高亢 / 惊喜期待）
  - 💙 **秋山澪 (`mio`)** · 💛 **田井中律 (`ritsu`)** · 🍰 **琴吹紬 (`tsumugi`)** · 🐱 **中野梓 (`azusa`)** · 🧡 **平泽忧 (`ui`)** · 📕 **真锅和 (`nodoka`)**
  - 每位角色均配备 3.5~5.5s 单句完整、纯净无杂音默认参考音频，并支持上传自定义参考音频自由克隆。
- **中/日/英跨语种 & `[JA]` 混读路由**：支持 `[JA]平沢唯[/JA]` 等标签在中文语句中直通日语原声专有名词读音，内置 K-ON! 专属读音校准（`ギー太`、`軽音部`、`平沢憂` 等）与音素边界防死循环守卫。
- **广播级声学后处理**：11.5kHz 2阶 Butterworth 温和低通滤除高频电音毛刺 + 20ms 自适应软噪声门，输出清润自然人声。

---

## 👥 支持角色与 v3 模型清单

| 代号 | 角色 | 担当 / 特质 | v3 SoVITS 权重 | v3 GPT 权重 |
| :--- | :--- | :--- | :--- | :--- |
| `yui` | **平泽唯** | 吉他手 & 主唱| `yui_pure_v3_e10_s200.pth` | `yui_pure_v3-e15.ckpt` |
| `mio` | **秋山澪** | 贝斯手 & 主唱 | `mio_pure_v3_e10_s160.pth` | `mio_pure_v3-e15.ckpt` |
| `ritsu` | **田井中律** | 鼓手 & 部长 | `ritsu_pure_v3_e10_s180.pth` | `ritsu_pure_v3-e15.ckpt` |
| `tsumugi` | **琴吹紬** | 键盘手| `tsumugi_pure_v3_e10_s200.pth` | `tsumugi_pure_v3-e15.ckpt` |
| `azusa` | **中野梓** | 吉他手| `azusa_pure_v3_e10_s190.pth` | `azusa_pure_v3-e15.ckpt` |
| `ui` | **平泽忧** | 唯的妹妹| `ui_pure_v3_e10_s220.pth` | `ui_pure_v3-e15.ckpt` |
| `nodoka` | **真锅和** | 学生会长| `nodoka_pure_v3_e10_s230.pth` | `nodoka_pure_v3-e15.ckpt` |

---

## 🔌 RESTful API 调用指南

在线服务地址：`https://nanguagua-yui-voice-clone.hf.space`

### 1. 健康检查与角色列表

```bash
curl -s "https://nanguagua-yui-voice-clone.hf.space/health"
curl -s "https://nanguagua-yui-voice-clone.hf.space/api/characters"
```

### 2. HTTP GET 快速合成音频

```bash
curl -G "https://nanguagua-yui-voice-clone.hf.space/api/tts" \
  --data-urlencode "character=mio" \
  --data-urlencode "text=恥ずかしいから、あまり見ないでよ…！でも、ベースの練習は付き合ってあげる。" \
  --data-urlencode "lang=ja" \
  --output mio_v3.wav
```

### 3. HTTP POST 结构化请求

```bash
curl -X POST "https://nanguagua-yui-voice-clone.hf.space/api/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "character": "yui",
    "text": "大家好，我是[JA]平沢唯[/JA]！今天的点心是草莓蛋糕哦~",
    "prompt": "元气活力",
    "lang": "auto",
    "speed": 1.0
  }' --output yui_v3.wav
```

### 4. Gradio Client (Python SDK)

```python
from gradio_client import Client

client = Client("nanguagua/yui-voice-clone")
result = client.predict(
    char_id="azusa",
    text="唯先輩、お茶ばっかり飲んでないで、ちゃんとギターの練習してください！",
    prompt_choice="🎵 默认",
    lang="日文 (Japanese)",
    speed=1.0,
    top_k=15,
    top_p=0.8,
    temperature=0.8,
    api_name="/predict"
)
print("生成的音频路径:", result)
```
