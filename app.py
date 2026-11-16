#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎸 K-ON! 放学后茶会全员声音克隆引擎 (After School Tea Time Voice Clone)
支持角色：平泽唯 (Yui)、秋山澪 (Mio)、田井中律 (Ritsu)、琴吹紬 (Tsumugi)、中野梓 (Azusa)、平泽忧 (Ui)、真锅和 (Nodoka)
集成：动态角色主题配色实时切换、多情绪语气注入、自定义声学克隆、ZeroGPU 适配与极速 RESTful API
"""

import os
import sys
import io
import re
import json
import time
import torch
import numpy as np
import soundfile as sf
import gradio as gr
from fastapi import FastAPI, Response, Request, HTTPException, Query
from pydantic import BaseModel

# 0. ZeroGPU 探针适配
try:
    import spaces
    has_spaces = True
except ImportError:
    has_spaces = False

    class spaces:
        @staticmethod
        def GPU(func):
            return func

# 1. 动态挂载 GPT-SoVITS 源码与环境目录
APP_DIR = os.path.dirname(os.path.abspath(__file__))
SOVITS_ROOT = os.path.join(APP_DIR, "GPT-SoVITS")
if os.path.exists(SOVITS_ROOT):
    sys.path.insert(0, SOVITS_ROOT)
    sys.path.insert(0, os.path.join(SOVITS_ROOT, "GPT_SoVITS"))
    os.chdir(SOVITS_ROOT)

from characters_data import (
    CHARACTERS,
    CHARACTER_CHOICES,
    CHOICE_TO_KEY,
    get_character_theme_css,
    get_character_header_html,
    get_character_todo_html,
)
from download_models import ensure_models, ensure_character_weights

# 确保预训练底模与默认平泽唯微调模型存在
DEFAULT_GPT, DEFAULT_SOVITS = ensure_models(APP_DIR)
os.environ["gpt_path"] = DEFAULT_GPT
os.environ["sovits_path"] = DEFAULT_SOVITS

import inference_webui as infer
import scipy.signal as signal

# 全局常驻当前加载的角色代号 (单例缓存)
CURRENT_LOADED_CHAR = "yui"

print("=" * 65)
print("🍓 正在初始化 K-ON! 放学后茶会声音引擎 (默认加载平泽唯)...")
t0 = time.time()
try:
    next(infer.change_sovits_weights(DEFAULT_SOVITS))
except (StopIteration, TypeError):
    pass
infer.change_gpt_weights(DEFAULT_GPT)
print(f"🎉 神经音色引擎就绪！初始加载耗时: {time.time() - t0:.2f}s")
print("=" * 65)

# 2. 文本清洗与语言映射中间件
K_ON_SPECIAL_WORDS = {
    r"ギー太": "ギータ",
    r"軽音部": "けいおんぶ",
    r"軽音": "けいおん",
    r"[Kk][Oo][Nn]部": "けいおんぶ",
    r"[Kk]-[Oo][Nn]部": "けいおんぶ",
    r"平沢憂": "ひらさわうい",
    r"憂ちゃん": "ういちゃん",
    r"憂": "うい",
    r"律ちゃん": "りっちゃん",
    r"澪ちゃん": "みおちゃん",
    r"紬ちゃん": "むぎちゃん",
    r"梓ちゃん": "あずさちゃん",
}

def clean_and_normalize_text(text: str) -> str:
    """消除复合标点防死循环，校准专有名词读音"""
    text = text.strip()
    for word, target in K_ON_SPECIAL_WORDS.items():
        text = re.sub(word, target, text)
    text = re.sub(r"[？?]{2,}", "？", text)
    text = re.sub(r"[！!]{2,}", "！", text)
    text = re.sub(r"[！？?!]{2,}", "！", text)
    text = re.sub(r"[。\.]{2,}", "。", text)
    text = re.sub(r"[，,、]{2,}", "，", text)
    return text

def enhance_voice_clarity(audio_data: np.ndarray, sr: int) -> np.ndarray:
    """Butterworth 低通滤波切除高频金属毛刺 + 软噪声门消除底噪"""
    if len(audio_data) == 0:
        return audio_data
    nyquist = sr / 2.0
    cutoff = min(11500.0, nyquist - 200.0)
    norm_cutoff = cutoff / nyquist
    b, a = signal.butter(2, norm_cutoff, btype='low', analog=False)
    filtered = signal.filtfilt(b, a, audio_data)

    window_size = int(sr * 0.02)
    stride = int(sr * 0.01)
    if len(filtered) > window_size:
        padded = np.pad(filtered, (0, window_size), mode='reflect')
        energy = np.array([
            np.sqrt(np.mean(padded[i:i + window_size] ** 2))
            for i in range(0, len(filtered), stride)
        ])
        threshold = max(float(np.percentile(energy, 10)) * 1.5, 0.003)
        gain = np.ones(len(filtered), dtype=np.float32)
        for idx, e in enumerate(energy):
            start = idx * stride
            end = min(start + stride, len(filtered))
            if e < threshold:
                gain[start:end] = np.clip(e / threshold, 0.1, 1.0)
        filtered = filtered * gain

    return filtered.astype(np.float32)

LANGUAGE_MAP = {
    "日文 (Japanese)": "Japanese",
    "中文 (Chinese)": "Chinese",
    "英文 (English)": "English",
    "多语种混合 (Multilingual)": "Multilingual Mixed",
    "ja": "Japanese",
    "zh": "Chinese",
    "en": "English",
    "auto": "Multilingual Mixed"
}

def switch_character_model(char_id: str):
    """动态热更当前角色的 SoVITS 和 GPT 权重"""
    global CURRENT_LOADED_CHAR
    char_id = char_id.lower()
    if char_id not in CHARACTERS:
        char_id = "yui"
    if CURRENT_LOADED_CHAR == char_id:
        return

    print(f"🔄 正在热更模型至角色: {CHARACTERS[char_id]['name']}...")
    s_path, g_path = ensure_character_weights(char_id, APP_DIR)
    t_start = time.time()
    try:
        next(infer.change_sovits_weights(s_path))
    except (StopIteration, TypeError):
        pass
    infer.change_gpt_weights(g_path)
    CURRENT_LOADED_CHAR = char_id
    print(f"✅ 模型热更完毕: {char_id} (耗时: {time.time() - t_start:.2f}s)")

# 3. 核心合成函数
@spaces.GPU
def generate_character_speech(
    char_id: str,
    text: str,
    prompt_name: str = "默认",
    language: str = "auto",
    speed: float = 1.0,
    top_k: int = 15,
    top_p: float = 0.8,
    temperature: float = 0.8,
    custom_ref_wav: str = None,
    custom_prompt_text: str = None,
    custom_prompt_lang: str = None
):
    """支持 7 位角色独立声音模型与风格注入的统一语音合成接口"""
    text = clean_and_normalize_text(text)
    if not text:
        raise ValueError("待合成文本内容不能为空哦！")

    char_info = CHARACTERS.get(char_id, CHARACTERS["yui"])
    switch_character_model(char_id)

    # 1. 确定声学参考音频与提示文本
    if custom_ref_wav and os.path.exists(custom_ref_wav) and custom_prompt_text:
        ref_wav = custom_ref_wav
        ref_text = clean_and_normalize_text(custom_prompt_text)
        ref_lang = LANGUAGE_MAP.get(custom_prompt_lang, "Japanese")
    else:
        if char_info["has_presets"]:
            matched = next((p for p in char_info["prompts"] if p["name"] == prompt_name), char_info["prompts"][0])
            ref_wav = os.path.join(APP_DIR, matched["audio_path"])
            ref_text = matched["prompt_text"]
            ref_lang = "Japanese"
        else:
            default_p = char_info["default_prompt"]
            ref_wav = os.path.join(APP_DIR, default_p["audio_path"])
            ref_text = default_p["prompt_text"]
            ref_lang = "Japanese"

    target_lang = LANGUAGE_MAP.get(language, "Multilingual Mixed")

    # 2. 推理渲染
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

    # 3. 后处理与数值归一化
    if isinstance(audio_data, np.ndarray) and len(audio_data) > 0:
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32767.0
        elif audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        audio_data = enhance_voice_clarity(audio_data, sr)
        max_val = np.abs(audio_data).max()
        if max_val > 1e-4:
            audio_data = (audio_data / max_val * 0.95).astype(np.float32)

    return sr, audio_data, infer_cost

# 4. Gradio 动态多主题页面设计
BASE_CSS = """
/* 基础全局字体与排版 */
body, .gradio-container {
    font-family: 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif !important;
    min-height: 100vh;
}
.char-selector-box {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 16px;
    padding: 12px 16px;
    margin-bottom: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
"""

with gr.Blocks(title="K-ON! 放学后茶会全员声音克隆", css=BASE_CSS) as demo:
    # 动态样式与标题容器
    theme_css = gr.HTML(value=get_character_theme_css("yui"))
    header_html = gr.HTML(value=get_character_header_html("yui"))

    # 当前选中的角色 key（隐藏状态变量）
    current_char_state = gr.State(value="yui")

    with gr.Row():
        with gr.Column(scale=5):
            # --- 角色选择器 ---
            with gr.Group(elem_classes=["char-selector-box"]):
                gr.Markdown("### 🎀 1. 点选放学后茶会角色 (选择即切换专属主题配色)")
                char_selector = gr.Radio(
                    choices=CHARACTER_CHOICES,
                    value=CHARACTER_CHOICES[0],
                    label="选择角色 (Character)",
                    interactive=True
                )

            # --- 语气风格选择 ---
            gr.Markdown("### 🎭 2. 语气风格与个性提示")
            todo_notice = gr.HTML(value=get_character_todo_html("yui"))

            initial_prompts = [p["name"] for p in CHARACTERS["yui"]["prompts"]] + ["🎨 自定义参考音频与台词"]
            prompt_radio = gr.Radio(
                choices=initial_prompts,
                value=initial_prompts[0],
                label="语气风格 (Tone Style)",
                interactive=True
            )

            with gr.Accordion("🛠️ 自定义声学参考 (上传专属音频 / 提示词)", open=False):
                custom_audio = gr.Audio(label="自定义参考音频 (建议 3~8 秒无杂音纯净人声)", type="filepath")
                custom_text = gr.Textbox(label="参考音频台词 (对应音频中说的话)", placeholder="输入该音频中对应的台词文本...")
                custom_lang = gr.Dropdown(
                    choices=["日文 (Japanese)", "中文 (Chinese)", "英文 (English)"],
                    value="日文 (Japanese)",
                    label="参考音频语言"
                )

            # --- 待合成文本 ---
            gr.Markdown("### 💬 3. 待合成文本 (支持中 / 日 / 英 / 混杂)")
            text_input = gr.Textbox(
                label="目标台词内容",
                placeholder="在此输入你想让角色说的话...",
                lines=4,
                value=CHARACTERS["yui"]["default_text"]
            )

            # --- 经典台词快速点选 ---
            with gr.Accordion("🍰 快速点选经典台词 (一键填入目标文本)", open=False):
                with gr.Tab("🇯🇵 日语原声台词"):
                    gr.Examples(
                        examples=[
                            ["むぎちゃん！今日のおやつ、もしかしてショートケーキなの！？"],
                            ["恥ずかしいから、あまり見ないでよ…！でも、ベースの練習は付き合ってあげる。"],
                            ["よーし！今日も放課後ティータイムのドラム、気合入れていくぞー！"],
                            ["ふふっ、今日はおいしい紅茶とバームクーヘンをお持ちしましたわ。"],
                            ["唯先輩、お茶ばっかり飲んでないで、ちゃんとギターの練習してください！"],
                            ["お姉ちゃん！朝ご飯できてるよ、遅刻しちゃうから早く起きて！"],
                            ["唯、また生徒会への提出物遅れてるわよ。もう、しっかりしなさい。"]
                        ],
                        inputs=[text_input]
                    )
                with gr.Tab("🇨🇳 中文日常对话"):
                    gr.Examples(
                        examples=[
                            ["早上好呀！今天的天气超级棒，要打起精神来哦！"],
                            ["今天放学后，一定要把那首合奏曲子好好练熟！"],
                            ["吃饱喝足之后再开始练习嘛，这就是放学后茶会的传统呀！"],
                            ["轻音部的各位，今天的红茶和蛋糕都已经准备好啦~"],
                            ["唯前辈！不要再赖在木地板上发呆了啦，很热的！"]
                        ],
                        inputs=[text_input]
                    )
                with gr.Tab("🌐 英语与多语言混杂"):
                    gr.Examples(
                        examples=[
                            ["Hello everyone! Welcome to After School Tea Time! Let's rock!"],
                            ["Wow! This strawberry cake is so delicious! Delicious cake makes me super happy!"],
                            ["Today's rehearsal will be super fun, Let's go, everyone!"]
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

            generate_btn = gr.Button("🍓 让平泽唯发声！ (Generate Speech)", variant="primary", elem_classes=["char-btn"])

        with gr.Column(scale=4):
            gr.Markdown("### 🎵 4. 语音输出与试听")
            audio_output = gr.Audio(label="生成的高保真音频", type="numpy", interactive=False)
            status_box = gr.Textbox(label="⚡ 渲染信息与推理耗时", interactive=False, value="等待点击生成...")

            gr.HTML("""
            <div class="char-card">
                <h4 style="margin-top: 0;" class="char-accent-text">🔌 开放 API 接入说明</h4>
                <p style="font-size: 13px; color: #475569; line-height: 1.6; margin-bottom: 0;">
                    本 Space 已自带常驻高性能 REST API，支持直接指定角色生成：<br>
                    • <b>GET 试听</b>: <code>/api/tts?text=你好&character=mio</code><br>
                    • <b>POST 合成</b>: <code>/api/tts</code> (参数包含 text, character, prompt)<br>
                    • <b>支持角色</b>: <code>yui</code>, <code>mio</code>, <code>ritsu</code>, <code>tsumugi</code>, <code>azusa</code>, <code>ui</code>, <code>nodoka</code>
                </p>
            </div>
            """)

    # --- 角色切换交互回调 ---
    def on_character_change(selected_choice: str):
        char_id = CHOICE_TO_KEY.get(selected_choice, "yui")
        char_info = CHARACTERS[char_id]

        new_css = get_character_theme_css(char_id)
        new_header = get_character_header_html(char_id)
        new_todo = get_character_todo_html(char_id)

        if char_info["has_presets"]:
            new_prompts = [p["name"] for p in char_info["prompts"]] + ["🎨 自定义参考音频与台词"]
            new_prompt_val = new_prompts[0]
        else:
            new_prompts = ["🎵 默认纯净台词语气", "🎨 自定义参考音频与台词"]
            new_prompt_val = new_prompts[0]

        new_btn_label = f"{char_info['avatar']} 让{char_info['short_name']}发声！ (Generate Speech)"
        new_text = char_info["default_text"]

        return (
            char_id,
            new_css,
            new_header,
            new_todo,
            gr.update(choices=new_prompts, value=new_prompt_val),
            new_text,
            gr.update(value=new_btn_label)
        )

    char_selector.change(
        on_character_change,
        inputs=[char_selector],
        outputs=[
            current_char_state,
            theme_css,
            header_html,
            todo_notice,
            prompt_radio,
            text_input,
            generate_btn
        ]
    )

    # --- 点击生成交互回调 ---
    def on_generate(char_id, text, prompt_choice, lang, speed, top_k, top_p, temp, c_audio, c_text, c_lang):
        t_before = time.time()
        try:
            sr, wav_data, cost = generate_character_speech(
                char_id=char_id,
                text=text,
                prompt_name=prompt_choice,
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
            c_name = CHARACTERS.get(char_id, CHARACTERS["yui"])["name"]
            msg = f"🎉 [{c_name}] 合成成功！模型推理: {cost:.2f}s | 总耗时: {total_cost:.2f}s | 音频时长: {dur:.2f}s"
            return (sr, wav_data), msg
        except Exception as e:
            return None, f"❌ 合成失败: {str(e)}"

    generate_btn.click(
        on_generate,
        inputs=[
            current_char_state,
            text_input, prompt_radio, lang_select, speed_slider,
            top_k_slider, top_p_slider, temp_slider,
            custom_audio, custom_text, custom_lang
        ],
        outputs=[audio_output, status_box],
        api_name="predict"
    )

# 5. RESTful API 路由定义
@demo.app.get("/health")
def health():
    return {
        "status": "ok",
        "current_character": CURRENT_LOADED_CHAR,
        "supported_characters": list(CHARACTERS.keys()),
        "model": "GPT-SoVITS v2Pro"
    }

@demo.app.get("/api/characters")
def api_characters():
    return {
        "characters": [
            {
                "id": c["id"],
                "name": c["name"],
                "short_name": c["short_name"],
                "role": c["role"],
                "has_presets": c["has_presets"]
            }
            for c in CHARACTERS.values()
        ]
    }

@demo.app.get("/api/tts")
def api_tts_get(
    text: str = Query(..., description="待合成文本内容"),
    character: str = Query("yui", description="角色代号 (yui/mio/ritsu/tsumugi/azusa/ui/nodoka)"),
    prompt: str = Query("默认", description="语气预设名称"),
    lang: str = Query("auto", description="语言 (ja/zh/en/auto)"),
    speed: float = Query(1.0, description="语速 (0.6 ~ 1.5)")
):
    char_id = character.lower()
    if char_id not in CHARACTERS:
        char_id = "yui"
    sr, audio_data, cost = generate_character_speech(
        char_id=char_id,
        text=text,
        prompt_name=prompt,
        language=lang,
        speed=speed
    )
    buf = io.BytesIO()
    wav_int16 = (np.clip(audio_data, -1.0, 1.0) * 32767.0).astype(np.int16)
    sf.write(buf, wav_int16, sr, format="WAV", subtype="PCM_16")
    buf.seek(0)
    return Response(
        content=buf.read(),
        media_type="audio/wav",
        headers={"X-Infer-Cost": f"{cost:.3f}s", "X-Audio-Sample-Rate": str(sr), "X-Character": char_id}
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
    character = req.get("character", "yui").lower()
    prompt = req.get("prompt", "默认")
    lang = req.get("lang", "auto")
    speed = float(req.get("speed", 1.0))
    top_k = int(req.get("top_k", 15))
    top_p = float(req.get("top_p", 0.8))
    temperature = float(req.get("temperature", 0.8))

    sr, audio_data, cost = generate_character_speech(
        char_id=character,
        text=text,
        prompt_name=prompt,
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
        headers={"X-Infer-Cost": f"{cost:.3f}s", "X-Audio-Sample-Rate": str(sr), "X-Character": character}
    )

demo.queue(max_size=20)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False
    )
