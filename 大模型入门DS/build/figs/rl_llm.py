"""RL tutorial — figures for the LLM part: token MDP, RLHF, DPO, GRPO,
what RL actually does to a model, and the algorithm map."""

from __future__ import annotations

import math

from .common import *  # noqa: F401,F403
from figkit import Axes, P, Canvas, tw


# ---------------------------------------------------------------------------
# 10 — generation as a token-level MDP
# ---------------------------------------------------------------------------

def f10():
    c = Canvas(960, 480)
    c.text(40, 34, "把一次生成看成一个 MDP：状态是前缀，动作是下一个 token，奖励只在最后",
           size=11.5, fill=P["ink2"], weight="600")

    # prompt + tokens
    px, py, ph = 50, 92, 40
    c.rect(px, py, 170, ph, fill=P["panel2"], stroke=P["rule"], rx=6)
    c.text(px + 85, py + 19, "提示 prompt", size=10, fill=P["ink2"], anchor="middle",
           weight="600")
    c.text(px + 85, py + 33, "（系统 + 用户）", size=8.5, fill=P["muted"], anchor="middle")

    toks = ["y₁", "y₂", "y₃", "y₄", "<eos>"]
    xs = []
    x = 250
    for i, t in enumerate(toks):
        c.arrow(x - 22, py + 20, x - 2, py + 20, color=P["faint"], sw=1.1, head=4)
        fill, stroke = (P["greenL"], P["greenM"]) if i == len(toks) - 1 else (P["violetL"], P["violetM"])
        c.rect(x, py, 56, ph, fill=fill, stroke=stroke, rx=5)
        c.text(x + 28, py + 25, t, size=10.5, fill=P["green"] if i == 4 else P["violet"],
               anchor="middle")
        xs.append(x + 28)
        x += 80

    # states under chips
    c.text(px + 85, py + 62, "s₀", size=9.5, fill=P["muted"], anchor="middle")
    for i, cx in enumerate(xs):
        c.text(cx, py + 62, f"s{i+1}", size=9.5, fill=P["muted"], anchor="middle")
    c.text(px, py + 84, "状态 sₜ = 已经生成的前缀（长度随 t 增长）", size=9.2, fill=P["muted"])

    # reward
    rx0 = 700
    c.rect(rx0, py - 6, 210, 52, fill=P["greenL"], stroke=P["greenM"], rx=6)
    c.text(rx0 + 105, py + 14, "奖励 r", size=10.5, fill=P["green"], anchor="middle",
           weight="600")
    c.text(rx0 + 105, py + 32, "由奖励模型或验证器给出", size=8.6, fill=P["green"],
           anchor="middle")
    c.arrow(xs[-1] + 30, py + 20, rx0 - 4, py + 20, color=P["green"], sw=1.2, head=5)
    c.text(rx0 + 105, py + 60, "只在回合结束给一次 → 稀疏", size=8.8, fill=P["muted"],
           anchor="middle")

    # shared advantage
    bar_y = 212
    c.line(250, bar_y, 520, bar_y, stroke=P["green"], sw=2)
    c.arrow(385, bar_y, 385, 186, color=P["green"], sw=1.2, head=5)
    c.line(250, 186, 520, 186, stroke=P["green"], sw=1.2)
    c.line(250, 186, 250, 178, stroke=P["green"], sw=1.2)
    c.line(520, 186, 520, 178, stroke=P["green"], sw=1.2)
    c.text(532, bar_y + 4, "同一个优势 Â 广播给这一段里的每个 token（最简单的信用分配）",
           size=9, fill=P["green"])

    # KL note
    c.line(50, 246, 910, 246, stroke=P["rule"], sw=1)
    c.text(50, 272, "每个 token 还有一项 KL 约束：把新策略拉在参考策略附近，别为了拿分把语言能力改坏。",
           size=9.8, fill=P["ink2"])
    c.text(50, 292, "−β · KL( πθ(·|sₜ) ‖ πref(·|sₜ) )，对所有 t 求和", size=9.5,
           fill=P["muted"], family="serif")

    c.text(50, 332, "与经典 RL 的差别：动作空间是整个词表（几万维）、回合很长（几千步）、"
                    "奖励几乎总在最后——信用分配因此更难。", size=10.2, fill=P["muted"])
    c.text(50, 354, "更细的做法：用 critic 估计每个位置的价值（PPO），或者引入过程奖励（process reward）；"
                    "GRPO 则干脆用组内相对分数代替 critic。", size=10.2, fill=P["muted"])
    c.text(50, 386, "注意：这里的「状态」是模型自己写出来的前缀，转移是确定的——"
                    "所以 LLM 的 RL 里没有环境噪声，只有采样噪声。", size=9.8, fill=P["faint"])
    return c


