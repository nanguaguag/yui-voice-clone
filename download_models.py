#!/usr/bin/env python3
"""
自动检查并下载 GPT-SoVITS 必需的离线预训练底模与平泽唯专属权重
"""
import os
import sys
import subprocess

def ensure_models(base_dir="."):
    models_dir = os.path.join(base_dir, "GPT-SoVITS/GPT_SoVITS/pretrained_models")
    os.makedirs(models_dir, exist_ok=True)
    
    hubert_dir = os.path.join(models_dir, "chinese-hubert-base")
    bert_dir = os.path.join(models_dir, "chinese-roberta-wwm-ext-large")
    
    from huggingface_hub import snapshot_download
    
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
        from huggingface_hub import hf_hub_download
        print("📦 正在下载语种识别分类底模 (lid.176.bin)...")
        hf_hub_download(
            repo_id="facebook/fasttext-language-identification",
            filename="lid.176.bin",
            local_dir=lang_dir,
            local_dir_use_symlinks=False
        )
        print("✅ 语种识别模型就绪！")

    # 4. 检查唯酱微调模型权重
    gpt_weight = os.path.join(base_dir, "weights/GPT_weights_v2Pro/yui-e15.ckpt")
    sovits_weight = os.path.join(base_dir, "weights/SoVITS_weights_v2Pro/yui_e12_s840.pth")

    if not os.path.exists(gpt_weight) or os.path.getsize(gpt_weight) < 1000:
        os.makedirs(os.path.dirname(gpt_weight), exist_ok=True)
        print("📦 正在拉取平泽唯 GPT 微调权重 (yui-e15.ckpt)...")
        url = "https://github.com/nanguaguag/yui-voice-clone/releases/download/v1.0.0/yui-e15.ckpt"
        subprocess.run(["curl", "-L", "-o", gpt_weight, url], check=False)

    if not os.path.exists(sovits_weight) or os.path.getsize(sovits_weight) < 1000:
        os.makedirs(os.path.dirname(sovits_weight), exist_ok=True)
        print("📦 正在拉取平泽唯 SoVITS 声学微调权重 (yui_e12_s840.pth)...")
        url = "https://github.com/nanguaguag/yui-voice-clone/releases/download/v1.0.0/yui_e12_s840.pth"
        subprocess.run(["curl", "-L", "-o", sovits_weight, url], check=False)

if __name__ == "__main__":
    ensure_models(".")
