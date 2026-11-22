"""第 8.1–8.4 节：AE、去噪 AE、MAE、VAE、GAN、Diffusion、Flow Matching。"""
import math

from svgkit import *


# ---------------------------------------------------------------------------
# 公共小工具
# ---------------------------------------------------------------------------
def digit(d, n=28, width=1.5):
    return raster_strokes(digit_strokes(d), n, width, 0.9)


def noisy(img, sigma, seed):
    r = RNG(seed)
    return [[max(0.0, min(1.0, v + sigma * r.normal())) for v in row] for row in img]


def show(s, x, y, size, img, label=None, sub=None, stroke=BORDER, sw=1.2, mode="L", lsize=14.5):
    s.image(x, y, size, size, png_uri(img, mode))
    s.rect(x, y, size, size, fill="none", stroke=stroke, sw=sw, rx=3)
    if label:
        s.text(x + size / 2, y + size + 20, label, size=lsize, weight="bold")
    if sub:
        s.text(x + size / 2, y + size + 42, sub, size=12.5, color=MUTED)


def trapezoid(s, x0, x1, cy, h0, h1, key, label, sub=None):
    d = (f"M{x0:.1f},{cy - h0 / 2:.1f} L{x1:.1f},{cy - h1 / 2:.1f} L{x1:.1f},{cy + h1 / 2:.1f} "
         f"L{x0:.1f},{cy + h0 / 2:.1f} Z")
    s.path(d, stroke=main(key), sw=1.5, fill=light(key))
    cx = (x0 + x1) / 2
    if sub:
        s.text(cx, cy - 11, label, size=15, weight="bold")
        s.text(cx, cy + 12, sub, size=12.5, color=MUTED)
    else:
        s.text(cx, cy, label, size=15, weight="bold")


def latent_grid(s, x, y, cell=18, seed=3, key="attn"):
    r = RNG(seed)
    vals = [[r.u() for _ in range(4)] for _ in range(4)]
    s.grid(x, y, 4, 4, cell, fills=lambda i, j: heat(0.15 + 0.85 * vals[i][j], key), stroke=WHITE, sw=1.5)
    s.rect(x, y, 4 * cell, 4 * cell, fill="none", stroke=main(key), sw=1.3)


def lock(s, x, y, color=MUTED):
    """小锁图标（左上角在 x,y，约 14×16）。"""
    s.path(f"M{x + 3:.1f},{y + 7:.1f} L{x + 3:.1f},{y + 4:.1f} A4,4 0 0 1 {x + 11:.1f},{y + 4:.1f} L{x + 11:.1f},{y + 7:.1f}",
           stroke=color, sw=1.6)
    s.rect(x, y + 7, 14, 10, fill=color, rx=2)


# ---------------------------------------------------------------------------
# 10 Autoencoder
# ---------------------------------------------------------------------------
def fig10():
    s = SVG(940, 370, "自编码器：压缩再重建", "编码器把 784 维图像压到 16 维潜在向量，解码器再重建；用重建误差训练。")
    x_img = digit(3)
    rec = blur(x_img, 1)
    cy = 150
    show(s, 40, cy - 70, 140, x_img, "输入 $x$", "28×28 = 784 个数")
    s.harrow(192, 222, cy, color=INK)
    trapezoid(s, 230, 390, cy, 200, 76, "k", "编码器 $f$_{φ}", "784 → 128 → 16")
    s.harrow(396, 424, cy, color=INK)
    latent_grid(s, 432, cy - 36)
    s.text(468, cy - 58, "潜在向量 $z$", size=14.5, weight="bold", color=main("attn"))
    s.text(472, cy + 56, "只有 16 个数（瓶颈）", size=12.5, color=MUTED)
    s.text(472, cy + 76, "迫使模型只保留主要结构", size=12.5, color=MUTED)
    s.harrow(512, 540, cy, color=INK)
    trapezoid(s, 548, 708, cy, 76, 200, "q", "解码器 $g$_{θ}", "16 → 128 → 784")
    s.harrow(714, 744, cy, color=INK)
    show(s, 752, cy - 70, 140, rec, "重建 $x̂$", "还原出主要笔画")

    # 重建损失
    yl = 300
    s.path(f"M110,276 L110,{yl} L340,{yl}", stroke=main("loss"), sw=1.6, dash="6 4")
    s.path(f"M822,276 L822,{yl} L600,{yl}", stroke=main("loss"), sw=1.6, dash="6 4")
    s.box(340, yl - 22, 260, 44, "重建损失  ‖$x$ − $x̂$‖^{2}", key="loss", size=15, weight="bold")
    s.text(470, yl + 46, "编码器和解码器一起训练，让重建误差尽量小 —— 输入本身就是答案，不需要标签。",
           size=13, color=MUTED)
    s.save(OUT / "10_autoencoder-reconstruction.svg")


