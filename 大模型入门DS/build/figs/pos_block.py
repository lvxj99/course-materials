"""Figures for positional encoding, Transformer block, architectures,
autoregressive generation, KV cache and batching."""

from __future__ import annotations

import math

from .common import *  # noqa: F401,F403
from figkit import P, Canvas, tw


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _mix(c0, c1, t):
    a, b = c0.lstrip("#"), c1.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(ca[i] + (cb[i] - ca[i]) * t):02x}" for i in range(3))


def _div(t):
    """Diverging ramp: orange (−1) — white (0) — blue (+1)."""
    t = min(1.0, max(0.0, t))
    return (_mix(P["orange"], P["white"], 2 * t) if t < 0.5
            else _mix(P["white"], P["blue"], 2 * t - 1))


def _arc(c, cx, cy, r, a0, a1, color=P["muted"], sw=1.1, dash="4 3", head=True):
    """Circular arc between two angles (degrees, CCW, y up)."""
    n = max(10, int(abs(a1 - a0)))
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    if head:
        s = 1 if a1 > a0 else -1
        ar = math.radians(a1)
        tx, ty = -math.sin(ar) * s, -math.cos(ar) * s
        L = math.hypot(tx, ty) or 1
        tx, ty = tx / L, ty / L
        px, py = pts[-1]
        hb, hw = 6.0, 3.2
        c.poly([(px, py), (px - hb * tx + hw * ty, py - hb * ty - hw * tx),
                (px - hb * tx - hw * ty, py - hb * ty + hw * tx)], fill=color)
        pts[-1] = (px - 0.7 * hb * tx, py - 0.7 * hb * ty)
    c.polyline(pts, stroke=color, sw=sw, dash=dash)


def _swatch_line(c, x, y, color, w=18):
    c.line(x, y - 3.5, x + w, y - 3.5, stroke=color, sw=1.8, cap="round")


def _mkparts(s):
    """Split a tiny math string into layout parts: letters italic, rest upright."""
    out, i = [], 0
    while i < len(s):
        ch = s[i]
        if ch in "_^" and i + 1 < len(s):
            i += 1
            kind = "sub" if ch == "_" else "sup"
            if i < len(s) and s[i] == "{":
                j = s.index("}", i)
                out.append((s[i + 1:j], kind))
                i = j + 1
            else:
                out.append((s[i], kind))
                i += 1
        elif ch == " ":
            out.append((" ", "s"))
            i += 1
        else:
            j = i
            alpha = ch.isalpha()
            while j < len(s) and s[j] != " " and s[j] not in "_^" and s[j].isalpha() == alpha:
                j += 1
            out.append((s[i:j], "i" if alpha else "u"))
            i = j
    return out


def _lay(c, x, y, parts, size=12.5, fill=None, anchor="start"):
    """Tiny math typesetter: parts = [(text, kind)] with kind u/i/sub/sup/'s'.

    Unlike Canvas.mtext it keeps upright serif for names such as MultiHead and
    never relies on leading/trailing spaces inside a <text> node."""
    fill = fill or P["ink"]

    def adv(t, k):
        if k == "s":
            return size * 0.30
        if k in ("sub", "sup"):
            return tw(t, size * 0.72, "serif")
        return tw(t, size, "serif")

    total = sum(adv(t, k) for t, k in parts)
    cx = x - (total if anchor == "end" else total / 2 if anchor == "middle" else 0)
    for t, k in parts:
        if k == "s":
            cx += adv(t, k)
            continue
        if k in ("sub", "sup"):
            sm = size * 0.72
            dy = size * 0.24 if k == "sub" else -size * 0.42
            c.text(cx, y + dy, t, size=sm, fill=fill, family="serif", italic=True)
        else:
            c.text(cx, y, t, size=size, fill=fill, family="serif", italic=(k == "i"))
        cx += adv(t, k)
    return cx


def _mth(c, x, y, s, size=12.5, fill=None, anchor="start"):
    return _lay(c, x, y, _mkparts(s), size=size, fill=fill, anchor=anchor)


# ---------------------------------------------------------------------------
# 05 — positional encoding and RoPE
# ---------------------------------------------------------------------------