# ---------------------------------------------------------------------------
# 11 — RLHF pipeline
# ---------------------------------------------------------------------------

def f11():
    c = Canvas(960, 440)
    c.text(40, 34, "RLHF 的三段式：先学会回答，再学会打分，最后按分数优化", size=11.5,
           fill=P["ink2"], weight="600")

    def stage(x, w, n, title, sub, color, fill, stroke):
        c.rect(x, 66, w, 300, fill=P["white"], stroke=P["rule"], rx=8)
        c.rect(x, 66, w, 40, fill=fill, stroke="none", rx=8)
        c.text(x + 14, 92, f"{n}  {title}", size=11, fill=color, weight="600")
        c.text(x + 14, 126, sub, size=9, fill=P["muted"])

    stage(40, 280, "①", "SFT：示范数据", "指令 + 人类写的回答", P["blue"], P["blueL"],
          P["blueM"])
    stage(348, 280, "②", "奖励模型 RM", "成对偏好 → 一个分数", P["orange"], P["orangeL"],
          P["orangeM"])
    stage(656, 280, "③", "PPO：按分数优化", "在线采样 + KL 约束", P["violet"], P["violetL"],
          P["violetM"])

    # stage 1 content
    c.rect(58, 150, 244, 54, fill=P["panel"], stroke=P["rule"], rx=5)
    c.text(66, 170, "Q：解释一下什么是梯度下降", size=8.6, fill=P["ink2"])
    c.text(66, 186, "A：（人类示范的一段正确解释）", size=8.6, fill=P["muted"])
    c.arrow(180, 210, 180, 238, color=P["faint"], sw=1.1, head=4)
    c.rect(84, 242, 192, 44, fill=P["blueL"], stroke=P["blueM"], rx=5)
    c.text(180, 262, "π_SFT", size=10.5, fill=P["blue"], anchor="middle", weight="600")
    c.text(180, 278, "会回答的模型", size=8.5, fill=P["blue"], anchor="middle")
    c.text(58, 320, "目标：最大化示范答案的似然", size=8.8, fill=P["muted"])

    # stage 2 content
    c.rect(366, 150, 244, 34, fill=P["panel"], stroke=P["rule"], rx=4)
    c.text(488, 172, "同一个问题，两个回答 A / B", size=8.8, fill=P["ink2"],
           anchor="middle")
    c.rect(366, 192, 244, 30, fill=P["greenL"], stroke=P["greenM"], rx=4)
    c.text(488, 212, "人类标注：A 比 B 好", size=8.8, fill=P["green"], anchor="middle")
    c.arrow(488, 226, 488, 248, color=P["faint"], sw=1.1, head=4)
    c.rect(392, 252, 192, 44, fill=P["orangeL"], stroke=P["orangeM"], rx=5)
    c.text(488, 272, "r_φ(x, y)", size=10.5, fill=P["orange"], anchor="middle", weight="600")
    c.text(488, 288, "打分器（可学习的标量）", size=8.3, fill=P["orange"], anchor="middle")
    c.text(366, 320, "目标：让好回答的分数高于差回答", size=8.8, fill=P["muted"])
    c.text(366, 336, "常用 Bradley–Terry：σ(r(A) − r(B))", size=8.6, fill=P["muted"])

    # stage 3 content
    c.rect(674, 150, 244, 34, fill=P["panel"], stroke=P["rule"], rx=4)
    c.text(796, 172, "πθ 现场生成若干回答", size=8.8, fill=P["ink2"], anchor="middle")
    c.arrow(796, 186, 796, 204, color=P["faint"], sw=1.1, head=4)
    c.rect(674, 208, 244, 30, fill=P["orangeL"], stroke=P["orangeM"], rx=4)
    c.text(796, 228, "RM 给每个回答打分 r", size=8.8, fill=P["orange"], anchor="middle")
    c.arrow(796, 240, 796, 258, color=P["faint"], sw=1.1, head=4)
    c.rect(674, 262, 244, 40, fill=P["violetL"], stroke=P["violetM"], rx=5)
    c.text(796, 282, "PPO 更新 πθ", size=10, fill=P["violet"], anchor="middle",
           weight="600")
    c.text(796, 298, "同时扣掉 β·KL(πθ‖πref)", size=8.2, fill=P["violet"], anchor="middle")
    c.text(674, 320, "πref 通常是 SFT 模型，防止跑偏", size=8.8, fill=P["muted"])
    c.text(674, 336, "奖励高 ≠ 事实正确，只代表「更被偏好」", size=8.6, fill=P["muted"])

    # arrows between stages
    c.arrow(322, 200, 344, 200, color=P["muted"], sw=1.3, head=5)
    c.arrow(630, 200, 652, 200, color=P["muted"], sw=1.3, head=5)
    c.text(333, 188, "预热", size=8.2, fill=P["muted"], anchor="middle")

    c.text(40, 392, "三段各自独立训练：SFT 教格式与基本行为，RM 学「人更喜欢什么」，"
                    "PPO 把这个偏好写回策略。", size=10.2, fill=P["ink2"])
    c.text(40, 412, "代价：RM 只是一个代理（proxy），优化过头就会出现 reward hacking——分数涨、真实质量不涨。",
           size=10, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 12 — DPO vs RLHF
# ---------------------------------------------------------------------------

def f12():
    c = Canvas(960, 440)
    c.text(40, 34, "DPO：把「先训奖励模型、再跑 RL」这一步代数地消掉", size=11.5,
           fill=P["ink2"], weight="600")

    # RLHF lane
    c.text(40, 76, "RLHF / PPO 路线", size=10.5, fill=P["violet"], weight="600")
    boxes = [(60, 96, 150, "偏好对 (y_w, y_l)"), (250, 96, 150, "训练 RM：r_φ"),
             (440, 96, 160, "PPO：用 r_φ 打分"), (640, 96, 150, "得到 πθ")]
    for x, y, w, label in boxes:
        c.rect(x, y, w, 46, fill=P["violetL"], stroke=P["violetM"], rx=6)
        c.text(x + w / 2, y + 27, label, size=9.2, fill=P["ink2"], anchor="middle")
    for a, b in [(210, 250), (400, 440), (600, 640)]:
        c.arrow(a + 2, 119, b - 2, 119, color=P["faint"], sw=1.1, head=4)

    # DPO lane
    c.text(40, 214, "DPO 路线", size=10.5, fill=P["teal"], weight="600")
    c.rect(60, 234, 150, 46, fill=P["tealL"], stroke=P["tealM"], rx=6)
    c.text(135, 261, "偏好对 (y_w, y_l)", size=9.2, fill=P["ink2"], anchor="middle")
    c.rect(250, 234, 340, 46, fill=P["tealL"], stroke=P["tealM"], rx=6)
    c.text(420, 253, "直接优化 πθ：让好回答的相对概率上升", size=9.2, fill=P["ink2"],
           anchor="middle")
    c.text(420, 269, "loss = −log σ( β·log(πθ(y_w)/πref(y_w)) − β·log(πθ(y_l)/πref(y_l)) )",
           size=8.2, fill=P["teal"], anchor="middle")
    c.arrow(212, 257, 248, 257, color=P["faint"], sw=1.1, head=4)
    c.arrow(592, 257, 638, 257, color=P["faint"], sw=1.1, head=4)
    c.rect(640, 234, 150, 46, fill=P["tealL"], stroke=P["tealM"], rx=6)
    c.text(715, 261, "得到 πθ", size=9.2, fill=P["ink2"], anchor="middle")

    # identity box
    c.rect(60, 312, 730, 56, fill=P["panel"], stroke=P["rule"], rx=6)
    c.text(76, 334, "关键一步：在 KL 正则的目标下，最优策略有闭式解 "
                    "π*(y|x) ∝ πref(y|x)·exp(r(x,y)/β)，", size=9.2, fill=P["ink2"])
    c.text(76, 354, "把它反解出来，奖励就可以写成 r(x,y) = β·log(π*(y|x)/πref(y|x)) + 常数——"
                    "奖励被「表示」成了策略本身。", size=9.2, fill=P["ink2"])

    c.text(40, 396, "于是不需要单独训 RM、也不需要在线采样：把上式代入 Bradley–Terry 似然，"
                    "奖励项直接消掉，只剩策略的对数概率比。", size=10.2, fill=P["ink2"])
    c.text(40, 418, "代价：DPO 是离线的，只用到固定的偏好对；探索与在线反馈的优势就没有了。",
           size=10, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 13 — GRPO
# ---------------------------------------------------------------------------

def f13():
    c = Canvas(960, 470)
    c.text(40, 34, "GRPO：同一个问题采样一组回答，用组内相对分数当优势", size=11.5,
           fill=P["ink2"], weight="600")

    c.rect(50, 150, 150, 90, fill=P["panel2"], stroke=P["rule"], rx=8)
    c.text(125, 184, "一个问题 x", size=10, fill=P["ink2"], anchor="middle", weight="600")
    c.text(125, 204, "采样 G = 4 次", size=8.8, fill=P["muted"], anchor="middle")
    c.text(125, 222, "（温度 > 0）", size=8.5, fill=P["faint"], anchor="middle")

    rewards = [0.2, 1.0, 0.0, 0.6]
    mean = sum(rewards) / len(rewards)
    var = sum((r - mean) ** 2 for r in rewards) / len(rewards)
    std = math.sqrt(var)
    labels = ["o₁", "o₂", "o₃", "o₄"]
    for i, (lab, r) in enumerate(zip(labels, rewards)):
        y = 92 + i * 70
        c.arrow(202, 195, 236, y + 24, color=P["faint"], sw=0.9, head=4, curve=6)
        c.rect(240, y, 330, 48, fill=P["white"], stroke=P["rule"], rx=6)
        c.text(254, y + 20, lab, size=10, fill=P["violet"], family="serif", italic=True)
        c.text(254, y + 36, "一段完整回答（若干 token）", size=8.4, fill=P["muted"])
        # reward
        c.rect(590, y + 8, 80, 32, fill=P["greenL"], stroke=P["greenM"], rx=4)
        c.text(630, y + 28, f"{r:.1f}", size=10, fill=P["green"], anchor="middle",
               weight="600")
        # advantage
        a = (r - mean) / (std + 1e-6)
        col = P["green"] if a > 0 else P["red"]
        fill = P["greenL"] if a > 0 else P["redL"]
        c.rect(700, y + 8, 80, 32, fill=fill, stroke=col, rx=4, sw=0.9)
        c.text(740, y + 28, f"{a:+.2f}", size=10, fill=col, anchor="middle")
        c.arrow(672, y + 24, 698, y + 24, color=P["faint"], sw=1, head=4)

    c.text(590, 76, "奖励（对/错、单测）", size=8.8, fill=P["muted"], anchor="middle")
    c.text(740, 76, "组内标准化优势", size=8.8, fill=P["muted"], anchor="middle")

    # group stats
    c.rect(820, 160, 120, 130, fill=P["panel"], stroke=P["rule"], rx=6)
    c.text(880, 184, "组统计量", size=9, fill=P["muted"], anchor="middle")
    c.text(880, 210, f"mean = {mean:.2f}", size=9.5, fill=P["ink2"], anchor="middle")
    c.text(880, 230, f"std = {std:.2f}", size=9.5, fill=P["ink2"], anchor="middle")
    c.text(880, 258, "Â = (r − mean)/std", size=8.6, fill=P["violet"], anchor="middle")
    c.text(880, 276, "同一个 Â 分给整条回答", size=8.4, fill=P["muted"], anchor="middle")

    # objective
    c.line(50, 372, 910, 372, stroke=P["rule"], sw=1)
    c.mtext(50, 400, "J_{GRPO}(θ) = E[ (1/G) Σ_{i} min( ρ_{i} Â_{i} , clip(ρ_{i}, 1−ε, 1+ε) Â_{i} ) − β·KL ]",
            size=10.5, fill=P["ink"])
    c.text(50, 426, "ρᵢ = πθ(oᵢ|x) / πold(oᵢ|x)：重要性比，与 PPO 的 clip 完全同构；"
                    "区别只是优势来自组内比较，而不是 critic。", size=9.8, fill=P["muted"])
    c.text(50, 448, "没有价值网络 → 省一份与策略同规模的显存；组内标准化还自动消掉了奖励的尺度。",
           size=9.8, fill=P["muted"])
    return c


# ---------------------------------------------------------------------------
# 14 — what RL does to the distribution
# ---------------------------------------------------------------------------

def f14():
    c = Canvas(960, 500)
    c.text(40, 34, "RL 主要是在「重新加权」已经会做的事：能答对的更容易被采样到", size=11.5,
           fill=P["ink2"], weight="600")

    # left: distribution over solution clusters
    c.text(50, 74, "同一道题的不同解法（按簇聚合）", size=9.5, fill=P["muted"])
    clusters = ["解 A", "解 B", "解 C", "解 D", "解 E"]
    base = [0.22, 0.28, 0.20, 0.18, 0.12]
    rl = [0.34, 0.42, 0.12, 0.08, 0.04]
    base_y, bw = 300, 46
    for i in range(5):
        x = 70 + i * 84
        hb = 200 * base[i] / 0.42
        hr = 200 * rl[i] / 0.42
        c.rect(x, base_y - hb, bw, hb, fill=P["blueL"], stroke=P["blue"], rx=2, sw=1)
        c.rect(x + bw + 4, base_y - hr, bw, hr, fill=P["violetL"], stroke=P["violet"],
               rx=2, sw=1)
        c.text(x + bw + 2, base_y + 16, clusters[i], size=8.5, fill=P["muted"],
               anchor="middle")
    c.line(60, base_y, 500, base_y, stroke=P["ink2"], sw=1)
    c.rect(60, 90, 12, 10, fill=P["blueL"], stroke=P["blue"], rx=2, sw=1)
    c.text(78, 99, "基座模型", size=9, fill=P["ink2"])
    c.rect(150, 90, 12, 10, fill=P["violetL"], stroke=P["violet"], rx=2, sw=1)
    c.text(168, 99, "RL 之后", size=9, fill=P["ink2"])
    c.text(60, 340, "正确解所在簇的概率上升，错误/冗余解被压低；熵下降，分布变尖。",
           size=9.2, fill=P["muted"])

    # right: pass@k
    ax = Axes(c, 590, 116, 320, 194, xlim=(1, 64), ylim=(0, 1), xlog=True,
              xticks=[1, 2, 4, 8, 16, 32, 64], yticks=[0, 0.5, 1],
              xlabel="采样数 k（log）", ylabel="pass@k")
    ks = list(range(1, 65))
    base_curve = [(k, 1 - (1 - 0.32) ** (k ** 0.62)) for k in ks]
    rl_curve = [(k, 1 - (1 - 0.55) ** (k ** 0.42)) for k in ks]
    ax.line(base_curve, color=P["blue"], sw=2)
    ax.line(rl_curve, color=P["violet"], sw=2)
    c.text(700, 300, "基座", size=9, fill=P["blue"])
    c.text(878, 152, "RL 后", size=9, fill=P["violet"])
    ax.vline(1, color=P["faint"], dash="2 3")
    c.text(596, 96, "pass@1：RL 明显更高；k 很大时可能趋同甚至反转（示意）", size=8.6,
           fill=P["muted"])

    c.text(40, 392, "这解释了为什么 RL 后 pass@1 涨得很快：不是「学会了新解法」，而是「更常选到已经会的解法」。",
           size=10.2, fill=P["ink2"])
    c.text(40, 412, "也解释了它的天花板：基座模型采样不到的正确解法，RL 也采样不出来（除非奖励信号足够细）。",
           size=10.2, fill=P["ink2"])
    c.text(40, 438, "曲线为示意；实验上常见的是 pass@1 上升、pass@k（k 很大）上升有限甚至下降。",
           size=9.8, fill=P["faint"])
    return c


# ---------------------------------------------------------------------------
# 15 — map of the algorithm family
# ---------------------------------------------------------------------------

def f15():
    c = Canvas(960, 500)
    c.text(40, 34, "一张图记住这些方法的位置：学什么、用不用模型、在不在策略上", size=11.5,
           fill=P["ink2"], weight="600")

    c.rect(360, 62, 240, 46, fill=P["panel2"], stroke=P["rule"], rx=8)
    c.text(480, 91, "强化学习", size=12, fill=P["ink"], anchor="middle", weight="600")

    c.line(480, 108, 480, 132, stroke=P["faint"], sw=1.2)
    c.line(190, 132, 770, 132, stroke=P["faint"], sw=1.2)
    for x in (190, 480, 770):
        c.line(x, 132, x, 150, stroke=P["faint"], sw=1.2)

    heads = [(190, "有模型 model-based", "先学/已知环境模型，再做规划", P["teal"]),
             (480, "无模型 · 价值", "学 V / Q，再由价值推策略", P["blue"]),
             (770, "无模型 · 策略", "直接参数化 π(a|s)", P["violet"])]
    for x, h, sub, col in heads:
        c.rect(x - 118, 150, 236, 56, fill=P["white"], stroke=col, rx=6, sw=1.1)
        c.text(x, 172, h, size=9.6, fill=col, anchor="middle", weight="600")
        c.text(x, 192, sub, size=8, fill=P["muted"], anchor="middle")

    cols = [
        (190, [("动态规划 DP", "有模型 + 自举"), ("树搜索 / 规划", "MCTS、AlphaZero")], P["teal"],
         P["tealL"], P["tealM"]),
        (480, [("SARSA / Q-learning", "表格控制"), ("DQN / Double", "价值 + 深度网络")], P["blue"],
         P["blueL"], P["blueM"]),
        (770, [("REINFORCE / A2C", "策略梯度 / actor-critic"), ("PPO / GRPO", "clip + 信任域"),
               ("DPO", "离线，无需 RM")], P["violet"], P["violetL"], P["violetM"]),
    ]
    for x, items, col, fill, stroke in cols:
        c.line(x, 206, x, 226, stroke=P["faint"], sw=1)
        for k, (name, note) in enumerate(items):
            y = 226 + k * 50
            c.rect(x - 108, y, 216, 40, fill=fill, stroke=stroke, rx=5)
            c.text(x - 98, y + 17, name, size=8.6, fill=col, weight="600")
            c.text(x - 98, y + 31, note, size=7.2, fill=P["muted"])

    # LLM band
    c.rect(60, 372, 840, 66, fill=P["panel"], stroke=P["rule"], rx=8)
    c.text(74, 392, "大模型后训练里实际在用的三种组合", size=8.8, fill=P["muted"])
    for i, (name, note) in enumerate([("PPO + 奖励模型（RLHF）", "在线、要 critic"),
                                      ("DPO / IPO", "离线、无 RM、无采样"),
                                      ("GRPO / RLVR", "可验证奖励、无 critic")]):
        x = 76 + i * 276
        c.rect(x, 400, 258, 26, fill=P["white"], stroke=P["rule"], rx=4)
        c.text(x + 10, 417, name, size=8.4, fill=P["ink2"], weight="600")
        c.text(x + 250, 417, note, size=7.2, fill=P["muted"], anchor="end")

    c.text(40, 468, "一条主线：贝尔曼（价值如何递归）→ 采样（模型未知时怎么估）→ 自举（TD）→ "
                    "函数逼近（深度 RL）→ 策略梯度（直接优化策略）→ 信任域（PPO）→ KL 正则（LLM）。",
           size=9.4, fill=P["muted"])
    return c


FIGURES = {
    "10_token_mdp": f10,
    "11_rlhf_pipeline": f11,
    "12_dpo_vs_rlhf": f12,
    "13_grpo": f13,
    "14_rl_effects": f14,
    "15_algorithm_map": f15,
}