# ---------------------------------------------------------------------------
# 11 去噪自编码器
# ---------------------------------------------------------------------------
def fig11():
    s = SVG(1040, 420, "去噪自编码器", "输入是加噪图像，训练目标却是干净图像。")
    x_img = digit(5)
    xt = noisy(x_img, 0.42, 11)
    rec = blur(x_img, 1)
    cy = 140
    sz = 128
    show(s, 40, cy - sz / 2, sz, x_img, "干净图像 $x$", stroke=main("v"), sw=2)
    s.harrow(178, 268, cy, color=INK)
    s.text(223, cy - 18, "+ 随机噪声", size=13.5, weight="bold")
    show(s, 276, cy - sz / 2, sz, xt, "受扰动的 $x̃$", "模型的输入")
    s.harrow(414, 444, cy, color=INK)
    trapezoid(s, 452, 552, cy, 150, 60, "k", "编码器")
    trapezoid(s, 552, 652, cy, 60, 150, "q", "解码器")
    s.harrow(660, 690, cy, color=INK)
    show(s, 698, cy - sz / 2, sz, rec, "输出 $x̂$", "去掉了噪声")

    # 损失框
    lx, ly = 870, cy
    s.box(860, cy - 34, 150, 68, "‖$x$ − $x̂$‖^{2}", key="loss", sub="重建损失", size=16)
    s.harrow(830, 856, cy, color=main("loss"), sw=1.6)
    # 目标：干净 x（底部绕行）
    yb = 310
    s.path(f"M104,{cy + sz / 2 + 32} L104,{yb} L935,{yb} L935,{cy + 38}", stroke=main("v"), sw=2.2,
           extra=f'marker-end="url(#{s._marker(main("v"), 1.1)})"')
    s.rect(370, yb - 16, 300, 32, fill=WHITE, stroke=main("v"), sw=1.3, rx=16)
    s.text(520, yb, "训练目标是干净的 $x$ ✓", size=14.5, weight="bold", color=main("v"))
    # x̃ 不是目标
    s.path(f"M340,{cy + sz / 2 + 52} L340,{yb - 40} L860,{yb - 40} L900,{cy + 38}", stroke=LINE, sw=1.4, dash="4 4")
    xm, ym = 600, yb - 40
    s.line(xm - 9, ym - 9, xm + 9, ym + 9, color=main("loss"), sw=2.6)
    s.line(xm - 9, ym + 9, xm + 9, ym - 9, color=main("loss"), sw=2.6)
    s.text(xm + 18, ym - 14, "不是去拟合 $x̃$", size=13, color=main("loss"), anchor="start")
    s.text(520, 370, "噪声每次都不一样，干净结构却是稳定的：模型只能靠学到“笔画该长什么样”来恢复图像。",
           size=13, color=MUTED)
    s.save(OUT / "11_denoising-autoencoder.svg")


# ---------------------------------------------------------------------------
# 12 MAE
# ---------------------------------------------------------------------------
def scene(n=64):
    """简单彩色场景：天空、太阳、山、房子。返回 n×n RGB。"""
    img = []
    for i in range(n):
        row = []
        for j in range(n):
            y, x = i / n, j / n
            c = (int(150 + 80 * y), int(200 + 40 * y), 250)  # 天空
            if (x - 0.78) ** 2 + (y - 0.2) ** 2 < 0.011:
                c = (250, 196, 50)
            hill1 = 0.62 - 0.18 * math.exp(-((x - 0.25) / 0.22) ** 2)
            hill2 = 0.68 - 0.12 * math.exp(-((x - 0.75) / 0.25) ** 2)
            if y > hill2:
                c = (96, 170, 96)
            if y > hill1:
                c = (70, 145, 80)
            # 房子
            if 0.5 < x < 0.74 and 0.56 < y < 0.8:
                c = (238, 226, 200)
                if 0.58 < x < 0.65 and 0.66 < y < 0.8:
                    c = (140, 90, 60)
                if 0.68 < x < 0.72 and 0.6 < y < 0.66:
                    c = (120, 170, 220)
            if 0.46 < x < 0.78 and 0.42 < y <= 0.56 and abs(x - 0.62) < (y - 0.42) * 1.15:
                c = (200, 70, 60)
            if y > 0.86:
                c = (90, 150, 80)
            row.append(c)
        img.append(row)
    return img


def blur_rgb(img, r=2):
    n, m = len(img), len(img[0])
    out = []
    for i in range(n):
        row = []
        for j in range(m):
            acc = [0, 0, 0]
            cnt = 0
            for di in range(-r, r + 1):
                for dj in range(-r, r + 1):
                    ii, jj = i + di, j + dj
                    if 0 <= ii < n and 0 <= jj < m:
                        for k in range(3):
                            acc[k] += img[ii][jj][k]
                        cnt += 1
            row.append(tuple(a / cnt for a in acc))
        out.append(row)
    return out


def crop(img, pi, pj, p):
    return [row[pj * p:(pj + 1) * p] for row in img[pi * p:(pi + 1) * p]]


