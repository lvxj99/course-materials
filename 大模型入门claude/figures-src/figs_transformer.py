"""第 7.0–7.4 节：原始 Transformer、因果掩码、多头注意力、位置编码、Block、三类架构。"""
import math

from svgkit import *


# ---------------------------------------------------------------------------
# 共用小部件
# ---------------------------------------------------------------------------
def token_row(s, cx, y, toks, key="k", size=13.5, gap=7, pad=8, keys=None):
    """把一排 token 胶囊居中排在 cx 处，返回各胶囊中心 x。"""
    ws = [text_width(t, size) + 2 * pad for t in toks]
    total = sum(ws) + gap * (len(toks) - 1)
    x = cx - total / 2
    centers = []
    for i, (t, w) in enumerate(zip(toks, ws)):
        c = x + w / 2
        s.pill(c, y, t, key=(keys[i] if keys else key), size=size, pad=pad)
        centers.append(c)
        x += w + gap
    return centers


def mask_icon(s, x, y, kind, n=4, m=None, cell=10):
    """注意力读取范围小图标。kind: full / causal / cross。左上角 (x,y)。"""
    m = m or n
    for i in range(n):
        for j in range(m):
            ok = kind != "causal" or j <= i
            if kind == "cross":
                f = main("attn") if ok else light("loss")
            f = mix(main("attn"), WHITE, 0.15) if ok else light("loss")
            s.rect(x + j * cell, y + i * cell, cell, cell, fill=f, stroke=WHITE, sw=1.2)
    if kind == "cross":
        # 行=译文（橙），列=原文（蓝）
        s.rect(x - 4, y, 3, n * cell, fill=main("q"))
        s.rect(x, y - 4, m * cell, 3, fill=main("k"))
    return x + m * cell, y + n * cell


