"""Transformer section figures."""

from __future__ import annotations

import math

from lib import (
    BLUE,
    FAINT,
    GOLD,
    GRAY,
    GREEN,
    INK,
    LINE,
    MUTED,
    ORANGE,
    PANEL,
    PAPER,
    PURPLE,
    RED,
    TEAL,
    Fig,
    bits,
    div_color,
    seq_color,
    softmax,
    text_width,
)


def _stack_panel(f: Fig, x, y, w, h) -> None:
    f.under(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="10" '
        f'fill="{PANEL}" stroke="{LINE}" stroke-width="1"/>'
    )
    f.mark(y + h)


def fig_01() -> None:
    f = Fig(960, "原始 Transformer 的编码器—解码器", "Post-Norm 的编码器解码器，交叉注意力从编码器取 K、V。")
    enc_x, dec_x, col_w = 36, 612, 300
    enc_cx, dec_cx = enc_x + col_w / 2, dec_x + col_w / 2

    f.text(enc_cx, 30, "编码器", size=18, weight=700, anchor="middle", color=BLUE)
    f.text(dec_cx, 30, "解码器", size=18, weight=700, anchor="middle", color=ORANGE)
    f.text(enc_cx, 50, "读入原文", size=12, anchor="middle", color=MUTED)
    f.text(dec_cx, 50, "右移一位的译文", size=12, anchor="middle", color=MUTED)

    def token_row(cx, y, labels, tones, emph):
        widths = [text_width(lb, 13) + 22 for lb in labels]
        total = sum(widths) + 8 * (len(labels) - 1)
        x = cx - total / 2
        for lb, tn, em, w in zip(labels, tones, emph, widths):
            f.chip(x, y, lb, tn, h=30, emphasize=em, min_w=w, size=13)
            x += w + 8

    token_row(enc_cx, 66, ["I", "love", "machine", "learning"], ["blue"] * 4, [False, False, False, False])
    token_row(dec_cx, 66, ["<bos>", "我", "喜欢", "机器"], ["orange", "neutral", "neutral", "neutral"], [True, False, False, False])

    def column(x, cx, y0, steps):
        y = y0
        boxes = {}
        splits = {}
        for kind, *rest in steps:
            if kind == "arrow":
                h = rest[0]
                f.arrow(cx, y, cx, y + h - 1, color=INK)
                y += h
            elif kind == "split":
                splits[rest[0]] = y
            elif kind == "box":
                name, h, title, sub, tn = rest
                f.card(x, y, col_w, h, title, sub, tn)
                boxes[name] = (x, y, col_w, h)
                y += h
        return boxes, splits, y

    enc_steps = [
        ("arrow", 16),
        ("box", "emb", 44, "输入嵌入", "Input Embedding", "teal"),
        ("arrow", 14),
        ("box", "pe", 38, "加上位置编码", "x + p", "purple"),
        ("split", "a"),
        ("arrow", 16),
        ("box", "mha", 48, "多头自注意力", "每个位置读取全文", "blue"),
        ("arrow", 14),
        ("box", "add1", 36, "Add & Norm", "先残差，再归一化", "purple"),
        ("split", "b"),
        ("arrow", 16),
        ("box", "ffn", 46, "逐位置前馈网络", "Position-wise FFN", "green"),
        ("arrow", 14),
        ("box", "add2", 36, "Add & Norm", "Post-Norm", "purple"),
    ]
    dec_steps = [
        ("arrow", 16),
        ("box", "emb", 44, "输出嵌入", "Output Embedding", "teal"),
        ("arrow", 14),
        ("box", "pe", 38, "加上位置编码", "x + p", "purple"),
        ("split", "a"),
        ("arrow", 16),
        ("box", "mmha", 50, "掩码多头自注意力", "只能读已生成的位置", "orange"),
        ("arrow", 14),
        ("box", "add0", 36, "Add & Norm", "Post-Norm", "purple"),
        ("split", "c"),
        ("arrow", 16),
        ("box", "cross", 56, "交叉注意力", "Q 来自解码器，K、V 来自编码器", "blue"),
        ("arrow", 14),
        ("box", "add1", 36, "Add & Norm", "Post-Norm", "purple"),
        ("split", "b"),
        ("arrow", 16),
        ("box", "ffn", 46, "逐位置前馈网络", "Position-wise FFN", "green"),
        ("arrow", 14),
        ("box", "add2", 36, "Add & Norm", "Post-Norm", "purple"),
        ("arrow", 16),
        ("box", "lin", 40, "线性层", "映射到词表", "gray"),
        ("arrow", 14),
        ("box", "sm", 40, "Softmax", "下一个 token 的概率", "orange"),
    ]
    enc_y0 = dec_y0 = 108
    eb, es, ey = column(enc_x, enc_cx, enc_y0, enc_steps)
    db, ds, dy = column(dec_x, dec_cx, dec_y0, dec_steps)

    def residual(cx, box, y_from, side):
        bx, by, bw, bh = box
        mid = by + bh / 2
        edge = bx if side < bx else bx + bw
        f.elbow([(cx, y_from), (side, y_from), (side, mid), (edge, mid)], color=GRAY, sw=1.25)

    residual(enc_cx, eb["add1"], es["a"], enc_x - 16)
    residual(enc_cx, eb["add2"], es["b"], enc_x - 16)
    residual(dec_cx, db["add0"], ds["a"], dec_x + col_w + 16)
    residual(dec_cx, db["add1"], ds["c"], dec_x + col_w + 16)
    residual(dec_cx, db["add2"], ds["b"], dec_x + col_w + 16)

    # Repeated block backdrop, drawn behind the sublayers.
    def backdrop(boxes, top_name, bot_name):
        x, y, w, _ = boxes[top_name]
        _, y2, _, h2 = boxes[bot_name]
        _stack_panel(f, x - 10, y - 8, w + 20, (y2 + h2) - y + 16)

    backdrop(eb, "mha", "add2")
    backdrop(db, "mmha", "add2")
    f.text(enc_x + 8, eb["add2"][1] + eb["add2"][3] + 16, "× N", size=14, weight=700, color=BLUE)
    f.text(dec_x + 8, db["add2"][1] + db["add2"][3] + 16, "× N", size=14, weight=700, color=ORANGE)

    # K, V from encoder output into cross-attention.
    _, e2y, e2w, e2h = eb["add2"]
    _, cy, _, ch = db["cross"]
    ex = enc_x + e2w
    ey_mid = e2y + e2h / 2
    cross_mid = cy + ch / 2
    bus = 500
    f.elbow([(ex, ey_mid), (bus, ey_mid), (bus, cross_mid), (dec_x, cross_mid)], color=BLUE, sw=1.6)
    f.text(bus + 8, (ey_mid + cross_mid) / 2, "K, V", size=13, weight=700, color=BLUE, baseline="middle")
    f.text(bus + 8, (ey_mid + cross_mid) / 2 + 16, "编码器输出", size=11, color=MUTED, baseline="middle")

    # Q label on the arrow entering cross from above.
    f.text(dec_cx + 18, db["cross"][1] - 8, "Q", size=12, weight=700, color=ORANGE, anchor="start")

    pred_y = dy + 14
    token_row(dec_cx, pred_y, ["我", "喜欢", "机器", "学习"], ["orange"] * 4, [False] * 4)
    f.text(dec_cx, pred_y + 46, "每个位置预测下一个 token", size=12, anchor="middle", color=MUTED)

    f.footnote(
        max(ey, pred_y) + 62,
        "灰底里的两级子层重复 N 次。原论文 N = 6，归一化放在残差之后，称为 Post-Norm。\n"
        "解码器输入比目标译文右移一位：第一个位置是起始符，注意力输出用来预测下一个 token。\n"
        "交叉注意力不沿译文做因果遮挡；因果遮挡发生在解码器的自注意力里。示意切分不是某个真实词表。",
    )
    f.save("01_original-transformer-architecture.svg")


