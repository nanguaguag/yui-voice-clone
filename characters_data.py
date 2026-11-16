#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K-ON! 放学后茶会全员 7 大角色元数据、主题配色与预设语气配置表
包含：平泽唯、秋山澪、田井中律、琴吹紬、中野梓、平泽忧、真锅和
"""

CHARACTERS = {
    "yui": {
        "id": "yui",
        "name": "平泽唯 (Hirasawa Yui)",
        "short_name": "平泽唯",
        "role": "吉他手 & 主唱 🎸 放学后茶会",
        "avatar": "🍓",
        "instrument": "Gibson Les Paul Standard (Giita / ギー太)",
        "theme": {
            "primary": "#FF5E87",         # 唯酱草莓珊瑚粉
            "primary_hover": "#E04870",
            "secondary": "#FFAA2A",       # 吉太金光闪闪
            "bg_gradient": "linear-gradient(135deg, #FFF5F7 0%, #FFFDF9 50%, #FFF9E6 100%)",
            "card_bg": "rgba(255, 255, 255, 0.88)",
            "border": "#FFE4EC",
            "shadow": "rgba(255, 94, 135, 0.22)",
            "badge_bg": "linear-gradient(45deg, #FF5E87, #FFAA2A)",
            "btn_gradient": "linear-gradient(135deg, #FF6B8B 0%, #FFAA2A 100%)",
            "text_color": "#D81E5B",
        },
        "default_text": "むぎちゃん！今日のおやつ、もしかしてショートケーキなの！？",
        "has_presets": True,
        "prompts": [
            {
                "id": "prompt_energetic",
                "name": "元气活力",
                "audio_path": "data/tts/yui_slices/yui_00065.wav",
                "prompt_text": "かっこいい大人の女性って感じです。",
                "prompt_language": "ja",
                "desc": "语速轻快，尾音上扬，充满朝气和略带迷糊的高中少女日常感。"
            },
            {
                "id": "prompt_routin",
                "name": "日常开朗",
                "audio_path": "data/tts/yui_slices/yui_00087.wav",
                "prompt_text": "ドラム担当の田井中律ちゃん",
                "prompt_language": "ja",
                "desc": "自然平和，标志性天真烂漫、无忧无虑的性格。"
            },
            {
                "id": "prompt_lazy_cute",
                "name": "呆萌撒娇",
                "audio_path": "data/tts/yui_slices/yui_00035.wav",
                "prompt_text": "夏は床の上を転がってばかりいるの",
                "prompt_language": "ja",
                "desc": "语速稍缓，尾音拉长，带着标志性的软绵绵鼻音与地板打滚撒娇拖音。"
            },
            {
                "id": "prompt_excited",
                "name": "兴奋高亢",
                "audio_path": "data/tts/yui_slices/yui_00136.wav",
                "prompt_text": "軽音部のみんなも協力してくれるんだ!",
                "prompt_language": "ja",
                "desc": "音调拔高，充满热情与眼睛放光的喜悦（买吉他/大家都会帮我）。"
            },
            {
                "id": "prompt_surprised",
                "name": "惊喜期待",
                "audio_path": "data/tts/yui_slices/yui_00059.wav",
                "prompt_text": "今日は麦ちゃん美味しいお菓子持ってきてくれるんだ",
                "prompt_language": "ja",
                "desc": "语调高昂、充满期待与喜悦，展现活泼、天真烂漫的性格。"
            }
        ],
        "examples": [
            "えへへ、憂〜、今日のご飯なに？お腹すいちゃった〜！",
            "ギー太、今日もいい音出してるよ！大好きだよ、ギー太！",
            "むぎちゃん！今日のおやつ、もしかしてショートケーキなの！？",
            "早上好呀！今天的天气超级棒，要打起精神来哦！",
            "小梓小梓~让我抱一下嘛！就抱五秒钟，吸一口小梓能量！",
            "Hello everyone! Welcome to After School Tea Time! Let's rock!"
        ],
        "weights": {
            "sovits": "yui_pure_v2_e10_s230.pth",
            "gpt": "yui_pure_v2-e15.ckpt"
        }
    },
    "mio": {
        "id": "mio",
        "name": "秋山澪 (Akiyama Mio)",
        "short_name": "秋山澪",
        "role": "贝斯手 & 害羞主唱 🎸 伊丽莎白",
        "avatar": "💙",
        "instrument": "Fender Jazz Bass 1962 (Elizabeth / エリザベス)",
        "theme": {
            "primary": "#2563EB",         # 澪酱纯净深蓝
            "primary_hover": "#1D4ED8",
            "secondary": "#60A5FA",       # 贝斯浅湖蓝
            "bg_gradient": "linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 50%, #E0F2FE 100%)",
            "card_bg": "rgba(255, 255, 255, 0.88)",
            "border": "#BFDBFE",
            "shadow": "rgba(37, 99, 235, 0.20)",
            "badge_bg": "linear-gradient(45deg, #2563EB, #60A5FA)",
            "btn_gradient": "linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)",
            "text_color": "#1E40AF",
        },
        "default_text": "恥ずかしいから、あまり見ないでよ…！でも、ベースの練習は付き合ってあげる。",
        "has_presets": False,
        "default_prompt": {
            "id": "prompt_default",
            "name": "默认纯净语气",
            "audio_path": "data/tts/slices/mio_00002.wav",
            "prompt_text": "知事?遅刻だぞ行ってきます",
            "prompt_language": "ja",
            "desc": "澪酱标志性沉稳清润的声线，带着微羞涩与认真的日常语调。"
        },
        "examples": [
            "恥ずかしいから、あまり見ないでよ…！でも、ベースの練習は付き合ってあげる。",
            "律！また練習サボってお菓子食べてるのか！？早く練習始めるぞ！",
            "萌え萌え、キュン！……うぅ、もう二度とやらないからな！",
            "不要盯着我看啦……我会紧张得弹错音的！",
            "今天放学后，一定要把那段贝斯独奏好好练熟。"
        ],
        "weights": {
            "sovits": "mio_pure_v2_e10_s220.pth",
            "gpt": "mio_pure_v2-e15.ckpt"
        }
    },
    "ritsu": {
        "id": "ritsu",
        "name": "田井中律 (Tainaka Ritsu)",
        "short_name": "田井中律",
        "role": "鼓手 & 傲娇部长 🥁 轻音部部长",
        "avatar": "💛",
        "instrument": "Yamaha Hipgig Drum Kit (Yellow Mustard)",
        "theme": {
            "primary": "#D97706",         # 律队元气亮琥珀黄
            "primary_hover": "#B45309",
            "secondary": "#FBBF24",       # 耀眼金色
            "bg_gradient": "linear-gradient(135deg, #FFFBEB 0%, #FFFDF8 50%, #FEF3C7 100%)",
            "card_bg": "rgba(255, 255, 255, 0.88)",
            "border": "#FDE68A",
            "shadow": "rgba(217, 119, 6, 0.20)",
            "badge_bg": "linear-gradient(45deg, #F59E0B, #FBBF24)",
            "btn_gradient": "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)",
            "text_color": "#92400E",
        },
        "default_text": "よーし！今日も放課後ティータイムのドラム、気合入れていくぞー！",
        "has_presets": False,
        "default_prompt": {
            "id": "prompt_default",
            "name": "默认纯净语气",
            "audio_path": "data/tts/slices/ritsu_00002.wav",
            "prompt_text": "7時、8時8時だと！",
            "prompt_language": "ja",
            "desc": "律队元气满满的大嗓门，豪爽乐观，充满领袖气息与欢快吐槽感。"
        },
        "examples": [
            "よーし！今日も放課後ティータイムのドラム、気合入れていくぞー！",
            "痛いっ！澪、なんで叩くんだよー！冗談じゃんかー！",
            "ガハハ！さすが私の相棒、澪！息ぴったりだな！",
            "好啦好啦！放学后茶会今天的排练正式开始！",
            "吃完点心再练习嘛，这才叫放学后茶会呀！"
        ],
        "weights": {
            "sovits": "ritsu_pure_v2_e10_s210.pth",
            "gpt": "ritsu_pure_v2-e15.ckpt"
        }
    },
    "tsumugi": {
        "id": "tsumugi",
        "name": "琴吹紬 (Kotobuki Tsumugi)",
        "short_name": "琴吹紬",
        "role": "键盘手 & 点心大小姐 🎹 皇家茶点",
        "avatar": "🍰",
        "instrument": "Korg Triton Extreme 76-key Synthesizer",
        "theme": {
            "primary": "#CA8A04",         # 紬大小姐奶金浅琥珀
            "primary_hover": "#A16207",
            "secondary": "#FDE047",       # 浅红茶金
            "bg_gradient": "linear-gradient(135deg, #FEFCE8 0%, #FFFDF8 50%, #FEF9C3 100%)",
            "card_bg": "rgba(255, 255, 255, 0.90)",
            "border": "#FEF08A",
            "shadow": "rgba(202, 138, 4, 0.20)",
            "badge_bg": "linear-gradient(45deg, #EAB308, #FACC15)",
            "btn_gradient": "linear-gradient(135deg, #EAB308 0%, #CA8A04 100%)",
            "text_color": "#854D0E",
        },
        "default_text": "ふふっ、今日はおいしい紅茶とバームクーヘンをお持ちしましたわ。",
        "has_presets": False,
        "default_prompt": {
            "id": "prompt_default",
            "name": "默认纯净语气",
            "audio_path": "data/tts/slices/tsumugi_00002.wav",
            "prompt_text": "8時、8時、8時ですよ",
            "prompt_language": "ja",
            "desc": "温柔文雅、轻声细语的大小姐语气，带点对平民生活的新奇与甜美笑意。"
        },
        "examples": [
            "ふふっ、今日はおいしい紅茶とバームクーヘンをお持ちしましたわ。",
            "私、ファストフード店でポテトを食べるのが夢だったんです！",
            "唯ちゃんのギターの音、温かくて大好きですわ。",
            "呵呵，今天特地为大家准备了热红茶和草莓蛋糕哦。",
            "能和大家一起在轻音部弹琴喝茶，是我最开心的事情了。"
        ],
        "weights": {
            "sovits": "tsumugi_pure_v2_e10_s240.pth",
            "gpt": "tsumugi_pure_v2-e15.ckpt"
        }
    },
    "azusa": {
        "id": "azusa",
        "name": "中野梓 (Nakano Azusa)",
        "short_name": "中野梓",
        "role": "吉他手 & 梓喵 🎸 穆斯唐",
        "avatar": "🐱",
        "instrument": "Fender Japan Mustang '69 Reissue (Candy Apple Red)",
        "theme": {
            "primary": "#059669",         # 梓喵翡翠薄荷绿
            "primary_hover": "#047857",
            "secondary": "#34D399",       # 翠青马卡龙
            "bg_gradient": "linear-gradient(135deg, #ECFDF5 0%, #F8FAF8 50%, #D1FAE5 100%)",
            "card_bg": "rgba(255, 255, 255, 0.88)",
            "border": "#A7F3D0",
            "shadow": "rgba(5, 150, 105, 0.20)",
            "badge_bg": "linear-gradient(45deg, #10B981, #34D399)",
            "btn_gradient": "linear-gradient(135deg, #10B981 0%, #059669 100%)",
            "text_color": "#065F46",
        },
        "default_text": "唯先輩、お茶ばっかり飲んでないで、ちゃんとギターの練習してください！",
        "has_presets": False,
        "default_prompt": {
            "id": "prompt_default",
            "name": "默认纯净语气",
            "audio_path": "data/tts/slices/azusa_00003.wav",
            "prompt_text": "いってきまーすいってらっしゃーい9時、10時、11時、12時お昼休みごはん",
            "prompt_language": "ja",
            "desc": "认真严谨的学妹声线，带着标志性的微傲娇、被前辈抱住时的娇嗔与纯真。"
        },
        "examples": [
            "唯先輩、お茶ばっかり飲んでないで、ちゃんとギターの練習してください！",
            "にゃ、にゃー……って、私を変な目で見ないでください！",
            "もう、先輩たちはいつもだらだらしすぎです！……でも、このケーキ美味しい。",
            "唯前辈！不要再抱过来了啦，很热的！",
            "喵……喵呜？！才、才不是什么梓喵呢！"
        ],
        "weights": {
            "sovits": "azusa_pure_v2_e10_s220.pth",
            "gpt": "azusa_pure_v2-e15.ckpt"
        }
    },
    "ui": {
        "id": "ui",
        "name": "平泽忧 (Hirasawa Ui)",
        "short_name": "平泽忧",
        "role": "唯的妹妹 & 全能天使 🌸 贤惠家务小太阳",
        "avatar": "🧡",
        "instrument": "全能乐理 & 料理家务样样精通",
        "theme": {
            "primary": "#EA580C",         # 忧酱温柔暖阳橘
            "primary_hover": "#C2410C",
            "secondary": "#FB923C",       # 暖杏温润色
            "bg_gradient": "linear-gradient(135deg, #FFF7ED 0%, #FFFDFB 50%, #FFEDD5 100%)",
            "card_bg": "rgba(255, 255, 255, 0.88)",
            "border": "#FED7AA",
            "shadow": "rgba(234, 88, 12, 0.20)",
            "badge_bg": "linear-gradient(45deg, #F97316, #FB923C)",
            "btn_gradient": "linear-gradient(135deg, #F97316 0%, #EA580C 100%)",
            "text_color": "#9A3412",
        },
        "default_text": "お姉ちゃん！朝ご飯できてるよ、遅刻しちゃうから早く起きて！",
        "has_presets": False,
        "default_prompt": {
            "id": "prompt_default",
            "name": "默认纯净语气",
            "audio_path": "data/tts/slices/ui_00002.wav",
            "prompt_text": "8時!8時!はっ!",
            "prompt_language": "ja",
            "desc": "极其体贴温柔、像小妈妈一样宠爱姐姐的乖巧甜美声线。"
        },
        "examples": [
            "お姉ちゃん！朝ご飯できてるよ、遅刻しちゃうから早く起きて！",
            "えへへ、お姉ちゃんが喜んでくれるなら、私、いくらでもご飯作っちゃうよ。",
            "軽音部のみなさん、いつもお姉ちゃんがお世話になってます！",
            "姐姐！快点起床啦，再赖床要迟到了哦！",
            "今天的早餐做好了姐姐最喜欢的煎蛋卷和味噌汤哦~"
        ],
        "weights": {
            "sovits": "ui_pure_v2_e10_s170.pth",
            "gpt": "ui_pure_v2-e15.ckpt"
        }
    },
    "nodoka": {
        "id": "nodoka",
        "name": "真锅和 (Manabe Nodoka)",
        "short_name": "真锅和",
        "role": "学生会长 & 知性青梅竹马 👓 红框眼镜",
        "avatar": "📕",
        "instrument": "学生会治理 & 事务决断担当",
        "theme": {
            "primary": "#DC2626",         # 和酱知性红镜框
            "primary_hover": "#B91C1C",
            "secondary": "#EF4444",       # 绛红学生会
            "bg_gradient": "linear-gradient(135deg, #FEF2F2 0%, #FFFAFA 50%, #FEE2E2 100%)",
            "card_bg": "rgba(255, 255, 255, 0.88)",
            "border": "#FECACA",
            "shadow": "rgba(220, 38, 38, 0.20)",
            "badge_bg": "linear-gradient(45deg, #DC2626, #EF4444)",
            "btn_gradient": "linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)",
            "text_color": "#991B1B",
        },
        "default_text": "唯、また生徒会への提出物遅れてるわよ。もう、しっかりしなさい。",
        "has_presets": False,
        "default_prompt": {
            "id": "prompt_default",
            "name": "默认纯净语气",
            "audio_path": "data/tts/slices/nodoka_00001.wav",
            "prompt_text": "1時、2時、3時、4時、5時、6時、7時、8時、もう8時よ",
            "prompt_language": "ja",
            "desc": "理智沉稳、知性端庄的学生会长声线，说话条理清晰，充满关切。"
        },
        "examples": [
            "唯、また生徒会への提出物遅れてるわよ。もう、しっかりしなさい。",
            "律さん、軽音部の部室申請書、期限は明日までですからね。",
            "幼馴染として、唯がこうして大好きなことを見つけられて嬉しいわ。",
            "唯，学生会要填写的社团表格你又拖到最后一天了哦。",
            "从小到大，唯只要一专注起来，就会展现出不可思议的能量呢。"
        ],
        "weights": {
            "sovits": "nodoka_pure_v2_e10_s160.pth",
            "gpt": "nodoka_pure_v2-e15.ckpt"
        }
    }
}

CHARACTER_KEYS = list(CHARACTERS.keys())
CHARACTER_CHOICES = [f"{c['avatar']} {c['short_name']}" for c in CHARACTERS.values()]
CHOICE_TO_KEY = {f"{c['avatar']} {c['short_name']}": c["id"] for c in CHARACTERS.values()}

def get_character_theme_css(char_id: str) -> str:
    """生成该角色对应的全局覆盖样式"""
    c = CHARACTERS.get(char_id, CHARACTERS["yui"])
    t = c["theme"]
    return f"""
