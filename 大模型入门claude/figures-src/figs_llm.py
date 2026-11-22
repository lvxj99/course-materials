"""第 8.6、10、11 节与附录 A.7：RL 回路、训练流程、三类扩展、多模态、MoE、RAG、Agent、贝尔曼递推。"""
import math

from svgkit import *


# ---------------------------------------------------------------------------
# 27 Agent 与 environment 的交互回路 + 折扣回报
# ---------------------------------------------------------------------------
def fig27():
    s = SVG(1000, 580, "强化学习的交互回路与折扣回报",
            "Agent 按策略选动作，环境返回奖励与下一状态；回报是未来奖励的折扣和。")
    # ---- 上：回路 ----
    s.text(500, 28, "① 交互回路：每一步都是“看状态 → 选动作 → 拿反馈”", size=16, weight="bold")
    ax, ay, aw, ah = 110, 92, 250, 106
    ex, ey = 640, 92
    s.box(ax, ay, aw, ah, "Agent（智能体）", key="q", sub="策略 $π$_{θ}($a$ | $s$)：看到状态，给出动作概率",
          size=16, subsize=12.5)
    s.box(ex, ey, aw, ah, "Environment（环境）", key="k", sub="根据动作，给出奖励和新状态",
          size=16, subsize=12.5)
    # 动作：上方弧线
    s.arrow([(ax + aw - 30, ay), (500, ay - 46), (ex + 30, ey)], color=main("q"), sw=2.2, curve=True)
    s.pill(500, ay - 22, "动作 $a$_{t}", key="q", size=14)
    # 奖励 + 状态：下方弧线
    s.arrow([(ex + 30, ey + ah), (500, ey + ah + 60), (ax + aw - 30, ay + ah)], color=main("k"), sw=2.2, curve=True)
    s.pill(440, ay + ah + 30, "奖励 $r$_{t+1}", key="v", size=14)
    s.pill(570, ay + ah + 30, "下一状态 $s$_{t+1}", key="k", size=14)
    s.text(500, 145, "下棋：落一子 / 机器人：一条电机指令", size=12.5, color=MUTED)

    # ---- 中：轨迹条 ----
    y1 = 290
    s.text(500, y1 - 28, "② 一条轨迹（trajectory）：状态、动作、奖励交替出现", size=16, weight="bold")
    seq = [("s", "$s$_{0}"), ("a", "$a$_{0}"), ("r", "$r$_{1}"), ("s", "$s$_{1}"), ("a", "$a$_{1}"), ("r", "$r$_{2}"),
           ("s", "$s$_{2}"), ("a", "$a$_{2}"), ("r", "$r$_{3}"), ("s", "$s$_{3}"), ("a", "$a$_{3}"), ("r", "$r$_{4}")]
    keymap = {"s": "k", "a": "q", "r": "v"}
    x = 92
    for i, (kind, lab) in enumerate(seq):
        s.pill(x, y1 + 6, lab, key=keymap[kind], size=14, pad=11)
        if i < len(seq) - 1:
            s.harrow(x + 22, x + 46, y1 + 6, color=LINE, sw=1.2, head=0.8)
        x += 70
    s.text(x - 20, y1 + 6, "…", size=18, color=MUTED)
    s.pill(150, y1 + 44, "状态", key="k", size=12.5)
    s.pill(210, y1 + 44, "动作", key="q", size=12.5)
    s.pill(270, y1 + 44, "奖励", key="v", size=12.5)

    # ---- 下：折扣权重条形 ----
    y2 = 380
    s.text(500, y2, "③ 回报：$G$_{t} = $r$_{t+1} + $γr$_{t+2} + $γ$^{2}$r$_{t+3} + … ——越远的奖励，乘上的折扣越小",
           size=15.5, weight="bold")
    bx, by, bw, bh = 150, 548, 46, 120  # 柱底基线 by
    s.line(bx - 20, by, bx + 10 * 70 + 10, by, color=BORDER, sw=1.2)
    for k in range(10):
        cx = bx + k * 70
        for g, key, off in ((0.9, "v", -12), (0.5, "gray", 12)):
            h = bh * g ** k
            s.rect(cx + off - 10, by - h, 20, h, fill=main(key) if key == "v" else "#B8BEC8", rx=2)
        s.text(cx + 1, by + 16, f"$r$_{{t+{k + 1}}}", size=12.5, color=MUTED)
        if k < 5:
            s.text(cx - 12, by - bh * 0.9 ** k - 10, f"{0.9 ** k:.2f}".rstrip("0").rstrip("."), size=12, color=main("v"))
    s.text(bx - 30, by - bh / 2, "折扣权重 $γ$^{k}", size=12.5, color=MUTED, anchor="end")
    # 图例
    lx = 790
    s.rect(lx, y2 + 28, 14, 14, fill=main("v"), rx=2)
    s.text(lx + 22, y2 + 35, "$γ$ = 0.9：远期奖励仍有分量", size=13, anchor="start")
    s.rect(lx, y2 + 54, 14, 14, fill="#B8BEC8", rx=2)
    s.text(lx + 22, y2 + 61, "$γ$ = 0.5：几乎只看眼前", size=13, anchor="start")
    s.save(OUT / "27_agent-environment-reinforcement-loop.svg")


