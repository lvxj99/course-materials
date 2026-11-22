"""Figures for the standalone reinforcement-learning lecture."""

from __future__ import annotations

from lib import (
    BLUE,
    GOLD,
    GRAY,
    GREEN,
    INK,
    LINE,
    MUTED,
    ORANGE,
    PAPER,
    PURPLE,
    RED,
    TEAL,
    Fig,
)


def fig_credit() -> None:
    f = Fig(960, "延迟奖励下的信用分配", "只有最后一步有奖励时，前面的动作该记多少功劳并不显然。")
    steps = [("出发", "向北"), ("岔路", "开门"), ("走廊", "拿钥匙"), ("终点", "到达")]
    rewards = ["0", "0", "0", "+1"]
    for i, ((state, action), reward) in enumerate(zip(steps, rewards)):
        x = 48 + i * 230
        f.card(x, 48, 150, 52, state, None, "blue")
        f.card(x, 140, 150, 52, action, "这一步的动作", "orange")
        f.arrow(x + 75, 100, x + 75, 140, color=ORANGE)
        last = i == 3
        f.text(x + 75, 224, reward, anchor="middle", size=20, weight=700, color=GOLD if last else MUTED)
        f.text(x + 75, 248, "即时奖励", anchor="middle", size=12, color=MUTED)
        if i < 3:
            f.arrow(x + 158, 166, x + 222, 166, color=GRAY)
    f.text(48, 292, "结局是好的。向北、开门、拿钥匙、到达，各分到多少功劳？", size=16, weight=650)
    f.footnote(
        328,
        "这是信用分配问题。监督学习在每一步都有目标；这里的学习信号要等轨迹结束后才出现，而且并不自带“哪一步造成了它”的标注。",
    )
    f.save("rl-01-credit-assignment.svg")


def fig_mdp() -> None:
    f = Fig(960, "马尔可夫决策过程中的一轮交互", "策略、转移和奖励是三件不同的事。")
    f.region(48, 36, 320, 200)
    f.text(208, 68, "智能体", anchor="middle", size=18, weight=700, color=BLUE)
    f.text(208, 104, "看见 s_t", anchor="middle", size=15)
    f.text(208, 134, "按 π(a | s) 选择 a_t", anchor="middle", size=15)
    f.text(208, 174, "策略是智能体自己的选择", anchor="middle", size=13, color=MUTED)
    f.region(560, 36, 352, 200)
    f.text(736, 68, "环境", anchor="middle", size=18, weight=700, color=GREEN)
    f.text(736, 104, "按 P 进入下一状态", anchor="middle", size=15)
    f.text(736, 134, "给出奖励 r(t+1)", anchor="middle", size=15, weight=650, color=GOLD)
    f.text(736, 174, "转移和奖励不属于策略", anchor="middle", size=13, color=MUTED)
    f.arrow(380, 100, 548, 100, color=ORANGE, sw=1.8)
    f.text(464, 84, "a_t", anchor="middle", size=16, weight=700, color=ORANGE)
    f.arrow(548, 170, 380, 170, color=GREEN, sw=1.8)
    f.text(464, 154, "r(t+1) ,  s(t+1)", anchor="middle", size=15, weight=700, color=GREEN)
    labels = [("S", "状态"), ("A", "动作"), ("P", "转移"), ("R", "奖励"), ("γ", "折扣")]
    tones = ["blue", "orange", "green", "gold", "purple"]
    for i, ((sym, name), tone_name) in enumerate(zip(labels, tones)):
        f.card(48 + i * 180, 280, 160, 64, sym, name, tone_name, title_size=20)
    f.footnote(
        368,
        "马尔可夫性说的是：给定现在的状态和动作，下一步的分布不再依赖更早的历史。它是建模时的选择。语言模型里，我们把当前上下文当作这个状态。",
    )
    f.save("rl-02-mdp.svg")


