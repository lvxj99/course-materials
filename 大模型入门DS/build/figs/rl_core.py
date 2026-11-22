"""RL tutorial — core figures: bandit, MDP, value, Bellman, MC/TD, Q-learning,
deadly triad + DQN, policy gradient, PPO clip."""

from __future__ import annotations

import math

from .common import *  # noqa: F401,F403
from figkit import Axes, P, Canvas, ramp, tw


# ---------------------------------------------------------------------------
# 01 — bandit: only tried actions can be estimated
# ---------------------------------------------------------------------------

def f01():
    c = Canvas(960, 420)
    c.text(40, 34, "只有被尝试过的动作才有估计——贪心可能一直错过真正最好的那个",
           size=11.5, fill=P["ink2"], weight="600")

    X0, X1 = 150, 870
    def xr(r):
        return X0 + r * (X1 - X0)

    # legend
    lx = 150
    c.circle(lx, 60, 3, fill=P["ink2"]); c.text(lx + 9, 64, "样本", size=9.5, fill=P["muted"])
    lx += 52
    c.line(lx, 54, lx, 66, stroke=P["blue"], sw=2)
    c.text(lx + 8, 64, "当前估计", size=9.5, fill=P["muted"])
    lx += 82
    c.rect(lx, 54, 20, 12, fill=P["panel2"], stroke=P["rule"], rx=2)
    c.text(lx + 28, 64, "真实分布（均值 ± 1σ）", size=9.5, fill=P["muted"])

    arms = [
        ("A", 0.62, 0.10, [0.58, 0.66, 0.61, 0.69, 0.63]),
        ("B", 0.45, 0.08, [0.41, 0.44, 0.47, 0.43, 0.46]),
        ("C", 0.72, 0.18, [0.56, 0.65]),
        ("D", 0.33, 0.08, []),
    ]
    rows = [106, 168, 230, 292]
    for (name, m, sd, samples), y in zip(arms, rows):
        c.text(72, y + 4, name, size=12, fill=P["ink"], anchor="middle", weight="600")
        c.text(112, y + 4, f"n = {len(samples)}", size=9.5,
               fill=P["muted"] if samples else P["red"], anchor="end")
        if samples:
            c.rect(xr(m - sd), y - 11, xr(m + sd) - xr(m - sd), 22, fill=P["panel2"],
                   stroke=P["rule"], rx=3)
            for s in samples:
                c.circle(xr(s), y, 3.2, fill=P["ink2"], opacity=0.55)
            est = sum(samples) / len(samples)
            c.line(xr(est), y - 13, xr(est), y + 13, stroke=P["blue"], sw=2)
            c.text(xr(est), y - 18, f"{est:.2f}", size=9, fill=P["blue"], anchor="middle")
        else:
            c.text((X0 + X1) / 2, y + 4, "从未尝试 → 没有估计，也就不知道它有多好",
                   size=9.5, fill=P["faint"], anchor="middle")

    c.line(X0, 320, X1, 320, stroke=P["ink2"], sw=1)
    for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        c.line(xr(v), 320, xr(v), 325, stroke=P["ink2"], sw=1)
        c.text(xr(v), 340, f"{v:.1f}", size=9.5, fill=P["muted"], anchor="middle")
    c.text(X1, 358, "单次奖励 r", size=9.5, fill=P["muted"], anchor="end")

    # truth line of arm C
    c.line(xr(0.72), 78, xr(0.72), 306, stroke=P["violet"], sw=1, dash="3 3")
    c.text(xr(0.72) + 6, 92, "C 的真实均值 0.72（尝试少、估计偏低）", size=9.5,
           fill=P["violet"])

    # callout
    c.text(xr(0.80), 274, "换成贪心：会继续选 A，C 再也没机会被尝试", size=9.5,
           fill=P["orange"])

    c.text(40, 384, "按估计贪心 → 选 A（0.63）；但 A 的真实均值 0.62 低于 C 的 0.72。想让 C 被多试几次，"
                    "就必须主动探索。", size=10.8, fill=P["ink2"])
    c.text(40, 404, "两种常见做法：ε-greedy 以 ε 的概率随机试；UCB 选「估计 + c·√(ln t / n)」，"
                    "不确定性 n 小的动作探索奖励更高。", size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 02 — MDP on a grid world
# ---------------------------------------------------------------------------

def f02():
    c = Canvas(960, 470)
    c.text(40, 34, "序贯决策：状态、动作、转移、奖励、折扣——一条轨迹就是一个样本",
           size=11.5, fill=P["ink2"], weight="600")

    cell, gx, gy = 56, 60, 84
    cols, rows = 5, 4
    walls = {(1, 1), (3, 2)}
    pit = (4, 1)
    goal = (4, 3)

    def cx(c_, r_):
        return gx + c_ * cell + cell / 2

    def cy(r_):
        return gy + r_ * cell + cell / 2

    for r_ in range(rows):
        for c_ in range(cols):
            x = gx + c_ * cell
            y = gy + r_ * cell
            fill, stroke = P["white"], P["rule"]
            if (c_, r_) in walls:
                fill, stroke = "#d7dee6", "#c2ccd6"
            elif (c_, r_) == pit:
                fill, stroke = P["redL"], P["redM"]
            elif (c_, r_) == goal:
                fill, stroke = P["greenL"], P["greenM"]
            c.rect(x, y, cell, cell, fill=fill, stroke=stroke, rx=3, sw=0.9)
    for (wc, wr) in walls:
        c.line(gx + wc * cell + 8, gy + wr * cell + 8, gx + (wc + 1) * cell - 8,
               gy + (wr + 1) * cell - 8, stroke="#aab6c1", sw=2)
        c.line(gx + (wc + 1) * cell - 8, gy + wr * cell + 8, gx + wc * cell + 8,
               gy + (wr + 1) * cell - 8, stroke="#aab6c1", sw=2)

    path = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), (3, 3), (4, 3)]
    pts = [(cx(a, b), cy(b)) for a, b in path]
    c.polyline(pts, stroke=P["blue"], sw=2, opacity=0.9)
    for i, (px, py) in enumerate(pts):
        c.circle(px, py, 3.4, fill=P["blue"])
        if i and i < len(pts) - 1:
            c.text((pts[i - 1][0] + px) / 2 + 7, (pts[i - 1][1] + py) / 2 - 5, "−0.04",
                   size=8, fill=P["blue"], anchor="start")
    # cell labels on top of the trajectory
    c.text(gx + 12, gy + 18, "S", size=11, fill=P["ink"], weight="600")
    c.text(gx + 4 * cell + 10, gy + 3 * cell + 18, "+1", size=11, fill=P["green"],
           weight="600")
    c.text(cx(*pit), cy(pit[1]) + 4, "−1", size=11, fill=P["red"], anchor="middle",
           weight="600")
    c.text(gx, gy - 12, "一条采样轨迹：每步 −0.04，最后一步拿到 +1", size=9.2,
           fill=P["blue"])

    # MDP tuple
    tx = 400
    c.text(tx, 74, "五元组  M = (S, A, P, R, γ)", size=11.5, fill=P["ink"], weight="600")
    items = [
        ("S", "状态：网格里的位置（含起终点、墙、陷阱）", P["ink2"]),
        ("A", "动作：上 / 下 / 左 / 右", P["ink2"]),
        ("P", "转移：P(s′|s,a)，撞墙留在原地", P["ink2"]),
        ("R", "奖励：每步 −0.04，进入终点 +1，陷阱 −1", P["ink2"]),
        ("γ", "折扣：让近期奖励更重要，γ∈[0,1)", P["ink2"]),
    ]
    for i, (k, v, col) in enumerate(items):
        y = 108 + i * 30
        c.text(tx, y, k, size=11, fill=P["blue"], weight="600", family="serif", italic=True)
        c.text(tx + 22, y, v, size=10.2, fill=col)

    # policy note
    c.text(tx, 282, "策略 π(a|s)：在每个状态给出动作分布。", size=10.2, fill=P["violet"])
    c.text(tx, 300, "轨迹 τ = (s₀,a₀,r₁,s₁,…)：数据由「当前策略」采样得到，", size=10.2,
           fill=P["violet"])
    c.text(tx, 318, "所以策略一变，数据分布也跟着变。", size=10.2, fill=P["violet"])

    c.text(tx, 356, "目标：找到 π，使期望回报 E_π[G₀] 最大，", size=10.5, fill=P["ink"])
    c.text(tx, 376, "G₀ = r₁ + γr₂ + γ²r₃ + …", size=10.5, fill=P["ink"], family="serif")

    c.text(40, 442, "与监督学习的三点不同：没有逐时刻的正确答案；奖励可能延迟且稀疏；"
                    "训练数据的分布由自己的策略决定。", size=10.5, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 03 — value and advantage
# ---------------------------------------------------------------------------

def f03():
    c = Canvas(960, 430)
    c.text(40, 34, "同一个状态下的三个动作：价值衡量「多好」，优势衡量「比平均水平好多少」",
           size=11.5, fill=P["ink2"], weight="600")

    sx, sy = 120, 210
    c.circle(sx, sy, 26, fill=P["panel2"], stroke=P["rule"])
    c.text(sx, sy + 5, "s", size=14, fill=P["ink"], anchor="middle", family="serif",
           italic=True)

    acts = [("a₁", 0.80, 0.5, 130), ("a₂", 0.50, 0.3, 210), ("a₃", 0.20, 0.2, 290)]
    for name, q, pi, y in acts:
        c.arrow(sx + 24, sy, 250, y, color=P["faint"], sw=1.3, head=5)
        c.text(200, (sy + y) / 2 - 8, f"π={pi:.1f}", size=9, fill=P["muted"], anchor="middle")
        c.rect(258, y - 20, 150, 40, fill=P["blueL"], stroke=P["blueM"], rx=5)
        c.text(300, y + 4, name, size=11, fill=P["blue"], anchor="middle", family="serif",
               italic=True)
        c.text(390, y + 4, f"Q = {q:.2f}", size=10.5, fill=P["ink2"], anchor="end")

    c.line(258, 340, 408, 340, stroke=P["rule"], sw=1)
    c.text(258, 366, "V(s) = Σ π(a|s)·Q(s,a) = 0.5×0.8 + 0.3×0.5 + 0.2×0.2 = 0.59",
           size=10.2, fill=P["ink2"])
    c.text(258, 386, "V 是这个状态的「平均分」；再给每个动作打分，就是优势。",
           size=9.8, fill=P["muted"])

    # advantage panel
    bx = 810
    c.text(620, 70, "A(s,a) = Q(s,a) − V(s)", size=11.5, fill=P["ink"], weight="600")
    c.line(bx, 96, bx, 300, stroke=P["ink2"], sw=1)
    c.text(bx, 88, "0", size=9, fill=P["muted"], anchor="middle")
    for i, (name, q, pi, y) in enumerate(acts):
        a = q - 0.59
        w = abs(a) * 260
        yy = 122 + i * 62
        col = P["green"] if a > 0 else P["red"]
        fill = P["greenL"] if a > 0 else P["redL"]
        c.text(660, yy + 4, name, size=10.5, fill=P["ink2"], anchor="end",
               family="serif", italic=True)
        c.rect(bx if a > 0 else bx - w, yy - 10, max(w, 1), 20, fill=fill, stroke=col,
               sw=0.9, rx=2)
        c.text(bx + 8 if a > 0 else bx - w - 8, yy + 4, f"{a:+.2f}", size=9.5, fill=col,
               anchor="start" if a > 0 else "end")
    c.text(620, 330, "正值：比当前策略的平均表现更好，应该被提高；", size=9.8,
           fill=P["muted"])
    c.text(620, 348, "负值：拉低平均，应该被压低。", size=9.8, fill=P["muted"])

    c.text(40, 412, "策略梯度里真正该乘的不是回报 G，而是优势 A：把一个动作的收益，"
                    "与「这个状态下通常会怎样」作比较。", size=10.5, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 04 — Bellman backup: expectation vs max
# ---------------------------------------------------------------------------

def f04():
    c = Canvas(960, 470)

    def panel(px, title, sub, color, is_max):
        c.text(px, 46, title, size=11.5, fill=color, weight="600")
        c.text(px, 64, sub, size=9.8, fill=P["muted"])
        vx = px + 200
        c.rect(vx - 70, 96, 140, 40, fill=P["blueL"], stroke=P["blueM"], rx=6)
        c.text(vx, 121, "V(s)", size=12, fill=P["blue"], anchor="middle", family="serif",
               italic=True)
        qy = 196
        for i, qx in enumerate([px + 70, px + 200, px + 330]):
            c.arrow(vx, 138, qx, qy - 22, color=P["faint"], sw=1.1, head=4)
            c.rect(qx - 52, qy - 22, 104, 40, fill=P["violetL"], stroke=P["violetM"], rx=5)
            c.text(qx, qy + 2, f"Q(s,a{i+1})", size=10, fill=P["violet"], anchor="middle",
                   family="serif", italic=True)
        c.text(vx + 34, 152, "取 max" if is_max else "对 a 加权求和", size=9,
               fill=P["ink"] if is_max else P["muted"], weight="600" if is_max else None)
        # to next value
        for qx in [px + 70, px + 200, px + 330]:
            c.arrow(qx, qy + 20, vx, 292, color=P["faint"], sw=1, head=4, opacity=0.8)
        c.rect(vx - 78, 292, 156, 40, fill=P["tealL"], stroke=P["tealM"], rx=6)
        c.text(vx, 317, "V(s′)", size=12, fill=P["teal"], anchor="middle", family="serif",
               italic=True)
        c.text(vx, 352, "对下一状态 s′ 按转移概率加权", size=9, fill=P["muted"],
               anchor="middle")

    panel(60, "① 策略评估：把期望一层层展开", "给定策略 π，算它的价值：先对动作加权，再对下一状态加权",
          P["blue"], False)
    panel(540, "② 最优价值：把加权平均换成 max", "不再问「按当前策略会怎样」，而是问「最好能怎样」",
          P["violet"], True)

    c.text(40, 396, "贝尔曼方程做的事：把「无限长的回报求和」改写成一个「自指」的等式。"
                    "只要下一层的 V 是对的，这一层的 V 就能用一次期望算出来。",
           size=10.8, fill=P["ink2"])
    c.text(40, 418, "于是求解 V 变成一个不动点问题：反复用右边更新左边（动态规划），或者从采样中估计右边（TD）。",
           size=10.5, fill=P["muted"])
    c.text(40, 444, "※ 图中每个 Q 只画了一条到 V(s′) 的边，实际要对所有下一状态按转移概率加权。",
           size=9.8, fill=P["faint"])
    return c


# ---------------------------------------------------------------------------
# 05 — Monte Carlo vs TD
# ---------------------------------------------------------------------------

def f05():
    c = Canvas(960, 480)

    def chain(px, py, n, label, color):
        pts = []
        for i in range(n):
            x = px + i * 46
            c.circle(x, py, 13, fill=P["white"], stroke=color, sw=1.4)
            c.text(x, py + 4, f"s{i}", size=9, fill=color, anchor="middle", family="serif",
                   italic=True)
            pts.append(x)
            if i:
                c.arrow(x - 46 + 14, py, x - 15, py, color=P["faint"], sw=1, head=4)
                c.text(x - 23, py - 9, f"r{i}", size=8, fill=P["muted"], anchor="middle")
        c.text(px + (n - 1) * 46 / 2, py + 34, label, size=9.5, fill=P["muted"],
               anchor="middle")
        return pts

    c.text(40, 40, "① 蒙特卡洛：走完整个回合，再用真实的 G 更新", size=11.5, fill=P["blue"],
           weight="600")
    pts = chain(70, 110, 5, "一条完整轨迹（必须有终止）", P["blue"])
    c.polyline([(pts[0], 138), (pts[0], 160), (pts[-1], 160), (pts[-1], 138)],
               stroke=P["blue"], sw=1.1, dash="3 3")
    c.text((pts[0] + pts[-1]) / 2, 176, "G₀ = r₁ + γr₂ + γ²r₃ + … 全部算出来",
           size=9.5, fill=P["blue"], anchor="middle")
    c.text(70, 218, "无偏，但要等回合结束；回合越长方差越大。", size=9.8, fill=P["muted"])

    c.text(40, 240, "② 时序差分：只走一步，用「估计」补上后面", size=11.5, fill=P["teal"],
           weight="600")
    c.rect(70, 288, 100, 34, fill=P["tealL"], stroke=P["tealM"], rx=5)
    c.text(120, 310, "sₜ", size=11, fill=P["teal"], anchor="middle", family="serif",
           italic=True)
    c.arrow(174, 305, 250, 305, color=P["teal"], sw=1.3, head=5)
    c.text(212, 296, "rₜ₊₁", size=8.5, fill=P["muted"], anchor="middle")
    c.rect(254, 288, 100, 34, fill=P["tealL"], stroke=P["tealM"], rx=5)
    c.text(304, 310, "sₜ₊₁", size=11, fill=P["teal"], anchor="middle", family="serif",
           italic=True)
    c.text(370, 310, "V(sₜ₊₁) 是现成的估计 → 直接拿来当「后续回报」", size=9.8,
           fill=P["ink2"])
    c.polyline([(354, 288), (354, 268), (120, 268), (120, 286)], stroke=P["teal"], sw=1,
               dash="3 3")
    c.arrow(120, 276, 120, 286, color=P["teal"], sw=1, head=4, dash="3 3")
    c.text(240, 262, "自举 bootstrap：用估计更新估计", size=9.2, fill=P["teal"],
           anchor="middle")
    c.text(70, 356, "有偏（V 还不准），但方差小、可以边走边学，不必等回合结束。", size=9.8,
           fill=P["muted"])

    # bias-variance minimap
    ax = Axes(c, 660, 96, 250, 210, xlim=(0, 1), ylim=(0, 1), xticks=[0, 1],
              yticks=[0, 1], xtick_labels=["小", "大"], ytick_labels=["小", "大"],
              grid=False, xlabel="方差", ylabel="偏差")
    c.text(785, 62, "估计量的取舍", size=9.8, fill=P["ink2"], anchor="middle")
    c.circle(830, 210, 5, fill=P["blue"])
    c.text(840, 214, "MC", size=10, fill=P["blue"])
    c.circle(710, 150, 5, fill=P["teal"])
    c.text(720, 154, "TD", size=10, fill=P["teal"])
    c.text(660, 380, "n-step、TD(λ) 就是在这两点之间连续调节。", size=9.2, fill=P["muted"])

    c.text(40, 452, "两者都是「用某种目标去逼近贝尔曼右边」：MC 用采样到的完整回报，"
                    "TD 用一步奖励加自举。", size=10.5, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 06 — Q-learning and on/off-policy
# ---------------------------------------------------------------------------

def f06():
    c = Canvas(960, 470)
    c.text(40, 34, "控制：学的是动作价值 Q(s,a)——它可以直接告诉我们该做什么",
           size=11.5, fill=P["ink2"], weight="600")

    # Q table
    tx, ty, cw, ch = 60, 90, 62, 40
    c.text(tx, 78, "Q 表（行 = 状态，列 = 动作）", size=9.8, fill=P["muted"])
    acts = ["↑", "→", "↓", "←"]
    for j, a in enumerate(acts):
        c.text(tx + 44 + j * cw + cw / 2, 104, a, size=10.5, fill=P["muted"],
               anchor="middle")
    rows = [["0.21", "0.35", "0.10", "0.05"], ["0.62", "0.48", "0.71", "0.30"],
            ["0.12", "0.66", "0.55", "0.41"]]
    for i, row in enumerate(rows):
        y = ty + 14 + i * ch
        c.text(tx + 34, y + 24, f"s{i+1}", size=10, fill=P["muted"], anchor="end",
               family="serif", italic=True)
        for j, v in enumerate(row):
            hot = (i == 1 and j == 2)
            c.rect(tx + 44 + j * cw, y, cw - 3, ch - 3,
                   fill=P["violetL"] if hot else P["white"],
                   stroke=P["violet"] if hot else P["rule"], sw=1.4 if hot else 0.9, rx=3)
            c.text(tx + 44 + j * cw + (cw - 3) / 2, y + 24, v, size=10,
                   fill=P["violet"] if hot else P["ink2"], anchor="middle")
    c.text(60, 272, "Q-learning 的更新：", size=10.2, fill=P["ink2"])
    c.mtext(60, 300, "Q(s,a) ← Q(s,a) + α [ r + γ max_a′ Q(s′,a′) − Q(s,a) ]", size=12.5,
            fill=P["ink"])
    c.text(60, 326, "方括号里就是 TD 误差；目标里用了下一状态的 max，", size=9.8,
           fill=P["muted"])
    c.text(60, 344, "所以它学的是「最优策略」的价值，而不是「当前策略」的。", size=9.8,
           fill=P["muted"])

    # cliff walking
    gx, gy, cc = 560, 120, 34
    cols, rows_n = 8, 3
    for r_ in range(rows_n):
        for c_ in range(cols):
            x, y = gx + c_ * cc, gy + r_ * cc
            cliff = (r_ == 2 and 1 <= c_ <= 6)
            c.rect(x, y, cc, cc, fill=P["redL"] if cliff else P["white"],
                   stroke=P["redM"] if cliff else P["rule"], rx=2, sw=0.9)
            if cliff:
                c.text(x + cc / 2, y + cc / 2 + 3.5, "−100", size=7.2, fill=P["red"],
                       anchor="middle")
    c.text(gx + cc / 2, gy + 2 * cc + cc / 2 + 4, "S", size=9.5, fill=P["ink2"],
           anchor="middle")
    c.text(gx + 7 * cc + cc / 2, gy + 2 * cc + cc / 2 + 4, "G", size=9.5,
           fill=P["green"], anchor="middle")
    c.text(gx + 4 * cc, gy - 14, "悬崖（掉下去 −100 并回到起点）", size=8.2, fill=P["red"],
           anchor="middle")

    # paths: q-learning along the bottom, sarsa one row up
    ql = [(gx + cc / 2 + i * cc, gy + 2 * cc + cc / 2) for i in range(8)]
    sa = [(gx + cc / 2, gy + 2 * cc + cc / 2), (gx + cc / 2, gy + 1 * cc + cc / 2),
          (gx + 6.5 * cc, gy + 1 * cc + cc / 2), (gx + 7 * cc + cc / 2, gy + 2 * cc + cc / 2)]
    c.polyline(ql, stroke=P["blue"], sw=1.8, opacity=0.9)
    c.polyline(sa, stroke=P["orange"], sw=1.8, opacity=0.9)
    ly = gy + 3 * cc + 16
    c.line(gx, ly - 4, gx + 20, ly - 4, stroke=P["blue"], sw=1.8)
    c.text(gx + 26, ly, "Q-learning：贴悬崖（最优但会随机掉下去）", size=8.4,
           fill=P["ink2"])
    c.line(gx, ly + 18, gx + 20, ly + 18, stroke=P["orange"], sw=1.8)
    c.text(gx + 26, ly + 22, "SARSA：离远一点（更安全）", size=8.4, fill=P["ink2"])

    c.text(560, 330, "同一条悬崖路：Q-learning 用 max 学「最优」，", size=9.8, fill=P["ink2"])
    c.text(560, 348, "SARSA 用实际采样的 a′ 学「当前策略」，", size=9.8, fill=P["ink2"])
    c.text(560, 366, "所以后者会为了避免随机探索掉下去而绕远。", size=9.8, fill=P["muted"])

    c.text(40, 410, "on-policy（SARSA）：用自己正在执行的动作去更新；off-policy（Q-learning）："
                    "用最优动作去更新，可以学别人的数据。", size=10.5, fill=P["ink2"])
    c.text(40, 432, "代价：max 会让估计系统性偏高（maximization bias），"
                    "常配合 Double Q-learning 修正。", size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 07 — deadly triad and DQN's fixes
# ---------------------------------------------------------------------------

def f07():
    c = Canvas(960, 430)
    c.text(40, 34, "把 Q-learning 接到神经网络上：三个东西同时出现时，训练可能不稳定",
           size=11.5, fill=P["ink2"], weight="600")

    nodes = [(230, 92, "函数逼近"), (110, 300, "自举"), (350, 300, "off-policy")]
    for x, y, name in nodes:
        c.rect(x - 62, y - 26, 124, 52, fill=P["panel2"], stroke=P["rule"], rx=8)
        c.text(x, y + 4, name, size=11, fill=P["ink2"], anchor="middle", weight="600")
    for a, b in [(0, 1), (1, 2), (2, 0)]:
        c.line(nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1], stroke=P["faint"],
               sw=1.2, dash="4 3")
    c.text(230, 214, "致命三角", size=11, fill=P["red"], anchor="middle", weight="600")
    c.text(230, 232, "误差被反复放大 → 发散", size=9.2, fill=P["red"], anchor="middle")

    cards = [
        ("经验回放 replay", "把历史样本存起来随机抽，打破样本相关性；也让同一批数据被反复使用。", P["blue"]),
        ("目标网络 target net", "用一份「慢半拍」的旧参数算自举目标，别让目标和预测一起跑。", P["violet"]),
        ("奖励 / 梯度裁剪", "把奖励压到合理范围，控制 TD 误差的尺度，避免大梯度冲击。", P["teal"]),
    ]
    for i, (name, desc, col) in enumerate(cards):
        y = 92 + i * 96
        c.rect(530, y, 390, 76, fill=P["white"], stroke=P["rule"], rx=8)
        c.rect(530, y, 4, 76, fill=col, stroke="none", rx=2)
        c.text(548, y + 26, name, size=11, fill=col, weight="600")
        c.text(548, y + 48, desc, size=9.6, fill=P["ink2"])
        c.text(548, y + 64, "", size=1)

    c.text(530, 74, "DQN 的三处工程修正", size=10.5, fill=P["ink2"], weight="600")

    c.text(40, 392, "这三项不是理论上的解法，而是让「深度 + 自举 + 离策略」在小规模上能跑起来的工程手段；"
                    "更根本的稳定性要靠在策略方法（第 9 节起）。", size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 08 — policy gradient
# ---------------------------------------------------------------------------

def f08():
    c = Canvas(960, 470)
    c.text(40, 34, "策略梯度：不学价值，直接调「选动作的概率」", size=11.5, fill=P["ink2"],
           weight="600")

    # policy bars
    c.text(60, 80, "当前策略 πθ(a|s)", size=10, fill=P["muted"])
    acts = [("a₁", 0.20), ("a₂", 0.55), ("a₃", 0.25)]
    base, hmax = 260, 150
    for i, (a, p) in enumerate(acts):
        x = 70 + i * 70
        h = hmax * p / 0.55
        hot = i == 1
        c.rect(x, base - h, 48, h, fill=P["blueL"] if hot else P["panel2"],
               stroke=P["blue"] if hot else P["rule"], sw=1.4 if hot else 1, rx=2)
        c.text(x + 24, base - h - 8, f"{p:.2f}", size=9.5,
               fill=P["blue"] if hot else P["ink2"], anchor="middle")
        c.text(x + 24, base + 16, a, size=10, fill=P["ink2"], anchor="middle",
               family="serif", italic=True)
    c.text(232, 186, "采样到 a₂", size=9, fill=P["blue"])
    c.arrow(232, 192, 218, 214, color=P["blue"], sw=1, head=4)
    c.line(60, base, 290, base, stroke=P["ink2"], sw=1)
    c.text(60, base + 44, "采样 a₂ → 得到一条轨迹 → 算出 G（或优势 A）", size=9.5,
           fill=P["blue"])

    # two cases
    c.text(400, 80, "按结果调整概率", size=10.5, fill=P["ink2"], weight="600")
    c.rect(400, 96, 200, 92, fill=P["greenL"], stroke=P["greenM"], rx=8)
    c.text(414, 120, "如果 G > 0（比预期好）", size=9.8, fill=P["green"], weight="600")
    c.text(414, 142, "π(a₂) ↑，其它动作 ↓", size=9.8, fill=P["ink2"])
    c.text(414, 162, "更新方向：∇log π(a₂|s) × G", size=9.2, fill=P["muted"])
    c.rect(400, 204, 200, 92, fill=P["redL"], stroke=P["redM"], rx=8)
    c.text(414, 228, "如果 G < 0（比预期差）", size=9.8, fill=P["red"], weight="600")
    c.text(414, 250, "π(a₂) ↓", size=9.8, fill=P["ink2"])
    c.text(414, 270, "梯度反号，同一个 log 项的系数变负", size=9.2, fill=P["muted"])

    # estimator
    c.text(640, 120, "梯度估计（REINFORCE）", size=10.5, fill=P["ink2"], weight="600")
    c.mtext(640, 154, "∇J(θ) ≈ (1/N) Σ_n Σ_t ∇log π(a_t|s_t) · G_t", size=12,
            fill=P["ink"])
    c.text(640, 186, "减去基线 b(s)：", size=9.8, fill=P["muted"])
    c.mtext(640, 212, "∇J ≈ ∇log π(a|s) · (G − b(s))", size=12, fill=P["ink"])
    c.text(640, 242, "不影响期望，但能大幅降低方差。", size=9.2, fill=P["muted"])
    c.text(640, 268, "b(s) 最简单的取法就是 V(s)——这就是 actor-critic。", size=9.2,
           fill=P["violet"])

    c.text(40, 396, "为什么是 log 项？因为 ∂π/∂θ = π · ∂log π/∂θ：只要「采样到」某个动作，"
                    "就能无偏地估计它概率的梯度。", size=10.5, fill=P["ink2"])
    c.text(40, 418, "代价是方差大、样本效率低；而且更新幅度受步长影响，策略可能一步走坏——"
                    "这才有了信任域与 PPO。", size=10.2, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 09 — PPO clipped objective
# ---------------------------------------------------------------------------

def f09():
    c = Canvas(960, 470)
    c.text(40, 34, "PPO：把「一步别走太远」写进目标函数", size=11.5, fill=P["ink2"],
           weight="600")

    eps = 0.2

    def clip(r):
        return max(1 - eps, min(1 + eps, r))

    def lp(r):
        return min(r * 1.0, clip(r) * 1.0)

    def ln(r):
        return min(r * (-1.0), clip(r) * (-1.0))

    ax = Axes(c, 90, 90, 520, 250, xlim=(0, 2), ylim=(-1.5, 1.5), xticks=[0, 0.5, 1, 1.5, 2],
              yticks=[-1, 0, 1], xlabel="概率比 r = πθ(a|s) / πold(a|s)", ylabel="目标项")
    # clipped regions
    c.rect(ax.X(1 + eps), ax.Y(1.5), ax.X(2) - ax.X(1 + eps), ax.Y(-1.5) - ax.Y(1.5),
           fill=P["panel2"], stroke="none", opacity=0.65)
    c.rect(ax.X(0), ax.Y(-0.8), ax.X(1 - eps) - ax.X(0), ax.Y(-1.5) - ax.Y(-0.8),
           fill=P["panel2"], stroke="none", opacity=0.65)
    rs = [2 * i / 240 for i in range(241)]
    ax.line([(r, lp(r)) for r in rs], color=P["green"], sw=2.2)
    ax.line([(r, ln(r)) for r in rs], color=P["red"], sw=2.2)
    ax.vline(1, color=P["faint"], dash="3 3")
    ax.vline(1 - eps, color=P["faint"], dash="2 3")
    ax.vline(1 + eps, color=P["faint"], dash="2 3")

    c.text(ax.X(1), 80, "r = 1（旧策略）", size=9, fill=P["muted"], anchor="middle")
    c.text(ax.X(1 + eps), 108, "1+ε", size=9, fill=P["muted"], anchor="middle")
    c.text(ax.X(1 - eps), 108, "1−ε", size=9, fill=P["muted"], anchor="middle")

    c.text(ax.X(1.62), ax.Y(1.02), "A > 0：r 再大也不再加分", size=9.2, fill=P["green"])
    c.text(ax.X(0.06), ax.Y(-1.18), "A < 0：r 再小也不再加分", size=9.2, fill=P["red"])

    c.text(660, 100, "目标函数", size=10.5, fill=P["ink2"], weight="600")
    c.mtext(660, 132, "L = E[ min( r·A , clip(r, 1−ε, 1+ε)·A ) ]", size=11.5, fill=P["ink"])
    c.text(660, 170, "两处「截断」的含义：", size=9.8, fill=P["muted"])
    c.text(660, 192, "· 好动作（A>0）把概率提到 1+ε 就够了，", size=9.6, fill=P["ink2"])
    c.text(660, 210, "  再提也不给额外奖励，避免一步走太远；", size=9.6, fill=P["ink2"])
    c.text(660, 232, "· 坏动作（A<0）把概率压到 1−ε 就够，", size=9.6, fill=P["ink2"])
    c.text(660, 250, "  再压也不额外奖励。", size=9.6, fill=P["ink2"])
    c.text(660, 282, "KL 惩罚 / 信任域的作用类似：", size=9.6, fill=P["violet"])
    c.text(660, 300, "让新策略别离旧策略太远。", size=9.6, fill=P["violet"])

    c.text(40, 424, "PPO 仍然用重要性采样复用旧策略采到的数据，但用 clip 把「复用」限制在信任域内；"
                    "实现上通常跑多个 epoch、几个 minibatch。", size=10.2, fill=P["muted"])
    return c


FIGURES = {
    "01_bandit": f01,
    "02_mdp_gridworld": f02,
    "03_value_advantage": f03,
    "04_bellman_backup": f04,
    "05_mc_vs_td": f05,
    "06_q_learning_cliff": f06,
    "07_deadly_triad_dqn": f07,
    "08_policy_gradient": f08,
    "09_ppo_clip": f09,
}
