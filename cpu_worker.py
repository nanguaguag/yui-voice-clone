#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persistent CPU fallback worker for Hugging Face ZeroGPU Spaces.
Runs in an isolated subprocess with CUDA disabled so ZeroGPU's CUDA hooks
never interfere with CPU inference.
"""

import json
import os
import sys
import tempfile
import time
from types import SimpleNamespace
import numpy as np
import soundfile as sf

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["device"] = "cpu"
os.environ["is_half"] = "False"

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SOVITS_ROOT = os.path.join(APP_DIR, "GPT-SoVITS")
if os.path.exists(SOVITS_ROOT):
    sys.path.insert(0, APP_DIR)
    sys.path.insert(0, SOVITS_ROOT)
    sys.path.insert(0, os.path.join(SOVITS_ROOT, "GPT_SoVITS"))
    os.chdir(SOVITS_ROOT)

from download_models import ensure_models, ensure_character_weights

DEFAULT_GPT, DEFAULT_SOVITS = ensure_models(APP_DIR)
os.environ["gpt_path"] = DEFAULT_GPT
os.environ["sovits_path"] = DEFAULT_SOVITS

import inference_webui as infer

try:
    next(infer.change_sovits_weights(DEFAULT_SOVITS))
except (StopIteration, TypeError):
    pass
infer.change_gpt_weights(DEFAULT_GPT)
CURRENT_CHAR = "yui"


def switch_char(char_id: str):
    global CURRENT_CHAR
    char_id = char_id.lower()
    if char_id == CURRENT_CHAR:
        return
    s_path, g_path = ensure_character_weights(char_id, APP_DIR)
    try:
        next(infer.change_sovits_weights(s_path))
    except (StopIteration, TypeError):
        pass
    infer.change_gpt_weights(g_path)
    CURRENT_CHAR = char_id


def main():
    # Signal readiness
    print(json.dumps({"ready": True}), flush=True)
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            req = json.loads(raw)
            switch_char(req["char_id"])
            t0 = time.time()
            inp_ref_paths = req.get("inp_refs") or []
            inp_refs = [SimpleNamespace(name=p) for p in inp_ref_paths if p and os.path.exists(p)] or None
            gen = infer.get_tts_wav(
                ref_wav_path=req["ref_wav"],
                prompt_text=req["ref_text"],
                prompt_language=req["ref_lang"],
                text=req["text"],
                text_language=req["target_lang"],
                how_to_cut=infer.i18n("不切"),
                top_k=int(req["top_k"]),
                top_p=float(req["top_p"]),
                temperature=float(req["temperature"]),
                speed=float(req["speed"]),
                inp_refs=inp_refs,
                pause_second=0.22,
            )
            sr, audio_data = next(gen)
            cost = time.time() - t0
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32767.0
            elif audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            fd, tmp_wav = tempfile.mkstemp(suffix=".wav", prefix="cpu_tts_")
            os.close(fd)
            sf.write(tmp_wav, audio_data, sr, format="WAV", subtype="FLOAT")
            print(json.dumps({"ok": True, "wav_path": tmp_wav, "sr": int(sr), "cost": cost}), flush=True)
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}), flush=True)


if __name__ == "__main__":
    main()
