"""Language-model, training, and systems figures."""

from __future__ import annotations

import math
from collections import Counter

from lib import (
    BLUE,
    GOLD,
    GRAY,
    GREEN,
    INK,
    LINE,
    MUTED,
    ORANGE,
    PURPLE,
    RED,
    TEAL,
    Fig,
    softmax,
    text_width,
)


def _pct_row(ps: list[float]) -> list[float]:
    units = [int(math.floor(p * 1000 + 1e-8)) for p in ps]
    left = 1000 - sum(units)
    order = sorted(range(len(ps)), key=lambda i: ps[i] * 1000 - units[i], reverse=True)
    for i in range(max(0, left)):
        units[order[i % len(ps)]] += 1
    return [u / 10 for u in units]


def _bars(f: Fig, x, y, labels, probs, w=150, h=120, color=BLUE) -> None:
    gap = 18
    bw = 36
    base = y + h
    for i, (lab, p) in enumerate(zip(labels, probs)):
        bx = x + i * (bw + gap)
        f.rect(bx, y, bw, h, fill="#F4F1EA", rx=3)
        bh = h * p
        f.rect(bx, base - bh, bw, bh, fill=color, rx=3)
        f.text(bx + bw / 2, base + 16, lab, anchor="middle", size=13, weight=650)
        f.text(bx + bw / 2, base - bh - 10, f"{p * 100:.1f}%", anchor="middle", size=11, weight=650, color=color)


def fig_17() -> None:
    f = Fig(960, "BPE 合并高频相邻片段", "数字是按合并规则数出来的，不是随便写的。")
    corpus = {
        ("l", "o", "w", "</w>"): 5,
        ("l", "o", "w", "e", "r", "</w>"): 2,
        ("n", "e", "w", "</w>"): 6,
        ("n", "e", "w", "e", "r", "</w>"): 3,
    }

    def pair_counts(data):
        counts = Counter()
        for word, freq in data.items():
            for a, b in zip(word, word[1:]):
                counts[(a, b)] += freq
        return counts

    def merge(data, pair):
        out = {}
        a, b = pair
        for word, freq in data.items():
            merged = []
            i = 0
            while i < len(word):
                if i < len(word) - 1 and word[i] == a and word[i + 1] == b:
                    merged.append(a + b)
                    i += 2
                else:
                    merged.append(word[i])
                    i += 1
            key = tuple(merged)
            out[key] = out.get(key, 0) + freq
        return out

    f.text(28, 30, "教学用语料。词尾用 </w> 标出，所以词中间的 w 和词尾的 w 不是同一对。", size=14)
    lines = ["low </w> × 5", "lower </w> × 2", "new </w> × 6", "newer </w> × 3"]
    for i, line in enumerate(lines):
        f.text(28, 64 + i * 22, line, size=15, font="serif")

    steps = []
    data = corpus
    for _ in range(3):
        best, count = pair_counts(data).most_common(1)[0]
        steps.append((best, count, data))
        data = merge(data, best)
    for i, ((a, b), count, _) in enumerate(steps):
        x = 280 + i * 220
        f.region(x, 52, 200, 120)
        f.text(x + 14, 76, f"第 {i + 1} 次合并", size=13, weight=700, color=ORANGE)
        f.text(x + 14, 104, f"{a}  +  {b}", size=16, font="serif", weight=700)
        f.text(x + 14, 130, f"相邻 {count} 次，全场最多", size=13)
        f.text(x + 14, 152, f"新符号  {a + b}", size=13, color=MUTED)

    f.text(280, 200, "三次合并之后，这四条词变成", size=14, weight=650)
    y = 224
    for word, freq in data.items():
        f.text(280, y, "  ".join(word) + f"    × {freq}", size=15, font="serif")
        y += 24
    f.region(28, 340, 904, 78)
    f.text(44, 366, "为什么是子词，而不是整词或单字", size=14, weight=700)
    f.text(44, 392, "整词表会因为词形变化胀得很大；单字又丢掉词内部的统计。BPE 停在中间。", size=14)
    f.footnote(
        436,
        "alignment 可能被切成 align 和 ment。这是讲义里的例子，不是上面这小份语料算出来的。\n"
        "次数并列时要规定先合并哪一对；这份语料前三次的冠军都是唯一的，所以没有用到并列规则。",
    )
    f.save("17_bpe-tokenization.svg")