def fig12():
    s = SVG(1100, 380, "掩码自编码器 MAE", "遮住 75% 的 patch，编码器只看可见 patch，解码器在原位置补全，损失只算遮住的部分。")
    n, P = 64, 16
    img = scene(n)
    rec_full = blur_rgb(img, 2)
    visible = {(0, 3), (1, 1), (2, 2), (3, 0)}
    cell, gap = 34, 3
    W = 4 * cell + 3 * gap
    y0 = 112

    def patches(x, y, kind):
        for i in range(4):
            for j in range(4):
                px, py = x + j * (cell + gap), y + i * (cell + gap)
                vis = (i, j) in visible
                if kind == "orig" or (kind == "mask" and vis):
                    s.image(px, py, cell, cell, png_uri(crop(img, i, j, P), "RGB"))
                elif kind == "mask":
                    s.rect(px, py, cell, cell, fill="#C9CDD3", rx=2)
                elif kind == "rec":
                    src = img if vis else rec_full
                    s.image(px, py, cell, cell, png_uri(crop(src, i, j, P), "RGB"))
                    if not vis:
                        s.rect(px + 0.8, py + 0.8, cell - 1.6, cell - 1.6, fill="none", stroke=main("loss"), sw=1.6, rx=2)

    def stage_title(cx, a, b=None):
        s.text(cx, 52, a, size=14.5, weight="bold")
        if b:
            s.text(cx, 74, b, size=12.5, color=MUTED)

    # ① 原图
    x1 = 30
    patches(x1, y0, "orig")
    stage_title(x1 + W / 2, "① 切成 16 个 patch")
    s.harrow(x1 + W + 8, x1 + W + 34, y0 + W / 2, color=INK)
    # ② 遮挡
    x2 = x1 + W + 42
    patches(x2, y0, "mask")
    stage_title(x2 + W / 2, "② 随机遮住 75%", "12 个遮住，4 个可见")
    s.harrow(x2 + W + 8, x2 + W + 34, y0 + W / 2, color=INK)
    # ③ 编码器：只看可见 patch
    x3 = x2 + W + 44
    vis_list = sorted(visible)
    for k, (i, j) in enumerate(vis_list):
        s.image(x3, y0 + k * (cell + 6) + 2, cell, cell, png_uri(crop(img, i, j, P), "RGB"))
    s.harrow(x3 + cell + 6, x3 + cell + 26, y0 + W / 2, color=INK)
    s.box(x3 + cell + 30, y0 - 4, 76, W + 8, "编码器", key="k", size=15)
    for k in range(4):
        yy = y0 + k * (cell + 6) + 2 + cell / 2
        s.harrow(x3 + cell + 110, x3 + cell + 132, yy, color=main("k"), sw=1.2, head=0.8)
        s.rect(x3 + cell + 136, yy - 11, 22, 22, fill=main("k"), rx=4)
    stage_title(x3 + 80, "③ 编码器只处理可见 patch", "计算量只有约 1/4")
    # ④ 解码器输入：原位置 + mask token
    x4 = x3 + cell + 190
    tc, tg = 24, 6
    TW = 4 * tc + 3 * tg
    ty = y0 + (W - TW) / 2
    for i in range(4):
        for j in range(4):
            px, py = x4 + j * (tc + tg), ty + i * (tc + tg)
            if (i, j) in visible:
                s.rect(px, py, tc, tc, fill=main("k"), rx=4)
            else:
                s.rect(px, py, tc, tc, fill="#E5E7EB", stroke="#9CA3AF", sw=1, rx=4)
                s.text(px + tc / 2, py + tc / 2, "M", size=11, color=MUTED, weight="bold")
    stage_title(x4 + TW / 2 + 40, "④ 按原位置补上 mask token", "解码器负责补全")
    s.harrow(x4 + TW + 6, x4 + TW + 26, y0 + W / 2, color=INK)
    s.box(x4 + TW + 30, y0 - 4, 76, W + 8, "解码器", key="q", size=15)
    s.harrow(x4 + TW + 112, x4 + TW + 138, y0 + W / 2, color=INK)
    # ⑤ 重建
    x5 = x4 + TW + 146
    patches(x5, y0, "rec")
    stage_title(x5 + W / 2, "⑤ 重建全部 patch")

    # 图例/说明（一行居中）
    ly = y0 + W + 40
    items = [("vis", "可见 patch 的编码"), ("mask", "mask token：共享的可学习向量"), ("loss", "只在被遮住的 12 个 patch 上算损失")]
    lx = 210
    for kind, txt in items:
        if kind == "vis":
            s.rect(lx, ly - 9, 18, 18, fill=main("k"), rx=4)
        elif kind == "mask":
            s.rect(lx, ly - 9, 18, 18, fill="#E5E7EB", stroke="#9CA3AF", sw=1, rx=4)
        else:
            s.rect(lx, ly - 9, 18, 18, fill="none", stroke=main("loss"), sw=1.8, rx=2)
        s.text(lx + 26, ly, txt, size=13, anchor="start", color=main("loss") if kind == "loss" else MUTED)
        lx += 26 + text_width(txt, 13) + 50
    s.text(550, ly + 44, "要补出被遮住的屋顶、山坡和太阳，模型必须理解“图里通常有什么”——这正是想让编码器学到的表示。",
           size=13, color=MUTED)
    s.save(OUT / "12_masked-autoencoder-mae.svg")


