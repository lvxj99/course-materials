"""第 7.5 节与第 9.1–9.2 节：自回归生成、KV cache、合批、BPE、分词与嵌入、温度与截断采样。"""
from collections import Counter

from svgkit import *


# ---------------------------------------------------------------------------
# 08 自回归生成：每步预测一个 token，再接回上下文
# ---------------------------------------------------------------------------
def fig08():
    steps = [
        ("我", [("我", 0.62), ("你", 0.20), ("今天", 0.10)]),
        ("喜欢", [("喜欢", 0.55), ("爱", 0.25), ("是", 0.10)]),
        ("机器", [("机器", 0.48), ("学习", 0.30), ("你", 0.08)]),
        ("学习", [("学习", 0.81), ("人", 0.12), ("翻译", 0.03)]),
        ("<eos>", [("<eos>", 0.70), ("。", 0.20), ("和", 0.05)]),
    ]
    W, row_h, y_first = 1020, 82, 112
    s = SVG(W, y_first + row_h * len(steps) + 10, "自回归生成",
            "每一步根据已有上下文预测下一个 token 的分布，选出一个后接回上下文，直到 <eos>。")
    s.text(W / 2, 28, "自回归生成：每次只多写一个 token，写完就接回上下文", size=17, weight="bold")
    # 列标题
    s.text(250, 70, "当前上下文（每步变长一格）", size=14, weight="bold", color=main("k"))
    s.text(560, 70, "模型", size=14, weight="bold")
    s.text(718, 70, "下一个 token 的概率（示例）", size=14, weight="bold", color=main("attn"))
    s.text(920, 70, "选出", size=14, weight="bold", color=main("q"))

    ctx = ["<bos>"]
    right = 470  # 上下文右对齐
    pw = {"<bos>": 58, "我": 40, "喜欢": 52, "机器": 52, "学习": 52}
    gap = 8
    for r, (pick, cands) in enumerate(steps):
        y = y_first + r * row_h
        s.text(26, y, f"第 {r + 1} 步", size=13, color=MUTED, anchor="start")
        # 上下文右对齐排开
        x = right
        boxes = []
        for i, tok in enumerate(reversed(ctx)):
            w = pw[tok]
            x0 = x - w
            new = (i == 0 and r > 0)
            key = "q" if new else ("gray" if tok == "<bos>" else "k")
            s.rect(x0, y - 15, w, 30, fill=light(key), stroke=main(key), sw=1.6 if new else 1.1, rx=8)
            s.text(x0 + w / 2, y, tok, size=14, weight="bold" if new else "normal")
            boxes.append((x0, w))
            x = x0 - gap
        # 模型
        s.harrow(right + 8, 522, y, color=LINE)
        s.box(526, y - 20, 68, 40, "LLM", key="gray", size=14)
        s.harrow(598, 628, y, color=LINE)
        # 概率条
        bx, bmax = 636, 150
        for j, (tok, p) in enumerate(cands):
            yy = y - 21 + j * 14.5
            s.text(bx + 34, yy + 5, tok, size=11.5 if len(tok) > 2 else 12.5, anchor="end",
                   color=INK if j == 0 else MUTED)
            s.rect(bx + 40, yy, bmax * p, 11, fill=main("attn") if j == 0 else light("attn"),
                   stroke="none", rx=2.5)
            s.text(bx + 46 + bmax * p, yy + 5.5, f"{p:.2f}", size=11.5, anchor="start",
                   color=INK if j == 0 else MUTED)
        s.harrow(848, 880, y, color=LINE)
        # 选出的 token
        is_end = pick == "<eos>"
        key = "loss" if is_end else "q"
        s.rect(888, y - 16, 64, 32, fill=light(key), stroke=main(key), sw=1.6, rx=8)
        s.text(920, y, pick, size=14, weight="bold")
        if is_end:
            s.text(992, y, "停止", size=14, weight="bold", color=main("loss"))
        else:
            # 回送路径：从选出的 token 下方，沿两行之间的空隙折回到下一行上下文的最右格
            yr = y + row_h / 2
            nx = right - pw[pick] / 2
            s.arrow([(920, y + 17), (920, yr), (nx, yr), (nx, y + row_h - 17)], color=main("q"), sw=1.5,
                    dash="5 4", opacity=0.85)
            if r == 0:
                s.text(800, yr - 10, "接回上下文末尾", size=12.5, color=main("q"))
        ctx.append(pick)
    yb = y_first + row_h * len(steps) - 18
    s.text(W / 2, yb + 14, "这里每步取概率最高的候选（贪心解码）；也可以按概率采样，见 9.2 节。生成在遇到 <eos> 或达到长度上限时停止。",
           size=12.5, color=MUTED)
    s.save(OUT / "08_autoregressive-generation.svg")


