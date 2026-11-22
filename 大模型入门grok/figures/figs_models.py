"""Generative-model and reinforcement-learning figures."""

from __future__ import annotations

import math
import random

from lib import (
    BLUE,
    GOLD,
    GRAY,
    GREEN,
    INK,
    LINE,
    MUTED,
    ORANGE,
    PANEL,
    PURPLE,
    RED,
    TEAL,
    DIGIT_3,
    DIGIT_5,
    DIGIT_8,
    Fig,
    bits,
)


def _alpha_bar(t: float, T: int = 1000, s: float = 0.008) -> float:
    def f(u: float) -> float:
        return math.cos((u / T + s) / (1 + s) * math.pi / 2) ** 2

    return f(t) / f(0)


def fig_10() -> None:
    f = Fig(960, "自编码器通过重建学习紧凑表示", "784 维图像压到 16 维，再重建回来。")
    f.text(28, 30, "压缩再重建。瓶颈只有 16 个数，留得下的是共同结构。", size=15, weight=650)
    f.glyph(48, 70, bits(DIGIT_5), cell=9)
    f.text(48, 156, "输入 x", size=13, weight=650)
    f.text(48, 176, "28×28 = 784", size=12, color=MUTED)
    f.arrow(140, 106, 210, 106)
    f.card(210, 78, 150, 56, "编码器", "784 → 16", "blue")
    f.arrow(360, 106, 420, 106)
    # 16-d bottleneck drawn as a thin vector
    for i in range(16):
        f.rect(430, 78 + i * 4.2, 36, 3.4, fill=ORANGE, fo=0.85, rx=1)
    f.text(422, 160, "z", size=16, font="serif", style="italic", weight=700, color=ORANGE)
    f.text(422, 180, "16 维瓶颈", size=12, color=MUTED)
    f.arrow(490, 106, 560, 106)
    f.card(560, 78, 150, 56, "解码器", "16 → 784", "green")
    f.arrow(710, 106, 780, 106)
    f.glyph(790, 70, bits(DIGIT_5), cell=9)
    f.text(790, 156, "重建  x̂", size=13, weight=650)
    f.line(80, 200, 80, 230, stroke=RED, sw=1.2)
    f.line(820, 200, 820, 230, stroke=RED, sw=1.2)
    f.line(80, 230, 820, 230, stroke=RED, sw=1.2)
    f.text(450, 250, "损失比较的是 x 和 x̂", anchor="middle", size=13, weight=650, color=RED)

    f.region(28, 280, 440, 110)
    f.text(44, 306, "用法一：拿走编码器", size=14, weight=700)
    f.text(44, 332, "z 用来可视化、检索、聚类，", size=13)
    f.text(44, 354, "或作为下游模型的特征。", size=13)
    f.region(484, 280, 448, 110)
    f.text(500, 306, "用法二：看重建误差", size=14, weight=700)
    f.text(500, 332, "没见过的异常往往重建得更差。", size=13)
    f.text(500, 354, "普通 AE 还没有采样规则。", size=13, color=MUTED)
    f.footnote(410, "格子画的是示意数字，不是 MNIST 里的某一张。损失用的是讲义里的平方误差。")
    f.save("10_autoencoder-reconstruction.svg")


def fig_11() -> None:
    f = Fig(960, "去噪自编码器", "输入是扰动后的图像，重建目标仍是干净图像。")
    f.glyph(40, 70, bits(DIGIT_5), cell=9)
    f.text(40, 158, "干净的 x", size=13, weight=650)
    f.arrow(130, 106, 190, 106, color=GRAY)
    f.text(145, 96, "加扰动", size=12, color=MUTED, anchor="middle")
    f.glyph(200, 70, bits(DIGIT_5), cell=9, noise=0.55, seed=3)
    f.text(200, 158, "网络的输入", size=13, weight=650)
    f.arrow(290, 106, 360, 106)
    f.card(360, 80, 200, 56, "编码器 + 解码器", "利用稳定结构", "blue")
    f.arrow(560, 108, 640, 108)
    f.glyph(650, 70, bits(DIGIT_5), cell=9)
    f.text(650, 158, "重建", size=13, weight=650, color=GREEN)
    # Target comes from the clean image, not the noisy one.
    f.elbow([(70, 200), (70, 240), (680, 240), (680, 200)], color=GREEN, sw=1.5)
    f.text(300, 258, "重建目标是干净的 x，不是带噪输入", size=14, weight=650, color=GREEN)
    f.footnote(
        300,
        "扰动可以是噪声，也可以是遮挡。模型要靠图像里稳定的笔画和形状把干净内容找回来。\n"
        "带噪图只是输入。损失仍然量在干净图像和重建结果之间。",
    )
    f.save("11_denoising-autoencoder.svg")