# ---------------------------------------------------------------------------
# 01 原始 Transformer：编码器—解码器
# ---------------------------------------------------------------------------
def fig01():
    s = SVG(1000, 760, "原始 Transformer 编码器—解码器架构",
            "编码器用双向自注意力读原文；解码器用因果自注意力读已生成的译文，再用交叉注意力读原文。")
    s.text(500, 26, "原始 Transformer：编码器读原文，解码器一边读原文一边写译文", size=17, weight="bold")

    bw, bh, nh = 230, 40, 28  # 子层框宽高、Add&Norm 高
    ex, dx = 265, 700         # 两列中心

    def sub(cx, y, label, key, sublabel=None):
        s.box(cx - bw / 2, y, bw, bh, label, key=key, size=14.5, sub=sublabel, subsize=11.5)

    def addnorm(cx, y):
        s.box(cx - bw / 2, y, bw, nh, "Add & Norm", key="gray", size=13, weight="normal")

    def resid(cx, y_from, y_to, side=-1):
        """残差旁路：从子层下方绕到 Add&Norm。"""
        xx = cx + side * (bw / 2 + 20)
        s.arrow([(cx, y_from), (xx, y_from), (xx, y_to), (cx + side * bw / 2, y_to)], color=LINE, sw=1.4, head=0.85)

    # ---------------- 编码器 ----------------
    s.rect(ex - 160, 330, 320, 290, fill=light("k"), stroke=main("k"), sw=1.2, rx=14, opacity=0.55)
    s.text(ex - 145, 350, "编码器", size=15, weight="bold", color=main("k"), anchor="start")
    s.text(ex + 145, 350, "× N 层", size=14, weight="bold", color=main("k"), anchor="end")
    y_attn, y_n1, y_ffn, y_n2 = 550, 500, 438, 390
    sub(ex, y_attn, "多头自注意力", "attn", "双向：每个词读整句")
    addnorm(ex, y_n1)
    sub(ex, y_ffn, "前馈网络 FFN", "ffn")
    addnorm(ex, y_n2)
    s.varrow(ex, 640, y_attn + bh + 1, color=INK)
    s.varrow(ex, y_attn, y_n1 + nh + 1, color=INK)
    s.varrow(ex, y_n1, y_ffn + bh + 1, color=INK)
    s.varrow(ex, y_ffn, y_n2 + nh + 1, color=INK)
    resid(ex, 610, y_n1 + nh / 2)
    resid(ex, y_n1 - 10, y_n2 + nh / 2)
    # 编码器输出
    s.varrow(ex, y_n2, 300, color=INK)
    s.box(ex - 130, 254, 260, 44, "编码器输出", key="k", size=14, sub="原文每个位置一个向量", subsize=11.5)

    # ---------------- 解码器 ----------------
    s.rect(dx - 160, 175, 320, 445, fill=light("q"), stroke=main("q"), sw=1.2, rx=14, opacity=0.55)
    s.text(dx - 145, 195, "解码器", size=15, weight="bold", color=main("q"), anchor="start")
    s.text(dx + 145, 195, "× N 层", size=14, weight="bold", color=main("q"), anchor="end")
    d_sa, d_n1, d_ca, d_n2, d_ffn, d_n3 = 550, 500, 420, 372, 282, 234
    sub(dx, d_sa, "掩码多头自注意力", "attn", "因果：只读自己和之前")
    addnorm(dx, d_n1)
    sub(dx, d_ca, "交叉注意力", "attn", "Q 来自译文，K、V 来自原文")
    addnorm(dx, d_n2)
    sub(dx, d_ffn, "前馈网络 FFN", "ffn")
    addnorm(dx, d_n3)
    s.varrow(dx, 640, d_sa + bh + 1, color=INK)
    s.varrow(dx, d_sa, d_n1 + nh + 1, color=INK)
    s.varrow(dx, d_n1, d_ca + bh + 1, color=INK)
    s.varrow(dx, d_ca, d_n2 + nh + 1, color=INK)
    s.varrow(dx, d_n2, d_ffn + bh + 1, color=INK)
    s.varrow(dx, d_ffn, d_n3 + nh + 1, color=INK)
    resid(dx, 610, d_n1 + nh / 2, side=1)
    resid(dx, d_n1 - 10, d_n2 + nh / 2, side=1)
    resid(dx, d_n2 - 10, d_n3 + nh / 2, side=1)

    # 编码器输出 → 交叉注意力（K、V）
    s.arrow([(ex + 130, 276), (500, 276), (500, d_ca + bh / 2), (dx - bw / 2, d_ca + bh / 2)],
            color=main("k"), sw=2.4)
    s.rect(470, 330, 60, 24, fill=WHITE, stroke=main("k"), sw=1.2, rx=12)
    s.text(500, 342, "K, V", size=13.5, weight="bold", color=main("k"))

    # 输出头
    s.box(dx - 95, 136, 190, 32, "Linear + softmax", key="gray", size=13.5)
    s.arrow([(dx, d_n3), (dx, 170)], color=INK)
    s.varrow(dx, 136, 116, color=INK)
    cands = [("学习", 0.82), ("研究", 0.10), ("其他", 0.08)]
    s.text(dx - 104, 73, "下一个词的概率", size=13, color=MUTED, anchor="end")
    for i, (w, p) in enumerate(cands):
        yy = 54 + i * 19
        s.text(dx - 76 + 20, yy, w, size=12.5, anchor="end", weight="bold" if i == 0 else "normal")
        s.rect(dx - 48, yy - 7, 150 * p, 14, fill=main("q") if i == 0 else light("q"), stroke=main("q"), sw=0.8, rx=3)
        s.text(dx - 48 + 150 * p + 6, yy, f"{p:.2f}", size=12, anchor="start", color=MUTED)
    s.text(dx + 120, 54, "→ 选出“学习”", size=13, anchor="start", color=main("q"), weight="bold")

    # 底部 token 与嵌入
    for cx, toks, key, lab in [(ex, ["I", "love", "machine", "learning"], "k", "原文（编码器输入）"),
                               (dx, ["<bos>", "我", "喜欢", "机器"], "q", "已生成的译文（右移一位）")]:
        s.box(cx - bw / 2, 640, bw, 34, "词嵌入 + 位置编码", key="gray", size=13.5, weight="normal")
        s.varrow(cx, 702, 676, color=INK)
        token_row(s, cx, 718, toks, key=key, size=13.5)
        s.text(cx, 748, lab, size=13, color=main(key))

    # 读取范围小图标
    mask_icon(s, 44, 548, "full")
    s.lines(64, 604, ["全部可读"], size=12.5, color=MUTED)
    mask_icon(s, 870, 548, "causal")
    s.lines(890, 604, ["未来位置屏蔽"], size=12.5, color=MUTED)
    mask_icon(s, 870, 418, "cross")
    s.lines(890, 474, ["行：译文", "列：原文"], size=12.5, color=MUTED, gap=17)
    s.text(890, 392, "读取范围", size=12.5, color=main("attn"), weight="bold")
    s.text(64, 526, "读取范围", size=12.5, color=main("attn"), weight="bold")
    s.rect(30, 120, 340, 84, fill=PANEL, stroke=BORDER, rx=10)
    s.lines(46, 142, ["灰色细线 = 残差连接：子层的输入直接加到输出上", "Add & Norm = 先相加、再归一化（Post-Norm，",
                      "原始论文做法；现代 LLM 多用 Pre-Norm）"], size=12.5, color=MUTED, anchor="start", gap=20)
    s.save(OUT / "01_original-transformer-architecture.svg")