def fig_24() -> None:
    f = Fig(960, "自注意力权重热图", "learning 作为 Query 时最关注 machine。")
    tokens = ["I", "love", "machine", "learning"]
    weights = [
        [0.55, 0.25, 0.10, 0.10],
        [0.20, 0.45, 0.15, 0.20],
        [0.05, 0.10, 0.25, 0.60],
        [0.05, 0.10, 0.55, 0.30],
    ]
    f.text(28, 32, "同一句话里的自注意力", size=16, weight=700)
    f.text(28, 54, "行是 Query，列是 Key。格子里是 softmax 之后的权重，不是点积原值。", size=13, color=MUTED)
    info = f.heatmap(28, 78, weights, tokens, tokens, cell=58, highlight_row=3)
    f.callout(
        520,
        150,
        400,
        [
            "橙色框：正在更新 learning 的表示",
            "这一行最关注 machine，权重 0.55",
            "0.05 + 0.10 + 0.55 + 0.30 = 1",
            "machine 那一行也反过来最关注 learning",
        ],
        "orange",
    )
    f.footnote(
        78 + info["h"] + 48,
        "数字是为了看清结构安排的示意权重，不是某个已训练模型的输出。这里没有遮住任何位置。\n"
        "交叉注意力的图也是这种矩阵，只是行来自解码器、列来自编码器，因此不必是方阵。",
    )
    f.save("24_self-attention-score-heatmap.svg")


def fig_02() -> None:
    f = Fig(960, "用 Query、Key、Value 做一次加权求和", "三个位置的权重 0.6、0.3、0.1 来自一次 softmax。")
    f.text(28, 30, "一次读取", size=16, weight=700)
    f.text(120, 30, "Query 与三个 Key 做缩放点积，softmax 后正好是 0.6、0.3、0.1", size=14, color=MUTED)

    cols = [230, 470, 710]
    headers = ["位置 1", "位置 2", "位置 3"]
    scores = ["0", "ln 1/2", "ln 1/6"]
    weights = [0.6, 0.3, 0.1]
    values = ["(2, 0)", "(0, 2)", "(2, 2)"]
    f.card(28, 118, 160, 58, "Query", "当前位置想找什么", "blue")
    for x, title, score, wgt, val in zip(cols, headers, scores, weights, values):
        f.text(x + 80, 62, title, anchor="middle", size=13, weight=700, color=MUTED)
        f.card(x, 78, 160, 46, "Key", "被匹配的描述", "teal")
        f.arrow(x + 80, 124, x + 80, 146, color=TEAL)
        f.text(x + 80, 204, score, anchor="middle", size=18, font="serif", style="italic", weight=700)
        f.rect(x, 232, 160, 14, fill="#F1EEE8", rx=3)
        f.rect(x, 232, 160 * wgt / 0.6, 14, fill=BLUE, rx=3)
        f.text(x + 80, 262, f"权重 {wgt:.1f}", anchor="middle", size=13, weight=700, color=BLUE)
        f.card(x, 282, 160, 46, "Value", val, "orange")
        f.elbow([(188, 147), (x + 80, 147), (x + 80, 186)], color=BLUE, sw=1.25)
    f.text(28, 232, "softmax", size=12, weight=700, color=MUTED, baseline="middle")

    f.region(28, 352, 904, 112)
    f.text(48, 364, "再对 Value 加权求和", size=14, weight=700)
    f.text(48, 396, "0.6×(2, 0) + 0.3×(0, 2) + 0.1×(2, 2) = (1.2, 0) + (0, 0.6) + (0.2, 0.2)", size=16, font="serif", style="italic")
    f.text(48, 428, "= (1.4, 0.8)", size=18, font="serif", style="italic", weight=700, color=ORANGE)
    f.text(230, 428, "这一位读到的上下文", size=14, color=MUTED)
    f.footnote(
        490,
        "分数整体加一个常数，softmax 不变，所以最大的缩放点积写成 0，另外两个正好是 ln(1/2) 和 ln(1/6)。\n"
        "Value 的坐标是为了把加权求和算完而设的示意，不是模型里的真实向量。点积已经除过 √d_k。",
    )
    f.save("02_self-attention-query-key-value.svg")


