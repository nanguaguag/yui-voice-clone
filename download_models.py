#!/usr/bin/env python3
"""
自动检查并下载 GPT-SoVITS 必需的离线预训练底模与放学后茶会全员专属权重
"""
import os
import sys
import urllib.request

CHARACTER_WEIGHT_FILENAMES = {
    "yui": ("yui_pure_v2_e10_s230.pth", "yui_pure_v2-e15.ckpt"),
    "mio": ("mio_pure_v2_e10_s220.pth", "mio_pure_v2-e15.ckpt"),
    "ritsu": ("ritsu_pure_v2_e10_s210.pth", "ritsu_pure_v2-e15.ckpt"),
    "tsumugi": ("tsumugi_pure_v2_e10_s240.pth", "tsumugi_pure_v2-e15.ckpt"),
    "azusa": ("azusa_pure_v2_e10_s220.pth", "azusa_pure_v2-e15.ckpt"),
    "ui": ("ui_pure_v2_e10_s170.pth", "ui_pure_v2-e15.ckpt"),
    "nodoka": ("nodoka_pure_v2_e10_s160.pth", "nodoka_pure_v2-e15.ckpt"),
}

def download_file(url, target_path, min_size=1024):
    if os.path.exists(target_path) and os.path.getsize(target_path) >= min_size:
        return
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    temp_target = target_path + ".tmp"
    print(f"📦 正在下载: {os.path.basename(target_path)} ...")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; YuiVoiceClone/1.0)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=300) as response, open(temp_target, "wb") as out_file:
            chunk_size = 1024 * 1024
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
        actual_size = os.path.getsize(temp_target)
        if actual_size < min_size:
            raise ValueError(f"下载文件大小异常 ({actual_size} 字节 < {min_size} 字节)")
        os.replace(temp_target, target_path)
    except Exception as e:
        if os.path.exists(temp_target):
            try:
                os.remove(temp_target)
            except Exception:
                pass
        raise e
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
    if not os.path.exists(bin_path) or os.path.getsize(bin_path) < 1000:
        print("📦 正在下载语种识别分类底模 (lid.176.bin)...")
        download_file("https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin", bin_path, min_size=1000)
        print("✅ 语种识别模型就绪！")

    # 4. 检查声纹识别特征底模 sv/pretrained_eres2netv2w24s4ep4.ckpt
    sv_path = os.path.join(models_dir, "sv/pretrained_eres2netv2w24s4ep4.ckpt")
    if not os.path.exists(sv_path):
        os.makedirs(os.path.dirname(sv_path), exist_ok=True)
        print("📦 正在下载声纹特征底模 (pretrained_eres2netv2w24s4ep4.ckpt)...")
        hf_hub_download(
            repo_id="lj1995/GPT-SoVITS",
            filename="sv/pretrained_eres2netv2w24s4ep4.ckpt",
            local_dir=models_dir,
            local_dir_use_symlinks=False
        )
        print("✅ 声纹特征模型就绪！")

    # 5. 确保默认平泽唯微调模型权重就绪
    gpt_weight = os.path.join(base_dir, "weights/GPT_weights_v2Pro/yui_pure_v2-e15.ckpt")
    sovits_weight = os.path.join(base_dir, "weights/SoVITS_weights_v2Pro/yui_pure_v2_e10_s230.pth")

    # 若本地已有 PSSD 目录则优先复用
    local_p1_s = "/Volumes/My PSSD/projects/FLUX3/weights/yui_pure_v2/SoVITS_weights_v2Pro/yui_pure_v2_e10_s230.pth"
    local_p1_g = "/Volumes/My PSSD/projects/FLUX3/weights/yui_pure_v2/GPT_weights_v2Pro/yui_pure_v2-e15.ckpt"
    if os.path.exists(local_p1_s) and os.path.exists(local_p1_g):
        sovits_weight = local_p1_s
        gpt_weight = local_p1_g
    else:
        try:
            download_file(
                "https://github.com/nanguaguag/yui-voice-clone/releases/download/v2.0.0/yui_pure_v2-e15.ckpt",
                gpt_weight,
                min_size=10 * 1024 * 1024
            )
        except Exception as e:
            print(f"⚠️ 下载 v2.0.0 GPT 权重失败: {e}，尝试回退 v1.0.0...")
            gpt_weight = os.path.join(base_dir, "weights/GPT_weights_v2Pro/yui-e15.ckpt")
            download_file(
                "https://github.com/nanguaguag/yui-voice-clone/releases/download/v1.0.0/yui-e15.ckpt",
                gpt_weight,
                min_size=10 * 1024 * 1024
            )

        try:
            download_file(
                "https://github.com/nanguaguag/yui-voice-clone/releases/download/v2.0.0/yui_pure_v2_e10_s230.pth",
                sovits_weight,
                min_size=10 * 1024 * 1024
            )
        except Exception as e:
            print(f"⚠️ 下载 v2.0.0 SoVITS 权重失败: {e}，尝试回退 v1.0.0...")
            sovits_weight = os.path.join(base_dir, "weights/SoVITS_weights_v2Pro/yui_e12_s840.pth")
            download_file(
                "https://github.com/nanguaguag/yui-voice-clone/releases/download/v1.0.0/yui_e12_s840.pth",
                sovits_weight,
                min_size=10 * 1024 * 1024
            )

    # 6. 预先下载 NLTK 英文音素转换与词性标注数据包
    import nltk
    print("📦 检查并下载 NLTK 基础数据包...")
    for pkg in ["averaged_perceptron_tagger", "averaged_perceptron_tagger_eng", "cmudict", "punkt", "punkt_tab"]:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass
    print("✅ NLTK 数据包就绪！")

    return gpt_weight, sovits_weight