# ---------------------------------------------------------------------------
# 20 从预训练、后训练到使用
# ---------------------------------------------------------------------------
def fig20():
    s = SVG(1100, 556, "从预训练、后训练到使用", "每个训练阶段用不同数据与信号更新权重，使用阶段权重固定。")
    cols = [  # x, w, key, 标题, 副标题
        (30, 220, "data", "预训练", "海量文本、代码"),
        (310, 220, "q", "监督微调 SFT", "指令—示范答案"),
        (590, 240, "attn", "偏好优化 / RLVR", "比较与验证"),
        (890, 180, "v", "使用", "权重固定"),
    ]
    # 顶部：训练 vs 使用
    s.brace(30, 44, 830, 44, "", color=main("loss"), depth=-8)
    s.text(430, 26, "训练：用数据和反馈更新权重", size=14.5, weight="bold", color=main("loss"))
    s.brace(890, 44, 1070, 44, "", color=main("v"), depth=-8)
    s.text(980, 26, "使用：不再改权重", size=14.5, weight="bold", color=main("v"))

    hy, hh = 58, 58
    for x, w, key, t, sub in cols:
        s.box(x, hy, w, hh, t, key=key, sub=sub, size=16, subsize=12.5)
    # 阶段之间的箭头和模型名
    tags = [(250, 310, "基础模型"), (530, 590, "指令模型"), (830, 890, "可用模型")]
    for x1, x2, tg in tags:
        s.harrow(x1 + 3, x2 - 3, hy + hh / 2 + 8, color=INK, sw=1.8)
        s.text((x1 + x2) / 2, hy + hh / 2 - 8, tg, size=12, color=INK, weight="bold")

    # 行 1：数据
    ry = 140
    s.text(30, ry - 4, "数据长什么样", size=13, color=MUTED, anchor="start", weight="bold")
    # 预训练：一段文本，下一个 token
    x, w = 30, 220
    s.rect(x, ry + 8, w, 92, fill=WHITE, stroke=BORDER, rx=8)
    s.text(x + 12, ry + 30, "df.groupby(\"a\").sum() 会把", size=12.5, anchor="start", family=MONO)
    s.text(x + 12, ry + 52, "相同 a 值的行合并，再对", size=12.5, anchor="start")
    s.text(x + 12, ry + 74, "其余列", size=12.5, anchor="start")
    s.pill(x + 108, ry + 74, "求和", key="data", size=12.5, pad=7, h=22)
    s.text(x + 136, ry + 74, "← 下一个 token", size=12, anchor="start", color=main("data"))
    # SFT：问答对
    x, w = 310, 220
    s.rect(x, ry + 8, w, 92, fill=WHITE, stroke=BORDER, rx=8)
    s.pill(x + 30, ry + 32, "指令", key="gray", size=12, pad=6, h=22)
    s.text(x + 58, ry + 32, "解释下面这段 groupby 代码", size=12.5, anchor="start")
    s.pill(x + 30, ry + 70, "示范", key="q", size=12, pad=6, h=22)
    s.text(x + 58, ry + 63, "这行代码按 a 分组，", size=12.5, anchor="start")
    s.text(x + 58, ry + 83, "对每组其余列求和……", size=12.5, anchor="start")
    # 偏好 + RLVR
    x, w = 590, 240
    s.rect(x, ry + 8, w, 42, fill=WHITE, stroke=BORDER, rx=8)
    s.pill(x + 30, ry + 29, "偏好", key="attn", size=12, pad=6, h=22)
    s.text(x + 58, ry + 29, "回答 A 优于 回答 B", size=12.5, anchor="start")
    s.rect(x, ry + 58, w, 42, fill=WHITE, stroke=BORDER, rx=8)
    s.pill(x + 30, ry + 79, "验证", key="v", size=12, pad=6, h=22)
    s.text(x + 58, ry + 79, "答案对比 / 测试运行：", size=12.5, anchor="start")
    s.text(x + 196, ry + 79, "✓", size=15, anchor="start", color=main("v"), weight="bold")
    s.text(x + 214, ry + 79, "✗", size=15, anchor="start", color=main("loss"), weight="bold")
    # 使用
    x, w = 890, 180
    s.rect(x, ry + 8, w, 92, fill=WHITE, stroke=BORDER, rx=8)
    items = ["提示（prompt）", "few-shot 示例", "检索资料（RAG）", "更多推理时计算"]
    for i, it in enumerate(items):
        s.text(x + 16, ry + 26 + i * 20, "· " + it, size=12.5, anchor="start")

    # 行 2：信号
    ry2 = 262
    s.text(30, ry2 - 4, "学习信号", size=13, color=MUTED, anchor="start", weight="bold")
    sig = [
        (30, 220, "data", "预测下一个 token", "交叉熵，自监督"),
        (310, 220, "q", "模仿示范答案", "只在回答位置算交叉熵"),
        (590, 240, "attn", "更好 / 更对的回答更常出现", "RLHF+PPO、DPO；RLVR+GRPO"),
        (890, 180, "v", "不学习，只改上下文", "上下文决定输出分布"),
    ]
    for x, w, key, a, b in sig:
        s.box(x, ry2 + 8, w, 52, a, key=key, sub=b, size=13.5, subsize=12, fill=WHITE, sw=1.2)

    # 行 3：同一个问题，各阶段的回答
    ry3 = 360
    s.text(30, ry3 - 4, "同一个问题：“请解释这段 groupby 代码”，此时的模型会怎样回答？", size=13, color=MUTED,
           anchor="start", weight="bold")
    answers = [
        (30, 220, "data", "基础模型：顺着往下续写", ["请解释这段 merge 代码。", "请解释这段 pivot 代码。", "第 3 章 习题……"],
         "像在续写一份习题集"),
        (310, 220, "q", "指令模型：开始回答问题", ["这行代码先按 a 分组，", "再对每组的其余列求和，", "返回一个新表。"],
         "学会了“问—答”的格式"),
        (590, 240, "attn", "可用模型：回答更好、更对", ["先说结论，再给一个小例子；", "指出 a 会变成索引，", "代码示例能直接运行。"],
         "偏好管表达，验证管正确"),
    ]
    for x, w, key, head, body, foot in answers:
        s.rect(x, ry3 + 8, w, 140, fill=light(key), stroke=main(key), sw=1.1, rx=10)
        s.text(x + 14, ry3 + 30, head, size=13.5, anchor="start", weight="bold")
        for i, ln in enumerate(body):
            s.text(x + 14, ry3 + 56 + i * 21, ln, size=12.5, anchor="start")
        s.text(x + 14, ry3 + 128, foot, size=12, anchor="start", color=MUTED)
    # 使用列：锁
    x = 890
    s.rect(x, ry3 + 8, 180, 140, fill=PANEL, stroke=BORDER, rx=10)
    s.text(x + 90, ry3 + 36, "同一组权重", size=13.5, weight="bold")
    # 锁形
    lx, ly = x + 90, ry3 + 78
    s.path(f"M{lx - 11},{ly - 6} L{lx - 11},{ly - 15} A11,11 0 0 1 {lx + 11},{ly - 15} L{lx + 11},{ly - 6}",
           stroke=main("v"), sw=3)
    s.rect(lx - 17, ly - 7, 34, 26, fill=main("v"), rx=4)
    s.text(x + 90, ry3 + 116, "换提示、加资料、多想，", size=12.5)
    s.text(x + 90, ry3 + 136, "只改变本次上下文", size=12.5)

    s.text(550, 534, "后训练的几种方法可以组合：SFT 先教基本行为，偏好优化调整回答质量，可验证奖励提升可判定任务的正确率。",
           size=12.5, color=MUTED)
    s.save(OUT / "20_training-to-usage-workflow.svg")