def fig_03() -> None:
    f = Fig(960, "缩放点积注意力里的矩阵形状", "从 X 投影出 Q、K、V，再得到 T×T 的权重。")
    f.text(28, 30, "同一个 X，三套投影", size=16, weight=700)
    f.card(28, 58, 86, 70, "X", "T × d", "gray")
    specs = [
        (180, "W_Q", "d × d_k", "Q", "T × d_k", "blue"),
        (180, "W_K", "d × d_k", "K", "T × d_k", "teal"),
        (180, "W_V", "d × d_v", "V", "T × d_v", "orange"),
    ]
    # three rows
    rows_y = [48, 132, 216]
    names = [("W_Q", "d × d_k", "Q", "T × d_k", "blue"), ("W_K", "d × d_k", "K", "T × d_k", "teal"), ("W_V", "d × d_v", "V", "T × d_v", "orange")]
    for y, (wn, ws, on, os, tn) in zip(rows_y, names):
        f.arrow(122, 93, 168, y + 26, color=INK)
        f.card(168, y, 100, 52, wn, ws, "gray")
        f.arrow(276, y + 26, 318, y + 26, color=INK)
        f.card(318, y, 100, 52, on, os, tn)
    f.text(28, 300, "块的大小只用来分清角色，维数以标注为准。同一头的每个位置共用同一套 W。", size=12, color=MUTED)

    f.text(500, 30, "然后做缩放点积", size=16, weight=700)
    flow = [
        (470, "Q Kᵀ", "T × T", "blue"),
        (600, "÷ √d_k", "压住点积尺度", "gray"),
        (730, "+ M", "掩码", "red"),
    ]
    for x, title, sub, tn in flow:
        f.card(x, 58, 112, 52, title, sub, tn)
    f.arrow(582, 84, 600, 84)
    f.arrow(712, 84, 730, 84)
    f.card(470, 132, 112, 52, "softmax", "对每一行", "gray")
    f.arrow(526, 110, 526, 132)
    f.card(610, 132, 112, 52, "× V", "T × d_v", "orange")
    f.arrow(582, 158, 610, 158)
    f.card(750, 132, 112, 52, "输出", "T × d_v", "blue")
    f.arrow(722, 158, 750, 158)

    weights = [
        [0.55, 0.25, 0.10, 0.10],
        [0.20, 0.45, 0.15, 0.20],
        [0.05, 0.10, 0.25, 0.60],
        [0.05, 0.10, 0.55, 0.30],
    ]
    tokens = ["I", "love", "machine", "learning"]
    f.text(28, 332, "softmax 之后的权重，每一行和为 1。列名是 Key。", size=13, weight=650)
    f.heatmap(28, 352, weights, tokens, tokens, cell=48, cbar=False)
    f.footnote(
        580,
        "QKᵀ 的第 t 行是位置 t 对所有位置的分数。M 在 softmax 之前加上：禁止读取的位置为 −∞，允许的位置为 0。\n"
        "热图与上一张自注意力图是同一组示意权重。多头会把这一步复制 h 份，再拼起来，见下一张图。",
    )
    f.save("03_scaled-dot-product-attention-matrices.svg")


def fig_04() -> None:
    f = Fig(960, "多头注意力与交叉注意力", "每个头独立投影，拼接后用 W_O 回到 d 维。")
    f.lead(28, 28, "a", "一个头就是一次缩放点积注意力")
    f.card(28, 52, 150, 64, "X", "T × d", "gray")
    f.arrow(186, 84, 214, 84)
    f.card(214, 52, 170, 64, "Q, K, V", "各有自己的 W", "blue")
    f.arrow(392, 84, 420, 84)
    f.card(420, 52, 200, 64, "Attention", "输出 T × d_v", "teal")

    f.lead(28, 156, "b", "h 个头并行，再投影回去")
    head_w = 150
    for i in range(4):
        x = 28 + i * (head_w + 12)
        f.card(x, 184, head_w, 58, f"头 {i+1}", "独立的 W_Q, W_K, W_V", "blue")
        f.arrow(x + head_w / 2, 242, x + head_w / 2, 268, color=BLUE)
    f.card(28, 268, 636, 48, "拼接", "T × (h · d_v)", "teal")
    f.arrow(680, 292, 712, 292)
    f.card(712, 268, 210, 48, "W_O", "回到 T × d", "green")
    f.text(28, 340, "常见等宽设计：d_k = d_v = d / h。原论文基础模型 d = 512，h = 8，所以每个头 64 维，前馈层宽 2048。", size=13, color=MUTED)

    f.lead(28, 384, "c", "交叉注意力：Q 与 K、V 来自不同序列")
    f.card(28, 412, 200, 70, "Q", "解码器，T × d_k", "orange")
    f.card(250, 412, 200, 70, "K, V", "编码器，S × d_k / d_v", "blue")
    f.arrow(228, 447, 250, 447)
    f.card(490, 412, 200, 70, "权重", "T × S", "teal")
    f.arrow(450, 447, 490, 447)
    f.card(720, 412, 200, 70, "输出", "T × d_v", "green")
    f.arrow(690, 447, 720, 447)
    f.footnote(
        508,
        "T 和 S 可以不同，所以交叉注意力的分数矩阵不一定是方阵。对源序列没有因果遮挡，每个译文位置都能读全部原文。\n"
        "各头的分工是训练出来的，图里不给它们指定句法角色。",
    )
    f.save("04_scaled-dot-product-and-multi-head-attention.svg")


def _spark(f: Fig, x, y, w, h, values, color) -> None:
    f.line(x, y + h / 2, x + w, y + h / 2, stroke=LINE, sw=1)
    pts = []
    n = len(values)
    for i, v in enumerate(values):
        pts.append((x + i * w / (n - 1), y + h / 2 - v * (h / 2 - 3)))
    f.poly(pts, stroke=color, sw=1.8)


def _pe(t: int, i: int, d: int = 16) -> float:
    j = i // 2
    div = 10000 ** ((2 * j) / d)
    ang = t / div
    return math.sin(ang) if i % 2 == 0 else math.cos(ang)