def fig_18() -> None:
    f = Fig(960, "从文字到向量", "分词、查表、加位置，然后才进入 Transformer。")
    stages = [
        ("prompt", "我喜欢机器学习", "gray"),
        ("分词", "一种可能的切法", "orange"),
        ("token id", "示意整数", "gold"),
        ("查嵌入表", "第 i 行是一个向量", "blue"),
        ("加位置", "x + p", "purple"),
        ("Transformer", "得到上下文表示", "teal"),
        ("logits", "词表上的分数", "green"),
    ]
    # seven is too many for one row of wide cards. Two conceptual rows.
    ids = ["<bos>", "我", "喜欢", "机器", "学习"]
    id_nums = ["1", "204", "88", "513", "77"]
    f.chips(28, 48, ids, tones=["orange", "blue", "blue", "blue", "blue"], h=30, size=13)
    x = 28
    for tok, num in zip(ids, id_nums):
        w = text_width(tok, 13) + 22
        f.text(x + w / 2, 96, num, anchor="middle", size=12, color=MUTED)
        x += w + 8
    f.text(28, 122, "上面是一种示意切分和示意 id，不是某个真实词表。", size=12, color=MUTED)

    # embedding matrix sketch
    f.text(28, 160, "嵌入矩阵", size=14, weight=700)
    f.text(120, 160, "每一行对应一个 token id", size=13, color=MUTED)
    shown = {0: "1", 2: "204", 3: "88", 5: "513", 7: "77"}
    for r in range(8):
        highlight = r in shown
        f.rect(28, 180 + r * 16, 220, 14, fill=BLUE if highlight else "#F4F1EA", fo=0.85 if highlight else 1, rx=2)
        f.text(256, 187 + r * 16, f"id {shown[r]}" if highlight else "其他 id", size=11, baseline="middle", color=BLUE if highlight else MUTED)
    f.text(28, 320, "高亮的行被查出来，按顺序堆成 X，形状 T × d。", size=13)
    f.arrow(470, 230, 530, 230)
    f.card(530, 200, 160, 60, "加上位置", "内容向量 + p_t", "purple")
    f.arrow(690, 230, 740, 230)
    f.card(740, 190, 180, 80, "Transformer", "逐层更新这些向量", "teal")
    f.card(740, 290, 180, 52, "logits", "再 softmax 成概率", "green")
    f.arrow(830, 270, 830, 290)
    f.text(530, 290, "d 通常是几千这一量级。", size=13, color=MUTED)
    f.text(530, 314, "分词规则在训练前定死，使用时必须用同一套。", size=13, color=MUTED)
    f.footnote(
        360,
        "整条链路是：prompt → tokenization → token id → embedding lookup → Transformer → logits。\n"
        "长度、上下文窗口和计费通常按 token 数，而不是按字符数。特殊符号如起始符也占一个 id。",
    )
    f.save("18_tokenization-and-embedding.svg")


def fig_19() -> None:
    f = Fig(960, "温度怎样改变下一个 token 的分布", "温度不改变谁最大；top-k 和 top-p 会丢掉一些候选。")
    labels = ["学", "吃", "看"]
    logits = [math.log(p) for p in (0.7, 0.2, 0.1)]
    temps = [0.5, 1, 2]
    f.text(28, 28, "同一组 logits。上下文示意是“我喜欢”，τ = 1 时概率就是 0.7、0.2、0.1。", size=14)
    for i, tau in enumerate(temps):
        x = 40 + i * 300
        probs = softmax([z / tau for z in logits])
        f.text(x, 64, f"τ = {tau:g}", size=16, weight=700, color=ORANGE if tau != 1 else BLUE)
        _bars(f, x, 88, labels, probs, color=ORANGE if tau < 1 else BLUE if tau == 1 else TEAL)
        note = "更接近贪心" if tau < 1 else "讲义里的例子" if tau == 1 else "分布更平"
        f.text(x, 250, note, size=13, color=MUTED)
    f.text(28, 278, "温度不改变排序。贪心永远选“学”。τ 趋向 0 时接近贪心，趋向无穷时接近均匀。", size=14)

    f.region(28, 310, 904, 150)
    f.text(44, 334, "另外两个旋钮会先丢掉候选，再重新归一化", size=14, weight=700)
    base = [0.50, 0.25, 0.15, 0.10]
    names = ["学", "吃", "看", "玩"]
    kept_k = _pct_row([0.50 / 0.75, 0.25 / 0.75, 0, 0])
    kept_p = _pct_row([0.50 / 0.90, 0.25 / 0.90, 0.15 / 0.90, 0])
    f.text(44, 364, "原分布  50%  25%  15%  10%", size=14, font="serif")
    f.text(44, 392, f"top-k = 2：留下学、吃 → {kept_k[0]:.1f}%  {kept_k[1]:.1f}%", size=14)
    f.text(44, 418, f"top-p = 0.8：50+25 还不到 0.8，于是再留下看 → {kept_p[0]:.1f}%  {kept_p[1]:.1f}%  {kept_p[2]:.1f}%", size=14)
    f.text(44, 444, "这个例子里两者留下的集合不同。玩在两种规则下都被丢掉。", size=13, color=MUTED)
    f.footnote(
        476,
        "百分比按一位小数配平，使一行加起来是 100%。这些分布是为了把公式算清楚，不是模型的真实输出。\n"
        "top-p 取最小的一组候选，使累计概率达到阈值，然后只在这组里重新归一化。",
    )
    f.save("19_temperature-next-token-distribution.png".replace(".png", ".svg"))