<style id="dynamic-char-theme">
:root {{
    --primary-500: {t['primary']} !important;
    --primary-600: {t['primary_hover']} !important;
    --border-color-primary: {t['border']} !important;
}}

body, .gradio-container {{
    background: {t['bg_gradient']} !important;
    transition: background 0.4s ease !important;
}}

.char-header {{
    text-align: center;
    padding: 24px 14px 16px 14px;
    background: {t['card_bg']} !important;
    border-radius: 20px;
    margin-bottom: 20px;
    border: 2px solid {t['border']} !important;
    box-shadow: 0 8px 24px {t['shadow']} !important;
    backdrop-filter: blur(8px);
    transition: all 0.3s ease !important;
}}

.char-badge {{
    display: inline-block;
    background: {t['badge_bg']} !important;
    color: white !important;
    padding: 5px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 10px;
    box-shadow: 0 4px 10px {t['shadow']} !important;
    letter-spacing: 0.5px;
}}

.char-title {{
    color: {t['primary']} !important;
    font-size: 26px;
    margin: 6px 0;
    font-weight: 800;
    transition: color 0.3s ease !important;
}}

.char-btn {{
    background: {t['btn_gradient']} !important;
    color: white !important;
    font-weight: bold !important;
    font-size: 16px !important;
    border-radius: 16px !important;
    border: none !important;
    box-shadow: 0 6px 18px {t['shadow']} !important;
    transition: all 0.25s ease !important;
    padding: 12px 24px !important;
}}

