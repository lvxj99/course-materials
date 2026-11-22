import { PALETTE as P, wrapSvg, box, labelBox, pill, arrow, pathArrow, vecBars, noteBar, esc } from '../lib/svg.mjs';

// 31: Top-k and Top-p Truncation
function fig31() {
  const width = 1160, height = 620;
  let b = '';

  const cands = [
    ['学习', 0.42],
    ['理解', 0.26],
    ['掌握', 0.14],
    ['研究', 0.08],
    ['探索', 0.04],
    ['阅读', 0.03],
    ['记忆', 0.02],
    ['苹果', 0.01],
  ];

  // Left Panel: Top-k (k = 3)
  b += box({ x: 34, y: 100, w: 534, h: 422, rx: 14, fill: '#FFFFFF', stroke: P.blue, sw: 1.6 });
  b += pill({ x: 54, y: 116, w: 220, h: 26, fill: P.bluePale, stroke: P.blue, text: 'Top-k 采样（固定保留前 k = 3 个）', color: P.blueDark, fontSize: 12 });
  b += `<text x="54" y="162" font-size="12.5" fill="${P.textSec}">无论概率分布是尖锐还是平缓，始终一刀切只留前 k 个候选，再重新归一化</text>`;

  const lx = 78, ly = 196, lw = 456, lh = 228;
  // Grid lines
  [0, 0.25, 0.5].forEach((lv) => {
    const gy = ly + lh - (lv / 0.5) * lh;
    b += `<line x1="${lx}" y1="${gy}" x2="${lx + lw}" y2="${gy}" stroke="#E2E8F0" stroke-dasharray="3 3" />`;
    b += `<text x="${lx - 8}" y="${gy + 4}" text-anchor="end" font-size="10.5" fill="${P.textMuted}">${Math.round(lv * 100)}%</text>`;
  });
  b += `<line x1="${lx}" y1="${ly + lh}" x2="${lx + lw}" y2="${ly + lh}" stroke="${P.slate}" stroke-width="1.5" />`;

  cands.forEach(([tok, pr], i) => {
    const bw = 38, gap = 17;
    const rx = lx + 12 + i * (bw + gap);
    const rh = Math.max(4, (pr / 0.5) * lh);
    const ry = ly + lh - rh;
    const kept = i < 3;
    b += `<rect x="${rx}" y="${ry.toFixed(1)}" width="${bw}" height="${rh.toFixed(1)}" rx="5" fill="${kept ? P.blue : '#CBD5E1'}" fill-opacity="${kept ? 0.88 : 0.7}" />`;
    b += `<text x="${rx + bw / 2}" y="${(ry - 6).toFixed(1)}" text-anchor="middle" font-size="10.5" font-weight="${kept ? 700 : 500}" fill="${kept ? P.blueDark : P.textMuted}">${Math.round(pr * 100)}%</text>`;
    b += `<text x="${rx + bw / 2}" y="${ly + lh + 18}" text-anchor="middle" font-size="11.5" font-weight="${kept ? 700 : 400}" fill="${kept ? P.text : P.textMuted}">${tok}</text>`;
  });

  // Vertical cutoff line after 3rd bar
  const cutK = lx + 12 + 3 * (38 + 17) - 8.5;
  b += `<line x1="${cutK}" y1="${ly - 10}" x2="${cutK}" y2="${ly + lh + 26}" stroke="${P.rose}" stroke-width="2.2" stroke-dasharray="6 4" />`;
  b += pill({ x: cutK - 54, y: ly - 24, w: 108, h: 22, fill: P.roseLight, stroke: P.rose, text: '固定截断 k = 3', color: P.roseDark, fontSize: 10.5 });
  b += `<text x="${cutK - 60}" y="${ly + 32}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.blueDark}">✓ 保留前 3 个</text>`;
  b += `<text x="${cutK + 132}" y="${ly + 32}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.roseDark}">✗ 丢弃其余候选（概率置 0）</text>`;

  b += box({ x: 54, y: 462, w: 494, h: 44, rx: 9, fill: P.bluePale, stroke: P.blueLight, shadow: false });
  b += `<text x="70" y="489" font-size="12" fill="${P.blueDark}">保留总概率：42% + 26% + 14% = 82% → 归一化后为 [51%, 32%, 17%]</text>`;

  // Right Panel: Top-p / Nucleus (p = 0.85)
  b += box({ x: 592, y: 100, w: 534, h: 422, rx: 14, fill: '#FFFFFF', stroke: P.teal, sw: 1.6 });
  b += pill({ x: 612, y: 116, w: 266, h: 26, fill: P.tealPale, stroke: P.teal, text: 'Top-p / 核采样（累计概率阈值 p = 0.85）', color: P.tealDark, fontSize: 12 });
  b += `<text x="612" y="162" font-size="12.5" fill="${P.textSec}">从高到低累加概率，保留刚好达到阈值 p 的最小集合（候选数动态自适应）</text>`;

  const rx0 = 636, ry0 = 196, rw = 456, rh0 = 228;
  // Grid lines for right axis (0%, 50%, 100% cumulative)
  [0, 0.5, 1.0].forEach((lv) => {
    const gy = ry0 + rh0 - lv * rh0;
    b += `<line x1="${rx0}" y1="${gy}" x2="${rx0 + rw}" y2="${gy}" stroke="#E2E8F0" stroke-dasharray="3 3" />`;
    b += `<text x="${rx0 + rw + 6}" y="${gy + 4}" font-size="10" fill="${P.violetDark}">${Math.round(lv * 100)}%</text>`;
  });
  b += `<line x1="${rx0}" y1="${ry0 + rh0}" x2="${rx0 + rw}" y2="${ry0 + rh0}" stroke="${P.slate}" stroke-width="1.5" />`;

  // Threshold horizontal line p = 0.85
  const pLineY = ry0 + rh0 - 0.85 * rh0;
  b += `<line x1="${rx0}" y1="${pLineY.toFixed(1)}" x2="${rx0 + rw}" y2="${pLineY.toFixed(1)}" stroke="${P.violet}" stroke-width="1.8" stroke-dasharray="5 3" />`;
  b += `<text x="${rx0 + rw - 4}" y="${(pLineY - 6).toFixed(1)}" text-anchor="end" font-size="11" font-weight="700" fill="${P.violetDark}">阈值 p = 85%</text>`;

  // Bars & Cumulative curve
  let cum = 0;
  let cumPath = '';
  const cumPts = [];
  cands.forEach(([tok, pr], i) => {
    const bw = 38, gap = 17;
    const bx = rx0 + 12 + i * (bw + gap);
    const bh = Math.max(4, (pr / 0.5) * rh0 * 0.72); // scaled neatly under cumulative curve
    const by = ry0 + rh0 - bh;
    const kept = i < 4; // 0.42 + 0.26 + 0.14 + 0.08 = 0.90 >= 0.85
    b += `<rect x="${bx}" y="${by.toFixed(1)}" width="${bw}" height="${bh.toFixed(1)}" rx="5" fill="${kept ? P.teal : '#CBD5E1'}" fill-opacity="${kept ? 0.85 : 0.7}" />`;
    b += `<text x="${bx + bw / 2}" y="${ry0 + rh0 + 18}" text-anchor="middle" font-size="11.5" font-weight="${kept ? 700 : 400}" fill="${kept ? P.text : P.textMuted}">${tok}</text>`;

    cum += pr;
    const cx = bx + bw / 2;
    const cy = ry0 + rh0 - cum * rh0;
    cumPts.push([cx, cy, cum, kept]);
    cumPath += (i === 0 ? 'M ' : ' L ') + cx.toFixed(1) + ' ' + cy.toFixed(1);
  });

  // Draw cumulative curve on top
  b += `<path d="${cumPath}" fill="none" stroke="${P.violet}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" />`;
  cumPts.forEach(([cx, cy, cval, kept], idx) => {
    b += `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="4.5" fill="${idx === 3 ? P.amber : '#FFFFFF'}" stroke="${P.violet}" stroke-width="2.2" />`;
    if (idx < 4) {
      b += `<text x="${cx.toFixed(1)}" y="${(cy - 9).toFixed(1)}" text-anchor="middle" font-size="10.5" font-weight="700" fill="${P.violetDark}">${Math.round(cval * 100)}%</text>`;
    }
  });

  // Vertical cutoff line after 4th bar
  const cutP = rx0 + 12 + 4 * (38 + 17) - 8.5;
  b += `<line x1="${cutP}" y1="${ry0 - 10}" x2="${cutP}" y2="${ry0 + rh0 + 26}" stroke="${P.rose}" stroke-width="2.2" stroke-dasharray="6 4" />`;
  b += pill({ x: cutP - 58, y: ry0 - 28, w: 116, h: 22, fill: P.roseLight, stroke: P.rose, text: '达标截断（留 4 词）', color: P.roseDark, fontSize: 10.5 });

  b += box({ x: 612, y: 462, w: 494, h: 44, rx: 9, fill: P.tealPale, stroke: P.tealLight, shadow: false });
  b += `<text x="628" y="489" font-size="12" fill="${P.tealDark}">前 3 词累计 82% &lt; 85%，加入第 4 词达 90% ≥ 85% → 切掉剩余 4 个长尾词！</text>`;

  // Bottom sampling pipeline bar
  b += box({ x: 34, y: 540, w: 1092, h: 52, rx: 12, fill: P.amberPale, stroke: P.amberLight, shadow: false });
  b += `<text x="580" y="571" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.amberDark}">采样完整流水线：原始 Logits  ──▶  ① Temperature 缩放改变分布形状  ──▶  ② Top-k / Top-p 切掉长尾低概率词  ──▶  ③ 重归一化并随机采样</text>`;

  return wrapSvg({
    width, height,
    title: 'Top-k 与 Top-p（核采样）的截断方式对比',
    subtitle: '防止模型不小心抽中极低概率的荒谬词（长尾噪声）：Top-k 固定个数，Top-p 按累计概率动态自适应',
    badge: '§9.2 截断采样',
    body: b,
  });
}