# ---------------------------------------------------------------------------
# 28 因果掩码与错开一位的训练目标
# ---------------------------------------------------------------------------
def fig28():
    inp = ["<bos>", "我", "喜欢", "机器", "学习"]
    tgt = ["我", "喜欢", "机器", "学习", "<eos>"]
    n = 5
    hi = 2
    c = 58
    x0, y0 = 150, 132
    s = SVG(1040, 480, "因果掩码与错开一位的训练目标",
            "每个位置只能读自己和之前的位置，并预测下一个 token；所有位置在一次前向计算中并行训练。")
    s.text(520, 30, "因果掩码：所有位置并行训练，但谁都看不到答案", size=17, weight="bold")
    s.text(x0 + n * c / 2, 68, "可以读取的位置（Key）", size=13.5, color=main("k"))
    for j, t in enumerate(inp):
        s.text(x0 + j * c + c / 2, y0 - 18, t, size=14)
    s.raw(f'<g transform="rotate(-90 38 {y0 + n * c / 2})">')
    s.text(38, y0 + n * c / 2, "当前位置（Query）", size=13.5, color=main("q"))
    s.raw("</g>")
    for i, t in enumerate(inp):
        s.text(x0 - 12, y0 + i * c + c / 2, t, size=14, anchor="end", weight="bold" if i == hi else "normal")

    def fill(i, j):
        if j > i:
            return light("loss")
        return main("attn") if i == hi else mix(main("attn"), WHITE, 0.72)

    def val(i, j):
        return "−∞" if j > i else ("✓" if i == hi else "")

    s.grid(x0, y0, n, n, c, fills=fill, values=val, vsize=15,
           vcolor=lambda i, j: main("loss") if j > i else WHITE, stroke=WHITE, sw=2.5)
    s.rect(x0 - 3, y0 + hi * c - 3, n * c + 6, c + 6, fill="none", stroke=main("q"), sw=3, rx=6)

    # 目标列
    tx = x0 + n * c + 90
    s.text(tx, y0 - 18, "训练目标", size=14, weight="bold", color=main("v"))
    for i, t in enumerate(tgt):
        y = y0 + i * c + c / 2
        s.arrow([(x0 + n * c + 10, y), (tx - 34, y)], color=main("q") if i == hi else LINE,
                sw=2.2 if i == hi else 1.3)
        s.pill(tx, y, t, key="v", size=14, pad=10,
               fill=main("v") if i == hi else None, color=WHITE if i == hi else INK,
               weight="bold" if i == hi else "normal")
    s.text(x0 + n * c / 2, y0 + n * c + 26, "红色 −∞：softmax 后权重为 0，即“读不到”", size=13, color=main("loss"))

    # 右侧说明
    px, py, pw = 610, 100, 400
    s.panel(px, py, pw, 354)
    s.text(px + 20, py + 28, "看高亮的一行（“喜欢”）", size=15, weight="bold", anchor="start")
    s.lines(px + 20, py + 58, ["能读：<bos>、我、喜欢", "读不到：机器、学习（未来）", "要预测：下一个词“机器”"],
            size=13.5, anchor="start", gap=24)
    s.line(px + 20, py + 140, px + pw - 20, py + 140, color=BORDER, sw=1)
    s.text(px + 20, py + 164, "目标 = 输入整体左移一位", size=15, weight="bold", anchor="start")
    cx = px + pw / 2 + 30
    sp = 64
    for k in range(n):
        x = cx + (k - 2) * sp
        s.pill(x, py + 204, inp[k], key="k", size=13, pad=7)
        s.pill(x, py + 266, tgt[k], key="v", size=13, pad=7)
        s.arrow([(x, py + 219), (x, py + 250)], color=LINE, sw=1.3, head=0.8)
    s.text(px + 20, py + 204, "输入", size=13, color=main("k"), anchor="start")
    s.text(px + 20, py + 266, "目标", size=13, color=main("v"), anchor="start")
    s.lines(px + 20, py + 306, ["一次前向计算同时得到 5 个预测和 5 份损失，"],
            size=13.5, anchor="start")
    s.text(px + 20, py + 328, "而 RNN 需要沿序列一步一步算。", size=13.5, anchor="start", color=MUTED)
    s.save(OUT / "28_causal-mask-and-shifted-targets.svg")


