#!/usr/bin/env python3
"""
extend-translations-10 — Tenth batch: low-coverage categories refinement.

Focus: photographer, color-look, character-fx, framing, character
Hold: quality, era, render-quality, action-fx, panel, transitions, negative
"""

EXTRA_TRANSLATIONS_10 = {
    # ============== photographer (34 terms) ==============
    # genre
    "shot in the language of a vogue editorial cover": "《Vogue》封面编辑风格",
    "composed as a top-down e-commerce flat lay with even shadowless white backdrop": "俯拍电商平铺图带均匀无影白底",
    "shot in the language of a jil sander editorial": "Jil Sander 风格编辑大片",
    "shot in the language of a vivienne tam editorial": "Vivienne Tam 风格编辑大片",
    "shot in the language of a jacquemus campaign": "Jacquemus 风格广告大片",
    "shot in the signature language of helmut newton": "赫尔穆特·牛顿标志性风格",
    "shot in the signature language of a harper's bazaar editorial": "《Harper's Bazaar》编辑大片风格",
    "shot in a street-photography idiom": "街头摄影风格",
    "shot as editorial photojournalism with a 35mm reportage lens": "35mm 报道镜头新闻摄影编辑大片",
    "shot as a polished corporate headshot": "精致企业形象照",
    "shot as a police booking mugshot": "警方登记摄录照",
    "shot as a wedding portrait": "婚礼人像",
    "shot as a posed family portrait": "全家福合影",
    "shot as a glamour portrait with soft diffused beauty lighting": "魅惑人像柔光美容光",
    "shot in a film-noir portrait idiom": "黑色电影人像风格",
    "shot as a gym mirror selfie": "健身房镜子自拍",
    "shot as a bathroom mirror selfie with a small on-phone flash": "浴室镜子自拍配小闪光灯",
    "shot as a group phone selfie taken at arm's length": "群臂合影自拍",
    "shot as a clean e-commerce product photograph": "干净电商产品照",
    # editorial
    "by steven meisel, polished mid-century editorial": "史蒂文·梅塞尔风格，精致中世纪编辑大片",
    "by mario sorrenti, intimate grainy fashion": "马里奥·索伦蒂风格，亲密颗粒时尚",
    "by oleg oprisco, cinematic film-grain storytelling": "奥列格·奥普里斯科风格，电影颗粒叙事",
    "by yigal ozeri, hyperreal painted portraiture": "伊加尔·奥泽里风格，超写实绘画人像",
    "by rinko kawauchi, quiet light-suffused everyday": "川内伦子风格，安静光感日常",
    "by robert mapplethorpe, formalist studio monochrome": "罗伯特·梅普尔索普风格，形式主义影棚黑白",
    "by steven klein, hard-edged fashion glamour": "史蒂文·克莱因风格，硬边时尚魅惑",
    "by peter lindbergh, minimalist monochrome fashion": "彼得·林德伯格风格，极简黑白时尚",
    "by wolfgang tillmans, candid on-camera-flash snapshot": "沃尔夫冈·提尔曼斯风格，直闪快照",
    "by ryan mcginley, sun-flared candid youth": "瑞安·麦金莱风格，眩光抓拍青春",
    "by tyler mitchell, soft-light contemporary portraiture": "泰勒·米切尔风格，柔光当代人像",
    "by petra collins, dreamy pink-saturated 35mm": "佩特拉·柯林斯风格，梦幻粉色饱和 35mm",
    # illustrator / documentary
    "by stefan gesell, dark surreal portraiture": "斯特凡·格塞尔风格，黑暗超现实人像",
    "by peter gric, architectural surrealist landscape": "彼得·格里奇风格，建筑超现实风景",
    "by diane arbus, stark confrontational portraiture": "黛安·阿布斯风格，刺眼对抗人像",

    # ============== color-look (24 terms) ==============
    # film-emulation
    "fuji pro 400h film stock emulation": "富士 Pro 400H 胶片模拟",
    "cinestill 800t film stock emulation": "Cinestill 800T 胶片模拟",
    "three-strip technicolor": "三色分离特艺彩色",
    "two-strip technicolor emulation": "两色分离特艺彩色模拟",
    "eastman color film stock emulation": "伊士曼彩色胶片模拟",
    "orwo film stock": "ORWO 胶片",
    "graded with a kodachrome 64 film palette": "柯达柯达克罗姆 64 调色",
    "ektachrome 100 slide film emulation": "柯达 Ektachrome 100 幻灯片模拟",
    "kodak tri-x 400 black-and-white film": "柯达 Tri-X 400 黑白胶片",
    "cinestill 50d daylight-balanced cinema film emulation": "Cinestill 50D 日光平衡电影胶片模拟",
    # post-process
    "heavy black vignette circumscribing the subject in a dramatic dark ring": "重型黑色暗角戏剧黑环环绕主体",
    "heavy coarse grain like push-processed high-iso film": "粗重颗粒如推压高 ISO 胶片",
    "warm orange light leak streaking across one edge of the frame": "暖橙光泄露条纹划过画面一边",
    "medium format analog texture": "中画幅模拟质感",
    "scratched, dusty film emulsion": "划痕灰尘胶片乳剂",
    "subtle color fringing": "微妙色散边缘",
    "the whole scene bathed in soft golden light": "整个画面沐浴在柔和金光中",
    "mid-tone clarity enhancement with increased local contrast": "中调清晰度增强与局部对比",
    "three-way lift gamma gain grade": "三向 Lift Gamma Gain 红绿调节",
    # palette
    "pastel color palette": "粉彩调色板",
    "high contrast color grade": "高对比度色彩分级",
    "vibrant saturated color palette": "鲜艳饱和调色板",
    # social-preset
    "iphone computational hdr look with extended highlight range": "iPhone 计算 HDR 高光范围效果",
    "warm lifestyle magazine grade": "暖色生活方式杂志调",

    # ============== character-fx (20 terms) ==============
    # power
    "the subject's hands trace through the air and a visible swirling magical rune circle appears": "主体手指空中画出魔法符文阵",
    "the subject's hand gestures pull a ribbon of water into the air": "主体手势将水带抽入空中",
    "the subject stomps or gestures downward and slabs of stone orbitate and shield them": "主体踏地手势下压石板环绕成盾",
    "the subject rises slowly off the ground in a controlled vertical hover": "主体缓缓离地垂直悬停",
    "the subject extends a hand and nearby objects rise into the air telekinetically": "主体伸手附近物体念力悬浮",
    "the subject's body fades into transparency with a faint refractive outline": "主体身体淡入透明仅留折射轮廓",
    "superhero flight takeoff": "超级英雄起飞",
    "the subject blurs into super-fast motion leaving multiple translucent trail-frames": "主体化为超速残影",
    # aura-ambient
    "the subject stands or moves while multiple camera flash bursts strobe around them": "主体站立时一连串闪光灯同步亮闪",
    "the subject stands or moves through a slow-motion cascade of falling petals": "主体慢动作花瓣瀑中穿行",
    "flames lick and curl around the subject's body without burning them": "未伤主体的火焰环绕",
    "dark shadow tendrils swirl and writhe around the subject's body": "黑暗影鞭环绕主体",
    "tiny glowing fairies": "微型发光精灵",
    # face-expression
    "a red and gold oni demon mask materializes and slides into place over the subject's face": "红金鬼面具在主体脸上浮现就位",
    "the subject's eyes ignite with a brilliant internal glow — without affecting the rest of their face": "主体双眼鬼力发光而脸庞如常",
    "the subject's body becomes semi-transparent in x-ray style": "主体身体以 X 光风格半透明",
    "a futuristic cybernetic visor materializes across the subject's eyes": "未来赛博格视镜浮现于主体眼上",
    # transformation
    "the subject's skin peels open along seams to reveal glowing circuitry beneath": "主体皮肤沿缝隙剥开显露发光线路",
    "the subject becomes translucent and ethereal": "主体化为半透明虚无",
    "the subject's body dissolves into a swirling cloud of coloured smoke": "主体化为彩色烟雾漩涡",

    # ============== framing (25 terms) ==============
    # composition
    "tight headroom": "紧凑顶部留白",
    "3x3 grid collage, nine equal panels": "3x3 网格拼贴九等格",
    "diptych composition": "双联画构图",
    "triptych composition": "三联画构图",
    "photo mosaic built from small image tiles": "小图块拼贴马赛克",
    "contact sheet layout": "接触印片布局",
    "magazine spread layout": "杂志跨页布局",
    "cutaway cross-section, near surface removed": "切开横截面，移除近表面",
    "s-curve composition": "S 型曲线构图",
    "diagonal composition": "对角构图",
    "triangular composition": "三角构图",
    # coverage
    "clean single, one subject in frame": "干净单人镜头，画面中一名主体",
    "three-shot": "三人镜头",
    "reverse shot": "反打镜头",
    "arm's-length selfie framing": "一臂之距自拍构图",
    "shot through a pane of glass": "透过玻璃拍摄",
    "dirty single, foreground shoulder in frame": "杂乱单人镜头，前景肩部入画",
    # shot-size
    "big close-up, chin to forehead": "大特写，下巴至额头",
    "choker shot, head and neck only": "颈部特写，仅头颈",
    "insert shot": "插入镜头",
    "head-to-hip framing": "头到胯部构图",
    "half-body portrait": "半身人像",
    # angle
    "overhead shot, looking straight down": "俯拍镜头，正直向下",
    "slightly downward angle, just above the eyeline": "微俯视角度，仅高于眼线",
    # vantage
    "front-on view, subject facing camera": "正面视角，主体面向镜头",

    # ============== character (110 terms) ==============
    # expression
    "smug expression": "自鸣得意表情",
    "skeptical look": "怀疑神情",
    "confident smile": "自信微笑",
    "nervous expression": "紧张表情",
    "tired look": "疲倦神情",
    "yawning": "打哈欠",
    "winking": "眨眼",
    "derpy expression": "呆傻表情",
    "speechless": "失语",
    "arrogant look": "傲慢神情",
    "tsundere expression": "傲娇表情",
    "yandere expression": "病娇表情",
    "kuudere expression": "冷娇表情",
    "deredere expression": "娇羞表情",
    "menhera": "精神弱",
    "stern look": "严厉神情",
    "gentle smile": "温柔微笑",
    "wicked smile": "邪恶微笑",
    "foolish smile": "傻笑",
    "evil smile": "邪笑",
    "blood": "血迹",
    "scratches": "划痕",
    "forehead vein": "额上青筋",
    "smug": "自得",
    "flustered": "慌乱",
    "imouto face": "妹妹脸",
    # clothing
    "mukuroizumi skirt": "深褶裙",
    "jumper skirt": "背带裙",
    "converse": "匡威",
    "hooded cloak": "连帽斗篷",
    "collared shirt": "带领衬衫",
    "long sleeves": "长袖",
    "short sleeves": "短袖",
    "off-shoulder": "露肩",
    "strapless": "无肩带",
    "gown": "礼服",
    "bikini": "比基尼",
    "fishnets": "网袜",
    "bikini top": "比基尼上衣",
    "no blouse": "无上衣",
    "translucent clothes": "半透明服装",
    "undone collar": "解开的衣领",
    # eyes
    "twitching eye": "抽动眼皮",
    "head tilt": "歪头",
    "teary eyes": "含泪眼睛",
    "dilated pupils": "放大瞳孔",
    "glowing pupils": "发光瞳孔",
    "pupils": "瞳孔",
    "long eyelashes": "长睫毛",
    "eyes closed": "闭眼",
    "monolids": "单眼皮",
    "double eyelids": "双眼皮",
    "droopy eyes": "下垂眼睛",
    "sharp eyes": "锐利眼睛",
    # body
    "large breasts": "大胸",
    "huge breasts": "巨乳",
    "thick thighs": "粗腿",
    "muscular": "肌肉",
    "skinny": "瘦",
    "petite": "娇小",
    "tall": "高挑",
    "chubby": "丰满",
    "child body": "童体",
    # bodyType
    "curvy body": "曲线身材",
    "petite frame": "娇小身材",
    "tall and slender": "高挑纤细",
    "stocky build": "敦实身材",
    "lean physique": "精瘦身段",
    "heavyset": "厚重体格",
    "toned body": "健美身材",
    "athletic physique": "运动体型",
    # skin
    "pale skin": "白皙皮肤",
    "fair skin": "白皙皮肤",
    "olive skin": "橄榄色皮肤",
    "tan skin": "晒黑皮肤",
    "dark skin": "深色皮肤",
    "ebony skin": "黝黑皮肤",
    "warm skin tone": "暖色肤色",
    "cool skin tone": "冷色肤色",
    # accessories
    "bow on head": "头部蝴蝶结",
    "headphone driver": "耳机驱动器",
    "one-eyed glass": "单片眼镜",
    "bandaged face": "包扎的脸",
    "mouth mask": "口罩",
    "weapon": "武器",
    "gun": "枪",
    "bell": "铃铛",
    # hair
    "neatly styled hair": "发型整洁",
    "hair over shoulder": "头发搭肩",
    "hair pulled back": "头发后梳",
    "hair covering one eye": "头发遮眼",
    "olive hair": "橄榄色头发",
    "single hair strand": "单缕发丝",
    # anatomy
    "perfect anatomy": "完美解剖",
    "beautiful face": "美丽的脸",
    "perfect facial symmetry": "完美面部对称",
    "clean anatomy": "干净解剖",
    "accurate proportions": "准确比例",
    "cleavage": "乳沟",
    # age
    "pre-teen": "学龄前",
    "middle-aged": "中年",
    "immortal looking": "不老外貌",
    "ageless": "不老",
    "baby": "婴儿",
    # face
    "dark circles under eyes": "黑眼圈",
    "freckles": "雀斑",
    # composition
    "moresolo": "更单人",
    "from side": "从侧面",
    # eyeColors
    "cat-like pupils": "猫瞳",
    # effects
    "wings-magic": "魔法之翼",

    # ============== quality (44 terms) ==============
    # advanced
    "professional grade": "专业级",
    "finely detailed": "精细细节",
    "premium quality": "顶级质量",
    "finely painted": "精细绘制",
    "smooth shading": "平滑阴影",
    "masterful coloring": "精湛上色",
    "best masterpiece": "最佳杰作",
    "awards winner": "获奖作品",
    "front page": "头版",
    "trending art": "热门艺术",
    "inquire within": "请询问",
    # texture
    "highly detailed face": "细致面部",
    "refined details": "精致细节",
    "perfect anatomy": "完美解剖",
    "perfect hands": "完美双手",
    "detailed feet": "细致脚部",
    "realistic anatomy": "逼真解剖",
    "delicate lips": "精致嘴唇",
    "perfectly drawn": "完美绘制",
    # technical
    "film look": "胶片感",
    "cinematic look": "电影感",
    "studio quality": "影棚质量",
    "porcelain skin": "瓷器皮肤",
    "skin details": "皮肤细节",
    "detailed skin": "细致皮肤",
    # animeSpecific
    "vivid colors": "鲜艳颜色",
    "official art": "官方艺术",
    "clean lineart": "干净线稿",
    "smooth coloring": "平滑上色",
    # composition
    "balanced composition": "平衡构图",
    "upper body": "上半身",
    "three-quarter shot": "四分之三镜头",
    "visual story": "视觉故事",
    # color
    "rich colors": "丰富色彩",
    "color splash": "色彩飞溅",
    "colorful background": "彩色背景",
    "gradient background": "渐变背景",
    # basic
    "highly detailed": "高细节",
    "raw photo": "RAW 照片",
    "super details": "超级细节",
    # anime
    "clean coloring": "干净上色",
    "detailed background": "细致背景",
    "elaborate background": "精细背景",
    # atmosphere
    "dreamy atmosphere": "梦幻氛围",

    # ============== render-quality (14 terms) ==============
    # other
    "rendered in houdini mantra": "Houdini Mantra 渲染",
    "rendered in solid angle arnold": "Solid Angle Arnold 渲染",
    "rendered in chaos corona": "Chaos Corona 渲染",
    "aces color space": "ACES 色彩空间",
    "ray-traced rendering": "光线追踪渲染",
    "neural-network ai-upscaled detail enhancement": "神经网络 AI 升采样增强细节",
    # resolution
    "8k ultra-high-definition resolution": "8K 超高清分辨率",
    "4k uhd resolution": "4K UHD 分辨率",
    "16k resolution": "16K 分辨率",
    # engines
    "rendered in blender cycles": "Blender Cycles 渲染",
    "rendered in chaos v-ray": "Chaos V-Ray 渲染",
    # stamps
    "raw photograph aesthetic": "RAW 摄影美学",
    "masterpiece-quality rendering": "杰作品质渲染",
    # technical
    "denoised render": "降噪渲染",

    # ============== era (7 terms) ==============
    "set in the renaissance era — velvet doublets": "文艺复兴 — 天鹅绒紧身上衣",
    "set in the victorian era — corseted bustled gowns": "维多利亚 — 紧身胸衣撑裙礼服",
    "set in the edwardian era — high-collared tea dresses": "爱德华 — 高领茶服",
    "set in ancient rome — draped togas": "古罗马 — 披挂托加袍",
    "set in feudal japan — layered kimono": "日本封建 — 多层和服",
    "set in the 1960s mod era — geometric a-line dresses": "1960 年代摩登 — 几何 A 字裙",
    "set in the 1980s neon era — power-shoulder blazers": "1980 年代霓虹 — 强肩西装外套",

    # ============== action-fx (21 terms) ==============
    # disaster
    "a towering sandstorm wall of orange-brown dust engulfing the scene": "高耸橙褐色沙尘暴墙吞没画面",
    "falling volcanic ash": "落下的火山灰",
    "a violent hailstorm pummeling the scene": "猛烈冰雹暴击打画面",
    "two blades clashing together at the moment of impact": "双刃撞击瞬间相撞",
    "an antimatter annihilation flash": "反物质湮灭闪光",
    # electric
    "a continuous high-voltage plasma arc crackling between two points": "两点间持续高压等离子电弧嗞嗞作响",
    "a compact taser-style electric discharge crackling on contact": "紧凑型电击枪放电嗞嗞作响",
    "a sudden electric discharge bursting from a malfunctioning device": "突然电气放电从故障设备喷出",
    "a small static shock burst visible at point of contact": "接触点小静电冲击爆发",
    "lightning magic arcing from a caster's outstretched hands": "施法者伸手指尖雷电魔法弧",
    # misc
    "a tall vertical column of dense black smoke rising into the air": "高耸浓密黑烟柱升入空中",
    "an eerie st. elmo's fire phenomenon": "诡异圣艾尔摩之火现象",
    "a smoke grenade billowing colored smoke outward": "烟雾弹向四周喷吐彩色烟雾",
    "an ominous dark vortex swirling in the scene": "不祥黑暗漩涡在画面中旋转",
    # combat
    "a visible shockwave expanding at ground level": "可见冲击波在地面扩散",
    "a sonic boom cone of compressed air visible around a supersonic object": "音爆压缩空气锥环绕超声速物体",
    "a cinematic arc of blood droplets spraying outward in slow-motion": "电影感血弧滴慢动作飞溅",
    "arrow impact sparks": "箭矢撞击火花",
    # fire-blasts
    "a massive explosion erupting in the scene with a building-level fireball": "巨型爆炸引发建筑级火球",
    "explosion of white-gold light": "白金光芒爆炸",
    # sci-fi
    "a translucent holographic projection flickering and glitching": "半透明全息投影闪烁与故障",

    # ============== panel (18 terms) ==============
    # comicEffects
    "speech balloon": "对话气泡",
    "focus line": "聚焦线",
    "radial lines": "放射线",
    "flash background": "闪光背景",
    "abstract background": "抽象背景",
    "narration box": "叙述框",
    "chapter title": "章节标题",
    # animation
    "hold frame": "定格帧",
    "animated pose": "动画姿势",
    "limited animation": "有限动画",
    "full animation": "全动画",
    "center of gravity shift": "重心偏移",
    "weight shift pose": "重心偏移姿势",
    "secondary action": "次要动作",
    # panelMood
    "reveal panel": "揭示分镜",
    "cliffhanger panel": "悬念分镜",
    "emotional climax": "情感高潮",
    "transition panel": "过渡分镜",

    # ============== transitions (15 terms) ==============
    # portal
    "the camera pushes toward a pane of glass in the scene": "镜头推向场景中的玻璃",
    "soul leaves body and enters another": "灵魂离体进入另一身体",
    "mask transition": "面具过渡",
    "zoom-through transition": "推进过渡",
    # standard
    "linear wipe": "线性擦除",
    "whip pan": "抡抡镜头",
    "jump cut": "跳切",
    # element
    "vivid splashes of coloured paint fly across the frame in arcs": "鲜艳彩色颜料弧线飞过画面",
    "a luminous curtain of green and violet aurora light ripples across the frame": "绿紫极光幕在画面中涟漪",
    "lush flowers and vines rapidly grow and bloom outward from the subject": "繁花藤蔓从主体快速生长绽放",
    # physics
    "match cut on a jump": "跳跃匹配剪辑",
    "a hand sweeps across the camera lens at close range": "手近距掠过镜头",
    "match cut on action": "动作匹配剪辑",
    # morph
    "melt into...": "融入...",
}