# ---------------------------------------------------------------------------
# 21 三类扩展：预训练 / 后训练 / 推理时计算
# ---------------------------------------------------------------------------
def _curve(s, x, y, w, h, xlabel, key):
    """示意曲线：x 轴为对数计算量，y 为能力；无具体数值。"""
    s.line(x, y + h, x + w, y + h, color=INK, sw=1.2)
    s.line(x, y + h, x, y, color=INK, sw=1.2)
    s.arrow([(x + w - 2, y + h), (x + w + 6, y + h)], color=INK, sw=1.2, head=0.8)
    s.arrow([(x, y + 2), (x, y - 6)], color=INK, sw=1.2, head=0.8)
    pts = []
    for i in range(41):
        u = i / 40
        pts.append((x + 8 + u * (w - 16), y + h - 8 - (h - 22) * (0.08 + 0.92 * (1 - math.exp(-2.2 * u)) / (1 - math.exp(-2.2)))))
    s.polyline(pts, stroke=main(key), sw=2.6)
    s.text(x + w / 2, y + h + 16, xlabel, size=12.5, color=MUTED)
    s.text(x - 8, y + h / 2, "能力", size=12.5, color=MUTED, anchor="end")
    s.text(x + w - 4, y + 6, "示意", size=12, color=MUTED, anchor="end")


def fig21():
    s = SVG(1100, 500, "三类扩展路径", "预训练、后训练和推理时计算分别在不同阶段增加计算预算。")
    W, gap, x0, y0, H = 340, 20, 30, 20, 466
    panels = [
        ("data", "① 预训练扩展", "更大的模型 + 更多训练 token", "改变权重", "loss"),
        ("q", "② 后训练扩展", "更多示范、偏好与强化学习", "改变权重", "loss"),
        ("v", "③ 推理时扩展", "回答一道题时多想、多试、多验证", "权重不变", "v"),
    ]
    for i, (key, title, what, wchg, wkey) in enumerate(panels):
        x = x0 + i * (W + gap)
        s.panel(x, y0, W, H, fill=WHITE, key=key)
        s.rect(x, y0, W, 46, fill=light(key), stroke=main(key), sw=1.1, rx=12)
        s.rect(x + 1, y0 + 30, W - 2, 16, fill=light(key))
        s.text(x + W / 2, y0 + 24, title, size=16.5, weight="bold")
        s.text(x + W / 2, y0 + 70, "预算加在哪：" + what, size=13.5)
        s.pill(x + W / 2, y0 + 102, wchg, key=wkey, size=13, weight="bold")
    # 面板 1 图标：层堆叠 + 文档堆
    x = x0
    iy = y0 + 140
    for k in range(5):
        s.rect(x + 50, iy + 82 - k * 17, 110, 13, fill=light("ffn"), stroke=main("ffn"), rx=3)
    s.text(x + 105, iy + 112, "更多层、更宽 → 更多参数", size=12.5, color=MUTED)
    s.text(x + 170, iy + 50, "×", size=18, color=MUTED)
    for k in range(4):
        s.rect(x + 200 + k * 7, iy + 34 - k * 7, 60, 56, fill=WHITE, stroke=main("data"), sw=1.2, rx=3)
    for k in range(4):
        s.line(x + 230, iy + 22 + k * 10 - 7 * 3 + 21, x + 280, iy + 22 + k * 10 - 7 * 3 + 21, color=main("data"), sw=1.2)
    s.text(x + 252, iy + 112, "更多训练 token", size=12.5, color=MUTED)
    # 面板 2 图标：示范 + 奖励回路
    x = x0 + W + gap
    s.rect(x + 40, iy + 30, 110, 60, fill=WHITE, stroke=main("q"), rx=6)
    s.text(x + 95, iy + 50, "问：……", size=12.5, anchor="middle")
    s.text(x + 95, iy + 72, "答：示范", size=12.5, anchor="middle")
    s.text(x + 95, iy + 112, "SFT 示范数据", size=12.5, color=MUTED)
    s.box(x + 200, iy + 20, 100, 30, "模型作答", key="q", size=12.5, weight="normal")
    s.box(x + 200, iy + 72, 100, 30, "奖励 / 偏好", key="attn", size=12.5, weight="normal")
    s.arrow([(x + 300, iy + 35), (x + 326, iy + 61), (x + 300, iy + 87)], color=main("attn"), sw=1.5, curve=True)
    s.arrow([(x + 200, iy + 87), (x + 174, iy + 61), (x + 200, iy + 35)], color=main("attn"), sw=1.5, curve=True)
    s.text(x + 250, iy + 124, "RL：试—评—改", size=12.5, color=MUTED)
    # 面板 3 图标：深度 vs 宽度
    x = x0 + 2 * (W + gap)
    s.text(x + 85, iy + 6, "加深：一条路径多步", size=12.5, weight="bold")
    for k in range(4):
        yy = iy + 22 + k * 24
        s.rect(x + 50, yy, 70, 18, fill=light("v"), stroke=main("v"), rx=4)
        s.text(x + 85, yy + 9, ["推导", "检查", "修正", "结论"][k], size=12)
        if k < 3:
            s.varrow(x + 85, yy + 18, yy + 24, color=main("v"), sw=1.2, head=0.6)
    s.arrow([(x + 122, iy + 79), (x + 146, iy + 55), (x + 122, iy + 31)], color=main("loss"), sw=1.3, curve=True, head=0.8)
    s.text(x + 248, iy + 6, "加宽：多条候选再筛选", size=12.5, weight="bold")
    for k in range(4):
        xx = x + 196 + k * 28
        s.rect(xx, iy + 22, 18, 50, fill=light("v"), stroke=main("v"), rx=4)
        s.text(xx + 9, iy + 86, "✓" if k in (1, 3) else "✗", size=13, color=main("v") if k in (1, 3) else main("loss"),
               weight="bold")
    s.box(x + 196, iy + 98, 102, 24, "验证器 / 投票", key="attn", size=12, weight="normal")
    # 曲线
    xlabels = ["预训练计算量（对数）", "后训练计算量（对数）", "每题推理计算量（对数）"]
    for i, key in enumerate(["data", "q", "v"]):
        x = x0 + i * (W + gap)
        _curve(s, x + 70, y0 + 300, W - 110, 120, xlabels[i], key)
    s.save(OUT / "21_three-scaling-laws.svg")


