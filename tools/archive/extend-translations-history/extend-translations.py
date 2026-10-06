#!/usr/bin/env python3
"""
extend-translations — One-shot helper to add many new PRE_TRANSLATIONS entries.

Run from repo root:
  python3 tools/extend-translations.py

This appends new entries to PRE_TRANSLATIONS dict in tools/pws-translate.py
and verifies the file still parses.
"""

import os
import re
import sys

# Additional translations to inject (kept separate from main pws-translate.py for review)
EXTRA_TRANSLATIONS = {
    # Lighting
    "spotlight": "聚光灯",
    "spotlighting": "聚光灯照明",
    "strobe lighting": "频闪灯",
    "blacklight": "黑光 / 紫外线灯",
    "ultraviolet light": "紫外线灯",
    "infrared light": "红外线灯",
    "x-ray light": "X 光灯",
    "halogen light": "卤素灯",
    "led light": "LED 灯",
    "fluorescent light": "荧光灯",
    "incandescent light": "白炽灯",
    "tungsten light": "钨丝灯",
    "diffused light": "漫射光",
    "direct light": "直射光",
    "reflected light": "反射光",
    "bounced light": "反射光",
    "practical light": "实物光",
    "motivated light": "动机光",
    "noir light": "黑色电影光",
    "high-key light": "高调光",
    "low-key light": "低调光",
    "key light": "主光",
    "fill light": "辅助光",
    "rim light": "轮廓光",
    "hair light": "发际光",
    "kicker light": "后侧强光",
    "background light": "背景光",
    "practical lamp": "室内灯光",

    # Expressions
    "shocked expression": "震惊表情",
    "angry expression": "愤怒表情",
    "serene expression": "宁静表情",
    "happy expression": "开心表情",
    "sad expression": "悲伤表情",
    "surprised expression": "惊讶表情",
    "disgusted expression": "厌恶表情",
    "afraid expression": "害怕表情",
    "contempt expression": "轻蔑表情",
    "determined expression": "坚定表情",
    "calm expression": "平静表情",
    "excited expression": "兴奋表情",
    "worried expression": "担心表情",
    "confused expression": "困惑表情",
    "embarrassed expression": "尴尬表情",
    "shy expression": "害羞表情",
    "smile": "微笑",
    "big smile": "大笑",
    "slight smile": "微微一笑",
    "grin": "露齿笑",
    "frown": "皱眉",
    "scowl": "怒视",
    "smirk": "得意笑",
    "pout": "撅嘴",
    "wink": "眨眼",
    "blush": "脸红",
    "tears": "眼泪",
    "crying": "哭泣",
    "laughing": "大笑",
    "shouting": "呐喊",
    "screaming": "尖叫",
    "whispering": "低语",
    "open mouth": "张嘴",
    "closed mouth": "闭嘴",
    "tongue out": "吐舌",
    "biting lip": "咬唇",
    "furrowed brow": "皱眉",
    "raised eyebrow": "挑眉",
    "wide eyes": "大眼睛",
    "narrowed eyes": "眯眼",
    "rolling eyes": "翻白眼",

    # Time
    "afternoon": "下午",
    "morning": "早上",
    "noon": "中午",
    "evening": "傍晚",
    "night": "夜晚",
    "twilight": "暮光",
    "dawn": "黎明",
    "daybreak": "拂晓",
    "dusk": "黄昏",
    "midday": "正午",
    "midnight": "午夜",
    "early morning": "清晨",
    "late afternoon": "傍晚",
    "late evening": "深夜",
    "small hours": "凌晨",
    "predawn": "黎明前",
    "post-sunset": "日落后",
    "pre-sunrise": "日出前",
    "rush hour": "高峰时段",
    "off-peak": "非高峰",
    "weekday": "平日",
    "weekend": "周末",
    "holiday": "节日",
    "summer": "夏",
    "winter": "冬",
    "spring": "春",
    "autumn": "秋",
    "fall": "秋",

    # Clothing common
    "jeans": "牛仔裤",
    "leggings": "紧身裤",
    "shorts": "短裤",
    "yoga pants": "瑜伽裤",
    "sweatpants": "运动裤",
    "joggers": "慢跑裤",
    "overalls": "背带裤",
    "romper": "连体短裤",
    "blazer dress": "西装连衣裙",
    "strapless dress": "抹胸连衣裙",
    "halter top": "挂脖上衣",
    "crop top": "露脐上衣",
    "tube top": "管状上衣",
    "off-shoulder top": "露肩上衣",
    "v-neck": "V 领",
    "round neck": "圆领",
    "turtleneck": "高领",
    "crew neck": "水手领",
    "scoop neck": "勺领",
    "jewelry": "珠宝",
    "anklet": "脚链",
    "brooch": "胸针",
    "pendant": "吊坠",
    "charm": "护身符",
    "bangle": "手镯",
    "cufflinks": "袖扣",
    "tie clip": "领带夹",
    "hair tie": "发圈",
    "scrunchie": "发圈",
    "barrette": "弹簧发夹",
    "wreath": "花圈",
    "garland": "花环",
    "gas mask": "防毒面具",
    "ski mask": "滑雪面罩",
    "balaclava": "巴拉克拉法帽",

    # Material
    "denim": "丹宁",
    "suede": "麂皮",
    "nylon": "尼龙",
    "polyester": "聚酯",
    "rayon": "人造丝",
    "spandex": "氨纶",
    "lycra": "莱卡",
    "tweed": "粗花呢",
    "flannel": "法兰绒",
    "corduroy": "灯芯绒",
    "khaki": "卡其",
    "tartan": "苏格兰格子",
    "plaid": "格子布",
    "polka dot": "圆点",
    "striped": "条纹",
    "checked": "方格",
    "floral print": "花卉印花",
    "animal print": "动物印花",
    "leopard print": "豹纹",
    "zebra print": "斑马纹",
    "snake print": "蛇纹",
    "camouflage": "迷彩",
    "tie dye": "扎染",
    "batik": "蜡染",

    # MJ V5 color paths (willwulfken)
    "colors/black/black": "颜色/黑/纯黑",
    "colors/black/light black": "颜色/黑/浅黑",
    "colors/black/dark black": "颜色/黑/深黑",
    "colors/white/white": "颜色/白/纯白",
    "colors/white/light white": "颜色/白/浅白",
    "colors/white/dark white": "颜色/白/深白",
    "colors/gray/gray": "颜色/灰/灰",
    "colors/gray/light gray": "颜色/灰/浅灰",
    "colors/gray/dark gray": "颜色/灰/深灰",
    "colors/gray/silver": "颜色/灰/银",
    "colors/gray/slate gray": "颜色/灰/板岩灰",
    "colors/brown/beige/beige": "颜色/棕/米色",
    "colors/brown/light brown": "颜色/棕/浅棕",
    "colors/brown/dark brown": "颜色/棕/深棕",
    "colors/brown/tan/tan": "颜色/棕/黄褐",
    "colors/brown/vivid brown": "颜色/棕/鲜艳棕",
    "colors/red/red": "颜色/红/红",
    "colors/red/light red": "颜色/红/浅红",
    "colors/red/dark red": "颜色/红/深红",
    "colors/red/crimson/crimson": "颜色/红/深红",
    "colors/red/vivid red": "颜色/红/鲜艳红",
    "colors/orange/orange": "颜色/橙/橙",
    "colors/orange/light orange": "颜色/橙/浅橙",
    "colors/orange/dark orange": "颜色/橙/深橙",
    "colors/orange/peach": "颜色/橙/桃",
    "colors/yellow/yellow": "颜色/黄/黄",
    "colors/yellow/light yellow": "颜色/黄/浅黄",
    "colors/yellow/dark yellow": "颜色/黄/深黄",
    "colors/yellow/gold": "颜色/黄/金",
    "colors/yellow/golden": "颜色/黄/金黄",
    "colors/green/green": "颜色/绿/绿",
    "colors/green/light green": "颜色/绿/浅绿",
    "colors/green/dark green": "颜色/绿/深绿",
    "colors/green/olive": "颜色/绿/橄榄",
    "colors/green/olive green": "颜色/绿/橄榄绿",
    "colors/green/lime/lime": "颜色/绿/青柠",
    "colors/green/lime/light lime": "颜色/绿/浅青柠",
    "colors/green/lime/dark lime": "颜色/绿/深青柠",
    "colors/green/lime/vivid lime": "颜色/绿/鲜艳青柠",
    "colors/green/chartreuse": "颜色/绿/黄绿",
    "colors/green/vivid green": "颜色/绿/鲜艳绿",
    "colors/green/forest green": "颜色/绿/森林绿",
    "colors/green/emerald": "颜色/绿/翡翠",
    "colors/green/sage": "颜色/绿/鼠尾草",
    "colors/green/mint": "颜色/绿/薄荷",
    "colors/green/jade": "颜色/绿/翡翠绿",
    "colors/green/pine": "颜色/绿/松绿",
    "colors/green/teal": "颜色/绿/鸭绿",
    "colors/blue/blue": "颜色/蓝/蓝",
    "colors/blue/light blue": "颜色/蓝/浅蓝",
    "colors/blue/dark blue": "颜色/蓝/深蓝",
    "colors/blue/navy/navy": "颜色/蓝/海军蓝",
    "colors/blue/azure/azure": "颜色/蓝/天青",
    "colors/blue/aqua/aqua": "颜色/蓝/水蓝",
    "colors/blue/cyan/cyan": "颜色/蓝/青",
    "colors/blue/cyan/light cyan": "颜色/蓝/浅青",
    "colors/blue/cyan/dark cyan": "颜色/蓝/深青",
    "colors/blue/cyan/vivid cyan": "颜色/蓝/鲜艳青",
    "colors/blue/indigo/indigo": "颜色/蓝/靛蓝",
    "colors/blue/vivid blue": "颜色/蓝/鲜艳蓝",
    "colors/blue/royal blue": "颜色/蓝/皇家蓝",
    "colors/blue/sky blue": "颜色/蓝/天蓝",
    "colors/blue/cobalt blue": "颜色/蓝/钴蓝",
    "colors/blue/turquoise": "颜色/蓝/绿松石",
    "colors/blue/steel blue": "颜色/蓝/钢蓝",
    "colors/blue/denim blue": "颜色/蓝/牛仔蓝",
    "colors/blue/periwinkle": "颜色/蓝/长春花蓝",
    "colors/purple/purple": "颜色/紫/紫",
    "colors/purple/light purple": "颜色/紫/浅紫",
    "colors/purple/dark purple": "颜色/紫/深紫",
    "colors/purple/violet": "颜色/紫/紫罗兰",
    "colors/purple/lavender": "颜色/紫/薰衣草紫",
    "colors/purple/orchid": "颜色/紫/兰花紫",
    "colors/purple/magenta/magenta": "颜色/紫/品红",
    "colors/purple/magenta/light magenta": "颜色/紫/浅品红",
    "colors/purple/magenta/dark magenta": "颜色/紫/深品红",
    "colors/purple/magenta/vivid magenta": "颜色/紫/鲜艳品红",
    "colors/purple/plum": "颜色/紫/梅紫",
    "colors/purple/grape": "颜色/紫/葡萄紫",
    "colors/purple/eggplant": "颜色/紫/茄子紫",
    "colors/purple/mauve": "颜色/紫/藕紫",
    "colors/purple/lilac": "颜色/紫/丁香紫",
    "colors/pink/pink": "颜色/粉/粉",
    "colors/pink/light pink": "颜色/粉/浅粉",
    "colors/pink/dark pink": "颜色/粉/深粉",
    "colors/pink/rose": "颜色/粉/玫瑰粉",
    "colors/pink/hot pink": "颜色/粉/热粉",
    "colors/pink/salmon": "颜色/粉/鲑鱼粉",
    "colors/pink/coral": "颜色/粉/珊瑚粉",
    "colors/pink/fuchsia": "颜色/粉/品红粉",
    "colors/pink/blush": "颜色/粉/腮红粉",
    "colors/brown/sienna": "颜色/棕/赭色",
    "colors/brown/chocolate": "颜色/棕/巧克力色",
    "colors/brown/coffee": "颜色/棕/咖啡色",
    "colors/brown/caramel": "颜色/棕/焦糖色",
    "colors/brown/rust": "颜色/棕/锈色",
    "colors/yellow/cream": "颜色/黄/奶油色",
    "colors/yellow/lemon": "颜色/黄/柠檬色",
    "colors/yellow/mustard": "颜色/黄/芥末色",
    "colors/yellow/amber": "颜色/黄/琥珀色",
    "colors/orange/tangerine": "颜色/橙/橘子色",
    "colors/orange/pumpkin": "颜色/橙/南瓜色",
    "colors/orange/amber": "颜色/橙/琥珀色",
    "colors/orange/apricot": "颜色/橙/杏色",
    "colors/orange/burnt orange": "颜色/橙/烧橙",
    "colors/red/burgundy": "颜色/红/酒红",
    "colors/red/scarlet": "颜色/红/猩红",
    "colors/red/coral": "颜色/红/珊瑚红",
    "colors/red/salmon": "颜色/红/鲑红",
    "colors/red/rose": "颜色/红/玫瑰红",
    "colors/red/rust": "颜色/红/锈红",
    "colors/red/maroon": "颜色/红/栗红",
    "colors/red/carmine": "颜色/红/胭脂红",
    "colors/white/cream": "颜色/白/奶油白",
    "colors/white/ivory": "颜色/白/象牙白",
    "colors/white/snow": "颜色/白/雪白",
    "colors/white/pearl": "颜色/白/珍珠白",
    "colors/white/off-white": "颜色/白/米白",
    "colors/white/alabaster": "颜色/白/雪花白",
    "colors/black/charcoal": "颜色/黑/炭灰",
    "colors/black/jet": "颜色/黑/黑檀",
    "colors/black/onyx": "颜色/黑/玛瑙黑",
    "colors/black/ebony": "颜色/黑/乌木黑",
    "colors/black/obsidian": "颜色/黑/黑曜黑",
    "colors/black/coal": "颜色/黑/煤黑",

    # Composition / framing
    "low angle": "仰视角度",
    "high angle": "俯视角度",
    "eye level": "平视",
    "dutch angle": "荷兰角",
    "tilted angle": "倾斜角",
    "isometric": "等距视角",
    "dynamic angle": "动态角度",
    "portrait orientation": "竖向构图",
    "landscape orientation": "横向构图",
    "square orientation": "正方形构图",
    "panoramic": "全景",

    # Sky / celestial
    "afternoon light": "午后光",
    "morning light": "早晨光",
    "evening light": "傍晚光",
    "night sky": "夜空",
    "day sky": "白天天空",
    "starry sky": "星空",
    "cloudy sky": "多云天空",
    "overcast sky": "阴天",
    "sunny sky": "晴朗天空",
    "sunset sky": "日落天空",
    "sunrise sky": "日出天空",
    "rainbow": "彩虹",
    "aurora": "极光",
    "aurora borealis": "北极光",
    "northern lights": "北极光",
    "milky way": "银河",
    "full moon": "满月",
    "new moon": "新月",
    "crescent moon": "弯月",
    "half moon": "半月",
    "harvest moon": "收获月",
    "blood moon": "血月",
    "eclipse": "日/月食",
    "lunar eclipse": "月食",
    "solar eclipse": "日食",
    "moonrise": "月升",
    "moonset": "月落",
    "starshine": "星光",
    "moonbeams": "月光",
    "sunbeams": "阳光",
    "sunrays": "太阳光线",
    "god rays": "上帝光线",
    "crepuscular rays": "暮曙光射线",
    "sun dog": "假日",
    "rainbow halo": "彩虹环",
    "light pillar": "光柱",
    "sun pillar": "日柱",
    "frost flowers": "霜花",
    "ice crystals": "冰晶",
    "hoarfrost": "白霜",
    "rime": "霜冻",
    "snowflakes": "雪花",
    "hailstones": "冰雹",
    "raindrops": "雨滴",
    "dew drops": "露珠",
    "morning dew": "晨露",
    "hazy": "朦胧",
    "smoggy": "烟雾笼罩",
    "smoky": "烟熏",

    # Art style
    "watercolor painting": "水彩画",
    "oil painting": "油画",
    "acrylic painting": "丙烯画",
    "pastel painting": "彩色绘画",
    "pencil drawing": "铅笔画",
    "pen and ink": "钢笔墨水画",
    "charcoal drawing": "炭笔画",
    "chalk drawing": "粉笔画",
    "marker drawing": "马克笔画",
    "crayon drawing": "蜡笔画",
    "graphite drawing": "石墨画",
    "ink wash painting": "水墨画",
    "ink and wash": "水墨画",
    "sumi-e": "墨绘",
    "guocha": "写意画",
    "gongbi": "工笔画",
    "rice paper": "宣纸",
    "calligraphy": "书法",
    "chibi": "Q版卡通",
    "kawaii": "可爱风",
    "flat color": "平涂",
    "flat shading": "平涂渲染",
    "gradient": "渐变",
    "line art": "线稿",
    "digital painting": "数字绘画",
    "low poly": "低多边形",
    "high poly": "高多边形",
    "voxel art": "体素艺术",
    "voxel render": "体素渲染",
    "isometric art": "等距艺术",
    "isometric render": "等距渲染",
    "vector art": "矢量艺术",
    "vector graphics": "矢量图形",
    "raster": "位图",
    "raster art": "位图艺术",
    "matcap": "材质球渲染",
    "toon shading": "卡通渲染",
    "npr": "非真实感渲染",
    "npr shading": "非真实感着色",
    "pbr": "基于物理的渲染",
    "physically based": "基于物理的",
    "physically accurate": "物理准确",
    "high detail": "高细节",
    "low detail": "低细节",
    "intricate detail": "复杂细节",
    "fine detail": "精细细节",
    "micro detail": "微细节",
    "macro detail": "宏观细节",

    # Negative common
    "low quality": "低质量",
    "worst quality": "最差质量",
    "normal quality": "普通质量",
    "best quality": "最佳质量",
    "high quality": "高质量",
    "bad anatomy": "畸形解剖",
    "extra limbs": "多余肢体",
    "missing fingers": "缺少手指",
    "extra fingers": "多余手指",
    "bad hands": "糟糕双手",
    "missing hands": "缺手",
    "extra hands": "多手",
    "poorly drawn face": "糟糕面部",
    "poorly drawn hands": "糟糕双手",
    "poorly drawn feet": "糟糕脚部",
    "mutation": "变异",
    "deformed": "变形",
    "ugly": "丑陋",
    "blurry": "模糊",
    "jpeg artifact": "JPEG 压缩",
    "compression artifact": "压缩",
    "watermark": "水印",
    "signature": "签名",
    "logo": "徽标",
    "cropped": "裁切",
    "out of frame": "出框",
    "cut off": "切断",
    "duplicate": "重复",
    "morbid": "病态",
    "mutilated": "残害",
    "long neck": "长颈",
    "long body": "长躯",
    "obese": "肥胖",
    "child": "儿童",
    "minor": "未成年",
    "censored": "审查",
    "lowres": "低分辨率",
    "username": "用户名",
    "artist name": "艺术家名",
    "grayscale": "灰度",
    "oversaturated": "过饱和",
    "low contrast": "低对比",
    "low brightness": "低亮度",
    "overexposed": "过曝",
    "underexposed": "欠曝",
    "asymmetrical": "不对称",
    "bad proportions": "比例失调",
    "amateur": "业余",
    "amateurish": "业余的",
    "unprofessional": "不专业",
    "beginner": "初学",
    "tutorial": "教程",
    "skill": "技巧",
    "advanced": "高级",
    "intermediate": "中级",
}