def fig_discount() -> None:
    f = Fig(960, "折扣怎样给将来的奖励加权", "同为 1 的未来奖励，γ 不同时占的分量差很多。")
    f.text(28, 32, "设从此以后每一步的即时奖励都是 1。图中只画前四项。", size=15)

    def panel(x, gamma, color):
        f.region(x, 56, 440, 280)
        f.text(x + 20, 84, f"γ = {gamma}", size=18, weight=700, color=color)
        weights = [gamma**k for k in range(4)]
        base = 250
        scale = 120
        for k, w in enumerate(weights):
            bx = x + 36 + k * 100
            h = scale * w
            f.rect(bx, base - h, 56, h, fill=color, fo=0.9, rx=3)
            f.text(bx + 28, base + 18, f"第 {k + 1} 步", anchor="middle", size=12, color=MUTED)
            f.text(bx + 28, base - h - 12, f"{w:.3f}".rstrip("0").rstrip("."), anchor="middle", size=13, weight=700, color=color)
        partial = sum(weights)
        total = 1 / (1 - gamma)
        f.text(x + 20, 308, f"前四项之和 {partial:.3f}，无穷和 1/(1−γ) = {total:.3f}", size=13)

    panel(28, 0.5, BLUE)
    panel(492, 0.9, ORANGE)
    f.footnote(
        360,
        "γ = 0.5 时，前四项已经接近无穷和 2，更远的奖励几乎可以忽略。γ = 0.9 时无穷和是 10，前四项大约只有 3.44，后面的项仍占大头。\n"
        "折扣同时让无穷长的和有有限值。它也表达一种偏好：更早拿到的 1，权重大于更晚拿到的 1。",
    )
    f.save("rl-03-discount.svg")


def fig_advantage() -> None:
    f = Fig(960, "价值是平均，优势是高出平均的部分", "按当前策略对优势求期望，结果是 0。")
    actions = ["走", "等", "退"]
    pi = [0.5, 0.3, 0.2]
    q = [4.0, 0.0, 1.0]
    v = sum(p * qi for p, qi in zip(pi, q))
    adv = [qi - v for qi in q]
    assert abs(v - 2.2) < 1e-9
    assert abs(sum(p * a for p, a in zip(pi, adv))) < 1e-9

    f.region(28, 24, 440, 340)
    f.text(48, 52, "动作价值 Q", size=16, weight=700)
    base = 280
    scale = 40  # px per unit, Q max 4 → 160
    for i, (name, p, qi) in enumerate(zip(actions, pi, q)):
        bx = 70 + i * 120
        h = scale * qi
        f.rect(bx, base - h, 64, max(h, 2), fill=BLUE, fo=0.9, rx=3)
        f.text(bx + 32, base + 20, name, anchor="middle", size=14, weight=650)
        f.text(bx + 32, base + 40, f"π = {p}", anchor="middle", size=12, color=MUTED)
        f.text(bx + 32, base - h - 14, f"{qi:.0f}", anchor="middle", size=14, weight=700, color=BLUE)
    vy = base - scale * v
    f.line(56, vy, 400, vy, stroke=PURPLE, sw=1.8, dash="5 3")
    f.text(404, vy, f"V = {v:.1f}", baseline="middle", size=14, weight=700, color=PURPLE)

    f.region(488, 24, 444, 340)
    f.text(508, 52, "优势 A = Q − V", size=16, weight=700)
    zero = 188
    ascale = 36
    for i, (name, a) in enumerate(zip(actions, adv)):
        bx = 540 + i * 120
        h = abs(a) * ascale
        color = GREEN if a > 0 else RED
        if a >= 0:
            f.rect(bx, zero - h, 64, h, fill=color, fo=0.9, rx=3)
            f.text(bx + 32, zero - h - 14, f"{a:+.1f}", anchor="middle", size=14, weight=700, color=color)
        else:
            f.rect(bx, zero, 64, h, fill=color, fo=0.9, rx=3)
            f.text(bx + 32, zero + h + 16, f"{a:+.1f}", anchor="middle", size=14, weight=700, color=color)
        f.text(bx + 32, 332, name, anchor="middle", size=14, weight=650)
    f.line(520, zero, 880, zero, stroke=GRAY, sw=1.2)
    f.text(888, zero, "0", baseline="middle", size=12, color=MUTED)
    f.footnote(
        384,
        "Q(走)=4，Q(等)=0，Q(退)=1。V = 0.5×4 + 0.3×0 + 0.2×1 = 2.2。优势为 +1.8、−2.2、−1.2，按 π 加权后是 0。\n"
        "后文的基线不改变策略梯度的期望，和“优势的策略平均为零”是同一件事。这些数是为了把定义算完，不是一次训练的记录。",
    )
    f.save("rl-04-advantage.svg")


