#!/usr/bin/env python3
import os
import sys
import re
import argparse

os.environ["version"] = "v2Pro"
os.environ["device"] = "cpu"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

sovits_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(sovits_root)
sys.path.insert(0, sovits_root)
sys.path.insert(0, os.path.join(sovits_root, "GPT_SoVITS"))

def normalize_text_punctuations(text: str) -> str:
    """归一化复合及连续标点，防止日文/中文分词器产生异常 token 或使自回归模型错过 EOS"""
    text = text.strip()
    # 复合问叹号规整为单一标点
    text = re.sub(r"[！？?!]{2,}", "！", text)
    # 重复句号/逗号缩减为单个
    text = re.sub(r"[。\.]{2,}", "。", text)
    text = re.sub(r"[，,、]{2,}", "，", text)
    return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpt", required=True)
    parser.add_argument("--sovits", required=True)
    parser.add_argument("--ref_wav", required=True)
    parser.add_argument("--ref_text", required=True)
    parser.add_argument("--ref_lang", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--lang", default="ja")
    parser.add_argument("--out", required=True)
    parser.add_argument("--top_k", type=int, default=15)
    parser.add_argument("--top_p", type=float, default=0.8)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--speed", type=float, default=1.0)
    args = parser.parse_args()

    import numpy as np
    import soundfile as sf
    import inference_webui as infer

    # 1. 切换权重：注意 change_sovits_weights 是生成器，必须通过 next() 消耗以完成权重加载
    try:
        next(infer.change_sovits_weights(args.sovits))
    except (StopIteration, TypeError):
        pass
    infer.change_gpt_weights(args.gpt)

    lang_map = {
        "ja": "Japanese",
        "zh": "Chinese",
        "en": "English",
        "auto": "Multilingual Mixed",
        "日文": "Japanese",
        "中文": "Chinese",
        "英文": "English",
    }

    ref_lang_val = lang_map.get(args.ref_lang.lower(), args.ref_lang)
    target_lang_val = lang_map.get(args.lang.lower(), args.lang)

    # 2. 文本清洗与标点规整
    clean_target_text = normalize_text_punctuations(args.text)
    clean_ref_text = normalize_text_punctuations(args.ref_text)

    gen = infer.get_tts_wav(
        ref_wav_path=args.ref_wav,
        prompt_text=clean_ref_text,
        prompt_language=ref_lang_val,
        text=clean_target_text,
        text_language=target_lang_val,
        how_to_cut=infer.i18n("凑四句一切"),
        top_k=args.top_k,
        top_p=args.top_p,
        temperature=args.temperature,
        speed=args.speed,
    )

    sr, audio_data = next(gen)

    # 音量规整化（避免模型输出动态过大或过小）
    if isinstance(audio_data, np.ndarray) and len(audio_data) > 0:
        max_val = np.abs(audio_data).max()
        if max_val > 0 and max_val < 1.0:
            # 浮点类型归一化至 -0.95 ~ 0.95
            audio_data = (audio_data / max_val * 0.95).astype(np.float32)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    sf.write(args.out, audio_data, sr)
    print(f"SUCCESS: Audio written to {args.out} (sr={sr}, duration={len(audio_data)/sr:.2f}s)")

if __name__ == "__main__":
    main()