# ---------------------------------------------------------------------------
# 22 多模态模型
# ---------------------------------------------------------------------------
def fig22():
    s = SVG(1100, 556, "多模态模型的结构", "各模态先编码成向量，再与文字向量拼成同一条序列送入 LLM。")
    rows = [  # key, 名称, 编码器, 连接
        ("k", "图像", "视觉编码器", "切成 patch"),
        ("q", "文字", "分词 + 嵌入", "token"),
        ("ffn", "音频", "音频编码器", "声谱片段"),
        ("pink", "视频", "视频编码器", "帧 + 时间"),
    ]
    ys = [100, 210, 320, 420]
    s.text(105, 28, "输入", size=15, weight="bold")
    s.text(330, 28, "各模态编码", size=15, weight="bold")
    s.text(500, 28, "连接模块", size=15, weight="bold")
    s.text(620, 28, "同一条序列", size=15, weight="bold")
    seq_counts = [4, 6, 3, 3]
    sy = 84
    seq_pos = []
    cell = 18
    yy = sy
    for i, n in enumerate(seq_counts):
        seq_pos.append((yy, yy + n * (cell + 3)))
        yy += n * (cell + 3) + 26
    # 让各行 y 与序列段中心对齐
    ys = [(a + b) / 2 - 1.5 for a, b in seq_pos]
    for i, (key, name, enc, conn) in enumerate(rows):
        y = ys[i]
        dim = i >= 2
        op = 0.55 if dim else None
        # 输入示意
        x = 40
        s.raw(f'<g opacity="{0.5 if dim else 1}">')
        if name == "图像":
            s.rect(x, y - 38, 130, 76, fill=WHITE, stroke=main(key), sw=1.4, rx=6)
            s.line(x + 12, y + 28, x + 122, y + 28, color=BORDER, sw=1)
            s.line(x + 12, y + 28, x + 12, y - 30, color=BORDER, sw=1)
            p1 = [(x + 14 + t * 106, y + 26 - 52 * (1 - math.exp(-4 * t))) for t in [k / 20 for k in range(21)]]
            p2 = [(x + 14 + t * 106, y + 22 - 40 * t ** 1.6) for t in [k / 20 for k in range(21)]]
            s.polyline(p1, stroke=main("q"), sw=2)
            s.polyline(p2, stroke=main("k"), sw=2)
            s.text(x + 65, y + 50, "实验曲线图", size=12.5, color=MUTED)
        elif name == "文字":
            s.rect(x, y - 26, 130, 52, fill=WHITE, stroke=main(key), sw=1.4, rx=6)
            s.text(x + 65, y - 8, "比较两条曲线", size=13)
            s.text(x + 65, y + 12, "的变化", size=13)
        elif name == "音频":
            pts = [(x + 10 + k * 2.2, y - 18 * math.sin(k * 0.55) * math.exp(-((k - 25) / 16) ** 2)) for k in range(51)]
            s.rect(x, y - 26, 130, 52, fill=WHITE, stroke=main(key), sw=1.4, rx=6)
            s.polyline(pts, stroke=main(key), sw=1.6)
        else:
            s.rect(x, y - 26, 130, 52, fill=WHITE, stroke=main(key), sw=1.4, rx=6)
            for k in range(4):
                s.rect(x + 10 + k * 29, y - 16, 24, 32, fill=light(key), stroke=main(key), sw=1, rx=2)
        s.pill(x + 65, y - (52 if name == "图像" else 40), name, key=key, size=12.5, h=22, weight="bold")
        # 编码器
        s.harrow(176, 262, y, color=main(key), sw=1.6)
        s.text(219, y - 12, conn, size=12, color=MUTED)
        s.box(266, y - 22, 128, 44, enc, key=key, size=13.5)
        s.harrow(398, 452, y, color=main(key), sw=1.6)
        s.box(456, y - 18, 88, 36, "投影" if name != "文字" else "（直接使用）",
              key=key if name != "文字" else "gray", size=13 if name != "文字" else 12, weight="normal",
              fill=WHITE)
        a, b = seq_pos[i]
        s.arrow([(548, y), (596, y)], color=main(key), sw=1.6)
        s.raw("</g>")
        for k in range(seq_counts[i]):
            s.rect(602, a + k * (cell + 3), 34, cell, fill=main(key), rx=3, opacity=0.35 if dim else 0.9)
    s.text(560, 534, "本例只用到图像 + 文字；音频、视频按同样方式接入（浅色）。", size=12.5, color=MUTED)
    # 序列外框
    s.rect(594, sy - 10, 50, seq_pos[-1][1] - sy + 20, fill="none", stroke=INK, sw=1.2, rx=6, dash="4 3")
    # LLM
    lx, ly, lw, lh = 690, 150, 180, 250
    s.arrow([(648, ly + lh / 2), (lx - 4, ly + lh / 2)], color=INK, sw=2.2)
    s.rect(lx, ly, lw, lh, fill=light("attn"), stroke=main("attn"), sw=1.6, rx=12)
    for k in range(5):
        s.rect(lx + 20, ly + 50 + k * 34, lw - 40, 24, fill=WHITE, stroke=main("attn"), sw=1, rx=4)
        s.text(lx + lw / 2, ly + 62 + k * 34, "Transformer Block", size=12, color=MUTED)
    s.text(lx + lw / 2, ly + 26, "LLM 主干", size=16, weight="bold")
    s.text(lx + lw / 2, ly + lh + 20, "注意力在所有向量之间", size=12.5, color=MUTED)
    s.text(lx + lw / 2, ly + lh + 38, "建立联系，不分模态", size=12.5, color=MUTED)
    # 输出
    ox = 912
    s.arrow([(lx + lw + 4, ly + lh / 2), (ox - 4, ly + lh / 2)], color=INK, sw=2.2)
    s.rect(ox, ly + 60, 168, 130, fill=WHITE, stroke=main("q"), sw=1.4, rx=10)
    s.text(ox + 84, ly + 82, "文字回答", size=14, weight="bold", color=main("q"))
    for i, ln in enumerate(["橙色曲线先快速上升，", "随后趋于平稳；", "蓝色曲线起步较慢，", "后期加速上升。"]):
        s.text(ox + 14, ly + 108 + i * 20, ln, size=12.5, anchor="start")
    s.save(OUT / "22_multimodal-model-architecture.svg")


