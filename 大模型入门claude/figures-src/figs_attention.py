"""第 7.1–7.2 节：注意力热图、Q/K/V 一次读取、矩阵形状。"""
from svgkit import *


# ---------------------------------------------------------------------------
# 24 自注意力热图
# ---------------------------------------------------------------------------
def fig24():
    words = ["I", "love", "machine", "learning"]
    W = [[0.55, 0.25, 0.10, 0.10],
         [0.30, 0.35, 0.15, 0.20],
         [0.05, 0.15, 0.40, 0.40],
         [0.05, 0.15, 0.60, 0.20]]
    for r in W:
        assert abs(sum(r) - 1) < 1e-9
    s = SVG(960, 456, "自注意力权重热图", "每一行是一个词作为 Query 时分配给各个词的权重，行和为 1。")

    # ---- 左：热图 ----
    cell = 66
    x0, y0 = 170, 112
    s.text(x0 + 2 * cell, 34, "注意力权重矩阵（每行和为 1）", size=16, weight="bold")
    s.text(x0 + 2 * cell, 70, "被读取的位置（Key）", size=13.5, color=main("k"))
    for j, w in enumerate(words):
        s.text(x0 + j * cell + cell / 2, y0 - 16, w, size=14, color=INK)
    s.raw(f'<g transform="rotate(-90 52 {y0 + 2 * cell})">')
    s.text(52, y0 + 2 * cell, "读取者（Query）", size=13.5, color=main("q"))
    s.raw("</g>")
    for i, w in enumerate(words):
        s.text(x0 - 12, y0 + i * cell + cell / 2, w, size=14, anchor="end",
               weight="bold" if i == 3 else "normal")
    s.grid(x0, y0, 4, 4, cell, fills=lambda i, j: heat(W[i][j] / 0.62),
           values=lambda i, j: f"{W[i][j]:.2f}", vsize=15,
           vcolor=lambda i, j: WHITE if W[i][j] > 0.38 else INK, stroke=WHITE, sw=2)
    # 高亮 learning 行
    s.rect(x0 - 3, y0 + 3 * cell - 3, 4 * cell + 6, cell + 6, fill="none", stroke=main("q"), sw=3, rx=6)
    s.text(x0 + 2 * cell, y0 + 4 * cell + 26, "↑ 看这一行：learning 主要从 machine 读取信息", size=13.5, color=main("q"))

    # ---- 右：同一行画成连线 ----
    px = 520
    s.panel(px, 52, 420, 350)
    s.text(px + 210, 76, "把 learning 这一行画出来", size=15, weight="bold")
    xs = [px + 62, px + 158, px + 262, px + 362]
    yb = 296
    top = (px + 210, 128)
    weights = W[3]
    s.pill(top[0], top[1], "learning（作为 Query）", key="q", size=14, pad=12)
    for j, (w, x) in enumerate(zip(words, xs)):
        wv = weights[j]
        s.line(top[0], top[1] + 16, x, yb - 17, color=main("attn"), sw=1 + 18 * wv, opacity=0.5, cap="butt")
    for j, (w, x) in enumerate(zip(words, xs)):
        wv = weights[j]
        lx, ly = top[0] + (x - top[0]) * 0.7, top[1] + 16 + (yb - 17 - top[1] - 16) * 0.7
        s.rect(lx - 21, ly - 11, 42, 22, fill=WHITE, stroke=main("attn"), sw=1, rx=11)
        s.text(lx, ly, f"{wv:.2f}", size=13.5, color=main("attn"), weight="bold")
        s.pill(x, yb, w, key="k", size=14, pad=10)
    s.text(px + 210, yb + 30, "被读取的 Key / Value（包括它自己）", size=12.5, color=main("k"))
    s.text(px + 210, 100, "线越粗 = 权重越大", size=12.5, color=MUTED)
    s.text(px + 210, yb + 70,
           "新的 learning ≈ 0.05·$v$_{I} + 0.15·$v$_{love} + 0.60·$v$_{machine} + 0.20·$v$_{learning}",
           size=13.5, color=INK)
    s.text(480, 440, "注：权重为教学示例，用来说明读法；真实模型每层、每个头的权重都不同。", size=12, color=MUTED)
    s.save(OUT / "24_self-attention-score-heatmap.svg")


