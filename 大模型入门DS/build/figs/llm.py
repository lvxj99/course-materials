"""Figures for the LLM intro: BPE, tokenization/embedding, temperature, training pipeline."""

from __future__ import annotations

import math

from .common import *  # noqa: F401,F403
from figkit import P, Canvas, tw


# ---------------------------------------------------------------------------
# small local helpers
# ---------------------------------------------------------------------------

def _token_chips(c, x, y, items, h=32, size=12, gap=5):
    """Row of coloured chips: items = (text, fill, stroke, text colour)."""
    spans, pos = [], x
    for t, fill, stroke, col in items:
        w = max(30, tw(t, size) + 20)
        c.rect(pos, y, w, h, fill=fill, stroke=stroke, rx=5)
        c.text(pos + w / 2, y + h / 2 + size * 0.36, t, size=size, fill=col,
               anchor="middle")
        spans.append((pos, w))
        pos += w + gap
    return spans


# ---------------------------------------------------------------------------
# 17 — BPE builds a subword vocabulary by merging frequent pairs
# ---------------------------------------------------------------------------

def f17():
    c = Canvas(960, 520)
    LX, MW, RX = 40, 356, 686

    c.text(LX, 40, "① 语料统计", size=11.5, fill=P["ink2"], weight="600")
    c.text(MW, 40, "② 贪心合并相邻对", size=11.5, fill=P["ink2"], weight="600")
    c.text(RX, 40, "③ 词表与切分", size=11.5, fill=P["ink2"], weight="600")
    c.text(LX, 58, "先把每个字符当作 token，再按词频合并", size=10.3, fill=P["muted"])
    c.text(MW, 58, "每轮统计当前语料里最高频的相邻对", size=10.3, fill=P["muted"])
    c.text(RX, 58, "合并出的子词进入词表", size=10.3, fill=P["muted"])

    # ---------------- left: corpus ----------------
    words = [
        ("low", 5, 3), ("lower", 2, 5), ("lowest", 2, 6), ("newer", 6, 5),
        ("newest", 6, 6), ("wider", 3, 5), ("widest", 3, 6),
    ]
    for i, (w, f, n) in enumerate(words):
        y = 94 + i * 36
        if w == "lowest":
            c.rect(40, y + 2, 3, 21, fill=P["blue"], rx=1.5)
        c.text(48, y + 15, w, size=11.5, fill=P["ink"], weight="600")
        c.text(116, y + 15, f"×{f}", size=9.8, fill=P["ink2"], anchor="end")
        for k in range(n):
            cx = 134 + k * 20
            c.rect(cx, y, 17.5, 21, fill=P["panel"], stroke=P["rule"], rx=3, sw=0.8)
            c.text(cx + 8.75, y + 14.6, w[k], size=9.8, fill=P["ink2"],
                   anchor="middle", family="mono")
        c.text(134 + n * 20 + 1, y + 15, "·", size=12, fill=P["muted"])

    c.text(48, 352, "· 表示词边界（常写作 </w>）", size=9.8, fill=P["muted"])
    c.rect(40, 368, 290, 54, fill=P["panel"], stroke=P["rule"], rx=6)
    c.text(54, 389, "7 种词 · 27 个词次 · 10 个不同字符",
           size=10.5, fill=P["ink2"])
    c.text(54, 407, "4 次合并后：10 个字符 + 4 个子词",
           size=9.5, fill=P["muted"])

    # ---------------- middle: merges ----------------
    O, B, T, V = P["orange"], P["blue"], P["teal"], P["violet"]
    rows = [
        (78, 1, 11, "e + s → es", ["n", "e", "w", "e", "s", "t"], (3, 4), "es",
         "来自 newest（6）+ widest（3）+ lowest（2）", P["blueL"], P["blueM"], B),
        (164, 2, 11, "es + t → est", ["n", "e", "w", "es", "t"], (3, 4), "est",
         "来自 newest（6）+ widest（3）+ lowest（2）", P["orangeL"], P["orangeM"], O),
        (250, 3, 9, "l + o → lo", ["l", "o", "w", "est"], (0, 1), "lo",
         "来自 low（5）+ lower（2）+ lowest（2）", P["tealL"], P["tealM"], T),
        (336, 4, 9, "lo + w → low", ["lo", "w", "est"], (0, 1), "low",
         "来自 low（5）+ lower（2）+ lowest（2）", P["violetL"], P["violetM"], V),
    ]
    for y, idx, freq, title, toks, pair, result, caption, fill, stroke, col in rows:
        c.rect(MW, y, 306, 78, fill=fill, stroke=stroke, rx=6)
        c.text(MW + 14, y + 20, f"第 {idx} 次合并：{title}", size=11,
               fill=col, weight="600")
        c.text(MW + 292, y + 20, f"{freq} 次", size=9.8, fill=col, anchor="end")

        spans, pos = [], MW + 14
        for t in toks:
            w = max(18, tw(t, 10, "mono") + 9)
            c.rect(pos, y + 30, w, 22, fill=P["white"], stroke=stroke, rx=4, sw=0.9)
            c.text(pos + w / 2, y + 44.6, t, size=10, fill=P["ink2"],
                   anchor="middle", family="mono")
            spans.append((pos, w))
            pos += w + 3
        a, b = spans[pair[0]], spans[pair[1]]
        c.rect(a[0] - 2, y + 28, b[0] + b[1] - a[0] + 4, 26, fill="none",
               stroke=col, sw=1.5, rx=5)

        last = spans[-1][0] + spans[-1][1]
        c.arrow(max(last + 8, MW + 140), y + 42, MW + 184, y + 42,
                color=col, sw=1.2, head=5)
        rw = max(26, tw(result, 10, "mono") + 14)
        c.rect(MW + 190, y + 31, rw, 22, fill=P["white"], stroke=col, rx=4, sw=1.2)
        c.text(MW + 190 + rw / 2, y + 45.6, result, size=10, fill=col,
               anchor="middle", family="mono", weight="600")
        c.text(MW + 14, y + 68, caption, size=9.5, fill=P["muted"])

    c.text(MW + 153, 440, "重复直到达到目标词表大小，或没有频次 ≥ 2 的相邻对",
           size=9.6, fill=P["muted"], anchor="middle")

    # ---------------- right: vocabulary & segmentation ----------------
    c.text(RX, 78, "词表片段 V", size=10.3, fill=P["ink2"], weight="600")
    chips(c, 803, 90, ["l", "o", "w", "e", "r"], h=20, size=9.5, pad=6, gap=4)
    chips(c, 803, 114, ["n", "s", "t", "i", "d"], h=20, size=9.5, pad=6, gap=4)
    c.text(803, 150, "＋ 合并新增", size=9.4, fill=P["muted"], anchor="middle")

    items = [("es", P["blueL"], P["blueM"], B), ("est", P["orangeL"], P["orangeM"], O),
             ("lo", P["tealL"], P["tealM"], T), ("low", P["violetL"], P["violetM"], V)]
    widths = [max(24, tw(t, 10, "mono") + 14) for t, _, _, _ in items]
    total = sum(widths) + 5 * 3
    x = 803 - total / 2
    for (t, f, s, col), w in zip(items, widths):
        c.rect(x, 162, w, 22, fill=f, stroke=s, rx=4)
        c.text(x + w / 2, 176.6, t, size=10, fill=col, anchor="middle",
               family="mono", weight="600")
        x += w + 5

    c.line(RX, 198, 920, 198, stroke=P["rule"], sw=1)
    c.text(RX, 218, "切分示例", size=10.3, fill=P["ink2"], weight="600")

    c.rect(714, 230, 68, 26, fill=P["panel"], stroke=P["rule"], rx=5)
    c.text(748, 247.5, "lowest", size=11, fill=P["ink"], anchor="middle",
           family="mono")
    c.arrow(788, 243, 804, 243, color=P["muted"], sw=1.2, head=5)
    for t, x0, w in (("low", 810, 38), ("est", 852, 44)):
        c.rect(x0, 230, w, 26, fill=P["panel2"], stroke=P["rule"], rx=5)
        c.text(x0 + w / 2, 247.5, t, size=11, fill=P["ink2"], anchor="middle",
               family="mono")
    c.text(803, 278, "6 个字符 → 2 个 token", size=9.6, fill=P["muted"],
           anchor="middle")

    c.text(RX, 312, "为什么用子词", size=10.3, fill=P["ink2"], weight="600")
    for i, s in enumerate([
        "· 罕见词拆成子词，不再有未登录词",
        "· 词表大小可控（如 32k / 50k）",
        "· 词根共享：low / lower / lowest",
    ]):
        c.text(RX + 2, 332 + i * 18, s, size=9.4, fill=P["ink2"])

    # ---------------- notes ----------------
    c.text(LX, 482, "词表大小是超参：过大则嵌入矩阵与输出 softmax 都变大，过小则退化成字符、丢失词级规律；"
                    "子词是两者的工程折中。", size=10.8, fill=P["muted"])
    c.text(LX, 500, "BPE 每轮贪心合并当前最高频的相邻对；图中按讲解顺序展示 e+s、es+t、l+o、lo+w，"
                    "实际次序由各轮统计决定。", size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 18 — text -> tokens -> ids -> embedding lookup
# ---------------------------------------------------------------------------

def f18():
    c = Canvas(960, 520)
    BL, BM = P["blueL"], P["blueM"]
    OL, OM = P["orangeL"], P["orangeM"]

    # ---------------- ① text ----------------
    c.text(40, 40, "① 文本", size=11.5, fill=P["ink2"], weight="600")
    c.rect(40, 56, 200, 64, fill=P["panel"], stroke=P["rule"], rx=6)
    c.text(140, 84, "alignment is hard", size=13, fill=P["ink"], anchor="middle")
    c.text(140, 102, "英文：3 个词 / 15 个字母", size=9.3, fill=P["muted"],
           anchor="middle")
    c.rect(40, 152, 200, 64, fill=P["panel"], stroke=P["rule"], rx=6)
    c.text(140, 180, "我喜欢机器学习", size=13.5, fill=P["ink"], anchor="middle")
    c.text(140, 198, "中文：6 个汉字", size=9.3, fill=P["muted"], anchor="middle")
    c.arrow(244, 88, 262, 88, color=P["faint"], sw=1.1, head=5)
    c.arrow(244, 184, 262, 184, color=P["faint"], sw=1.1, head=5)
    c.text(40, 246, "切分粒度因语言而异：", size=9.4, fill=P["muted"])
    c.text(40, 262, "中文常见整词，英文常见子词。", size=9.4, fill=P["muted"])

    # ---------------- ② tokens + ③ ids ----------------
    c.text(268, 40, "② 分词　·　③ token id", size=11.5, fill=P["ink2"],
           weight="600")
    en = _token_chips(c, 268, 72, [
        ("align", BL, BM, P["blue"]),
        ("ment", OL, OM, P["orange"]),
        ("is", BL, BM, P["blue"]),
        ("hard", BL, BM, P["blue"]),
    ])
    en_ids = ["512", "78", "12", "903"]
    _token_chips(c, 268, 168, [
        ("我", BL, BM, P["blue"]),
        ("喜欢", BL, BM, P["blue"]),
        ("机器", BL, BM, P["blue"]),
        ("学习", BL, BM, P["blue"]),
    ])
    for (x, w), s in zip(en, en_ids):
        c.text(x + w / 2, 126, s, size=10, fill=P["muted"], anchor="middle",
               family="mono")
    c.text(268, 222, "对照：中文按整词切，4 个 token", size=9.3, fill=P["muted"])
    c.text(268, 246, "英文把 alignment 拆成 align + ment：", size=9.4, fill=P["muted"])
    c.text(268, 262, "子词复用词根，也能拼出没见过的词。", size=9.4, fill=P["muted"])

    # ---------------- ④ lookup ----------------
    c.text(600, 40, "④ 查表：token id → 向量", size=11.5, fill=P["ink2"],
           weight="600")
    EX, EY, CELL, NROW, NCOL, GAP = 640, 84, 13, 10, 8, 1.4
    c.text(692, 74, "E 的片段（10 行 × d，示意）", size=10.3, fill=P["ink2"],
           anchor="middle")
    c.mat(EX, EY, NCOL, NROW, cell=CELL, fill=P["panel"], stroke=P["rule"],
          gap=GAP, rx=1.5)
    hi = [3, 4, 6, 7]
    for r in hi:
        for j in range(NCOL):
            c.rect(EX + j * CELL, EY + r * CELL, CELL - GAP, CELL - GAP,
                   fill=P["blueM"], stroke=P["blue"], sw=0.8, rx=1.5)

    # one id -> one row
    for (x, w), s, r in zip(en, en_ids, hi):
        cx = x + w / 2
        c.arrow(cx, 133, EX - 4, EY + (r + 0.5) * CELL,
                color=P["blue2"], sw=1.1, head=4.5)

    # extracted rows -> X
    XX, XY = 800, 123
    c.text(818, 108, "X", size=12, fill=P["ink"], family="serif", italic=True)
    c.text(829, 108, "∈", size=11.5, fill=P["ink"], family="serif")
    c.text(840, 108, "R", size=12, fill=P["ink"], family="serif")
    c.text(851, 102, "T×d", size=8, fill=P["ink"], family="serif")
    c.mat(XX, XY, NCOL, 4, cell=CELL, fill=P["blueL"], stroke=P["blueM"],
          gap=GAP, rx=1.5)
    for i in range(4):
        for j in range(NCOL):
            c.rect(XX + j * CELL, XY + i * CELL, CELL - GAP, CELL - GAP,
                   fill=P["blueM"], stroke=P["blue"], sw=0.8, rx=1.5)
        c.arrow(EX + NCOL * CELL + 3, EY + (hi[i] + 0.5) * CELL,
                XX - 4, XY + (i + 0.5) * CELL, color=P["blue2"], sw=1.1, head=4.5)

    c.text(852, 190, "T = 4，d = 8", size=9, fill=P["muted"], anchor="middle",
           family="mono")
    c.text(692, 232, "行号 = token id；一个 id 取出一行", size=9.3,
           fill=P["muted"], anchor="middle")
    c.text(692, 246, "E 的每一行都是可学习参数；图中只画 10 行示意", size=9.3,
           fill=P["muted"], anchor="middle")

    # ---------------- bottom: one row, zoomed ----------------
    c.line(40, 290, 920, 290, stroke=P["rule"], sw=1)
    c.text(40, 314, "把一行放大看：这串数就是 token 的表示", size=10.5,
           fill=P["ink2"], weight="600")

    c.rect(40, 328, 48, 26, fill=OL, stroke=OM, rx=5)
    c.text(64, 345.5, "ment", size=10, fill=P["orange"], anchor="middle",
           family="mono")
    c.arrow(92, 341, 110, 341, color=P["muted"], sw=1.1, head=4.5)
    c.rect(114, 328, 62, 26, fill=P["panel2"], stroke=P["rule"], rx=5)
    c.text(145, 345.5, "id 78", size=10, fill=P["ink2"], anchor="middle",
           family="mono")
    c.arrow(180, 341, 198, 341, color=P["muted"], sw=1.1, head=4.5)

    vals = ["0.21", "−0.03", "0.44", "0.07", "−0.12", "0.33", "0.05", "−0.28"]
    for i, v in enumerate(vals):
        cx = 202 + i * 35
        c.rect(cx, 328, 32, 26, fill=P["blueL"], stroke=P["blueM"], rx=2, sw=0.8)
        c.text(cx + 16, 345.5, v, size=8.8, fill=P["blue"], anchor="middle",
               family="mono")
    c.text(496, 345.5, "= E[78]，一个 d 维向量", size=10.2, fill=P["ink2"])

    c.text(40, 384, "查表没有非线性：它只是按 id 取出 E 的一行。",
           size=9.8, fill=P["muted"])
    c.text(40, 400, "训练时，这一行的梯度来自语料里所有出现过该 token 的位置。",
           size=9.8, fill=P["muted"])

    # ---------------- notes ----------------
    c.text(40, 470, "id 只是索引，本身没有大小含义；查表把离散的 id 变成连续的 d 维向量。",
           size=10.8, fill=P["muted"])
    c.text(40, 488, "d 通常是几千量级（如 4096）；位置信息不在嵌入里，而是在下一步的位置编码中加入。",
           size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 19 — temperature reshapes the next-token distribution
# ---------------------------------------------------------------------------

def f19():
    c = Canvas(960, 440)
    toks = ["的", "了", "是", "在", "和"]
    logits = [2.8, 1.6, 0.8, 0.1, -0.7]
    taus = [0.5, 1.0, 2.0]

    def softmax(zs):
        m = max(zs)
        e = [math.exp(z - m) for z in zs]
        s = sum(e)
        return [v / s for v in e]

    c.text(40, 30, "同一组 logits，三种温度：softmax(z / τ)", size=10.6,
           fill=P["muted"])

    BASE, SCALE = 326, 226
    descs = ["首位 0.90，几乎总是选「的」", "前 3 个累计 0.94", "首位 0.43，五个候选差距缩小"]
    marks = ["分布很尖", "原始分布", "分布变平"]

    for i, tau in enumerate(taus):
        x = 40 + i * 304
        p = softmax([z / tau for z in logits])

        c.text(x + 16, 74, f"τ = {tau:.1f}", size=13, fill=P["ink"], weight="600")
        c.text(x + 84, 74, marks[i], size=10.2, fill=P["muted"])

        # grid + axes
        for v, gy in ((0.5, BASE - SCALE * 0.5), (1.0, BASE - SCALE)):
            c.line(x + 30, gy, x + 252, gy, stroke=P["rule"], sw=0.8, dash="2 3")
        c.line(x + 30, BASE, x + 252, BASE, stroke=P["ink2"], sw=1)
        if i == 0:
            for v, gy in ((0.0, BASE), (0.5, BASE - SCALE * 0.5), (1.0, BASE - SCALE)):
                c.text(x + 26, gy + 3.5, f"{v:.1f}", size=9, fill=P["muted"],
                       anchor="end")

        for j, pj in enumerate(p):
            bx = x + 36 + j * 45
            h = max(1.2, pj * SCALE)
            t = 0.18 + 0.62 * math.sqrt(pj)
            c.rect(bx, BASE - h, 32, h, fill=BLUES(t), stroke="none", rx=2)
            val = f"{pj:.2f}" if pj >= 0.005 else "<0.01"
            c.text(bx + 16, BASE - h - 6, val, size=9.2, fill=P["ink2"],
                   anchor="middle", family="mono")
            c.text(bx + 16, 344, toks[j], size=11.5, fill=P["ink2"], anchor="middle")

        # top-k cut on the tau = 1 panel
        if i == 1:
            cut = x + 36 + 3 * 45 - 6.5
            c.line(cut, BASE, cut, 96, stroke=P["orange"], sw=1.2, dash="4 3")
            c.text(cut + 5, 92, "top-k = 3", size=9.3, fill=P["orange"],
                   weight="600")

        c.text(x + 136, 374, descs[i], size=9.6, fill=P["muted"], anchor="middle")

    # ---------------- notes ----------------
    c.text(40, 402, "贪心解码 = 取 argmax；采样 = 按概率抽；top-k 只保留前 k 个；"
                    "top-p 保留累计概率达到阈值的最小集合。", size=10.3, fill=P["muted"])
    c.text(40, 420, "温度不改变候选的排序（z/τ 单调、softmax 保序），只改变分布的平缓程度；"
                    "过低容易重复，过高容易跑题。", size=10.3, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 20 — pretraining -> post-training -> deployment
# ---------------------------------------------------------------------------

def f20():
    c = Canvas(960, 420)
    XS = [40, 222, 404, 586, 768]
    BW, BY, BH = 152, 66, 142
    CY = 137

    stages = [
        dict(col=P["violet"], fill=P["violetL"], stroke=P["violetM"], num="1",
             title="预训练", sub="pre-training",
             lines=["海量文本 / 代码", "自监督 · 下一 token 预测"],
             tag="base model", signal="训练信号：下一 token 的似然"),
        dict(col=P["blue"], fill=P["blueL"], stroke=P["blueM"], num="2",
             title="SFT 指令微调", sub="supervised fine-tuning",
             lines=["指令 + 示范答案", "模仿人类的写法"],
             tag="instruct model", signal="训练信号：示范答案的似然"),
        dict(col=P["orange"], fill=P["orangeL"], stroke=P["orangeM"], num="3",
             title="偏好优化", sub="RLHF / DPO",
             lines=["成对比较：A 优于 B", "让好答案更可能"],
             tag="aligned model", signal="训练信号：人类偏好比较"),
        dict(col=P["green"], fill=P["greenL"], stroke=P["greenM"], num="4",
             title="可验证奖励", sub="RLVR / GRPO",
             lines=["规则、单测、标准答案", "答对才给奖励"],
             tag="reasoning model", signal="训练信号：规则 / 测试判定"),
        dict(col=P["teal"], fill=P["tealL"], stroke=P["tealM"], num="5",
             title="部署使用", sub="inference",
             lines=["prompt + 上下文", "工具、检索、记忆"],
             tag="产品 / API", signal="训练信号：无，仅前向推理"),
    ]

    # grouping labels
    c.text(116, 34, "预训练", size=10.8, fill=P["violet"], weight="600",
           anchor="middle")
    c.text(480, 34, "后训练（post-training）", size=10.8, fill=P["violet"],
           weight="600", anchor="middle")
    c.text(844, 34, "推理 / 使用", size=10.8, fill=P["teal"], weight="600",
           anchor="middle")

    # band behind stages 2-4
    c.rect(206, 46, 548, 204, fill=P["violetL"], stroke="none", rx=8)

    for x, s in zip(XS, stages):
        c.rect(x, BY, BW, BH, fill=s["fill"], stroke=s["stroke"], rx=8)
        c.circle(x + 18, BY + 22, 8.5, fill=P["white"], stroke=s["col"], sw=1)
        c.text(x + 18, BY + 25.5, s["num"], size=9.5, fill=s["col"],
               anchor="middle", weight="600")
        c.text(x + 32, BY + 26, s["title"], size=12.5, fill=s["col"], weight="600")
        c.text(x + 32, BY + 41, s["sub"], size=8.8, fill=P["muted"])

        c.text(x + 16, BY + 70, s["lines"][0], size=10, fill=P["ink2"])
        c.text(x + 16, BY + 88, s["lines"][1], size=10, fill=P["ink2"])

        c.rect(x + 16, BY + 102, 120, 24, fill=P["white"], stroke=s["stroke"],
               rx=12, sw=0.9)
        c.text(x + 76, BY + 117.5, s["tag"], size=9.2, fill=s["col"],
               anchor="middle", family="mono")

        c.text(x, 230, s["signal"], size=9.4, fill=P["muted"])

    for x in XS[:-1]:
        c.arrow(x + BW + 2, CY, x + BW + 28, CY, color=P["muted"], sw=1.4, head=5)

    # feedback loop: deployment -> post-training
    c.path("M 910 208 L 910 254 Q 910 276 888 276 L 752 276 "
           "Q 730 276 730 254 L 730 218",
           stroke=P["muted"], sw=1.1, dash="3 3", cap="round", join="round")
    c.poly([(730, 208), (725.5, 217), (734.5, 217)], fill=P["muted"])
    c.text(820, 266, "评测 / 反馈 → 继续迭代", size=9.2, fill=P["muted"],
           anchor="middle")

    # ---------------- notes ----------------
    c.text(40, 366, "预训练给基础能力，后训练给行为与偏好；实际流程常常组合使用，不是三选一。",
           size=10.8, fill=P["muted"])
    c.text(40, 384, "越靠后的阶段数据越少、越针对具体行为；部署阶段只做前向推理，不再更新参数。",
           size=10.8, fill=P["muted"])
    return c


FIGURES = {
    "17_bpe-tokenization": f17,
    "18_tokenization-and-embedding": f18,
    "19_temperature-next-token-distribution": f19,
    "20_training-to-usage-workflow": f20,
}