def fig_12() -> None:
    f = Fig(960, "掩码自编码器", "编码器只看可见 patch，解码器才放入 mask token。")
    visible = {(0, 1), (0, 4), (1, 2), (2, 0), (2, 5), (3, 3), (4, 1), (4, 4), (5, 2)}
    cell = 22
    ox, oy = 40, 70
    for r in range(6):
        for c in range(6):
            on = (r, c) in visible
            f.rect(ox + c * cell, oy + r * cell, cell - 3, cell - 3, fill=BLUE if on else "#E6E2DA", fo=0.9 if on else 1, stroke=LINE, rx=2)
            if not on:
                f.text(ox + c * cell + (cell - 3) / 2, oy + r * cell + (cell - 3) / 2, "×", anchor="middle", baseline="middle", size=11, color=FAINT_COLOR())
    f.text(40, 214, "6×6 = 36 个 patch", size=13, weight=650)
    f.text(40, 234, f"{len(visible)} 个可见，{36 - len(visible)} 个被遮住", size=13)
    f.text(40, 254, "遮住的比例是 75%。", size=13, color=MUTED)

    f.arrow(190, 130, 250, 90)
    f.card(250, 64, 200, 64, "编码器", "只接收可见 patch", "blue")
    f.text(250, 148, "可见 patch 仍带着原来的位置。", size=12, color=MUTED)
    f.arrow(450, 96, 520, 96)
    f.card(520, 64, 200, 64, "解码器", "可见表示 + mask token", "green")
    f.text(520, 148, "mask token 到这里才出现。", size=12, color=MUTED)
    # loss only on masked
    f.text(520, 190, "损失主要算在被遮住的位置。", size=13, weight=650, color=RED)
    masked_positions = [(r, c) for r in range(6) for c in range(6) if (r, c) not in visible]
    f.text(520, 214, f"也就是这 {len(masked_positions)} 个打叉的 patch。", size=13, color=MUTED)
    f.region(250, 250, 470, 78)
    f.text(266, 276, "和去噪自编码器的差别", size=14, weight=700)
    f.text(266, 302, "去噪：整张图都进编码器。MAE：编码器看不到被遮住的 patch。", size=13)
    f.footnote(
        348,
        "75% 是 MAE 论文里常见的遮挡比例，不是必须唯一的数字。可见 patch 的位置在图里是固定挑的，用来数清楚 9 和 27。\n"
        "解码器要有位置编码，否则它不知道该把哪一块填回哪个格子。",
    )
    f.save("12_masked-autoencoder-mae.svg")


def FAINT_COLOR() -> str:
    from lib import FAINT

    return FAINT


