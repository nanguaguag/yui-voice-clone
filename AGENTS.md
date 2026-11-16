# 🤖 AGENTS.md - 平泽唯 (Hirasawa Yui) GPT-SoVITS 项目协作与运维指南

> **适用对象**: 接入本项目的 AI Assistant、自动化 Agent 及工程师。  
> **核心原则**: 在对代码、脚本或云服务做任何修改之前，**必须严格阅读并遵守本文件中的全部红线约束与工程规范**。

---

## 🎯 一、 项目使命与定位

- **项目名称**: 平泽唯 (Hirasawa Yui - 《轻音少女》K-ON!) 专属全离线/云端声音克隆引擎
- **底层架构**: 基于 **GPT-SoVITS v2Pro**，具备完整的跨语言自然表达能力与情绪风格注入。
- **运行模式**:
  1. **Mac 本地 Apple Silicon 全离线极速推理**: 3~4 秒极速出声，模型常驻内存。
  2. **云端高可用免费服务 (Hugging Face Space + ZeroGPU)**: 绑定 GitHub 开源仓库，集成 K-ON! 放学后茶会主题可爱风 UI，暴露极速 RESTful API。

---

## 🚨 二、 不可逾越的绝对红线约束 (Strict Guardrails)

在执行任何命令或生成代码时，任何 Agent 必须无条件执行以下规则：

1. **移动硬盘数据隔离（零污染系统盘）**:
   - 工作根目录为 `/Volumes/My PSSD/projects/FLUX3`；
   - 所有的依赖库、Python 虚拟环境（`GPT-SoVITS/venv`）、下载的官方预训练模型（`chinese-roberta`, `hubert`, `sv`, `lid` 等）及生成的音频输出，**必须严格保留在移动硬盘内**，严禁在 `~`、`/tmp`、`/usr/local` 等系统路径下载或存放模型大文件。
2. **本地环境强制 CPU 设备绑定**:
   - macOS 14.4+ 上 PyTorch 对 Apple Silicon MPS（Metal Performance Shaders）的线性切片算子存在原生内核 Crash（`MPSNDArray arrayViewWithShape:strides: unrecognized selector`）。
   - **本地代码必须显式指定 `os.environ["device"] = "cpu"`**。M1 Pro 8核在 CPU 模式下单句耗时仅 3~4 秒，稳定且快，严禁切换为 `mps`。
3. **UID 与用户身份**:
   - 用户 UID 为 `D5 4F 0E D9`。
4. **Git 与 GitHub 提交署名严格约束**:
   - 远程仓库必须统一署名为维护者：
     ```bash
     git config user.name "nanguaguag"
     git config user.email "2022181640245@stu.scu.edu.cn"
     ```
   - 任何提交、标签或推送严禁出现其他本地系统用户名（如 `huzongyao`）。

---

## 🗺️ 三、 核心架构与工程地图

```text
/Volumes/My PSSD/projects/FLUX3/
├── scripts/
│   ├── test_infer.py              # ⭐ 本地推理主入口 (CLI)，支持 --prompt, --lang, --play
│   ├── batch_test_samples.py      # 边缘 Case 与 30 条中日英台词基准压测脚本
│   └── remote_slice_and_asr.py    # 云端切片与标注辅助脚本
├── weights/                       # 微调模型权重 (v2Pro 架构)
│   ├── GPT_weights_v2Pro/yui-e15.ckpt          # 最佳自回归韵律模型 (Epoch 15)
│   └── SoVITS_weights_v2Pro/yui_e12_s840.pth   # 最佳声学解码模型 (Epoch 12, Step 840)
├── data/tts/
│   ├── yui_character_prompts.json # 3 大黄金语气切片 (日常元气 / 呆萌撒娇 / 演出兴奋)
│   ├── yui_test_sentences.txt     # 30 条评测台词覆盖边缘 Case
│   └── yui_slices/                # 唯酱高质量无损人声参考切片库
├── GPT-SoVITS/                    # 本地运行环境与源码
│   ├── venv/                      # 专属 Python 3.11 虚拟环境 (已固化所有依赖与 nltk 数据)
│   └── GPT_SoVITS/
│       ├── pretrained_models/     # 本地离线底模 (Hubert, RoBERTa, SV, fast_langdetect)
│       ├── sv.py                  # ⭐ 声纹特征提取 (已修复 Half 精度算子缺失)
│       └── eres2net/kaldi.py      # ⭐ Kaldi 频域滤波器 (已加固 float 兜底转换)
├── deploy_space/                  # ⭐ Hugging Face Space 云端部署包工程
│   ├── app.py                     # Gradio 4.44.1 可爱风 UI + FastAPI 原生路由 + ZeroGPU 适配
│   ├── download_models.py         # 自动从 GitHub Release v1.0.0 与 Meta/HF 拉取全量底模
│   ├── requirements.txt           # 经过严格依赖冲突解耦的 Python 包版本清单
│   └── packages.txt               # Debian 底层系统库 (ffmpeg, libsox-dev 等)
├── PROJECT_HANDOVER.md            # 项目全量架构与详细交接技术文档
└── AGENTS.md                      # 本文档 (AI Agent 指南)
```