# ---------------------------------------------------------------------------
# 02 一次注意力读取：匹配 → 归一化 → 加权求和
# ---------------------------------------------------------------------------
def fig02():
    scores = [2.1, 1.4, 0.3]
    w = softmax(scores)
    assert [round(x, 2) for x in w] == [0.60, 0.30, 0.10], w
    w = [0.6, 0.3, 0.1]
    vals = [(1, 0), (0, 1), (1, 1)]
    o = (sum(wi * v[0] for wi, v in zip(w, vals)), sum(wi * v[1] for wi, v in zip(w, vals)))
    s = SVG(1000, 556, "一次注意力读取", "Query 与各 Key 打分，softmax 变成权重，再对 Value 加权求和。")

    # 顶部类比条
    s.rect(30, 18, 940, 50, fill=PANEL, stroke=BORDER, rx=10)
    s.text(52, 43, "类比：在图书馆找资料", size=14, anchor="start", weight="bold")
    s.pill(300, 43, "Query：我想找什么", key="q", size=13.5)
    s.pill(520, 43, "Key：每本书的标签", key="k", size=13.5)
    s.pill(752, 43, "Value：书里真正的内容", key="v", size=13.5)

    # 列标题
    cols = [(95, "被读取的位置"), (270, "① 匹配打分"), (445, "② softmax 归一化"), (650, "③ 按权重取 Value")]
    for x, t in cols:
        s.text(x, 104, t, size=14.5, weight="bold")
    s.text(270, 125, "$q$_{t}·$k$_{s} / √$d$_{k}", size=13.5, color=MUTED)
    s.text(445, 125, "权重之和 = 1", size=13, color=MUTED)
    s.text(650, 125, "$α$_{ts} × $v$_{s}", size=13.5, color=MUTED)

    # Query：底部一个框，经竖直"总线"送到每个打分圆
    s.box(150, 452, 170, 44, "$q$_{t}：当前位置的 Query", key="q", size=14, weight="normal")
    bus = 214
    ys = [175, 265, 355]
    s.line(bus, ys[0] + 12, bus, 452, color=main("q"), sw=1.8)
    for i, y in enumerate(ys):
        s.text(30, y, f"位置 {i + 1}", size=13.5, anchor="start", color=MUTED)
        s.box(88, y - 33, 52, 28, f"$k$_{{{i + 1}}}", key="k", size=14, weight="normal")
        s.box(88, y + 5, 52, 28, f"$v$_{{{i + 1}}}", key="v", size=14, weight="normal")
        # 打分：k 从左上进入，q 从总线进入
        s.arrow([(144, y - 19), (250, y - 13)], color=main("k"), sw=1.5)
        s.arrow([(bus, y + 12), (247, y + 10)], color=main("q"), sw=1.5)
        s.circle(272, y, 24, fill=WHITE, stroke=main("attn"), sw=1.6)
        s.text(272, y, f"{scores[i]:.1f}", size=16, weight="bold", color=main("attn"))
        s.harrow(298, 362, y, color=LINE)
        # 权重条
        bw = 150 * w[i]
        s.rect(372, y - 14, 150, 28, fill=PANEL, stroke=BORDER, rx=5)
        s.rect(372, y - 14, bw, 28, fill=main("attn"), rx=5, opacity=0.85)
        s.text(372 + bw + 8 if w[i] < 0.5 else 372 + bw - 8, y, f"{w[i]:.1f}", size=15, weight="bold",
               color=INK if w[i] < 0.5 else WHITE, anchor="start" if w[i] < 0.5 else "end")
        s.harrow(530, 572, y, color=LINE)
        # 加权 value
        s.text(590, y, f"{w[i]:.1f} ×", size=15, anchor="start")
        s.grid(632, y - 14, 1, 2, 30, fills=lambda a, b: light("v"), values=[[vals[i][0], vals[i][1]]], vsize=14,
               stroke=main("v"), sw=1)
        s.text(704, y, "=", size=16)
        sc = (w[i] * vals[i][0], w[i] * vals[i][1])
        s.grid(718, y - 14, 1, 2, 34, fills=lambda a, b: light("v"),
               values=[[f"{sc[0]:.1f}", f"{sc[1]:.1f}"]], vsize=14, stroke=main("v"), sw=1)
        # v 的内容沿下方细线送到第③列
        s.arrow([(144, y + 19), (160, y + 19), (160, y + 38), (628, y + 38), (645, y + 17)], color=main("v"),
                sw=1.1, opacity=0.5, head=0.8)

    # 求和
    s.path("M795,161 L805,161 L805,369 L795,369", stroke=INK, sw=1.3)
    s.harrow(808, 840, 265, color=INK)
    s.text(822, 234, "④ 求和", size=14.5, weight="bold", anchor="start")
    s.grid(848, 251, 1, 2, 44, fills=lambda a, b: light("attn"), values=[[f"{o[0]:.1f}", f"{o[1]:.1f}"]],
           vsize=15, stroke=main("attn"), sw=1.2)
    s.text(892, 312, "输出 $o$_{t}", size=14.5, weight="bold", color=main("attn"))

    # 右下几何小图：输出落在 Value 围成的区域内
    gx, gy, gs = 850, 528, 88
    s.line(gx - 8, gy, gx + gs + 24, gy, color=BORDER, sw=1)
    s.line(gx, gy + 8, gx, gy - gs - 20, color=BORDER, sw=1)
    pts = [(gx + v[0] * gs, gy - v[1] * gs) for v in vals]
    s.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z", stroke=main("v"), sw=1, fill=light("v"))
    offs = [(0, 15), (-16, -2), (16, -2)]
    for i, (x, y) in enumerate(pts):
        s.circle(x, y, 4.5, fill=main("v"))
        s.text(x + offs[i][0], y + offs[i][1], f"$v$_{{{i + 1}}}", size=13, color=main("v"))
    ox, oy = gx + o[0] * gs, gy - o[1] * gs
    s.circle(ox, oy, 5.5, fill=main("attn"))
    s.text(ox - 10, oy - 2, "$o$_{t}", size=13.5, color=main("attn"), anchor="end", weight="bold")
    s.lines(818, 440, ["几何直觉：权重非负、和为 1，", "所以输出 $o$_{t} 是各 Value 的", "加权平均，落在它们围成的区域内。"],
            size=12.5, color=MUTED, anchor="end")
    s.save(OUT / "02_self-attention-query-key-value.svg")