// 20: Training to Usage Workflow
function fig20() {
  const width = 1160, height = 580;
  let b = '';

  // Post-training dashed grouping bracket covering stage 2 & 3
  b += box({ x: 312, y: 102, w: 544, h: 368, rx: 16, fill: P.violetPale, stroke: P.violet, sw: 1.5, dash: '6 4', shadow: false });
  b += pill({ x: 472, y: 90, w: 224, h: 24, fill: P.violet, stroke: P.violetDark, text: '后训练阶段（Post-training）', color: '#FFFFFF', fontSize: 11.5 });

  const stages = [
    {
      x: 34, w: 250, col: P.blue, bg: P.bluePale, dark: P.blueDark,
      step: '阶段 1 · 预训练',
      title: 'Pre-training',
      model: '产出：基础模型（Base Model）',
      data: '海量网页、书籍、代码\n（数万亿 Token）',
      signal: '自监督：Next Token Prediction\n（最小化交叉熵）',
      cap: '具备广泛世界知识与语言规律，\n但只会“顺着往下续写”。',
    },
    {
      x: 326, w: 248, col: P.teal, bg: P.tealPale, dark: P.tealDark,
      step: '阶段 2 · 指令微调',
      title: 'SFT（监督微调）',
      model: '产出：指令模型（Instruct）',
      data: '高质量「指令—示范回答」对\n（含推导与代码步骤）',
      signal: '监督学习：只在回答部分算\n交叉熵损失（可用 LoRA）',
      cap: '从“会续写”走向“听懂要求、\n按格式清晰回答问题”。',
    },
    {
      x: 594, w: 248, col: P.violet, bg: '#FFFFFF', dark: P.violetDark,
      step: '阶段 3 · 偏好与验证优化',
      title: 'RLHF/DPO & RLVR',
      model: '产出：对齐 / 推理大模型',
      data: '人类偏好对比（更好）+\n数学/代码规则验证（更对）',
      signal: 'RL 奖励信号：PPO / DPO /\nGRPO 提升高分轨迹概率',
      cap: '对齐人类风格与安全标准，\n涌现深度反思与复杂推理能力。',
    },
    {
      x: 876, w: 250, col: P.emerald, bg: P.emeraldPale, dark: P.tealDark,
      step: '阶段 4 · 实际使用',
      title: 'Inference & 应用',
      model: '权重固定 · 面向真实任务',
      data: 'Prompt、Few-shot 示例、\nRAG 文档与工具结果',
      signal: '不改模型参数，通过上下文\n条件化 + 推理预算求解',
      cap: '对话、文档问答、代码工程、\n多模态分析与 Agent 任务执行。',
    },
  ];

  stages.forEach((st, idx) => {
    b += box({ x: st.x, y: 126, w: st.w, h: 328, rx: 14, fill: '#FFFFFF', stroke: st.col, sw: 1.8 });
    b += `<rect x="${st.x}" y="126" width="${st.w}" height="62" rx="14" fill="${st.bg === '#FFFFFF' ? P.violetPale : st.bg}" />`;
    b += `<rect x="${st.x}" y="172" width="${st.w}" height="16" fill="${st.bg === '#FFFFFF' ? P.violetPale : st.bg}" />`;
    b += `<text x="${st.x + st.w / 2}" y="150" text-anchor="middle" font-size="11.5" font-weight="700" fill="${st.dark}">${st.step}</text>`;
    b += `<text x="${st.x + st.w / 2}" y="174" text-anchor="middle" font-size="16" font-weight="700" fill="${P.text}">${st.title}</text>`;

    // Data, Signal, Capability blocks
    const blocks = [
      { lbl: '输入数据', txt: st.data, y: 204 },
      { lbl: '学习信号 / 机制', txt: st.signal, y: 274 },
      { lbl: '形成的能力', txt: st.cap, y: 344 },
    ];
    blocks.forEach((bl) => {
      b += `<text x="${st.x + 14}" y="${bl.y}" font-size="11" font-weight="700" fill="${st.dark}">${bl.lbl}</text>`;
      const [l1, l2] = bl.txt.split('\n');
      b += `<text x="${st.x + 14}" y="${bl.y + 18}" font-size="11.5" fill="${P.text}">${esc(l1)}</text>`;
      if (l2) b += `<text x="${st.x + 14}" y="${bl.y + 35}" font-size="11.5" fill="${P.textSec}">${esc(l2)}</text>`;
    });

    // Output badge at bottom of card
    b += pill({ x: st.x + 12, y: 414, w: st.w - 24, h: 28, fill: st.bg === '#FFFFFF' ? P.violetPale : st.bg, stroke: st.col, text: st.model, color: st.dark, fontSize: 11 });

    // Arrow to next stage
    if (idx < stages.length - 1) {
      const x1 = st.x + st.w + 2, x2 = stages[idx + 1].x - 4;
      b += arrow(x1, 286, x2, 286, { color: st.col, marker: idx === 0 ? 'arr-blue' : (idx === 1 ? 'arr-teal' : 'arr-violet'), sw: 2.5 });
    }
  });

  // Bottom comparison strip: Weight Update vs Fixed Weights
  b += box({ x: 34, y: 492, w: 822, h: 52, rx: 10, fill: P.bluePale, stroke: P.blueLight, shadow: false });
  b += `<text x="445" y="515" text-anchor="middle" font-size="13" font-weight="700" fill="${P.blueDark}">◀ 阶段 1 ~ 3：参数学习阶段（反向传播更新神经网络权重 θ，将知识与行为写进模型） ▶</text>`;
  b += `<text x="445" y="535" text-anchor="middle" font-size="11.5" fill="${P.textSec}">算力消耗逐级递减，但数据质量与反馈精准度要求逐级升高</text>`;

  b += box({ x: 876, y: 492, w: 250, h: 52, rx: 10, fill: P.emeraldPale, stroke: P.emerald, shadow: false });
  b += `<text x="1001" y="515" text-anchor="middle" font-size="13" font-weight="700" fill="${P.tealDark}">阶段 4：权重冻结</text>`;
  b += `<text x="1001" y="535" text-anchor="middle" font-size="11.5" fill="${P.textSec}">靠上下文工程 + 推理计算发挥能力</text>`;

  return wrapSvg({
    width, height,
    title: '一个可用大模型的诞生全流程：从预训练、后训练到实际使用',
    subtitle: '同样的 Transformer 架构，在不同阶段配以不同数据与学习信号，逐步演进为通用智能助手',
    badge: '§10 训练全流程',
    body: b,
  });
}

