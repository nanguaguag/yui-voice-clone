#!/usr/bin/env python3
"""
🎸 平泽唯 (Hirasawa Yui) GPT-SoVITS 专属声音克隆云服务 (Hugging Face Space)
- 可爱风 K-ON! 放学后茶会视觉体验
- 常驻内存单例 + Prompt 缓存极速推理
- 暴露标准 Gradio 接口与 RESTful FastAPI 接口 (/api/tts)
"""

import spaces
import os
import sys
import re
import time
import json
import base64
import io
import numpy as np
import soundfile as sf
import torch
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
import gradio as gr

# 解决 Gradio Client 与 Pydantic v2 schema 中 additionalProperties: bool 的解析冲突
try:
    import gradio_client.utils as client_utils
    _orig_json_schema_to_python_type = client_utils._json_schema_to_python_type
    def safe_json_schema_to_python_type(schema, defs=None):
        if not isinstance(schema, dict):
            return "typing.Any"
        return _orig_json_schema_to_python_type(schema, defs)
    client_utils._json_schema_to_python_type = safe_json_schema_to_python_type
except Exception:
    pass

# 解决 Gradio 4.44.1 与 Starlette 0.38+ 在 TemplateResponse 参数签名上的不兼容
try:
    import starlette.templating
    _orig_TemplateResponse = starlette.templating.Jinja2Templates.TemplateResponse
    def safe_TemplateResponse(self, *args, **kwargs):
        if args and isinstance(args[0], str):
            name = args[0]
            context = args[1] if len(args) > 1 else kwargs.get("context", {})
            request = context.get("request") if isinstance(context, dict) else kwargs.get("request")
            rest_args = args[2:]
            return _orig_TemplateResponse(
                self, request, name, context, *rest_args,
                **{k: v for k, v in kwargs.items() if k not in ("request", "name", "context")}
            )
        return _orig_TemplateResponse(self, *args, **kwargs)
    starlette.templating.Jinja2Templates.TemplateResponse = safe_TemplateResponse
except Exception:
    pass

# 1. 基础路径与环境变量配置
APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["no_proxy"] = "localhost,127.0.0.1,0.0.0.0"
os.environ["NO_PROXY"] = "localhost,127.0.0.1,0.0.0.0"
os.environ["version"] = "v2Pro"
if "device" not in os.environ:
    os.environ["device"] = "cpu"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

SOVITS_ROOT = os.path.join(APP_DIR, "GPT-SoVITS")
if os.path.exists(SOVITS_ROOT):
    sys.path.insert(0, SOVITS_ROOT)
    sys.path.insert(0, os.path.join(SOVITS_ROOT, "GPT_SoVITS"))
    os.chdir(SOVITS_ROOT)

WEIGHTS_DIR = os.path.join(APP_DIR, "weights")
DEFAULT_GPT = os.path.join(WEIGHTS_DIR, "GPT_weights_v2Pro/yui-e15.ckpt")
DEFAULT_SOVITS = os.path.join(WEIGHTS_DIR, "SoVITS_weights_v2Pro/yui_e12_s840.pth")

# 确保预训练底模与权重存在
from download_models import ensure_models
ensure_models(APP_DIR)

os.environ["gpt_path"] = DEFAULT_GPT
os.environ["sovits_path"] = DEFAULT_SOVITS

import inference_webui as infer

# 2. 参考切片与提示词配置

PROMPTS_FILE = os.path.join(APP_DIR, "data/tts/yui_character_prompts.json")
if os.path.exists(PROMPTS_FILE):
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        prompts_cfg = json.load(f)["prompts"]
else:
    prompts_cfg = [
        {
            "id": "prompt_energetic",
            "name": "日常元气 / 开朗少女",
            "audio_path": "data/tts/yui_slices/yui_00002.wav",
            "prompt_text": "文化系のクラブもよくわかんないし",
            "prompt_language": "ja"
        },
        {
            "id": "prompt_lazy_cute",
            "name": "呆萌慵懒 / 地板撒娇",
            "audio_path": "data/tts/yui_slices/yui_00035.wav",
            "prompt_text": "夏は床の上を転がってばかりいるの",
            "prompt_language": "ja"
        },
        {
            "id": "prompt_excited",
            "name": "兴奋高亢 / 满血鸡血",
            "audio_path": "data/tts/yui_slices/yui_00136.wav",
            "prompt_text": "軽音部のみんなも協力してくれるんだ!",
            "prompt_language": "ja"
        }
    ]