def fig_13() -> None:
    f = Fig(960, "VAE 把潜变量变成可以采样的分布", "重参数化让梯度经过 μ 和 σ；生成时不再使用编码器。")
    f.region(28, 24, 560, 340)
    f.lead(44, 48, "a", "训练：重建，同时把分布拉向先验")
    f.card(44, 78, 90, 48, "x", "一张图像", "gray")
    f.arrow(134, 102, 170, 102)
    f.card(170, 72, 120, 60, "编码器", "输出 μ 和 σ", "blue")
    f.arrow(290, 90, 340, 78)
    f.arrow(290, 114, 340, 130)
    f.card(340, 58, 100, 40, "μ(x)", "均值", "teal")
    f.card(340, 112, 100, 40, "σ(x)", "标准差", "teal")
    f.card(340, 168, 140, 44, "ε ~ N(0, I)", "抽样，反传时当常数", "gold")
    f.arrow(390, 98, 470, 230)
    f.arrow(390, 152, 470, 240)
    f.arrow(410, 212, 470, 250)
    f.card(470, 214, 90, 52, "z", "μ + σ⊙ε", "orange")
    f.text(44, 240, "梯度沿 μ、σ 走，不穿过“怎样抽出 ε”。", size=13)
    f.text(44, 268, "重建项希望解码器把概率放在原来的 x 上。", size=13)
    f.text(44, 296, "KL 把 q(z|x) 拉向 N(0, I)。", size=13)
    f.text(44, 328, "两件事同时做。", size=13, color=MUTED)

    f.region(604, 24, 328, 340)
    f.lead(620, 48, "b", "生成：编码器退出")
    f.card(640, 90, 160, 52, "z ~ N(0, I)", "从先验抽样", "gold")
    f.arrow(720, 142, 720, 180)
    f.card(640, 180, 160, 52, "解码器", "p(x | z)", "green")
    f.arrow(720, 232, 720, 268)
    f.glyph(690, 268, bits(DIGIT_3), cell=6)
    f.text(750, 292, "新样本", size=13, weight=650, color=GREEN)
    f.text(620, 330, "换一个 z，就换一张图。", size=13)
    f.footnote(
        382,
        "z = μ + σ⊙ε 是重参数化：随机性来自 ε，μ 和 σ 仍能收到梯度。生成时直接从先验抽样，不再把某张输入编码一遍。\n"
        "训练损失是讲义里的重建负对数概率加上 KL，也就是在最小化负 ELBO。",
    )
    f.save("13_vae-latent-sampling.svg")


def fig_14() -> None:
    f = Fig(960, "GAN 用判别器给生成器反馈", "两步交替更新；判别器在更新生成器时保持不动。")
    f.card(40, 70, 120, 52, "z", "随机向量", "gold")
    f.arrow(160, 96, 210, 96)
    f.card(210, 70, 150, 52, "生成器 G", "z → 图像", "blue")
    f.arrow(360, 96, 430, 96)
    f.card(430, 70, 140, 52, "生成图像", "x̃", "orange")
    f.card(430, 160, 140, 52, "真实图像", "来自数据", "green")
    f.arrow(570, 96, 640, 140)
    f.arrow(570, 186, 640, 160)
    f.card(640, 120, 160, 64, "判别器 D", "判断来源", "purple")
    f.text(820, 152, "分数", size=13, weight=650, baseline="middle")

    f.region(40, 250, 430, 120)
    f.text(56, 276, "第 1 步  更新判别器", size=15, weight=700)
    f.text(56, 304, "真实样本标成真实，生成样本标成生成。", size=13)
    f.text(56, 328, "标签由样本来源决定，不用人工另标。", size=13, color=MUTED)
    f.region(490, 250, 442, 120)
    f.text(506, 276, "第 2 步  更新生成器", size=15, weight=700)
    f.text(506, 304, "判别器参数固定，像一把暂时不动的尺子。", size=13)
    f.text(506, 328, "生成器被推向更高的“真实”分数。", size=13, color=MUTED)

    f.text(40, 400, "常见失败", size=13, weight=700, color=MUTED)
    f.chips(120, 386, ["模式崩溃：只会少数几种", "判别器过强：梯度消失", "两边拉锯：损失震荡"], tone_name="gray", h=28, size=12)
    f.footnote(
        436,
        "生成时只保留生成器：再抽一个 z，就得到一张新图。判别器的标准一直在变，所以训练比固定目标的重建更不稳定。\n"
        "模式崩溃、梯度消失和震荡是这套交替训练里常见的失败，不是某一次运行的实测曲线。",
    )
    f.save("14_gan-generator-discriminator.svg")