# ---------------------------------------------------------------------------
# 09 Prefill 与 Decode：KV cache
# ---------------------------------------------------------------------------
def fig09():
    W, H = 1060, 560
    s = SVG(W, H, "Prefill、Decode 与 KV cache",
            "Prefill 并行处理整段提示并写入 K/V 缓存；Decode 每步只为新 token 计算 q/k/v，新 q 读取全部缓存。")

    def kv_cache(x, y, n, new_idx=None, faded=False):
        """画 KV cache：上排 K（蓝）下排 V（绿），每列一个位置。"""
        cw, ch = 46, 26
        for i in range(n):
            isnew = (new_idx is not None and i == new_idx)
            for row, key, lab in ((0, "k", "k"), (1, "v", "v")):
                fill = main(key) if isnew else light(key)
                s.rect(x + i * (cw + 6), y + row * (ch + 4), cw, ch, fill=fill, stroke=main(key), sw=1.1, rx=4)
                s.text(x + i * (cw + 6) + cw / 2, y + row * (ch + 4) + ch / 2, f"${lab}$_{{{i + 1}}}",
                       size=13.5, color=WHITE if isnew else INK)
        return cw, ch

    toks = ["我", "喜欢", "机器"]
    # ---------------- 左：Prefill ----------------
    s.panel(20, 20, 500, 380, "① Prefill：整段提示一次并行算完", key="k", tag="1" if False else None)
    xs = [110, 210, 310]
    yt = 338
    for i, (x, t) in enumerate(zip(xs, toks)):
        s.pill(x, yt, t, key="k", size=14, pad=12)
        s.varrow(x, yt - 17, 292, color=LINE)
    s.box(70, 222, 290, 66, "Transformer 各层", key="gray", size=14.5,
          sub="三个位置同时计算（因果掩码）", subsize=12.5)
    # 写入 cache
    cx0, cy0 = 76, 118
    cw, ch = kv_cache(cx0, cy0, 3)
    s.text(cx0 - 8, cy0 + ch / 2, "K", size=13, color=main("k"), anchor="end", weight="bold")
    s.text(cx0 - 8, cy0 + ch * 1.5 + 4, "V", size=13, color=main("v"), anchor="end", weight="bold")
    s.rect(cx0 - 26, cy0 - 30, 3 * (cw + 6) + 42, 2 * ch + 46, fill="none", stroke=main("ffn"), sw=1.4, dash="5 4", rx=8)
    s.text(cx0 - 14, cy0 - 16, "KV cache（写入）", size=13, color=main("ffn"), anchor="start", weight="bold")
    for i in range(3):
        x = cx0 + i * (cw + 6) + cw / 2
        s.varrow(x, 220, cy0 + 2 * ch + 8, color=main("ffn"), sw=1.4)
    # 输出第一个 token
    s.arrow([(360, 255), (404, 255)], color=main("q"), sw=1.6)
    s.pill(450, 255, "学习", key="q", size=14, pad=12, weight="bold")
    s.text(450, 222, "第一个输出", size=12.5, color=main("q"))
    s.text(270, 378, "计算量大，但能充分并行 → 决定首 token 延迟（TTFT）", size=12.5, color=MUTED)

    # ---------------- 右：Decode ----------------
    s.panel(540, 20, 500, 380, "② Decode 一步：只算新来的 token", key="q")
    dx0, dy0 = 600, 118
    cw, ch = kv_cache(dx0, dy0, 4, new_idx=3)
    s.text(dx0 - 8, dy0 + ch / 2, "K", size=13, color=main("k"), anchor="end", weight="bold")
    s.text(dx0 - 8, dy0 + ch * 1.5 + 4, "V", size=13, color=main("v"), anchor="end", weight="bold")
    s.rect(dx0 - 26, dy0 - 30, 4 * (cw + 6) + 42, 2 * ch + 46, fill="none", stroke=main("ffn"), sw=1.4, dash="5 4", rx=8)
    s.text(dx0 - 14, dy0 - 16, "KV cache", size=13, color=main("ffn"), anchor="start", weight="bold")
    s.text(790, 66, "前三列在之前的步骤已算好，直接复用；只有第 4 列是新算的", size=12.5, color=MUTED)
    nx = dx0 + 3 * (cw + 6) + cw / 2
    s.text(nx, dy0 - 16, "新追加", size=12.5, color=main("q"), weight="bold")
    # 新 token
    s.pill(nx, 338, "学习", key="q", size=14, pad=12, weight="bold")
    s.text(nx, 366, "上一步的输出，成为新输入", size=12.5, color=main("q"))
    s.box(nx - 52, 236, 104, 52, "只算 $q$_{4}, $k$_{4}, $v$_{4}", key="q", size=13.5, weight="normal")
    s.varrow(nx, 320, 290, color=LINE)
    s.varrow(nx, 234, dy0 + 2 * ch + 8, color=main("q"), sw=1.6)
    s.text(nx + 8, 212, "写入", size=12.5, color=main("q"), anchor="start")
    # q4 读取全部 K/V（第 4 列就是它自己刚写入的）
    for i in range(3):
        tx = dx0 + i * (cw + 6) + cw / 2
        s.arrow([(nx - 52, 262), (tx, 262), (tx, dy0 + 2 * ch + 8)], color=main("attn"), sw=1.4, opacity=0.8, curve=True)
    s.text(565, 312, "$q$_{4} 读取全部 4 列 K/V", size=13, color=main("attn"), weight="bold", anchor="start")
    s.text(565, 332, "（含刚写入的 $k$_{4}, $v$_{4}）", size=12.5, color=main("attn"), anchor="start")
    s.arrow([(nx + 52, 262), (968, 262)], color=main("q"), sw=1.6)
    s.pill(995, 262, "。", key="q", size=14, pad=12, weight="bold")
    s.text(995, 232, "下一个", size=12.5, color=main("q"))
    s.text(790, 390, "每步计算很少，但要读全部权重和缓存 → 决定 TPOT", size=12.5, color=MUTED, anchor="middle")

    # ---------------- 底部：时间线 ----------------
    ty = 470
    s.text(30, 428, "一次请求的时间线", size=14, weight="bold", anchor="start")
    segs = [("排队", 70, "gray"), ("prefill", 190, "k"), ("decode", 95, "q"), ("decode", 95, "q")]
    x = 110
    s.text(100, ty, "到达", size=12.5, color=MUTED, anchor="end")
    marks = []
    for lab, w, key in segs:
        s.rect(x, ty - 15, w - 4, 30, fill=light(key), stroke=main(key), sw=1.1, rx=6)
        s.text(x + (w - 4) / 2, ty, lab, size=13)
        marks.append(x + w - 4)
        x += w
    out_toks = ["学习", "。", "<eos>"]
    for i, t in enumerate(out_toks):
        mx = marks[1 + i]
        s.line(mx + 2, ty - 24, mx + 2, ty + 18, color=main("q"), sw=1.6)
        s.text(mx + 2, ty - 34, t, size=12.5, color=main("q"), weight="bold")
    # TTFT
    s.brace(110, ty + 22, marks[1] + 2, ty + 22, "TTFT：等到第一个 token", color=main("k"), size=13, depth=10)
    s.brace(marks[2] + 2, ty + 22, marks[3] + 2, ty + 22, "TPOT：后续每个 token", color=main("q"), size=13, depth=10)
    s.text(x + 30, ty - 10, "生成到 <eos> 结束。", size=12.5, color=MUTED, anchor="start")
    s.text(x + 30, ty + 12, "注：每层各有一份 KV cache，图中只画一层。", size=12.5, color=MUTED, anchor="start")
    s.save(OUT / "09_parallel-processing-and-kv-cache.svg")