prompts_map = {p["id"]: p for p in prompts_cfg}
prompts_name_to_id = {p["name"]: p["id"] for p in prompts_cfg}

# 3. 全局常驻单例加载与预热
print("=" * 65)
print("🍓 正在初始化平泽唯专属声音克隆引擎 (常驻内存)...")
t0 = time.time()
try:
    next(infer.change_sovits_weights(DEFAULT_SOVITS))
except (StopIteration, TypeError):
    pass
infer.change_gpt_weights(DEFAULT_GPT)
print(f"🎉 唯酱神经网络加载完毕！耗时: {time.time() - t0:.2f}s")
print("=" * 65)

# 4. 文本清洗与语言映射中间件
def clean_and_normalize_text(text: str) -> str:
    """消除复合问叹号防自回归死循环，规范化省略号与波浪号"""
    text = text.strip()
    text = re.sub(r"[！？?!]{2,}", "！", text)
    text = re.sub(r"[。\.]{2,}", "。", text)
    text = re.sub(r"[，,、]{2,}", "，", text)
    text = re.sub(r"[~〜]{2,}", "〜", text)
    return text

LANGUAGE_MAP = {
    "ja": "Japanese",
    "zh": "Chinese",
    "en": "English",
    "auto": "Multilingual Mixed",
    "日文 (Japanese)": "Japanese",
    "中文 (Chinese)": "Chinese",
    "英文 (English)": "English",
    "多语种混合 (Multilingual)": "Multilingual Mixed",
}

@spaces.GPU(duration=20)
def generate_yui_speech(
    text: str,
    prompt_key: str = "prompt_energetic",
    language: str = "auto",
    speed: float = 1.0,
    top_k: int = 15,
    top_p: float = 0.8,
    temperature: float = 0.8,
    custom_ref_wav: str = None,
    custom_prompt_text: str = None,
    custom_prompt_lang: str = None
):
    """核心合成函数：支持极速出声与自定义语气注入"""
    text = clean_and_normalize_text(text)
    if not text:
        raise ValueError("合成文本内容不能为空哦！")

    # 1. 确定参考音频与提示文本
    if custom_ref_wav and os.path.exists(custom_ref_wav) and custom_prompt_text:
        ref_wav = custom_ref_wav
        ref_text = clean_and_normalize_text(custom_prompt_text)
        ref_lang = LANGUAGE_MAP.get(custom_prompt_lang, "Japanese")
    else:
        preset = prompts_map.get(prompt_key, prompts_cfg[0])
        ref_wav = os.path.join(APP_DIR, preset["audio_path"])
        ref_text = preset["prompt_text"]
        ref_lang = "Japanese"

    target_lang = LANGUAGE_MAP.get(language, "Multilingual Mixed")

    # 2. 推理生成
    t_start = time.time()
    gen = infer.get_tts_wav(
        ref_wav_path=ref_wav,
        prompt_text=ref_text,
        prompt_language=ref_lang,
        text=text,
        text_language=target_lang,
        how_to_cut=infer.i18n("凑四句一切"),
        top_k=top_k,
        top_p=top_p,
        temperature=temperature,
        speed=speed,
    )
    sr, audio_data = next(gen)
    infer_cost = time.time() - t_start

    # 3. 严格音频转换与峰值规整化到 [-0.95, 0.95] float32
    if isinstance(audio_data, np.ndarray) and len(audio_data) > 0:
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32767.0
        elif audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        max_val = np.abs(audio_data).max()
        if max_val > 1e-4:
            audio_data = (audio_data / max_val * 0.95).astype(np.float32)

    return sr, audio_data, infer_cost