// 21: Three Scaling Laws (Pre-training, Post-training, Test-time Scaling)
function fig21() {
  const width = 1160, height = 610;
  let b = '';

  function scalingCard({ x, w, title, badge, col, bg, dark, xLabel, yLabel, curveFn, pts, desc1, desc2, extra = '' }) {
    let out = box({ x, y: 100, w, h: 472, rx: 14, fill: '#FFFFFF', stroke: col, sw: 1.7 });
    out += `<rect x="${x}" y="100" width="${w}" height="46" rx="14" fill="${bg}" />`;
    out += `<rect x="${x}" y="132" width="${w}" height="14" fill="${bg}" />`;
    out += `<text x="${x + w / 2}" y="129" text-anchor="middle" font-size="15.5" font-weight="700" fill="${dark}">${title}</text>`;

    // Plot area
    const px = x + 46, py = 172, pw = w - 68, ph = 186;
    out += `<rect x="${px}" y="${py}" width="${pw}" height="${ph}" rx="8" fill="#F8FAFC" stroke="${P.borderLight}" />`;
    for (let i = 1; i <= 3; i++) {
      const gy = py + (i / 4) * ph;
      out += `<line x1="${px}" y1="${gy}" x2="${px + pw}" y2="${gy}" stroke="#E2E8F0" stroke-dasharray="3 3" />`;
    }
    out += `<line x1="${px}" y1="${py + ph}" x2="${px + pw}" y2="${py + ph}" stroke="${P.slate}" stroke-width="1.5" marker-end="url(#arr-slate)" />`;
    out += `<line x1="${px}" y1="${py + ph}" x2="${px}" y2="${py}" stroke="${P.slate}" stroke-width="1.5" marker-end="url(#arr-slate)" />`;
    out += `<text x="${px + pw / 2}" y="${py + ph + 22}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.text}">${xLabel}</text>`;
    out += `<text x="${px - 26}" y="${py + ph / 2}" text-anchor="middle" font-size="11" font-weight="700" fill="${dark}" transform="rotate(-90 ${px - 26} ${py + ph / 2})">${yLabel}</text>`;

    // Curve
    let d = '';
    for (let i = 0; i <= 60; i++) {
      const t = i / 60;
      const v = curveFn(t);
      const sx = px + 10 + t * (pw - 24);
      const sy = py + ph - 12 - v * (ph - 30);
      d += (i === 0 ? 'M ' : ' L ') + sx.toFixed(1) + ' ' + sy.toFixed(1);
    }
    out += `<path d="${d}" fill="none" stroke="${col}" stroke-width="3" stroke-linecap="round" />`;
    pts.forEach(([t, lbl]) => {
      const v = curveFn(t);
      const sx = px + 10 + t * (pw - 24);
      const sy = py + ph - 12 - v * (ph - 30);
      out += `<circle cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" r="4.5" fill="#FFFFFF" stroke="${col}" stroke-width="2.2" />`;
      out += `<text x="${sx.toFixed(1)}" y="${(sy - 10).toFixed(1)}" text-anchor="middle" font-size="10" font-weight="700" fill="${dark}">${lbl}</text>`;
    });

    // Descriptions
    out += `<line x1="${x + 20}" y1="398" x2="${x + w - 20}" y2="398" stroke="${P.borderLight}" />`;
    out += `<text x="${x + 20}" y="422" font-size="12.5" font-weight="700" fill="${dark}">${badge}</text>`;
    out += `<text x="${x + 20}" y="446" font-size="12" fill="${P.text}">${desc1}</text>`;
    out += `<text x="${x + 20}" y="466" font-size="12" fill="${P.textSec}">${desc2}</text>`;
    out += extra;
    return out;
  }

  // 1. Pre-training Scaling
  b += scalingCard({
    x: 34, w: 346,
    title: '① Pre-training Scaling（预训练扩展）',
    badge: '投入：更多数据 × 更大模型 × 更多算力',
    col: P.blue, bg: P.bluePale, dark: P.blueDark,
    xLabel: '预训练算力 / 数据与参数规模（对数）',
    yLabel: '基础能力 / 预测精度',
    curveFn: (t) => 0.12 + 0.80 * Math.pow(t, 0.72),
    pts: [[0.18, '1B'], [0.52, '70B'], [0.88, '1T+']],
    desc1: '• Chinchilla 法则：参数与数据需同步扩展',
    desc2: '  （经典比例：每 1 参数配约 20 Token）',
    extra: pill({ x: 54, y: 500, w: 306, h: 48, fill: P.bluePale, stroke: P.blueLight, text: '构建通用语言、世界知识与代码底座', color: P.blueDark, fontSize: 12 }),
  });

  // 2. Post-training Scaling
  b += scalingCard({
    x: 407, w: 346,
    title: '② Post-training Scaling（后训练扩展）',
    badge: '投入：高质量合成数据 × 强化学习步数',
    col: P.teal, bg: P.tealPale, dark: P.tealDark,
    xLabel: '后训练 RL 计算量 / 验证轨迹数（对数）',
    yLabel: '推理与指令能力',
    curveFn: (t) => 0.14 + 0.78 * (1 / (1 + Math.exp(-6 * (t - 0.45)))),
    pts: [[0.18, 'SFT'], [0.55, 'RLHF'], [0.88, 'RLVR/GRPO']],
    desc1: '• 通过可验证奖励（数学/代码/测试）大规模强化',
    desc2: '• 让模型主动涌现反思、拆解与纠错习惯',
    extra: pill({ x: 427, y: 500, w: 306, h: 48, fill: P.tealPale, stroke: P.tealLight, text: '把底座潜力转化为高可靠解题与对齐能力', color: P.tealDark, fontSize: 12 }),
  });

  // 3. Test-time Scaling (with Depth vs Width mini visual!)
  const extraTT = `
    <rect x="800" y="486" width="146" height="66" rx="8" fill="${P.violetPale}" stroke="${P.violetLight}" />
    <text x="873" y="508" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.violetDark}">深度（长 CoT）</text>
    <text x="873" y="527" text-anchor="middle" font-size="10.5" fill="${P.textSec}">单条路径多步推导</text>
    <text x="873" y="543" text-anchor="middle" font-size="10.5" fill="${P.textSec}">检查并自我修正</text>

    <rect x="960" y="486" width="146" height="66" rx="8" fill="${P.amberPale}" stroke="${P.amberLight}" />
    <text x="1033" y="508" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.amberDark}">宽度（多候选）</text>
    <text x="1033" y="527" text-anchor="middle" font-size="10.5" fill="${P.textSec}">并行生成多份解法</text>
    <text x="1033" y="543" text-anchor="middle" font-size="10.5" fill="${P.textSec}">投票或验证器择优</text>
  `;
  b += scalingCard({
    x: 780, w: 346,
    title: '③ Test-time Scaling（推理时扩展）',
    badge: '投入：单道难题分配更多“思考计算预算”',
    col: P.violet, bg: P.violetPale, dark: P.violetDark,
    xLabel: '单题推理 Token 数 / 采样候选数（对数）',
    yLabel: '难题正确率',
    curveFn: (t) => 0.16 + 0.78 * (1 - Math.exp(-3.4 * t)),
    pts: [[0.16, '直答'], [0.52, 'CoT'], [0.88, '深度反思+验证']],
    desc1: '• 权重不变，让模型在答题前“多想一会儿”',
    desc2: '• 两条路线按延迟和成本预算灵活组合：',
    extra: extraTT,
  });

  return wrapSvg({
    width, height,
    title: '大模型能力扩展的三条 Scaling 路径',
    subtitle: '从“把模型训大”走向“用 RL 训精”再到“答题时多想”，三类扩展路径彼此叠加',
    badge: '§11.1 Scaling Laws',
    body: b,
  });
}