# ---------------------------------------------------------------------------
# 25 合批：吞吐与延迟
# ---------------------------------------------------------------------------
def fig25():
    t_w, c = 20.0, 1.0  # ms：读一遍权重的时间；每条请求的额外计算时间
    Bs = [2 ** k for k in range(0, 8)]  # 1..128

    def step(B):
        return t_w + B * c

    def thr(B):
        return B / step(B) * 1000.0  # tokens/s

    assert abs(thr(1) - 1000 / 21) < 1e-9 and thr(128) < 1000
    W, H = 1060, 470
    s = SVG(W, H, "合批提升吞吐，但会拉长每一步",
            "同一次权重读取服务更多请求，吞吐上升并趋于饱和；每一步的耗时随批次变大。")

    # ---------------- 左：直觉 ----------------
    s.panel(20, 20, 400, 430, "直觉：读一次权重，服务几个请求？")

    def scene(y0, n, title):
        s.text(40, y0, title, size=14, weight="bold", anchor="start")
        # 权重（书本）
        bx, by = 52, y0 + 22
        for k in range(3):
            s.rect(bx + k * 4, by + k * 4, 86, 108, fill=light("gray"), stroke=main("gray"), sw=1.1, rx=4)
        s.text(bx + 51, by + 54, "模型权重", size=13.5, weight="bold")
        s.text(bx + 51, by + 76, "（从显存读出）", size=12, color=MUTED)
        s.text(bx + 51, by + 128, "读 1 次", size=12.5, color=main("gray"), weight="bold")
        # 请求
        ys = [by + 58] if n == 1 else [by + 10 + i * 30 for i in range(n)]
        for i, yy in enumerate(ys):
            s.arrow([(bx + 96, by + 58), (262, yy)], color=main("k"), sw=1.5)
            s.pill(318, yy, f"请求 {i + 1} 的新 token", key="k", size=12.5, pad=8)
        return by

    scene(64, 1, "batch = 1")
    s.text(166, 190, "大部分时间花在搬运权重上", size=12.5, color=MUTED, anchor="start")
    scene(250, 4, "batch = 4")
    s.text(220, 424, "同一份权重被 4 个请求共享", size=12.5, color=main("v"), weight="bold")

    # ---------------- 右：两条曲线 ----------------
    s.panel(440, 20, 600, 430, "一个简化成本模型")
    s.text(740, 60, "每步耗时 = 读权重 $t$_{w} + 批次 $B$ × 每条计算 $c$", size=13.5)
    s.text(740, 82, f"（取 $t$_{{w}} = {t_w:.0f} ms，$c$ = {c:.0f} ms；教学用简化模型，不代表真实设备测量）", size=12.5, color=MUTED)

    gx0, gx1 = 530, 1010

    def X(B):
        return gx0 + (math.log2(B) / 7) * (gx1 - gx0)

    def axes(y_top, y_bot, ymax, yticks, ylabel, color):
        s.line(gx0, y_bot, gx1 + 6, y_bot, color=INK, sw=1.1)
        s.line(gx0, y_bot, gx0, y_top - 6, color=INK, sw=1.1)
        for v in yticks:
            yy = y_bot - v / ymax * (y_bot - y_top)
            s.line(gx0 - 4, yy, gx0, yy, color=INK, sw=1)
            s.line(gx0, yy, gx1, yy, color=BORDER, sw=0.8, dash="3 3")
            s.text(gx0 - 8, yy, f"{v:g}", size=12, anchor="end", color=MUTED)
        s.raw(f'<g transform="rotate(-90 {gx0 - 50} {(y_top + y_bot) / 2})">')
        s.text(gx0 - 50, (y_top + y_bot) / 2, ylabel, size=13, color=color, weight="bold")
        s.raw("</g>")

        def Y(v):
            return y_bot - v / ymax * (y_bot - y_top)
        return Y

    # 上图：吞吐
    yt0, yt1 = 124, 248
    Yt = axes(yt0, yt1, 1000, [0, 250, 500, 750, 1000], "吞吐 tok/s", main("v"))
    pts = [(X(2 ** (k / 10)), Yt(thr(2 ** (k / 10)))) for k in range(0, 71)]
    s.line(gx0, Yt(1000), gx1, Yt(1000), color=main("v"), sw=1.2, dash="6 4")
    s.text(gx0 + 14, Yt(1000) - 10, "上限 1/$c$ = 1000 tok/s", size=12.5, color=main("v"), anchor="start")
    s.polyline(pts, stroke=main("v"), sw=2.6)
    for B in (1, 8, 64):
        s.circle(X(B), Yt(thr(B)), 4, fill=main("v"))
        s.text(X(B) + (10 if B < 64 else -8), Yt(thr(B)) + (-12 if B == 1 else 14 if B < 64 else 16), f"{thr(B):.0f}",
               size=12, color=main("v"), anchor="start" if B < 64 else "end", weight="bold")

    # 下图：每步耗时（≈ 每个用户的 TPOT）
    yl0, yl1 = 280, 400
    Yl = axes(yl0, yl1, 150, [0, 50, 100, 150], "每步耗时 ms", main("loss"))
    pts = [(X(2 ** (k / 10)), Yl(step(2 ** (k / 10)))) for k in range(0, 71)]
    s.polyline(pts, stroke=main("loss"), sw=2.6)
    for B in (1, 8, 64):
        s.circle(X(B), Yl(step(B)), 4, fill=main("loss"))
        s.text(X(B) + (-8 if B == 64 else 8), Yl(step(B)) - 12, f"{step(B):.0f}", size=12, color=main("loss"),
               anchor="end" if B == 64 else "start", weight="bold")
    # x 轴刻度
    for B in Bs:
        s.line(X(B), yl1, X(B), yl1 + 4, color=INK, sw=1)
        s.text(X(B), yl1 + 15, str(B), size=12, color=MUTED)
        s.line(X(B), yt1, X(B), yt1 + 4, color=INK, sw=1)
    s.text((gx0 + gx1) / 2, yl1 + 36, "批次大小 $B$（同时生成的请求数，对数刻度）", size=13)
    s.text(gx1, yl0 - 10, "再加上凑批的排队时间，单个用户等得更久", size=12.5, color=main("loss"), anchor="end")
    s.save(OUT / "25_batching-throughput-latency.svg")