# ---------------------------------------------------------------------------
# 13 VAE
# ---------------------------------------------------------------------------
def fig13():
    s = SVG(1080, 640, "VAE：可以采样的潜在空间", "编码器输出分布，重参数化采样后解码；KL 把编码分布拉向标准正态。")
    x_img = digit(2)
    rec = blur(x_img, 1)
    cy = 132
    sz = 104
    s.panel(20, 16, 1040, 336, "训练：损失 = 重建项 + KL 项", key="k", tag="1")
    show(s, 44, cy - sz / 2, sz, x_img, "输入 $x$")
    s.harrow(156, 180, cy, color=INK)
    trapezoid(s, 186, 300, cy, 120, 60, "k", "编码器")
    # μ σ
    s.arrow([(304, cy - 12), (340, cy - 34)], color=INK, sw=1.4)
    s.arrow([(304, cy + 12), (340, cy + 34)], color=INK, sw=1.4)
    s.box(344, cy - 52, 66, 34, "$μ$($x$)", key="attn", size=15, weight="normal")
    s.box(344, cy + 18, 66, 34, "$σ$($x$)", key="attn", size=15, weight="normal")
    s.text(377, cy, "均值与标准差", size=12, color=MUTED)
    # 重参数化节点
    nx = 500
    s.arrow([(414, cy - 35), (nx - 60, cy - 10)], color=INK, sw=1.4)
    s.arrow([(414, cy + 35), (nx - 60, cy + 10)], color=INK, sw=1.4)
    s.rect(nx - 58, cy - 28, 116, 56, fill=WHITE, stroke=main("attn"), sw=1.8, rx=10)
    s.text(nx, cy - 8, "$z$ = $μ$ + $σ$ ⊙ $ε$", size=14, weight="bold")
    s.text(nx, cy + 13, "重参数化", size=12, color=MUTED)
    # ε 从上方注入
    s.box(nx - 62, 50, 124, 30, "$ε$ ~ 𝒩(0, $I$)", key="gray", size=14, weight="normal", dash="5 3")
    s.varrow(nx, 82, cy - 30, color=MUTED, dash="4 3")
    s.text(nx + 70, 66, "随机性只从这里进入", size=12.5, color=MUTED, anchor="start")
    s.text(nx, cy + 46, "梯度可经 $μ$、$σ$ 传回编码器", size=12.5, color=main("loss"))
    s.harrow(nx + 60, nx + 84, cy, color=INK)
    latent_grid(s, nx + 90, cy - 24, cell=12)
    s.text(nx + 114, cy + 40, "$z$", size=15, weight="bold", color=main("attn"))
    s.harrow(nx + 144, nx + 168, cy, color=INK)
    trapezoid(s, nx + 172, nx + 284, cy, 60, 120, "q", "解码器")
    s.harrow(nx + 290, nx + 314, cy, color=INK)
    show(s, nx + 320, cy - sz / 2, sz, rec, "重建 $x̂$")
    # 两项损失
    ky = 262
    s.box(260, ky - 20, 270, 40, "KL( $q$_{φ}($z$|$x$) ‖ 𝒩(0, $I$) )", key="loss", size=14)
    s.path(f"M377,{cy + 52} L377,{ky - 20}", stroke=main("loss"), sw=1.4, dash="6 4")
    s.text(540, ky, "← 把编码分布拉向标准正态", size=12.5, color=main("loss"), anchor="start")
    ly = 318
    s.path(f"M96,{cy + sz / 2 + 34} L96,{ly} L380,{ly}", stroke=main("loss"), sw=1.4, dash="6 4")
    s.path(f"M{nx + 372},{cy + sz / 2 + 34} L{nx + 372},{ly} L700,{ly}", stroke=main("loss"), sw=1.4, dash="6 4")
    s.box(380, ly - 18, 320, 36, "重建：−log $p$_{θ}($x$ | $z$)", key="loss", size=14)

    # 生成
    gy = 382
    s.panel(20, gy - 12, 330, 248, "生成：直接从先验采样", key="q", tag="2")
    s.box(44, gy + 40, 120, 40, "$z$ ~ 𝒩(0, $I$)", key="attn", size=14.5, weight="normal")
    s.varrow(104, gy + 82, gy + 104, color=main("q"), dash="5 3")
    trapezoid(s, 50, 158, gy + 140, 34, 70, "q", "解码器")
    s.harrow(170, 200, gy + 140, color=main("q"), dash="5 3")
    for k, d in enumerate([3, 8]):
        show(s, 206 + k * 64, gy + 112, 56, digit(d))
    s.text(266, gy + 192, "新样本", size=13.5, weight="bold")
    s.text(185, gy + 220, "不再需要输入图像", size=12.5, color=MUTED)

    # 潜在空间直觉
    def latent_panel(x, y, w, h, vae):
        title = "VAE：编码是一团团分布，铺满先验" if vae else "普通 AE：编码是散落的点，中间有空洞"
        s.panel(x, y, w, h, title, key="attn" if vae else None, size=14)
        cx, cy2 = x + w / 2 - 40, y + h / 2 + 6
        R = 84
        s.circle(cx, cy2, R, fill="none", stroke=MUTED, sw=1.2, dash="5 4")
        s.text(x + w / 2, y + h - 14, "虚线圈：先验 𝒩(0, $I$) 的主要范围", size=12, color=MUTED)
        cols = [main("k"), main("q"), main("v"), main("pink")]
        r = RNG(5 if vae else 9)
        centers = ([(-0.62, -0.35), (0.55, -0.45), (-0.35, 0.5), (0.45, 0.42)] if vae else
                   [(-0.95, -0.6), (0.9, -0.7), (-0.75, 0.85), (1.0, 0.75)])
        for k, (mx, my) in enumerate(centers):
            if vae:
                s.circle(cx + mx * R, cy2 + my * R, 0.55 * R, fill=cols[k], opacity=0.14)
            spread = 0.24 if vae else 0.07
            for _ in range(16):
                px = cx + (mx + spread * r.normal()) * R
                py = cy2 + (my + spread * r.normal()) * R
                s.circle(px, py, 2.6, fill=cols[k], opacity=0.85)
        # 随机采样点
        sx, sy = cx + 0.05 * R, cy2 + 0.02 * R
        s.text(sx, sy, "★", size=22, color=INK)
        ex = x + w - 70
        s.arrow([(sx + 14, sy), (ex - 36, sy)], color=INK, sw=1.4)
        if vae:
            show(s, ex - 30, sy - 30, 60, blur(digit(8), 1), stroke=main("v"), sw=2)
            s.text(ex, sy + 48, "像样的数字", size=12.5, color=main("v"))
        else:
            r2 = RNG(21)
            junk = blur([[max(0, min(1, 0.5 * r2.normal())) ** 2 for _ in range(28)] for _ in range(28)], 1)
            show(s, ex - 30, sy - 30, 60, junk, stroke=main("loss"), sw=2)
            s.text(ex, sy + 48, "解码出乱码", size=12.5, color=main("loss"))
        s.rect(sx - 38, sy + 13, 70, 20, fill=WHITE, rx=4, opacity=0.9)
        s.text(sx - 3, sy + 23, "随机采一点", size=12, color=INK)

    latent_panel(366, gy - 12, 342, 248, False)
    latent_panel(718, gy - 12, 342, 248, True)
    s.save(OUT / "13_vae-latent-sampling.svg")