def fig_bellman() -> None:
    f = Fig(960, "贝尔曼备份只看一步", "当前价值等于这一步的期望奖励，加上折扣后的下一状态价值。")
    f.card(36, 150, 130, 64, "s", "现在的状态", "blue")
    f.arrow(166, 168, 250, 100, color=ORANGE)
    f.arrow(166, 196, 250, 250, color=ORANGE)
    f.card(250, 70, 160, 56, "动作 a", "概率 π(a|s)", "orange")
    f.card(250, 224, 160, 56, "动作 b", "概率 π(b|s)", "orange")
    f.arrow(410, 98, 530, 98, color=GREEN)
    f.arrow(410, 252, 530, 252, color=GREEN)
    f.card(530, 70, 250, 56, "s′", "R(s,a,s′) + γ V(s′)", "green")
    f.card(530, 224, 250, 56, "s″", "R(s,b,s″) + γ V(s″)", "teal")
    f.text(36, 330, "还要按转移概率 P(s′ | s, a) 对下一状态求期望。图里每个动作只画了一个后继。", size=14)
    f.text(36, 366, "V(s) = Σ_a π(a|s) Σ_s′ P(s′|s,a) [ R(s,a,s′) + γ V(s′) ]", size=16, font="serif", style="italic")
    f.footnote(
        404,
        "把 G(t) = r(t+1) + γ G(t+1) 取条件期望，再用马尔可夫性把下一时刻的期望回报换成 V(s′)，就得到这个等式。\n"
        "它对任意策略都成立。最优方程是把对动作的加权平均换成 max。",
    )
    f.save("rl-05-bellman.svg")


def fig_mc_td() -> None:
    f = Fig(960, "同一条轨迹上的蒙特卡洛目标和时序差分目标", "γ = 0.9，价值函数起初全是 0。")
    states = ["s0", "s1", "s2"]
    rewards = ["0", "0", "1"]
    xs = [48, 300, 552]
    for x, state in zip(xs, states):
        f.card(x, 48, 110, 48, state, None, "blue")
    f.card(804, 48, 110, 48, "结束", "价值记为 0", "gray")
    for i, reward in enumerate(rewards):
        x0 = xs[i] + 110
        x1 = (xs[i + 1] if i < 2 else 804) - 8
        f.arrow(x0, 72, x1, 72, color=GOLD if reward == "1" else GRAY)
        f.text((x0 + x1) / 2, 58, f"r = {reward}", anchor="middle", size=13, weight=700, color=GOLD if reward == "1" else MUTED)

    mc = ["0.81", "0.90", "1.00"]
    td = ["0.00", "0.00", "1.00"]
    f.region(28, 160, 440, 180)
    f.text(48, 188, "蒙特卡洛：用从这里往后的真实回报", size=15, weight=700, color=BLUE)
    for i, (state, g) in enumerate(zip(states, mc)):
        f.card(48 + i * 136, 220, 120, 64, state, f"G = {g}", "blue")
    f.text(48, 310, "要等轨迹结束才能计算。", size=13, color=MUTED)

    f.region(492, 160, 440, 180)
    f.text(512, 188, "时序差分：只用下一步的奖励和当前 V", size=15, weight=700, color=ORANGE)
    for i, (state, g) in enumerate(zip(states, td)):
        tone = "green" if g == "1.00" else "orange"
        f.card(512 + i * 136, 220, 120, 64, state, f"目标 {g}", tone)
    f.text(512, 310, "V 仍是 0，所以前两步的目标还是 0。", size=13, color=MUTED)
    f.footnote(
        360,
        "从后往前：G_2 = 1，G_1 = 0 + 0.9×1 = 0.9，G_0 = 0 + 0.9×0.9 = 0.81。TD 目标是 r + γV(下一状态)。\n"
        "等 s2 的价值被学到 1 附近，下一次访问 s1 时，TD 目标才会变成 0.9。价值是倒着、一步一步传回去的。",
    )
    f.save("rl-06-mc-td.svg")