// 22: Multimodal Model Architecture
function fig22() {
  const width = 1160, height = 580;
  let b = '';

  // Three modality input lanes on left
  // Lane 1: Image / Video
  b += box({ x: 34, y: 112, w: 146, h: 108, rx: 12, fill: P.bluePale, stroke: P.blue, sw: 1.5 });
  b += `<text x="107" y="136" text-anchor="middle" font-size="13" font-weight="700" fill="${P.blueDark}">图像 / 视频</text>`;
  // Mini 3x2 patch icon
  for (let r = 0; r < 2; r++) {
    for (let c = 0; c < 3; c++) {
      b += `<rect x="${64 + c * 28}" y="${148 + r * 24}" width="24" height="20" rx="3" fill="${(r + c) % 2 === 0 ? '#60A5FA' : '#34D399'}" stroke="#FFFFFF" />`;
    }
  }
  b += `<text x="107" y="210" text-anchor="middle" font-size="10.5" fill="${P.textSec}">切分为 Patch 序列</text>`;

  b += arrow(182, 166, 220, 166, { color: P.blue, marker: 'arr-blue', sw: 2 });
  b += labelBox({ x: 224, y: 132, w: 144, h: 68, title: '视觉编码器', sub: 'Vision Encoder (ViT)\n提取时空视觉特征', fill: '#FFFFFF', stroke: P.blue, titleColor: P.blueDark, titleSize: 13, subSize: 10.5 });
  b += arrow(370, 166, 404, 166, { color: P.blue, marker: 'arr-blue', sw: 2 });
  b += labelBox({ x: 408, y: 138, w: 118, h: 56, title: 'Projector', sub: '投影对齐到 d 维', fill: P.blueLight, stroke: P.blue, titleColor: P.blueDark, titleSize: 12.5, subSize: 10.5 });

  // Lane 2: Audio
  b += box({ x: 34, y: 242, w: 146, h: 108, rx: 12, fill: P.amberPale, stroke: P.amber, sw: 1.5 });
  b += `<text x="107" y="266" text-anchor="middle" font-size="13" font-weight="700" fill="${P.amberDark}">音频 / 语音</text>`;
  // Mini waveform bars
  [14, 30, 44, 24, 38, 18, 34, 22].forEach((h, i) => {
    b += `<rect x="${56 + i * 13}" y="${302 - h / 2}" width="8" height="${h}" rx="3" fill="${P.amber}" />`;
  });
  b += `<text x="107" y="340" text-anchor="middle" font-size="10.5" fill="${P.textSec}">声谱图 / 音频帧</text>`;

  b += arrow(182, 296, 220, 296, { color: P.amber, marker: 'arr-amber', sw: 2 });
  b += labelBox({ x: 224, y: 262, w: 144, h: 68, title: '音频编码器', sub: 'Audio Encoder\n提取语音与声学特征', fill: '#FFFFFF', stroke: P.amber, titleColor: P.amberDark, titleSize: 13, subSize: 10.5 });
  b += arrow(370, 296, 404, 296, { color: P.amber, marker: 'arr-amber', sw: 2 });
  b += labelBox({ x: 408, y: 268, w: 118, h: 56, title: 'Projector', sub: '投影对齐到 d 维', fill: P.amberLight, stroke: P.amber, titleColor: P.amberDark, titleSize: 12.5, subSize: 10.5 });

  // Lane 3: Text
  b += box({ x: 34, y: 372, w: 146, h: 108, rx: 12, fill: P.tealPale, stroke: P.teal, sw: 1.5 });
  b += `<text x="107" y="396" text-anchor="middle" font-size="13" font-weight="700" fill="${P.tealDark}">文本指令</text>`;
  b += `<text x="107" y="424" text-anchor="middle" font-size="12" font-weight="600" fill="${P.text}">“比较图中两条</text>`;
  b += `<text x="107" y="444" text-anchor="middle" font-size="12" font-weight="600" fill="${P.text}">实验曲线变化”</text>`;
  b += `<text x="107" y="468" text-anchor="middle" font-size="10.5" fill="${P.textSec}">文字 Prompt</text>`;

  b += arrow(182, 426, 220, 426, { color: P.teal, marker: 'arr-teal', sw: 2 });
  b += labelBox({ x: 224, y: 392, w: 302, h: 68, title: 'Tokenizer + Text Embedding 查表', sub: '直接映射到同一 d 维词向量空间', fill: '#FFFFFF', stroke: P.teal, titleColor: P.tealDark, titleSize: 13, subSize: 11 });

  // Unified Token Sequence Connector
  b += pathArrow('M 528 166 L 560 166 L 560 220 L 586 220', { color: P.blue, marker: 'arr-blue', sw: 2 });
  b += arrow(528, 296, 586, 296, { color: P.amber, marker: 'arr-amber', sw: 2 });
  b += pathArrow('M 528 426 L 560 426 L 560 372 L 586 372', { color: P.teal, marker: 'arr-teal', sw: 2 });

  // Unified Sequence column
  b += box({ x: 590, y: 152, w: 94, h: 288, rx: 12, fill: '#FFFFFF', stroke: P.violet, sw: 1.8 });
  b += `<text x="637" y="138" text-anchor="middle" font-size="12" font-weight="700" fill="${P.violetDark}">统一向量序列</text>`;
  // Vision tokens
  [0, 1, 2].forEach((i) => {
    b += `<rect x="604" y="${168 + i * 26}" width="66" height="20" rx="5" fill="${P.blue}" fill-opacity="${0.9 - i * 0.15}" />`;
    b += `<text x="637" y="${182 + i * 26}" text-anchor="middle" font-size="10" font-weight="700" fill="#FFFFFF">Img_${i + 1}</text>`;
  });
  // Audio tokens
  [0, 1, 2].forEach((i) => {
    b += `<rect x="604" y="${258 + i * 26}" width="66" height="20" rx="5" fill="${P.amber}" fill-opacity="${0.9 - i * 0.15}" />`;
    b += `<text x="637" y="${272 + i * 26}" text-anchor="middle" font-size="10" font-weight="700" fill="#FFFFFF">Aud_${i + 1}</text>`;
  });
  // Text tokens
  [0, 1, 2].forEach((i) => {
    b += `<rect x="604" y="${348 + i * 26}" width="66" height="20" rx="5" fill="${P.teal}" fill-opacity="${0.9 - i * 0.15}" />`;
    b += `<text x="637" y="${362 + i * 26}" text-anchor="middle" font-size="10" font-weight="700" fill="#FFFFFF">Txt_${i + 1}</text>`;
  });

  // Big LLM Backbone
  b += arrow(686, 296, 728, 296, { color: P.violet, marker: 'arr-violet', sw: 2.5 });
  b += box({ x: 732, y: 146, w: 204, h: 300, rx: 16, fill: P.violetPale, stroke: P.violet, sw: 2.2 });
  b += `<text x="834" y="190" text-anchor="middle" font-size="16" font-weight="700" fill="${P.violetDark}">LLM Backbone</text>`;
  b += `<text x="834" y="212" text-anchor="middle" font-size="12" font-weight="600" fill="${P.text}">（Transformer Decoder）</text>`;

  // Mini stacked blocks inside backbone
  for (let i = 0; i < 3; i++) {
    b += labelBox({ x: 754, y: 234 + i * 56, w: 160, h: 42, title: `Transformer Block ${i + 1}`, sub: '跨模态自注意力融合', fill: '#FFFFFF', stroke: P.violet, titleColor: P.violetDark, titleSize: 11.5, subSize: 10 });
  }
  b += `<text x="834" y="426" text-anchor="middle" font-size="11" font-weight="600" fill="${P.violetDark}">图文音在同一空间自由交互！</text>`;

  // Output decoders on right
  b += pathArrow('M 938 256 L 976 256 L 976 218 L 998 218', { color: P.emerald, marker: 'arr-emerald', sw: 2.2 });
  b += labelBox({ x: 1002, y: 168, w: 126, h: 100, title: '文本回答', sub: '解释曲线差异、\n分析代码与图表', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 13.5, subSize: 11 });

  b += pathArrow('M 938 336 L 976 336 L 976 370 L 998 370', { color: P.violet, marker: 'arr-violet', sw: 2, dash: '5 3' });
  b += labelBox({ x: 1002, y: 320, w: 126, h: 100, title: '多模态生成', sub: '（可选）接图像 /\n语音生成解码器', fill: '#F8FAFC', stroke: P.violet, titleColor: P.violetDark, titleSize: 13, subSize: 11 });

  // Bottom insight
  b += noteBar({
    x: 34, y: 510, w: 1092, h: 44,
    text: '核心思想：Transformer 对输入来源一视同仁——只要通过各自编码器 + Projector 把图片、视频、音频变成 d 维向量，LLM 就能像读文字一样“读懂世界”（如 Qwen3-VL）。',
  });

  return wrapSvg({
    width, height,
    title: '多模态大模型架构：把文字、图像、音频统一为 Token 序列',
    subtitle: '各模态通过专属编码器与投影层对齐到同一向量空间，再交由共享的 LLM Backbone 联合理解与推理',
    badge: '§11.2 多模态架构',
    body: b,
  });
}