# ---------------------------------------------------------------------------
# 14 GAN
# ---------------------------------------------------------------------------
def fake_digit(d, seed, amount=0.6):
    """“半成品”生成样本：笔画抖动 + 噪声。"""
    r = RNG(seed)
    st = [[(x + 0.05 * amount * r.normal(), y + 0.05 * amount * r.normal()) for x, y in stroke]
          for stroke in digit_strokes(d)]
    img = raster_strokes(st, 28, 1.3, 1.2)
    return blur(noisy(img, 0.25 * amount, seed + 1), 1)


def fig14():
    s = SVG(1060, 560, "GAN 的两步交替训练", "先固定 G 训练 D 分辨真假，再固定 D 训练 G 骗过 D。")

    def gen_box(x, y, active):
        s.box(x, y, 96, 52, "生成器 $G$", key="q", size=14.5,
              sw=2.6 if active else 1.2, fill=light("q") if active else "#F3F4F6",
              stroke=main("q") if active else "#B8BEC7")
        if not active:
            lock(s, x + 78, y - 8)

    def dis_box(x, y, active):
        s.box(x, y, 96, 52, "判别器 $D$", key="k", size=14.5,
              sw=2.6 if active else 1.2, fill=light("k") if active else "#F3F4F6",
              stroke=main("k") if active else "#B8BEC7")
        if not active:
            lock(s, x + 78, y - 8)

    # ---- 第 1 步 ----
    y = 16
    s.panel(20, y, 1020, 250, "第 1 步：更新判别器 —— 学会分辨真假（$G$ 固定）", key="k", tag="1")
    ry, fy = y + 82, y + 182
    s.text(60, ry, "真实数据", size=13.5, weight="bold", anchor="start")
    for k, d in enumerate([3, 5]):
        show(s, 140 + k * 58, ry - 26, 52, digit(d), stroke=main("v"), sw=1.6)
    s.box(36, fy - 20, 70, 40, "$z$ ~ 𝒩", key="attn", size=14, weight="normal")
    s.harrow(108, 132, fy, color=INK)
    gen_box(136, fy - 26, False)
    s.harrow(236, 262, fy, color=INK)
    for k, d in enumerate([3, 2]):
        show(s, 266 + k * 58, fy - 26, 52, fake_digit(d, 30 + k), stroke=main("q"), sw=1.6)
    s.text(406, ry, "标签 1（真）", size=13.5, color=main("v"), weight="bold", anchor="start")
    s.text(406, fy, "标签 0（假）", size=13.5, color=main("q"), weight="bold", anchor="start")
    dx, dy = 560, (ry + fy) / 2 - 26
    s.arrow([(500, ry), (dx - 4, dy + 18)], color=INK, sw=1.4)
    s.arrow([(500, fy), (dx - 4, dy + 34)], color=INK, sw=1.4)
    dis_box(dx, dy, True)
    s.harrow(dx + 100, dx + 136, dy + 26, color=INK)
    s.text(dx + 186, dy + 16, "$D$($x$) ∈ [0, 1]", size=14)
    s.text(dx + 186, dy + 38, "“是真样本”的概率", size=12.5, color=MUTED)
    s.box(830, dy, 186, 52, "分类损失", key="loss", sub="真 → 1，假 → 0", size=14.5)
    s.arrow([(870, dy + 56), (870, dy + 84), (dx + 48, dy + 84), (dx + 48, dy + 56)], color=main("loss"),
            sw=1.5, dash="6 4")
    s.text(700, dy + 100, "只更新 $D$ 的参数", size=13, color=main("loss"))

    # ---- 第 2 步 ----
    y = 290
    s.panel(20, y, 1020, 250, "第 2 步：更新生成器 —— 学会骗过判别器（$D$ 固定）", key="q", tag="2")
    fy = y + 120
    s.box(36, fy - 20, 70, 40, "$z$ ~ 𝒩", key="attn", size=14, weight="normal")
    s.harrow(108, 132, fy, color=INK)
    gen_box(136, fy - 26, True)
    s.harrow(236, 262, fy, color=INK)
    for k, d in enumerate([3, 2]):
        show(s, 266 + k * 58, fy - 26, 52, fake_digit(d, 40 + k, 0.45), stroke=main("q"), sw=1.6)
    s.harrow(386, 556, fy, color=INK)
    s.text(470, fy - 16, "只送入生成样本", size=12.5, color=MUTED)
    dis_box(560, fy - 26, False)
    s.harrow(660, 696, fy, color=INK)
    s.text(746, fy - 10, "$D$($G$($z$))", size=14)
    s.box(830, fy - 26, 186, 52, "生成器损失", key="loss", sub="希望 $D$ 判成“真”", size=14.5)
    # 梯度回传
    gy = fy + 64
    s.arrow([(922, fy + 30), (922, gy), (184, gy), (184, fy + 30)], color=main("loss"), sw=2, dash="7 4")
    s.text(560, gy + 22, "梯度穿过 $D$ 传回 $G$：$D$ 告诉 $G$ “往哪里改更像真的”，但 $D$ 自己的参数不变",
           size=13, color=main("loss"))
    s.text(810, y + 22, "", size=12)
    lock(s, 818, y + 13)
    s.text(840, y + 22, "= 本步参数冻结", size=12.5, color=MUTED, anchor="start")
    s.save(OUT / "14_gan-generator-discriminator.svg")