def fig_05() -> None:
    f = Fig(960, "位置编码与 RoPE", "没有位置时模型分不清词序；三种办法把位置送进注意力。")
    f.region(28, 24, 904, 92)
    f.chips(48, 42, ["人", "咬", "狗"], tone_name="orange", h=28)
    f.chips(230, 42, ["狗", "咬", "人"], tone_name="blue", h=28)
    f.text(430, 56, "字的集合相同，顺序不同", size=14, weight=650, baseline="middle")
    f.text(48, 92, "自注意力对 Q、K、V 的同一行置换是等变的：它能看见有哪些向量，看不见谁在前。位置信息要另外送进去。", size=13, color=MUTED)

    # (a) add
    f.region(28, 132, 300, 470)
    f.lead(44, 156, "a", "加到输入上")
    f.text(44, 182, "输入变成   x_t + p_t", size=14, font="serif", style="italic")
    cell = 6
    ox, oy = 48, 204
    d, npos = 16, 32
    for t in range(npos):
        for i in range(d):
            f.rect(ox + i * cell, oy + t * cell, cell - 0.6, cell - 0.6, fill=div_color(_pe(t, i, d)))
    f.text(ox, oy - 8, "维 0", size=10, color=MUTED)
    f.text(ox + d * cell, oy - 8, "维 15", size=10, color=MUTED, anchor="end")
    f.colorbar_div(ox + d * cell + 6, oy, npos * cell - 2)
    sparks = [
        (0, "维 0  高频", ORANGE),
        (4, "维 4  中频", TEAL),
        (14, "维 14  低频", BLUE),
    ]
    for k, (dim, name, col) in enumerate(sparks):
        sy = 412 + k * 48
        f.text(44, sy, name, size=11, weight=650, color=col)
        _spark(f, 120, sy - 10, 170, 28, [_pe(t, dim, d) for t in range(npos)], col)
    f.text(44, 558, "右侧几乎不动，是因为频率很低。", size=12, color=MUTED)
    f.text(44, 576, "也可换成可学习的位置表。", size=12, color=MUTED)

    # (b) bias
    f.region(340, 132, 290, 470)
    f.lead(356, 156, "b", "加到分数上")
    f.text(356, 182, "点积分数再加上", size=13, color=MUTED)
    f.text(356, 202, "b(t − s)", size=16, font="serif", style="italic")
    labels = [
        ["0", "−1", "−2", "−3"],
        ["+1", "0", "−1", "−2"],
        ["+2", "+1", "0", "−1"],
        ["+3", "+2", "+1", "0"],
    ]
    cell_b = 48
    bx, by = 378, 230
    for r in range(4):
        for c in range(4):
            delta = r - c
            f.rect(bx + c * cell_b, by + r * cell_b, cell_b - 4, cell_b - 4, fill=div_color(delta / 3), rx=4)
            f.text(bx + c * cell_b + (cell_b - 4) / 2, by + r * cell_b + (cell_b - 4) / 2, labels[r][c], anchor="middle", baseline="middle", size=13, weight=650)
    f.text(356, by + 4 * cell_b + 12, "格子里是 t−s。", size=12, color=MUTED)
    f.text(356, by + 4 * cell_b + 30, "同一对角线，相对距离相同。", size=12, color=MUTED)
    f.text(356, by + 4 * cell_b + 48, "b 通常是可学习的表。", size=12, color=MUTED)
    f.text(356, by + 4 * cell_b + 66, "它改分数，不改 Value。", size=12, color=MUTED)

    # (c) RoPE
    f.region(642, 132, 290, 470)
    f.lead(658, 156, "c", "旋转 Q 和 K")
    f.text(658, 184, "RoPE 不加一条 p_t。", size=12.5, color=MUTED)
    fast = [i * 58 for i in range(3)]
    slow = [i * 16 for i in range(3)]
    f.text(658, 214, "高频一对", size=12, weight=650, color=ORANGE)
    f.text(800, 214, "低频一对", size=12, weight=650, color=BLUE)
    for i, ang in enumerate(fast):
        _dial(f, 690, 268 + i * 62, 24, ang, ORANGE)
        f.text(722, 268 + i * 62, f"t={i}", size=11, baseline="middle", color=MUTED)
    for i, ang in enumerate(slow):
        _dial(f, 832, 268 + i * 62, 24, ang, BLUE)
        f.text(864, 268 + i * 62, f"t={i}", size=11, baseline="middle", color=MUTED)
    f.text(658, 462, "q 旋转角度 tθ", size=13, font="serif", style="italic")
    f.text(658, 482, "k 旋转角度 sθ", size=13, font="serif", style="italic")
    f.text(658, 504, "点积只留下 (s−t)θ", size=13, font="serif", style="italic")
    f.text(658, 528, "旋转的是 Q 和 K，不是 V。", size=12, color=MUTED)
    f.text(658, 558, "角度是示意，用来对比快慢。", size=12, color=MUTED)

    f.footnote(
        616,
        "正弦热图是 d = 16、位置 t = 0…31 的真实取值，颜色从 −1 到 1。它不需要训练，外推到更长序列的效果有限。\n"
        "RoPE 的常用频率是 θ_j = 10000^(−2j/d)。R(t)ᵀ R(s) = R(s−t)，所以相对位置直接进了点积。",
    )
    f.save("05_positional-encoding-and-rope.svg")


def _dial(f: Fig, cx, cy, r, deg, color) -> None:
    f.circle(cx, cy, r, fill=PAPER, stroke=LINE, sw=1)
    f.line(cx - r + 2, cy, cx + r - 2, cy, stroke=LINE, sw=0.8)
    f.line(cx, cy - r + 2, cx, cy + r - 2, stroke=LINE, sw=0.8)
    a = math.radians(deg)
    f.arrow(cx, cy, cx + (r - 5) * math.cos(a), cy - (r - 5) * math.sin(a), color=color, sw=1.5)