# ---------------------------------------------------------------------------
# 17 BPE：反复合并最高频的相邻对
# ---------------------------------------------------------------------------
def bpe_rounds(corpus, n):
    words = [(tuple(w), c) for w, c in corpus]
    rounds = []
    for _ in range(n):
        pc = Counter()
        for w, c in words:
            for a, b in zip(w, w[1:]):
                pc[(a, b)] += c
        top = pc.most_common()
        assert top[0][1] > top[1][1], "示例语料不应出现并列最高频"
        best = top[0][0]
        nw = []
        for w, c in words:
            out, i = [], 0
            while i < len(w):
                if i < len(w) - 1 and (w[i], w[i + 1]) == best:
                    out.append(w[i] + w[i + 1])
                    i += 2
                else:
                    out.append(w[i])
                    i += 1
            nw.append((tuple(out), c))
        words = nw
        rounds.append((top[:3], best, words))
    return rounds


def fig17():
    corpus = [("机器学习", 6), ("深度学习", 4), ("学习率", 3), ("机器人", 2), ("深度", 1)]
    rounds = bpe_rounds(corpus, 4)
    merged = ["".join(r[1]) for r in rounds]
    assert merged == ["学习", "机器", "机器学习", "深度"], merged
    assert rounds[0][0][0][1] == 13 and rounds[1][0][0][1] == 8 and rounds[2][0][0][1] == 6 and rounds[3][0][0][1] == 5
    base = sorted({ch for w, _ in corpus for ch in w}, key=lambda ch: "".join(w for w, _ in corpus).index(ch))
    W = 1060
    row_h = 74
    y_rows = 178
    H = y_rows + row_h * 4 + 56
    s = SVG(W, H, "BPE：反复合并最高频的相邻对", "在带词频的小语料上，每轮统计相邻 token 对的出现次数，合并最高频的一对并加入词表。")
    s.text(W / 2, 26, "BPE：每一轮把「出现最多的相邻一对」合并成一个新 token", size=17, weight="bold")

    # 列
    cx_seg, cx_cnt, cx_voc = 40, 650, 912
    s.text(cx_seg, 64, "语料中的每个词（括号内是出现次数）及其当前切分", size=14, weight="bold", anchor="start")
    s.text(cx_cnt + 105, 64, "相邻对计数（前三）", size=14, weight="bold", anchor="middle")
    s.text(cx_voc + 70, 64, "词表新增", size=14, weight="bold", anchor="middle")

    CW = 24  # 单字格宽

    def tokw(tok):
        return CW * len(tok) - (len(tok) - 1) * 2

    col_x, x = [], 40
    for w, c in corpus:  # 按初始（最宽）切分排列各词的起点
        col_x.append(x)
        x += sum(tokw(ch) + 3 for ch in w) + 40
    assert x < cx_cnt + 40, x

    def draw_seg(y, words, newtok=None):
        for (w, c), x in zip(words, col_x):
            xx = x
            for tok in w:
                tw = tokw(tok)
                is_new = newtok is not None and tok == newtok
                key = "q" if is_new else ("attn" if len(tok) > 1 else "gray")
                s.rect(xx, y - 13, tw, 26, fill=light(key) if not is_new else main(key), stroke=main(key),
                       sw=1.1, rx=5)
                s.text(xx + tw / 2, y, tok, size=14, color=WHITE if is_new else INK,
                       weight="bold" if is_new else "normal")
                xx += tw + 3
            s.text(xx + 2, y, f"×{c}", size=12, color=MUTED, anchor="start")

    # 初始
    y0 = 112
    s.text(cx_seg - 4, y0 - 26, "初始：按单字切开", size=13, color=MUTED, anchor="start")
    draw_seg(y0, [(tuple(w), c) for w, c in corpus])
    s.text(cx_voc + 70, y0 - 26, f"基础字符（{len(base)} 个）", size=12.5, color=MUTED)
    s.text(cx_voc + 70, y0, " ".join(base), size=14)
    s.line(30, 148, W - 30, 148, color=BORDER, sw=1)

    vocab = len(base)
    for r, (top, best, words) in enumerate(rounds):
        y = y_rows + r * row_h
        if r % 2 == 0:
            s.rect(24, y - row_h / 2 + 4, W - 48, row_h - 8, fill=PANEL, stroke="none", rx=8)
        s.badge(cx_seg + 6, y - 22, str(r + 1), key="q", r=10, size=12)
        s.text(cx_seg + 22, y - 22, f"第 {r + 1} 轮", size=12.5, color=MUTED, anchor="start")
        draw_seg(y + 10, words, newtok="".join(best))
        # 计数
        for j, ((a, b), n) in enumerate(top):
            yy = y - 20 + j * 18
            hl = j == 0
            lab = f"{a} + {b}"
            s.text(cx_cnt + 120, yy, lab, size=13 if hl else 12.5, anchor="end",
                   color=main("q") if hl else MUTED, weight="bold" if hl else "normal")
            s.rect(cx_cnt + 128, yy - 6, n * 7, 12, fill=main("q") if hl else light("gray"), stroke="none", rx=2)
            s.text(cx_cnt + 134 + n * 7, yy, str(n), size=12.5, anchor="start",
                   color=main("q") if hl else MUTED, weight="bold" if hl else "normal")
        vocab += 1
        s.pill(cx_voc + 70, y - 4, "+ " + "".join(best), key="q", size=14, pad=10, weight="bold")
        s.text(cx_voc + 70, y + 22, f"词表大小 {vocab}", size=12.5, color=MUTED)
    yb = y_rows + row_h * 4 - 6
    s.text(W / 2, yb + 18, "高频组合（学习、机器学习）成为整体 token；低频的「率」「人」仍单独成 token。真实分词器通常在字节或字符上做同样的事，合并数万轮。",
           size=12.5, color=MUTED)
    s.save(OUT / "17_bpe-tokenization.svg")