def fig_sarsa() -> None:
    f = Fig(960, "同一次转移，SARSA 和 Q-learning 的目标不同", "γ = 0.9，这一步奖励是 1。")
    f.card(36, 80, 140, 64, "s", "当前状态", "blue")
    f.arrow(176, 112, 240, 112, color=ORANGE)
    f.text(208, 96, "a", anchor="middle", size=14, weight=700, color=ORANGE)
    f.card(240, 80, 120, 64, "r = 1", None, "gold")
    f.arrow(360, 112, 430, 112, color=GREEN)
    f.card(430, 48, 200, 56, "s′ 的左动作", "Q = 2", "green")
    f.card(430, 120, 200, 56, "s′ 的右动作", "Q = 0，实际走了它", "orange")
    f.text(430, 200, "行为策略这次选了右动作，用来探索。", size=14)
    f.region(36, 240, 420, 130)
    f.text(56, 270, "SARSA", size=16, weight=700, color=BLUE)
    f.text(56, 302, "目标 = 1 + 0.9 × 0 = 1.0", size=18, font="serif", style="italic")
    f.text(56, 336, "用实际采取的下一步。跟着当前行为学。", size=14, color=MUTED)
    f.region(480, 240, 444, 130)
    f.text(500, 270, "Q-learning", size=16, weight=700, color=GREEN)
    f.text(500, 302, "目标 = 1 + 0.9 × 2 = 2.8", size=18, font="serif", style="italic")
    f.text(500, 336, "用下一状态里最大的 Q。学的是贪心策略。", size=14, color=MUTED)
    f.footnote(
        392,
        "两个目标来自同一条转移。SARSA 是同策略的：采样用什么策略，更新就评价什么策略。Q-learning 是离策略的：探索可以更随机，备份仍指向最大的动作。\n"
        "格子里的 Q 是为了把两种目标算清楚而设的，不是某个环境里测到的值。",
    )
    f.save("rl-07-sarsa-qlearning.svg")


def fig_reinforce() -> None:
    f = Fig(960, "策略梯度只改被采样到、并且回报高或低的动作", "没有出现在轨迹里的动作，这一次不会直接被改写。")
    rows = [
        (40, "这条轨迹的回报高", GREEN, "提高这些已采取动作的概率", "↑"),
        (210, "这条轨迹的回报低", RED, "降低这些已采取动作的概率", "↓"),
    ]
    actions = ["a", "b", "c", "d"]
    for y, title, color, note, mark in rows:
        f.text(36, y + 8, title, size=16, weight=700, color=color)
        for i, name in enumerate(actions):
            x = 36 + i * 150
            f.card(x, y + 28, 120, 52, name, "被采样到", "orange" if color == GREEN else "gray")
            f.text(x + 60, y + 104, mark, anchor="middle", size=20, weight=700, color=color)
        f.card(650, y + 28, 270, 52, "没采样的动作", "这次梯度不直接碰它", "gray")
        f.text(36, y + 136, note, size=14, color=MUTED)
    f.footnote(
        380,
        "更新方向是梯度上升：回报越高，log π(a_t | s_t) 被推得越大。时刻 t 之前已经拿到的奖励可以不放进这一项，期望梯度不变。\n"
        "再减去只依赖状态的基线，期望仍不变，方差通常会下降。优势就是扣掉这个基线之后的分量。",
    )
    f.save("rl-08-reinforce.svg")


def fig_actor() -> None:
    f = Fig(960, "Actor-Critic 把评价和决策分开", "λ 决定优势向后看一步，还是看到结局。")
    f.card(36, 48, 250, 90, "Critic", "估计 V(s)，评价当前状态", "purple")
    f.card(674, 48, 250, 90, "Actor", "输出 π(a | s)，真正做选择", "blue")
    f.card(330, 56, 300, 74, "优势", "做到的 − 预期的", "gold")
    f.arrow(286, 93, 330, 93, color=PURPLE)
    f.arrow(630, 93, 674, 93, color=GOLD)
    f.text(36, 170, "一步的时候，优势的估计就是 TD 误差", size=15)
    f.text(36, 198, "δ(t) = r(t+1) + γ V(s(t+1)) − V(s(t))", size=18, font="serif", style="italic")
    f.region(36, 236, 888, 130)
    f.text(56, 264, "GAE 的 λ", size=15, weight=700)
    f.line(56, 310, 880, 310, stroke=LINE, sw=2)
    f.circle(56, 310, 7, fill=ORANGE, stroke=ORANGE)
    f.circle(880, 310, 7, fill=BLUE, stroke=BLUE)
    f.text(56, 286, "λ = 0", size=14, weight=700, color=ORANGE)
    f.text(880, 286, "λ = 1", anchor="end", size=14, weight=700, color=BLUE)
    f.text(56, 336, "只使用 δ_t，也就是只看下一步", size=13, color=MUTED)
    f.text(620, 336, "把后续 TD 误差按 γλ 加回去，直到结局", size=13, color=MUTED)
    f.footnote(
        386,
        "λ = 1 且终止状态的价值记为 0 时，优势估计回到折扣蒙特卡洛回报减去 V(s_t)。λ = 0 就是单独的一步 TD 误差。\n"
        "中间的 λ 在偏差和方差之间取一个点：向后看得越远，越接近真实回报，也越容易被整段轨迹的噪声拉动。",
    )
    f.save("rl-09-actor-critic.svg")