def ensure_character_weights(char_id: str, base_dir="."):
    """获取指定角色的 SoVITS 和 GPT 权重路径 (优先本地 -> 次选容器 weights -> 云端动态拉取)"""
    char_id = char_id.lower()
    if char_id not in CHARACTER_WEIGHT_FILENAMES:
        char_id = "yui"
    
    s_name, g_name = CHARACTER_WEIGHT_FILENAMES[char_id]
    
    # 候选 1: 本地移动硬盘 projects 根目录
    local_p1_s = f"/Volumes/My PSSD/projects/FLUX3/weights/{char_id}_pure_v2/SoVITS_weights_v2Pro/{s_name}"
    local_p1_g = f"/Volumes/My PSSD/projects/FLUX3/weights/{char_id}_pure_v2/GPT_weights_v2Pro/{g_name}"
    if os.path.exists(local_p1_s) and os.path.exists(local_p1_g):
        return local_p1_s, local_p1_g

    # 候选 2: 容器/工作区内的 weights 目录
    target_s = os.path.join(base_dir, f"weights/{char_id}_pure_v2/SoVITS_weights_v2Pro/{s_name}")
    target_g = os.path.join(base_dir, f"weights/{char_id}_pure_v2/GPT_weights_v2Pro/{g_name}")
    if os.path.exists(target_s) and os.path.exists(target_g):
        return target_s, target_g

    # 候选 3: 若本地或已下载有默认 yui
    if char_id == "yui":
        p_g = os.path.join(base_dir, "weights/GPT_weights_v2Pro/yui_pure_v2-e15.ckpt")
        p_s = os.path.join(base_dir, "weights/SoVITS_weights_v2Pro/yui_pure_v2_e10_s230.pth")
        if os.path.exists(p_s) and os.path.exists(p_g):
            return p_s, p_g

    # 尝试从 GitHub Release 下载
    try:
        download_file(
            f"https://github.com/nanguaguag/yui-voice-clone/releases/download/v2.0.0/{s_name}",
            target_s,
            min_size=10 * 1024 * 1024
        )
        download_file(
            f"https://github.com/nanguaguag/yui-voice-clone/releases/download/v2.0.0/{g_name}",
            target_g,
            min_size=10 * 1024 * 1024
        )
        return target_s, target_g
    except Exception as e:
        print(f"⚠️ 下载 {char_id} 权重异常: {e}，回退使用平泽唯模型")
        return ensure_character_weights("yui", base_dir)

if __name__ == "__main__":
    ensure_models(".")