# ---------------------------------------------------------------------------
# 18 分词 → token id → 查嵌入表 → X
# ---------------------------------------------------------------------------
def fig18():
    toks = ["模型", "的", "␣align", "ment"]
    ids = [3812, 109, 17531, 434]
    cols = ["k", "v", "attn", "q"]
    W, H = 1060, 470
    s = SVG(W, H, "分词与嵌入查表", "tokenizer 把文本切成 token 并给出 id；id 是嵌入矩阵的行号，查表取出那一行向量，组成 X。")

    # ① 文本
    s.text(110, 40, "① 文本", size=14.5, weight="bold")
    s.box(30, 60, 160, 46, "模型的 alignment", key="data", size=15, weight="normal")
    s.varrow(110, 110, 140, color=LINE)
    s.text(118, 125, "tokenizer", size=12.5, color=MUTED, anchor="start")
    # ② token 与 id
    s.text(110, 160, "② token → id", size=14.5, weight="bold")
    ys = [200 + i * 54 for i in range(4)]
    for t, i_, y, k in zip(toks, ids, ys, cols):
        s.rect(34, y - 16, 84, 32, fill=light(k), stroke=main(k), sw=1.2, rx=7)
        s.text(76, y, t, size=14.5)
        s.harrow(122, 146, y, color=LINE, head=0.8)
        s.text(178, y, str(i_), size=15, weight="bold", family=MONO)
    s.text(110, 420, "␣ 表示空格；切法与 id 均为示例", size=12, color=MUTED)

    # ③ 嵌入矩阵：按 id 排序的若干行 + 省略号
    mx, my, cw, rh = 380, 92, 26, 22
    d = 8
    s.text(mx + d * cw / 2, 40, "③ 嵌入矩阵 $E$（$V$ 行 × $d$ 列，可学习）", size=14.5, weight="bold")
    rows = [("0", None), ("1", None), ("⋮", "gap"), ("109", 1), ("⋮", "gap"), ("434", 3), ("⋮", "gap"),
            ("3812", 0), ("⋮", "gap"), ("17531", 2), ("⋮", "gap"), ("$V$−1", None)]
    row_y = {}
    y = my
    rng = RNG(7)
    for lab, tag in rows:
        if tag == "gap":
            s.text(mx + d * cw / 2, y + rh / 2 - 2, "⋮", size=15, color=MUTED)
            s.text(mx - 10, y + rh / 2 - 2, "⋮", size=13, color=MUTED, anchor="end")
            y += rh
            continue
        hl = tag is not None
        k = cols[tag] if hl else "gray"
        for j in range(d):
            v = rng.u()
            fill = mix(light(k), main(k), 0.25 + 0.6 * v) if hl else mix(WHITE, "#C9CED6", 0.3 + 0.5 * v)
            s.rect(mx + j * cw, y, cw, rh, fill=fill, stroke=WHITE, sw=1.2)
        s.text(mx - 10, y + rh / 2, lab, size=13, anchor="end", family=MONO if lab[0].isdigit() else None,
               color=INK if hl else MUTED, weight="bold" if hl else "normal")
        if hl:
            s.rect(mx - 1, y - 1, d * cw + 2, rh + 2, fill="none", stroke=main(k), sw=1.8, rx=2)
            row_y[tag] = y + rh / 2
        y += rh
    s.text(mx - 10, my - 14, "行号", size=12, color=MUTED, anchor="end")
    s.brace(mx, y + 6, mx + d * cw, y + 6, "$d$ 维（常为几千）", size=12.5, depth=6)
    # id → 行
    for i_, (y0, k) in enumerate(zip(ys, cols)):
        s.arrow([(212, y0), (mx - 52, row_y[i_])], color=main(k), sw=1.4, opacity=0.85)
    s.rect(220, 412, 300, 32, fill=light("attn"), stroke=main("attn"), sw=1.1, rx=8)
    s.text(370, 428, "id 只是行号：查表 = 取出第 id 行", size=13.5, weight="bold", color=main("attn"))

    # ④ X
    xx, xy = 760, 110
    s.text(xx + d * cw / 2, 40, "④ 输入矩阵 $X$（$T$×$d$）", size=14.5, weight="bold")
    rng = RNG(7)
    # 重新生成相同的数值，保证 X 的每一行与 E 中对应行一模一样
    vals = {}
    for lab, tag in rows:
        if tag == "gap":
            continue
        vs = [rng.u() for _ in range(d)]
        if tag is not None:
            vals[tag] = vs
    for i_ in range(4):
        k = cols[i_]
        y0 = xy + i_ * 46
        for j in range(d):
            s.rect(xx + j * cw, y0, cw, 30, fill=mix(light(k), main(k), 0.25 + 0.6 * vals[i_][j]),
                   stroke=WHITE, sw=1.2)
        s.text(xx - 10, y0 + 15, toks[i_], size=13, anchor="end")
        s.arrow([(mx + d * cw + 8, row_y[i_]), (xx - 50, y0 + 15)], color=main(k), sw=1.4, opacity=0.85)
    s.brace(xx + d * cw + 6, xy, xx + d * cw + 6, xy + 3 * 46 + 30, "$T$ = 4 行", size=12.5, depth=6)
    s.varrow(xx + d * cw / 2, xy + 4 * 46 + 4, xy + 4 * 46 + 44, color=INK, sw=1.6)
    s.box(xx - 10, xy + 4 * 46 + 48, d * cw + 20, 46, "+ 位置信息 → Transformer", key="gray", size=14)
    s.text(xx + d * cw / 2, xy + 4 * 46 + 118, "逐层更新为上下文表示，最后输出 logits", size=12.5, color=MUTED)
    s.save(OUT / "18_tokenization-and-embedding.svg")