def fig_15() -> None:
    f = Fig(960, "扩散模型的加噪与去噪", "前向加噪不学习；网络学习的是预测被加入的噪声。")
    f.lead(28, 28, "a", "前向：从数据走到噪声，这一步不用训练")
    times = [0, 250, 500, 750, 1000]
    for i, t in enumerate(times):
        a = _alpha_bar(t)
        x = 36 + i * 150
        f.glyph(x, 52, bits(DIGIT_5), cell=7, noise=math.sqrt(max(0.0, 1 - a)), seed=10 + i)
        f.text(x, 120, f"t = {t}", size=12, weight=650)
        f.text(x, 138, f"√ᾱ = {math.sqrt(a):.2f}", size=11, color=MUTED)
        f.text(x, 154, f"√(1−ᾱ) = {math.sqrt(max(0.0, 1 - a)):.2f}", size=11, color=MUTED)
        if i < len(times) - 1:
            f.arrow(x + 62, 78, x + 96, 78, color=GRAY)
    f.text(36, 182, "x_t = √ᾱ_t x_0 + √(1−ᾱ_t) ε。系数来自 T = 1000 的余弦调度。", size=13)

    f.lead(28, 220, "b", "训练与采样是两条不同的用法")
    f.region(28, 244, 440, 130)
    f.text(44, 270, "训练", size=15, weight=700, color=BLUE)
    f.text(44, 298, "抽一张 x_0、一个等级 t、一份噪声 ε。", size=13)
    f.text(44, 320, "让 ε_θ(x_t, t) 去预测这份 ε。", size=13)
    f.text(44, 344, "损失是两者之差的平方。", size=13, color=MUTED)
    f.region(484, 244, 448, 130)
    f.text(500, 270, "采样", size=15, weight=700, color=ORANGE)
    f.text(500, 298, "从新的纯噪声 x_T 出发。", size=13)
    f.text(500, 320, "反复：预测噪声，再更新成更干净的 x。", size=13)
    f.text(500, 344, "走到 t = 0，得到一张新图。", size=13, color=MUTED)
    f.footnote(
        392,
        "更新不是把预测噪声原样减掉，系数由 α_t、β_t 决定。网络可以是 U-Net，也可以是 Transformer，例如 DiT。\n"
        "格子按公式把信号和噪声混在一起，只说明“信号变少、噪声变多”，不是某张真实生成结果。",
    )
    f.save("15_diffusion-forward-reverse-process.svg")


def _blob(f: Fig, cx, cy, color, label) -> None:
    f.circle(cx, cy, 28, fill=color, fo=0.18, stroke=color, sw=1.4)
    f.text(cx, cy + 46, label, anchor="middle", size=12, weight=650, color=color)


def fig_16() -> None:
    f = Fig(960, "反向 SDE、概率流 ODE 与 Flow Matching", "边缘分布可以相同，单条轨迹不必相同。")
    panels = [
        (28, "a", "反向 SDE", "每一步还有随机噪声", RED),
        (344, "b", "概率流 ODE", "去掉随机项后的漂移", BLUE),
        (660, "c", "Flow Matching", "直接学习速度场", GREEN),
    ]
    rng = random.Random(7)
    for x, letter, title, sub, color in panels:
        f.region(x, 24, 300, 360)
        f.lead(x + 16, 48, letter, title)
        f.text(x + 16, 72, sub, size=12, color=MUTED)
        _blob(f, x + 70, 180, GRAY, "噪声")
        _blob(f, x + 230, 180, GREEN, "数据")
        for k in range(4):
            y0 = 150 + k * 16
            y1 = 150 + (k * 9) % 40
            if letter == "a":
                pts = [(x + 70, y0)]
                cx0 = x + 70
                for step in range(6):
                    cx0 += 26
                    y0 = max(120, min(240, y0 + rng.uniform(-14, 14)))
                    pts.append((cx0, y0))
                pts.append((x + 230, y1))
                f.poly(pts, stroke=color, sw=1.4, arrow=True)
            elif letter == "b":
                y0 = 150 + k * 16
                y1 = 156 + (k * 9) % 36
                f.path(
                    f"M {x+100} {y0} Q {x+155} {y0 - 62} {x+198} {y1}",
                    stroke=color,
                    sw=1.7,
                    arrow=True,
                )
            else:
                f.arrow(x + 70, 150 + k * 16, x + 222, 150 + (k * 9) % 40, color=color, sw=1.5)
        f.text(x + 16, 300, "同一起点可以有很多条轨迹。" if letter == "a" else "同一时刻的分布与左图一致。" if letter == "b" else "线性条件路径是直线。", size=12.5)
        f.text(x + 16, 322, "步数通常更多。" if letter == "a" else "轨迹是确定的曲线。" if letter == "b" else "往往可以用更少的步数。", size=12.5, color=MUTED)
        f.text(x + 16, 348, "示意轨迹，不是数值积分的输出。", size=11.5, color=MUTED)
    f.footnote(
        404,
        "扩散的前向过程是随机微分方程。概率流 ODE 去掉随机项，并调整漂移，使每个时刻的边缘分布保持不变。\n"
        "Flow Matching 直接拟合一条从噪声分布到数据分布的速度场。条件流匹配里常用直线插值；不是所有 flow 模型都只能走直线。",
    )
    f.save("16_flow-matching-vs-diffusion.svg")