def fig_06() -> None:
    f = Fig(960, "Pre-Norm Transformer Block", "残差从 Norm 之前接出；右侧是 SwiGLU。")
    f.region(28, 24, 470, 560)
    f.lead(44, 48, "a", "一个 Block，形状始终是 T × d")

    cx, x, w = 250, 150, 210
    y = 78
    nodes = []

    def box(title, sub, tn, h=42):
        nonlocal y
        f.card(x, y, w, h, title, sub, tn)
        nodes.append((y, h))
        y += h

    def arr(h=16):
        nonlocal y
        f.arrow(cx, y, cx, y + h - 1)
        y += h

    def split_mark():
        return y

    f.text(cx, y + 8, "H⁽ℓ⁾", anchor="middle", size=16, font="serif", style="italic")
    y += 22
    s1 = split_mark()
    arr(18)
    box("Norm", "LayerNorm 或 RMSNorm", "purple", 40)
    arr(14)
    box("Multi-Head Attention", "位置之间交换信息", "blue", 48)
    arr(14)
    add1 = y
    f.plus(cx, y + 16)
    f.text(cx + 28, y + 16, "得到 U", baseline="middle", size=13, weight=650)
    y += 36
    s2 = y
    arr(18)
    box("Norm", "另一组参数", "purple", 40)
    arr(14)
    box("FFN", "每个位置自己的 MLP", "green", 48)
    arr(14)
    f.plus(cx, y + 16)
    f.text(cx + 28, y + 16, "H⁽ℓ⁺¹⁾", baseline="middle", size=14, font="serif", style="italic")
    y += 40

    # Residuals leave BEFORE the norm.
    f.elbow([(cx, s1), (96, s1), (96, add1 + 16), (cx - 9, add1 + 16)], color=GRAY, sw=1.3)
    f.elbow([(cx, s2), (118, s2), (118, y - 24), (cx - 9, y - 24)], color=GRAY, sw=1.3)
    f.text(46, (s1 + add1) / 2 - 8, "残差从", size=11, color=MUTED)
    f.text(46, (s1 + add1) / 2 + 8, "Norm 前接出", size=11, color=MUTED)

    f.region(514, 24, 418, 300)
    f.lead(530, 48, "b", "SwiGLU：一门一特征")
    f.card(530, 118, 78, 40, "x", "d", "gray")
    f.elbow([(608, 130), (640, 130), (640, 86), (668, 86)], color=GOLD, sw=1.3)
    f.elbow([(608, 146), (668, 168)], color=GREEN, sw=1.3)
    f.card(668, 66, 120, 40, "x W_g", "门控支路", "gold")
    f.card(668, 148, 120, 40, "x W_u", "特征支路", "green")
    f.arrow(788, 86, 820, 86, color=GOLD)
    f.card(820, 66, 90, 40, "SiLU", "开关", "gold")
    f.arrow(788, 168, 850, 200, color=GREEN)
    f.arrow(865, 106, 865, 188, color=GOLD)
    f.card(812, 188, 106, 40, "逐元素 ⊙", "相乘", "orange")
    f.arrow(865, 228, 865, 252, color=ORANGE)
    f.card(760, 252, 160, 36, "再乘 W_d 回到 d", None, "green")
    f.text(530, 302, "只有门控支路经过 SiLU。", size=12, color=MUTED)

    f.region(514, 340, 418, 244)
    f.lead(530, 364, "c", "Norm 放在哪里")
    f.text(530, 396, "Pre-Norm，本图，也是现代常见写法", size=13, weight=650)
    f.text(530, 418, "先 Norm，再子层；残差绕过这两步。", size=13, color=MUTED)
    f.text(530, 450, "Post-Norm，原论文", size=13, weight=650)
    f.text(530, 472, "先子层，残差相加，然后再 Norm。", size=13, color=MUTED)
    f.text(530, 508, "原始 FFN 是线性 → ReLU → 线性。", size=13, color=MUTED)
    f.text(530, 530, "GELU、SwiGLU 是后来的选择。", size=13, color=MUTED)
    f.footnote(
        600,
        "两次 Norm 各有自己的可学习参数。残差把子层改成“在原表示上加一个增量”，形状保持 T × d，层才能直接叠上去。",
    )
    f.save("06_transformer-block-residual-norm.svg")


def _mask_icon(f: Fig, x, y, kind: str, n=5, cell=11) -> None:
    for r in range(n):
        for c in range(n):
            if kind == "full":
                on = True
            elif kind == "causal":
                on = c <= r
            else:
                on = False
            f.rect(x + c * cell, y + r * cell, cell - 1.5, cell - 1.5, fill=BLUE if on else "#E7E4DE", rx=1)


def fig_07() -> None:
    f = Fig(960, "三种 Transformer 用法", "差别在于谁可以读谁，以及有没有交叉注意力。")
    cols = [
        (28, "Encoder-only", "双向自注意力", "blue", "BERT、ViT", "分类、检索表示、图像识别", "full"),
        (344, "Encoder–decoder", "编码双向，解码因果 + 交叉", "teal", "原始 Transformer、T5", "翻译、摘要", "both"),
        (660, "Decoder-only", "一条序列上的因果自注意力", "orange", "GPT，以及多数大语言模型", "把提示和回答放在一起，预测下一个 token", "causal"),
    ]
    for x, title, mech, tn, examples, tasks, kind in cols:
        f.region(x, 24, 300, 430)
        f.rect(x, 24, 300, 8, fill=tone_of(tn), rx=0)
        f.text(x + 18, 52, title, size=16, weight=700)
        f.text(x + 18, 76, mech, size=13, color=MUTED)
        if kind == "both":
            f.text(x + 18, 112, "编码器", size=12, weight=650, color=BLUE)
            _mask_icon(f, x + 18, 128, "full")
            f.text(x + 110, 112, "解码器自注意力", size=12, weight=650, color=ORANGE)
            _mask_icon(f, x + 110, 128, "causal")
            f.text(x + 18, 196, "交叉注意力是 T × S，源侧不遮挡。", size=12, color=MUTED)
        else:
            f.text(x + 18, 112, "允许读取的位置", size=12, weight=650)
            _mask_icon(f, x + 18, 130, kind)
            cap = "全部有效位置" if kind == "full" else "自己和过去"
            f.text(x + 90, 150, cap, size=12, color=MUTED, baseline="middle")
        f.text(x + 18, 250, "例子", size=12, weight=700, color=FAINT)
        f.text(x + 18, 274, examples, size=14, weight=650)
        f.text(x + 18, 312, "适合", size=12, weight=700, color=FAINT)
        # wrap tasks
        yy = 336
        for line in _wrap_manual(tasks, 260, 14):
            f.text(x + 18, yy, line, size=14)
            yy += 22
        if kind == "causal":
            f.chips(x + 18, 400, ["提示", "已生成"], tones=["blue", "orange"], h=26, size=12)
    f.footnote(
        470,
        "深色格子是可以读取的位置。Encoder-only 让整段输入互相看见；Decoder-only 把任务说明和正在生成的内容放进同一条因果序列。\n"
        "三种结构最后都接一个任务输出层：类别、数值，或词表上的 softmax。",
    )
    f.save("07_transformer-architectures-encoder-decoder.svg")