# ---------------------------------------------------------------------------
# 19 温度 / top-k / top-p
# ---------------------------------------------------------------------------
def fig19():
    cands = ["好", "热", "冷", "差"]
    logits = [2, 1, 0, -1]
    taus = [0.5, 1.0, 2.0]
    P = {t: softmax(logits, t) for t in taus}
    assert [round(x, 3) for x in P[1.0]] == [0.644, 0.237, 0.087, 0.032]
    W, H = 1080, 470
    s = SVG(W, H, "温度与截断采样", "温度缩放 logits 改变分布的集中程度；top-k 固定候选个数，top-p 固定累计概率。")

    # ---------------- 左：温度 ----------------
    s.panel(20, 20, 540, 430, "温度 τ：先把 logits 除以 τ，再做 softmax", key="attn")
    s.text(40, 62, "上下文：「今天天气很 ___」", size=14, anchor="start")
    s.text(40, 86, "候选 logits：好 = 2，热 = 1，冷 = 0，差 = −1", size=13.5, anchor="start", color=MUTED)
    gy0, gy1 = 130, 370  # 柱子区域
    bw = 26
    group_w = 160
    for g, t in enumerate(taus):
        gx = 60 + g * (group_w + 10)
        key = "k" if t < 1 else ("attn" if t == 1 else "q")
        s.text(gx + group_w / 2 - 10, gy0 - 6, f"τ = {t:g}", size=15, weight="bold", color=main(key))
        sub = {0.5: "更尖锐、更确定", 1.0: "原始分布", 2.0: "更平坦、更多样"}[t]
        s.text(gx + group_w / 2 - 10, gy0 + 16, sub, size=12.5, color=MUTED)
        for i, p in enumerate(P[t]):
            x = gx + i * (bw + 9)
            h = p * (gy1 - gy0 - 50)
            s.rect(x, gy1 - h, bw, h, fill=main(key) if i == 0 else mix(main(key), WHITE, 0.45), rx=3)
            s.text(x + bw / 2, gy1 - h - 10, f"{p * 100:.0f}%" if p >= 0.01 else "<1%", size=12, color=INK)
            s.text(x + bw / 2, gy1 + 16, cands[i], size=14)
        s.line(gx - 6, gy1, gx + 4 * (bw + 9) - 3, gy1, color=INK, sw=1)
    s.text(290, 418, "τ 越小越接近贪心（总选「好」）；τ 越大，低概率词越容易被抽中", size=12.5, color=MUTED)

    # ---------------- 右：top-k / top-p ----------------
    names = ["A", "B", "C", "D", "E"]
    p = [0.40, 0.25, 0.20, 0.10, 0.05]
    cum = [sum(p[:i + 1]) for i in range(5)]
    kk = [x / sum(p[:2]) for x in p[:2]]
    n_top_p = next(i for i, c_ in enumerate(cum) if c_ >= 0.8 - 1e-12) + 1
    assert n_top_p == 3 and abs(cum[2] - 0.85) < 1e-9
    pp = [x / cum[2] for x in p[:3]]
    assert [round(x * 100, 1) for x in kk] == [61.5, 38.5]
    assert [round(x * 100, 1) for x in pp] == [47.1, 29.4, 23.5]

    s.panel(580, 20, 480, 430, "截断后再采样：top-k 与 top-p", key="q")
    bx0, by1, bh = 640, 210, 120
    bwid = 54
    s.text(bx0 - 16, 62, "五个候选（已按概率排序）", size=13.5, anchor="start", color=MUTED)
    for i in range(5):
        x = bx0 + i * (bwid + 18)
        h = p[i] / 0.4 * bh
        s.rect(x, by1 - h, bwid, h, fill=light("gray"), stroke=main("gray"), sw=1, rx=3)
        s.text(x + bwid / 2, by1 - h - 10, f"{p[i]:.2f}", size=12.5)
        s.text(x + bwid / 2, by1 + 15, names[i], size=14, weight="bold")
        s.text(x + bwid / 2, by1 + 35, f"累计 {cum[i]:.2f}", size=11.5 if i else 11.5, color=MUTED)
    s.line(bx0 - 8, by1, bx0 + 5 * (bwid + 18) - 10, by1, color=INK, sw=1)
    # k=2 截断线
    xk = bx0 + 2 * (bwid + 18) - 9
    s.line(xk, 82, xk, by1 + 2, color=main("k"), sw=1.8, dash="5 4")
    s.text(xk - 6, 92, "top-k：k = 2", size=12.5, color=main("k"), anchor="end", weight="bold")
    xp = bx0 + 3 * (bwid + 18) - 9
    s.line(xp, 82, xp, by1 + 2, color=main("q"), sw=1.8, dash="5 4")
    s.text(xp + 6, 92, "top-p：累计 ≥ 0.8", size=12.5, color=main("q"), anchor="start", weight="bold")

    # 归一化结果：堆叠条
    def stacked(y, probs, key, label, note):
        s.text(600, y - 28, label, size=13.5, anchor="start", weight="bold", color=main(key))
        s.text(1040, y - 28, note, size=12.5, anchor="end", color=MUTED)
        x = 600
        total = 440
        for i, q in enumerate(probs):
            w = total * q
            s.rect(x, y - 15, w - 3, 30, fill=mix(main(key), WHITE, 0.15 + 0.25 * i), rx=4)
            s.text(x + (w - 3) / 2, y, f"{names[i]}  {q * 100:.1f}%", size=13, color=WHITE, weight="bold")
            x += w

    stacked(300, kk, "k", "top-k（k = 2）：保留 A、B", "0.40/0.65，0.25/0.65")
    stacked(380, pp, "q", "top-p（p = 0.8）：保留 A、B、C", "累计 0.85，除以 0.85")
    s.text(820, 422, "两者都在保留的候选里重新归一化，再按新概率抽取", size=12.5, color=MUTED)
    s.save(OUT / "19_temperature-next-token-distribution.svg")


if __name__ == "__main__":
    fig08()
    fig09()
    fig25()
    fig17()
    fig18()
    fig19()
