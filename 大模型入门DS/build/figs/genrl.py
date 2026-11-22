"""Figures for 8.4-8.6: diffusion, flow matching, RL, and the seq2seq bottleneck."""

from __future__ import annotations

import math

from .common import *  # noqa: F401,F403
from figkit import P, Canvas, ramp, tw

DIGIT3 = [
    "............",
    "...######...",
    "..#......#..",
    ".........#..",
    "........#...",
    ".....####...",
    "........#...",
    "........#...",
    "..#......#..",
    "...######...",
    "............",
    "............",
]
DARK = ramp("#ffffff", "#26323c")


def _digit_grid(t=0.0, seed=7, size=12):
    """A 12x12 digit image blended with deterministic noise, x_t = sqrt(a)x0 + sqrt(1-a)e."""
    rng = seed
    out = []
    a = max(0.0, min(1.0, t))
    for i in range(size):
        row = []
        for j in range(size):
            rng = (1103515245 * rng + 12345) % (2 ** 31)
            e = (rng / (2 ** 31)) * 2 - 1
            x0 = 2 * (1.0 if DIGIT3[i][j] == "#" else 0.0) - 1
            v = math.sqrt(a) * x0 + math.sqrt(max(1e-6, 1 - a)) * e
            row.append(min(1.0, max(0.0, (v + 1) / 2)))
        out.append(row)
    return out


def pixel_img(c, x, y, size, grid, gap=0.7):
    n = len(grid)
    cell = size / n
    for i in range(n):
        for j in range(n):
            c.rect(x + j * cell, y + i * cell, cell - gap, cell - gap,
                   fill=DARK(grid[i][j]), stroke="none", rx=0.8)


# ---------------------------------------------------------------------------
# 28 — seq2seq with a fixed-size bottleneck
# ---------------------------------------------------------------------------