// 23: Mixture of Experts (MoE) Layer
function fig23() {
  const width = 1160, height = 620;
  let b = '';

  // Input token x on left
  b += labelBox({ x: 38, y: 244, w: 124, h: 86, title: '单个 Token 向量 x', sub: '来自 Self-Attention\n（每个 Token 独立路由）', fill: P.bluePale, stroke: P.blue, titleColor: P.blueDark, titleSize: 13, subSize: 10.5 });

  // Router (Gating Network)
  b += arrow(164, 287, 214, 287, { color: P.blue, marker: 'arr-blue', sw: 2.2 });
  b += box({ x: 218, y: 212, w: 162, h: 150, rx: 14, fill: P.amberPale, stroke: P.amber, sw: 2 });
  b += `<text x="299" y="242" text-anchor="middle" font-size="15" font-weight="700" fill="${P.amberDark}">路由器 Router</text>`;
  b += `<text x="299" y="262" text-anchor="middle" font-size="11.5" fill="${P.textSec}">Softmax(x · W_gate)</text>`;
  b += `<line x1="234" y1="276" x2="364" y2="276" stroke="${P.amberLight}" />`;
  b += `<text x="299" y="298" text-anchor="middle" font-size="12" font-weight="700" fill="${P.text}">Top-K 稀疏选择 (K=2)</text>`;
  b += pill({ x: 234, y: 310, w: 130, h: 22, fill: P.bluePale, stroke: P.blue, text: '选中 E₂：权重 0.68', color: P.blueDark, fontSize: 10.5 });
  b += pill({ x: 234, y: 336, w: 130, h: 22, fill: P.tealPale, stroke: P.teal, text: '选中 E₆：权重 0.32', color: P.tealDark, fontSize: 10.5 });

  // 8 Expert FFN boxes arranged cleanly in a vertical stack (right-center)
  const experts = [
    { id: 1, active: false },
    { id: 2, active: true, col: P.blue, bg: P.bluePale, dark: P.blueDark, w: '0.68', role: '激活计算 E₂(x)' },
    { id: 3, active: false },
    { id: 4, active: false },
    { id: 5, active: false },
    { id: 6, active: true, col: P.teal, bg: P.tealPale, dark: P.tealDark, w: '0.32', role: '激活计算 E₆(x)' },
    { id: 7, active: false },
    { id: 8, active: false },
  ];

  // Outer dashed box for Expert Pool
  b += box({ x: 452, y: 102, w: 294, h: 374, rx: 14, fill: '#FFFFFF', stroke: P.border, dash: '6 4', shadow: false });
  b += `<text x="599" y="124" text-anchor="middle" font-size="13" font-weight="700" fill="${P.textSec}">专家子网络池（替代稠密 FFN，共 N=8 个专家）</text>`;

  experts.forEach((ex, i) => {
    const ey = 136 + i * 41;
    const cy = ey + 17;
    if (ex.active) {
      b += box({ x: 472, y: ey, w: 254, h: 34, rx: 8, fill: ex.bg, stroke: ex.col, sw: 2 });
      b += `<text x="492" y="${ey + 22}" font-size="13" font-weight="700" fill="${ex.dark}">Expert E${ex.id}（FFN）</text>`;
      b += `<text x="712" y="${ey + 22}" text-anchor="end" font-size="11.5" font-weight="700" fill="${ex.dark}">${ex.role} ✓</text>`;
      // Active route arrow from Router to Expert
      b += pathArrow(`M 382 287 C 418 287, 418 ${cy}, 468 ${cy}`, { color: ex.col, marker: ex.id === 2 ? 'arr-blue' : 'arr-teal', sw: 2.6 });
      // Active output arrow from Expert to Weighted Sum
      b += pathArrow(`M 728 ${cy} C 790 ${cy}, 796 287, 844 287`, { color: ex.col, marker: ex.id === 2 ? 'arr-blue' : 'arr-teal', sw: 2.6 });
      b += pill({ x: 756, y: cy - 11, w: 54, h: 22, fill: '#FFFFFF', stroke: ex.col, text: `× ${ex.w}`, color: ex.dark, fontSize: 11 });
    } else {
      b += box({ x: 472, y: ey, w: 254, h: 32, rx: 8, fill: '#F8FAFC', stroke: '#E2E8F0', sw: 1, shadow: false });
      b += `<text x="492" y="${ey + 21}" font-size="12" fill="#94A3B8">Expert E${ex.id}（FFN）</text>`;
      b += `<text x="712" y="${ey + 21}" text-anchor="end" font-size="11" fill="#94A3B8">未激活（跳过计算）</text>`;
      b += `<path d="M 382 287 C 416 287, 420 ${cy}, 468 ${cy}" fill="none" stroke="#CBD5E1" stroke-width="1" stroke-dasharray="3 3" />`;
    }
  });

  // Weighted Sum circle + Output
  b += `<circle cx="868" cy="287" r="24" fill="${P.emeraldPale}" stroke="${P.emerald}" stroke-width="2.2" />`;
  b += `<text x="868" y="295" text-anchor="middle" font-size="22" font-weight="700" fill="${P.emerald}">Σ</text>`;
  b += arrow(894, 287, 944, 287, { color: P.emerald, marker: 'arr-emerald', sw: 2.4 });

  b += box({ x: 948, y: 224, w: 178, h: 126, rx: 14, fill: P.emeraldPale, stroke: P.emerald, sw: 2 });
  b += `<text x="1037" y="256" text-anchor="middle" font-size="14.5" font-weight="700" fill="${P.tealDark}">MoE 层输出 y</text>`;
  b += `<text x="1037" y="284" text-anchor="middle" font-size="13" font-weight="700" fill="${P.text}">0.68 E₂(x) + 0.32 E₆(x)</text>`;
  b += `<text x="1037" y="310" text-anchor="middle" font-size="11.5" fill="${P.textSec}">保持 d 维形状不变，</text>`;
  b += `<text x="1037" y="328" text-anchor="middle" font-size="11.5" fill="${P.textSec}">加回残差继续进下一层</text>`;

  // Bottom comparison cards: Total vs Active Params & Engineering considerations
  b += box({ x: 34, y: 496, w: 540, h: 92, rx: 12, fill: '#FFFFFF', stroke: P.blueLight, sw: 1.5 });
  b += pill({ x: 52, y: 508, w: 234, h: 24, fill: P.bluePale, stroke: P.blue, text: '总参数量 vs 激活参数量（解耦容量与算力）', color: P.blueDark, fontSize: 11.5 });
  b += `<text x="52" y="552" font-size="12.5" font-weight="700" fill="${P.text}">例：DeepSeek-V4-Pro 总参数 ≈ 1.6T，但每 Token 仅激活 ≈ 49B！</text>`;
  b += `<text x="52" y="574" font-size="12" fill="${P.textSec}">像一家大型综合医院：拥有庞大专家团队（容量大），但每位病人只挂 2 个号（算得快）。</text>`;

  b += box({ x: 594, y: 496, w: 532, h: 92, rx: 12, fill: '#FFFFFF', stroke: P.amberLight, sw: 1.5 });
  b += pill({ x: 612, y: 508, w: 204, h: 24, fill: P.amberPale, stroke: P.amber, text: '稀疏 MoE 的现实工程代价', color: P.amberDark, fontSize: 11.5 });
  b += `<text x="612" y="552" font-size="12.5" fill="${P.text}">• 显存仍需装下全部总参数（所有专家权重常驻显存）</text>`;
  b += `<text x="612" y="574" font-size="12.5" fill="${P.textSec}">• 需要解决专家负载均衡（避免“旱的旱死、涝的涝死”）与跨卡通信开销</text>`;

  return wrapSvg({
    width, height,
    title: '稀疏专家模型（Mixture of Experts, MoE）层：按需路由与加权汇总',
    subtitle: '用多个专家子网络替换稠密 FFN，路由器为每个 Token 仅激活少数专家，大幅提升容量同时控制单步算力',
    badge: '§11.3 MoE 架构',
    body: b,
  });
}