# 5. RESTful API 请求结构体定义
class TTSRequest(BaseModel):
    text: str
    prompt: str = "energetic"  # energetic, lazy, excited
    lang: str = "auto"         # ja, zh, en, auto
    speed: float = 1.0
    top_k: int = 15
    top_p: float = 0.8
    temperature: float = 0.8

# 6. Gradio 可爱风前端页面设计
CUSTOM_CSS = """
/* K-ON! 放学后茶会专属软萌粉黄配色 */
:root {
    --primary-500: #FF7597;
    --primary-600: #E0567B;
    --background-fill-primary: #FFFDF9;
    --block-background-fill: #FFFFFF;
    --border-color-primary: #FFD1DC;
}

body, .gradio-container {
    background: linear-gradient(135deg, #FFF5F7 0%, #FFFDF9 50%, #FFF9E6 100%) !important;
    font-family: 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif !important;
}

.yui-header {
    text-align: center;
    padding: 24px 10px 10px 10px;
    background: rgba(255, 255, 255, 0.7);
    border-radius: 20px;
    margin-bottom: 20px;
    border: 2px solid #FFE4EC;
    box-shadow: 0 8px 24px rgba(255, 117, 151, 0.12);
}

.yui-badge {
    display: inline-block;
    background: linear-gradient(45deg, #FF7597, #FFAA2A);
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 8px;
    box-shadow: 0 4px 10px rgba(255, 117, 151, 0.3);
}

.yui-btn {
    background: linear-gradient(135deg, #FF7597 0%, #FF8EA9 100%) !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 16px !important;
    border: none !important;
    box-shadow: 0 6px 16px rgba(255, 117, 151, 0.35) !important;
    transition: all 0.2s ease !important;
}

.yui-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(255, 117, 151, 0.45) !important;
}

.preset-chip {
    font-size: 12px !important;
    border-radius: 12px !important;
    margin: 2px !important;
}
"""