# ---------------------------------------------------------------------------
# 04 多头注意力
# ---------------------------------------------------------------------------
def fig04():
    T, d, h = 4, 6, 3
    dh = d // h
    assert dh * h == d
    words = ["I", "love", "machine", "learning"]
    heads = [
        ("pink", "头 1：多看前一个词",
         [[1, 0, 0, 0], [0.8, 0.2, 0, 0], [0.1, 0.8, 0.1, 0], [0.05, 0.1, 0.75, 0.1]]),
        ("ffn", "头 2：多看语义相关的词",
         [[0.4, 0.4, 0.1, 0.1], [0.5, 0.3, 0.1, 0.1], [0.05, 0.05, 0.3, 0.6], [0.05, 0.05, 0.6, 0.3]]),
        ("data", "头 3：多看自己",
         [[0.85, 0.05, 0.05, 0.05], [0.05, 0.85, 0.05, 0.05], [0.05, 0.05, 0.85, 0.05], [0.05, 0.05, 0.05, 0.85]]),
    ]
    for _, _, A in heads:
        for r in A:
            assert abs(sum(r) - 1) < 1e-9
    s = SVG(1100, 470, "多头注意力", "每个头用自己的投影独立做一次注意力读取，各头输出拼接后经 W_O 投影回 d 维。")
    s.text(550, 30, "多头注意力：几组投影各读一遍，再拼起来", size=17, weight="bold")
    c = 17
    ys = [125, 245, 365]  # 各头中心
    # 输入 X
    xX, yX = 40, 245 - T * c / 2
    s.grid(xX, yX, T, d, c, fills=lambda i, j: light("gray"), stroke=WHITE, sw=1.2)
    s.rect(xX, yX, d * c, T * c, fill="none", stroke=main("gray"), sw=1.2)
    s.text(xX + d * c / 2, yX - 16, "$X$", size=17, weight="bold")
    s.text(xX + d * c / 2, yX + T * c + 18, "$T$×$d$", size=13.5, color=MUTED)
    for k, (key, lab, A) in enumerate(heads):
        y = ys[k]
        # 分叉
        s.arrow([(xX + d * c + 6, 245), (182, 245), (182, y), (204, y)], color=main(key), sw=1.6)
        # 投影框
        s.box(208, y - 26, 150, 52, f"$W$_{{Q}}^{{({k + 1})}}  $W$_{{K}}^{{({k + 1})}}  $W$_{{V}}^{{({k + 1})}}",
              key=key, size=14, weight="normal")
        s.harrow(362, 400, y, color=main(key))
        # 注意力图样
        ax, ay = 410, y - 2 * 16
        s.grid(ax, ay, 4, 4, 16, fills=lambda i, j, A=A, key=key: heat(A[i][j], key), stroke=WHITE, sw=1)
        s.rect(ax, ay, 64, 64, fill="none", stroke=main(key), sw=1)
        s.text(ax + 82, y - 10, lab, size=13.5, anchor="start", weight="bold", color=INK)
        s.text(ax + 82, y + 12, f"Attention → head_{{{k + 1}}}", size=12.5, anchor="start", color=MUTED)
        # head 输出
        hx = 680
        s.harrow(650, hx - 6, y, color=main(key))
        s.grid(hx, y - T * c / 2, T, dh, c, fills=lambda i, j, key=key: main(key), stroke=WHITE, sw=1.2)
        s.text(hx + dh * c + 10, y, f"$T$×$d$/$h$", size=12.5, color=MUTED, anchor="start")
    s.text(550, ys[2] + 56, "（4×4 小图：行=读取者 I / love / machine / learning，列=被读取者）", size=12.5, color=MUTED)
    # 拼接
    cx = 820
    yC = 245 - T * c / 2
    for k, (key, _, _) in enumerate(heads):
        s.arrow([(hx + dh * c + 60, ys[k]), (cx - 26, ys[k]), (cx - 26, 245 + (k - 1) * 18), (cx - 6, 245 + (k - 1) * 18)],
                color=main(key), sw=1.4, head=0.8)
        s.grid(cx + k * dh * c, yC, T, dh, c, fills=lambda i, j, key=key: main(key), stroke=WHITE, sw=1.2)
    s.text(cx + d * c / 2, yC - 16, "Concat", size=15, weight="bold")
    s.text(cx + d * c / 2, yC + T * c + 18, "$T$×($h$·$d$_{v}) = $T$×$d$", size=13, color=MUTED)
    # W_O
    s.harrow(cx + d * c + 8, 952, 245, color=INK)
    s.box(956, 225, 44, 40, "$W$_{O}", key="gray", size=15, weight="normal")
    s.harrow(1002, 1014, 245, color=INK)
    s.grid(1018, yC, T, d, 11, fills=lambda i, j: heat(0.55 + 0.1 * ((i + j) % 3), "attn"), stroke=WHITE, sw=1,
           cellh=c)
    s.text(1018 + 33, yC - 16, "输出", size=15, weight="bold")
    s.text(1018 + 33, yC + T * c + 18, "$T$×$d$", size=13, color=MUTED)
    s.text(550, 446, "各头参数独立、一起训练；不同的头学到不同的“关注方式”（图中图样为教学示例）。", size=13, color=MUTED)
    s.save(OUT / "04_scaled-dot-product-and-multi-head-attention.svg")


# ---------------------------------------------------------------------------
# 05 位置编码与 RoPE
# ---------------------------------------------------------------------------
def _diverging(v):
    """-1 → 蓝, 0 → 白, +1 → 橙。"""
    if v >= 0:
        col = mix("#FFFFFF", main("q"), v)
    else:
        col = mix("#FFFFFF", main("k"), -v)
    return tuple(int(col[i:i + 2], 16) for i in (1, 3, 5))