def f05():
    c = Canvas(960, 560)
    D = TT = 32                    # 编码维度 / 位置数

    c.text(40, 30, "① 每个位置得到一个编码向量", size=11.5, fill=P["ink2"], weight="600")
    c.text(396, 30, "② 不同维度 = 不同频率的时钟", size=11.5, fill=P["ink2"], weight="600")
    c.text(628, 30, "③ RoPE：旋转 q、k 的相位", size=11.5, fill=P["ink2"], weight="600")

    # ---------------- ① sinusoidal table ----------------
    X0, Y0, CW, CH = 64, 88, 19, 9.5
    vals = [[math.sin(t / (10000 ** (2 * j / D))) for j in range(D // 2)]
            for t in range(TT)]
    c.heat(X0, Y0, (D // 2) * CW, TT * CH, vals, cmap=_div, vmin=-1, vmax=1,
           gap=0.7, rx=0.8)
    c.rect(X0, Y0, (D // 2) * CW, TT * CH, fill="none", stroke=P["rule"], rx=1)

    for t in (0, 8, 16, 24, 31):
        c.text(X0 - 8, Y0 + (t + 0.5) * CH + 3.2, str(t), size=9.2, fill=P["muted"],
               anchor="end")
    c.text(36, Y0 + TT * CH / 2, "位置 t ↓", size=10, fill=P["ink2"], anchor="middle",
           rotate=(-90, 36, Y0 + TT * CH / 2))

    for j in (0, 4, 8, 12, 15):
        c.text(X0 + (j + 0.5) * CW, Y0 + TT * CH + 15, str(j), size=9.2, fill=P["muted"],
               anchor="middle")
    c.text(X0 + 152, Y0 + TT * CH + 32, "维度 j →（每列一对 sin / cos）", size=10,
           fill=P["ink2"], anchor="middle")

    c.text(X0 + 152, 444, "每一行 = 一个位置的编码", size=9.8, fill=P["ink2"],
           anchor="middle")
    c.text(X0 + 152, 461, "左列变化快、右列几乎不变", size=9.4, fill=P["muted"],
           anchor="middle")

    # legend
    for i in range(40):
        c.rect(X0 + i * 3.3, 474, 3.4, 7, fill=_div(i / 39), stroke="none")
    c.text(X0, 495, "−1", size=9, fill=P["muted"])
    c.text(X0 + 132, 495, "+1", size=9, fill=P["muted"], anchor="end")
    c.text(X0 + 146, 483, "sin 值", size=9.4, fill=P["muted"])

    # ---------------- ② frequencies ----------------
    ax = Axes(c, 396, 88, 210, 304, xlim=(0, 60), ylim=(-1.28, 1.28),
              xticks=[0, 20, 40, 60], yticks=[-1, 0, 1],
              ytick_labels=["−1", "0", "+1"], grid=False, xlabel="位置 t")
    ax.curve(lambda t: math.sin(2 * math.pi * t / 60), 0, 60, n=240,
             color=P["blue"], sw=1.8)
    ax.curve(lambda t: math.sin(2 * math.pi * t / 10), 0, 60, n=600,
             color=P["orange"], sw=1.4, opacity=0.95)

    _swatch_line(c, 398, 448, P["blue"])
    c.text(422, 451, "低频：波长长、变化慢", size=9.8, fill=P["ink2"])
    _swatch_line(c, 398, 466, P["orange"])
    c.text(422, 469, "高频：波长短、变化快", size=9.8, fill=P["ink2"])
    c.text(398, 492, "叠加后每个位置都有唯一编码", size=9.4, fill=P["muted"])

    # ---------------- ③ RoPE ----------------
    ox, oy = 676, 360
    A_Q, A_K = 10, -40
    A_QP, A_KP = 65, -10
    R_Q, R_K = 158, 108

    def P_(a, r):
        return (ox + r * math.cos(math.radians(a)), oy - r * math.sin(math.radians(a)))

    c.line(ox - 46, oy, ox + 220, oy, stroke=P["rule"], sw=1)
    c.arrow(ox + 214, oy, ox + 224, oy, color=P["faint"], sw=1, head=5)
    c.line(ox, oy - 46, ox, oy + 82, stroke=P["rule"], sw=1)

    c.arrow(ox, oy, *P_(A_Q, R_Q), color=P["blue"], sw=1.5, head=6)
    c.arrow(ox, oy, *P_(A_K, R_K), color=P["orange"], sw=1.5, head=6)
    c.arrow(ox, oy, *P_(A_QP, R_Q), color=P["blue2"], sw=1.2, head=6, dash="5 3")
    c.arrow(ox, oy, *P_(A_KP, R_K), color=P["orange2"], sw=1.2, head=6, dash="5 3")

    _arc(c, ox, oy, R_Q, A_Q, A_QP, color=P["blue2"], sw=1.1, dash="4 3")
    _arc(c, ox, oy, R_K, A_K, A_KP, color=P["orange2"], sw=1.1, dash="4 3")

    qx, qy = P_(A_Q, R_Q)
    c.text(qx + 10, qy + 4, "q", size=11.5, fill=P["blue"], weight="600")
    kx, ky = P_(A_K, R_K)
    c.text(kx + 11, ky + 10, "k", size=11.5, fill=P["orange"], weight="600")

    px, py = P_(42, R_Q + 16)
    _mth(c, px, py, "tθ", size=11, fill=P["blue2"])
    px, py = P_(-25, R_K + 16)
    _mth(c, px + 2, py + 4, "sθ", size=11, fill=P["orange2"])

    qpx, qpy = P_(A_QP, R_Q)
    _mth(c, qpx - 6, qpy - 8, "q′ = R(tθ)q", size=10.5, fill=P["blue2"], anchor="end")
    kpx, kpy = P_(A_KP, R_K)
    _mth(c, kpx + 10, kpy + 4, "k′ = R(sθ)k", size=10.5, fill=P["orange2"])

    # key identity
    c.rect(628, 444, 300, 52, fill=P["blueL"], stroke=P["blueM"], rx=6)
    _mth(c, 640, 466, "q′^{T}k′ = q^{T}R((s−t)θ)k", size=12.5, fill=P["blue"])
    c.text(640, 487, "点积只依赖相对位移 s − t", size=9.8, fill=P["ink2"])

    c.text(40, 526, "正弦编码只是一个加在嵌入上的常数向量，不改变注意力公式；RoPE 则把位置写进 q、k 的相位，"
                    "让点积里自然出现相对位移 s − t。",
           size=10.8, fill=P["muted"])
    c.text(40, 544, "注意力本身对排列等变：没有位置信息时，「猫追狗」和「狗追猫」对模型是同一个词袋。",
           size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 06 — transformer block: residual + norm
# ---------------------------------------------------------------------------

def f06():
    c = Canvas(960, 560)

    # ---------------- main flow ----------------
    c.text(64, 44, "① 一个 Block 内的数据流", size=11, fill=P["ink2"], weight="600")
    c.text(64, 66, "隐藏状态 H 始终保持 T × d：每一步只改数值，不改形状", size=10.5,
           fill=P["muted"])
    c.rect(64, 160, 304, 288, fill="none", stroke=P["blueM"], rx=8, dash="5 4")
    c.rect(68, 157, 132, 15, fill=P["white"])
    c.text(72, 168, "Block ℓ（Pre-Norm）", size=10.5, fill=P["blue"], weight="600")
    c.rect(324, 157, 32, 15, fill=P["white"])
    c.text(354, 168, "× N", size=10.5, fill=P["muted"], anchor="end")

    # input
    _mth(c, 206, 460, "H^{(ℓ)}", size=13, anchor="end")
    c.text(212, 460, "（T × d）", size=10, fill=P["muted"])
    c.arrow(220, 446, 220, 430, color=P["muted"], sw=1.3, head=5)

    norm_box(c, 110, 406, 220, 24, "LayerNorm / RMSNorm")
    c.arrow(220, 406, 220, 390, color=P["muted"], sw=1.3, head=5)

    block(c, 110, 334, 220, 56, "Multi-Head Attention", "h 个头 · Q/K/V 投影 · 因果掩码",
          fill=P["blueL"], stroke=P["blueM"], color=P["blue"], color2=P["blue"])
    c.arrow(220, 334, 220, 325, color=P["muted"], sw=1.3, head=5)

    plus_circle(c, 220, 316)
    _mth(c, 242, 321, "U", size=12.5)

    c.arrow(220, 307, 220, 292, color=P["muted"], sw=1.3, head=5)
    norm_box(c, 110, 268, 220, 24, "LayerNorm / RMSNorm")
    c.arrow(220, 268, 220, 252, color=P["muted"], sw=1.3, head=5)

    block(c, 110, 196, 220, 56, "Feed Forward", "逐位置 MLP：d → 4d → d",
          fill=P["panel"], stroke=P["rule"])
    c.arrow(220, 196, 220, 187, color=P["muted"], sw=1.3, head=5)

    plus_circle(c, 220, 178)
    c.arrow(220, 169, 220, 154, color=P["muted"], sw=1.3, head=5)

    _mth(c, 206, 144, "H^{(ℓ+1)}", size=13, anchor="end")
    c.text(212, 144, "（T × d）", size=10, fill=P["muted"])

    # residual rails
    c.polyline([(220, 442), (74, 442), (74, 316)], stroke=P["gold"], sw=1.2)
    c.arrow(74, 316, 211, 316, color=P["gold"], sw=1.2, head=5)
    c.polyline([(220, 302), (358, 302), (358, 178)], stroke=P["gold"], sw=1.2)
    c.arrow(358, 178, 229, 178, color=P["gold"], sw=1.2, head=5)

    # ---------------- formulas ----------------
    c.text(396, 44, "② 两次子层更新，结构完全相同", size=11, fill=P["ink2"],
           weight="600")
    c.rect(396, 56, 534, 92, fill=P["panel"], stroke=P["rule"], rx=6)
    _lay(c, 414, 88, [("U", "i"), (" ", "s"), ("=", "u"), (" ", "s"), ("H", "i"),
                     ("(ℓ)", "sup"), (" ", "s"), ("+", "u"), (" ", "s"),
                     ("MultiHead", "u"), ("(", "u"), ("Norm", "u"), ("(", "u"),
                     ("H", "i"), ("(ℓ)", "sup"), (")", "u"), (")", "u")], size=13.2)
    _lay(c, 414, 124, [("H", "i"), ("(ℓ+1)", "sup"), (" ", "s"), ("=", "u"), (" ", "s"),
                      ("U", "i"), (" ", "s"), ("+", "u"), (" ", "s"),
                      ("FFN", "u"), ("(", "u"), ("Norm", "u"), ("(", "u"), ("U", "i"),
                      (")", "u"), (")", "u")], size=13.2)

    c.text(396, 172, "两次 Norm 各有自己的可学习参数：LayerNorm 有 γ、β，RMSNorm 只有缩放 g。",
           size=10.5, fill=P["ink2"])
    c.text(396, 190, "残差把 H 原样抄进下一行：信息与梯度都沿这条恒等通路逐层累积。",
           size=10.5, fill=P["ink2"])

    # ---------------- pre-norm vs post-norm ----------------
    c.rect(396, 206, 534, 258, fill=P["white"], stroke=P["rule"], rx=8)
    c.text(412, 228, "③ 区别只在 Norm 放在子层之前还是之后", size=11, fill=P["ink2"],
           weight="600")
    c.line(663, 242, 663, 452, stroke=P["rule"], sw=1, dash="3 4")

    def stack(cx, head, desc, order, rail, caption, head_color):
        c.text(cx, 252, head, size=11.5, fill=head_color, weight="600", anchor="middle")
        c.text(cx, 268, desc, size=9.6, fill=P["muted"], anchor="middle")
        c.text(cx, 442, caption, size=9.6, fill=P["muted"], anchor="middle")

        rows = [300, 340, 380, 420]
        kinds = order + ["x"]          # top → bottom, 3 boxes + input chip
        bw = 132
        # input chip
        c.rect(cx - 24, 408, 48, 24, fill=P["panel2"], stroke=P["rule"], rx=4)
        c.text(cx, 424, "x", size=11.5, fill=P["ink2"], anchor="middle",
               family="serif", italic=True)
        # boxes
        for i, kind in enumerate(kinds[:3]):
            y = rows[i] - 12
            if kind == "norm":
                norm_box(c, cx - bw / 2, y, bw, 24, "Norm")
            elif kind == "attn":
                c.rect(cx - bw / 2, y, bw, 24, fill=P["blueL"], stroke=P["blueM"], rx=4)
                c.text(cx, y + 16, "Self-Attention", size=10.5, fill=P["blue"],
                       anchor="middle")
            else:
                plus_circle(c, cx, rows[i])
        # arrows between consecutive rows
        for i in range(3):
            up_gap = 9 if kinds[i] == "plus" else 12
            lo_gap = 9 if kinds[i + 1] == "plus" else 12
            c.arrow(cx, rows[i + 1] - lo_gap, cx, rows[i] + up_gap,
                    color=P["muted"], sw=1.2, head=5)
        # output stub
        top_gap = 9 if kinds[0] == "plus" else 12
        c.arrow(cx, rows[0] - top_gap, cx, rows[0] - 28, color=P["muted"], sw=1.2, head=5)
        # skip connection from x chip to the plus circle row
        plus_row = rows[kinds.index("plus")] if "plus" in kinds else rows[2]
        c.polyline([(cx - 24, 420), (rail, 420), (rail, plus_row)], stroke=P["gold"],
                   sw=1.2)
        c.arrow(rail, plus_row, cx - 9, plus_row, color=P["gold"], sw=1.2, head=5)

    stack(520, "Pre-Norm", "Norm 在子层之前", ["plus", "attn", "norm"], 438,
          "残差通路不经过任何 Norm", P["blue"])
    stack(790, "Post-Norm", "先相加、再 Norm", ["norm", "plus", "attn"], 708,
          "每层输出先归一化再进下一层", P["ink2"])

    # ---------------- footnotes ----------------
    c.text(40, 526, "Pre-Norm 把残差留成一条从输入直通输出的恒等通路，深层网络更容易优化；"
                    "Post-Norm 让每层输出都被归一化，训练通常需要 warmup。",
           size=10.8, fill=P["muted"])
    c.text(40, 544, "残差相加要求形状一致（都是 T × d）；两次 Norm 的参数互不共享，"
                    "换成 RMSNorm 只是去掉均值中心化、省下一部分开销。",
           size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 07 — encoder-only / encoder-decoder / decoder-only
# ---------------------------------------------------------------------------

def _mask(c, x, y, cell, rows, cols, ok, split=None):
    """Attention mask grid; a wider gap is inserted before column `split`."""
    s = cell - 1.4
    for i in range(rows):
        for j in range(cols):
            xx = x + j * cell + (3 if split is not None and j >= split else 0)
            if ok(i, j):
                c.rect(xx, y + i * cell, s, s, fill=P["blueM"], stroke="none", rx=1.4)
            else:
                c.rect(xx, y + i * cell, s, s, fill=P["white"], stroke=P["rule"],
                       sw=0.7, rx=1.4)


def _roww(toks, size=11, gap=5):
    return sum(max(28, tw(t, size) + 18) for t in toks) + gap * (len(toks) - 1)


def _row(c, x, y, toks, h=26, size=11, hl=None, gap=5, fill=P["panel2"],
         stroke=P["rule"], color=P["ink2"], hfill=P["violetL"], hstroke=P["violetM"],
         hcolor=P["violet"]):
    """Left-aligned chip row; returns (spans, width)."""
    spans, cx = [], x
    for i, t in enumerate(toks):
        w = max(28, tw(t, size) + 18)
        on = (i == hl)
        c.rect(cx, y, w, h, fill=hfill if on else fill,
               stroke=hstroke if on else stroke, rx=4)
        c.text(cx + w / 2, y + h / 2 + size * 0.36, t, size=size,
               fill=hcolor if on else color, anchor="middle")
        spans.append((cx, w))
        cx += w + gap
    return spans, cx - x - gap


def f07():
    c = Canvas(960, 470)
    X0 = [40, 340, 640]
    CX = [180, 480, 780]

    heads = [("A", "Encoder-only", "每个位置都能读整句"),
             ("B", "Encoder–decoder", "先编码整句，再逐字解码"),
             ("C", "Decoder-only", "只看左边，逐字生成")]
    for i, (tag_, name, desc) in enumerate(heads):
        c.text(X0[i], 36, tag_, size=11.5, fill=P["faint"], weight="700")
        c.text(X0[i] + 17, 36, name, size=11.5, fill=P["ink"], weight="600")
        c.text(X0[i], 56, desc, size=10.2, fill=P["muted"])

    # ---------------- A ----------------
    _row(c, 180 - _roww(["x₁", "x₂", "x₃", "x₄"], 10) / 2, 194,
         ["x₁", "x₂", "x₃", "x₄"], h=22, size=10)
    c.arrow(180, 194, 180, 182, color=P["muted"], sw=1.2, head=5)
    block(c, 110, 140, 140, 40, "Transformer Block", "双向自注意力 · 无掩码",
          fill=P["blueL"], stroke=P["blueM"], color=P["blue"], color2=P["blue"],
          size=11.5, size2=9.4)
    c.arrow(180, 140, 180, 124, color=P["muted"], sw=1.2, head=5)
    _row(c, 180 - _roww(["h₁", "h₂", "h₃", "h₄"], 10) / 2, 98,
         ["h₁", "h₂", "h₃", "h₄"], h=22, size=10,
         fill=P["blueL"], stroke=P["blueM"], color=P["blue"])
    c.text(180, 86, "每个位置都有一个上下文化表示", size=9, fill=P["muted"],
           anchor="middle")

    # ---------------- B ----------------
    block(c, 350, 140, 100, 40, "Encoder", "× N 层", fill=P["blueL"],
          stroke=P["blueM"], color=P["blue"], color2=P["blue"], size=11, size2=9.2)
    block(c, 510, 140, 100, 40, "Decoder", "× N 层 + 因果掩码", fill=P["violetL"],
          stroke=P["violetM"], color=P["violet"], color2=P["violet"], size=11,
          size2=9.2)
    c.arrow(450, 160, 508, 160, color=P["violet"], sw=1.3, head=5)
    _mth(c, 480, 150, "K, V", size=9, fill=P["violet"], anchor="middle")
    c.text(480, 176, "交叉注意力", size=8.8, fill=P["violet"], anchor="middle")

    _row(c, 400 - _roww(["x₁", "x₂"], 10) / 2, 194, ["x₁", "x₂"], h=22, size=10)
    c.arrow(400, 194, 400, 182, color=P["muted"], sw=1.2, head=5)
    _row(c, 560 - _roww(["y₁", "y₂"], 10) / 2, 194, ["y₁", "y₂"], h=22, size=10)
    c.arrow(560, 194, 560, 182, color=P["muted"], sw=1.2, head=5)
    c.arrow(560, 140, 560, 124, color=P["muted"], sw=1.2, head=5)
    _row(c, 560 - _roww(["下一个 token"], 10) / 2, 98, ["下一个 token"], h=22,
         size=10, fill=P["violetL"], stroke=P["violetM"], color=P["violet"])

    # ---------------- C ----------------
    _row(c, 780 - _roww(["x₁", "x₂", "x₃", "x₄"], 10) / 2, 194,
         ["x₁", "x₂", "x₃", "x₄"], h=22, size=10)
    c.arrow(780, 194, 780, 182, color=P["muted"], sw=1.2, head=5)
    block(c, 710, 140, 140, 40, "Transformer Block", "因果掩码 · 只看左边",
          fill=P["violetL"], stroke=P["violetM"], color=P["violet"],
          color2=P["violet"], size=11.5, size2=9.4)
    c.arrow(780, 140, 780, 124, color=P["muted"], sw=1.2, head=5)
    _row(c, 780 - _roww(["下一个 token"], 10) / 2, 98, ["下一个 token"], h=22,
         size=10, fill=P["violetL"], stroke=P["violetM"], color=P["violet"])
    c.text(780, 86, "只回看左边，位置 t 不读 t+1", size=9, fill=P["muted"],
           anchor="middle")

    # ---------------- masks ----------------
    c.line(40, 236, 920, 236, stroke=P["rule"], sw=1)
    c.text(40, 258, "注意力掩码：行 = 读取者，列 = 可读的位置；蓝格 = 可以读", size=10,
           fill=P["ink2"])

    _mask(c, 145, 272, 14, 5, 5, lambda i, j: True)
    _mask(c, 745, 272, 14, 5, 5, lambda i, j: j <= i)
    _mask(c, 407, 272, 14, 5, 10, lambda i, j: j < 5 or j - 5 <= i, split=5)

    c.text(180, 356, "每行都全亮：双向", size=9.6, fill=P["ink2"], anchor="middle")
    c.text(480, 356, "左 5 列全亮 + 右下三角", size=9.6, fill=P["ink2"], anchor="middle")
    c.text(780, 356, "下三角：只看 1..t", size=9.6, fill=P["ink2"], anchor="middle")

    # ---------------- models ----------------
    models = [("BERT · RoBERTa · ViT", "分类、检索表示、图像 patch"),
              ("T5 · 原始 Transformer", "翻译、摘要（整段进、整段出）"),
              ("GPT 系列 · Llama", "自回归生成、对话")]
    for i, (m, t) in enumerate(models):
        c.text(X0[i], 382, m, size=10.2, fill=P["ink2"], weight="600")
        c.text(X0[i], 398, t, size=10.2, fill=P["muted"])

    # ---------------- footnote ----------------
    c.text(40, 432, "三者的 Block 内部几乎一样（注意力 + FFN + 残差 + Norm），"
                    "区别只在「掩码」和「如何组织输入输出」。",
           size=10.8, fill=P["muted"])
    c.text(40, 450, "编码器能看全句，适合理解；解码器只能看左边，适合生成；"
                    "编码器–解码器把两者串起来，中间用交叉注意力传递 K、V。",
           size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 08 — autoregressive generation
# ---------------------------------------------------------------------------

def f08():
    c = Canvas(960, 520)
    X0 = [40, 270, 500, 730]
    CAND = ["我", "喜欢", "机器", "学习", "。"]
    PROBS = [
        [0.62, 0.04, 0.03, 0.02, 0.29],
        [0.04, 0.58, 0.04, 0.02, 0.32],
        [0.03, 0.02, 0.50, 0.06, 0.39],
        [0.02, 0.02, 0.03, 0.52, 0.41],
    ]
    ROWS = [["<bos>"],
            ["<bos>", "我"],
            ["<bos>", "我", "喜欢"],
            ["<bos>", "我", "喜欢", "机器"]]
    BASE, SCALE = 288, 148

    c.text(40, 34, "每一步只生成一个 token，再把它接回上下文", size=11.5,
           fill=P["ink2"], weight="600")

    for s in range(4):
        x0 = X0[s]
        c.text(x0, 58, f"第 {s + 1} 步", size=9.8, fill=P["muted"])

        spans, wsum = _row(c, x0, 86, ROWS[s], h=26, size=11,
                           hl=None if s == 0 else s)
        lastx, lastw = spans[-1]

        # panel + bars
        c.rect(x0, 132, 210, 180, fill=P["panel"], stroke=P["rule"], rx=6)
        c.arrow(lastx + lastw / 2, 114, lastx + lastw / 2, 130, color=P["muted"],
                sw=1.2, head=5)
        c.line(x0 + 8, BASE - 0.5 * SCALE, x0 + 202, BASE - 0.5 * SCALE,
               stroke=P["faint"], sw=0.8, dash="3 3")
        c.text(x0 + 202, BASE - 0.5 * SCALE - 4, "0.5", size=8.2, fill=P["faint"],
               anchor="end")

        bw, gap = 22, 8
        bx0 = x0 + (210 - (5 * bw + 4 * gap)) / 2
        top_i = max(range(5), key=lambda k: PROBS[s][k])
        for k, p in enumerate(PROBS[s]):
            h = p * SCALE
            x = bx0 + k * (bw + gap)
            on = (k == top_i)
            c.rect(x, BASE - h, bw, h, fill=P["violetM"] if on else P["blueM"],
                   stroke=P["violet"] if on else "none", sw=1, rx=2)
            c.text(x + bw / 2, BASE - h - 5, f"{p:.2f}", size=8.4,
                   fill=P["violet"] if on else P["muted"], anchor="middle",
                   weight="600" if on else None)
            c.text(x + bw / 2, BASE + 15, CAND[k], size=8.6,
                   fill=P["violet"] if on else P["muted"], anchor="middle",
                   weight="600" if on else None)

        # chosen token, feeding the next step
        tok = CAND[top_i]
        c.rect(x0 + 12, 318, 46, 24, fill=P["violetL"], stroke=P["violet"], rx=4)
        c.text(x0 + 35, 334, tok, size=11, fill=P["violet"], anchor="middle",
               weight="600")
        _mth(c, x0 + 64, 334, "→ 并入下一步" if s < 3 else "→ 拼出整句", size=9,
             fill=P["muted"])

        # wire back into the next context row
        if s < 3:
            nx = X0[s + 1]
            nrow = ROWS[s + 1]
            cx_new = nx
            for k, t in enumerate(nrow):
                wid = max(28, tw(t, 11) + 18)
                if k == len(nrow) - 1:
                    cx_new = cx_new + wid / 2
                else:
                    cx_new += wid + 5
            c.polyline([(x0 + 35, 342), (x0 + 35, 356), (x0 + 214, 356),
                        (x0 + 214, 74), (cx_new, 74)], stroke=P["violet2"], sw=1.1,
                       dash="4 3")
            c.arrow(cx_new, 74, cx_new, 84, color=P["violet2"], sw=1.1, head=5)

    # ---------------- train vs infer ----------------
    c.rect(40, 376, 880, 78, fill=P["panel"], stroke=P["rule"], rx=8)
    c.text(60, 400, "训练：整段一次送入", size=11, fill=P["blue"], weight="600")
    c.text(60, 421, "因果掩码保证每个位置只看左边，T 个位置的", size=10.2,
           fill=P["ink2"])
    c.text(60, 437, "损失在同一个前向里并行算出。", size=10.2, fill=P["ink2"])

    c.line(480, 386, 480, 444, stroke=P["rule"], sw=1, dash="3 4")
    c.text(492, 400, "推理：一次只前进一格", size=11, fill=P["violet"], weight="600")
    c.text(492, 421, "第 t 步的输出要接回输入才能算第 t+1 步，只能", size=10.2,
           fill=P["ink2"])
    c.text(492, 437, "串行；每一步都要重新读入全部上下文。", size=10.2, fill=P["ink2"])

    c.text(40, 488, "同一套权重、同一个前向：训练并行、推理串行——这是训练吞吐远高于推理的根本原因。",
           size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 09 — parallel processing and KV cache
# ---------------------------------------------------------------------------

def f09():
    c = Canvas(960, 560)
    T, CELL = 6, 34
    MX, MY = 64, 112

    # ---------------- left: prefill ----------------
    c.text(40, 38, "① Prefill / 训练：T 个位置一次算完", size=11.5, fill=P["ink2"],
           weight="600")
    c.text(40, 58, "整段序列同时进入；第 t 个位置只读 1..t", size=10.2,
           fill=P["muted"])

    for k in range(T):
        c.rect(MX + k * CELL, 80, CELL - 2, 24, fill=P["panel2"], stroke=P["rule"],
               rx=4)
        c.text(MX + k * CELL + (CELL - 2) / 2, 96, f"x{k + 1}", size=8.8,
               fill=P["ink2"], anchor="middle")

    c.rect(MX, MY, T * CELL, T * CELL, fill="none", stroke=P["rule"], rx=1)
    _mask(c, MX, MY, CELL, T, T, lambda i, j: j <= i)
    for i in range(T):
        c.text(MX - 8, MY + i * CELL + CELL / 2 + 3.4, str(i + 1), size=8.8,
               fill=P["muted"], anchor="end")
    c.text(MX - 8, MY - 8, "Query", size=8.8, fill=P["muted"], anchor="end")
    c.text(MX + T * CELL + 9, MY + 12, "Key →", size=8.8, fill=P["muted"])
    c.rect(MX, MY + 3 * CELL, T * CELL, CELL, fill="none", stroke=P["blue"],
           sw=1.6, rx=2)

    c.text(40, 348, "第 4 行的蓝色区域 = 允许读的 1..4；右侧白色格已被掩掉。", size=9.6,
           fill=P["ink2"])
    c.text(40, 366, "T 个 Query 行在同一次前向里并行算完 → 决定 TTFT（首 token 延迟）。",
           size=9.6, fill=P["ink2"])

    # ---------------- right: decode ----------------
    RX = 480
    c.text(RX, 38, "② Decode：每步只算 1 个新位置", size=11.5, fill=P["ink2"],
           weight="600")
    c.text(RX, 58, "Q 只有 1 行；历史 K、V 从缓存直接取，不再重算", size=10.2,
           fill=P["muted"])

    c.rect(RX, 82, 108, 26, fill=P["violetL"], stroke=P["violet"], rx=4)
    c.text(RX + 54, 99, "新位置 T+1", size=10, fill=P["violet"], anchor="middle")
    c.arrow(RX + 54, 108, RX + 54, 132, color=P["violet"], sw=1.2, head=5)

    c.rect(RX, 136, 210, 46, fill=P["blueL"], stroke=P["blueM"], rx=5)
    c.text(RX + 105, 156, "Attention", size=11.5, fill=P["blue"], anchor="middle",
           weight="600")
    c.text(RX + 105, 172, "q 只有 1 行，读全部 T 行 K", size=9, fill=P["blue"],
           anchor="middle")

    # caches
    for i, (lab, tot, fillc, strokec, col) in enumerate(
            [("K cache", "T 行 × d", P["orangeL"], P["orangeM"], P["orange"]),
             ("V cache", "T 行 × d", P["tealL"], P["tealM"], P["teal"])]):
        bx = RX + i * 110
        c.rect(bx, 216, 100, 50, fill=fillc, stroke=strokec, rx=5)
        c.text(bx + 50, 236, lab, size=10.5, fill=col, anchor="middle", weight="600")
        c.text(bx + 50, 252, tot, size=8.8, fill=col, anchor="middle")
        c.arrow(bx + 50, 216, bx + 50, 186, color=P["muted"], sw=1.2, head=5)
    c.text(RX + 105, 284, "每步只往后追加 1 行，历史部分不重算", size=9.2,
           fill=P["muted"], anchor="middle")

    # cache growth
    for i, (w, lab) in enumerate(((36, "t = T"), (56, "T+1"), (76, "T+2"))):
        y = 300 + i * 11
        c.rect(RX, y, w - 9, 7, fill=P["panel2"], stroke=P["rule"], rx=2)
        c.rect(RX + w - 9, y, 9, 7, fill=P["violetM"], rx=2)
        c.text(RX + w + 6, y + 7, lab, size=8, fill=P["faint"])

    c.arrow(RX + 212, 159, RX + 240, 159, color=P["muted"], sw=1.2, head=5)
    c.rect(RX + 244, 146, 122, 26, fill=P["violetL"], stroke=P["violetM"], rx=4)
    c.text(RX + 305, 163, "下一个 token", size=9.8, fill=P["violet"], anchor="middle")

    c.text(RX, 348, "每步都要把新 token 的 q 与全部缓存做注意力，但不必重算历史 K、V。",
           size=9.6, fill=P["ink2"])
    c.text(RX, 366, "这一步的耗时接近常数 → 决定 TPOT（每个输出 token 的间隔）。", size=9.6,
           fill=P["ink2"])

    # ---------------- bottom ----------------
    c.line(40, 390, 920, 390, stroke=P["rule"], sw=1)
    c.text(40, 414, "缓存省掉重复计算历史 K/V，代价是显存随 T 线性增长：", size=10.5,
           fill=P["ink2"])
    _mth(c, 40, 444, "KV cache ≈ 2 · B · L · T · H_{kv} · d_{head} · b 字节", size=13,
         fill=P["ink"])
    c.text(40, 468, "2 = K 与 V；B 批大小，L 层数，T 序列长度，H_kv KV 头数（GQA 时小于头数），"
                    "d_head 每头维度，b 每元素字节（fp16 为 2）。",
           size=9.6, fill=P["muted"])
    c.text(40, 500, "训练 / prefill 不需要缓存：T 个位置本来就一次算完，K、V 现算现用；"
                    "只有自回归解码才需要把历史存下来。",
           size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 25 — batching: throughput vs tail latency
# ---------------------------------------------------------------------------

def f25():
    c = Canvas(960, 420)
    X0, Y0, W, H = 110, 56, 700, 232
    BT = [1, 2, 4, 8, 16, 32, 64]

    def X(v):
        return X0 + math.log10(v) / math.log10(64) * W

    def thr(b):
        return 2400 * (1 - math.exp(-b / 6))

    def lat(b):
        return 6 + 1.4 * b ** 1.08

    def Yr(v):
        return Y0 + H - v / 180 * H

    # mode bands
    c.rect(X0, Y0, X(4) - X0, H, fill=P["blueL"], stroke="none")
    c.rect(X(16), Y0, X(64) - X(16), H, fill=P["panel2"], stroke="none")
    c.text(X0 + 10, Y0 + 18, "Fast 模式", size=10.5, fill=P["blue"], weight="600")
    c.text(X0 + 10, Y0 + 32, "小批次 · 低延迟 · 单价高", size=9, fill=P["ink2"])
    c.text(X(16) + 10, Y0 + 18, "标准模式", size=10.5, fill=P["ink2"], weight="600")
    c.text(X(16) + 10, Y0 + 32, "大批次 · 高吞吐 · 单价低", size=9, fill=P["ink2"])

    ax = Axes(c, X0, Y0, W, H, xlim=(1, 64), ylim=(0, 2600), xlog=True,
              xticks=BT, xtick_labels=["1", "2", "4", "8", "16", "32", "64"],
              yticks=[0, 800, 1600, 2400],
              ytick_labels=["0", "800", "1600", "2400"],
              xlabel="batch size（对数刻度）")
    ax.curve(thr, 0, math.log10(64), n=160, color=P["blue"], sw=2)

    # right axis (P95 latency)
    c.line(X0 + W, Y0, X0 + W, Y0 + H, stroke=P["red2"], sw=1)
    for v in (0, 45, 90, 135, 180):
        c.line(X0 + W, Yr(v), X0 + W + 3.5, Yr(v), stroke=P["red2"], sw=1)
        c.text(X0 + W + 8, Yr(v) + 3.6, str(v), size=10, fill=P["red"])
    bs = [1 + 63 * i / 48 for i in range(49)]
    c.polyline([(X(b), Yr(lat(b))) for b in bs], stroke=P["red"], sw=1.8)

    # saturation line
    c.line(X(16), Y0 - 4, X(16), Y0 + H, stroke=P["ink2"], sw=1.1, dash="3 3")
    c.text(X(16), Y0 - 12, "吞吐饱和点 b ≈ 16", size=9.3, fill=P["ink2"],
           anchor="middle")

    # axis titles
    c.text(60, Y0 + H / 2, "吞吐 tokens/s", size=11, fill=P["blue"], anchor="middle",
           rotate=(-90, 60, Y0 + H / 2))
    c.text(X0 + W + 56, Y0 + H / 2, "P95 延迟 ms", size=11, fill=P["red"],
           anchor="middle", rotate=(-90, X0 + W + 56, Y0 + H / 2))

    # legend
    c.line(112, 40, 130, 40, stroke=P["blue"], sw=2)
    c.text(136, 44, "吞吐（左轴）", size=10, fill=P["ink2"])
    c.line(226, 40, 244, 40, stroke=P["red"], sw=2)
    c.text(250, 44, "P95 延迟（右轴）", size=10, fill=P["ink2"])

    # callouts
    c.text(608, 150, "带宽 / 算力打满", size=9.2, fill=P["blue"])
    c.text(608, 164, "→ 吞吐不再上升", size=9.2, fill=P["blue"])
    c.line(700, 156, 762, 80, stroke=P["blue2"], sw=0.9, dash="3 2")
    c.dot(763, 79, 2.2, fill=P["blue"])
    c.text(626, 250, "排队等待 + 单步更久", size=9.2, fill=P["red"])
    c.text(626, 264, "→ 尾部延迟（P95）上升", size=9.2, fill=P["red"])
    c.line(700, 246, 746, 178, stroke=P["red2"], sw=0.9, dash="3 2")
    c.dot(749, 170, 2.2, fill=P["red"])

    # footnotes
    c.text(40, 352, "合批让同一份权重同时服务多条序列，算术强度上升、单位成本下降；"
                    "代价是排队等待与单步墙钟时间变长。",
           size=10.8, fill=P["muted"])
    c.text(40, 372, "吞吐 = batch ÷ 单步延迟；当延迟的增长快过 batch，边际收益就变负——"
                    "所以 Fast / 标准两种模式按业务选。",
           size=10.8, fill=P["muted"])
    c.text(40, 400, "P95 取的是尾部：平均值还好看时，最慢的那 5% 请求可能已经超时。",
           size=10.2, fill=P["faint"])
    return c


FIGURES = {
    "05_positional-encoding-and-rope": f05,
    "06_transformer-block-residual-norm": f06,
    "07_transformer-architectures-encoder-decoder": f07,
    "08_autoregressive-generation": f08,
    "09_parallel-processing-and-kv-cache": f09,
    "25_batching-throughput-latency": f25,
}