# ---------------------------------------------------------------------------
# 03 缩放点积注意力：矩阵形状
# ---------------------------------------------------------------------------
def fig03():
    T, dk, dv = 4, 3, 3
    c = 26
    t_hi, s_hi = 2, 1  # 高亮第 3 行、第 2 列（0 基）
    s = SVG(1060, 400, "缩放点积注意力的矩阵形状", "QK^T 得到 T×T 打分矩阵，逐行 softmax 后乘 V。")
    y0 = 80

    def mat(x, rows, cols, key, label, shape, hl_row=None, hl_col=None, fills=None, values=None):
        def f(i, j):
            if fills:
                return fills(i, j)
            on = (hl_row is not None and i == hl_row) or (hl_col is not None and j == hl_col)
            return main(key) if on else light(key)
        yy = y0 + (T * c - rows * c) / 2
        s.grid(x, yy, rows, cols, c, fills=f, stroke=WHITE, sw=1.5, values=values, vsize=10.5,
               vcolor=lambda i, j: INK)
        s.rect(x, yy, cols * c, rows * c, fill="none", stroke=main(key), sw=1.2)
        s.text(x + cols * c / 2, y0 - 26, label, size=17, weight="bold")
        s.text(x + cols * c / 2, y0 + T * c + 22, shape, size=13.5, color=MUTED)
        return x + cols * c

    x = 40
    xe = mat(x, T, dk, "q", "$Q$", "$T$×$d$_{k}", hl_row=t_hi)
    s.text(xe + 16, y0 + T * c / 2, "×", size=20)
    xe = mat(xe + 32, dk, T, "k", "$K$^{⊤}", "$d$_{k}×$T$", hl_col=s_hi)
    s.text(xe + 16, y0 + T * c / 2, "=", size=20)
    xS = xe + 32
    xe = mat(xS, T, T, "attn", "$QK$^{⊤}", "$T$×$T$（打分）",
             fills=lambda i, j: main("attn") if (i, j) == (t_hi, s_hi) else light("attn"))
    # 缩放 + 掩码 + softmax
    s.arrow([(xe + 10, y0 + T * c / 2), (xe + 140, y0 + T * c / 2)], color=INK, sw=1.6)
    s.text(xe + 75, y0 + T * c / 2 - 34, "÷ √$d$_{k}", size=14)
    s.text(xe + 75, y0 + T * c / 2 - 14, "+ $M$（掩码）", size=13.5)
    s.text(xe + 75, y0 + T * c / 2 + 18, "逐行 softmax", size=13.5, weight="bold", color=main("attn"))
    xA = xe + 150
    A = [[0.70, 0.30, 0.0, 0.0], [0.25, 0.45, 0.30, 0.0], [0.10, 0.60, 0.20, 0.10], [0.15, 0.25, 0.20, 0.40]]
    A = [[0.40, 0.25, 0.20, 0.15], [0.25, 0.45, 0.20, 0.10], [0.10, 0.60, 0.20, 0.10], [0.15, 0.25, 0.20, 0.40]]
    for r in A:
        assert abs(sum(r) - 1) < 1e-9
    xe = mat(xA, T, T, "attn", "$A$", "$T$×$T$（权重）",
             fills=lambda i, j: heat(A[i][j] / 0.65), values=lambda i, j: f".{int(round(A[i][j] * 100)):02d}")
    s.rect(xA - 2, y0 + t_hi * c - 2, T * c + 4, c + 4, fill="none", stroke=main("q"), sw=2.4, rx=3)
    s.text(xe + 16, y0 + T * c / 2, "×", size=20)
    xV = xe + 32
    xe = mat(xV, T, dv, "v", "$V$", "$T$×$d$_{v}")
    s.text(xe + 16, y0 + T * c / 2, "=", size=20)
    xO = xe + 32
    xe = mat(xO, T, dv, "attn", "输出", "$T$×$d$_{v}",
             fills=lambda i, j: main("attn") if i == t_hi else light("attn"))

    # 注释
    yb = 250
    notes = [
        (40, "1", "q", "$Q$ 第 $t$ 行 · $K$^{⊤} 第 $s$ 列", "= $q$_{t}·$k$_{s}：位置 $t$ 对位置 $s$ 的打分"),
        (380, "2", "attn", "每一行单独做 softmax", "一行 = 一个位置的注意力分配，和为 1"),
        (700, "3", "v", "$A$ 的第 $t$ 行乘 $V$", "= 对 $V$ 各行的加权和 = 输出第 $t$ 行"),
    ]
    for x, n, key, a, b in notes:
        s.rect(x, yb, 320 if n != "3" else 320, 84, fill=PANEL, stroke=BORDER, rx=10)
        s.badge(x + 24, yb + 26, n, key=key)
        s.text(x + 44, yb + 27, a, size=14, anchor="start", weight="bold")
        s.text(x + 44, yb + 57, b, size=13.5, anchor="start", color=INK)
    # 连线：注释到矩阵
    s.line(40 + 2 * c, y0 + T * c + 34, 40 + 2 * c, yb, color=main("q"), sw=1, dash="3 3")
    s.line(xA + 2 * c, y0 + T * c + 34, 530, yb, color=main("attn"), sw=1, dash="3 3")
    s.line(xO + 1.5 * c, y0 + T * c + 34, 860, yb, color=main("v"), sw=1, dash="3 3")
    s.text(530, 372, "深色格子跟踪同一个位置 $t$（这里 $t$=3）：它的 Query 行 → 它的打分行 → 它的权重行 → 它的输出行。"
           , size=13, color=MUTED)
    s.save(OUT / "03_scaled-dot-product-attention-matrices.svg")


if __name__ == "__main__":
    fig24()
    fig02()
    fig03()