with gr.Blocks(title="平泽唯 (Hirasawa Yui) 专属声音克隆", css=CUSTOM_CSS) as demo:
    with gr.Column():
        gr.HTML("""
        <div class="yui-header">
            <span class="yui-badge">🎸 放学后茶会 After School Tea Time</span>
            <h1 style="color: #FF5E87; font-size: 28px; margin: 8px 0;">平泽唯 (Hirasawa Yui) 专属声音克隆</h1>
            <p style="color: #7A6A65; font-size: 14px; margin: 0;">
                基于 <b>GPT-SoVITS v2Pro</b> 打造的唯酱高保真音色引擎 | 支持多语气自然对话与极速秒级响应 🍰
            </p>
        </div>
        """)

    with gr.Row():
        with gr.Column(scale=5):
            gr.Markdown("### 🎭 1. 选择唯酱语气风格")
            prompt_radio = gr.Radio(
                choices=[p["name"] for p in prompts_cfg] + ["🎨 自定义提示词与参考音频"],
                value="日常元气 / 开朗少女",
                label="语气预设 (Preset Tone)",
                interactive=True
            )

            with gr.Accordion("🛠️ 自定义声学参考 (上传专属音频 / 提示词)", open=False):
                custom_audio = gr.Audio(label="自定义参考音频 (建议 3~8 秒无杂音人声)", type="filepath")
                custom_text = gr.Textbox(label="参考音频台词 (对应音频中说的话)", placeholder="输入该音频中对应的台词文本...")
                custom_lang = gr.Dropdown(
                    choices=["日文 (Japanese)", "中文 (Chinese)", "英文 (English)"],
                    value="日文 (Japanese)",
                    label="参考音频语言"
                )

            gr.Markdown("### 💬 2. 待合成文本 (支持中 / 日 / 英 / 混杂)")
            text_input = gr.Textbox(
                label="目标台词内容",
                placeholder="在此输入你想让唯酱说的话，例如：むぎちゃん！今日のおやつ、もしかしてショートケーキなの！？",
                lines=4,
                value="むぎちゃん！今日のおやつ、もしかしてショートケーキなの！？"
            )

            with gr.Accordion("🍰 快速点选经典台词 (30 条精选台词一键填入)", open=False):
                with gr.Tab("🇯🇵 日语原汁原味"):
                    gr.Examples(
                        examples=[
                            ["えへへ、憂〜、今日のご飯なに？お腹すいちゃった〜！"],
                            ["ギー太、今日もいい音出してるよ！大好きだよ、ギー太！"],
                            ["暑いよ〜、動きたくないよ〜、誰かアイス持ってきて〜！"],
                            ["むぎちゃん！今日のおやつ、もしかしてショートケーキなの！？"],
                            ["私、ギターもっともっと練習して、武道館でライブするんだから！"]
                        ],
                        inputs=[text_input]
                    )
                with gr.Tab("🇨🇳 中文跨语言克隆"):
                    gr.Examples(
                        examples=[
                            ["早上好呀！今天的天气超级棒，要打起精神来哦！"],
                            ["呐呐，我们先吃点小蛋糕再开始练习嘛，不吃饱哪有力气弹吉他呀！"],
                            ["唔……地板上好凉快啊，我今天就要当一只趴在木地板上的软体动物~"],
                            ["锵锵！快看我的吉太，是不是全世界最帅气的电吉他！"],
                            ["小梓小梓~让我抱一下嘛！就抱五秒钟，吸一口小梓能量！"]
                        ],
                        inputs=[text_input]
                    )
                with gr.Tab("🌐 英语与多语言混杂"):
                    gr.Examples(
                        examples=[
                            ["Hello everyone! Welcome to After School Tea Time! Let's rock!"],
                            ["Wow! This strawberry cake is so delicious! Delicious cake makes me super happy!"],
                            ["Let me see... C chord... D chord... あれ？次はなんだっけ？"],
                            ["Okay! 今天的练习也要加油，Let's go, 各位！"],
                            ["Fun things are always fun! 楽しいことは、やっぱり楽しいね！"]
                        ],
                        inputs=[text_input]
                    )

            with gr.Row():
                lang_select = gr.Dropdown(
                    choices=["多语种混合 (Multilingual)", "日文 (Japanese)", "中文 (Chinese)", "英文 (English)"],
                    value="多语种混合 (Multilingual)",
                    label="朗读语种"
                )
                speed_slider = gr.Slider(minimum=0.6, maximum=1.5, value=1.0, step=0.05, label="语速调节")

            with gr.Accordion("⚙️ 高级模型参数 (可选)", open=False):
                with gr.Row():
                    top_k_slider = gr.Slider(minimum=1, maximum=30, value=15, step=1, label="Top-K")
                    top_p_slider = gr.Slider(minimum=0.1, maximum=1.0, value=0.8, step=0.05, label="Top-P")
                    temp_slider = gr.Slider(minimum=0.1, maximum=1.5, value=0.8, step=0.05, label="Temperature")

            generate_btn = gr.Button("🍓 唯酱，开始发声！ (Generate Speech)", variant="primary", elem_classes=["yui-btn"])

        with gr.Column(scale=4):
            gr.Markdown("### 🎵 3. 语音输出与试听")
            audio_output = gr.Audio(label="生成的人声音频", type="numpy", interactive=False)
            status_box = gr.Textbox(label="⚡ 渲染信息与推理耗时", interactive=False, value="等待点击生成...")

            gr.HTML("""
            <div style="background: white; border-radius: 16px; padding: 16px; margin-top: 15px; border: 1px solid #FFE4EC;">
                <h4 style="color: #FF5E87; margin-top: 0;">🔌 开放 API 接入快速说明</h4>
                <p style="font-size: 13px; color: #666; line-height: 1.6;">
                    本 Space 已自带常驻高性能 REST API，任何客户端均可极速调用：<br>
                    • <b>GET 试听</b>: <code>/api/tts?text=你好&prompt=energetic</code><br>
                    • <b>POST 合成</b>: <code>/api/tts</code> (传参 JSON)<br>
                    • <b>Gradio Client</b>: <code>client.predict(text=..., api_name='/predict')</code>
                </p>
            </div>
            """)

    def on_generate(text, prompt_choice, lang, speed, top_k, top_p, temp, c_audio, c_text, c_lang):
        p_id = prompts_name_to_id.get(prompt_choice, "prompt_energetic")
        t_before = time.time()
        try:
            sr, wav_data, cost = generate_yui_speech(
                text=text,
                prompt_key=p_id,
                language=lang,
                speed=speed,
                top_k=int(top_k),
                top_p=float(top_p),
                temperature=float(temp),
                custom_ref_wav=c_audio,
                custom_prompt_text=c_text,
                custom_prompt_lang=c_lang
            )
            total_cost = time.time() - t_before
            dur = len(wav_data) / sr
            msg = f"🎉 合成成功！模型纯推理: {cost:.2f}s | 端到端总耗时: {total_cost:.2f}s | 音频时长: {dur:.2f}s"
            return (sr, wav_data), msg
        except Exception as e:
            return None, f"❌ 合成失败: {str(e)}"

    generate_btn.click(
        on_generate,
        inputs=[
            text_input, prompt_radio, lang_select, speed_slider,
            top_k_slider, top_p_slider, temp_slider,
            custom_audio, custom_text, custom_lang
        ],
        outputs=[audio_output, status_box],
        api_name="predict"
    )