def tone_of(name: str) -> str:
    return {"blue": BLUE, "teal": TEAL, "orange": ORANGE}[name]


def _wrap_manual(text: str, width: float, size: float) -> list[str]:
    from lib import wrap_text

    return wrap_text(text, width, size)


def fig_08() -> None:
    f = Fig(960, "自回归生成", "每选出一个 token，就把它接回上下文，直到结束符。")
    frames = [
        (["<bos>"], "我"),
        (["<bos>", "我"], "喜欢"),
        (["<bos>", "我", "喜欢"], "机器"),
        (["…", "机器", "学习"], "</eos>"),
    ]
    fw, gap = 216, 14
    for i, (ctx, nxt) in enumerate(frames):
        x = 28 + i * (fw + gap)
        f.region(x, 28, fw, 250)
        f.text(x + 16, 52, f"第 {i+1} 步", size=13, weight=700, color=ORANGE)
        f.text(x + 16, 78, "已有上下文", size=12, color=MUTED)
        cx = x + 16
        cy = 96
        for tok in ctx:
            tw = text_width(tok, 12) + 18
            if cx + tw > x + fw - 12:
                cx = x + 16
                cy += 34
            emph = tok == "<bos>"
            f.chip(cx, cy, tok, "orange" if emph else "neutral", h=26, size=12, emphasize=emph, min_w=tw)
            cx += tw + 6
        f.arrow(x + fw / 2, cy + 40, x + fw / 2, cy + 62, color=ORANGE)
        f.text(x + 16, cy + 84, "选出", size=12, color=MUTED)
        stop = nxt == "</eos>"
        f.chip(x + 16, cy + 96, nxt, "red" if stop else "orange", h=30, emphasize=True, size=14)
        if stop:
            f.text(x + 78, cy + 111, "停止", size=13, weight=650, color=RED, baseline="middle")
    f.text(28, 310, "上下文只变长，不改已经选过的 token。结束符或长度上限都会让生成停下来。", size=14, color=INK)
    f.footnote(
        342,
        "图里不画每一步的概率，避免把示意分布误当成模型输出。温度、top-k 和 top-p 决定“怎样从分布里选”，见后文。\n"
        "训练时可以用右移一位的整句同时算所有位置的损失；真正生成时必须等新 token 接回去，才能算下一步。",
    )
    f.save("08_autoregressive-generation.svg")


def fig_09() -> None:
    f = Fig(960, "并行计算与 KV cache", "训练和 prefill 一次处理整段；decode 只为新 token 计算，并复用历史 K、V。")
    f.region(28, 24, 440, 300)
    f.lead(44, 48, "a", "训练 / prefill：整段一起算")
    labels = ["<bos>", "我", "喜欢", "机器", "学习"]
    f.chips(44, 78, labels, tone_name="blue", h=28, size=12)
    f.text(44, 128, "每个位置同时得到自己的 Q、K、V。", size=13)
    _mask_icon(f, 44, 156, "causal", n=5, cell=14)
    f.text(130, 186, "因果掩码仍然生效", size=13, color=MUTED, baseline="middle")
    f.text(44, 246, "训练时，各位置的下一 token 损失一起算。", size=13)
    f.text(44, 270, "prefill 一次读完提示，决定首字延迟 TTFT。", size=13)
    f.text(44, 294, "这一步的计算可以铺满 GPU。", size=13, color=MUTED)

    f.region(484, 24, 448, 300)
    f.lead(500, 48, "b", "decode：只算新位置")
    f.chips(500, 78, ["<bos>", "我", "喜欢", "机器"], tone_name="gray", h=28, size=12)
    f.chips(500, 116, ["学习"], tone_name="orange", h=28, emphasize=[True], size=12)
    f.text(560, 130, "新 token", size=12, color=ORANGE, baseline="middle")
    f.text(500, 168, "历史位置的 K、V 留在缓存里，直接拼接。", size=13)
    f.text(500, 192, "这一步只算新的 q、k、v，再把 k、v 追加进去。", size=13)
    f.text(500, 216, "新的 q 读取缓存中的全部 K、V。", size=13)
    f.text(500, 250, "每步耗时是 TPOT。", size=13, weight=650)
    f.text(500, 274, "省掉的是重算，省不掉把缓存从显存读出来。", size=13, color=MUTED)

    f.region(28, 340, 904, 150)
    f.lead(44, 364, "c", "这条序列的 KV 缓存有多大")
    factors = [("2", "K 和 V"), ("B=1", "序列数"), ("L=32", "层数"), ("T=8192", "长度"), ("H_kv=8", "KV 头"), ("d=128", "每头维数"), ("2 字节", "每个元素")]
    x = 44
    for i, (a, b) in enumerate(factors):
        f.card(x, 386, 108, 52, a, b, "teal" if i == 0 else "gray", title_size=14, sub_size=11)
        x += 108
        if i < len(factors) - 1:
            f.text(x + 2, 412, "×", size=16, weight=700, baseline="middle")
            x += 18
    f.text(44, 462, "2 × 1 × 32 × 8192 × 8 × 128 × 2  =  1,073,741,824 字节  =  1 GiB", size=15, font="serif", style="italic")
    f.footnote(
        508,
        "公式假设每层的 KV 头数和每头维数相同，并且只统计这些 KV 张量，不含权重和其他激活。上下文或并发序列一变长，缓存就按比例变大。",
    )
    f.save("09_parallel-processing-and-kv-cache.svg")