# ---------------------------------------------------------------------------
# 23 Mixture of Experts
# ---------------------------------------------------------------------------
def fig23():
    p = [0.50, 0.08, 0.27, 0.15]
    assert abs(sum(p) - 1) < 1e-9
    top = sorted(range(4), key=lambda i: -p[i])[:2]
    assert top == [0, 2]
    g = [p[0] / (p[0] + p[2]), p[2] / (p[0] + p[2])]
    assert [round(v, 2) for v in g] == [0.65, 0.35], g
    s = SVG(1100, 534, "Mixture of Experts 层", "路由器为每个 token 选 2 个专家，按归一化权重汇总输出。")
    s.text(500, 30, "一个 token 经过 MoE 层（FFN 换成 4 个专家，选其中 2 个）", size=16, weight="bold")
    # token
    hy = 250
    s.box(30, hy - 28, 92, 56, "token 表示", key="k", sub="$h$", size=13.5, subsize=15)
    # router
    s.harrow(124, 162, hy, color=INK)
    s.box(166, hy - 32, 98, 64, "路由器", key="attn", sub="打分 + softmax", size=14.5, subsize=12)
    # 打分条
    ey = [100, 200, 300, 400]
    bx = 320
    s.text(bx + 60, 66, "路由概率", size=13.5, weight="bold")
    for i in range(4):
        sel = i in top
        s.arrow([(266, hy), (bx - 8, ey[i])], color=main("attn") if sel else BORDER, sw=1.4, head=0.8)
        s.rect(bx, ey[i] - 12, 120, 24, fill=PANEL, stroke=BORDER, rx=4)
        s.rect(bx, ey[i] - 12, 120 * p[i] / 0.5, 24, fill=main("attn") if sel else "#C5CAD3", rx=4)
        s.text(bx + 128, ey[i], f"{p[i]:.2f}", size=14, anchor="start", weight="bold" if sel else "normal",
               color=INK if sel else MUTED)
    s.text(bx + 60, 438, "取最大的 2 个（top-2）", size=13, color=main("attn"))
    # experts
    exx = 530
    for i in range(4):
        sel = i in top
        if sel:
            s.box(exx, ey[i] - 26, 140, 52, f"专家 $E$_{{{i + 1}}}", key="ffn", sub="一个 FFN", size=14.5, subsize=12)
        else:
            s.box(exx, ey[i] - 26, 140, 52, f"专家 $E$_{{{i + 1}}}", key="gray", sub="本 token 不计算", size=14.5,
                  subsize=12, dash="5 4", color=MUTED, fill=WHITE, stroke=BORDER)
        s.arrow([(bx + 172, ey[i]), (exx - 4, ey[i])], color=main("ffn") if sel else BORDER, sw=1.6 if sel else 1.1,
                dash=None if sel else "4 4", head=0.8)
    # 合并
    cx, cy = 790, hy
    s.circle(cx, cy, 24, fill=WHITE, stroke=INK, sw=1.6)
    s.text(cx, cy + 1, "+", size=24)
    gi = {0: g[0], 2: g[1]}
    for i in top:
        s.arrow([(exx + 142, ey[i]), (cx - 18, cy - 14 if i == 0 else cy + 14)], color=main("ffn"), sw=1.8)
        mx, my = (exx + 142 + cx) / 2, (ey[i] + cy) / 2
        s.rect(mx - 36, my - 14 - (6 if i == 0 else -6), 72, 26, fill=WHITE, stroke=main("ffn"), rx=13)
        s.text(mx, my - 1 - (6 if i == 0 else -6), f"× {gi[i]:.2f}", size=14, color=main("ffn"), weight="bold")
    s.harrow(cx + 26, 860, cy, color=INK)
    s.box(864, cy - 26, 96, 52, "输出 $y$", key="k", size=15)
    # 公式
    s.rect(300, 462, 540, 56, fill=PANEL, stroke=BORDER, rx=10)
    s.text(570, 478, "被选中的权重重新归一化：0.50 / (0.50+0.27) ≈ 0.65，0.27 / (0.50+0.27) ≈ 0.35", size=12.5, color=MUTED)
    s.text(570, 502, "$y$ = 0.65 · $E$_{1}($h$) + 0.35 · $E$_{3}($h$)", size=15, weight="bold")
    # 右侧：不同 token 选不同专家
    rx0, ry0 = 880, 60
    s.text(rx0 + 100, ry0, "不同 token 选不同专家", size=13.5, weight="bold")
    toks = [("温度", (0, 2)), ("def", (1, 3)), ("梯度", (0, 3))]
    for j, (tk, sel) in enumerate(toks):
        yy = ry0 + 30 + j * 34
        s.pill(rx0 + 32, yy, tk, key="k", size=12.5, h=24)
        for i in range(4):
            on = i in sel
            s.rect(rx0 + 74 + i * 30, yy - 11, 24, 22, fill=main("ffn") if on else WHITE,
                   stroke=main("ffn") if on else BORDER, rx=4)
            s.text(rx0 + 86 + i * 30, yy, f"{i + 1}", size=12, color=WHITE if on else MUTED)
    s.text(rx0 + 100, ry0 + 132, "分工由训练形成，不是人为指定", size=12, color=MUTED)
    # 参数量对比
    py = 380
    s.text(rx0 + 100, py - 4, "参数量：存得多，算得少", size=13.5, weight="bold")
    s.text(rx0 + 100, py + 16, "例：DeepSeek-V4-Pro", size=12, color=MUTED)
    s.rect(rx0 + 4, py + 30, 200, 18, fill="#C5CAD3", rx=3)
    s.text(rx0 + 4, py + 62, "总参数 ≈ 1.6T", size=12.5, anchor="start")
    s.rect(rx0 + 4, py + 76, 200 * 49 / 1600, 18, fill=main("ffn"), rx=2)
    s.text(rx0 + 16, py + 85, "每个 token 激活 ≈ 49B（约 3%）", size=12.5, anchor="start")
    s.save(OUT / "23_mixture-of-experts-layer.svg")