# 7. 在 Gradio 内置的 FastAPI app 上注册极速 RESTful API 路由
@demo.app.get("/health")
def health():
    return {"status": "ok", "character": "Hirasawa Yui", "model": "GPT-SoVITS v2Pro"}

@demo.app.get("/api/prompts")
def get_prompts():
    return {"prompts": prompts_cfg}

@demo.app.get("/api/tts")
def api_tts_get(
    text: str = Query(..., description="待合成文本内容"),
    prompt: str = Query("energetic", description="语气 (energetic/lazy/excited)"),
    lang: str = Query("auto", description="语言 (ja/zh/en/auto)"),
    speed: float = Query(1.0, description="语速 (0.6 ~ 1.5)")
):
    p_id = f"prompt_{prompt}" if not prompt.startswith("prompt_") else prompt
    if p_id not in prompts_map:
        p_id = "prompt_energetic"
    sr, audio_data, cost = generate_yui_speech(text=text, prompt_key=p_id, language=lang, speed=speed)
    
    buf = io.BytesIO()
    wav_int16 = (np.clip(audio_data, -1.0, 1.0) * 32767.0).astype(np.int16)
    sf.write(buf, wav_int16, sr, format="WAV", subtype="PCM_16")
    buf.seek(0)
    return Response(
        content=buf.read(),
        media_type="audio/wav",
        headers={"X-Infer-Cost": f"{cost:.3f}s", "X-Audio-Sample-Rate": str(sr)}
    )

@demo.app.post("/api/tts")
async def api_tts_post(request: Request):
    try:
        req = await request.json()
    except Exception:
        req = {}
    text = req.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Missing required field: text")
    prompt = req.get("prompt", "energetic")
    lang = req.get("lang", "auto")
    speed = float(req.get("speed", 1.0))
    top_k = int(req.get("top_k", 15))
    top_p = float(req.get("top_p", 1.0))
    temperature = float(req.get("temperature", 1.0))

    p_id = f"prompt_{prompt}" if not prompt.startswith("prompt_") else prompt
    if p_id not in prompts_map:
        p_id = "prompt_energetic"
    sr, audio_data, cost = generate_yui_speech(
        text=text,
        prompt_key=p_id,
        language=lang,
        speed=speed,
        top_k=top_k,
        top_p=top_p,
        temperature=temperature
    )
    buf = io.BytesIO()
    wav_int16 = (np.clip(audio_data, -1.0, 1.0) * 32767.0).astype(np.int16)
    sf.write(buf, wav_int16, sr, format="WAV", subtype="PCM_16")
    buf.seek(0)
    return Response(
        content=buf.read(),
        media_type="audio/wav",
        headers={"X-Infer-Cost": f"{cost:.3f}s", "X-Audio-Sample-Rate": str(sr)}
    )

# 8. 启动应用 (调用 demo.launch 触发 ZeroGPU 探针并激活 Queue)
demo.queue(max_size=20)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False
    )