def fig05():
    s = SVG(1080, 660, "位置编码与 RoPE", "纯自注意力分不清词序；正弦位置编码像一组快慢不同的时钟；RoPE 让点积只依赖相对位移。")

    # ---------------- (a) 为什么需要位置 ----------------
    s.panel(20, 16, 1040, 176, "为什么需要位置信息？", key="loss", tag="a")
    wc = {"狗": "k", "咬": "attn", "人": "v"}

    def sentence(x, y, toks):
        cs = []
        for i, t in enumerate(toks):
            cx = x + i * 52
            s.pill(cx, y, t, key=wc[t], size=15, pad=11)
            cs.append(cx)
        return cs

    for row, toks in enumerate([["狗", "咬", "人"], ["人", "咬", "狗"]]):
        y = 82 + row * 62
        cs = sentence(80, y, toks)
        s.harrow(218, 296, y, color=INK)
        s.text(257, y - 13, "自注意力", size=12.5, color=MUTED)
        s.text(257, y + 13, "（无位置）", size=12.5, color=MUTED)
        for i, t in enumerate(toks):
            x = 318 + i * 64
            s.grid(x, y - 11, 1, 3, 15, fills=lambda a, b, t=t: mix(main(wc[t]), WHITE, 0.15 + 0.3 * b), stroke=WHITE)
            s.text(x + 22, y + 22, f"$o$_{{{t}}}", size=12.5, color=main(wc[t]))
    s.lines(520, 72, ["两句话得到的是同一组输出向量，只是换了行的顺序。",
                      "“狗”无论在第 1 位还是第 3 位，算出的表示都一样，",
                      "模型分不清谁咬谁。"], size=13.5, anchor="start", gap=22)
    s.rect(520, 140, 520, 38, fill=light("v"), stroke=main("v"), rx=8)
    s.text(536, 159, "解决：给第 $t$ 个位置加上坐标  $x̃$_{t} = $x$_{t} + $p$_{t}，或在打分里引入相对位置",
           size=13.5, anchor="start")

    # ---------------- (b) 正弦位置编码热图 ----------------
    s.panel(20, 206, 520, 438, "正弦位置编码：一组快慢不同的“时钟”", key="data", tag="b")
    P, D = 64, 64
    J = D // 2  # 只画 sin 维（第 2j 维），共 32 个频率
    pe = [[math.sin(tt / 10000 ** (2 * j / D)) for j in range(J)] for tt in range(P)]
    assert abs(pe[1][0] - math.sin(1)) < 1e-12 and abs(pe[5][8] - math.sin(5 / 10)) < 1e-12
    hx, hy, cwid, rh = 96, 262, 10.0, 3.0
    s.image(hx, hy, J * cwid, P * rh, png_uri([[_diverging(v) for v in row] for row in pe], mode="RGB"))
    s.rect(hx, hy, J * cwid, P * rh, fill="none", stroke=BORDER, sw=1)
    s.text(hx + J * cwid / 2, hy + P * rh + 16, "频率序号 $j$（只画第 2$j$ 维的 sin）→ 越往右转得越慢", size=12.5, color=MUTED)
    s.raw(f'<g transform="rotate(-90 {hx - 34} {hy + P * rh / 2})">')
    s.text(hx - 34, hy + P * rh / 2, "位置 $t$（向下递增）", size=12.5, color=MUTED)
    s.raw("</g>")
    for tt in (0, 30, 63):
        s.text(hx - 6, hy + tt * rh + rh / 2, str(tt), size=11, anchor="end", color=MUTED)
    lx = hx + J * cwid + 16
    for k in range(21):
        col = _diverging(1 - k / 10)
        s.rect(lx, hy + k * 9.14, 12, 9.24, fill="#%02X%02X%02X" % col)
    s.text(lx + 18, hy + 4, "+1", size=11, anchor="start", color=MUTED)
    s.text(lx + 18, hy + 96, "0", size=11, anchor="start", color=MUTED)
    s.text(lx + 18, hy + 188, "−1", size=11, anchor="start", color=MUTED)
    cw = J * cwid
    for k, (j, key, lab) in enumerate([(0, "q", "$j$=0：转得快，约 6 个位置一圈"), (8, "k", "$j$=8：转得慢，约 63 个位置一圈")]):
        yb = 542 + k * 52
        s.text(hx, yb - 24, lab, size=12.5, anchor="start", color=main(key))
        s.line(hx, yb, hx + cw, yb, color=BORDER, sw=1)
        fine = []
        for q in range(400):
            tt = q / 399 * (P - 1)
            fine.append((hx + tt / (P - 1) * cw, yb - 13 * math.sin(tt / 10000 ** (2 * j / D))))
        s.polyline(fine, stroke=main(key), sw=1.8)
        s.rect(hx + j * cwid, hy - 7, cwid, 5, fill=main(key))
    s.text(hx + cw / 2, 628, "每个位置得到一串独一无二的“读数”；相邻位置读数接近", size=12.5, color=INK)

    # ---------------- (c) RoPE ----------------
    s.panel(556, 206, 504, 438, "RoPE：按位置旋转 Q、K，点积只看距离", key="attn", tag="c")
    th = 25  # 每个位置转 25°
    base = 10
    R = 74
    for k, (t, sp) in enumerate([(1, 3), (5, 7)]):
        cx, cy = 686 + k * 244, 436
        s.circle(cx, cy, R + 8, fill=WHITE, stroke=BORDER, sw=1)
        s.line(cx - R - 14, cy, cx + R + 14, cy, color=BORDER, sw=1)
        s.line(cx, cy - R - 14, cx, cy + R + 14, color=BORDER, sw=1)
        aq, ak = base + t * th, base + sp * th
        assert (ak - aq) == 50
        for ang, key, lab in [(aq, "q", f"$q$′_{{{t}}}"), (ak, "k", f"$k$′_{{{sp}}}")]:
            ex, ey = cx + R * math.cos(math.radians(ang)), cy - R * math.sin(math.radians(ang))
            s.arrow([(cx, cy), (ex, ey)], color=main(key), sw=2.6)
            lx2, ly2 = cx + (R + 22) * math.cos(math.radians(ang)), cy - (R + 22) * math.sin(math.radians(ang))
            s.text(lx2, ly2, lab, size=15, color=main(key), weight="bold")
        # 夹角弧
        arc = [(cx + 34 * math.cos(math.radians(a)), cy - 34 * math.sin(math.radians(a)))
               for a in [aq + (ak - aq) * i / 20 for i in range(21)]]
        s.polyline(arc, stroke=main("attn"), sw=2.2)
        am = math.radians((aq + ak) / 2)
        s.text(cx + 50 * math.cos(am), cy - 50 * math.sin(am), "50°", size=12.5, color=main("attn"), weight="bold")
        s.text(cx, cy + R + 34, f"$t$ = {t}，$s$ = {sp}", size=14, weight="bold")
        s.text(cx, cy + R + 56, f"$q$ 转 {t}×25°，$k$ 转 {sp}×25°", size=12.5, color=MUTED)
    s.lines(576, 254, ["把向量每两维看成一个平面：位置 $t$ 的 $q$ 转 $tθ$，位置 $s$ 的 $k$ 转 $sθ$。",
                       "两组位置不同，但相隔都是 $s$−$t$ = 2，夹角相同 → 点积相同。"],
            size=13, anchor="start", gap=22)
    s.rect(600, 296, 416, 34, fill=light("attn"), stroke=main("attn"), rx=8)
    s.text(808, 313, "$q$′_{t}^{⊤}$k$′_{s} = $q$_{t}^{⊤}$R$($s$−$t$)$k$_{s}", size=15)
    s.text(808, 628, "（示意：一个二维子平面，θ = 25°；真实模型每对维度用不同的 θ）", size=12, color=MUTED)
    s.save(OUT / "05_positional-encoding-and-rope.svg")