def fig_27() -> None:
    f = Fig(960, "智能体与环境", "动作进入环境，环境返回奖励和下一状态。")
    f.region(48, 36, 300, 180)
    f.text(198, 64, "智能体", anchor="middle", size=16, weight=700, color=BLUE)
    f.text(198, 96, "看见状态  s_t", anchor="middle", size=14)
    f.text(198, 122, "按策略  π(a | s)  选动作", anchor="middle", size=14)
    f.text(198, 148, "动作  a_t", anchor="middle", size=14, weight=650, color=ORANGE)
    f.text(198, 176, "策略本身可以是随机的", anchor="middle", size=12, color=MUTED)

    f.region(560, 36, 340, 180)
    f.text(730, 64, "环境", anchor="middle", size=16, weight=700, color=GREEN)
    f.text(730, 100, "收下 a_t", anchor="middle", size=14)
    f.text(730, 128, "给出奖励  r(t+1)", anchor="middle", size=14, weight=650, color=GOLD)
    f.text(730, 156, "进入下一状态  s(t+1)", anchor="middle", size=14)
    f.text(730, 184, "转移也可以是随机的", anchor="middle", size=12, color=MUTED)

    f.arrow(360, 90, 548, 90, color=ORANGE, sw=1.8)
    f.text(454, 78, "a_t", anchor="middle", size=14, weight=700, color=ORANGE)
    f.arrow(548, 160, 360, 160, color=GREEN, sw=1.8)
    f.text(454, 148, "r(t+1) ,  s(t+1)", anchor="middle", size=14, weight=700, color=GREEN)

    f.text(48, 250, "一条轨迹把这些接起来", size=14, weight=700)
    tape = ["s0", "a0", "r1", "s1", "a1", "r2", "s2", "…"]
    tones = ["blue", "orange", "gold", "blue", "orange", "gold", "blue", "gray"]
    f.chips(48, 268, tape, tones=tones, h=32, size=14)
    f.text(48, 330, "从 t 往后的折扣回报", size=14, weight=700)
    f.text(48, 358, "G(t) = r(t+1) + γ r(t+2) + γ² r(t+3) + …", size=18, font="serif", style="italic")
    f.text(48, 390, "γ 越接近 1，越在乎以后；越接近 0，越只看眼前。", size=14)
    f.footnote(
        424,
        "奖励写成 r(t+1)，和后文公式一致：先做动作 a(t)，再收到奖励并到达 s(t+1)。\n"
        "要优化的是回报的期望。状态价值 V 和动作价值 Q 是这个期望在不同条件下的名字，见下文。",
    )
    f.save("27_agent-environment-reinforcement-loop.svg")


def build() -> None:
    fig_10()
    fig_11()
    fig_12()
    fig_13()
    fig_14()
    fig_15()
    fig_16()
    fig_27()