def fig_20() -> None:
    f = Fig(960, "预训练、后训练、再使用", "先从材料里学规律，再用示范和评价把行为调准。")
    stages = [
        ("预训练", "海量文本上的\n下一 token", "得到基座模型", "blue"),
        ("指令微调", "问题配一份\n示范回答", "学会按要求答", "teal"),
        ("偏好优化", "同一问题的\n两个回答比一比", "更可取的更常出现", "orange"),
        ("可验证奖励", "答案、测试、\n格式能判定", "可判定的题更稳", "green"),
        ("使用", "权重保持不动\n条件来自上下文", "任务放进这一次的输入", "gray"),
    ]
    for i, (title, _body, out, tone) in enumerate(stages):
        x = 28 + i * 186
        f.card(x, 70, 168, 48, title, None, tone)
        lines = stages[i][1].split("\n")
        f.text(x + 84, 142, lines[0], anchor="middle", size=13)
        f.text(x + 84, 162, lines[1], anchor="middle", size=13)
        f.text(x + 84, 192, out, anchor="middle", size=12, weight=650, color=MUTED)
        if i < 4:
            f.arrow(x + 168, 94, x + 186, 94)
    f.line(28, 230, 28 + 4 * 186 - 18, 230, stroke=TEAL, sw=1.5)
    f.text(28, 252, "后训练：指令、偏好、可验证奖励可以组合，不必三选一。", size=14, weight=650, color=TEAL)
    f.text(28, 286, "使用时不再改权重。提示、材料和例子都只是这一次的条件。", size=14)
    f.footnote(
        324,
        "预训练的损失是每个位置的下一 token 负对数概率。文本自己提供输入和目标。\n"
        "基座模型会续写；后训练把它继续训练成更能按要求回答的模型。",
    )
    f.save("20_training-to-usage-workflow.svg")