# ---------------------------------------------------------------------------
# 06 Pre-Norm Transformer Block
# ---------------------------------------------------------------------------
def fig06():
    s = SVG(1040, 676, "Transformer Block（Pre-Norm）", "残差流贯穿整个 Block，注意力与 FFN 先归一化，再把结果加回残差流。")
    s.text(520, 28, "一个 Transformer Block（Pre-Norm）：两个子层，各自把结果加回残差流", size=17, weight="bold")
    rx = 170          # 残差流 x
    bx = 360          # 分支中心
    bw = 190
    y_in, y_add1, y_add2, y_out = 590, 360, 150, 66
    # 残差流
    s.rect(rx - 7, y_out + 18, 14, y_in - y_out - 38, fill=mix(main("gray"), WHITE, 0.55), rx=7)
    s.raw(f'<g transform="rotate(-90 {rx - 46} {(y_in + y_out) / 2})">')
    s.text(rx - 46, (y_in + y_out) / 2, "残差流：形状始终是 $T$×$d$", size=13, color=MUTED)
    s.raw("</g>")
    s.box(rx - 60, y_in - 18, 120, 36, "$H$^{(ℓ)}", key="gray", size=16, weight="normal")
    s.box(rx - 60, y_out - 18, 120, 36, "$H$^{(ℓ+1)}", key="gray", size=16, weight="normal")
    s.varrow(rx, y_out + 52, y_out + 20, color=INK, sw=2)
    for y in (y_add1, y_add2):
        s.circle(rx, y, 17, fill=WHITE, stroke=INK, sw=1.8)
        s.text(rx, y + 0.5, "+", size=22, weight="bold")
    s.text(rx + 22, (y_add1 + y_add2) / 2 + 30, "$U$", size=17, anchor="start")

    def branch(y_from, y_to, boxes):
        """从残差流 y_from 分出，经过 boxes，回到 y_to 处的加号。"""
        s.arrow([(rx, y_from), (bx, y_from), (bx, boxes[0][0] + boxes[0][3])], color=INK, sw=1.6)
        for k, (y, lab, key, h) in enumerate(boxes):
            s.box(bx - bw / 2, y, bw, h, lab, key=key, size=15)
            if k + 1 < len(boxes):
                s.varrow(bx, y, boxes[k + 1][0] + boxes[k + 1][3] + 1, color=INK)
        s.arrow([(bx, boxes[-1][0]), (bx, y_to), (rx + 19, y_to)], color=INK, sw=1.6)
        s.circle(rx, y_from, 4, fill=INK)

    branch(545, y_add1, [(495, "Norm", "gray", 32), (410, "多头注意力", "attn", 50)])
    branch(320, y_add2, [(270, "Norm", "gray", 32), (190, "FFN", "ffn", 50)])
    s.text(bx + bw / 2 + 12, 435, "位置之间交换信息", size=13, color=main("attn"), anchor="start", weight="bold")
    s.text(bx + bw / 2 + 12, 215, "每个位置单独加工", size=13, color=main("ffn"), anchor="start", weight="bold")

    # 右侧：两种操作的直观对比
    px, pw = 620, 400
    words = ["I", "love", "machine", "learning"]
    colx = [px + 70 + k * 88 for k in range(4)]

    def tokens_cols(y, key_fill):
        for k, x in enumerate(colx):
            s.grid(x - 11, y, 4, 1, 22, fills=lambda i, j, k=k: mix(main(key_fill), WHITE, 0.35 + 0.12 * ((i + k) % 3)),
                   stroke=WHITE, sw=1.2, cellh=13)
            s.text(x, y + 66, words[k], size=12.5, color=MUTED)

    # FFN 小图
    s.panel(px, 76, pw, 236, "FFN：同一个 MLP，分别作用于每个位置", key="ffn")
    tokens_cols(194, "gray")
    for x in colx:
        s.box(x - 30, 122, 60, 30, "MLP", key="ffn", size=12.5)
        s.varrow(x, 192, 156, color=main("ffn"), sw=1.5)
        s.varrow(x, 120, 104, color=main("ffn"), sw=1.5)
    s.text(px + pw / 2, 292, "各列之间没有连线：位置之间不交流，参数共享", size=12.5, color=INK)

    # 注意力小图
    s.panel(px, 330, pw, 250, "注意力：每个位置去读其他位置", key="attn")
    tokens_cols(470, "gray")
    tgt = colx[3]
    for k, x in enumerate(colx[:3]):
        h = 40 + 26 * (3 - k)
        s.arrow([(x, 466), ((x + tgt) / 2, 466 - h * 1.6), (tgt - 4, 466)], color=main("attn"), sw=1.2 + (k == 2) * 2.2,
                curve=True, head=0.9)
    s.text(px + pw / 2, 566, "信息沿着箭头在位置之间流动（图示 learning 读取前面各词）", size=12.5, color=INK)

    # 底部：Pre-Norm vs Post-Norm
    s.rect(20, 626, 1000, 38, fill=PANEL, stroke=BORDER, rx=8)
    s.text(40, 645, "对比", size=13.5, weight="bold", anchor="start")
    s.text(90, 645, "Pre-Norm（本图，现代 LLM 常用）：$x$ ← $x$ + $F$(Norm($x$))", size=13.5, anchor="start")
    s.text(560, 645, "Post-Norm（原始 Transformer）：$x$ ← Norm($x$ + $F$($x$))", size=13.5, anchor="start", color=MUTED)
    s.save(OUT / "06_transformer-block-residual-norm.svg")