# ---------------------------------------------------------------------------
# 15 Diffusion
# ---------------------------------------------------------------------------
def alpha_bar_table(T=1000, b0=1e-4, b1=0.02):
    ab, a = [1.0], 1.0
    for t in range(1, T + 1):
        beta = b0 + (b1 - b0) * (t - 1) / (T - 1)
        a *= 1 - beta
        ab.append(a)
    return ab


def to_signed(img):
    return [[2 * v - 1 for v in row] for row in img]


def to_disp(img):
    return [[max(0.0, min(1.0, (v + 1) / 2)) for v in row] for row in img]


def gauss_img(seed, n=28):
    r = RNG(seed)
    return [[r.normal() for _ in range(n)] for _ in range(n)]


def fig15():
    s = SVG(1080, 560, "扩散模型：前向加噪与反向去噪", "前向过程按固定公式加噪；模型学习预测噪声，生成时从新噪声逐步去噪。")
    ab = alpha_bar_table()
    x0 = to_signed(digit(3))
    eps = gauss_img(7)
    ts = [0, 50, 150, 300, 500, 1000]
    sz, gap = 116, 52
    x_start = 70
    y = 88

    def xt_img(t, e=eps):
        a = ab[t]
        return [[math.sqrt(a) * x0[i][j] + math.sqrt(1 - a) * e[i][j] for j in range(28)] for i in range(28)]

    # 前向箭头
    s.arrow([(x_start, 50), (x_start + 6 * sz + 5 * gap, 50)], color=main("k"), sw=2.2)
    s.text(x_start + 3 * sz + 2.5 * gap, 34, "前向加噪：公式事先固定，不需要学习", size=14.5, weight="bold", color=main("k"))
    for k, t in enumerate(ts):
        x = x_start + k * (sz + gap)
        show(s, x, y, sz, to_disp(xt_img(t)), lsize=14)
        lab = f"$x$_{{{t}}}" if t not in (0, 1000) else ("$x$_{0}（数据）" if t == 0 else "$x$_{T}（≈ 纯噪声）")
        s.text(x + sz / 2, y + sz + 20, lab, size=14, weight="bold")
        s.text(x + sz / 2, y + sz + 40, f"$ᾱ$_{{t}} = {ab[t]:.2f}" if ab[t] >= 0.005 else "$ᾱ$_{t} ≈ 0", size=12.5, color=MUTED)
        if k < 5:
            s.harrow(x + sz + 8, x + sz + gap - 8, y + sz / 2, color=LINE, sw=1.3)
    # 反向箭头
    yr = y + sz + 72
    s.arrow([(x_start + 6 * sz + 5 * gap, yr), (x_start, yr)], color=main("q"), sw=2.2)
    s.text(x_start + 3 * sz + 2.5 * gap, yr + 20,
           "反向去噪（生成）：从一份新的噪声出发，模型 $ε$_{θ} 每步预测噪声，采样器据此走一小步",
           size=14.5, weight="bold", color=main("q"))

    # 训练面板
    py = yr + 46
    s.panel(20, py, 1040, 252 - 20, "训练一步：随机挑一个噪声等级，一步构造输入，让网络猜出加进去的噪声", key="k")
    t = 300
    a = ab[t]
    bs = 80
    by = py + 70
    show(s, 50, by, bs, to_disp(x0))
    s.text(90, by + bs + 18, "数据 $x$_{0}", size=13.5)
    s.text(152, by + bs / 2, "+", size=20)
    show(s, 172, by, bs, to_disp(eps))
    s.text(212, by + bs + 18, "已知噪声 $ε$", size=13.5)
    s.text(212, by - 14, "随机采样", size=12.5, color=MUTED)
    s.harrow(262, 300, by + bs / 2, color=INK)
    s.text(386, by + 14, f"随机选 $t$（例：$t$ = {t}）", size=13)
    s.text(386, by + 40, "$x$_{t} = √$ᾱ$_{t} $x$_{0} + √(1−$ᾱ$_{t}) $ε$", size=14, weight="bold")
    s.text(386, by + 64, "一步算出，不必真的走 300 步", size=12.5, color=MUTED)
    s.harrow(476, 506, by + bs / 2, color=INK)
    show(s, 512, by, bs, to_disp(xt_img(t)))
    s.text(552, by + bs + 18, "$x$_{t}", size=13.5)
    s.harrow(598, 628, by + bs / 2, color=INK)
    s.box(632, by + 6, 120, bs - 12, "网络 $ε$_{θ}($x$_{t}, $t$)", key="q", size=13.5, sub="U-Net / DiT")
    s.harrow(756, 786, by + bs / 2, color=INK)
    r = RNG(99)
    eps_hat = [[0.85 * e + 0.45 * r.normal() for e in row] for row in eps]
    show(s, 792, by, bs, to_disp(eps_hat))
    s.text(832, by + bs + 18, "预测 $ε̂$", size=13.5)
    s.box(900, by + 8, 140, bs - 16, "‖$ε$ − $ε̂$‖^{2}", key="loss", size=15, sub="平方误差")
    s.harrow(876, 896, by + bs / 2, color=main("loss"))
    s.path(f"M212,{by + bs + 32} L212,{by + bs + 50} L970,{by + bs + 50} L970,{by + bs - 6}",
           stroke=main("loss"), sw=1.5, dash="6 4", extra=f'marker-end="url(#{s._marker(main("loss"), 1.0)})"')
    s.text(590, by + bs + 66, "答案就是我们自己加进去的那份噪声 —— 训练目标唾手可得", size=12.5, color=main("loss"))
    s.save(OUT / "15_diffusion-forward-reverse-process.svg")