---

## ⚙️ 四、 关键技术流水线与修复机制 (必须遵守的代码契约)

### 1. 文本预处理与 K-ON! 专属分词校准
在调用 `get_tts_wav` 之前，任何接口必须统一经过 `clean_and_normalize_text` 处理：
- **专有名词强制平假名映射**：
  - `ギー太` ➡️ `ギータ`（防止 OpenJTalk 将汉字「太」误读为男性本名「ふとし / futoshi」）
  - `軽音部` / `kon部` / `k-on部` ➡️ `けいおんぶ`（防止切词为地名「音部(otobe)」读成「kee-otobe」）
  - `平沢憂` / `憂ちゃん` / `憂` ➡️ `うい`（防止按通用大词典读作「yuu」或吞音为「u」）
- **标点符号安全合并（防死循环）**：
  - `[？?]{2,} -> ？`，`[！!]{2,} -> ！`，`[！？?!]{2,} -> ！`，`[。\.]{2,} -> 。`
  - 严禁向模型输入未归一化的连续标点，否则自回归注意力振荡，丢失 EOS 导致 24 秒空白静音或跑满 1500 步超时。

### 2. 神经声码器高频去电音与底噪门限 (`enhance_voice_clarity`)
所有生成的音频统一经过轻量级声学后处理（耗时仅 30ms）：
- **11.5kHz 2阶 Butterworth 低通滤波**：切除声码器在 10kHz~16kHz 产生的周期性高频金属伪影与机械毛刺，保留人声清润甜美。
- **20ms 自适应软噪声门**：在字句停顿、叹气和尾部静音段自动压低底噪，消除电路感背景蜂鸣。

### 3. 音频输出数值规整化规范
- `inference_webui.py` 原生已返回 `(audio * 32767).astype(np.int16)`；
- 外层函数接收后**绝不可二次乘以 32767**（会导致模 65536 整型溢出回绕，造成炸耳白噪音）；
- 统一规范：在解包时先除以 32767.0 还原为 `float32 [-1.0, 1.0]`，做 0.95 峰值归一化，向 Gradio 传递 `float32`，向 API 输出 `PCM_16` WAV。

---

## 🛠️ 五、 常用开发与运维命令速查

### 1. 本地极速 CLI 推理
```bash
cd "/Volumes/My PSSD/projects/FLUX3"
# 必须使用指定 venv 解释器
./GPT-SoVITS/venv/bin/python ./scripts/test_infer.py --prompt energetic --text "むぎちゃん！今日のおやつ、もしかしてショートケーキなの！？" --play
```

### 2. 抽样运行边缘 Case 压测
```bash
./GPT-SoVITS/venv/bin/python ./scripts/batch_test_samples.py
```

### 3. 同步并部署云端 Space (GitHub + Hugging Face)
```bash
cd "/Volumes/My PSSD/projects/FLUX3/deploy_space"
git add .
git commit -m "fix/feat: <描述变更>"
# 双向推送 (必须确保作者为 nanguaguag)
git push origin main
git push hf main
```

---

## 📌 六、 云端在线服务资产清单

- **GitHub 仓库**: [https://github.com/nanguaguag/yui-voice-clone](https://github.com/nanguaguag/yui-voice-clone)
- **Hugging Face Space 主页**: [https://huggingface.co/spaces/nanguagua/yui-voice-clone](https://huggingface.co/spaces/nanguagua/yui-voice-clone)
- **Space 专属全屏 Web URL**: [https://nanguagua-yui-voice-clone.hf.space](https://nanguagua-yui-voice-clone.hf.space)
- **API 端点**:
  - `GET https://nanguagua-yui-voice-clone.hf.space/api/tts?text=...&prompt=energetic`
  - `POST https://nanguagua-yui-voice-clone.hf.space/api/tts`
  - `POST https://nanguagua-yui-voice-clone.hf.space/gradio_api/call/predict`
