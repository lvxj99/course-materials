"""Figures for 9-11 and the added explainers: scaling, multimodal, MoE, agent, RAG."""

from __future__ import annotations

import math

from .common import *  # noqa: F401,F403
from figkit import Axes, P, Canvas, tw


# ---------------------------------------------------------------------------
# 21 — three scaling paths
# ---------------------------------------------------------------------------

def f21():
    c = Canvas(960, 520)
    c.text(40, 34, "扩展能力的三条路径：把算力花在训练、后训练，还是推理时的求解上",
           size=11.5, fill=P["ink2"], weight="600")

    # ---------------- A: pretraining
    ax = Axes(c, 74, 96, 236, 226, xlim=(1e19, 1e23), ylim=(1.6, 2.8), xlog=True,
              ylog=True, xlabel="训练算力（FLOPs）", ylabel="验证损失",
              xticks=[1e19, 1e21, 1e23], yticks=[1.7, 2.0, 2.4, 2.8],
              xtick_labels=["10¹⁹", "10²¹", "10²³"])
    ax.line([(1e19, 2.72), (1e23, 2.30)], color=P["orange"], sw=2)
    ax.line([(1e19, 2.72), (1e23, 1.72)], color=P["blue"], sw=2)
    c.text(150, 124, "数据不足", size=9.5, fill=P["orange"])
    c.text(150, 258, "数据充足", size=9.5, fill=P["blue"])
    c.text(40, 56, "A  预训练", size=11, fill=P["blue"], weight="600")
    c.text(40, 74, "同样的算力，数据越多，损失还能继续降", size=9.8, fill=P["muted"])
    c.text(74, 378, "Chinchilla：约 20 个 token 对应 1 个参数；", size=9.5, fill=P["muted"])
    c.text(74, 394, "只放大模型、不放大数据，收益会很快变平。", size=9.5, fill=P["muted"])

    # ---------------- B: post-training
    c.text(360, 56, "B  后训练", size=11, fill=P["violet"], weight="600")
    c.text(360, 74, "同样的基座，用不同的信号调整行为", size=9.8, fill=P["muted"])
    bx, by, bw = 372, 330, 236
    stages = [("基座", P["panel2"], P["faint"]), ("SFT", P["violetL"], P["violetM"]),
              ("偏好", P["violetL"], P["violet"]), ("RLVR", P["violetL"], P["violet"])]
    heights = [0.35, 0.55, 0.72, 0.9]
    step_w = bw / 4
    for i, (name, fill, stroke) in enumerate(stages):
        h = 150 * heights[i]
        c.rect(bx + i * step_w, by - h, step_w - 6, h, fill=fill, stroke=stroke, rx=3,
               sw=1)
        c.text(bx + i * step_w + (step_w - 6) / 2, by + 16, name, size=9.8,
               fill=P["ink2"], anchor="middle")
    c.line(bx, by, bx + bw, by, stroke=P["ink2"], sw=1)
    c.text(360, 378, "信号依次是：下一个 token、示范答案、偏好比较、可验证奖励。",
           size=9.5, fill=P["muted"])
    c.text(360, 394, "每一阶段都在同一份权重上继续训练。", size=9.5, fill=P["muted"])

    # ---------------- C: test-time
    ax2 = Axes(c, 704, 96, 216, 226, xlim=(1, 256), ylim=(0, 1), xlog=True,
               xlabel="推理时计算（相对）", ylabel="正确率",
               xticks=[1, 4, 16, 64, 256], yticks=[0, 0.5, 1])
    easy = [(x / 10, 0.95 - 0.55 * math.exp(-(x / 10) / 1.4)) for x in range(1, 257)]
    hard = [(x / 10, 0.82 - 0.62 * math.exp(-(x / 10) / 12)) for x in range(1, 257)]
    ax2.line(easy, color=P["teal"], sw=2)
    ax2.line(hard, color=P["red"], sw=2)
    c.text(760, 132, "简单题", size=9.5, fill=P["teal"])
    c.text(860, 250, "难题", size=9.5, fill=P["red"])
    c.text(672, 56, "C  推理时计算", size=11, fill=P["teal"], weight="600")
    c.text(672, 74, "同样的模型，多花推理算力换正确率", size=9.8, fill=P["muted"])
    c.text(672, 378, "更长推导、更多候选、验证器筛选；", size=9.5, fill=P["muted"])
    c.text(672, 394, "收益递减，且难题的收益窗口更靠后。", size=9.5, fill=P["muted"])

    c.text(40, 452, "三条路径可以叠加：更大的基座、更好的后训练、更充分的推理时求解。"
                    "判断该往哪儿投入，要看当前瓶颈在哪一段。",
           size=10.8, fill=P["ink2"])
    c.text(40, 474, "图中曲线为示意，用来比较趋势与边际收益，不是某一具体模型的实测数值。",
           size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 22 — multimodal model
# ---------------------------------------------------------------------------

def f22():
    c = Canvas(960, 520)
    c.text(40, 34, "不同模态先各自编码成 token，再进入同一个 Transformer", size=11.5,
           fill=P["ink2"], weight="600")

    lanes = [190, 266, 340]
    mod = ["文字", "图像", "音频"]

    # token block
    c.rect(470, 150, 210, 232, fill=P["white"], stroke=P["rule"], rx=8)
    c.text(575, 142, "统一 token 序列", size=10, fill=P["muted"], anchor="middle")
    for i, yc in enumerate(lanes):
        band = P["panel2"] if i == 0 else (P["blueL"] if i == 1 else P["tealL"])
        c.rect(478, yc - 28, 194, 56, fill=band, stroke="none", rx=4)
        if i == 0:
            for k, w in enumerate(["比较", "两条", "曲线", "变化"]):
                c.rect(486 + k * 46, yc - 20, 40, 40, fill=P["white"], stroke=P["rule"],
                       rx=3)
                c.text(506 + k * 46, yc + 3.5, w, size=9, fill=P["ink2"], anchor="middle")
        else:
            for k in range(8):
                c.rect(486 + k * 23, yc - 20, 19, 40,
                       fill=P["blueM"] if i == 1 else P["tealM"], stroke="none", rx=2)

    # inputs
    c.rect(40, lanes[0] - 34, 130, 68, fill=P["panel"], stroke=P["rule"], rx=6)
    c.text(105, lanes[0] - 6, "比较这两条", size=10.5, fill=P["ink2"], anchor="middle")
    c.text(105, lanes[0] + 12, "曲线的变化", size=10.5, fill=P["ink2"], anchor="middle")

    c.rect(40, lanes[1] - 34, 130, 68, fill=P["panel"], stroke=P["rule"], rx=6)
    for k in range(4):
        for j in range(3):
            c.rect(52 + j * 13, lanes[1] - 26 + k * 14, 11, 12, fill=P["blueM"],
                   stroke="none", rx=2)
    px = [58, 72, 80, 94, 102, 116, 124, 138]
    py = [lanes[1] + 22, lanes[1] + 10, lanes[1] + 18, lanes[1] - 2, lanes[1] + 6,
          lanes[1] - 8, lanes[1] + 2, lanes[1] - 12]
    c.polyline(list(zip(px, py)), stroke=P["blue"], sw=1.4)

    c.rect(40, lanes[2] - 34, 130, 68, fill=P["panel"], stroke=P["rule"], rx=6)
    for k in range(18):
        hh = 8 + 16 * abs(math.sin(k * 1.7)) + 4 * abs(math.sin(k * 0.6))
        c.line(52 + k * 6.6, lanes[2] - hh / 2, 52 + k * 6.6, lanes[2] + hh / 2,
               stroke=P["teal"], sw=1.2)

    # encoders + projectors
    encs = [("分词 + 嵌入", "tokenizer / embedding", P["panel2"], P["rule"], P["ink2"]),
            ("视觉编码器", "ViT：patch → 向量", P["blueL"], P["blueM"], P["blue"]),
            ("音频编码器", "声谱图 / 特征", P["tealL"], P["tealM"], P["teal"])]
    for i, (l1, l2, fill, stroke, col) in enumerate(encs):
        yc = lanes[i]
        c.rect(196, yc - 31, 154, 62, fill=fill, stroke=stroke, rx=6)
        c.text(273, yc - 4, l1, size=10.5, fill=col, anchor="middle", weight="600")
        c.text(273, yc + 14, l2, size=9, fill=P["ink2"], anchor="middle")
        c.arrow(172, yc, 192, yc, color=P["faint"], sw=1.1, head=4)
        c.rect(366, yc - 22, 64, 44, fill=P["white"], stroke=P["rule"], rx=5, dash="3 3")
        c.text(398, yc + 3.5, "投影", size=9.5, fill=P["muted"], anchor="middle")
        c.arrow(352, yc, 362, yc, color=P["faint"], sw=1.1, head=4)
        c.arrow(432, yc, 466, yc, color=P["faint"], sw=1.1, head=4)

    # backbone
    c.rect(712, 140, 176, 250, fill=P["violetL"], stroke=P["violetM"], rx=8)
    c.text(800, 176, "LLM backbone", size=12, fill=P["violet"], anchor="middle",
           weight="600")
    c.text(800, 196, "Transformer blocks", size=9.5, fill=P["violet"], anchor="middle")
    for k in range(3):
        c.rect(736, 214 + k * 40, 128, 30, fill=P["white"], stroke=P["violetM"], rx=4)
        c.text(800, 233 + k * 40, "自注意力 + FFN", size=9, fill=P["ink2"],
               anchor="middle")
    c.text(800, 372, "同一个网络处理所有模态的 token", size=8.8, fill=P["violet"],
           anchor="middle")
    c.arrow(682, 266, 708, 266, color=P["violet"], sw=1.4, head=5)

    c.rect(712, 418, 176, 52, fill=P["panel2"], stroke=P["rule"], rx=6)
    c.text(800, 440, "文字回答", size=10.5, fill=P["ink2"], anchor="middle", weight="600")
    c.text(800, 457, "例如指出哪条曲线上升更快", size=8.8, fill=P["muted"], anchor="middle")
    c.arrow(800, 390, 800, 414, color=P["violet"], sw=1.4, head=5)

    c.text(40, 492, "各模态的编码器与投影层独立，进入 backbone 后共享同一套注意力和 FFN；"
                    "训练数据是图文、音文、视频说明等配对材料。",
           size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 23 — mixture of experts
# ---------------------------------------------------------------------------

def f23():
    c = Canvas(960, 470)
    c.text(40, 34, "每个 token 只经过少数专家：容量按总参数算，计算按激活参数算",
           size=11.5, fill=P["ink2"], weight="600")

    toks = ["token 1", "token 2", "token 3"]
    for i, t in enumerate(toks):
        c.rect(40, 110 + i * 54, 96, 34, fill=P["panel2"], stroke=P["rule"], rx=4)
        c.text(88, 132 + i * 54, t, size=9.8, fill=P["ink2"], anchor="middle")
        c.arrow(140, 127 + i * 54, 190, 200, color=P["faint"], sw=1.0, head=4,
                curve=-8)

    c.rect(196, 164, 110, 84, fill=P["violetL"], stroke=P["violetM"], rx=6)
    c.text(251, 188, "Router", size=11, fill=P["violet"], anchor="middle", weight="600")
    c.text(251, 206, "为每个 token", size=9, fill=P["violet"], anchor="middle")
    c.text(251, 220, "给出专家权重", size=9, fill=P["violet"], anchor="middle")
    c.text(251, 236, "取 top-2", size=9, fill=P["muted"], anchor="middle")

    experts = [(360, 84), (360, 158), (360, 232), (360, 306)]
    for i, (x, y) in enumerate(experts):
        act = i in (1, 2)
        c.rect(x, y, 150, 56, fill=P["violetL"] if act else P["panel"],
               stroke=P["violet"] if act else P["rule"], rx=6,
               sw=1.4 if act else 1)
        c.text(x + 75, y + 24, f"专家 {i+1}", size=10.5,
               fill=P["violet"] if act else P["muted"], anchor="middle", weight="600")
        c.text(x + 75, y + 41, "FFN", size=9, fill=P["muted"], anchor="middle")
        if act:
            c.arrow(310, 206, x - 2, y + 28, color=P["violet"], sw=1.3, head=5, curve=6)
            c.text(330, y + 20, "0.7" if i == 1 else "0.3", size=9, fill=P["violet"])

    # merge
    c.circle(556, 206, 11, fill=P["white"], stroke=P["violet"], sw=1.2)
    c.text(556, 211, "+", size=12, fill=P["violet"], anchor="middle")
    for i, (x, y) in enumerate(experts):
        if i in (1, 2):
            c.arrow(x + 152, y + 28, 544, 206, color=P["violet"], sw=1.2, head=4)
    c.arrow(570, 206, 612, 206, color=P["muted"], sw=1.2, head=5)
    c.rect(616, 176, 150, 60, fill=P["panel2"], stroke=P["rule"], rx=6)
    c.text(691, 200, "输出 T×d", size=10.5, fill=P["ink2"], anchor="middle", weight="600")
    c.text(691, 218, "进入下一层", size=9, fill=P["muted"], anchor="middle")

    # parameters box
    c.rect(616, 268, 300, 104, fill=P["white"], stroke=P["rule"], rx=8)
    c.text(632, 292, "总参数量", size=9.8, fill=P["muted"])
    c.text(632, 310, "全部专家 + 共享层", size=10.5, fill=P["ink2"])
    c.text(632, 336, "激活参数量", size=9.8, fill=P["muted"])
    c.text(632, 354, "每个 token 实际调用的那部分", size=10.5, fill=P["violet"])

    c.text(40, 398, "例：DeepSeek-V4-Pro 保存约 1.6T 参数，每个 token 激活约 49B。"
                    "“大容量、小计算”是 MoE 的核心权衡。",
           size=10.5, fill=P["ink2"])
    c.text(40, 420, "代价：专家之间要交换数据（通信）、需要负载均衡，"
                    "路由本身也有计算开销；实际速度取决于执行方式与硬件。",
           size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 26 — agent loop
# ---------------------------------------------------------------------------

def f26():
    c = Canvas(960, 540)
    c.text(40, 34, "围绕目标反复「规划 → 执行 → 观察」，直到任务完成", size=11.5,
           fill=P["ink2"], weight="600")

    cx, cy = 420, 240
    c.rect(cx - 76, cy - 40, 152, 80, fill=P["violetL"], stroke=P["violetM"], rx=10)
    c.text(cx, cy - 12, "LLM", size=14, fill=P["violet"], anchor="middle", weight="600")
    c.text(cx, cy + 8, "理解 · 生成", size=9.5, fill=P["violet"], anchor="middle")
    c.text(cx, cy + 26, "决定下一步做什么", size=9, fill=P["muted"], anchor="middle")

    nodes = [
        (420, 100, "① 感知", "读入任务、文件、环境状态", P["blue"], P["blueL"], P["blueM"]),
        (610, 240, "② 规划", "拆解步骤、选择工具", P["violet"], P["violetL"], P["violetM"]),
        (420, 380, "③ 执行", "调用工具、运行代码", P["orange"], P["orangeL"], P["orangeM"]),
        (230, 240, "④ 观察", "检查结果、更新状态", P["teal"], P["tealL"], P["tealM"]),
    ]
    for (x, y, t1, t2, col, fill, stroke) in nodes:
        c.rect(x - 95, y - 31, 190, 62, fill=fill, stroke=stroke, rx=8)
        c.text(x, y - 6, t1, size=11.5, fill=col, anchor="middle", weight="600")
        c.text(x, y + 13, t2, size=9.3, fill=P["ink2"], anchor="middle")

    # clockwise loop: 感知 -> 规划 -> 执行 -> 观察 -> 感知
    c.arrow(516, 112, 601, 207, color=P["muted"], sw=1.3, head=6, curve=-26)
    c.arrow(601, 273, 516, 368, color=P["muted"], sw=1.3, head=6, curve=-26)
    c.arrow(324, 368, 239, 273, color=P["muted"], sw=1.3, head=6, curve=-26)
    c.arrow(239, 207, 324, 112, color=P["muted"], sw=1.3, head=6, curve=-26)

    # tools panel
    c.rect(740, 170, 190, 150, fill=P["panel"], stroke=P["rule"], rx=8)
    c.text(756, 194, "工具与执行环境", size=10, fill=P["ink2"], weight="600")
    tools = ["搜索 / 浏览器", "文件读写", "Python / shell", "数据库 / API"]
    for i, t in enumerate(tools):
        c.rect(752, 206 + i * 27, 166, 22, fill=P["white"], stroke=P["rule"], rx=4)
        c.text(835, 221 + i * 27, t, size=8.8, fill=P["ink2"], anchor="middle")

    c.text(40, 452, "例：给定一份数据和分析目标 → 读文件 → 写并运行分析脚本 → 检查输出 → "
                    "修正 → 整理成报告。",
           size=10.5, fill=P["ink2"])
    c.text(40, 474, "与单次问答的区别：模型的动作会改变外部状态，下一步要依据真实结果调整；"
                    "失败也提供信息。",
           size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 30 — RAG pipeline
# ---------------------------------------------------------------------------

def f30():
    c = Canvas(960, 400)
    c.text(40, 34, "检索增强生成：先找出相关片段，再把它们放进上下文", size=11.5,
           fill=P["ink2"], weight="600")

    y1, h1 = 96, 62
    steps = [
        (30, 120, "问题", P["panel"], P["rule"], P["ink2"]),
        (180, 180, "检索器", P["blueL"], P["blueM"], P["blue"]),
        (390, 140, "top-k 片段", P["blueL"], P["blueM"], P["blue"]),
        (560, 150, "拼装 prompt", P["violetL"], P["violetM"], P["violet"]),
        (740, 120, "LLM", P["violetL"], P["violetM"], P["violet"]),
    ]
    subs = {180: "向量相似度检索", 390: "取相关度最高的几段", 560: "问题 + 片段 + 指令"}
    for (x, w, label, fill, stroke, col) in steps:
        c.rect(x, y1, w, h1, fill=fill, stroke=stroke, rx=6)
        c.text(x + w / 2, y1 + 26, label, size=10.5, fill=col, anchor="middle",
               weight="600")
        if x in subs:
            c.text(x + w / 2, y1 + 44, subs[x], size=8.6, fill=P["ink2"], anchor="middle")
    for a, b in [(150, 180), (360, 390), (530, 560), (710, 740)]:
        c.arrow(a + 2, y1 + h1 / 2, b - 2, y1 + h1 / 2, color=P["muted"], sw=1.2, head=5)

    c.rect(884, y1, 56, h1, fill=P["panel2"], stroke=P["rule"], rx=6)
    c.text(912, y1 + 30, "回答", size=9.5, fill=P["ink2"], anchor="middle")
    c.text(912, y1 + 46, "带出处", size=8.5, fill=P["muted"], anchor="middle")
    c.arrow(862, y1 + h1 / 2, 882, y1 + h1 / 2, color=P["muted"], sw=1.2, head=5)

    # offline lane
    y2 = 286
    off = [(30, 130, "文档库", P["panel"], P["rule"], P["ink2"]),
           (190, 130, "切块 chunk", P["panel"], P["rule"], P["ink2"]),
           (350, 140, "嵌入模型", P["tealL"], P["tealM"], P["teal"]),
           (520, 130, "向量索引", P["tealL"], P["tealM"], P["teal"])]
    for (x, w, label, fill, stroke, col) in off:
        c.rect(x, y2, w, 56, fill=fill, stroke=stroke, rx=6)
        c.text(x + w / 2, y2 + 33, label, size=10, fill=col, anchor="middle", weight="600")
    for a, b in [(160, 190), (320, 350), (490, 520)]:
        c.arrow(a + 2, y2 + 28, b - 2, y2 + 28, color=P["muted"], sw=1.2, head=5)

    # indexing feeds the retriever
    c.polyline([(650, y2 + 28), (700, y2 + 28), (700, 220), (270, 220)],
               stroke=P["teal"], sw=1.2, dash="4 3")
    c.arrow(270, 220, 270, 162, color=P["teal"], sw=1.2, head=5, dash="4 3")
    c.text(708, 214, "离线：建索引", size=9.5, fill=P["teal"])

    c.text(40, 372, "检索可以和生成解耦：索引定期更新，问题实时检索；"
                    "片段长度、k 的取值、是否重排，都会影响回答质量与成本。",
           size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 31 — top-k and top-p
# ---------------------------------------------------------------------------

def f31():
    c = Canvas(960, 420)
    probs = [0.32, 0.24, 0.16, 0.11, 0.07, 0.05, 0.03, 0.02]
    toks = ["的", "了", "是", "在", "和", "有", "不", "就"]
    base, hmax = 300, 170

    def bars(x0, keep, col_on, col_off):
        for i, p in enumerate(probs):
            h = hmax * p / 0.32
            on = i < keep
            c.rect(x0 + i * 44, base - h, 34, h,
                   fill=col_on if on else P["panel2"],
                   stroke=P["blue"] if on else P["rule"], rx=2, sw=1)
            c.text(x0 + i * 44 + 17, base - h - 8, f"{p:.2f}", size=8.8,
                   fill=P["ink2"] if on else P["faint"], anchor="middle")
            c.text(x0 + i * 44 + 17, base + 16, toks[i], size=9.5,
                   fill=P["muted"] if not on else P["ink2"], anchor="middle")

    # top-k
    c.text(40, 34, "top-k：只保留概率最高的 k 个候选", size=11.5, fill=P["blue"],
           weight="600")
    bars(60, 4, P["blueM"], P["panel2"])
    c.line(60, base, 60 + 8 * 44 - 10, base, stroke=P["ink2"], sw=1)
    c.line(60 + 4 * 44, 62, 60 + 4 * 44, base, stroke=P["blue"], sw=1.2, dash="4 3")
    c.text(60 + 4 * 44, 52, "k = 4", size=9.5, fill=P["blue"], anchor="middle")
    c.text(60, 340, "截断后重新归一化，再在这 4 个里按概率采样。", size=9.8, fill=P["muted"])

    # top-p
    c.text(520, 34, "top-p：保留累计概率达到 p 的最小集合", size=11.5, fill=P["teal"],
           weight="600")
    x0 = 540
    bars(x0, 5, P["tealM"], P["panel2"])
    c.line(x0, base, x0 + 8 * 44 - 10, base, stroke=P["ink2"], sw=1)

    cum, pts = 0.0, []
    for i, p in enumerate(probs):
        cum += p
        pts.append((x0 + i * 44 + 17, base - 180 * cum))
    c.polyline(pts, stroke=P["teal"], sw=1.6)
    for (px, py) in pts:
        c.circle(px, py, 2.2, fill=P["teal"])
    # right axis for cumulative probability
    c.line(x0 + 8 * 44 + 6, base, x0 + 8 * 44 + 6, base - 180, stroke=P["ink2"], sw=1)
    for v in (0, 0.5, 1.0):
        c.line(x0 + 8 * 44 + 6, base - 180 * v, x0 + 8 * 44 + 10, base - 180 * v,
               stroke=P["ink2"], sw=1)
        c.text(x0 + 8 * 44 + 14, base - 180 * v + 3.5, f"{v:g}", size=8.5, fill=P["muted"])
    c.text(x0 + 8 * 44 + 14, 78, "累计", size=8.5, fill=P["muted"])

    c.line(x0, base - 180 * 0.9, x0 + 8 * 44 + 6, base - 180 * 0.9, stroke=P["teal"],
           sw=1, dash="3 3")
    c.text(x0 + 5 * 44 - 6, 64, "累计 ≥ 0.90 → 保留 5 个", size=9.5, fill=P["teal"],
           anchor="middle")
    c.line(x0 + 5 * 44, 76, x0 + 5 * 44, base, stroke=P["teal"], sw=1.2, dash="4 3")
    c.text(x0 - 20, 340, "候选集合随分布形状变化：分布尖锐时保留少，平缓时保留多。",
           size=9.8, fill=P["muted"])

    c.text(40, 388, "温度先改变分布形状，top-k / top-p 再截断长尾；三者常一起使用。"
                    "贪心解码相当于 k = 1。",
           size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 32 — context window budget
# ---------------------------------------------------------------------------

def f32():
    c = Canvas(960, 380)
    c.text(40, 34, "一次请求的上下文预算：所有内容都要放进同一个窗口", size=11.5,
           fill=P["ink2"], weight="600")

    total, x0, wmax = 8192, 60, 840
    scale = wmax / total
    segs = [("系统提示", 400, P["panel2"], P["muted"]),
            ("检索到的片段", 3600, P["blueL"], P["blue"]),
            ("对话历史", 1800, P["violetL"], P["violet"]),
            ("问题", 200, P["goldL"], P["gold"]),
            ("为生成预留", 2192, P["tealL"], P["teal"])]
    x = x0
    for name, n, fill, col in segs:
        w = n * scale
        c.rect(x, 110, w - 1.5, 64, fill=fill, stroke=col, rx=2, sw=0.8)
        x += w

    x = x0
    small = []
    for i, (name, n, fill, col) in enumerate(segs):
        w = n * scale
        if w > 110:
            c.text(x + w / 2, 138, name, size=9.5, fill=col, anchor="middle", weight="600")
            c.text(x + w / 2, 156, f"{n} tokens", size=8.8, fill=P["ink2"], anchor="middle")
        else:
            small.append((x + w / 2, name, n, col, i))
        x += w
    for (xc, name, n, col, i) in small:
        ly = 200 if i == 0 else 200
        c.line(xc, 176, xc, ly - 10, stroke=col, sw=0.8)
        c.text(xc, ly, f"{name} {n}", size=8.8, fill=col, anchor="middle")

    c.line(x0, 110, x0 + wmax, 110, stroke=P["ink2"], sw=1)
    c.line(x0, 174, x0 + wmax, 174, stroke=P["ink2"], sw=1)
    c.line(x0, 110, x0, 174, stroke=P["ink2"], sw=1)
    c.line(x0 + wmax, 110, x0 + wmax, 174, stroke=P["ink2"], sw=1)
    c.text(x0 + wmax, 100, "窗口上限 8192", size=9.5, fill=P["ink2"], anchor="end")

    # overflow advice
    c.rect(650, 226, 290, 88, fill=P["redL"], stroke=P["redM"], rx=6)
    c.text(666, 250, "超出窗口怎么办？", size=9.8, fill=P["red"], weight="600")
    c.text(666, 270, "截断历史、摘要已读内容、少取几个片段，", size=9, fill=P["ink2"])
    c.text(666, 286, "或改用检索按需取用；长上下文并不能", size=9, fill=P["ink2"])
    c.text(666, 302, "替代检索。", size=9, fill=P["ink2"])

    c.text(60, 236, "同一窗口里，材料、历史与生成空间互相挤占：", size=10.5, fill=P["ink2"])
    c.text(60, 256, "材料越多，能留给生成的余地越小；", size=10.2, fill=P["muted"])
    c.text(60, 276, "把无关内容放进来反而会干扰回答。", size=10.2, fill=P["muted"])

    c.text(60, 348, "计费与限长按 token 数计算，不同 tokenizer 的切分方式不同，"
                    "所以“能放多少页”只能按 token 估算。",
           size=10.2, fill=P["muted"])
    return c


FIGURES = {
    "21_three-scaling-laws": f21,
    "22_multimodal-model-architecture": f22,
    "23_mixture-of-experts-layer": f23,
    "26_agent-iterative-cycle": f26,
    "30_rag-pipeline": f30,
    "31_top-k-and-top-p": f31,
    "32_context-window-budget": f32,
}