# ---------------------------------------------------------------------------
# 29 RAG
# ---------------------------------------------------------------------------
def _doc(s, x, y, w=46, h=58, key="data"):
    s.path(f"M{x},{y} L{x + w - 12},{y} L{x + w},{y + 12} L{x + w},{y + h} L{x},{y + h} Z",
           stroke=main(key), sw=1.3, fill=WHITE)
    for k in range(4):
        s.line(x + 8, y + 18 + k * 9, x + w - 8, y + 18 + k * 9, color=light(key) if False else mix(main(key), WHITE, 0.55), sw=1.4)


def fig29():
    s = SVG(1100, 520, "检索增强生成 RAG", "离线把资料切片建索引；在线检索相关片段，与问题一起交给 LLM。")
    # ---- 离线 ----
    s.panel(20, 16, 1060, 170, "离线：建索引（资料更新时重做）", key="data", size=15)
    y = 108
    for k in range(3):
        _doc(s, 60 + k * 10, y - 40 + k * 6)
    s.text(95, y + 50, "规范、报告、手册", size=12.5, color=MUTED)
    s.harrow(150, 210, y, color=main("data"), sw=1.6)
    s.text(180, y - 12, "切片", size=12.5, color=MUTED)
    chunks = ["规范 v3 · §4.2", "规范 v3 · §4.3", "附录 B · 表 2"]
    for k, c in enumerate(chunks):
        cy = y - 46 + k * 36
        s.rect(216, cy - 13, 170, 28, fill=WHITE, stroke=main("data"), rx=5)
        s.rect(216, cy - 13, 8, 28, fill=main("data"), rx=2)
        s.text(234, cy + 1, f"片段{k + 1}", size=12.5, anchor="start")
        s.text(380, cy + 1, c, size=12, anchor="end", color=main("data"))
    s.text(301, y + 64, "每段保留出处", size=12.5, color=main("data"), weight="bold")
    s.harrow(394, 470, y, color=main("k"), sw=1.6)
    s.box(474, y - 26, 130, 52, "向量化", key="k", sub="嵌入模型", size=14, subsize=12)
    s.harrow(608, 690, y, color=main("k"), sw=1.6)
    # 向量索引
    ix, iy = 694, y - 48
    s.rect(ix, iy, 170, 96, fill=WHITE, stroke=main("k"), sw=1.3, rx=8)
    rng = RNG(7)
    for k in range(26):
        px, py = ix + 14 + rng.u() * 142, iy + 12 + rng.u() * 72
        s.circle(px, py, 3.2, fill=mix(main("k"), WHITE, 0.35))
    hot = [(ix + 120, iy + 32), (ix + 134, iy + 46)]
    for px, py in hot:
        s.circle(px, py, 4.2, fill=main("data"))
    s.text(ix + 85, iy + 112, "向量索引（片段 → 向量）", size=12.5, color=MUTED)
    s.text(970, y - 10, "相近的含义", size=12.5, color=MUTED)
    s.text(970, y + 10, "→ 相近的向量", size=12.5, color=MUTED)

    # ---- 在线 ----
    s.panel(20, 206, 1060, 300, "在线：每次提问", key="q", size=15)
    y2 = 300
    s.rect(40, y2 - 32, 196, 64, fill=light("q"), stroke=main("q"), rx=10)
    s.text(138, y2 - 10, "问题：这份规范对", size=13)
    s.text(138, y2 + 12, "某项指标的要求是什么？", size=13)
    s.harrow(240, 470, y2, color=main("k"), sw=1.6)
    s.text(355, y2 - 12, "用同一个嵌入模型", size=12.5, color=MUTED)
    s.box(474, y2 - 26, 130, 52, "向量化", key="k", sub="问题 → 向量", size=14, subsize=12)
    s.harrow(608, 690, y2, color=main("k"), sw=1.6)
    s.box(694, y2 - 26, 170, 52, "检索 top-k", key="k", sub="找最相近的片段", size=14, subsize=12)
    s.arrow([(779, y2 - 28), (779, iy + 100)], color=main("k"), sw=1.4, dash="5 4", both=True)
    s.text(790, 214 + 30, "查索引", size=12.5, color=main("k"), anchor="start")
    # 上下文拼装
    s.arrow([(866, y2), (960, y2), (960, 364)], color=main("data"), sw=1.6)
    s.text(970, y2 + 34, "返回片段 1、2", size=12.5, color=main("data"), anchor="start")
    cxx, cyy, cw = 690, 368, 370
    s.rect(cxx, cyy, cw, 120, fill=WHITE, stroke=INK, sw=1.2, rx=8, dash="5 3")
    s.text(cxx + 12, cyy + 16, "拼成上下文", size=12.5, anchor="start", weight="bold")
    s.rect(cxx + 12, cyy + 30, cw - 24, 24, fill=light("q"), stroke=main("q"), rx=4)
    s.text(cxx + 22, cyy + 42, "问题：这份规范对某项指标的要求是什么？", size=12.5, anchor="start")
    for k in range(2):
        yy = cyy + 60 + k * 28
        s.rect(cxx + 12, yy, cw - 24, 24, fill=light("data"), stroke=main("data"), rx=4)
        s.text(cxx + 22, yy + 12, f"[{k + 1}] {chunks[k]}：……原文……", size=12.5, anchor="start")
    # LLM 与回答
    s.arrow([(cxx - 4, cyy + 60), (606, cyy + 60)], color=INK, sw=1.8)
    s.box(474, cyy + 30, 130, 60, "LLM", key="attn", sub="依据片段作答", size=16, subsize=12)
    s.arrow([(470, cyy + 60), (408, cyy + 60)], color=INK, sw=1.8)
    s.rect(40, cyy - 4, 364, 128, fill=WHITE, stroke=main("v"), sw=1.4, rx=10)
    s.text(56, cyy + 18, "回答（带出处）", size=13.5, anchor="start", weight="bold", color=main("v"))
    s.text(56, cyy + 46, "该指标应不超过规定上限 [1]；", size=13, anchor="start")
    s.text(56, cyy + 70, "检验方法见第 4.3 节 [2]。", size=13, anchor="start")
    s.text(56, cyy + 100, "→ 可按 [1][2] 回查原文，核对条款与数值", size=12.5, anchor="start", color=MUTED)
    s.save(OUT / "29_rag-retrieval-evidence-generation.svg")