def fig_25() -> None:
    f = Fig(960, "合批、吞吐与延迟", "权重复用提高吞吐；批次变大后延迟上升，吞吐会碰到上限。")
    f.region(28, 24, 430, 360)
    f.lead(44, 48, "a", "一次读出权重，服务多个序列")
    f.card(44, 78, 160, 64, "模型权重", "从显存读一遍", "gray")
    f.arrow(204, 100, 248, 100)
    f.elbow([(204, 120), (232, 120), (232, 176), (250, 176)], color=INK, sw=1.4)
    f.text(250, 86, "批次 1", size=12, weight=700, color=MUTED)
    f.chip(250, 98, "序列 A", "orange", h=26, size=12)
    f.text(250, 150, "批次 B", size=12, weight=700, color=MUTED)
    for i, name in enumerate(["序列 A", "序列 B", "序列 C", "序列 D"]):
        f.chip(250 + (i % 2) * 86, 164 + (i // 2) * 34, name, "blue", h=26, size=12)
    f.text(44, 268, "权重的这次读取摊到 B 个序列上。", size=13.5)
    f.text(44, 292, "每个序列自己的 KV cache 仍要分别读。", size=13.5)
    f.text(44, 316, "省下的是权重搬运，不是全部显存流量。", size=13.5, color=MUTED)
    f.text(44, 348, "单序列时，算力常常在等数据。", size=13.5, color=MUTED)

    f.plot_curve(
        478,
        24,
        220,
        250,
        [(0.02, 0.08), (0.14, 0.30), (0.26, 0.52), (0.40, 0.72), (0.55, 0.86), (0.70, 0.91), (0.84, 0.92), (0.96, 0.92)],
        BLUE,
        "批次大小",
        "吞吐",
    )
    f.plot_dot(0.22, 0.45, "Fast", ORANGE, dx=6, dy=14)
    f.plot_dot(0.78, 0.915, "标准", BLUE, dx=-34, dy=16)
    f.plot_curve(
        710,
        24,
        220,
        250,
        [(0.04, 0.16), (0.2, 0.26), (0.36, 0.4), (0.52, 0.56), (0.7, 0.74), (0.88, 0.92)],
        RED,
        "批次大小",
        "P95 延迟",
    )
    f.plot_dot(0.24, 0.30, "Fast", ORANGE, dx=6, dy=-8)
    f.plot_dot(0.72, 0.76, "标准", RED, dx=-36, dy=-12)
    f.text(478, 300, "两条曲线都是定性形状，不是测量数据，坐标也没有真实刻度。", size=12.5, color=MUTED)
    f.text(478, 324, "吞吐先升后平：算力或带宽打满之后，再加大批次不再提高吞吐。", size=13)
    f.text(478, 348, "延迟随批次上升，因为要等凑批，单步计算也更久。", size=13)
    f.footnote(
        400,
        "标准档把批次做大，单位 token 的成本低。Fast 档主动限制批次、减少排队，延迟更好，同样的权重搬运被更少的 token 分摊，所以单价更高。\n"
        "P95 指较慢的那部分请求。图上的点只标出两种经营方式落在曲线的哪一侧。",
    )
    f.save("25_batching-throughput-latency.svg")


def fig_28() -> None:
    f = Fig(960, "因果掩码", "未来位置在 softmax 之前就是 −∞，权重变成 0。")
    tokens = ["我", "喜欢", "机器", "学习"]
    raw = [
        [1.2, None, None, None],
        [0.4, 1.1, None, None],
        [0.2, 0.8, 1.0, None],
        [0.1, 0.3, 1.2, 0.6],
    ]
    probs = []
    for row in raw:
        finite = [v for v in row if v is not None]
        p = softmax(finite)
        full = []
        k = 0
        for v in row:
            if v is None:
                full.append(0.0)
            else:
                full.append(p[k])
                k += 1
        probs.append(_to_cents(full))

    f.text(28, 30, "softmax 之前：允许的位置加 0，未来的位置加 −∞", size=15, weight=700)
    f.text(520, 30, "softmax 之后：未来权重是 0，每一行和为 1", size=15, weight=700)

    def draw(x, matrix, future_label):
        cell = 62
        lab = 64
        for c, tok in enumerate(tokens):
            f.text(x + lab + c * cell + cell / 2, 58, tok, anchor="middle", size=13, weight=650)
        f.text(x + lab + 2 * cell, 78, "Key", anchor="middle", size=11, color=MUTED)
        for r, tok in enumerate(tokens):
            f.text(x + lab - 10, 100 + r * cell + cell / 2, tok, anchor="end", baseline="middle", size=13, weight=650)
            for c in range(4):
                v = matrix[r][c]
                blocked = raw[r][c] is None and future_label
                if blocked:
                    fill = "#F8E8E6"
                    label = "−∞"
                    tc = RED
                elif future_label:
                    fill = "#F7F6F3"
                    label = f"{v:.1f}"
                    tc = INK
                else:
                    fill = seq_color(v)
                    label = f"{v:.2f}"
                    tc = ink_of(fill)
                f.rect(x + lab + c * cell + 3, 100 + r * cell + 3, cell - 6, cell - 6, fill=fill, stroke=LINE, sw=1, rx=4)
                f.text(x + lab + c * cell + cell / 2, 100 + r * cell + cell / 2, label, anchor="middle", baseline="middle", size=13, weight=650, color=tc)
        f.text(x + 8, 100 + 2 * cell, "Query", size=11, color=MUTED, anchor="middle")

    draw(20, [[v if v is not None else None for v in row] for row in raw], True)
    draw(500, probs, False)
    # Highlight the row that predicts 学习: index 2 "机器"
    f.rect(20 + 64, 100 + 2 * 62, 4 * 62, 62, fill="none", stroke=ORANGE, sw=1.8, rx=4)
    f.rect(500 + 64, 100 + 2 * 62, 4 * 62, 62, fill="none", stroke=ORANGE, sw=1.8, rx=4)
    f.callout(28, 370, 900, ["橙色这一行是“机器”。它只能看见“我、喜欢、机器”，输出用来预测下一个 token“学习”。"], "orange")
    f.footnote(
        430,
        "左侧未来格是 −∞，不是一个很小的负数凑出来的。softmax(−∞) = 0。对角线保留，当前位置可以读自己。\n"
        "补齐用的 padding 也在进 softmax 之前写成 −∞。训练时各行仍然可以并行，只是每行看不见自己的未来。",
    )
    f.save("28_causal-mask.svg")


def ink_of(fill: str) -> str:
    from lib import ink_on

    return ink_on(fill)


def fig_29() -> None:
    f = Fig(960, "MHA、GQA 与 MQA", "Query 头可以很多；减少的是 KV 头，缓存随 KV 头数下降。")
    plans = [
        (28, "MHA", "每个 Query 头一对 K、V", [0, 1, 2, 3], "4 份 KV"),
        (344, "GQA", "一组 Query 共享一对 K、V", [0, 0, 1, 1], "2 份 KV"),
        (660, "MQA", "所有 Query 头共享一对 K、V", [0, 0, 0, 0], "1 份 KV"),
    ]
    for x, title, sub, groups, cache in plans:
        f.region(x, 24, 300, 340)
        f.text(x + 16, 50, title, size=16, weight=700)
        f.text(x + 16, 72, sub, size=12.5, color=MUTED)
        qy = [110, 160, 210, 260]
        n_kv = len(set(groups))
        kvy = []
        top, bot = 110, 260
        if n_kv == 1:
            kvy = [185]
        elif n_kv == 2:
            kvy = [135, 235]
        else:
            kvy = qy
        colors = [BLUE, TEAL, ORANGE, PURPLE]
        for i, gy in enumerate(qy):
            f.circle(x + 70, gy, 14, fill=BLUE, fo=0.18, stroke=BLUE, sw=1.4)
            f.text(x + 70, gy, f"Q{i+1}", anchor="middle", baseline="middle", size=11, weight=700, color=BLUE)
            dest = kvy[groups[i]]
            f.line(x + 84, gy, x + 176, dest, stroke=colors[groups[i]], sw=1.4)
        for j, gy in enumerate(kvy):
            f.card(x + 176, gy - 16, 100, 32, f"K{j+1} V{j+1}", None, "teal", title_size=13)
        f.text(x + 16, 318, f"缓存 ∝   {cache}", size=14, weight=700)
        f.text(x + 16, 342, "图中画 4 个 Query 头", size=12, color=MUTED)
    f.footnote(
        390,
        "生成时每个新 token 仍要读出对应的历史 KV。GQA / MQA 缩小的是每一层缓存的头数 H_kv，不改变“历史要读出来”这件事。\n"
        "Query 头保持较多，不同头仍可以有自己的查询；共享的是被读取的 Key 和 Value。",
    )
    f.save("29_mha-gqa-mqa.svg")


def _to_cents(ps: list[float]) -> list[float]:
    """Round a probability row to two decimals that still sum to 1."""
    units = [int(math.floor(p * 100 + 1e-8)) for p in ps]
    left = 100 - sum(units)
    order = sorted(range(len(ps)), key=lambda i: p_frac(ps[i], units[i]), reverse=True)
    for i in range(max(0, left)):
        units[order[i % len(ps)]] += 1
    return [u / 100 for u in units]


def p_frac(p: float, unit: int) -> float:
    return p * 100 - unit


def fig_30() -> None:
    f = Fig(960, "FlashAttention 与显存墙", "标准注意力把 T×T 矩阵写入显存；分块算法把中间结果留在片上。")
    f.region(28, 24, 448, 390)
    f.lead(44, 48, "a", "标准实现")
    f.card(44, 72, 170, 52, "HBM 里的 Q K V", "容量大，带宽紧", "gray")
    f.arrow(129, 124, 129, 148, color=GOLD)
    f.card(44, 148, 170, 48, "SRAM 算一小块", "很快，但很小", "gold")
    f.arrow(214, 172, 250, 172, color=RED)
    f.card(250, 146, 190, 56, "整张 T × T", "写进 HBM 再读回", "red")
    f.text(250, 224, "中间矩阵落在慢速显存里。", size=13, color=MUTED)
    f.text(44, 330, "序列一长，搬运 T×T 矩阵的时间", size=14)
    f.text(44, 354, "会盖过矩阵乘法本身。", size=14)
    f.text(44, 384, "算力在等数据。这就是 memory wall。", size=14, color=RED)

    f.region(492, 24, 440, 390)
    f.lead(508, 48, "b", "FlashAttention")
    f.card(508, 78, 180, 70, "HBM 里只留", "Q、K、V 和输出 O", "gray")
    f.card(508, 170, 180, 78, "SRAM 里的一块", "这一块的 softmax 与累加", "gold")
    f.arrow(598, 148, 598, 170, color=GOLD)
    f.text(708, 100, "按块读入", size=13, color=MUTED)
    f.text(708, 196, "不把整张", size=13, color=MUTED)
    f.text(708, 214, "T×T 写回去", size=13, color=MUTED)
    f.text(508, 276, "反向传播时中间分数没有保存，", size=14)
    f.text(508, 300, "就再算一遍注意力。", size=14)
    f.text(508, 336, "多算的那一点，远少于少搬一次大矩阵。", size=14, weight=650)
    f.text(508, 368, "结果与标准注意力相同。", size=14, color=GREEN)
    f.footnote(
        432,
        "相同是指算法本身是精确的，差别只在浮点误差。它没有改变 Q、K、V 和 softmax 的定义，改变的是计算和存储的顺序。\n"
        "HBM 是显卡上的大显存，SRAM 是靠计算单元更近的小缓存。图里的方块表示存放位置，不是某一张真实的地址布局。",
    )
    f.save("30_flashattention-tiling.svg")


def build() -> None:
    fig_01()
    fig_24()
    fig_02()
    fig_03()
    fig_04()
    fig_05()
    fig_06()
    fig_07()
    fig_08()
    fig_09()
    fig_25()
    fig_28()
    fig_29()
    fig_30()