def fig_21() -> None:
    f = Fig(960, "三条扩展路径", "预训练花算力换能力，后训练改行为，推理时再花额外计算。")
    cols = [
        (28, "预训练规模", BLUE),
        (344, "后训练", ORANGE),
        (660, "推理时计算", GREEN),
    ]
    for x, title, _tone in cols:
        f.region(x, 24, 300, 360)
        f.text(x + 16, 52, title, size=16, weight=700)
    f.text(44, 86, "固定训练算力时，", size=14)
    f.text(44, 110, "参数和数据要一起加。", size=14)
    f.card(44, 140, 250, 52, "只把模型做大", "数据不够就吃亏", "gray")
    f.card(44, 206, 250, 64, "Chinchilla 的建议", "大约 20 个 token / 1 个参数", "blue")
    f.text(44, 292, "代码、数学、文档、对话", size=13)
    f.text(44, 314, "提供的信号并不一样。", size=13, color=MUTED)
    f.text(44, 344, "这是当时算力范围里的估计。", size=12, color=MUTED)

    f.text(360, 86, "改的是行为，不是无限加大参数。", size=14)
    f.text(360, 124, "1  示范回答：指令微调", size=14)
    f.text(360, 154, "2  哪份回答更好：偏好", size=14)
    f.text(360, 184, "3  对不对：可验证奖励", size=14)
    f.text(360, 230, "三者可以接在同一个基座后面。", size=14)
    f.text(360, 264, "偏好优化不自动保证事实正确。", size=13, color=MUTED)
    f.text(360, 292, "可验证奖励用于能判定的题。", size=13, color=MUTED)

    f.text(676, 86, "深度：把一条解写得更长", size=14)
    f.text(676, 112, "推导、检查、再改。", size=13, color=MUTED)
    f.chips(676, 136, ["一步", "检查", "修正"], tone_name="green", h=28, size=12)
    f.text(676, 190, "宽度：独立写几条再挑选", size=14)
    f.chips(676, 214, ["解法 A", "解法 B", "解法 C"], tone_name="teal", h=28, size=12)
    f.text(676, 264, "验证器或相互比较，留下一条。", size=13)
    f.text(676, 300, "多花的是推理预算，不是参数。", size=13, color=MUTED)
    f.text(676, 328, "简单题不必把两条都用上。", size=13, color=MUTED)
    f.footnote(
        404,
        "20 token / 参数来自讲义对 Chinchilla 的概括，是计算量最优附近的经验比例，不是所有模型和所有数据都自动成立。\n"
        "图里没有画论文里的损失曲线，避免把示意图看成测量结果。思维链的中间 token 和普通 token 用的是同一种生成。",
    )
    f.save("21_three-scaling-laws.svg")


def fig_22() -> None:
    f = Fig(960, "多模态模型怎样接上语言模型", "各模态先变成向量，投影到同一维度，再进入骨干网络。")
    f.card(36, 70, 170, 90, "实验曲线", "一张图像", "blue")
    f.line(58, 130, 110, 92, stroke=BLUE, sw=1.6)
    f.line(58, 118, 150, 108, stroke=ORANGE, sw=1.6)
    f.card(36, 190, 170, 70, "比较两条曲线", "一句文字", "orange")
    f.arrow(206, 115, 270, 115)
    f.arrow(206, 225, 270, 160)
    f.card(270, 80, 180, 70, "视觉编码器", "图像或视频帧", "blue")
    f.card(270, 190, 180, 70, "分词 + 嵌入", "文字", "orange")
    f.arrow(450, 115, 520, 150)
    f.arrow(450, 225, 520, 190)
    f.card(520, 140, 160, 70, "投影", "对齐到同一维度", "purple")
    f.arrow(680, 175, 740, 175)
    f.card(740, 140, 180, 70, "语言模型", "一起读这些向量", "teal")
    f.text(740, 240, "输出通常仍是文字", size=13, weight=650)
    f.text(36, 300, "视频是带时间的画面，可以走视觉这条路。音频用自己的编码器，再投影进来。", size=14)
    f.text(36, 328, "生成图像或语音要另接解码器，不是每个多模态模型都有。", size=14, color=MUTED)
    f.footnote(
        364,
        "图对应讲义里的理解路径：曲线和句子一起成为输入。Qwen3-VL 这类模型把文字、图像和视频接到同一个骨干上。\n"
        "投影层的作用是把不同编码器的向量变到语言模型使用的维度，不是再做一次分词。",
    )
    f.save("22_multimodal-model-architecture.svg")


def fig_23() -> None:
    f = Fig(960, "混合专家层", "路由器为每个 token 挑选少数专家；总参数和激活参数不是同一个数。")
    f.card(36, 150, 110, 52, "一个 token", "x", "orange")
    f.arrow(146, 176, 200, 176)
    f.card(200, 150, 130, 52, "路由器", "给专家打分", "purple")
    f.arrow(330, 176, 368, 176, color=PURPLE)
    gates = [0.05, 0.41, 0.08, 0.37, 0.04, 0.03, 0.01, 0.01]
    chosen = {1, 3}
    for i, g in enumerate(gates):
        x = 370
        y = 48 + i * 36
        on = i in chosen
        f.rect(x, y, 160 * g / 0.41, 22, fill=GREEN if on else "#E7E3DC", rx=3)
        f.text(x + 168, y + 11, f"专家 {i + 1}", baseline="middle", size=12, weight=700 if on else 400, color=GREEN if on else MUTED)
    f.text(370, 348, "图中 8 选 2，只为看清路由。", size=13, color=MUTED)
    f.text(370, 370, "选中的输出按权重加起来。", size=13)
    f.region(700, 48, 230, 250)
    f.text(716, 76, "始终要算的部分", size=14, weight=700)
    f.text(716, 108, "注意力和其他共享层", size=13)
    f.text(716, 132, "每个 token 都经过。", size=13, color=MUTED)
    f.text(716, 170, "DeepSeek-V4-Pro", size=14, weight=700, color=BLUE)
    f.text(716, 198, "总参数约 1.6T", size=13)
    f.text(716, 220, "每 token 激活约 49B", size=13)
    f.text(716, 250, "1 个共享专家", size=13)
    f.text(716, 272, "384 个路由专家里选 6 个", size=13)
    f.footnote(
        400,
        "专家是一起训练出来的子网络，分工随数据形成，不是事先指定的学科。专家之间还要通信，负载不均会吃掉稀疏结构的收益。\n"
        "左侧的 8 选 2 不是 V4-Pro 的配置。右侧数字来自该模型的公开说明，用来区分总参数和激活参数。",
    )
    f.save("23_mixture-of-experts-layer.svg")