def inject_translations(filepath, new_entries):
    """Inject new entries into PRE_TRANSLATIONS dict, preserving sorted order."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        print(f"❌ Failed to read {filepath}: {e}")
        sys.exit(1)

    # Find PRE_TRANSLATIONS bounds
    start_marker = "PRE_TRANSLATIONS = {"
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print(f"❌ PRE_TRANSLATIONS not found in {filepath}")
        sys.exit(1)

    i = start_idx + len(start_marker) - 1  # point at '{'
    end_idx = None
    brace_count = 0
    for j in range(i, len(content)):
        c = content[j]
        if c == '{':
            brace_count += 1
        elif c == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = j + 1
                break

    before = content[:start_idx]
    dict_str = content[start_idx + len("PRE_TRANSLATIONS = "):end_idx]
    after = content[end_idx:]

    # Parse existing entries
    existing = {}
    for k, v in re.findall(r'"([^"]+)":\s*"([^"]+)"', dict_str):
        existing[k] = v

    # Merge new entries (only add new keys)
    added = 0
    skipped = 0
    for k, v in new_entries.items():
        if k in existing:
            skipped += 1
        else:
            existing[k] = v
            added += 1

    # Re-sort and format
    new_lines = []
    for k, v in sorted(existing.items()):
        v_safe = v.replace('"', '\\"')
        new_lines.append(f'    "{k}": "{v_safe}",')

    new_dict_str = '{\n' + '\n'.join(new_lines) + '\n}'
    new_content = before + 'PRE_TRANSLATIONS = ' + new_dict_str + after

    try:
        with open(filepath, 'w', encoding="utf-8") as f:
            f.write(new_content)
    except OSError as e:
        print(f"❌ Failed to write {filepath}: {e}")
        sys.exit(1)

    print(f"✅ Added {added} new entries, skipped {skipped} duplicates (file now has {len(existing)} unique entries)")

    # Verify it parses
    try:
        with open(filepath, encoding="utf-8") as f:
            code = f.read()
        # Extract just the dict
        m = re.search(r'PRE_TRANSLATIONS = (\{[^\n]+(?:.+?\n)*?\})\n\n', code, re.DOTALL)
        if m:
            from ast import literal_eval
            ns = {'__name__': 'test'}
            ns['PRE_TRANSLATIONS'] = literal_eval(m.group(1))
            print("✅ File syntactically valid")
    except Exception as e:
        print(f"⚠️  Syntax check failed: {e}")


if __name__ == "__main__":
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(repo_root, "tools", "pws-translate.py")
    inject_translations(target, EXTRA_TRANSLATIONS)