.char-btn:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 24px {t['shadow']} !important;
    filter: brightness(1.05);
}}

.char-card {{
    background: {t['card_bg']} !important;
    border: 1.5px solid {t['border']} !important;
    border-radius: 16px !important;
    padding: 14px 18px;
    margin-top: 14px;
    box-shadow: 0 4px 16px {t['shadow']} !important;
}}

.char-accent-text {{
    color: {t['text_color']} !important;
    font-weight: 600;
}}
</style>
"""

def get_character_header_html(char_id: str) -> str:
    """生成角色专属的可爱风标题面板"""
    c = CHARACTERS.get(char_id, CHARACTERS["yui"])
    t = c["theme"]
    return f"""
    <div class="char-header">
        <span class="char-badge">{c['avatar']} 放学后茶会 After School Tea Time</span>
        <h1 class="char-title">{c['name']} 专属声音克隆</h1>
        <p style="color: #64748B; font-size: 14px; margin: 4px 0 0 0;">
            <b>身份/担当:</b> <span class="char-accent-text">{c['role']}</span> | 
            <b>专属乐器/特质:</b> <span style="color: #475569;">{c['instrument']}</span>
        </p>
        <p style="color: #94A3B8; font-size: 13px; margin: 4px 0 0 0;">
            基于 <b>GPT-SoVITS v2Pro</b> 打造的纯净干音专属神经音色引擎 | 支持跨语种高保真出声 🎵
        </p>
    </div>
    """

def get_character_todo_html(char_id: str) -> str:
    """生成角色预设语气与 TODO 说明"""
    c = CHARACTERS.get(char_id, CHARACTERS["yui"])
    if c["has_presets"]:
        return """
        <div style="background: rgba(255, 241, 242, 0.7); border: 1px dashed #FECDD3; border-radius: 12px; padding: 10px 14px; margin-bottom: 12px;">
            <span style="font-size: 13px; color: #BE123C;">
                🍓 <b>语气说明</b>: 平泽唯已集成 5 大黄金情绪语气预设（元气/日常/撒娇/兴奋/惊喜），可直接一键切换点选！
            </span>
        </div>
        """
    else:
        return f"""
        <div style="background: rgba(240, 249, 255, 0.75); border: 1px dashed #BAE6FD; border-radius: 12px; padding: 10px 14px; margin-bottom: 12px;">
            <span style="font-size: 13px; color: #0369A1;">
                💡 <b>预设说明 [TODO]</b>: 当前 <b>{c['short_name']}</b> 提供官方原版纯净干音默认语气。
                更多细分专属情绪预设正在制作中，您也可以立即使用下方<b>「🎨 自定义语气」</b>上传参考音频与台词自由克隆任何情绪！
            </span>
        </div>
        """