def fig_26() -> None:
    f = Fig(960, "Agent 的一轮循环", "模型决定下一步，工具和环境把文字变成操作和观察。")
    labels = [
        ("感知", "读入目标和材料", "blue"),
        ("推理", "理解当前状态", "purple"),
        ("规划", "决定下一步", "orange"),
        ("执行", "调用工具", "green"),
        ("观察", "看执行结果", "teal"),
    ]
    cx, cy, radius = 470, 230, 178
    centers = []
    for i, (name, sub, tone) in enumerate(labels):
        ang = -math.pi / 2 + i * 2 * math.pi / 5
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        centers.append((x, y, ang))
        f.card(x - 62, y - 28, 124, 56, name, sub, tone)
    for i, (x, y, ang) in enumerate(centers):
        ang2 = -math.pi / 2 + ((i + 1) % 5) * 2 * math.pi / 5
        # leave the cards before drawing the arrow
        a0 = ang + 0.48
        a1 = ang2 - 0.48
        if a1 < a0:
            a1 += 2 * math.pi
        f.arrow(
            cx + radius * math.cos(a0),
            cy + radius * math.sin(a0),
            cx + radius * math.cos(a1),
            cy + radius * math.sin(a1),
            color=INK,
            sw=1.4,
        )
    f.text(cx, cy - 8, "目标", anchor="middle", size=16, weight=700)
    f.text(cx, cy + 16, "分析数据并写成报告", anchor="middle", size=12, color=MUTED)
    f.footnote(
        430,
        "观察会回到下一轮的感知。执行可以是读文件、跑代码、检索或检查结果；模型负责理解和生成。\n"
        "五个词按讲义的顺序：感知、推理、规划、执行、观察。箭头是直线，画在圆周上，避免挡住文字。",
    )
    f.save("26_agent-iterative-cycle.svg")


def fig_31() -> None:
    f = Fig(960, "LoRA 用低秩增量改权重", "原权重冻结，可训练的是两个小矩阵。")
    f.card(40, 70, 180, 180, "W", "d × d，冻结", "gray")
    f.text(250, 160, "+", size=28, weight=700, baseline="middle")
    f.card(290, 70, 70, 180, "B", "d × r", "blue")
    f.text(380, 160, "×", size=24, weight=700, baseline="middle")
    f.card(410, 130, 180, 60, "A", "r × d", "orange")
    f.text(620, 160, "=", size=28, weight=700, baseline="middle")
    f.card(660, 70, 180, 180, "W + BA", "形状仍是 d × d", "green")
    f.text(40, 280, "前向：h = W x + B A x", size=16, font="serif", style="italic")
    f.text(40, 314, "例子：d = 4096，r = 8。可训练参数 2 × 4096 × 8 = 65,536。", size=15)
    f.text(40, 342, "全量更新是 4096² = 16,777,216。这份增量大约是全量的 1/256，也就是 0.39%。", size=15)
    f.text(40, 376, "B 常从 0 开始，所以训练刚开始时模型和原来一样。推理前可以把 BA 合并进 W。", size=14, color=MUTED)
    f.footnote(414, "秩 r 远小于 d，这是低秩这个名字的含义。合并之后，推理不再多一次小矩阵乘法。d 和 r 是示意里常用的量级。")
    f.save("31_lora-low-rank.svg")


