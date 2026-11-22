"""Figures for section 7: original Transformer, attention mechanics, masks."""

from __future__ import annotations

import math

from .common import *  # noqa: F401,F403
from figkit import P, Canvas, tw


# ---------------------------------------------------------------------------
# 01 — original Transformer encoder-decoder architecture
# ---------------------------------------------------------------------------

def f01():
    c = Canvas(960, 620)
    EX, EW = 160, 220
    ECX = EX + EW / 2          # 270
    DX, DW = 610, 220
    DCX = DX + DW / 2          # 720

    def up(x, y0, y1, color=P["muted"], sw=1.2):
        c.arrow(x, y0, x, y1, color=color, sw=sw, head=5)

    # ---------------- encoder ----------------
    chips(c, ECX, 500, ["I", "love", "machine", "learning"], h=26, size=11.5)
    c.text(ECX, 542, "输入（英文）", size=10.8, fill=P["muted"], anchor="middle")
    up(ECX, 500, 486)
    block(c, EX, 452, EW, 34, "Input Embedding", fill=P["panel2"], stroke=P["rule"])
    up(ECX, 452, 435)
    plus_circle(c, ECX, 426)
    tag(c, ECX + 24, 426, "PE", color=P["gold"], bg=P["goldL"], size=9.5, h=15)
    up(ECX, 417, 406)
    block(c, EX, 360, EW, 46, "Multi-Head Attention", "双向自注意力，不加掩码",
          fill=P["blueL"], stroke=P["blueM"], color=P["blue"], color2=P["blue"])
    up(ECX, 360, 348)
    norm_box(c, EX, 326, EW, 22)
    up(ECX, 326, 314)
    block(c, EX, 270, EW, 44, "Feed Forward", "逐位置 MLP",
          fill=P["panel"], stroke=P["rule"])
    up(ECX, 270, 258)
    norm_box(c, EX, 236, EW, 22)

    # encoder out -> decoder cross attention
    c.polyline([(ECX, 236), (ECX, 208), (480, 208), (480, 291)], stroke=P["violet"], sw=1.3)
    c.arrow(480, 291, DX, 291, color=P["violet"], sw=1.3)
    c.text(492, 284, "K, V", size=10.5, fill=P["violet"], weight="600")

    # encoder residual rails (left)
    c.polyline([(ECX, 416), (148, 416), (148, 337)], stroke=P["gold"], sw=1.2)
    c.arrow(148, 337, EX, 337, color=P["gold"], sw=1.2, head=5)
    c.polyline([(ECX, 320), (148, 320), (148, 247)], stroke=P["gold"], sw=1.2)
    c.arrow(148, 247, EX, 247, color=P["gold"], sw=1.2, head=5)

    # encoder group
    c.rect(140, 226, 260, 182, fill="none", stroke=P["blueM"], rx=8, dash="5 4")
    c.rect(150, 219, 104, 15, fill=P["white"])
    c.text(156, 230, "Encoder × 6", size=10.5, fill=P["blue"], weight="600")

    # ---------------- decoder ----------------
    c.text(DCX, 18, "下一个 token 的概率分布", size=10.8, fill=P["muted"], anchor="middle")
    chips(c, DCX, 30, ["我", "喜欢", "机器", "学习"], h=26, size=11.5,
          colors=[P["panel2"]] * 4)
    up(DCX, 68, 60)
    block(c, DX, 72, DW, 24, "Softmax", fill=P["panel2"], stroke=P["rule"], size=11.5)
    up(DCX, 102, 96)
    block(c, DX, 102, DW, 28, "Linear（词表 logits）", fill=P["panel2"], stroke=P["rule"],
          size=11.5)
    up(DCX, 142, 130)

    block(c, DX, 360, DW, 46, "Masked Multi-Head Attention", "自注意力 + 因果掩码",
          fill=P["blueL"], stroke=P["blueM"], color=P["blue"], color2=P["blue"])
    up(DCX, 326, 314)
    norm_box(c, DX, 326, DW, 22)
    up(DCX, 268, 256)
    block(c, DX, 268, DW, 46, "Multi-Head Cross-Attention", "Q ← 解码器；K, V ← 编码器",
          fill=P["violetL"], stroke=P["violetM"], color=P["violet"], color2=P["violet"])
    up(DCX, 234, 222)
    norm_box(c, DX, 234, DW, 22)
    up(DCX, 178, 166)
    block(c, DX, 178, DW, 44, "Feed Forward", "逐位置 MLP", fill=P["panel"], stroke=P["rule"])
    up(DCX, 142, 130)

    # decoder residuals (right)
    c.polyline([(DCX, 416), (842, 416), (842, 337)], stroke=P["gold"], sw=1.2)
    c.arrow(842, 337, DX + DW, 337, color=P["gold"], sw=1.2, head=5)
    c.polyline([(DCX, 320), (842, 320), (842, 245)], stroke=P["gold"], sw=1.2)
    c.arrow(842, 245, DX + DW, 245, color=P["gold"], sw=1.2, head=5)
    c.polyline([(DCX, 228), (842, 228), (842, 155)], stroke=P["gold"], sw=1.2)
    c.arrow(842, 155, DX + DW, 155, color=P["gold"], sw=1.2, head=5)

    # decoder input stack
    up(DCX, 500, 486)
    chips(c, DCX, 500, ["我", "喜欢", "机器", "学习"], h=26, size=11.5)
    c.text(DCX, 542, "输出（右移一位）", size=10.8, fill=P["muted"], anchor="middle")
    block(c, DX, 452, DW, 34, "Output Embedding", fill=P["panel2"], stroke=P["rule"])
    up(DCX, 452, 435)
    plus_circle(c, DCX, 426)
    tag(c, DCX + 24, 426, "PE", color=P["gold"], bg=P["goldL"], size=9.5, h=15)

    # decoder group
    c.rect(590, 134, 260, 284, fill="none", stroke=P["violetM"], rx=8, dash="5 4")
    c.rect(600, 127, 104, 15, fill=P["white"])
    c.text(606, 138, "Decoder × 6", size=10.5, fill=P["violet"], weight="600")

    # ---------------- legend ----------------
    lx, ly = 140, 570
    items = [("自注意力", P["blueM"], P["blue"]), ("交叉注意力", P["violetM"], P["violet"]),
             ("前馈网络", "#e9eef3", P["faint"]), ("Add & Norm", P["goldM"], P["gold"])]
    for lab, fill, stroke in items:
        c.rect(lx, ly - 8, 15, 11, fill=fill, stroke=stroke, rx=2, sw=0.8)
        c.text(lx + 20, ly + 1, lab, size=10.5, fill=P["ink2"])
        lx += 20 + tw(lab, 10.5) + 26
    c.line(lx, ly - 2, lx + 26, ly - 2, stroke=P["gold"], sw=1.3)
    c.text(lx + 32, ly + 1, "残差连接", size=10.5, fill=P["ink2"])

    c.text(140, 598, "原论文 base 配置：N = 6 层，d_model = 512，h = 8 个头；同一 Block 堆叠 6 次，"
                     "每层参数各自独立。PE = 正弦位置编码，与嵌入相加。",
           size=10.5, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 02 — Q / K / V intuition
# ---------------------------------------------------------------------------

def f02():
    c = Canvas(960, 600)
    toks = ["小猫", "坐", "在", "垫子", "上", "它", "很", "困"]
    weights = [0.62, 0.04, 0.05, 0.06, 0.04, 0.12, 0.04, 0.03]
    scores = ["2.6", "-0.2", "0.0", "0.2", "-0.2", "0.9", "-0.2", "-0.5"]

    X0, CW, GAP = 170, 88, 6
    centers = [X0 + i * (CW + GAP) + CW / 2 for i in range(8)]

    c.text(170, 26, "① 用当前位置的 q 与每个位置的 k 比较", size=11.5, fill=P["ink2"],
           weight="600")
    c.text(944, 26, "s = qₜ · kₛ / √dₖ", size=11, fill=P["muted"], anchor="end")

    for i, t in enumerate(toks):
        fill = P["blueL"] if i == 5 else P["panel"]
        stroke = P["blue"] if i == 5 else P["rule"]
        c.rect(X0 + i * (CW + GAP), 60, CW, 30, fill=fill, stroke=stroke, rx=5)
        c.text(centers[i], 79, t, size=12.5, fill=P["ink"], anchor="middle",
               weight="600" if i == 5 else None)

    # query route: highlighted token -> q chip on the left
    c.polyline([(centers[5], 60), (centers[5], 44), (54, 44), (54, 138)],
               stroke=P["blue"], sw=1.2, dash="3 3")
    c.arrow(54, 128, 54, 145, color=P["blue"], sw=1.2, head=5)
    c.text(centers[5] + 8, 36, "q 来自「它」", size=9.5, fill=P["blue"], anchor="start")

    # q chip
    c.rect(14, 146, 80, 66, fill=P["blueL"], stroke=P["blue"], rx=6)
    c.text(54, 172, "q", size=17, fill=P["blue"], anchor="middle", family="serif",
           italic=True)
    c.text(54, 192, "我想找", size=10, fill=P["blue"], anchor="middle")

    # gutter labels
    c.text(158, 124, "Key  k", size=10.5, fill=P["orange"], anchor="end")
    c.text(158, 162, "分数", size=10.5, fill=P["muted"], anchor="end")
    c.text(158, 200, "权重 α", size=10.5, fill=P["violet"], anchor="end")

    for i in range(8):
        c.rect(centers[i] - 27, 104, 54, 24, fill=P["orangeL"], stroke=P["orangeM"], rx=4)
        c.text(centers[i], 121, f"k{i+1}", size=11, fill=P["orange"], anchor="middle")
        c.text(centers[i], 162, scores[i], size=11, fill=P["ink2"], anchor="middle")

    # weights
    for i, w in enumerate(weights):
        bw = 74 * w
        c.rect(centers[i] - bw / 2, 180, bw, 12, fill=P["violetM"], stroke="none", rx=2)
        c.text(centers[i], 208, f"{w:.2f}", size=10, fill=P["violet"], anchor="middle")

    c.text(170, 232, "softmax 之后：8 个权重相加为 1", size=10.5, fill=P["muted"])

    # ---------------- aggregation ----------------
    c.text(170, 268, "② 按权重取出各位置的 v，再加权求和", size=11.5, fill=P["ink2"],
           weight="600")
    for i in range(8):
        c.rect(centers[i] - 27, 282, 54, 24, fill=P["tealL"], stroke=P["tealM"], rx=4)
        c.text(centers[i], 299, f"v{i+1}", size=11, fill=P["teal"], anchor="middle")
        sw = 0.7 + 5.2 * weights[i]
        c.line(centers[i], 306, centers[i], 348, stroke=P["teal"], sw=sw, opacity=0.55)

    c.line(centers[0], 348, centers[7], 348, stroke=P["teal"], sw=1.4)
    c.arrow((centers[0] + centers[7]) / 2, 348, (centers[0] + centers[7]) / 2, 372,
            color=P["teal"], sw=1.4, head=6)
    c.text(170, 372, "线的粗细代表权重", size=9.5, fill=P["teal"], anchor="start")

    c.rect(320, 376, 424, 46, fill=P["tealL"], stroke=P["tealM"], rx=6)
    c.text(532, 396, "oₜ = Σₛ αₜₛ · vₛ", size=13.5, fill=P["teal"], anchor="middle")
    c.text(532, 412, "「它」更新后的表示：已经读取了整句上下文", size=10.2,
           fill=P["ink2"], anchor="middle")

    # ---------------- roles ----------------
    roles = [
        ("Q  Query", "当前位置想找什么", P["blue"], P["blueL"], 170),
        ("K  Key", "每个位置能被怎样匹配", P["orange"], P["orangeL"], 420),
        ("V  Value", "每个位置实际提供的信息", P["teal"], P["tealL"], 690),
    ]
    c.line(170, 452, 916, 452, stroke=P["rule"], sw=1)
    for name, desc, col, bg, x in roles:
        c.rect(x, 470, 14, 14, fill=bg, stroke=col, rx=3, sw=1)
        c.text(x + 22, 481, name, size=11.5, fill=col, weight="600")
        c.text(x + 22, 500, desc, size=10.8, fill=P["ink2"])

    c.text(170, 548, "每个位置都同时扮演三种角色：训练会分别学出 W_Q、W_K、W_V，把同一个 x 投影成 q、k、v。",
           size=10.8, fill=P["muted"])
    c.text(170, 570, "注意：这一层的读写并不携带位置信息——顺序要由 7.3 的位置编码补上。",
           size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 03 — scaled dot-product attention, matrix shapes
# ---------------------------------------------------------------------------

def f03():
    c = Canvas(960, 500)
    cell = 18

    c.text(40, 34, "① 整句一起算：所有位置的分数用一个矩阵乘法得到", size=11.5,
           fill=P["ink2"], weight="600")

    defs = [
        ("Q", 56, 105, 4, 5, P["blueL"], P["blueM"], "T × d_k"),
        ("Kᵀ", 152, 114, 5, 4, P["orangeL"], P["orangeM"], "d_k × T"),
        ("S = QKᵀ", 268, 105, 5, 5, P["violetL"], P["violetM"], "T × T"),
    ]
    for name, x, y, cols, rows, fill, stroke, shp in defs:
        c.mat(x, y, cols, rows, cell=cell, fill=fill, stroke=stroke, gap=1)
        c.text(x + cols * cell / 2, y - 12, name, size=12.5, fill=P["ink"],
               anchor="middle", weight="600")
        c.text(x + cols * cell / 2, 214, shp, size=9.5, fill=P["muted"], anchor="middle",
               family="mono")

    c.text(142, 155, "×", size=15, fill=P["muted"], anchor="middle")
    c.text(256, 155, "=", size=15, fill=P["muted"], anchor="middle")

    # op cards
    ops = [("÷ √d_k", 380, 70), ("+ M", 460, 60), ("softmax", 530, 70)]
    for name, x, w in ops:
        c.rect(x, 137, w, 26, fill=P["panel"], stroke=P["rule"], rx=5)
        c.text(x + w / 2, 154, name, size=11, fill=P["ink2"], anchor="middle",
               family="mono")
    c.arrow(361, 150, 378, 150, color=P["muted"], sw=1.2, head=5)
    c.arrow(450, 150, 458, 150, color=P["muted"], sw=1.2, head=5)
    c.arrow(520, 150, 528, 150, color=P["muted"], sw=1.2, head=5)
    c.arrow(600, 150, 611, 150, color=P["muted"], sw=1.2, head=5)
    c.mat(614, 105, 5, 5, cell=cell, fill=P["violetL"], stroke=P["violetM"], gap=1)
    c.text(659, 93, "A（权重）", size=12.5, fill=P["ink"], anchor="middle", weight="600")
    c.text(659, 214, "T × T", size=9.5, fill=P["muted"], anchor="middle", family="mono")

    # highlight row t in S and A
    for x in (268, 614):
        c.rect(x, 105 + 2 * cell, 5 * cell, cell, fill="none", stroke=P["violet"], sw=1.6,
               rx=1)

    # notes
    notes = [
        ("S 的每一行", "一个位置对全部位置的打分"),
        ("softmax 按行归一化", "每行相加为 1"),
        ("M 是掩码矩阵", "因果掩码时未来位置为 −∞"),
        ("÷ √d_k", "把点积拉回合适的尺度"),
    ]
    for i, (a, b) in enumerate(notes):
        y = 112 + i * 28
        c.circle(726, y - 4, 1.8, fill=P["faint"])
        c.text(736, y, a, size=10.5, fill=P["ink2"], weight="600")
        c.text(736, y + 14, b, size=10, fill=P["muted"])

    # ---------------- row view ----------------
    c.text(40, 256, "② 只看第 t 行：一个位置怎样把 Value 汇总成自己的输出", size=11.5,
           fill=P["ink2"], weight="600")
    cc = 26
    weights = [0.62, 0.04, 0.05, 0.06, 0.23]
    for j, w in enumerate(weights):
        x = 56 + j * cc
        c.rect(x, 332, cc - 1, cc - 1, fill=P["violetL"], stroke=P["violetM"], rx=1)
        c.text(x + cc / 2, 348, f"{w:.2f}", size=8.6, fill=P["violet"], anchor="middle")
    c.text(56 + 5 * cc / 2, 322, "αₜ：A 的第 t 行", size=10.5, fill=P["ink2"],
           anchor="middle")
    c.text(200, 349, "×", size=15, fill=P["muted"], anchor="middle")

    c.mat(214, 280, 4, 5, cell=cc, fill=P["tealL"], stroke=P["tealM"], gap=1)
    c.text(214 + 4 * cc / 2, 270, "V（T × d_v）", size=10.5, fill=P["ink2"], anchor="middle")
    c.text(327, 349, "=", size=15, fill=P["muted"], anchor="middle")
    c.mat(344, 332, 4, 1, cell=cc, fill=P["tealM"], stroke=P["teal"], gap=1)
    c.text(344 + 4 * cc / 2, 322, "oₜ（d_v）", size=10.5, fill=P["ink2"], anchor="middle")

    c.text(476, 342, "oₜ = Σₛ αₜₛ · vₛ", size=13, fill=P["ink"])
    c.text(476, 364, "权重只作用在对应位置的 Value 行上，", size=10.5, fill=P["muted"])
    c.text(476, 380, "再把 5 行向量按权重加起来。", size=10.5, fill=P["muted"])

    c.text(40, 452, "Q、K、V 都来自同一组输入 X，只差三组投影参数：XW_Q、XW_K、XW_V。"
                    "交叉注意力同理，只是 K、V 改由编码器的输出生成。",
           size=10.8, fill=P["muted"])
    c.text(40, 474, "计算量：QKᵀ 约 T²·d_k，softmax 后与 V 相乘约 T²·d_v；保存 T×T 的权重还需要 O(T²) 的空间。",
           size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 04 — multi-head attention
# ---------------------------------------------------------------------------

def f04():
    c = Canvas(960, 480)
    c.text(40, 32, "同一个 X，h 组不同的投影各自读一次，再拼起来投影回去", size=11.5,
           fill=P["ink2"], weight="600")

    c.rect(40, 184, 46, 92, fill=P["panel2"], stroke=P["rule"], rx=5)
    c.text(63, 226, "X", size=15, fill=P["ink"], anchor="middle", family="serif",
           italic=True)
    c.text(63, 250, "T×d", size=9.5, fill=P["muted"], anchor="middle", family="mono")

    lanes = [56, 144, 232, 320]
    colors = [P["blue"], P["orange"], P["teal"], P["violet"]]
    fills = [P["blueL"], P["orangeL"], P["tealL"], P["violetL"]]
    borders = [P["blueM"], P["orangeM"], P["tealM"], P["violetM"]]
    for i, y in enumerate(lanes):
        c.arrow(88, 230, 132, y + 32, color=P["faint"], sw=1.1, head=5, curve=-6)
        c.rect(132, y, 214, 64, fill=fills[i], stroke=borders[i], rx=6)
        c.text(144, y + 20, f"head {i+1}", size=11.5, fill=colors[i], weight="600")
        c.text(144, y + 39, "Attention(XW_Q, XW_K, XW_V)", size=9.6, fill=P["ink2"])
        c.text(144, y + 54, "输出 T×d_v", size=9.2, fill=P["muted"])

    # concat: contiguous stack
    cy0, chh = 44, 88
    c.rect(420, cy0, 84, 4 * chh, fill=P["white"], stroke=P["rule"], rx=4)
    for i in range(4):
        c.rect(422, cy0 + 2 + i * chh, 80, chh, fill=fills[i], stroke="none")
        c.text(462, cy0 + 2 + i * chh + chh / 2 + 3.5, f"head {i+1}", size=10,
               fill=colors[i], anchor="middle")
        if i:
            c.line(422, cy0 + 2 + i * chh, 502, cy0 + 2 + i * chh, stroke=P["white"], sw=1.4)
    c.text(462, 34, "Concat", size=11, fill=P["ink2"], anchor="middle", weight="600")
    c.text(462, 414, "T × (h·d_v)", size=9.5, fill=P["muted"], anchor="middle",
           family="mono")
    for i, y in enumerate(lanes):
        c.arrow(350, y + 32, 416, cy0 + 2 + i * chh + chh / 2, color=P["faint"], sw=1.1,
                head=5)

    c.arrow(506, 220, 546, 220, color=P["muted"], sw=1.2, head=5)
    c.rect(548, 192, 96, 56, fill=P["panel"], stroke=P["rule"], rx=5)
    c.text(596, 216, "W_O", size=12.5, fill=P["ink"], anchor="middle", weight="600")
    c.text(596, 234, "(h·d_v) × d", size=9, fill=P["muted"], anchor="middle",
           family="mono")

    c.arrow(646, 220, 686, 220, color=P["muted"], sw=1.2, head=5)
    c.rect(688, 192, 76, 56, fill=P["panel2"], stroke=P["rule"], rx=5)
    c.text(726, 216, "T×d", size=12, fill=P["ink"], anchor="middle", family="mono")
    c.text(726, 234, "输出", size=9.5, fill=P["muted"], anchor="middle")

    # notes
    note_lines = [
        "各头的 W_Q、W_K、W_V 形状相同，",
        "但参数不同、独立初始化并训练。",
        "",
        "常见等宽设计：d_k = d_v = d / h，",
        "h 个头的总计算量与一个 d 维的",
        "单头大致相当。",
    ]
    for i, s in enumerate(note_lines):
        if s:
            c.text(786, 66 + i * 19, s, size=10.2, fill=P["ink2"])

    c.text(40, 440, "不同头可以学到不同的关联类型：有的偏向相邻位置，有的偏向同一实体或语法关系；"
                    "拼接后再由 W_O 融合成一个 d 维表示。",
           size=10.8, fill=P["muted"])
    c.text(40, 462, "图中画了 4 个头，实际 h 由模型决定（原论文 h = 8）。",
           size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 24 — self-attention score heatmap
# ---------------------------------------------------------------------------

def f24():
    c = Canvas(960, 500)
    toks = ["小猫", "坐", "在", "垫子", "上", "它", "很", "困"]
    A = [
        [0.42, 0.08, 0.06, 0.10, 0.04, 0.18, 0.05, 0.07],
        [0.20, 0.38, 0.12, 0.10, 0.04, 0.09, 0.03, 0.04],
        [0.10, 0.22, 0.36, 0.14, 0.06, 0.06, 0.02, 0.04],
        [0.12, 0.14, 0.18, 0.36, 0.08, 0.06, 0.02, 0.04],
        [0.04, 0.10, 0.16, 0.32, 0.28, 0.04, 0.02, 0.04],
        [0.62, 0.04, 0.05, 0.06, 0.04, 0.12, 0.04, 0.03],
        [0.05, 0.03, 0.03, 0.03, 0.02, 0.18, 0.28, 0.38],
        [0.10, 0.03, 0.03, 0.03, 0.02, 0.28, 0.22, 0.29],
    ]
    X0, Y0, cell = 150, 84, 40
    txt = [[f"{v:.2f}" for v in row] for row in A]

    c.rect(X0, Y0 + 5 * cell, 8 * cell, cell, fill=P["blueL"], opacity=0.9)
    c.rect(X0, Y0, cell, 8 * cell, fill=P["orangeL"], opacity=0.9)

    c.heat(X0, Y0, 8 * cell, 8 * cell, A, cmap=BLUES, vmin=0, vmax=1, gap=1.2,
           cells_text=txt, text_size=8.6, text_color=None, rx=1)
    for i, t in enumerate(toks):
        c.text(X0 + i * cell + cell / 2, Y0 - 10, t, size=11.5, fill=P["ink2"],
               anchor="middle")
        c.text(X0 - 12, Y0 + i * cell + cell / 2 + 4, t, size=11.5, fill=P["ink2"],
               anchor="end")
    c.rect(X0, Y0 + 5 * cell, 8 * cell, cell, fill="none", stroke=P["blue"], sw=1.8, rx=2)
    c.rect(X0, Y0, cell, 8 * cell, fill="none", stroke=P["orange"], sw=1.8, rx=2)

    c.text(X0 + 4 * cell, Y0 + 8 * cell + 26, "Key（被读取的位置）→", size=10.5,
           fill=P["orange"], anchor="middle")
    c.text(84, Y0 + 4 * cell, "Query（读取者）→", size=10.5, fill=P["blue"],
           anchor="middle", rotate=(-90, 84, Y0 + 4 * cell))

    # colorbar
    bx, by = 500, 110
    for i in range(24):
        c.rect(bx, by + i * 5, 11, 5.4, fill=BLUES(1 - i / 23), stroke="none")
    c.text(bx + 5.5, by - 10, "权重", size=9.5, fill=P["muted"], anchor="middle")
    c.text(bx + 17, by + 4, "1", size=9, fill=P["muted"])
    c.text(bx + 17, by + 120, "0", size=9, fill=P["muted"])

    # callout
    c.polyline([(X0 + 8 * cell + 3, Y0 + 5.5 * cell), (566, Y0 + 5.5 * cell)],
               stroke=P["blue"], sw=1.1)
    c.text(574, Y0 + 5.5 * cell - 16, "「它」这一行：", size=11, fill=P["blue"], weight="600")
    c.text(574, Y0 + 5.5 * cell - 1, "0.62 的权重分配给「小猫」，", size=10.5, fill=P["ink2"])
    c.text(574, Y0 + 5.5 * cell + 15, "0.12 留给自己，其余位置很小。", size=10.5, fill=P["ink2"])

    c.text(574, 110, "每行 softmax 后相加为 1；", size=10.8, fill=P["ink2"])
    c.text(574, 130, "颜色越深，读取时越依赖该位置。", size=10.8, fill=P["ink2"])
    c.text(574, 166, "同一句话里，不同位置的读取重点", size=10.8, fill=P["ink2"])
    c.text(574, 182, "并不相同：这是内容驱动的。", size=10.8, fill=P["ink2"])

    c.text(150, 456, "热图为示意：数值用来展示强弱关系，不代表某个具体模型的真实输出。",
           size=10.8, fill=P["muted"])
    c.text(150, 476, "注意力权重是 T×T 的矩阵：行是读取者，列是被读取的位置。",
           size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 29 — causal mask
# ---------------------------------------------------------------------------

def f29():
    c = Canvas(960, 420)
    T = 6
    cell = 36
    X0, Y0 = 150, 92
    toks = ["它", "在", "垫子", "上", "睡着", "了"]

    c.text(150, 40, "因果掩码：第 t 个位置只能读取 1..t", size=11.5, fill=P["ink2"],
           weight="600")

    for i in range(T):
        for j in range(T):
            if j <= i:
                c.rect(X0 + j * cell, Y0 + i * cell, cell - 2, cell - 2, fill=P["panel"],
                       stroke=P["rule"], rx=2, sw=0.6)
                c.text(X0 + j * cell + cell / 2, Y0 + i * cell + cell / 2 + 4, "0",
                       size=9.5, fill=P["faint"], anchor="middle")
            else:
                c.rect(X0 + j * cell, Y0 + i * cell, cell - 2, cell - 2, fill="#5b6875",
                       stroke="none", rx=2)
                c.text(X0 + j * cell + cell / 2, Y0 + i * cell + cell / 2 + 4, "−∞",
                       size=10, fill="#e9eef2", anchor="middle")

    for i, t in enumerate(toks):
        c.text(X0 + i * cell + cell / 2, Y0 - 9, t, size=11, fill=P["ink2"], anchor="middle")
        c.text(X0 - 12, Y0 + i * cell + cell / 2 + 4, f"t{i+1}", size=10.5,
               fill=P["ink2"], anchor="end")
    c.text(96, Y0 + T * cell / 2, "Query →", size=10, fill=P["muted"], anchor="middle",
           rotate=(-90, 96, Y0 + T * cell / 2))
    c.text(X0 + T * cell / 2, Y0 + T * cell + 26, "Key（位置）→", size=10,
           fill=P["muted"], anchor="middle")

    # highlight row t4
    c.rect(X0, Y0 + 3 * cell, T * cell, cell, fill="none", stroke=P["blue"], sw=1.8, rx=2)

    # right: the resulting row
    rx = 470
    c.text(rx, 40, "第 4 个位置这一行：", size=11, fill=P["blue"], weight="600")
    c.text(rx, 58, "允许的 4 个位置权重和为 1，未来位置为 0", size=10.5, fill=P["ink2"])
    vals = [0.18, 0.31, 0.22, 0.29, 0.0, 0.0]
    for j, v in enumerate(vals):
        bx = rx + 10 + j * 66
        h = 94 * v / 0.31
        c.rect(bx, 196 - h, 40, h, fill=P["blueM"] if v > 0 else "none",
               stroke=P["blue"] if v > 0 else P["faint"], rx=2, sw=1,
               dash=None if v > 0 else "3 3")
        c.text(bx + 20, 212, toks[j], size=9.5, fill=P["muted"], anchor="middle")
        c.text(bx + 20, 192 - h, f"{v:.2f}", size=8.8, fill=P["blue"] if v > 0 else P["faint"],
               anchor="middle")
    c.line(rx + 6, 196, rx + 6 + 6 * 66, 196, stroke=P["ink2"], sw=1)
    c.text(rx, 246, "训练时：整句一次送进模型，每个位置都在自己的掩码下并行计算；",
           size=10.5, fill=P["ink2"])
    c.text(rx, 264, "生成时：第 t 步只需要前 t 个 Key，后面的位置还不存在。",
           size=10.5, fill=P["ink2"])

    c.text(150, 356, "掩码加在 softmax 之前的打分上：允许的位置 +0，禁止的位置 −∞。"
                     "经过 softmax，−∞ 变成 0，未来位置就完全不会被读到。",
           size=10.8, fill=P["muted"])
    c.text(150, 376, "补齐序列长度时插入的 padding 位置也用同样的办法排除；"
                     "它和位置编码解决的是两个问题——一个管“能读谁”，一个管“相对多远”。",
           size=10.8, fill=P["muted"])
    return c


FIGURES = {
    "01_original-transformer-architecture": f01,
    "02_self-attention-query-key-value": f02,
    "03_scaled-dot-product-attention-matrices": f03,
    "04_scaled-dot-product-and-multi-head-attention": f04,
    "24_self-attention-score-heatmap": f24,
    "29_causal-mask": f29,
}