// 32: Context Window Budget
function fig32() {
  const width = 1140, height = 590;
  let b = '';

  // Top Scenario 1: Healthy Request Budget inside Context Window
  b += box({ x: 34, y: 100, w: 1072, h: 178, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += `<text x="56" y="128" font-size="15" font-weight="700" fill="${P.text}">一次请求的上下文预算分配（总容量固定，例如 Context Window = 128K Tokens）</text>`;

  // Main segmented horizontal bar
  const bx = 56, by = 148, bw = 1028, bh = 58;
  const segs = [
    { lbl: '系统提示 & 工具定义', sub: 'System Prompt', pct: 0.13, col: P.slate, bg: '#E2E8F0', tc: P.text },
    { lbl: 'RAG 检索片段 / 文档资料', sub: 'Retrieved Docs', pct: 0.34, col: P.blue, bg: P.blueLight, tc: P.blueDark },
    { lbl: '多轮对话历史', sub: 'Chat History', pct: 0.25, col: P.teal, bg: P.tealLight, tc: P.tealDark },
    { lbl: '当前问题', sub: 'Query', pct: 0.08, col: P.amber, bg: P.amberLight, tc: P.amberDark },
    { lbl: '生成预留（含 CoT 思考）', sub: 'Output Reserve', pct: 0.20, col: P.violet, bg: P.violetLight, tc: P.violetDark },
  ];
  let curX = bx;
  segs.forEach((sg, idx) => {
    const sw = Math.round(sg.pct * bw);
    const actualW = idx === segs.length - 1 ? bx + bw - curX : sw - 3;
    b += `<rect x="${curX}" y="${by}" width="${actualW}" height="${bh}" rx="8" fill="${sg.bg}" stroke="${sg.col}" stroke-width="1.8" />`;
    b += `<text x="${curX + actualW / 2}" y="${by + 25}" text-anchor="middle" font-size="${actualW < 100 ? 11.5 : 12.5}" font-weight="700" fill="${sg.tc}">${sg.lbl}</text>`;
    b += `<text x="${curX + actualW / 2}" y="${by + 45}" text-anchor="middle" font-size="10.5" fill="${P.textSec}">${sg.sub} (${Math.round(sg.pct * 100)}%)</text>`;
    curX += sw;
  });

  // Total capacity bracket underneath
  b += `<line x1="${bx}" y1="226" x2="${bx + bw}" y2="226" stroke="${P.slate}" stroke-width="1.6" />`;
  b += `<line x1="${bx}" y1="220" x2="${bx}" y2="232" stroke="${P.slate}" stroke-width="1.6" />`;
  b += `<line x1="${bx + bw}" y1="220" x2="${bx + bw}" y2="232" stroke="${P.slate}" stroke-width="1.6" />`;
  b += pill({ x: 432, y: 214, w: 276, h: 24, fill: '#F1F5F9', stroke: P.slate, text: '总长度 ≤ 上下文窗口上限（固定天花板）', color: P.text, fontSize: 11.5 });
  b += `<text x="56" y="262" font-size="12" fill="${P.textSec}">⚠️ 提示：输入和输出共享同一个窗口——资料放得越满，留给模型思考（CoT）和生成回答的空间就被挤占得越小！</text>`;

  // Bottom Scenario 2: Overflow & 3 Mitigation Strategies
  b += box({ x: 34, y: 296, w: 1072, h: 262, rx: 14, fill: '#FFFFFF', stroke: P.roseLight, sw: 1.6 });
  b += pill({ x: 56, y: 312, w: 266, h: 26, fill: P.roseLight, stroke: P.rose, text: '当多轮历史 + 长文档超出窗口上限怎么办？', color: P.roseDark, fontSize: 12 });

  // Overflow bar schematic
  b += `<rect x="56" y="352" width="760" height="32" rx="7" fill="${P.bluePale}" stroke="${P.blue}" stroke-width="1.4" />`;
  b += `<text x="436" y="373" text-anchor="middle" font-size="12" font-weight="600" fill="${P.blueDark}">窗口内可容纳部分（System + 历史 + 文档 + 问题 + 输出）</text>`;
  b += `<rect x="820" y="352" width="264" height="32" rx="7" fill="${P.roseLight}" stroke="${P.rose}" stroke-width="1.8" stroke-dasharray="5 3" />`;
  b += `<text x="952" y="373" text-anchor="middle" font-size="12" font-weight="700" fill="${P.roseDark}">💥 溢出超出上限！无法直接送入</text>`;
  b += `<line x1="818" y1="344" x2="818" y2="394" stroke="${P.rose}" stroke-width="2.5" />`;

  // 3 Mitigation Cards
  const strats = [
    {
      x: 56, col: P.amber, bg: P.amberPale, dark: P.amberDark,
      t: '对策 1 · 截断（Truncation）',
      d1: '丢弃最早的对话历史或文档末尾，',
      d2: '实现最简单，但可能丢失早期关键约束。',
      fit: '适用：短平快对话、对延迟要求极高的场景',
    },
    {
      x: 406, col: P.teal, bg: P.tealPale, dark: P.tealDark,
      t: '对策 2 · 摘要压缩（Summarization）',
      d1: '把旧对话提炼成精简摘要保留要点，',
      d2: '大幅释放空间，但会损失部分原文细节。',
      fit: '适用：超长多轮会话、长期记忆与个人助理',
    },
    {
      x: 756, col: P.blue, bg: P.bluePale, dark: P.blueDark,
      t: '对策 3 · 按需检索（RAG / Tool Search）',
      d1: '不把整个文档库塞进窗口，只临时检索',
      d2: '当前问题最相关的片段，兼顾成本与精度！',
      fit: '适用：海量资料库、频繁更新的技术规范与代码',
    },
  ];
  strats.forEach((s) => {
    b += box({ x: s.x, y: 410, w: 328, h: 126, rx: 12, fill: s.bg, stroke: s.col, sw: 1.5, shadow: false });
    b += `<text x="${s.x + 16}" y="440" font-size="14" font-weight="700" fill="${s.dark}">${s.t}</text>`;
    b += `<text x="${s.x + 16}" y="472" font-size="12.5" fill="${P.text}">${s.d1}</text>`;
    b += `<text x="${s.x + 16}" y="494" font-size="12.5" fill="${P.textSec}">${s.d2}</text>`;
    b += `<text x="${s.x + 16}" y="520" font-size="11.5" font-weight="600" fill="${s.dark}">${s.fit}</text>`;
  });

  return wrapSvg({
    width, height,
    title: '一次请求里的上下文窗口预算（Context Window Budget）',
    subtitle: '系统提示、检索材料、历史对话、当前问题与生成预留共享同一块有限空间，超出时必须做上下文管理',
    badge: '§11.4 上下文预算',
    body: b,
  });
}

// 30: RAG Pipeline (Offline Indexing + Online Query)
function fig30() {
  const width = 1160, height = 610;
  let b = '';

  // Top Lane: Offline Indexing
  b += box({ x: 34, y: 100, w: 1092, h: 196, rx: 14, fill: P.bluePale, stroke: P.blueLight, sw: 1.6, shadow: false });
  b += pill({ x: 54, y: 114, w: 286, h: 26, fill: P.blue, stroke: P.blueDark, text: '离线建索引路径（Offline · 定期更新资料库）', color: '#FFFFFF', fontSize: 12 });
  b += `<text x="1104" y="132" text-anchor="end" font-size="12" font-weight="600" fill="${P.blueDark}">知识更新只需重跑索引，完全无需重新训练或微调 LLM！</text>`;

  b += labelBox({ x: 56, y: 162, w: 178, h: 104, title: '私有文档库', sub: '技术规范 PDF、实验报告\n内部 Wiki、最新标准', fill: '#FFFFFF', stroke: P.blue, titleColor: P.blueDark, titleSize: 14, subSize: 11 });
  b += arrow(236, 214, 286, 214, { color: P.blue, marker: 'arr-blue', sw: 2.2 });

  b += labelBox({ x: 290, y: 162, w: 186, h: 104, title: '文本切块 Chunking', sub: '拆分为合适长度的片段\n（附带文档出处与页码）', fill: '#FFFFFF', stroke: P.blue, titleColor: P.blueDark, titleSize: 13.5, subSize: 11 });
  b += arrow(478, 214, 528, 214, { color: P.blue, marker: 'arr-blue', sw: 2.2 });

  b += labelBox({ x: 532, y: 162, w: 188, h: 104, title: 'Embedding 编码模型', sub: '把每个片段转成语义向量\n（同时可建关键词倒排索引）', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 13.5, subSize: 11 });
  b += arrow(722, 214, 782, 214, { color: P.violet, marker: 'arr-violet', sw: 2.2 });

  // Vector DB / Index Storage cylinder-styled box
  b += box({ x: 786, y: 154, w: 316, h: 120, rx: 14, fill: '#FFFFFF', stroke: P.violet, sw: 2.2 });
  b += `<text x="944" y="182" text-anchor="middle" font-size="15" font-weight="700" fill="${P.violetDark}">向量数据库 / 检索索引</text>`;
  b += `<text x="944" y="202" text-anchor="middle" font-size="11.5" fill="${P.textSec}">Vector DB + 关键词索引（解耦存储）</text>`;
  // Mini index rows
  ['片段 #102 · [0.81, 0.24, ...]', '片段 #205 · [0.19, 0.92, ...]', '片段 #318 · [0.64, 0.55, ...]'].forEach((t, i) => {
    b += `<rect x="810" y="${212 + i * 18}" width="268" height="15" rx="4" fill="${i === 1 ? P.amberLight : '#F1F5F9'}" />`;
    b += `<text x="820" y="${223 + i * 18}" font-size="10" class="mono" font-weight="${i === 1 ? 700 : 400}" fill="${i === 1 ? P.amberDark : P.textSec}">${t}</text>`;
  });

  // Bottom Lane: Online Retrieval & Generation
  b += box({ x: 34, y: 318, w: 1092, h: 204, rx: 14, fill: P.tealPale, stroke: P.tealLight, sw: 1.6, shadow: false });
  b += pill({ x: 54, y: 332, w: 286, h: 26, fill: P.teal, stroke: P.tealDark, text: '在线检索与生成路径（Online · 实时响应）', color: '#FFFFFF', fontSize: 12 });

  b += labelBox({ x: 56, y: 382, w: 162, h: 110, title: '用户提问', sub: '“这份规范对某指标\n的要求是什么？”', fill: '#FFFFFF', stroke: P.teal, titleColor: P.tealDark, titleSize: 14, subSize: 11 });
  b += arrow(220, 437, 260, 437, { color: P.teal, marker: 'arr-teal', sw: 2.2 });

  b += labelBox({ x: 264, y: 382, w: 176, h: 110, title: '问题检索 Retriever', sub: '计算问题向量 / 关键词\n按语义相似度查 Top-K', fill: '#FFFFFF', stroke: P.violet, titleColor: P.violetDark, titleSize: 13.5, subSize: 11 });

  // Vertical bidirectional bridge between Retriever and Vector DB!
  b += pathArrow('M 352 380 L 352 308 L 882 308 L 882 278', { color: P.violet, marker: 'arr-violet', sw: 2.2 });
  b += `<text x="618" y="302" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.violetDark}">① 实时相似度查询</text>`;

  b += pathArrow('M 944 276 L 944 352 L 584 352 L 584 378', { color: P.amberDark, marker: 'arr-amber', sw: 2.4 });
  b += `<text x="766" y="346" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.amberDark}">② 返回最相关的 Top-K 原始片段</text>`;

  // Prompt Assembly box
  b += arrow(442, 437, 480, 437, { color: P.teal, marker: 'arr-teal', sw: 2 });
  b += box({ x: 484, y: 380, w: 204, h: 114, rx: 12, fill: P.amberPale, stroke: P.amber, sw: 1.8 });
  b += `<text x="586" y="405" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.amberDark}">③ 拼装增强上下文</text>`;
  b += `<rect x="498" y="416" width="176" height="28" rx="6" fill="#FFFFFF" stroke="${P.amberLight}" />`;
  b += `<text x="586" y="434" text-anchor="middle" font-size="11" font-weight="600" fill="${P.text}">[参考条款 #205, #412]</text>`;
  b += `<rect x="498" y="450" width="176" height="28" rx="6" fill="#FFFFFF" stroke="${P.tealLight}" />`;
  b += `<text x="586" y="468" text-anchor="middle" font-size="11" font-weight="600" fill="${P.tealDark}">+ 用户原始问题</text>`;

  // LLM -> Grounded Answer
  b += arrow(690, 437, 730, 437, { color: P.amberDark, marker: 'arr-amber', sw: 2.2 });
  b += labelBox({ x: 734, y: 384, w: 144, h: 106, title: 'LLM 生成', sub: '结合给定资料\n总结并引用条款', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 14, subSize: 11 });
  b += arrow(880, 437, 920, 437, { color: P.emerald, marker: 'arr-emerald', sw: 2.2 });
  b += labelBox({ x: 924, y: 382, w: 180, h: 110, title: '④ 带出处的可靠回答', sub: '大幅减少事实幻觉\n可回溯核对原文条款', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 13.5, subSize: 11 });

  // Bottom insight comparing Classic RAG vs Agentic Search
  b += noteBar({
    x: 34, y: 540, w: 1092, h: 42,
    text: '进阶演进（Agentic RAG）：面对复杂多跳问题，也可以把检索工具直接交给模型自主决策——由模型多轮调整查询词、交叉验证后再作答！',
  });

  return wrapSvg({
    width, height,
    title: '检索增强生成（RAG）：离线建索引与在线检索拼装流程',
    subtitle: '把“外部知识存储与检索”和“大模型语言推理”解耦，让回答用上最新私有资料并可追溯出处',
    badge: '§11.4 RAG 流程',
    body: b,
  });
}

// 26: Agent Iterative Cycle (Perceive - Reason - Plan - Act - Observe)
function fig26() {
  const width = 1140, height = 650;
  let b = '';

  // Left entrance: User Goal
  b += box({ x: 34, y: 244, w: 196, h: 158, rx: 14, fill: P.bluePale, stroke: P.blue, sw: 1.8 });
  b += pill({ x: 54, y: 258, w: 156, h: 24, fill: P.blue, stroke: P.blueDark, text: '用户给出高层目标', color: '#FFFFFF', fontSize: 11.5 });
  b += `<text x="132" y="310" text-anchor="middle" font-size="13" font-weight="700" fill="${P.text}">“读取实验 CSV 数据，</text>`;
  b += `<text x="132" y="332" text-anchor="middle" font-size="13" font-weight="700" fill="${P.text}">运行统计分析并检查异常，</text>`;
  b += `<text x="132" y="354" text-anchor="middle" font-size="13" font-weight="700" fill="${P.text}">最终整理成一份报告。”</text>`;
  b += `<text x="132" y="384" text-anchor="middle" font-size="11" fill="${P.textSec}">不再只是一问一答</text>`;

  b += arrow(232, 323, 292, 323, { color: P.blue, marker: 'arr-blue', sw: 2.5 });

  // Center Hub: LLM Brain + Context Memory
  const cx = 574, cy = 356;
  // Subtle circular orbit guide
  b += `<circle cx="${cx}" cy="${cy}" r="186" fill="none" stroke="${P.border}" stroke-width="2" stroke-dasharray="6 6" />`;

  // Center LLM Brain Card
  b += `<circle cx="${cx}" cy="${cy}" r="88" fill="${P.violetPale}" stroke="${P.violet}" stroke-width="2.6" filter="url(#shadow-md)" />`;
  b += `<text x="${cx}" y="${cy - 20}" text-anchor="middle" font-size="16" font-weight="700" fill="${P.violetDark}">大模型核心</text>`;
  b += `<text x="${cx}" y="${cy + 2}" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.text}">LLM Brain</text>`;
  b += `<text x="${cx}" y="${cy + 26}" text-anchor="middle" font-size="11.5" fill="${P.textSec}">+ 上下文记忆</text>`;
  b += `<text x="${cx}" y="${cy + 44}" text-anchor="middle" font-size="11" fill="${P.violetDark}">（维护中间状态）</text>`;

  // 5 cycle nodes around the circle (clockwise starting from top-left!)
  // Angles in degrees: Perceive (-144° -> top-left), Reason (-90° -> top), Plan (-36° -> top-right), Act (36° -> bottom-right), Observe (144° -> bottom-left)
  const nodes = [
    { x: 296, y: 274, w: 158, h: 74, num: '①', title: '感知 Perceive', sub: '读取目标、上下文\n与当前环境状态', col: P.blue, bg: P.bluePale, dark: P.blueDark },
    { x: 495, y: 112, w: 158, h: 74, num: '②', title: '推理 Reason', sub: '分析问题结构，\n判断缺少什么信息', col: P.violet, bg: P.violetPale, dark: P.violetDark },
    { x: 694, y: 274, w: 158, h: 74, num: '③', title: '规划 Plan', sub: '拆解子步骤，\n决定调用哪个工具', col: P.amber, bg: P.amberPale, dark: P.amberDark },
    { x: 646, y: 468, w: 174, h: 78, num: '④', title: '执行 Act', sub: '调用外部工具执行\n真实操作并改变环境', col: P.teal, bg: P.tealPale, dark: P.tealDark },
    { x: 326, y: 468, w: 174, h: 78, num: '⑤', title: '观察 Observe', sub: '收集返回结果或报错，\n写回上下文继续迭代', col: P.rose, bg: P.rosePale, dark: P.roseDark },
  ];

  // Curved clockwise arrows connecting 1->2->3->4->5->1
  b += pathArrow('M 378 272 C 392 198, 434 156, 491 148', { color: P.blue, marker: 'arr-blue', sw: 2.6 });
  b += pathArrow('M 656 148 C 714 156, 754 198, 768 270', { color: P.violet, marker: 'arr-violet', sw: 2.6 });
  b += pathArrow('M 776 350 C 786 402, 774 438, 752 464', { color: P.amber, marker: 'arr-amber', sw: 2.6 });
  b += pathArrow('M 644 510 C 594 522, 550 522, 504 510', { color: P.teal, marker: 'arr-teal', sw: 2.6 });
  b += pathArrow('M 396 464 C 374 436, 362 398, 370 352', { color: P.rose, marker: 'arr-rose', sw: 2.6 });

  nodes.forEach((nd) => {
    b += labelBox({ x: nd.x, y: nd.y, w: nd.w, h: nd.h, title: `${nd.num} ${nd.title}`, sub: nd.sub, fill: nd.bg, stroke: nd.col, titleColor: nd.dark, titleSize: 13.5, subSize: 11, sw: 2 });
  });

  // Right Side Top: Final Output when Goal Done
  b += pathArrow('M 854 310 L 892 310 L 892 214 L 932 214', { color: P.emerald, marker: 'arr-emerald', sw: 2.4 });
  b += pill({ x: 846, y: 180, w: 82, h: 24, fill: P.emeraldPale, stroke: P.emerald, text: '目标完成 ✓', color: P.tealDark, fontSize: 10.5 });

  b += box({ x: 936, y: 134, w: 170, h: 158, rx: 14, fill: P.emeraldPale, stroke: P.emerald, sw: 2 });
  b += `<text x="1021" y="166" text-anchor="middle" font-size="14.5" font-weight="700" fill="${P.tealDark}">交付最终成果</text>`;
  b += `<text x="1021" y="196" text-anchor="middle" font-size="12" fill="${P.text}">• 清洗后的数据</text>`;
  b += `<text x="1021" y="220" text-anchor="middle" font-size="12" fill="${P.text}">• 统计图表与验证</text>`;
  b += `<text x="1021" y="244" text-anchor="middle" font-size="12" fill="${P.text}">• 结构化分析报告</text>`;
  b += `<text x="1021" y="274" text-anchor="middle" font-size="11" font-weight="600" fill="${P.tealDark}">从“回答问题”到“完成任务”</text>`;

  // Right Side Bottom: External Tools & Execution Environment connected to Act & Observe
  b += box({ x: 912, y: 368, w: 194, h: 192, rx: 14, fill: '#FFFFFF', stroke: P.teal, sw: 1.8 });
  b += pill({ x: 930, y: 382, w: 158, h: 24, fill: P.teal, stroke: P.tealDark, text: '工具与执行环境 Tools', color: '#FFFFFF', fontSize: 11.5 });
  const tools = [
    '📂 文件读写与代码编辑',
    '🐍 Python / 终端运行',
    '🔍 文档搜索 / 数据库',
    '🌐 外部 API 与仿真器',
  ];
  tools.forEach((t, i) => {
    b += `<rect x="926" y="${418 + i * 33}" width="166" height="26" rx="6" fill="#F8FAFC" stroke="${P.borderLight}" />`;
    b += `<text x="936" y="${435 + i * 33}" font-size="11.5" fill="${P.text}">${t}</text>`;
  });

  // Bidirectional arrows between Act (④) and Tools
  b += arrow(822, 496, 908, 496, { color: P.teal, marker: 'arr-teal', sw: 2.2 });
  b += `<text x="865" y="488" text-anchor="middle" font-size="10.5" font-weight="700" fill="${P.tealDark}">工具调用</text>`;
  b += arrow(908, 524, 822, 524, { color: P.rose, marker: 'arr-rose', sw: 2.2 });
  b += `<text x="865" y="542" text-anchor="middle" font-size="10.5" font-weight="700" fill="${P.roseDark}">返回输出/报错</text>`;

  // Bottom summary note
  b += noteBar({
    x: 34, y: 586, w: 1072, h: 40,
    text: 'Agentic Scaling：当大模型接上工具与反馈闭环，遇到报错会自动调试重试，把语言理解转化为可验证的现实行动！',
  });

  return wrapSvg({
    width, height,
    title: '智能体（Agent）工作闭环：感知—推理—规划—执行—观察',
    subtitle: '以大模型为推理中枢，围绕目标自主调用外部工具并利用反馈持续迭代，直至完成复杂任务',
    badge: '§11.5 Agent 循环',
    body: b,
  });
}

export const figures = [
  { filename: '31_top-k-and-top-p.png', width: 1160, height: 620, render: fig31 },
  { filename: '20_training-to-usage-workflow.png', width: 1160, height: 580, render: fig20 },
  { filename: '21_three-scaling-laws.png', width: 1160, height: 610, render: fig21 },
  { filename: '22_multimodal-model-architecture.png', width: 1160, height: 580, render: fig22 },
  { filename: '23_mixture-of-experts-layer.png', width: 1160, height: 620, render: fig23 },
  { filename: '32_context-window-budget.png', width: 1140, height: 590, render: fig32 },
  { filename: '30_rag-pipeline.png', width: 1160, height: 610, render: fig30 },
  { filename: '26_agent-iterative-cycle.png', width: 1140, height: 650, render: fig26 },
];