# ---------------------------------------------------------------------------
# 26 Agent 循环
# ---------------------------------------------------------------------------
def fig26():
    s = SVG(1100, 540, "Agent 的迭代循环", "模型选择工具动作，环境执行并返回结果，结果写回上下文，循环直到完成。")
    # ---- 左：循环 ----
    s.text(270, 28, "循环：想 → 做 → 看 → 再想", size=16, weight="bold")
    cx, cy, R = 270, 270, 150
    nodes = [
        (-90, "q", "① 思考与规划", "LLM 读上下文，决定下一步"),
        (0, "attn", "② 调用工具", "读文件 / 运行 Python / 搜索"),
        (90, "k", "③ 环境执行", "真的去读、去算、去查"),
        (180, "v", "④ 观察结果", "输出或报错写回上下文"),
    ]
    pos = []
    for ang, key, t, sub in nodes:
        x = cx + R * math.cos(math.radians(ang))
        y = cy + R * math.sin(math.radians(ang))
        pos.append((x, y))
    # 圆弧箭头（相邻节点之间）
    for i in range(4):
        a0, a1 = nodes[i][0], nodes[(i + 1) % 4][0] + (360 if i == 3 else 0)
        off0 = 42 if i % 2 == 0 else 16   # 上/下节点是宽框，需要更大的角度避让
        off1 = 16 if i % 2 == 0 else 42
        pts = arc_pts(cx, cy, R, R, a0 + off0, a1 - off1, 12)
        s.arrow([pts[0], pts[6], pts[-1]], color="#7C8594", sw=2.2, curve=True)
    for (x, y), (ang, key, t, sub) in zip(pos, nodes):
        s.box(x - 92, y - 30, 184, 60, t, key=key, sub=sub, size=14.5, subsize=12)
    # 中心：目标
    s.circle(cx, cy, 54, fill=PANEL, stroke=BORDER, sw=1.2)
    s.text(cx, cy - 18, "目标", size=14, weight="bold")
    s.text(cx, cy + 4, "分析 data.csv", size=12.5)
    s.text(cx, cy + 24, "并写报告", size=12.5)
    # 退出
    x1, y1 = pos[0]
    s.arrow([(x1 + 92, y1), (470, y1)], color=main("v"), sw=1.8)
    s.text(476, y1 - 16, "满足完成条件？是", size=12.5, color=main("v"), anchor="start")
    s.box(476, y1 - 2, 80, 32, "输出报告", key="v", size=13)
    s.text(270, 500, "每转一圈，上下文就多一轮“动作 + 结果”", size=13, color=MUTED)

    # ---- 右：上下文逐轮增长 ----
    px = 600
    s.panel(px, 16, 480, 510, "上下文逐轮变长（分析 data.csv 的一次运行）", size=14.5)
    seg = {"goal": ("gray", "目标"), "act": ("q", "动作"), "ok": ("v", "结果"), "err": ("loss", "报错")}
    rounds = [
        ("第 1 轮", [("goal", 40), ("act", 38), ("ok", 44)], "读文件 → 1000 行、5 列"),
        ("第 2 轮", [("act", 38), ("err", 44)], "运行分析 → 报错：没有 temp 列"),
        ("第 3 轮", [("act", 38), ("ok", 44)], "改用列名 temp_C 重跑 → 得到结果"),
        ("第 4 轮", [("act", 38), ("ok", 38)], "写报告 → 检查后结束"),
    ]
    yy = 74
    prev = []
    for name, add, desc in rounds:
        s.text(px + 18, yy + 12, name, size=13, anchor="start", weight="bold")
        x = px + 80
        for kind, w in prev:
            k = seg[kind][0]
            s.rect(x, yy, w, 24, fill=light(k), stroke=mix(main(k), WHITE, 0.4), rx=3)
            x += w + 2
        for kind, w in add:
            k = seg[kind][0]
            s.rect(x, yy, w, 24, fill=main(k), rx=3)
            s.text(x + w / 2, yy + 12, seg[kind][1], size=12, color=WHITE)
            x += w + 2
        s.text(px + 80, yy + 42, desc, size=12.5, anchor="start", color=INK)
        prev = prev + add
        yy += 92
    # 图例
    ly = 450
    lx = px + 20
    for kind in ["goal", "act", "ok", "err"]:
        k, lab = seg[kind]
        s.rect(lx, ly, 14, 14, fill=main(k), rx=2)
        s.text(lx + 20, ly + 7, {"goal": "任务目标", "act": "模型的工具调用", "ok": "执行结果", "err": "错误信息"}[kind],
               size=12.5, anchor="start")
        lx += {"goal": 90, "act": 132, "ok": 98}.get(kind, 0)
    s.text(px + 240, 494, "深色 = 本轮新增；浅色 = 之前各轮留下的内容", size=12.5, color=MUTED)
    s.save(OUT / "26_agent-iterative-cycle.svg")