def f28():
    c = Canvas(960, 380)
    cw, chh = 62, 56
    ey = 130
    enc_x = [46, 126, 206, 286]
    dec_x = [490, 570, 650, 730]
    src = ["I", "love", "machine", "learning"]
    tgt = ["我", "喜欢", "机器", "学习"]

    c.text(197, 40, "编码器 encoder：逐步读入原文", size=11.5, fill=P["blue"], weight="600",
           anchor="middle")
    c.text(641, 40, "解码器 decoder：逐步输出译文", size=11.5, fill=P["violet"], weight="600",
           anchor="middle")

    # source tokens + encoder cells
    for i, (x, tok) in enumerate(zip(enc_x, src)):
        c.rect(x + cw / 2 - 30, 66, 60, 24, fill=P["panel"], stroke=P["rule"], rx=4)
        c.text(x + cw / 2, 83, tok, size=10.5, fill=P["ink2"], anchor="middle")
        c.arrow(x + cw / 2, 91, x + cw / 2, ey - 2, color=P["muted"], sw=1.1, head=4)
        c.rect(x, ey, cw, chh, fill=P["blueL"], stroke=P["blueM"], rx=6)
        c.text(x + cw / 2, ey + 24, "RNN", size=10, fill=P["blue"], anchor="middle")
        c.text(x + cw / 2, ey + 40, f"h{i+1}", size=9.5, fill=P["blue"], anchor="middle")
        if i:
            c.arrow(enc_x[i - 1] + cw, ey + chh / 2, x - 3, ey + chh / 2,
                    color=P["blue"], sw=1.2, head=4)

    # context vector
    cx0 = 404
    c.rect(cx0, 106, 16, 104, fill=P["violetL"], stroke=P["violetM"], rx=2)
    for k in range(8):
        c.line(cx0, 106 + k * 13, cx0 + 16, 106 + k * 13, stroke=P["violetM"], sw=0.6)
    c.arrow(enc_x[-1] + cw, ey + chh / 2, cx0 - 2, ey + chh / 2, color=P["violet"], sw=1.3,
            head=5)
    c.text(cx0 + 8, 96, "c", size=12, fill=P["violet"], anchor="middle", family="serif",
           italic=True)
    c.rect(cx0 - 16, 86, 48, 140, fill="none", stroke=P["violet"], rx=6, dash="4 3")
    c.text(cx0 - 16, 240, "瓶颈：整句只压成", size=9.8, fill=P["violet"])
    c.text(cx0 - 16, 254, "这一个固定维数向量", size=9.8, fill=P["violet"])

    # decoder cells
    for i, (x, tok) in enumerate(zip(dec_x, tgt)):
        c.rect(x + cw / 2 - 26, 66, 52, 24, fill=P["violetL"], stroke=P["violetM"], rx=4)
        c.text(x + cw / 2, 83, tok, size=10.5, fill=P["violet"], anchor="middle")
        c.arrow(x + cw / 2, ey - 2, x + cw / 2, 92, color=P["violet"], sw=1.1, head=4)
        c.rect(x, ey, cw, chh, fill=P["violetL"], stroke=P["violetM"], rx=6)
        c.text(x + cw / 2, ey + 24, "RNN", size=10, fill=P["violet"], anchor="middle")
        c.text(x + cw / 2, ey + 40, f"s{i+1}", size=9.5, fill=P["violet"], anchor="middle")
        if i:
            c.arrow(dec_x[i - 1] + cw, ey + chh / 2, x - 3, ey + chh / 2,
                    color=P["violet"], sw=1.2, head=4)

    c.arrow(cx0 + 18, ey + chh / 2, dec_x[0] - 3, ey + chh / 2, color=P["violet"], sw=1.3,
            head=5)

    c.text(46, 214, "h_t：编码器在第 t 步的隐藏状态，只沿序列向前传递", size=10.2,
           fill=P["muted"])
    c.text(490, 214, "每一步都读取上一步的输出（teacher forcing 时读真实的前一词）",
           size=10.2, fill=P["muted"])

    c.text(46, 272, "句子越长，需要塞进 c 的细节越多；而 c 的维数固定，信息只能被压缩。"
                    "读取时也没有“看哪里”的选择。",
           size=10.8, fill=P["ink2"])
    c.text(46, 294, "这正是注意力机制要改的地方：把每个位置的隐藏状态都保留下来，"
                    "让解码器在每一步按需读取（7.1 节）。",
           size=10.8, fill=P["ink2"])
    c.text(46, 326, "注意力版本里，编码器交出的是 T 个向量 h₁ … h_T，解码器每一步为它们分配权重，"
                    "再汇总；seq2seq 的交出物只有一个 c。",
           size=10.5, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 15 — diffusion forward / reverse
# ---------------------------------------------------------------------------

def f15():
    c = Canvas(960, 540)
    n = 6
    th, step = 96, 124
    x0 = (960 - (n - 1) * step - th) / 2
    abar = [1.0, 0.72, 0.5, 0.32, 0.16, 0.04]
    yy_top, yy_bot = 80, 252

    c.text(x0, 38, "前向：按固定日程逐步加噪（不需要学习）", size=11.5, fill=P["ink2"],
           weight="600")
    for i in range(n):
        x = x0 + i * step
        pixel_img(c, x, yy_top, th, _digit_grid(abar[i], seed=7 + i))
        c.text(x + th / 2, yy_top - 10, f"x{i}", size=10.5, fill=P["ink2"], anchor="middle")
        if i:
            c.arrow(x - step + th + 5, yy_top + th / 2, x - 7, yy_top + th / 2,
                    color=P["red"], sw=1.3, head=5)
    c.text(x0 + (n - 1) * step + th + 12, yy_top + th / 2 + 4, "t → T", size=10,
           fill=P["red"])

    c.text(x0, 214, "反向：从纯噪声出发，用学到的模型一步步去噪（生成）", size=11.5,
           fill=P["ink2"], weight="600")
    for i in range(n):
        x = x0 + i * step
        pixel_img(c, x, yy_bot, th, _digit_grid(abar[n - 1 - i], seed=7 + (n - 1 - i)))
        c.text(x + th / 2, yy_bot - 10, f"x{n-1-i}", size=9.5, fill=P["muted"],
               anchor="middle")
        if i:
            c.arrow(x - 6, yy_bot + th / 2, x - step + th + 5, yy_bot + th / 2,
                    color=P["blue"], sw=1.3, head=5)

    # bus: the same network is applied at every reverse step
    c.line(x0 + 20, 372, x0 + (n - 1) * step + th - 20, 372, stroke=P["violet"], sw=1,
           dash="3 3")
    for i in range(1, n):
        xb = x0 + i * step - (step - th) / 2
        c.line(xb, 372, xb, 360, stroke=P["violet"], sw=0.9, dash="2 3", opacity=0.85)
    c.line(480, 372, 480, 392, stroke=P["violet"], sw=1, dash="3 3")
    c.rect(330, 392, 300, 46, fill=P["violetL"], stroke=P["violetM"], rx=6)
    c.text(480, 412, "噪声预测网络 εθ(xₜ, t)", size=12, fill=P["violet"], anchor="middle",
           weight="600")
    c.text(480, 429, "U-Net / DiT 等；每一步都调用同一个网络", size=9.8, fill=P["violet"],
           anchor="middle")

    c.text(x0, 470, "训练目标：让预测的噪声接近真实加入的噪声 —— L = E‖ε − εθ(xₜ, t)‖²",
           size=10.8, fill=P["ink2"])
    c.text(x0, 492, "采样：从 xₜ（t = T）出发，反复「预测噪声 → 去掉一点」，逐步得到 x₀",
           size=10.8, fill=P["ink2"])
    c.text(x0, 518, "xₜ = √ᾱₜ · x₀ + √(1 − ᾱₜ) · ε，其中 ᾱₜ 由日程决定；t 越大，"
                    "原始信号保留得越少，最后接近纯高斯噪声。",
           size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 16 — flow matching vs diffusion paths
# ---------------------------------------------------------------------------

def f16():
    c = Canvas(960, 490)

    def dots(cx, cy, n, seed, fill, rx=30, ry=20):
        rng = seed
        for k in range(n):
            rng = (1103515245 * rng + 12345) % (2 ** 31)
            u = rng / (2 ** 31)
            rng = (1103515245 * rng + 12345) % (2 ** 31)
            v = rng / (2 ** 31)
            r = math.sqrt(u)
            a = 2 * math.pi * v
            c.circle(cx + rx * r * math.cos(a), cy + ry * r * math.sin(a), 1.7, fill=fill)

    def frame(px, title, sub, color):
        c.text(px, 40, title, size=11.5, fill=color, weight="600")
        c.text(px, 58, sub, size=10.5, fill=P["muted"])
        c.rect(px, 74, 400, 320, fill=P["white"], stroke=P["rule"], rx=8)

    # ---- left: reverse SDE
    px = 40
    frame(px, "反向 SDE：每一步都注入新的随机噪声", "同一起点，不同轨迹", P["red"])
    dx_, dy_ = px + 130, 132
    dx2, dy2 = px + 285, 132
    for (bx, by) in [(dx_, dy_), (dx2, dy2)]:
        c.circle(bx, by, 34, fill=P["blueL"], stroke="none")
        dots(bx, by, 34, bx, P["blue2"], rx=30, ry=22)
        c.text(bx, by - 42, "数据分布", size=9.5, fill=P["blue"], anchor="middle")
    c.circle(px + 205, 340, 36, fill=P["redL"], stroke="none")
    dots(px + 205, 340, 40, 11, P["red2"], rx=30, ry=22)
    c.text(px + 205, 388, "噪声", size=9.5, fill=P["red"], anchor="middle")

    for k in range(7):
        sx = px + 205 + 10 * math.cos(k * 1.9)
        sy = 330
        tx, ty = (dx_, dy_ + 18) if k % 2 == 0 else (dx2, dy2 + 18)
        tx += 14 * math.cos(k * 2.7)
        L = math.hypot(tx - sx, ty - sy)
        nx, ny = -(ty - sy) / L, (tx - sx) / L
        pts = []
        for i in range(33):
            u = i / 32
            bx_ = sx + (tx - sx) * u
            by_ = sy + (ty - sy) * u
            w = 16 * math.sin(math.pi * u) * math.sin(9 * u + k * 1.3)
            pts.append((bx_ + nx * w, by_ + ny * w))
        c.polyline(pts, stroke=P["red2"], sw=1.05, opacity=0.7)

    # ---- right: probability-flow ODE
    px2 = 500
    frame(px2, "概率流 ODE / Flow Matching：确定性的速度场", "从同一处出发，路径彼此不交叉",
          P["blue"])
    ex_, ey_ = px2 + 130, 132
    ex2, ey2 = px2 + 285, 132
    for (bx, by) in [(ex_, ey_), (ex2, ey2)]:
        c.circle(bx, by, 34, fill=P["blueL"], stroke="none")
        dots(bx, by, 34, bx + 3, P["blue2"], rx=30, ry=22)
        c.text(bx, by - 42, "数据分布", size=9.5, fill=P["blue"], anchor="middle")
    c.circle(px2 + 205, 340, 36, fill=P["redL"], stroke="none")
    dots(px2 + 205, 340, 40, 17, P["red2"], rx=30, ry=22)
    c.text(px2 + 205, 388, "噪声", size=9.5, fill=P["red"], anchor="middle")

    for k in range(7):
        sx = px2 + 205 + 9 * (k - 3) / 3
        tx, ty = (ex_, ey_ + 20) if k % 2 == 0 else (ex2, ey2 + 20)
        tx += 12 * math.cos(k * 2.1)
        L = math.hypot(tx - sx, ty - 330)
        nx = -(ty - 330) / L
        pts = []
        for i in range(33):
            u = i / 32
            e = u ** 1.15
            bx_ = sx + (tx - sx) * e
            by_ = 330 + (ty - 330) * e
            w = 9 * math.sin(math.pi * u) * (1 if k % 3 == 0 else -1)
            pts.append((bx_ + nx * w, by_))
        c.polyline(pts, stroke=P["blue2"], sw=1.35, opacity=0.85)

    c.text(40, 424, "SDE 的每条轨迹都不同，但在任一时刻，大量轨迹的边缘分布相同；"
                    "概率流 ODE 去掉随机项、只保留调整后的漂移，诱导出同样的边缘分布。",
           size=10.8, fill=P["ink2"])
    c.text(40, 446, "Flow Matching 训练的正是这条 ODE 的速度场：给定时点与位置，预测该往哪里走；"
                    "生成时做数值积分即可，不需要逐步注入噪声。",
           size=10.8, fill=P["ink2"])
    c.text(40, 470, "结果：采样路径更直、步数可以更少；代价是模型必须学好整个向量场，"
                    "而不只是单步去噪。",
           size=10.5, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 27 — reinforcement learning loop
# ---------------------------------------------------------------------------

def f27():
    c = Canvas(960, 460)
    c.text(120, 40, "策略 πθ 观察状态、选择动作；环境返回奖励与下一个状态", size=11.5,
           fill=P["ink2"], weight="600")

    c.rect(120, 150, 240, 96, fill=P["violetL"], stroke=P["violetM"], rx=8)
    c.text(240, 182, "Agent", size=13.5, fill=P["violet"], anchor="middle", weight="600")
    c.text(240, 206, "策略 πθ(a | s)", size=11, fill=P["violet"], anchor="middle")
    c.text(240, 224, "（可以是神经网络）", size=9.5, fill=P["muted"], anchor="middle")

    c.rect(640, 150, 240, 96, fill=P["panel"], stroke=P["rule"], rx=8)
    c.text(760, 182, "Environment", size=13.5, fill=P["ink2"], anchor="middle", weight="600")
    c.text(760, 206, "状态转移 P(s′ | s, a)", size=10.5, fill=P["ink2"], anchor="middle")
    c.text(760, 224, "与奖励 R(s, a, s′)", size=10.5, fill=P["ink2"], anchor="middle")

    c.arrow(364, 178, 636, 178, color=P["blue"], sw=1.5, head=6)
    c.text(500, 170, "动作 aₜ", size=11.5, fill=P["blue"], anchor="middle")
    c.arrow(636, 222, 364, 222, color=P["ink2"], sw=1.5, head=6)
    c.text(500, 240, "状态 sₜ₊₁", size=11.5, fill=P["ink2"], anchor="middle")

    # reward loop above
    c.polyline([(760, 150), (760, 110), (240, 110)], stroke=P["green"], sw=1.4)
    c.arrow(240, 110, 240, 146, color=P["green"], sw=1.4, head=6)
    c.text(500, 102, "奖励 rₜ₊₁", size=11.5, fill=P["green"], anchor="middle")

    # trajectory
    c.text(120, 306, "一条 trajectory（轨迹）：", size=10.5, fill=P["muted"])
    items = [("s₀", P["panel2"], P["muted"]), ("a₀", P["violetL"], P["violet"]),
             ("r₁", P["greenL"], P["green"]), ("s₁", P["panel2"], P["muted"]),
             ("a₁", P["violetL"], P["violet"]), ("r₂", P["greenL"], P["green"]),
             ("s₂", P["panel2"], P["muted"]), ("a₂", P["violetL"], P["violet"]),
             ("r₃", P["greenL"], P["green"]), ("…", P["white"], P["faint"])]
    x = 250
    for i, (s, fill, col) in enumerate(items):
        w = 44
        c.rect(x, 288, w, 26, fill=fill, stroke=col, rx=4, sw=0.9)
        c.text(x + w / 2, 305, s, size=10.5, fill=col, anchor="middle")
        x += w + 6

    c.text(120, 366, "Gₜ = rₜ₊₁ + γ·rₜ₊₂ + γ²·rₜ₊₃ + …", size=14, fill=P["ink"])
    c.text(120, 396, "训练目标是最大化期望回报 E[Gₜ]；γ ∈ [0, 1) 越接近 1，越在乎远期结果。"
                     "V(s) 与 Q(s, a) 分别描述“在状态 s 下”“在 s 先做 a 再按 π 行动”的期望回报。",
           size=10.8, fill=P["muted"])
    c.text(120, 418, "与监督学习的差别：没有每一步的标准答案，只有行动之后的评价；"
                     "奖励可能延迟、稀疏，且由环境或规则给出。",
           size=10.8, fill=P["muted"])
    return c


FIGURES = {
    "28_seq2seq-bottleneck": f28,
    "15_diffusion-forward-reverse-process": f15,
    "16_flow-matching-vs-diffusion": f16,
    "27_agent-environment-reinforcement-loop": f27,
}