# ---------------------------------------------------------------------------
# 07 三类架构
# ---------------------------------------------------------------------------
def fig07():
    s = SVG(1100, 600, "三类 Transformer 架构",
            "Encoder-only 双向理解；Encoder–decoder 用交叉注意力连接输入和输出；Decoder-only 在同一序列上因果生成。")
    pw, ph, py = 345, 564, 18
    xs = [20, 377, 734]
    titles = [("Encoder-only", "k", "整段读完，形成理解"),
              ("Encoder–decoder", "attn", "先读输入，再写输出"),
              ("Decoder-only", "q", "一条序列，边读边续写")]
    for (t, key, sub), x in zip(titles, xs):
        s.panel(x, py, pw, ph)
        s.text(x + pw / 2, py + 30, t, size=18, weight="bold", color=main(key))
        s.text(x + pw / 2, py + 56, sub, size=13.5, color=MUTED)

    def stack(cx, y, w, label, key, sub=None):
        s.box(cx - w / 2, y, w, 60, label, key=key, size=14.5, sub=sub, subsize=12)

    y_blk, y_tok, y_out = 236, 360, 170

    # ---- Encoder-only ----
    cx = xs[0] + pw / 2
    stack(cx, y_blk, 220, "编码器 Block × N", "k", "双向自注意力")
    cs = token_row(s, cx, y_tok, ["I", "love", "machine", "learning"], key="k", size=13)
    s.varrow(cx, y_tok - 18, y_blk + 62, color=INK)
    for c in cs:
        s.grid(c - 7, 160, 3, 1, 14, fills=lambda i, j: mix(main("k"), WHITE, 0.3 + 0.2 * i), stroke=WHITE)
    s.varrow(cx, y_blk - 2, 206, color=INK)
    s.box(cx - 115, 92, 230, 40, "汇总 → 分类 / 检索 / 识别", key="gray", size=13.5, weight="normal")
    s.varrow(cx, 156, 134, color=INK)
    s.text(cx, 398, "每个词都能看到整句（左右两边），", size=12.5, color=INK)
    s.text(cx, 418, "输出每个位置的上下文表示", size=12.5, color=INK)

    # ---- Encoder–decoder ----
    cx = xs[1] + pw / 2
    ecx, dcx = cx - 82, cx + 82
    stack(ecx, y_blk, 140, "编码器 × N", "k", "双向")
    stack(dcx, y_blk, 140, "解码器 × N", "q", "因果 + 交叉")
    s.arrow([(ecx + 70, y_blk + 30), (dcx - 72, y_blk + 30)], color=main("k"), sw=2.4)
    s.text(cx, y_blk + 16, "K,V", size=12, color=main("k"), weight="bold")
    token_row(s, ecx, y_tok, ["I", "love", "ML"], key="k", size=12.5, gap=4, pad=6)
    token_row(s, dcx, y_tok, ["<bos>", "我", "喜欢"], key="q", size=12.5, gap=4, pad=6)
    s.varrow(ecx, y_tok - 18, y_blk + 62, color=INK)
    s.varrow(dcx, y_tok - 18, y_blk + 62, color=INK)
    s.varrow(dcx, y_blk - 2, y_out + 18, color=INK)
    token_row(s, dcx, y_out, ["我", "喜欢", "机器"], key="q", size=12.5, gap=4, pad=6)
    s.text(dcx, y_out - 30, "逐个输出译文", size=12.5, color=MUTED)
    s.text(ecx, y_tok + 30, "原文", size=12, color=main("k"))
    s.text(dcx, y_tok + 30, "已生成的译文", size=12, color=main("q"))
    s.text(cx, 418, "输出侧通过交叉注意力读取输入", size=12.5, color=INK)

    # ---- Decoder-only ----
    cx = xs[2] + pw / 2
    stack(cx, y_blk, 220, "解码器 Block × N", "q", "因果自注意力")
    seq = ["翻译：", "I", "love", "ML", "→", "我", "喜欢"]
    keys = ["k"] * 5 + ["q"] * 2
    cs = token_row(s, cx, y_tok, seq, keys=keys, size=12.5, gap=3, pad=5)
    s.varrow(cx, y_tok - 18, y_blk + 62, color=INK)
    s.varrow(cx, y_blk - 2, y_out + 18, color=INK)
    s.pill(cx, y_out, "下一个 token：机器", key="q", size=13, pad=10)
    rx = xs[2] + pw - 18
    s.arrow([(cx + 74, y_out), (rx, y_out), (rx, y_tok), (cs[-1] + 27, y_tok)],
            color=main("q"), sw=1.4, dash="5 4", head=0.85)
    s.text(rx - 6, (y_out + y_blk) / 2 - 10, "接回", size=12, color=main("q"), anchor="end")
    s.text((cs[0] + cs[4]) / 2, y_tok + 30, "提示", size=12, color=main("k"))
    s.text((cs[5] + cs[6]) / 2, y_tok + 30, "已生成", size=12, color=main("q"))
    s.text(cx, 418, "提示和生成内容放在同一条序列里", size=12.5, color=INK)

    # ---- 读取范围图标（与图 01、28 相同的画法）----
    iy = 446
    icons = [
        [("full", "全部可读", 0)],
        [("full", "编码器", -108), ("causal", "解码器自注意力", 0), ("cross", "交叉注意力", 108)],
        [("causal", "只读自己和之前", 0)],
    ]
    for x, group in zip(xs, icons):
        cx = x + pw / 2
        s.text(x + 18, iy + 20, "读取范围", size=12.5, color=main("attn"), weight="bold", anchor="start") \
            if len(group) == 1 else None
        for kind, lab, off in group:
            ix = cx + off - 20
            mask_icon(s, ix, iy, kind, cell=10)
            s.text(cx + off, iy + 54, lab, size=12, color=MUTED)

    # 底部：代表与任务
    info = [("BERT、ViT", "文本分类、检索表示、图像识别"),
            ("原始 Transformer、T5", "翻译、摘要"),
            ("GPT 系列与多数大语言模型", "续写、对话、通用生成")]
    for (m, task), x in zip(info, xs):
        s.line(x + 20, 520, x + pw - 20, 520, color=BORDER, sw=1)
        s.text(x + pw / 2, 540, f"代表：{m}", size=13, color=INK)
        s.text(x + pw / 2, 562, f"适合：{task}", size=13, color=MUTED)
    s.save(OUT / "07_transformer-architectures-encoder-decoder.svg")


if __name__ == "__main__":
    fig01()
    fig28()
    fig04()
    fig05()
    fig06()
    fig07()