def _ppo_curve(advantage: float, eps: float = 0.2):
    """Return vertices of the PPO clipped objective as a function of the probability ratio."""
    lo, hi = 1 - eps, 1 + eps
    xs = [i / 50 for i in range(0, 101)]  # 0..2
    pts = []
    for rho in xs:
        unclipped = rho * advantage
        clipped = min(hi, max(lo, rho)) * advantage
        pts.append((rho, min(unclipped, clipped)))
    return pts


def fig_ppo() -> None:
    f = Fig(960, "PPO 截断后的目标对比率不再无限敏感", "ε = 0.2。优势分别取 +1 和 −1。")

    def panel(x, advantage, title, color):
        f.region(x, 24, 452, 340)
        f.text(x + 16, 50, title, size=15, weight=700, color=color)
        left, right = x + 52, x + 420
        top, bot = 86, 292
        ymin, ymax = -2.3, 1.5
        f.line(left, top, left, bot, stroke=GRAY, sw=1.1)
        f.line(left, bot, right, bot, stroke=GRAY, sw=1.1)

        def X(rho):
            return left + rho / 2 * (right - left)

        def Y(val):
            return bot - (val - ymin) / (ymax - ymin) * (bot - top)

        zero_y = Y(0)
        f.line(left, zero_y, right, zero_y, stroke=LINE, sw=1)
        for mark, lab in ((0.8, "1−ε"), (1.0, "1"), (1.2, "1+ε")):
            mx = X(mark)
            f.line(mx, bot, mx, bot + 5, stroke=GRAY, sw=1)
            f.text(mx, bot + 18, lab, anchor="middle", size=11, color=MUTED)
        pts = [(X(rho), Y(val)) for rho, val in _ppo_curve(advantage)]
        f.poly(pts, stroke=color, sw=2.2)
        f.text(left, top - 8, "截断目标", size=12, color=MUTED)
        f.text((left + right) / 2, bot + 38, "概率比率  π_new / π_old", anchor="middle", size=12, color=MUTED)

    panel(20, 1.0, "优势为正：高过 1+ε 后变平", GREEN)
    panel(488, -1.0, "优势为负：低于 1−ε 后变平", RED)
    f.footnote(
        384,
        "变平的那一段对比率的梯度是 0：正优势不再鼓励把概率提得更高，负优势也不再鼓励把概率压得更低。\n"
        "这限制的是旧样本继续把策略往外推的动力。它并不是在采样之前把比率硬性限制在区间里。ε = 0.2 是常用默认值，不是定理给出的唯一常数。",
    )
    f.save("rl-10-ppo-clip.svg")


def fig_rlhf() -> None:
    f = Fig(960, "RLHF 里有两道不同的约束", "一道对着采样时的旧策略，一道对着参考模型。")
    steps = [
        (28, "提示", "gray"),
        (176, "当前策略采样", "blue"),
        (360, "奖励模型打分", "gold"),
        (544, "减去 KL 惩罚", "teal"),
        (728, "PPO 更新", "orange"),
    ]
    for x, name, tone_name in steps:
        f.card(x, 56, 140, 56, name, None, tone_name)
    for x in (168, 352, 536, 720):
        f.arrow(x, 84, x + 8, 84)
    f.card(176, 150, 300, 64, "参考模型", "通常是指令微调后的模型，参数冻结", "teal")
    f.elbow([(326, 214), (326, 250), (616, 250), (616, 112)], color=TEAL, sw=1.4)
    f.text(340, 268, "KL 惩罚：不要离开参考模型太远", size=14, weight=650, color=TEAL)
    f.text(28, 310, "PPO 的比率：不要离开采集这批样本的旧策略太远", size=14, weight=650, color=ORANGE)
    f.text(28, 342, "奖励模型学的是偏好比较，本身也可以被钻空子。KL 限制策略能跑多远。", size=14)
    f.footnote(
        378,
        "常用的塑形奖励是：奖励模型的分数，减去 β 乘以当前策略相对参考模型的对数概率差。β 越大，最优策略越靠近参考模型。\n"
        "PPO 截断管的是同一次更新里、相对采样策略的步长。两道约束可以同时存在，它们比较的对象不同。",
    )
    f.save("rl-11-rlhf.svg")