def inject_translations(filepath, new_entries):
    import re as _re
    import sys as _sys

    content = None
    content = None
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        print(f"FAILED to read {filepath}: {e}")
        _sys.exit(1)


    start_marker = "PRE_TRANSLATIONS = {"
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print(f"❌ PRE_TRANSLATIONS not found")
        return

    i = start_idx + len(start_marker) - 1
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

    existing = {}
    for k, v in _re.findall(r'"([^"]+)":\s*"([^"]+)"', dict_str):
        existing[k] = v

    added = 0
    skipped = 0
    for k, v in new_entries.items():
        if k in existing:
            skipped += 1
        else:
            existing[k] = v
            added += 1

    new_lines = []
    for k, v in sorted(existing.items()):
        v_safe = v.replace('"', '\\"')
        new_lines.append(f'    "{k}": "{v_safe}",')

    new_dict_str = '{\n' + '\n'.join(new_lines) + '\n}'
    new_content = before + 'PRE_TRANSLATIONS = ' + new_dict_str + after

    content = None
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    except OSError as e:
        print(f'FAILED to write {filepath}: {e}')
        _sys.exit(1)

    print(f"✅ Added {added} new entries, skipped {skipped} duplicates (file now has {len(existing)} unique entries)")


if __name__ == "__main__":
    import os as _os
    repo_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    target = _os.path.join(repo_root, "tools", "pws-translate.py")
    inject_translations(target, EXTRA_TRANSLATIONS_10)