def fig_32() -> None:
    f = Fig(960, "RLHF 和 DPO", "偏好数据可以先训练奖励模型，也可以直接写进损失函数。")
    f.region(28, 24, 446, 360)
    f.lead(44, 50, "a", "RLHF")
    f.card(60, 80, 360, 48, "同一 prompt 的两份回答", "标出哪一份更好", "gold")
    f.arrow(240, 128, 240, 156)
    f.card(80, 156, 320, 48, "训练奖励模型", "给回答打一个分数", "orange")
    f.arrow(240, 204, 240, 232)
    f.card(80, 232, 320, 56, "用 PPO 更新语言模型", "高分回答变得更可能", "blue")
    f.text(60, 312, "旁边有一个参考模型，限制不要偏离太远。", size=13)
    f.text(60, 338, "流程更灵活，也要稳住强化学习。", size=13, color=MUTED)
    f.region(490, 24, 442, 360)
    f.lead(506, 50, "b", "DPO")
    f.card(522, 80, 360, 48, "还是同一类偏好对", "更好 / 更差", "gold")
    f.arrow(702, 128, 702, 180)
    f.card(542, 180, 340, 70, "直接更新策略", "不另训一个奖励模型", "green")
    f.text(522, 280, "损失函数里带着参考模型，", size=13)
    f.text(522, 304, "提高偏好回答的相对概率。", size=13)
    f.text(522, 338, "步骤更少，目标就是这个相对偏好。", size=13, color=MUTED)
    f.footnote(
        404,
        "两者解决的是“哪份回答更可取”，常用于帮助性、风格、安全性和格式。它们不自动保证事实或数学正确。\n"
        "奖励模型学的是比较，不是一份绝对的真理分数。",
    )
    f.save("32_rlhf-vs-dpo.svg")


def fig_33() -> None:
    f = Fig(960, "检索增强，以及把检索交给模型", "文档留在模型外面；模型每次只把用到的片段放进上下文。")
    f.region(28, 24, 446, 300)
    f.lead(44, 48, "a", "经典 RAG")
    steps = ["问题", "检索相关片段", "片段和问题一起进入上下文", "按资料生成回答"]
    for i, name in enumerate(steps):
        f.card(60, 78 + i * 58, 360, 42, name, None, "blue" if i < 3 else "green")
        if i < 3:
            f.arrow(240, 120 + i * 58, 240, 136 + i * 58)
    f.region(490, 24, 442, 300)
    f.lead(506, 48, "b", "由模型决定查什么")
    f.card(540, 80, 300, 48, "模型看过当前结果", None, "orange")
    f.arrow(690, 128, 690, 156)
    f.card(540, 156, 300, 48, "再调用搜索、grep 或数据库", None, "teal")
    f.arrow(690, 204, 690, 232)
    f.card(540, 232, 300, 48, "决定还要不要再查", None, "purple")
    f.text(28, 348, "资料更新时改的是文档，不是模型权重。", size=14, weight=650)
    f.text(28, 376, "稳定、可预期的查询用经典 RAG 更省；要多步核对时，把“查什么”交给模型更灵活。", size=14)
    f.footnote(
        412,
        "检索可以是关键词，也可以是把问题和片段都编成向量再比相似度。两种做法都能给经典 RAG 用。\n"
        "模型决定查询之后，真正的查找仍可以由一个专门的检索器完成。",
    )
    f.save("33_rag-and-agentic-retrieval.svg")


def fig_34() -> None:
    f = Fig(960, "贝尔曼方程的一步回溯", "当前价值等于这一步的期望奖励，加上折扣后的下一状态价值。")
    f.card(40, 150, 120, 64, "状态 s", "现在在这里", "blue")
    f.arrow(160, 166, 250, 100)
    f.arrow(160, 198, 250, 250)
    f.card(250, 70, 140, 52, "动作 a", "按 π 选出", "orange")
    f.card(250, 230, 140, 52, "另一个动作", "π 给出概率", "orange")
    f.arrow(390, 96, 500, 96)
    f.arrow(390, 256, 500, 256)
    f.card(500, 70, 180, 52, "s′", "R + γ V(s′)", "green")
    f.card(500, 230, 180, 52, "s″", "R + γ V(s″)", "green")
    f.text(40, 330, "V(s) = Σ_a π(a|s) Σ_s′ P(s′|s,a) [ R(s,a,s′) + γ V(s′) ]", size=16, font="serif", style="italic")
    f.text(40, 366, "图里只展开了两个动作、各自一个下一状态。公式里的求和把其余分支也算进去。", size=14)
    f.text(40, 396, "它没有新的假设：只是把 G(t) = r(t+1) + γ G(t+1) 取了期望。", size=14)
    f.footnote(
        432,
        "最优方程把对动作的加权平均换成 max。价值方法用这个递归做动态规划或时序差分，就不必真的把无限长的回报加到底。\n"
        "P 和 R 是环境的转移和奖励。策略 π 决定动作的概率。",
    )
    f.save("34_bellman-backup.svg")