def fig_dpo() -> None:
    f = Fig(960, "DPO 里配分函数在比较中消去", "偏好对直接变成策略上的分类损失。")
    f.card(36, 48, 200, 70, "更好的回答 y_w", "偏好数据里胜出的一方", "green")
    f.card(280, 48, 200, 70, "更差的回答 y_l", "同一提示下落败的一方", "red")
    f.text(36, 150, "最优策略下，奖励可以写回策略", size=15, weight=650)
    f.text(36, 182, "r(y) = β log(π*(y) / π_ref(y)) + β log Z(x)", size=16, font="serif", style="italic")
    f.region(36, 214, 888, 120)
    f.text(56, 242, "两份回答相减", size=15, weight=700)
    f.text(56, 274, "r(y_w) − r(y_l) = β log π*(y_w)/π_ref(y_w) − β log π*(y_l)/π_ref(y_l)", size=15, font="serif", style="italic")
    f.text(56, 306, "两边的 β log Z(x) 相同，相减后消失。比较不再需要单独的奖励网络。", size=14, color=MUTED)
    f.text(36, 364, "训练时把 π* 换成正在学习的 π_θ，让这个差经过 sigmoid 之后接近 1。", size=15)
    f.footnote(
        400,
        "这里的 π* 是 KL 约束下的最优策略，π_ref 是参考模型。Z(x) 是把参考模型按 exp(r/β) 重新加权后的配分函数，它只依赖提示，不依赖哪一份回答。\n"
        "基本的 DPO 在固定的偏好数据上训练，训练过程中不再从更新后的策略继续采样。",
    )
    f.save("rl-12-dpo.svg")


def fig_grpo() -> None:
    f = Fig(960, "GRPO 用同一道题的一组回答做基线", "奖励 1, 0, 1, 0。组均值 0.5，总体标准差 0.5。")
    rewards = [1, 0, 1, 0]
    advantages = [1, -1, 1, -1]
    f.text(28, 32, "同一个提示采样四份回答。优势 = (奖励 − 0.5) / 0.5。", size=15)
    base, scale = 200, 120
    for i, (reward, adv) in enumerate(zip(rewards, advantages)):
        x = 80 + i * 220
        if reward:
            h = reward * scale
            f.rect(x, base - h, 80, h, fill=GREEN, fo=0.9, rx=3)
        adv_color = GREEN if adv > 0 else RED
        f.text(x + 40, base + 22, f"回答 {i + 1}", anchor="middle", size=13, weight=650)
        f.text(x + 40, base + 44, f"奖励 {reward}", anchor="middle", size=13, color=MUTED)
        f.text(x + 40, base + 70, f"优势 {adv:+d}", anchor="middle", size=16, weight=700, color=adv_color)
    mean_y = base - 0.5 * scale
    f.line(48, mean_y, 912, mean_y, stroke=PURPLE, sw=1.5, dash="5 3")
    f.text(616, mean_y - 16, "组均值 0.5", size=13, weight=650, color=PURPLE)
    f.text(28, 300, "柱高是奖励。高于虚线的得到正优势，贴在零线上的得到负优势。", size=15)
    f.text(28, 328, "只看最终对错时，一份回答里的各个 token 共用这一个优势。更新仍可用 PPO 的截断比率。", size=15)
    f.footnote(
        366,
        "这里的标准差是总体标准差：四个偏差平方的平均是 0.25，开方得 0.5。有的实现用样本标准差，或在分母上加一个很小的数以免除零。\n"
        "组内优势的平均是 0。奖励来自判定程序时，这套更新就属于可验证奖励的训练；GRPO 规定的是优势怎么算，不是奖励从哪来。",
    )
    f.save("rl-13-grpo.svg")