# ---------------------------------------------------------------------------
# 16 Flow Matching vs Diffusion（1 维精确计算）
# ---------------------------------------------------------------------------
MEANS, PIS, SD = (-1.5, 1.5), (0.5, 0.5), 0.25


def _post(x, u):
    var = (1 - u) ** 2 + u * u * SD * SD
    logs = [math.log(p) - (x - u * m) ** 2 / (2 * var) for m, p in zip(MEANS, PIS)]
    mx = max(logs)
    w = [math.exp(l - mx) for l in logs]
    z = sum(w)
    return [v / z for v in w], var


def velocity(x, u):
    w, var = _post(x, u)
    c = (u * SD * SD - (1 - u)) / var
    return sum(wk * (m + c * (x - u * m)) for wk, m in zip(w, MEANS))


def score(x, u):
    w, var = _post(x, u)
    return sum(wk * (-(x - u * m) / var) for wk, m in zip(w, MEANS))


def inv_norm(p):
    lo, hi = -6.0, 6.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def fig16():
    s = SVG(1100, 552, "扩散采样与 Flow Matching 的路径对比", "同样从高斯噪声走到双峰数据分布：SDE 路径带随机抖动，ODE 路径平滑确定。")
    N = 24
    zs = [inv_norm((i + 0.5) / N) * 1.0 for i in range(N)]
    steps = 400
    du = 1.0 / steps

    def ode(z):
        x, pts = z, [(0.0, z)]
        for k in range(steps):
            u = k * du
            # 中点法
            xm = x + 0.5 * du * velocity(x, u)
            x = x + du * velocity(xm, u + 0.5 * du)
            if k % 8 == 7:
                pts.append(((k + 1) * du, x))
        return pts

    def sde(z, seed):
        r = RNG(seed)
        x, pts = z, [(0.0, z)]
        for k in range(steps):
            u = k * du
            g = 1.1 * (1 - u) ** 0.5 + 0.15
            x = x + (velocity(x, u) + 0.5 * g * g * score(x, u)) * du + g * math.sqrt(du) * r.normal()
            if k % 5 == 4:
                pts.append(((k + 1) * du, x))
        return pts

    ymax = 3.0
    pw, ph = 360, 320

    def panel(px, title, sub, paths, finals, straight=None):
        s.panel(px - 72, 20, pw + 154, 492, None)
        s.text(px + pw / 2, 46, title, size=15.5, weight="bold")
        s.text(px + pw / 2, 70, sub, size=12.5, color=MUTED)
        top = 100

        def X(u):
            return px + u * pw

        def Y(v):
            return top + ph / 2 - v / ymax * ph / 2

        s.rect(px, top, pw, ph, fill=WHITE, stroke=BORDER, sw=1)
        # 源分布（左侧，朝左）
        dens = [(v / 50 * ymax, math.exp(-(v / 50 * ymax) ** 2 / 2)) for v in range(-50, 51)]
        s.path("M" + " L".join(f"{px - 4 - 44 * d:.1f},{Y(v):.1f}" for v, d in dens), stroke=main("gray"), sw=1.6,
               fill=light("gray"))
        # 数据分布（右侧，朝右）
        def mix_pdf(v):
            return sum(p * math.exp(-(v - m) ** 2 / (2 * SD * SD)) for m, p in zip(MEANS, PIS))
        dens2 = [(v / 80 * ymax, mix_pdf(v / 80 * ymax)) for v in range(-80, 81)]
        s.path("M" + " L".join(f"{px + pw + 4 + 44 * d:.1f},{Y(v):.1f}" for v, d in dens2), stroke=main("data"),
               sw=1.6, fill=light("data"))
        if straight:
            for z, xx in straight:
                s.line(X(0), Y(z), X(1), Y(xx), color=INK, sw=1.3, dash="5 4", opacity=0.55)
        for pts, fin in zip(paths, finals):
            col = main("k") if fin < 0 else main("q")
            s.polyline([(X(u), Y(max(-ymax, min(ymax, v)))) for u, v in pts], stroke=col, sw=1.3, opacity=0.75)
        # 坐标
        s.line(px, top + ph + 14, px + pw, top + ph + 14, color=MUTED, sw=1.2)
        for u in (0, 0.5, 1):
            s.line(X(u), top + ph + 10, X(u), top + ph + 18, color=MUTED, sw=1.2)
            s.text(X(u), top + ph + 30, f"{u:g}", size=12.5, color=MUTED)
        s.text(px + pw / 2, top + ph + 52, "进度 $u$（0 = 噪声，1 = 数据）", size=13, color=INK)
        s.text(px - 26, top - 12, "噪声 𝒩(0,1)", size=12.5, color=MUTED)
        s.text(px + pw + 26, top - 12, "数据分布", size=12.5, color=main("data"), weight="bold")
        return X, Y

    sp = [sde(z, 100 + i) for i, z in enumerate(zs)]
    op = [ode(z) for z in zs]
    X, Y = panel(110, "随机采样（SDE 视角）", "每一步：沿漂移方向走 + 加一点随机扰动", sp, [p[-1][1] for p in sp])
    s.text(110 + pw / 2, 100 + ph + 82, "路线随机抖动；同一起点每次可能走向不同的峰", size=12.5, color=MUTED)
    # 训练配对：选 3 对 (z, x)
    pairs = [(-1.6, 1.45), (0.9, -1.55), (0.2, 1.6)]
    X, Y = panel(650, "确定性采样（ODE / Flow Matching）", "每一步：沿学到的速度场 $v$_{θ}($x$, $u$) 走一小步", op,
                 [p[-1][1] for p in op], straight=pairs)
    # 图例：训练用的直线配对
    lx, ly = 650, 100 + ph + 82
    s.line(lx, ly, lx + 26, ly, color=INK, sw=1.3, dash="5 4")
    s.text(lx + 34, ly, "训练配对的直线 $x$_{u} = (1−$u$)$z$ + $u$$x$，目标速度 $x$ − $z$", size=12.5, anchor="start")
    s.text(550, 534, "两侧粒子从同样的噪声出发，用同一个精确计算的速度场；中间路线不同，终点都落到同一个双峰分布。"
           "（颜色按终点所在的峰区分）", size=12.5, color=MUTED)
    s.save(OUT / "16_flow-matching-vs-diffusion.svg")


if __name__ == "__main__":
    fig10()
    fig11()
    fig12()
    fig13()
    fig14()
    fig15()
    fig16()