def fig_35() -> None:
    f = Fig(960, "投机解码", "小模型先写一段草稿，主模型用一次前向验收。")
    f.text(28, 36, "草稿模型较快，一次写几个 token", size=14, weight=650, color=MUTED)
    draft = ["习", "惯", "上", "下"]
    x = 28
    for i, tok in enumerate(draft):
        f.chip(x, 56, tok, "gray", h=32, size=14)
        if i < 3:
            f.arrow(x + 46, 72, x + 62, 72, color=GRAY)
        x += 78
    f.text(360, 72, "串行，但是便宜", size=13, color=MUTED, baseline="middle")

    f.rect(28, 112, 300, 36, fill=BLUE, fo=0.12, stroke=BLUE, rx=6)
    f.text(178, 130, "主模型一次前向，并行看这四步", anchor="middle", baseline="middle", size=13, weight=650, color=BLUE)

    f.text(28, 176, "按接受规则留下前缀，第一处不一致就改写，后面的草稿作废", size=14, weight=650)
    results = [("习", "留下", "green"), ("惯", "留下", "green"), ("中", "改写", "orange"), ("下", "丢弃", "red")]
    x = 28
    for tok, status, tone in results:
        f.card(x, 200, 120, 56, tok, status, tone)
        x += 136
    f.footnote(
        280,
        "标准的接受—拒绝规则保证：这样采样的分布和主模型自己逐步采样相同，只是串行的步数更少。\n"
        "图里的“习 / 惯 / 中”是示意的接受结果，不是一次真实推理。多 token 预测可以为主模型提供这种草稿。",
    )
    f.save("35_speculative-decoding.svg")


def fig_36() -> None:
    f = Fig(960, "为什么注意力要除以 √d_k", "点积的标准差大约是 √d_k，不缩放时 softmax 会过于尖锐。")
    f.text(28, 32, "设 q、k 的各分量独立、均值 0、方差 1。点积是 d_k 个乘积之和，方差是 d_k。", size=15)
    f.text(28, 60, "下面用 d_k = 64，√d_k = 8。四份示意点积取在 1、0.5、0、−0.5 个标准差上。", size=15)
    raw = [8, 4, 0, -4]
    names = ["1σ", "0.5σ", "0", "−0.5σ"]
    raw_p = softmax(raw)
    scaled_p = softmax([v / 8 for v in raw])
    f.text(40, 100, "不除", size=16, weight=700, color=RED)
    f.text(40, 124, "分数  8,  4,  0,  −4", size=14, font="serif")
    _bars(f, 40, 150, names, raw_p, color=RED)
    f.text(480, 100, "除以 8 之后", size=16, weight=700, color=BLUE)
    f.text(480, 124, "分数  1,  0.5,  0,  −0.5", size=14, font="serif")
    _bars(f, 480, 150, names, scaled_p, color=BLUE)
    f.text(40, 320, "左边几乎把全部质量给了第一名。右边仍然分得清高下，但其他候选还留着梯度。", size=15)
    f.footnote(
        356,
        "这是方差论证，不是从某个训练好的模型里读出来的分数。softmax 对尺度很敏感：分数整体变大，分布就更尖。\n"
        "除以 √d_k 把这个尺度拉回大约方差为 1 的范围。百分比按图中的精确 softmax 取一位小数。",
    )
    f.save("36_scaled-dot-product-variance.svg")


def build() -> None:
    fig_17()
    fig_18()
    fig_19()
    fig_20()
    fig_21()
    fig_22()
    fig_23()
    fig_26()
    fig_31()
    fig_32()
    fig_33()
    fig_34()
    fig_35()
    fig_36()
