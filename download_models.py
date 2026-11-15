#!/usr/bin/env python3
"""
自动检查并下载 GPT-SoVITS 必需的离线预训练底模与平泽唯专属权重
"""
import os
import sys
import urllib.request

def download_file(url, target_path, min_size=1024):
    if os.path.exists(target_path) and os.path.getsize(target_path) >= min_size:
        return
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    print(f"📦 正在下载: {os.path.basename(target_path)} ...")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; YuiVoiceClone/1.0)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=300) as response, open(target_path, "wb") as out_file:
        chunk_size = 1024 * 1024
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
    print(f"✅ 下载完成: {os.path.basename(target_path)} ({os.path.getsize(target_path)/(1024*1024):.2f} MB)")

def ensure_models(base_dir="."):
    models_dir = os.path.join(base_dir, "GPT-SoVITS/GPT_SoVITS/pretrained_models")
    os.makedirs(models_dir, exist_ok=True)
    
    hubert_dir = os.path.join(models_dir, "chinese-hubert-base")
    bert_dir = os.path.join(models_dir, "chinese-roberta-wwm-ext-large")
    
    from huggingface_hub import snapshot_download, hf_hub_download
    
    # 1. 检查并下载 HuBERT
    if not os.path.exists(hubert_dir) or not os.path.exists(os.path.join(hubert_dir, "pytorch_model.bin")):
        print("📦 正在下载官方 HuBERT 预训练模型 (chinese-hubert-base)...")
        snapshot_download(
            repo_id="TencentGameMate/chinese-hubert-base",
            local_dir=hubert_dir,
            local_dir_use_symlinks=False
        )
        print("✅ HuBERT 模型就绪！")
        
    # 2. 检查并下载 RoBERTa
    if not os.path.exists(bert_dir) or not os.path.exists(os.path.join(bert_dir, "pytorch_model.bin")):
        print("📦 正在下载官方 RoBERTa 预训练模型 (chinese-roberta-wwm-ext-large)...")
        snapshot_download(
            repo_id="hfl/chinese-roberta-wwm-ext-large",
            local_dir=bert_dir,
            local_dir_use_symlinks=False
        )
        print("✅ RoBERTa 模型就绪！")

    # 3. 检查快慢语种识别模型 fast_langdetect
    lang_dir = os.path.join(models_dir, "fast_langdetect")
    os.makedirs(lang_dir, exist_ok=True)
    bin_path = os.path.join(lang_dir, "lid.176.bin")
    if not os.path.exists(bin_path):
        print("📦 正在下载语种识别分类底模 (lid.176.bin)...")
        hf_hub_download(
            repo_id="facebook/fasttext-language-identification",
            filename="lid.176.bin",
            local_dir=lang_dir,
            local_dir_use_symlinks=False
        )
        print("✅ 语种识别模型就绪！")

    # 4. 检查唯酱微调模型权重 (从 GitHub Release v1.0.0 下载)
    gpt_weight = os.path.join(base_dir, "weights/GPT_weights_v2Pro/yui-e15.ckpt")
    sovits_weight = os.path.join(base_dir, "weights/SoVITS_weights_v2Pro/yui_e12_s840.pth")

    download_file(
        "https://github.com/nanguaguag/yui-voice-clone/releases/download/v1.0.0/yui-e15.ckpt",
        gpt_weight,
        min_size=10 * 1024 * 1024
    )
    download_file(
        "https://github.com/nanguaguag/yui-voice-clone/releases/download/v1.0.0/yui_e12_s840.pth",
        sovits_weight,
        min_size=10 * 1024 * 1024
    )

if __name__ == "__main__":
    ensure_models(".")