# ---------------------------------------------------------------------------
# 30 贝尔曼递推
# ---------------------------------------------------------------------------
def fig30():
    gamma = 0.9
    leaves = [  # 所属动作, P, r, V
        (0, 0.6, 2, 5),
        (0, 0.4, -1, 2),
        (1, 1.0, 0, 4),
    ]
    pi = [0.7, 0.3]
    back = [r + gamma * v for _, _, r, v in leaves]
    Q = [sum(P * b for (a, P, _, _), b in zip(leaves, back) if a == ai) for ai in range(2)]
    V = sum(p * q for p, q in zip(pi, Q))
    assert abs(Q[0] - 4.22) < 1e-9 and abs(Q[1] - 3.6) < 1e-9 and abs(V - 4.034) < 1e-9, (Q, V)

    def fmt(x):
        return f"{x:g}".replace("-", "−")

    s = SVG(1060, 560, "贝尔曼递推示例", "从后继状态的价值回推动作价值，再按策略加权得到状态价值。")
    # 层标签
    s.text(30, 80, "状态", size=13.5, color=MUTED, anchor="start", weight="bold")
    s.text(30, 236, "动作", size=13.5, color=MUTED, anchor="start", weight="bold")
    s.text(30, 410, "下一状态", size=13.5, color=MUTED, anchor="start", weight="bold")
    s.text(30, 154, "策略 $π$ 选动作", size=12.5, color=main("q"), anchor="start")
    s.text(30, 322, "环境 $P$ 决定去哪", size=12.5, color=main("k"), anchor="start")

    root = (440, 80)
    acts = [(300, 236), (680, 236)]
    leaf_pos = [(170, 410), (430, 410), (680, 410)]
    # 边
    for (ax, ay), p in zip(acts, pi):
        s.line(root[0], root[1] + 30, ax, ay - 16, color=main("q"), sw=1.8)
        mx, my = (root[0] + ax) / 2, (root[1] + 30 + ay - 16) / 2
        s.pill(mx + (-34 if ax < root[0] else 34), my, f"$π$ = {p}", key="q", size=13, h=24)
    for (a, P, r, v), (lx, ly) in zip(leaves, leaf_pos):
        ax, ay = acts[a]
        s.line(ax, ay + 12, lx, ly - 32, color=main("k"), sw=1.8)
        mx, my = (ax + lx) / 2, (ay + 12 + ly - 32) / 2
        s.pill(mx + (-40 if lx < ax else (40 if lx > ax else 44)), my, f"$P$ = {P}", key="k", size=13, h=24)
    # 叶节点
    for i, ((a, P, r, v), (lx, ly), b) in enumerate(zip(leaves, leaf_pos, back)):
        s.circle(lx, ly, 30, fill=light("k"), stroke=main("k"), sw=1.6)
        s.text(lx, ly - 7, f"$s$'_{{{i + 1}}}", size=14.5)
        s.text(lx, ly + 11, f"$V$ = {v}", size=12.5)
        s.pill(lx, ly + 50, f"奖励 $r$ = {fmt(r)}", key="v", size=12.5, h=24)
        s.rect(lx - 98, ly + 72, 196, 50, fill=PANEL, stroke=BORDER, rx=8)
        s.text(lx, ly + 87, "$r$ + $γV$", size=12.5, color=MUTED)
        s.text(lx, ly + 108, f"= {fmt(r)} + 0.9×{v} = {fmt(round(b, 3))}", size=13.5, weight="bold")
    # 动作节点
    qtxt = ["= 0.6×6.5 + 0.4×0.8 = 4.22", "= 1.0×3.6 = 3.6"]
    for i, (ax, ay) in enumerate(acts):
        s.circle(ax, ay, 13, fill=main("q"))
        s.text(ax + 22, ay, f"$a$_{{{i + 1}}}", size=15, anchor="start", weight="bold")
        bx = ax + 50 if i == 0 else ax + 46
        s.rect(bx, ay - 26, 226 if i == 0 else 150, 52, fill=light("q"), stroke=main("q"), rx=8)
        s.text(bx + 10, ay - 11, f"$Q$($s$, $a$_{{{i + 1}}}) = Σ $P$·($r$ + $γV$)", size=12.5, anchor="start",
               color=MUTED) if i == 0 else s.text(bx + 10, ay - 11, f"$Q$($s$, $a$_{{{i + 1}}})", size=12.5,
                                                  anchor="start", color=MUTED)
        s.text(bx + 10, ay + 11, qtxt[i], size=13.5, anchor="start", weight="bold")
    # 根节点
    s.circle(root[0], root[1], 30, fill=light("attn"), stroke=main("attn"), sw=1.8)
    s.text(root[0], root[1] + 1, "$s$", size=17)
    s.rect(root[0] + 50, root[1] - 26, 330, 52, fill=light("attn"), stroke=main("attn"), rx=8)
    s.text(root[0] + 62, root[1] - 11, "$V$($s$) = Σ $π$($a$|$s$)·$Q$($s$, $a$)", size=12.5, anchor="start", color=MUTED)
    s.text(root[0] + 62, root[1] + 11, "= 0.7×4.22 + 0.3×3.6 = 4.034", size=14, anchor="start", weight="bold")
    # 回传箭头
    s.arrow([(1000, 470), (1000, 90)], color=main("attn"), sw=2.2, dash="7 5")
    s.raw('<g transform="rotate(-90 1022 280)">')
    s.text(1022, 280, "从下往上回传（backup），$γ$ = 0.9", size=13, color=main("attn"))
    s.raw("</g>")
    s.save(OUT / "30_bellman-backup-example.svg")


if __name__ == "__main__":
    fig27()
    fig20()
    fig21()
    fig22()
    fig23()
    fig29()
    fig26()
    fig30()