def fig_tokens() -> None:
    f = Fig(960, "语言模型的轨迹往往只在结束时有奖励", "每个被采样的 token 都乘上同一个序列级优势。")
    tokens = ["设", "x = 2", "则", "x² = 4"]
    for i, tok in enumerate(tokens):
        x = 36 + i * 170
        f.card(x, 48, 140, 52, tok, "动作", "orange")
        f.text(x + 70, 128, "即时奖励 0", anchor="middle", size=13, color=MUTED)
        if i < 3:
            f.arrow(x + 148, 74, x + 162, 74, color=GRAY)
    f.card(720, 48, 200, 52, "检查通过", "序列奖励 +1", "gold")
    f.arrow(36 + 3 * 170 + 148, 74, 712, 74, color=GOLD)
    f.text(36, 176, "策略梯度里，这一整段的优势会乘在每一个已生成 token 的 log π 上。", size=15)
    f.text(36, 208, "(R − b) ∇ log π(y1) + (R − b) ∇ log π(y2) + …", size=16, font="serif", style="italic")
    f.text(36, 248, "前三个 token 没有自己的即时奖励。它们是否该得分，要靠最终检查倒推。", size=15)
    f.footnote(
        290,
        "状态是已经写出来的上下文，动作是下一个 token，策略是语言模型。和第一节的延迟奖励是同一类信用分配，只是轨迹通常长得多。\n"
        "相对参考模型的 KL 也是按 token 的对数概率差相加，所以离开参考模型的代价会摊在每一个 token 上。",
    )
    f.save("rl-14-token-credit.svg")


def fig_lineage() -> None:
    f = Fig(960, "每一种算法在修补前一种留下的困难", "顺序是问题的依赖，不是完整的编年史。")
    rows = [
        ("转移已知，可以在纸上备份", "贝尔曼方程，策略迭代与价值迭代"),
        ("模型未知，但可以等到结局", "蒙特卡洛，用从该步往后的回报"),
        ("希望走一步就更新", "时序差分，用 r + γV"),
        ("探索时仍想学贪心策略", "Q-learning 的 max 目标"),
        ("状态太多，表格放不下", "DQN：经验回放和目标网络"),
        ("想直接提高好动作的概率", "REINFORCE"),
        ("整段回报的方差太大", "优势，Actor-Critic，GAE"),
        ("一步不能离采样策略太远", "PPO 的截断概率比率"),
        ("只有成对偏好，没有逐步标签", "RLHF：奖励模型，再加 KL"),
        ("不想单独维持奖励模型", "DPO：配分函数在比较中消去"),
        ("奖励可判定，价值网络又贵", "GRPO：同一题的组内优势"),
    ]
    for i, (problem, method) in enumerate(rows):
        y = 28 + i * 46
        f.card(28, y, 390, 38, problem, None, "gray", title_size=13)
        f.arrow(426, y + 19, 458, y + 19, color=BLUE)
        f.card(466, y, 466, 38, method, None, "blue", title_size=13)
    f.footnote(
        28 + len(rows) * 46 + 8,
        "右边每一行都假定左边的困难已经出现。后面的方法没有废除前面的对象：PPO 仍使用优势，DPO 仍对应一个带 KL 约束的奖励最大化，GRPO 仍使用策略梯度那一类更新。",
    )
    f.save("rl-15-lineage.svg")


def build() -> None:
    fig_credit()
    fig_mdp()
    fig_discount()
    fig_advantage()
    fig_bellman()
    fig_mc_td()
    fig_sarsa()
    fig_reinforce()
    fig_actor()
    fig_ppo()
    fig_rlhf()
    fig_dpo()
    fig_grpo()
    fig_tokens()
    fig_lineage()


if __name__ == "__main__":
    # Sanity checks for numbers that also appear in the prose.
    assert abs(sum(0.5**k for k in range(4)) - 1.875) < 1e-9
    assert abs(sum(0.9**k for k in range(4)) - 3.439) < 1e-9
    curve_pos = _ppo_curve(1.0)
    assert abs(curve_pos[0][1]) < 1e-9
    assert abs(dict(curve_pos).get(1.2, min(curve_pos, key=lambda p: abs(p[0] - 1.2))[1]) - 1.2) < 0.05
    # At rho=2, positive advantage is clipped to 1.2; negative advantage is -2.
    assert abs(curve_pos[-1][1] - 1.2) < 1e-6
    curve_neg = _ppo_curve(-1.0)
    assert abs(curve_neg[0][1] - (-0.8)) < 1e-6
    assert abs(curve_neg[-1][1] - (-2.0)) < 1e-6
    build()
    print("rl figures written")
