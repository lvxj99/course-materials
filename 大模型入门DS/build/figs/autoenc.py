"""Figures for section 8: autoencoders, denoising AE, MAE, VAE, GAN."""

from __future__ import annotations

import math
import random

from .common import *  # noqa: F401,F403
from figkit import P, Canvas, ramp, tw


# ---------------------------------------------------------------------------
# shared: a handwritten "3", rasterised to a 28x28 grey-scale image
# ---------------------------------------------------------------------------

INK_IMG = ramp("#ffffff", "#3a4550")
LAT = VIOLETS

# skeleton of the digit, in normalised coordinates (y grows downwards)
_S3 = [
    (0.285, 0.235), (0.355, 0.172), (0.470, 0.145), (0.585, 0.152),
    (0.690, 0.196), (0.752, 0.278), (0.760, 0.372), (0.720, 0.448),
    (0.640, 0.492), (0.556, 0.505), (0.636, 0.532), (0.716, 0.590),
    (0.758, 0.678), (0.752, 0.772), (0.686, 0.842), (0.570, 0.876),
    (0.430, 0.874), (0.318, 0.836), (0.246, 0.768),
]


def _seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    t = ((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy or 1e-9)
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    return math.hypot(px - ax - t * vx, py - ay - t * vy)


def glyph(n=28):
    """Rasterised digit: n x n grid of intensities in [0, 1]."""
    hw, aa = 0.086, 0.052
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            px, py = (j + 0.5) / n, (i + 0.5) / n
            d = min(_seg_dist(px, py, *_S3[k], *_S3[k + 1]) for k in range(len(_S3) - 1))
            row.append(round(max(0.0, min(1.0, (hw + aa - d) / aa)), 3))
        out.append(row)
    return out


def _blur(vals, k=1, gain=0.94):
    n = len(vals)
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            s, cnt = 0.0, 0
            for di in range(-k, k + 1):
                for dj in range(-k, k + 1):
                    ii, jj = i + di, j + dj
                    if 0 <= ii < n and 0 <= jj < n:
                        s += vals[ii][jj]
                        cnt += 1
            row.append(gain * s / cnt)
        out.append(row)
    return out


def recon_img(vals):
    """Slightly blurred reconstruction with a lost bottom-right corner."""
    n = len(vals)
    g = _blur(vals, 1, 0.96)
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            v = g[i][j]
            d = (i + j) - 2 * (n - 5)
            if d > 0:
                v *= max(0.0, 1.0 - d / 3.5)
            row.append(round(v, 3))
        out.append(row)
    return out


def noisy(vals, seed=7, sigma=0.34):
    rnd = random.Random(seed)
    n = len(vals)
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            v = vals[i][j] + rnd.gauss(0, sigma)
            row.append(round(max(0.0, min(1.0, v)), 3))
        out.append(row)
    return out


def img(c, x, y, size, vals, grid=True, border=P["faint"], rx=3):
    """Draw the grey-scale digit as a pixel grid with a hairline frame."""
    n = len(vals)
    cell = size / n
    c.rect(x, y, size, size, fill=P["white"])
    for i in range(n):
        for j in range(n):
            v = vals[i][j]
            c.rect(x + j * cell, y + i * cell, cell, cell, fill=INK_IMG(v),
                   stroke="#eef1f4" if grid else None, sw=0.4, rx=0.5)
    c.rect(x, y, size, size, fill="none", stroke=border, sw=1, rx=rx)
    return {"x": x, "y": y, "w": size, "h": size, "c": cell}


def latent(c, x, y, vals, w=22, cell=8.2, cmap=LAT):
    for i, v in enumerate(vals):
        c.rect(x, y + i * cell, w, cell - 1.3, fill=cmap(0.13 + 0.78 * v),
               stroke=P["violet"], sw=0.5, rx=1.5)
    return {"x": x, "y": y, "w": w, "h": len(vals) * cell}


def latent_h(c, x, y, vals, h=12, cell=5.2, cmap=LAT):
    for i, v in enumerate(vals):
        c.rect(x + i * cell, y, cell - 1.2, h, fill=cmap(0.13 + 0.78 * v),
               stroke=P["violet"], sw=0.5, rx=1.5)
    return {"x": x, "y": y, "w": len(vals) * cell, "h": h}


def circle_pts(cx, cy, r, n=72):
    return [(cx + r * math.cos(2 * math.pi * i / n),
             cy + r * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]


def funnel(c, x, y, w, h, narrow=0.64, flip=False, fill=P["blueL"], stroke=P["blueM"]):
    hh = h * narrow
    if flip:
        pts = [(x, y + (h - hh) / 2), (x + w, y), (x + w, y + h), (x, y + (h + hh) / 2)]
    else:
        pts = [(x, y), (x + w, y + (h - hh) / 2), (x + w, y + (h + hh) / 2), (x, y + h)]
    c.poly(pts, fill=fill, stroke=stroke, sw=1.1)
    return c


def ar(c, x1, y1, x2, y2, color=P["muted"], sw=1.3, head=5.5, dash=None, sh=False):
    c.arrow(x1, y1, x2, y2, color=color, sw=sw, head=head, dash=dash, start_head=sh)
    return c


# ---------------------------------------------------------------------------
# mixed text / math runs
# ---------------------------------------------------------------------------
# x̂ is drawn with a hand-placed circumflex and the norm bars with two hairlines:
# the combining mark Segoe UI ships lands off-centre at these sizes, and an
# italic double-bar slants.  Runs: ("text", kind) with kind
#   "s" sans, "m" serif italic, "h" hatted x, "t" tilded x, "b" norm bars.

def _xmark(c, x, y, size, fill, mark):
    w = size * 0.66
    if mark == "tilde":
        c.text(x, y, "x\u0303", size=size, fill=fill, family="serif", italic=True)
        return
    c.text(x, y, "x", size=size, fill=fill, family="serif", italic=True)
    d = (f"M {x + w * 0.04:.2f} {y - size * 0.50:.2f} "
         f"L {x + w * 0.50:.2f} {y - size * 0.71:.2f} "
         f"L {x + w * 0.96:.2f} {y - size * 0.50:.2f}")
    c.path(d, stroke=fill, sw=max(0.9, size * 0.075), cap="round", join="round")


def _normbar(c, x, y, size, fill):
    for dx in (0.0, size * 0.15):
        c.line(x + dx + 0.4, y - size * 0.66, x + dx + 0.4, y + size * 0.02,
               stroke=fill, sw=max(0.9, size * 0.065))


def rich(c, x, y, runs, size=11.5, fill=P["ink"], anchor="start"):
    """Lay out mixed runs; returns the total width."""
    widths = []
    for s, k in runs:
        if k in ("h", "t"):
            widths.append(size * 0.86)
        elif k == "b":
            widths.append(size * 0.30)
        elif k == "m":
            widths.append(tw(s, size, "serif"))
        else:
            widths.append(tw(s, size, "sans"))
    total = sum(widths)
    cx = x - total / 2 if anchor == "middle" else (x - total if anchor == "end" else x)
    for (s, k), w in zip(runs, widths):
        if k in ("h", "t"):
            _xmark(c, cx, y, size, fill, "hat" if k == "h" else "tilde")
        elif k == "b":
            _normbar(c, cx, y, size, fill)
        else:
            c.text(cx, y, s, size=size, fill=fill,
                   family="serif" if k == "m" else "sans", italic=(k == "m"))
        cx += w
    return total


Z16 = [0.30, 0.74, 0.52, 0.16, 0.86, 0.40, 0.64, 0.22,
       0.68, 0.34, 0.90, 0.48, 0.26, 0.58, 0.76, 0.12]


# ---------------------------------------------------------------------------
# 10 — autoencoder reconstruction
# ---------------------------------------------------------------------------

def f10():
    c = Canvas(960, 460)
    G = glyph(28)
    R = recon_img(G)

    IMW = 144
    yi = 88
    cy = yi + IMW / 2                     # 160
    x0 = 99

    c.text(x0, 34, "① 输入本身就是监督信号：让输出复现输入", size=11.5,
           fill=P["ink2"], weight="600")

    # ---- input image ----
    img(c, x0, yi, IMW, G)
    c.text(x0 + 72, 68, "x ∈ R⁷⁸⁴", size=11.5, fill=P["ink"], anchor="middle",
           family="serif", italic=True)
    c.text(x0 + 72, 82, "输入：28 × 28 灰度图", size=9.5, fill=P["muted"],
           anchor="middle")
    ar(c, x0 + 144, cy, x0 + 186, cy)

    # ---- encoder ----
    ex = x0 + 190
    funnel(c, ex, 74, 124, 172, narrow=0.66)
    c.text(ex + 62, cy - 2, "encoder", size=12.5, fill=P["blue"], anchor="middle",
           weight="600")
    c.mtext(ex + 62, cy + 16, "f_φ", size=12, fill=P["blue2"], anchor="middle")
    ar(c, ex + 124, cy, ex + 166, cy)

    # ---- bottleneck ----
    lx = ex + 178
    latent(c, lx, 94, Z16, w=22, cell=8.2)
    c.text(lx + 11, 70, "bottleneck", size=9.5, fill=P["violet"], anchor="middle",
           weight="600")
    c.text(lx + 11, 250, "z ∈ R¹⁶", size=11, fill=P["violet"], anchor="middle",
           family="serif", italic=True)
    ar(c, lx + 22, cy, lx + 64, cy)

    # ---- decoder ----
    dx = lx + 68
    funnel(c, dx, 74, 124, 172, narrow=0.66, flip=True, fill=P["tealL"],
           stroke=P["tealM"])
    c.text(dx + 62, cy - 2, "decoder", size=12.5, fill=P["teal"], anchor="middle",
           weight="600")
    c.mtext(dx + 62, cy + 16, "g_θ", size=12, fill=P["teal2"], anchor="middle")
    ar(c, dx + 124, cy, dx + 166, cy)

    # ---- reconstruction ----
    ox = dx + 170
    img(c, ox, yi, IMW, R)
    rich(c, ox + 72, 68, [("", "h"), ("\u00A0∈ R⁷⁸⁴", "m")], size=11.5,
         fill=P["ink"], anchor="middle")
    c.text(ox + 72, 82, "重建：28 × 28 灰度图", size=9.5, fill=P["muted"],
           anchor="middle")

    # ---- loss bracket ----
    yb = 294
    c.line(x0 + 72, 236, x0 + 72, yb, stroke=P["red2"], sw=1)
    c.line(ox + 72, 236, ox + 72, yb, stroke=P["red2"], sw=1)
    c.arrow(x0 + 72, yb, ox + 72, yb, color=P["red"], sw=1.3, head=6, start_head=True)
    lw = rich(c, x0 + 72, 318, [("重建损失  ", "s"), ("", "b"), ("x − ", "m"),
                                ("", "h"), ("", "b"), ("²", "m")],
              size=11.5, fill=P["red"])
    c.text(x0 + 72 + lw + 18, 318,
           "逐像素平方误差，越小越好；梯度只回传到编码器与解码器的参数 φ、θ",
           size=10.5, fill=P["red2"])

    # ---- notes ----
    notes = [
        "自监督：目标由输入本身给出，不需要任何人工标注。",
        "瓶颈限制可用的“带宽”（784 → 16 → 784）：模型只能保留笔画形状、位置、粗细这类跨样本都成立的"
        "共同结构，丢掉无关细节。",
        "动机与 PCA 相通——都在找低维子空间；区别是 AE 的编码器与解码器是非线性映射，能贴合弯曲的流形。",
        "示意：图为手写数字 28 × 28 灰度图的合成结果，灰度越深表示笔画越实。",
    ]
    for i, s in enumerate(notes):
        c.text(x0, 352 + i * 22, s, size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 11 — denoising autoencoder
# ---------------------------------------------------------------------------

def f11():
    c = Canvas(960, 430)
    G = glyph(28)
    N = noisy(G)
    R = _blur(G, 1, 1.04)

    IMW = 96
    yi = 100
    cy = yi + IMW / 2                     # 148

    c.text(48, 34, "① 训练时把输入弄脏，目标仍是干净图", size=11.5,
           fill=P["ink2"], weight="600")

    # ---- clean input ----
    img(c, 48, yi, IMW, G)
    c.text(96, 216, "x · 干净图", size=10.5, fill=P["ink2"], anchor="middle")
    ar(c, 144, cy, 178, cy)

    # ---- corruption node ----
    rnd = random.Random(5)
    for _ in range(11):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(19, 27)
        c.circle(191 + r * math.cos(a), cy + r * math.sin(a),
                 rnd.uniform(0.9, 1.8), fill=P["red2"])
    c.circle(191, cy, 12, fill=P["redL"], stroke=P["red"], sw=1)
    c.text(191, cy + 4.4, "+", size=15, fill=P["red"], anchor="middle")
    c.text(191, 217, "加噪", size=9.5, fill=P["red"], anchor="middle")
    ar(c, 204, cy, 234, cy)

    # ---- noisy input ----
    img(c, 238, yi, IMW, N)
    rich(c, 286, 216, [("", "t"), ("\u00A0带噪图", "s")], size=10.5,
         fill=P["ink2"], anchor="middle")
    ar(c, 334, cy, 366, cy)

    # ---- encoder / decoder ----
    funnel(c, 370, 92, 86, 112, narrow=0.60)
    c.text(413, cy - 2, "encoder", size=11.5, fill=P["blue"], anchor="middle",
           weight="600")
    c.mtext(413, cy + 14, "f_φ", size=10.5, fill=P["blue2"], anchor="middle")
    ar(c, 456, cy, 486, cy)

    latent(c, 490, yi, Z16, w=16, cell=6.0)
    c.text(498, 216, "z", size=11, fill=P["violet"], anchor="middle",
           family="serif", italic=True)
    ar(c, 506, cy, 536, cy)

    funnel(c, 540, 92, 86, 112, narrow=0.60, flip=True, fill=P["tealL"],
           stroke=P["tealM"])
    c.text(583, cy - 2, "decoder", size=11.5, fill=P["teal"], anchor="middle",
           weight="600")
    c.mtext(583, cy + 14, "g_θ", size=10.5, fill=P["teal2"], anchor="middle")
    ar(c, 626, cy, 656, cy)

    # ---- reconstruction vs target ----
    img(c, 660, yi, IMW, R)
    rich(c, 708, 216, [("", "h"), ("\u00A0重建", "s")], size=10.5,
         fill=P["teal"], anchor="middle")

    c.arrow(760, cy, 816, cy, color=P["red"], sw=1.3, head=6, start_head=True)
    c.text(788, 176, "重建损失", size=9.5, fill=P["red"], anchor="middle")
    rich(c, 788, 192, [("", "b"), ("x", "m"), (" − ", "m"), ("", "h"),
                       ("", "b"), ("²", "m")], size=9.5, fill=P["red"],
         anchor="middle")

    img(c, 820, yi, IMW, G, border=P["red"])
    c.text(868, 216, "目标：干净 x", size=10.5, fill=P["red"], anchor="middle")

    # ---- bottom ----
    c.text(48, 262, "扰动形式：高斯噪声 · 随机遮挡 / cutout · 模糊 · 椒盐噪点 · 像素丢弃",
           size=10.5, fill=P["ink2"])
    c.text(48, 300,
           "如果只要求输出接近输入，网络可能退化成恒等映射；输入先被破坏，“抄近路”被堵住，"
           "模型必须学会去掉扰动。", size=10.8, fill=P["muted"])
    c.text(48, 322,
           "要恢复被遮挡或模糊的内容，模型必须利用图像中稳定的结构（笔画走向、部件的相对位置）——"
           "这正是有用的表示。", size=10.8, fill=P["muted"])
    c.text(48, 344,
           "因此去噪自编码器本身就是一种自监督预训练方式；MAE、BERT 的掩码重建都可以看作它的推广。",
           size=10.8, fill=P["muted"])
    c.text(48, 366,
           "示意：扰动用逐像素高斯噪声表示；实际训练中还会叠加随机遮挡、模糊等更强的退化。",
           size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 12 — masked autoencoder (MAE)
# ---------------------------------------------------------------------------

def f12():
    c = Canvas(960, 460)
    G = glyph(28)
    R = recon_img(G)

    # 8x8 patch mask: 16 of 64 patches visible (25 %)
    vis = set(random.Random(11).sample(range(64), 16))

    # what the decoder outputs: crisp inside the visible patches, soft elsewhere
    soft = _blur(G, 1, 1.12)
    RC = [[G[i][j] if ((i * 8 // 28) * 8 + (j * 8 // 28)) in vis else soft[i][j]
           for j in range(28)] for i in range(28)]

    IMW = 120
    yi = 100
    cy = yi + IMW / 2                     # 160
    ps = IMW / 8                          # 15 px per patch

    c.text(44, 32, "① 遮住大部分 patch，让模型从残缺输入里重建", size=11.5,
           fill=P["ink2"], weight="600")

    # ---- 1. masked input --------------------------------------------------
    img(c, 44, yi, IMW, G, grid=True)
    for k in range(64):
        i, j = divmod(k, 8)
        x, y = 44 + j * ps, yi + i * ps
        if k in vis:
            c.rect(x, y, ps, ps, fill=P["blue"], stroke=P["blue"], sw=0.6,
                   opacity=0.09)
            c.rect(x + 0.6, y + 0.6, ps - 1.2, ps - 1.2, fill="none",
                   stroke=P["blue2"], sw=0.9)
        else:
            c.rect(x, y, ps, ps, fill="#7f8c98", stroke="#727f8b", sw=0.6)

    # ---- 2. visible tokens ------------------------------------------------
    tx1 = 204
    c.text(tx1 + 48, 100, "可见 patch → token", size=9.5, fill=P["blue"],
           anchor="middle")
    for k in range(64):
        i, j = divmod(k, 8)
        x, y = tx1 + j * 12, 112 + i * 12
        if k in vis:
            c.rect(x + 0.8, y + 0.8, 10.4, 10.4, fill=P["blueL"],
                   stroke=P["blue2"], sw=0.9, rx=2)
        else:
            c.rect(x + 0.8, y + 0.8, 10.4, 10.4, fill=P["white"],
                   stroke=P["rule"], sw=0.6, rx=2, dash="2 2")

    # ---- 3. encoder -------------------------------------------------------
    ex = 340
    block(c, ex, 102, 120, 116, "encoder", "只处理可见 token", fill=P["blueL"],
          stroke=P["blueM"], color=P["blue"], color2=P["blue"], rx=6)

    # ---- 4. encoded + mask tokens -----------------------------------------
    tx2 = 500
    c.text(tx2 + 48, 100, "16 编码 + 48 mask token", size=9.5, fill=P["violet"],
           anchor="middle")
    for k in range(64):
        i, j = divmod(k, 8)
        x, y = tx2 + j * 12, 112 + i * 12
        if k in vis:
            c.rect(x + 0.8, y + 0.8, 10.4, 10.4, fill=P["blueM"],
                   stroke=P["blue"], sw=0.9, rx=2)
        else:
            c.rect(x + 0.8, y + 0.8, 10.4, 10.4, fill="#e4e9ee",
                   stroke="#b9c4ce", sw=0.6, rx=2, dash="2 2")

    # ---- 5. decoder -------------------------------------------------------
    dx = 636
    block(c, dx, 102, 120, 116, "decoder", "补位置、还原全部 patch",
          fill=P["tealL"], stroke=P["tealM"], color=P["teal"], color2=P["teal"],
          rx=6)

    # ---- 6. reconstruction with loss marks ---------------------------------
    ox = 796
    img(c, ox, yi, IMW, RC, grid=True)
    for k in range(64):
        i, j = divmod(k, 8)
        if k not in vis:
            c.circle(ox + (j + 0.5) * ps, yi + (i + 0.5) * ps, 1.0,
                     fill=P["red"], opacity=0.5)

    # ---- arrows -----------------------------------------------------------
    ar(c, 164, cy, 200, cy)
    ar(c, 300, cy, 336, cy)
    ar(c, 460, cy, 496, cy)
    ar(c, 596, cy, 632, cy)
    ar(c, 756, cy, 792, cy)

    # ---- labels -----------------------------------------------------------
    lab = [
        (104, "输入 x：随机遮住 75%", P["ink2"]),
        (252, "16 个 token（25%）", P["blue"]),
        (400, "只看这 16 个", P["blue"]),
        (548, "64 个位置全部到位", P["violet"]),
        (696, "轻量解码", P["teal"]),
    ]
    for x, s, col in lab:
        c.text(x, 240, s, size=9.5, fill=col, anchor="middle")
    rich(c, 856, 240, [("重建 ", "s"), ("", "h"), ("：64 个 patch", "s")],
         size=9.5, fill=P["teal"], anchor="middle")

    # ---- bottom -----------------------------------------------------------
    c.circle(48, 278, 2.2, fill=P["red"])
    c.text(56, 281,
           "红色小点 = 被遮住的位置：损失只在这 48 个 patch 上算，可见的 16 个 patch 不计入。",
           size=10.2, fill=P["red2"])
    c.text(44, 318,
           "原图像是已知的：被遮掉的像素本身就是监督信号，不需要任何标注。"
           "编码器只看 25% 的可见 token，计算量大幅下降。", size=10.8, fill=P["muted"])
    c.text(44, 342,
           "遮住比例越高，任务越难，模型越不能靠局部插值蒙混，学到的表示越偏语义；"
           "75% 是 MAE 的常见设定。", size=10.8, fill=P["muted"])
    c.text(44, 366,
           "解码器很轻，只在预训练时使用；预训练结束后通常只保留编码器，再接下游任务。",
           size=10.8, fill=P["muted"])
    c.text(44, 390,
           "patch 的顺序被打乱，所以解码器必须显式拿到位置编码，才知道每一块该放回哪里。",
           size=10.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 13 — variational autoencoder
# ---------------------------------------------------------------------------

def f13():
    c = Canvas(960, 520)
    G = glyph(28)

    c.text(40, 32, "① 编码器输出一个分布，采样之后才进解码器", size=11.5,
           fill=P["ink2"], weight="600")

    # ---- input ----
    img(c, 44, 92, 64, G)
    c.text(76, 172, "输入 x", size=9.5, fill=P["muted"], anchor="middle")
    ar(c, 108, 124, 134, 124)

    # ---- encoder ----
    c.rect(138, 86, 118, 76, fill=P["blueL"], stroke=P["blueM"], rx=6)
    c.text(197, 116, "encoder", size=12.8, fill=P["blue"], anchor="middle",
           weight="600")
    c.mtext(197, 136, "q_φ(z|x)", size=10.5, fill=P["blue2"], anchor="middle")

    # ---- split into mu / sigma ----
    ar(c, 256, 124, 292, 124)
    c.line(292, 102, 292, 128, stroke=P["muted"], sw=1.2)
    ar(c, 292, 102, 316, 102)
    ar(c, 292, 128, 316, 128)
    c.text(322, 105, "μ(x)", size=9.5, fill=P["violet"], anchor="start")
    c.text(322, 131, "σ(x)", size=9.5, fill=P["violet"], anchor="start")

    latent_h(c, 352, 96, Z16[:8], h=12)
    latent_h(c, 352, 122, Z16[8:], h=12)

    # ---- reparameterisation -----------------------------------------------
    c.arrow(470, 102, 522, 102, color=P["violet"], sw=1.3, head=5)
    c.arrow(470, 128, 482, 128, color=P["violet"], sw=1.3, head=5)

    c.circle(490, 128, 8, fill=P["violetL"], stroke=P["violet"], sw=1)
    c.text(490, 131.6, "⊙", size=10, fill=P["violet"], anchor="middle")
    c.circle(530, 102, 8, fill=P["violetL"], stroke=P["violet"], sw=1)
    c.text(530, 105.6, "⊕", size=10, fill=P["violet"], anchor="middle")

    c.rect(452, 152, 92, 17, fill=P["violetL"], stroke=P["violetM"], rx=8)
    c.text(498, 164, "ε ~ N(0, I)", size=9.5, fill=P["violet"], anchor="middle")
    c.arrow(490, 152, 490, 137, color=P["violet"], sw=1.2, head=5)

    c.polyline([(498, 128), (530, 128), (530, 111)], stroke=P["violet"], sw=1.2)
    ar(c, 538, 102, 548, 102, color=P["violet"], sw=1.3)

    latent_h(c, 548, 96, Z16[:8], h=12)
    c.text(570, 88, "z", size=11, fill=P["violet"], anchor="middle",
           family="serif", italic=True)
    c.polyline([(590, 102), (602, 102), (602, 124)], stroke=P["muted"], sw=1.2)
    ar(c, 602, 124, 614, 124)

    # ---- decoder ----
    c.rect(616, 86, 118, 76, fill=P["tealL"], stroke=P["tealM"], rx=6)
    c.text(675, 116, "decoder", size=12.8, fill=P["teal"], anchor="middle",
           weight="600")
    c.mtext(675, 136, "p_θ(x|z)", size=10.5, fill=P["teal2"], anchor="middle")
    ar(c, 734, 124, 760, 124)

    img(c, 762, 92, 64, G)
    rich(c, 794, 172, [("重建 ", "s"), ("", "h")], size=9.5, fill=P["teal"],
         anchor="middle")

    # ---- two loss terms ---------------------------------------------------
    brace_h(c, 340, 556, 176, color=P["violetM"], w=6, up=False)
    c.text(384, 202, "KL 项  ", size=10, fill=P["violet"], anchor="start")
    c.mtext(424, 202, "D_{KL}(q(z|x) ‖ p(z))", size=10, fill=P["violet"])
    c.text(448, 218, "把每个输入的编码分布拉向先验", size=9.5, fill=P["muted"],
           anchor="middle")

    brace_h(c, 736, 850, 176, color=P["tealM"], w=6, up=False)
    c.text(793, 202, "重建项  −log p(x|z)", size=10, fill=P["teal"],
           anchor="middle")
    c.text(793, 218, "解码器把 z 还原成输入", size=9.5, fill=P["muted"],
           anchor="middle")

    # ---- latent-space panel -----------------------------------------------
    sx, sy, sw_, sh_ = 470, 272, 200, 200
    c.text(sx + sw_ / 2, 256, "潜在空间（2 维示意）", size=10.5, fill=P["ink2"],
           anchor="middle", weight="600")

    def PX(v):
        return sx + (v + 3.4) / 6.8 * sw_

    def PY(v):
        return sy + sh_ - (v + 3.4) / 6.8 * sh_

    c.line(sx, sy + sh_, sx + sw_, sy + sh_, stroke=P["ink2"], sw=1)
    c.line(sx, sy, sx, sy + sh_, stroke=P["ink2"], sw=1)
    for v in (-2, 0, 2):
        c.text(PX(v), sy + sh_ + 14, f"{v}", size=9, fill=P["faint"],
               anchor="middle")
        c.text(sx - 6, PY(v) + 3, f"{v}", size=9, fill=P["faint"], anchor="end")
    c.text(sx + sw_ / 2, sy + sh_ + 30, "z₁", size=10, fill=P["muted"],
           anchor="middle", family="serif", italic=True)
    c.text(sx - 34, sy + sh_ / 2, "z₂", size=10, fill=P["muted"], anchor="middle",
           family="serif", italic=True, rotate=(-90, sx - 34, sy + sh_ / 2))

    ox_, oy_ = PX(0), PY(0)
    r1 = sw_ / 6.8
    c.poly(circle_pts(ox_, oy_, r1)[:-1], fill=P["violetL"], opacity=0.55)
    for k in (1, 2, 3):
        c.polyline(circle_pts(ox_, oy_, r1 * k), stroke=P["violet2"], sw=1,
                   dash="3 3", opacity=0.8)

    rnd = random.Random(4)
    for cx_, cy_ in ((-1.55, 1.25), (1.45, 1.10), (-1.20, -1.35), (1.50, -1.15)):
        for _ in range(13):
            px = PX(cx_ + rnd.gauss(0, 0.42))
            py = PY(cy_ + rnd.gauss(0, 0.42))
            c.circle(px, py, 2.0, fill=P["violet"], opacity=0.5)

    # one encoded sample and its q(z|x)
    qx, qy = PX(-1.42), PY(1.42)
    c.polyline(circle_pts(qx, qy, 13), stroke=P["blue"], sw=1.1, dash="2.5 2.5")
    c.circle(qx, qy, 2.6, fill=P["blue"])
    c.text(qx - 12, qy - 15, "q(z|x)", size=9.5, fill=P["blue"], anchor="end")

    # sample from the prior -> decode (arrow leaves the plot toward the legend)
    px0, py0 = PX(0.95), PY(-0.85)
    c.circle(px0, py0, 3.6, fill=P["white"], stroke=P["teal"], sw=1.4)
    c.arrow(px0 + 6, py0 - 2, 690, 408, color=P["teal"], sw=1.2, head=5)

    # ---- legend -----------------------------------------------------------
    lx = 700
    ly = [300, 336, 372, 408]
    c.polyline(circle_pts(lx + 6, ly[0] - 4, 6), stroke=P["violet2"], sw=1,
               dash="2.5 2.5")
    c.text(lx + 18, ly[0], "先验 N(0, I)：1σ / 2σ / 3σ 的等高线", size=9.5,
           fill=P["ink2"])
    c.circle(lx + 6, ly[1] - 4, 2.2, fill=P["violet"], opacity=0.6)
    c.text(lx + 18, ly[1], "编码后的样本点，同类成簇", size=9.5, fill=P["ink2"])
    c.polyline(circle_pts(lx + 6, ly[2] - 4, 5.5), stroke=P["blue"], sw=1.1,
               dash="2 2")
    c.text(lx + 18, ly[2], "单个输入的编码分布 q(z|x)", size=9.5, fill=P["ink2"])
    c.circle(lx + 6, ly[3] - 4, 3.2, fill=P["white"], stroke=P["teal"], sw=1.3)
    c.text(lx + 18, ly[3], "从先验里采样 z，解码即得新样本", size=9.5,
           fill=P["teal"])

    # ---- notes ------------------------------------------------------------
    note_lines = [
        "KL 项把每个输入的 q(z|x) 拉向先验，潜在空间才连续、可采样。",
        "相近的 z 解码出相近的样本，圆心附近也不会生成怪东西。",
        "重参数化把随机性放到 ε 上：z = μ + σ ⊙ ε，μ、σ 仍能收到梯度——",
        "否则“采样”这一步不可导，编码器就没法用反向传播训练。",
        "训练时两项加权求和；KL 权重太小会退化成普通自编码器。",
    ]
    for i, s in enumerate(note_lines):
        c.text(40, 300 + i * 24, s, size=10.5, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 14 — GAN: generator vs discriminator
# ---------------------------------------------------------------------------

def _shift(vals, dx, dy):
    n = len(vals)
    return [[vals[i - dy][j - dx] if 0 <= i - dy < n and 0 <= j - dx < n else 0.0
             for j in range(n)] for i in range(n)]


def f14():
    c = Canvas(960, 480)
    G = glyph(28)

    c.text(40, 32, "一个造样本、一个判真假：两条训练路径互相博弈", size=11.5,
           fill=P["ink2"], weight="600")

    # ---- z -> G -> x~ -----------------------------------------------------
    latent(c, 52, 150, Z16[:8], w=18, cell=10)
    c.text(61, 142, "z ~ N(0, I)", size=9.5, fill=P["violet"], anchor="middle")
    ar(c, 70, 190, 100, 190)

    c.rect(104, 140, 130, 100, fill=P["violetL"], stroke=P["violetM"], rx=6)
    c.text(169, 184, "生成器", size=12.5, fill=P["violet"], anchor="middle",
           weight="600")
    c.mtext(169, 204, "G_θ(z)", size=10.5, fill=P["violet2"], anchor="middle")
    ar(c, 234, 190, 262, 190)

    img(c, 266, 148, 84, G, border=P["violetM"])
    rich(c, 308, 250, [("生成样本 ", "s"), ("", "t")], size=9.5,
         fill=P["violet"], anchor="middle")

    # ---- real batch -------------------------------------------------------
    for i, dx in enumerate((-2, 0, 2)):
        img(c, 614 + i * 54, 48, 46, _shift(G, dx, i - 1), grid=False,
            border=P["rule"], rx=2)
    c.text(690, 38, "真实数据 x（一小批）", size=9.5, fill=P["ink2"],
           anchor="middle")
    brace_h(c, 618, 758, 100, color=P["rule"], w=5, up=False)
    c.arrow(690, 106, 690, 126, color=P["muted"], sw=1.3, head=5)

    # ---- fake path into D -------------------------------------------------
    c.arrow(350, 190, 614, 190, color=P["muted"], sw=1.3, head=6)
    tag(c, 520, 176, "假 → 0", color=P["red"], bg=P["redL"], size=9, h=15)

    # ---- discriminator ----------------------------------------------------
    c.rect(614, 124, 152, 132, fill="none", stroke=P["blue"], rx=8, sw=1.1,
           dash="4 3")
    c.rect(620, 130, 140, 120, fill=P["orangeL"], stroke=P["orangeM"], rx=6)
    c.text(690, 184, "判别器", size=12.5, fill=P["orange"], anchor="middle",
           weight="600")
    c.mtext(690, 204, "D_ψ(x)", size=10.5, fill=P["orange2"], anchor="middle")
    tag(c, 722, 114, "真 → 1", color=P["green"], bg=P["greenL"], size=9, h=15)

    # ---- score ------------------------------------------------------------
    ar(c, 760, 190, 786, 190, color=P["orange"], sw=1.3)
    c.rect(790, 140, 140, 100, fill=P["white"], stroke=P["rule"], rx=6)
    c.text(860, 158, "D 的输出", size=9.5, fill=P["muted"], anchor="middle")
    c.rect(800, 168, 120, 26, fill=P["greenL"], stroke=P["greenM"], rx=4)
    c.text(810, 185, "x → 0.93 真", size=9.5, fill=P["green"], weight="600")
    c.rect(800, 200, 120, 26, fill=P["redL"], stroke=P["redM"], rx=4)
    rich(c, 810, 217, [("", "t"), (" → 0.07 假", "s")], size=9.5,
         fill=P["red"])

    # ---- (2) gradient path back to G --------------------------------------
    c.polyline([(690, 256), (690, 292), (169, 292), (169, 250)],
               stroke=P["blue"], sw=1.3, dash="5 4")
    c.arrow(169, 260, 169, 244, color=P["blue"], sw=1.3, head=5)
    c.rect(424, 283, 18, 18, fill=P["white"], stroke=P["blue"], rx=9, sw=1)
    c.text(433, 296.5, "②", size=9.5, fill=P["blue"], anchor="middle")

    # ---- (1)(2) legend ----------------------------------------------------
    tag(c, 44, 316, "1", color=P["green"], bg=P["greenL"], size=9, h=15)
    tag(c, 66, 316, "0", color=P["red"], bg=P["redL"], size=9, h=15)
    c.text(88, 320, "① 更新 D：真实样本标 1、生成样本标 0，让 D 学会分辨",
           size=10, fill=P["ink2"])

    c.polyline([(44, 340), (66, 340)], stroke=P["blue"], sw=1.3, dash="5 4")
    c.arrow(56, 340, 68, 340, color=P["blue"], sw=1.3, head=4.5)
    c.text(88, 344, "② 更新 G：固定 D（虚线框），让 D(G(z)) 更大——梯度穿过 D 回到 G",
           size=10, fill=P["ink2"])

    # ---- failure modes ----------------------------------------------------
    c.text(40, 384, "常见失败模式", size=10.5, fill=P["ink2"], weight="600")
    fm = [
        (40, 408, "模式崩溃：G 只生成少数几类样本，多样性丢失"),
        (40, 432, "梯度消失：D 太强时 G 几乎收不到有效梯度，训练停滞"),
        (490, 408, "训练震荡：G 与 D 此消彼长，损失反复摆动、不收敛"),
        (490, 432, "对超参敏感：学习率、容量、更新比例都要仔细调"),
    ]
    for x, y, s in fm:
        c.circle(x + 3, y - 3.4, 2, fill=P["red"], opacity=0.55)
        c.text(x + 11, y, s, size=10, fill=P["muted"])
    return c


FIGURES = {
    "10_autoencoder-reconstruction": f10,
    "11_denoising-autoencoder": f11,
    "12_masked-autoencoder-mae": f12,
    "13_vae-latent-sampling": f13,
    "14_gan-generator-discriminator": f14,
}
