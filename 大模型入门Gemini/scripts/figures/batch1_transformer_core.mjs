import { PALETTE as P, wrapSvg, box, labelBox, pill, arrow, pathArrow, vecBars, noteBar, esc } from '../lib/svg.mjs';

// 28: seq2seq bottleneck
function fig28() {
  const width = 1140, height = 560;
  const encTokens = ['I', 'love', 'machine', 'learning'];
  const decTokens = ['我', '喜欢', '机器', '学习'];
  let b = '';

  // Left region: Encoder
  b += box({ x: 36, y: 108, w: 416, h: 292, rx: 14, fill: P.bluePale, stroke: P.blueLight, sw: 1.5, shadow: false });
  b += `<text x="56" y="136" font-size="15" font-weight="700" fill="${P.blueDark}">编码器（Encoder · RNN / LSTM）</text>`;
  b += `<text x="56" y="156" font-size="12" fill="${P.textSec}">必须按时间步 t=1→2→3→4 串行读入，无法并行</text>`;

  encTokens.forEach((tok, i) => {
    const cx = 92 + i * 96;
    // RNN cell
    b += labelBox({ x: cx - 32, y: 204, w: 64, h: 52, title: `h${i + 1}`, sub: 'RNN', fill: '#FFFFFF', stroke: P.blue, titleColor: P.blueDark, titleSize: 15, subSize: 11 });
    // Input token pill
    b += pill({ x: cx - 36, y: 320, w: 72, h: 30, fill: '#FFFFFF', stroke: P.blue, text: tok, color: P.text, fontSize: 12.5 });
    b += arrow(cx, 318, cx, 260, { color: P.blue, marker: 'arr-blue', sw: 1.8 });
    if (i < encTokens.length - 1) {
      b += arrow(cx + 34, 230, cx + 62, 230, { color: P.blue, marker: 'arr-blue', sw: 2 });
    }
    b += `<text x="${cx}" y="374" text-anchor="middle" font-size="11.5" fill="${P.textMuted}">t = ${i + 1}</text>`;
  });

  // Funnel / Bottleneck in the middle
  b += `<path d="M 452 178 L 520 206 L 520 256 L 452 284 Z" fill="${P.roseLight}" fill-opacity="0.55" stroke="${P.rose}" stroke-width="1.3" stroke-dasharray="4 3" />`;
  b += `<path d="M 622 206 L 690 178 L 690 284 L 622 256 Z" fill="${P.amberLight}" fill-opacity="0.55" stroke="${P.amber}" stroke-width="1.3" stroke-dasharray="4 3" />`;
  b += arrow(414, 230, 514, 230, { color: P.rose, marker: 'arr-rose', sw: 2.4 });

  // Bottleneck vector card
  b += box({ x: 520, y: 170, w: 102, h: 122, rx: 12, fill: P.rosePale, stroke: P.rose, sw: 2.2 });
  b += `<text x="571" y="194" text-anchor="middle" font-size="13" font-weight="700" fill="${P.roseDark}">固定维数向量</text>`;
  b += `<text x="571" y="212" text-anchor="middle" font-size="12" font-weight="600" fill="${P.rose}">Context c</text>`;
  b += vecBars({ x: 541, y: 224, vals: [0.9, 0.5, 0.8, 0.35], cellW: 13, cellH: 34, color: P.rose });
  b += `<text x="571" y="279" text-anchor="middle" font-size="11" font-weight="700" fill="${P.roseDark}">信息瓶颈！</text>`;

  b += pill({ x: 492, y: 312, w: 158, h: 28, fill: P.roseLight, stroke: P.rose, text: '整句信息被强行压进这里', color: P.roseDark, fontSize: 11.5 });
  b += arrow(571, 310, 571, 295, { color: P.rose, marker: 'arr-rose', sw: 1.6 });

  // Right region: Decoder
  b += box({ x: 690, y: 108, w: 414, h: 292, rx: 14, fill: P.tealPale, stroke: P.tealLight, sw: 1.5, shadow: false });
  b += `<text x="710" y="136" font-size="15" font-weight="700" fill="${P.tealDark}">解码器（Decoder · RNN / LSTM）</text>`;
  b += `<text x="710" y="156" font-size="12" fill="${P.textSec}">仅凭向量 c 与已生成词，逐步吐出译文</text>`;

  decTokens.forEach((tok, i) => {
    const cx = 758 + i * 94;
    b += labelBox({ x: cx - 30, y: 204, w: 60, h: 52, title: `s${i + 1}`, sub: 'RNN', fill: '#FFFFFF', stroke: P.teal, titleColor: P.tealDark, titleSize: 15, subSize: 11 });
    // Output above
    b += pill({ x: cx - 28, y: 318, w: 56, h: 30, fill: P.tealLight, stroke: P.teal, text: tok, color: P.tealDark, fontSize: 13 });
    b += arrow(cx, 258, cx, 314, { color: P.teal, marker: 'arr-teal', sw: 1.8 });
    if (i < decTokens.length - 1) {
      b += arrow(cx + 32, 230, cx + 62, 230, { color: P.teal, marker: 'arr-teal', sw: 2 });
    }
    b += `<text x="${cx}" y="374" text-anchor="middle" font-size="11.5" fill="${P.textMuted}">step ${i + 1}</text>`;
  });

  // Draw context -> s1 arrow on top so arrowhead is crisp
  b += arrow(624, 230, 725, 230, { color: P.teal, marker: 'arr-teal', sw: 2.4 });

  // Two problem cards at bottom
  b += box({ x: 36, y: 422, w: 524, h: 102, rx: 12, fill: '#FFFFFF', stroke: P.roseLight, sw: 1.6 });
  b += pill({ x: 52, y: 436, w: 128, h: 24, fill: P.roseLight, stroke: P.rose, text: '痛点 1 · 信息瓶颈', color: P.roseDark, fontSize: 11.5 });
  b += `<text x="52" y="482" font-size="13.5" font-weight="600" fill="${P.text}">无论原句 4 个词还是 400 个词，都被压进同样大小的向量 c</text>`;
  b += `<text x="52" y="505" font-size="12.5" fill="${P.textSec}">句子变长时，早期细节（如主语、修饰语）容易被覆盖丢失，翻译质量骤降。</text>`;

  b += box({ x: 580, y: 422, w: 524, h: 102, rx: 12, fill: '#FFFFFF', stroke: P.amberLight, sw: 1.6 });
  b += pill({ x: 596, y: 436, w: 128, h: 24, fill: P.amberLight, stroke: P.amber, text: '痛点 2 · 无法并行', color: P.amberDark, fontSize: 11.5 });
  b += `<text x="596" y="482" font-size="13.5" font-weight="600" fill="${P.text}">hₜ 必须等 hₜ₋₁ 算完才能算，训练时难以充分利用 GPU 并行算力</text>`;
  b += `<text x="596" y="505" font-size="12.5" fill="${P.textSec}">这直接催生了「注意力机制」与完全抛弃循环结构的 Transformer。</text>`;

  return wrapSvg({
    width, height,
    title: '早期的 Seq2Seq 架构：为什么需要注意力机制？',
    subtitle: '以机器翻译 “I love machine learning” → “我喜欢机器学习” 为例',
    badge: '§7 序列建模演进',
    body: b,
  });
}

// 01: Original Transformer Architecture
function fig01() {
  const width = 1140, height = 740;
  let b = '';

  // Encoder Outer Box (N×)
  b += box({ x: 86, y: 186, w: 388, h: 344, rx: 16, fill: P.bluePale, stroke: P.blue, sw: 1.8, dash: '6 4', shadow: false });
  b += pill({ x: 102, y: 173, w: 172, h: 26, fill: P.blue, stroke: P.blueDark, text: 'Encoder 编码器 × N 层', color: '#FFFFFF', fontSize: 12.5 });

  // Encoder sub-blocks (bottom-up flow)
  // Self-Attention
  b += labelBox({ x: 150, y: 416, w: 260, h: 52, title: 'Multi-Head Self-Attention', sub: '源序列内部双向交互', fill: '#FFFFFF', stroke: P.blue, titleColor: P.blueDark, titleSize: 13.5 });
  b += labelBox({ x: 150, y: 348, w: 260, h: 38, title: 'Add & Norm（残差连接 + 归一化）', fill: P.amberPale, stroke: P.amber, titleColor: P.amberDark, titleSize: 12.5 });
  // FFN
  b += labelBox({ x: 150, y: 274, w: 260, h: 46, title: 'Feed-Forward Network (FFN)', sub: '逐位置非线性变换', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 13.5 });
  b += labelBox({ x: 150, y: 210, w: 260, h: 38, title: 'Add & Norm（残差连接 + 归一化）', fill: P.amberPale, stroke: P.amber, titleColor: P.amberDark, titleSize: 12.5 });

  // Encoder vertical arrows
  b += arrow(280, 416, 280, 389, { color: P.blue, marker: 'arr-blue' });
  b += arrow(280, 348, 280, 323, { color: P.blue, marker: 'arr-blue' });
  b += arrow(280, 274, 280, 251, { color: P.violet, marker: 'arr-violet' });

  // Encoder residual arcs (left side)
  b += pathArrow('M 280 494 L 122 494 L 122 367 L 147 367', { color: P.amber, marker: 'arr-amber', sw: 1.8 });
  b += pathArrow('M 280 336 L 122 336 L 122 229 L 147 229', { color: P.amber, marker: 'arr-amber', sw: 1.8 });

  // Encoder Inputs bottom
  b += `<circle cx="280" cy="566" r="15" fill="#FFFFFF" stroke="${P.blue}" stroke-width="2" />`;
  b += `<text x="280" y="572" text-anchor="middle" font-size="18" font-weight="700" fill="${P.blueDark}">+</text>`;
  b += arrow(280, 551, 280, 471, { color: P.blue, marker: 'arr-blue', sw: 2 });
  // PE badge left of +
  b += labelBox({ x: 46, y: 544, w: 168, h: 44, title: 'Positional Encoding', sub: '注入位置顺序信息', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 12.5, subSize: 10.5 });
  b += arrow(216, 566, 262, 566, { color: P.violet, marker: 'arr-violet', sw: 1.8 });

  b += labelBox({ x: 164, y: 604, w: 232, h: 42, title: 'Input Embedding', sub: '词向量查表', fill: P.blueLight, stroke: P.blue, titleColor: P.blueDark, titleSize: 13 });
  b += arrow(280, 604, 280, 583, { color: P.blue, marker: 'arr-blue', sw: 2 });
  b += pill({ x: 120, y: 666, w: 320, h: 32, fill: '#FFFFFF', stroke: P.border, text: '输入原文：I  love  machine  learning', color: P.text, fontSize: 13 });
  b += arrow(280, 665, 280, 649, { color: P.slate, marker: 'arr-slate', sw: 1.8 });

  // Decoder Outer Box (N×)
  b += box({ x: 616, y: 186, w: 438, h: 400, rx: 16, fill: P.tealPale, stroke: P.teal, sw: 1.8, dash: '6 4', shadow: false });
  b += pill({ x: 634, y: 173, w: 178, h: 26, fill: P.teal, stroke: P.tealDark, text: 'Decoder 解码器 × N 层', color: '#FFFFFF', fontSize: 12.5 });

  // Decoder sub-blocks (bottom-up)
  b += labelBox({ x: 682, y: 512, w: 288, h: 48, title: 'Masked Multi-Head Self-Attention', sub: '因果掩码：只能看已生成的前文', fill: '#FFFFFF', stroke: P.rose, titleColor: P.roseDark, titleSize: 13 });
  b += labelBox({ x: 682, y: 454, w: 288, h: 36, title: 'Add & Norm', fill: P.amberPale, stroke: P.amber, titleColor: P.amberDark, titleSize: 12.5 });

  b += labelBox({ x: 682, y: 382, w: 288, h: 48, title: 'Multi-Head Cross-Attention', sub: '用解码器 Q 去读编码器的 K、V', fill: P.tealLight, stroke: P.teal, titleColor: P.tealDark, titleSize: 13 });
  b += labelBox({ x: 682, y: 324, w: 288, h: 36, title: 'Add & Norm', fill: P.amberPale, stroke: P.amber, titleColor: P.amberDark, titleSize: 12.5 });

  b += labelBox({ x: 682, y: 258, w: 288, h: 44, title: 'Feed-Forward Network (FFN)', sub: '逐位置非线性变换', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 13 });
  b += labelBox({ x: 682, y: 204, w: 288, h: 36, title: 'Add & Norm', fill: P.amberPale, stroke: P.amber, titleColor: P.amberDark, titleSize: 12.5 });

  // Decoder vertical arrows
  b += arrow(826, 512, 826, 493, { color: P.rose, marker: 'arr-rose' });
  b += arrow(826, 454, 826, 433, { color: P.teal, marker: 'arr-teal' });
  b += arrow(826, 382, 826, 363, { color: P.teal, marker: 'arr-teal' });
  b += arrow(826, 324, 826, 305, { color: P.violet, marker: 'arr-violet' });
  b += arrow(826, 258, 826, 243, { color: P.violet, marker: 'arr-violet' });

  // Decoder residual arcs (right side)
  b += pathArrow('M 826 574 L 1018 574 L 1018 472 L 973 472', { color: P.amber, marker: 'arr-amber', sw: 1.8 });
  b += pathArrow('M 826 444 L 1018 444 L 1018 342 L 973 342', { color: P.amber, marker: 'arr-amber', sw: 1.8 });
  b += pathArrow('M 826 314 L 1018 314 L 1018 222 L 973 222', { color: P.amber, marker: 'arr-amber', sw: 1.8 });

  // Cross-attention bridge from Encoder top to Decoder Cross-Attention
  b += pathArrow('M 280 209 L 280 156 L 544 156 L 544 406 L 679 406', { color: P.blueDark, marker: 'arr-blue', sw: 2.5 });
  b += labelBox({ x: 468, y: 254, w: 152, h: 48, rx: 14, title: '传递 K, V 记忆', sub: 'Cross-Attention 桥梁', fill: '#FFFFFF', stroke: P.blue, titleColor: P.blueDark, titleSize: 12.5, subSize: 10.5 });

  // Decoder Input bottom
  b += `<circle cx="826" cy="608" r="14" fill="#FFFFFF" stroke="${P.teal}" stroke-width="2" />`;
  b += `<text x="826" y="613.5" text-anchor="middle" font-size="17" font-weight="700" fill="${P.tealDark}">+</text>`;
  b += arrow(826, 594, 826, 563, { color: P.teal, marker: 'arr-teal', sw: 2 });

  b += labelBox({ x: 912, y: 590, w: 170, h: 36, title: 'Positional Encoding', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 12 });
  b += arrow(912, 608, 843, 608, { color: P.violet, marker: 'arr-violet', sw: 1.8 });

  b += labelBox({ x: 716, y: 636, w: 220, h: 34, title: 'Output Embedding', fill: P.tealLight, stroke: P.teal, titleColor: P.tealDark, titleSize: 12.5 });
  b += arrow(826, 636, 826, 624, { color: P.teal, marker: 'arr-teal', sw: 1.8 });
  b += pill({ x: 682, y: 682, w: 288, h: 28, fill: '#FFFFFF', stroke: P.border, text: '已生成译文（右移）：<bos>  我  喜欢', color: P.text, fontSize: 12 });
  b += arrow(826, 682, 826, 672, { color: P.slate, marker: 'arr-slate', sw: 1.6 });

  // Decoder Output top (Linear + Softmax)
  b += labelBox({ x: 682, y: 122, w: 132, h: 38, title: 'Linear', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 13 });
  b += labelBox({ x: 838, y: 122, w: 132, h: 38, title: 'Softmax', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.emerald, titleSize: 13 });
  b += pathArrow('M 826 204 L 826 172 L 748 172 L 748 163', { color: P.teal, marker: 'arr-teal', sw: 2 });
  b += arrow(814, 141, 835, 141, { color: P.violet, marker: 'arr-violet', sw: 2 });
  b += pill({ x: 988, y: 124, w: 112, h: 34, fill: P.emeraldLight, stroke: P.emerald, text: '预测：机器', color: P.tealDark, fontSize: 12.5 });
  b += arrow(970, 141, 985, 141, { color: P.emerald, marker: 'arr-emerald', sw: 2 });

  // Annotation callout at top left
  b += box({ x: 46, y: 100, w: 454, h: 46, rx: 10, fill: P.amberPale, stroke: P.amberLight, sw: 1.2, shadow: false });
  b += `<text x="62" y="128" font-size="12.5" font-weight="600" fill="${P.amberDark}">⚡ 彻底抛弃 RNN/CNN：全部由「注意力 + 前馈网络 + 残差归一化」堆叠而成</text>`;

  return wrapSvg({
    width, height,
    title: '原始 Transformer 编码器—解码器架构（Attention Is All You Need, 2017）',
    subtitle: '左侧编码器并行理解源序列，右侧解码器结合因果自注意力与交叉注意力逐步生成译文',
    badge: '§7 Transformer 架构',
    body: b,
  });
}

// 24: Self-attention score heatmap
function fig24() {
  const width = 1140, height = 620;
  const tokens = ['I', 'love', 'machine', 'learning', 'because', 'it', 'works'];
  // Realistic attention weights (rows sum to 1.00)
  const weights = [
    [0.54, 0.24, 0.06, 0.07, 0.03, 0.03, 0.03], // I
    [0.28, 0.34, 0.14, 0.16, 0.02, 0.03, 0.03], // love
    [0.04, 0.12, 0.42, 0.34, 0.02, 0.04, 0.02], // machine
    [0.03, 0.11, 0.46, 0.31, 0.02, 0.04, 0.03], // learning  <-- HIGHLIGHTED
    [0.05, 0.14, 0.10, 0.14, 0.30, 0.12, 0.15], // because
    [0.04, 0.06, 0.32, 0.38, 0.05, 0.09, 0.06], // it
    [0.04, 0.08, 0.14, 0.18, 0.10, 0.24, 0.22], // works
  ];

  let b = '';
  const gx = 126, gy = 174, cell = 52;

  // Left card: Heatmap
  b += box({ x: 34, y: 102, w: 516, h: 478, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += `<text x="56" y="130" font-size="15.5" font-weight="700" fill="${P.text}">自注意力权重矩阵 α（每行之和 = 1.00）</text>`;
  b += `<text x="56" y="150" font-size="12" fill="${P.textSec}">纵轴 = 当前查询词 Query，横轴 = 被读取词 Key</text>`;

  // Column labels
  tokens.forEach((tok, j) => {
    const cx = gx + j * cell + cell / 2;
    b += `<text x="${cx}" y="${gy - 10}" text-anchor="middle" font-size="11" font-weight="${j === 2 || j === 3 ? 700 : 500}" fill="${j === 2 ? P.blueDark : P.textSec}">${tok}</text>`;
  });

  // Grid cells
  for (let i = 0; i < 7; i++) {
    const ry = gy + i * cell;
    const isFocus = i === 3; // "learning"
    b += `<text x="${gx - 12}" y="${ry + 31}" text-anchor="end" font-size="12.5" font-weight="${isFocus ? 700 : 500}" fill="${isFocus ? P.amberDark : P.text}">${tokens[i]}</text>`;
    for (let j = 0; j < 7; j++) {
      const cx = gx + j * cell;
      const v = weights[i][j];
      const alpha = Math.min(1, 0.08 + v * 1.65);
      const fill = isFocus ? `rgba(217, 119, 6, ${alpha.toFixed(2)})` : `rgba(37, 99, 235, ${alpha.toFixed(2)})`;
      const txtCol = v >= 0.30 ? '#FFFFFF' : P.text;
      b += `<rect x="${cx + 2}" y="${ry + 2}" width="${cell - 4}" height="${cell - 4}" rx="6" fill="${fill}" stroke="${isFocus ? P.amber : '#E2E8F0'}" stroke-width="${isFocus ? 1.4 : 0.8}" />`;
      b += `<text x="${cx + cell / 2}" y="${ry + 31}" text-anchor="middle" font-size="11.5" font-weight="${v >= 0.25 ? 700 : 500}" fill="${txtCol}">${v.toFixed(2)}</text>`;
    }
    if (isFocus) {
      b += `<rect x="${gx - 2}" y="${ry - 1}" width="${7 * cell + 4}" height="${cell + 2}" rx="8" fill="none" stroke="${P.amber}" stroke-width="2.5" />`;
    }
  }

  // Highlight badge below heatmap
  b += pill({ x: 56, y: 545, w: 468, h: 24, fill: P.amberPale, stroke: P.amberLight, text: '高亮行：当 Query = "learning" 时，它重点读取 "machine" (0.46) 组成词组', color: P.amberDark, fontSize: 11.5 });

  // Right card: Intuitive connection breakdown for Query = "learning"
  b += box({ x: 574, y: 102, w: 532, h: 478, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += `<text x="598" y="130" font-size="15.5" font-weight="700" fill="${P.text}">聚焦当前词 "learning"：如何从上下文汲取信息</text>`;
  b += `<text x="598" y="150" font-size="12" fill="${P.textSec}">线条越粗、颜色越深，表示分配给该词的注意力权重越高</text>`;

  // Left node: Query "learning"
  b += labelBox({ x: 602, y: 282, w: 126, h: 70, title: 'learning', sub: '当前 Query (q₄)', fill: P.amberLight, stroke: P.amber, titleColor: P.amberDark, titleSize: 16, subSize: 11.5, sw: 2.2 });

  // Right nodes: All 7 Keys + Value bars
  const focusRow = weights[3];
  tokens.forEach((tok, j) => {
    const ny = 180 + j * 48;
    const w = focusRow[j];
    const strong = w >= 0.10;
    // Bezier line from Query to Key
    const sw = Math.max(1.2, w * 14);
    const op = Math.max(0.18, Math.min(0.95, w * 2.1));
    const strokeCol = j === 2 ? P.blue : (j === 3 ? P.amber : P.teal);
    b += `<path d="M 728 317 C 786 317, 792 ${ny + 18}, 848 ${ny + 18}" fill="none" stroke="${strokeCol}" stroke-width="${sw.toFixed(1)}" stroke-opacity="${op.toFixed(2)}" stroke-linecap="round" />`;

    // Token box
    b += box({ x: 850, y: ny, w: 102, h: 36, rx: 8, fill: j === 2 ? P.bluePale : (j === 3 ? P.amberPale : '#F8FAFC'), stroke: strong ? strokeCol : P.border, sw: strong ? 1.8 : 1, shadow: false });
    b += `<text x="901" y="${ny + 23}" text-anchor="middle" font-size="13" font-weight="${strong ? 700 : 500}" fill="${P.text}">${tok}</text>`;

    // Horizontal mini bar for weight
    const barW = Math.round(w * 180);
    b += `<rect x="964" y="${ny + 10}" width="118" height="16" rx="4" fill="#F1F5F9" />`;
    b += `<rect x="964" y="${ny + 10}" width="${Math.min(118, barW)}" height="16" rx="4" fill="${strokeCol}" fill-opacity="${strong ? 0.85 : 0.35}" />`;
    b += `<text x="1088" y="${ny + 23}" text-anchor="end" font-size="11.5" font-weight="${strong ? 700 : 500}" fill="${strong ? P.text : P.textMuted}">${(w * 100).toFixed(0)}%</text>`;
  });

  // Extra insight box at bottom right
  b += box({ x: 594, y: 526, w: 492, h: 42, rx: 10, fill: P.bluePale, stroke: P.blueLight, sw: 1.2, shadow: false });
  b += `<text x="610" y="551" font-size="11.5" font-weight="600" fill="${P.blueDark}">📌 看矩阵第 6 行 "it"：它把 70% 的权重分给了 "machine"(0.32) + "learning"(0.38)！</text>`;

  return wrapSvg({
    width, height,
    title: '自注意力分数热图：让每个词直接“看到”上下文中的相关词',
    subtitle: '任意两个词在一层之内直接建立联系，无需像 RNN 那样一步步传递状态',
    badge: '§7.1 注意力直觉',
    body: b,
  });
}

// 02: Self-attention Q, K, V matching and aggregation
function fig02() {
  const width = 1160, height = 650;
  let b = '';

  // Top legend explaining Q, K, V roles
  b += box({ x: 34, y: 98, w: 348, h: 52, rx: 10, fill: P.bluePale, stroke: P.blueLight, shadow: false });
  b += `<text x="50" y="120" font-size="13.5" font-weight="700" fill="${P.blueDark}">Query (q) · 查询向量</text>`;
  b += `<text x="50" y="139" font-size="12" fill="${P.textSec}">“当前位置想寻找哪类上下文信息？”</text>`;

  b += box({ x: 406, y: 98, w: 348, h: 52, rx: 10, fill: P.tealPale, stroke: P.tealLight, shadow: false });
  b += `<text x="422" y="120" font-size="13.5" font-weight="700" fill="${P.tealDark}">Key (k) · 键向量</text>`;
  b += `<text x="422" y="139" font-size="12" fill="${P.textSec}">“我这个位置有什么可供匹配的标签？”</text>`;

  b += box({ x: 778, y: 98, w: 348, h: 52, rx: 10, fill: P.amberPale, stroke: P.amberLight, shadow: false });
  b += `<text x="794" y="120" font-size="13.5" font-weight="700" fill="${P.amberDark}">Value (v) · 值向量</text>`;
  b += `<text x="794" y="139" font-size="12" fill="${P.textSec}">“匹配成功后，我实际提供的语义内容”</text>`;

  // Step 1: Three tokens on the left producing Q, K, V
  const toks = [
    { name: 'x₁ (machine)', y: 204, k: 'k₁', v: 'v₁', score: '2.8', alpha: '0.6', barW: 96, vVals: [0.9, 0.3, 0.8, 0.6] },
    { name: 'x₂ (learning)', y: 340, k: 'k₂', v: 'v₂', score: '2.1', alpha: '0.3', barW: 48, vVals: [0.4, 0.85, 0.5, 0.7] },
    { name: 'x₃ (love)', y: 476, k: 'k₃', v: 'v₃', score: '1.0', alpha: '0.1', barW: 16, vVals: [0.2, 0.5, 0.9, 0.3] },
  ];

  // Column headers
  b += `<text x="108" y="182" text-anchor="middle" font-size="13" font-weight="700" fill="${P.textSec}">① 序列输入与投影</text>`;
  b += `<text x="380" y="182" text-anchor="middle" font-size="13" font-weight="700" fill="${P.textSec}">② Q 与各 K 点积打分</text>`;
  b += `<text x="646" y="182" text-anchor="middle" font-size="13" font-weight="700" fill="${P.textSec}">③ Softmax 权重</text>`;
  b += `<text x="954" y="182" text-anchor="middle" font-size="13" font-weight="700" fill="${P.textSec}">④ 对 V 加权求和输出</text>`;

  // Highlight Query source from x2 (current token)
  toks.forEach((t, idx) => {
    const isCur = idx === 1;
    b += labelBox({
      x: 42, y: t.y, w: 132, h: 52,
      title: t.name, sub: isCur ? '当前计算位置 t' : '上下文位置 s',
      fill: isCur ? P.bluePale : '#FFFFFF', stroke: isCur ? P.blue : P.border,
      titleColor: isCur ? P.blueDark : P.text, titleSize: 13, subSize: 10.5
    });

    // K vector pill
    b += box({ x: 214, y: t.y - 6, w: 88, h: 30, rx: 7, fill: P.tealLight, stroke: P.teal, sw: 1.4, shadow: false });
    b += `<text x="258" y="${t.y + 13.5}" text-anchor="middle" font-size="12" font-weight="700" fill="${P.tealDark}">${t.k} = x${idx + 1}W_K</text>`;
    b += arrow(174, t.y + 14, 212, t.y + 10, { color: P.teal, marker: 'arr-teal', sw: 1.5 });

    // V vector pill
    b += box({ x: 214, y: t.y + 34, w: 88, h: 30, rx: 7, fill: P.amberLight, stroke: P.amber, sw: 1.4, shadow: false });
    b += `<text x="258" y="${t.y + 53.5}" text-anchor="middle" font-size="12" font-weight="700" fill="${P.amberDark}">${t.v} = x${idx + 1}W_V</text>`;
    b += arrow(174, t.y + 38, 212, t.y + 48, { color: P.amber, marker: 'arr-amber', sw: 1.5 });

    // Dot product node
    b += box({ x: 424, y: t.y - 10, w: 124, h: 42, rx: 9, fill: '#FFFFFF', stroke: P.blue, sw: 1.5 });
    b += `<text x="486" y="${t.y + 8}" text-anchor="middle" font-size="12" font-weight="700" fill="${P.blueDark}">q₂ᵀ ${t.k} / √dₖ</text>`;
    b += `<text x="486" y="${t.y + 25}" text-anchor="middle" font-size="11.5" fill="${P.textSec}">分数 = ${t.score}</text>`;
    b += arrow(302, t.y + 9, 421, t.y + 11, { color: P.teal, marker: 'arr-teal', sw: 1.6 });

    // Arrow to Softmax weight
    b += arrow(548, t.y + 11, 594, t.y + 11, { color: P.slate, marker: 'arr-slate', sw: 1.6 });

    // Weight card
    b += box({ x: 598, y: t.y - 10, w: 118, h: 42, rx: 9, fill: P.violetPale, stroke: P.violet, sw: 1.6 });
    b += `<text x="657" y="${t.y + 8}" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.violetDark}">α = ${t.alpha}</text>`;
    b += `<rect x="609" y="${t.y + 17}" width="96" height="8" rx="4" fill="#E2E8F0" />`;
    b += `<rect x="609" y="${t.y + 17}" width="${t.barW}" height="8" rx="4" fill="${P.violet}" />`;

    // Multiply node (α * v)
    b += `<circle cx="776" cy="${t.y + 26}" r="16" fill="${P.amberPale}" stroke="${P.amber}" stroke-width="1.8" />`;
    b += `<text x="776" y="${t.y + 32}" text-anchor="middle" font-size="17" font-weight="700" fill="${P.amberDark}">×</text>`;

    // Connect alpha and v into ×
    b += pathArrow(`M 716 ${t.y + 11} L 748 ${t.y + 11} L 762 ${t.y + 20}`, { color: P.violet, marker: 'arr-violet', sw: 1.8 });
    b += pathArrow(`M 302 ${t.y + 49} L 732 ${t.y + 49} L 761 ${t.y + 34}`, { color: P.amber, marker: 'arr-amber', sw: 1.5, dash: '5 3' });

    // Weighted v output arrow to Sum
    b += pathArrow(`M 792 ${t.y + 26} L 836 ${t.y + 26} L 872 366`, { color: P.amberDark, marker: 'arr-amber', sw: 1.4 + parseFloat(t.alpha) * 3 });
  });

  // Floating Query box (q2) branching to all 3 dot products
  b += box({ x: 326, y: 342, w: 72, h: 44, rx: 9, fill: P.blue, stroke: P.blueDark, sw: 1.8 });
  b += `<text x="362" y="362" text-anchor="middle" font-size="14" font-weight="700" fill="#FFFFFF">q₂</text>`;
  b += `<text x="362" y="378" text-anchor="middle" font-size="10.5" fill="${P.blueLight}">x₂ W_Q</text>`;
  b += pathArrow('M 108 392 L 108 424 L 362 424 L 362 389', { color: P.blue, marker: 'arr-blue', sw: 2 });
  b += pathArrow('M 398 354 L 410 354 L 410 215 L 421 215', { color: P.blue, marker: 'arr-blue', sw: 1.8 });
  b += arrow(398, 364, 421, 352, { color: P.blue, marker: 'arr-blue', sw: 1.8 });
  b += pathArrow('M 398 374 L 410 374 L 410 487 L 421 487', { color: P.blue, marker: 'arr-blue', sw: 1.8 });

  // Softmax vertical brace box label
  b += pill({ x: 604, y: 540, w: 106, h: 24, fill: P.violetLight, stroke: P.violet, text: '0.6+0.3+0.1=1', color: P.violetDark, fontSize: 11 });

  // Sum circle & Final Output Box
  b += `<circle cx="894" cy="366" r="24" fill="${P.emeraldPale}" stroke="${P.emerald}" stroke-width="2.2" />`;
  b += `<text x="894" y="374" text-anchor="middle" font-size="22" font-weight="700" fill="${P.emerald}">Σ</text>`;
  b += arrow(918, 366, 954, 366, { color: P.emerald, marker: 'arr-emerald', sw: 2.4 });

  b += box({ x: 958, y: 294, w: 168, h: 146, rx: 14, fill: P.emeraldPale, stroke: P.emerald, sw: 2 });
  b += `<text x="1042" y="322" text-anchor="middle" font-size="14.5" font-weight="700" fill="${P.tealDark}">输出表示 o₂</text>`;
  b += `<text x="1042" y="344" text-anchor="middle" font-size="12.5" font-weight="600" fill="${P.text}">0.6v₁ + 0.3v₂ + 0.1v₃</text>`;
  b += vecBars({ x: 992, y: 360, vals: [0.74, 0.56, 0.72, 0.61], cellW: 22, cellH: 22, color: P.emerald });
  b += `<text x="1042" y="406" text-anchor="middle" font-size="11.5" fill="${P.textSec}">融合了 "machine" 等</text>`;
  b += `<text x="1042" y="423" text-anchor="middle" font-size="11.5" fill="${P.textSec}">上下文的新语义向量</text>`;

  // Bottom summary note
  b += noteBar({
    x: 34, y: 584, w: 1092, h: 40,
    text: '核心直觉：权重不是写死的规则，而是由当前内容 qₜ 与各位置 kₛ 的相似度动态算出——不同句子里，同一个词会动态读取不同上下文。',
  });

  return wrapSvg({
    width, height,
    title: '用 Query、Key、Value 直观理解一次自注意力读取',
    subtitle: '展示位置 t=2（learning）如何通过点积匹配、Softmax 归一化与加权汇总得到上下文输出 o₂',
    badge: '§7.2 Q/K/V 机制',
    body: b,
  });
}

// 03: Scaled Dot-Product Attention Matrices & Shapes
function fig03() {
  const width = 1160, height = 560;
  let b = '';

  // Formula bar
  b += box({ x: 260, y: 98, w: 640, h: 42, rx: 10, fill: P.bluePale, stroke: P.blueLight, shadow: false });
  b += `<text x="580" y="125" text-anchor="middle" font-size="16" font-weight="700" fill="${P.blueDark}">Attention(Q, K, V) = softmax(  Q Kᵀ / √dₖ  +  M  ) · V</text>`;

  // Helper to draw a styled matrix grid
  function drawMatrix({ x, y, rows, cols, cellW, cellH, color, hiRow = -1, hiCol = -1, label, dim, sub = '' }) {
    const w = cols * cellW, h = rows * cellH;
    let out = `<g>`;
    out += `<text x="${x + w / 2}" y="${y - 12}" text-anchor="middle" font-size="14" font-weight="700" fill="${color}">${esc(label)}</text>`;
    out += `<rect x="${x - 3}" y="${y - 3}" width="${w + 6}" height="${h + 6}" rx="6" fill="#FFFFFF" stroke="${color}" stroke-width="1.6" />`;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const isHi = r === hiRow || c === hiCol;
        out += `<rect x="${x + c * cellW + 1}" y="${y + r * cellH + 1}" width="${cellW - 2}" height="${cellH - 2}" rx="2.5" fill="${color}" fill-opacity="${isHi ? 0.72 : 0.16}" />`;
      }
    }
    out += `<text x="${x + w / 2}" y="${y + h + 22}" text-anchor="middle" font-size="13" font-weight="700" fill="${P.text}" class="mono">${esc(dim)}</text>`;
    if (sub) out += `<text x="${x + w / 2}" y="${y + h + 40}" text-anchor="middle" font-size="11.5" fill="${P.textSec}">${esc(sub)}</text>`;
    out += `</g>`;
    return out;
  }

  // Stage 1: Q (T × d_k) × K^T (d_k × T)
  b += drawMatrix({ x: 46, y: 204, rows: 5, cols: 3, cellW: 24, cellH: 26, color: P.blue, hiRow: 1, label: 'Q', dim: 'T × dₖ', sub: '第 t 行 = qₜ' });
  b += `<text x="136" y="274" text-anchor="middle" font-size="22" font-weight="700" fill="${P.slate}">×</text>`;
  b += drawMatrix({ x: 156, y: 230, rows: 3, cols: 5, cellW: 24, cellH: 26, color: P.teal, hiCol: -1, label: 'Kᵀ', dim: 'dₖ × T', sub: '每列 = kₛ' });

  b += arrow(288, 268, 326, 268, { color: P.slate, marker: 'arr-slate', sw: 2.2 });

  // Stage 2: Score Matrix QK^T (T × T)
  b += drawMatrix({ x: 336, y: 204, rows: 5, cols: 5, cellW: 24, cellH: 26, color: P.amber, hiRow: 1, label: '匹配分数 QKᵀ', dim: 'T × T', sub: '两两打分矩阵' });

  // Scale + Mask + Softmax op pill
  b += arrow(466, 268, 496, 268, { color: P.violet, marker: 'arr-violet', sw: 2.2 });
  b += labelBox({ x: 500, y: 224, w: 124, h: 88, title: '÷ √dₖ  +  M', sub: '逐行 Softmax', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 13.5, subSize: 12 });
  b += `<text x="562" y="330" text-anchor="middle" font-size="11" fill="${P.textSec}">防点积过大 + 掩码</text>`;
  b += arrow(626, 268, 656, 268, { color: P.violet, marker: 'arr-violet', sw: 2.2 });

  // Stage 3: Attention Weights (T × T)
  b += drawMatrix({ x: 666, y: 204, rows: 5, cols: 5, cellW: 24, cellH: 26, color: P.violet, hiRow: 1, label: '注意力权重 A', dim: 'T × T', sub: '每行和为 1.0' });

  b += `<text x="804" y="274" text-anchor="middle" font-size="22" font-weight="700" fill="${P.slate}">×</text>`;

  // Stage 4: V (T × d_v)
  b += drawMatrix({ x: 824, y: 204, rows: 5, cols: 4, cellW: 24, cellH: 26, color: P.amberDark, hiRow: -1, label: 'V', dim: 'T × dᵥ', sub: '各位置值向量' });

  b += `<text x="942" y="274" text-anchor="middle" font-size="22" font-weight="700" fill="${P.slate}">=</text>`;

  // Stage 5: Output (T × d_v)
  b += drawMatrix({ x: 964, y: 204, rows: 5, cols: 4, cellW: 24, cellH: 26, color: P.emerald, hiRow: 1, label: '输出 O', dim: 'T × dᵥ', sub: '第 t 行 = oₜ' });

  // Callout cards below explaining dimension flow & complexity
  b += box({ x: 42, y: 404, w: 342, h: 118, rx: 12, fill: '#FFFFFF', stroke: P.blueLight, sw: 1.5 });
  b += pill({ x: 58, y: 418, w: 124, h: 24, fill: P.bluePale, stroke: P.blue, text: '1. 为什么除以 √dₖ', color: P.blueDark, fontSize: 11.5 });
  b += `<text x="58" y="464" font-size="12.5" fill="${P.text}">向量维度 dₖ 越大，点积的方差越大（≈ dₖ），</text>`;
  b += `<text x="58" y="484" font-size="12.5" fill="${P.text}">直接进 Softmax 会导致梯度接近 0；</text>`;
  b += `<text x="58" y="504" font-size="12.5" font-weight="600" fill="${P.blueDark}">除以 √dₖ 把方差拉回 ≈ 1，训练更稳定。</text>`;

  b += box({ x: 408, y: 404, w: 342, h: 118, rx: 12, fill: '#FFFFFF', stroke: P.violetLight, sw: 1.5 });
  b += pill({ x: 424, y: 418, w: 140, h: 24, fill: P.violetPale, stroke: P.violet, text: '2. 为什么复杂度 O(T²)', color: P.violetDark, fontSize: 11.5 });
  b += `<text x="424" y="464" font-size="12.5" fill="${P.text}">中间分数矩阵 QKᵀ 的形状是 T × T：</text>`;
  b += `<text x="424" y="484" font-size="12.5" fill="${P.text}">序列长度 T 翻倍，计算量与显存占用</text>`;
  b += `<text x="424" y="504" font-size="12.5" font-weight="600" fill="${P.violetDark}">都会变成原来的 4 倍！</text>`;

  b += box({ x: 774, y: 404, w: 342, h: 118, rx: 12, fill: '#FFFFFF', stroke: P.emeraldLight, sw: 1.5 });
  b += pill({ x: 790, y: 418, w: 132, h: 24, fill: P.emeraldPale, stroke: P.emerald, text: '3. 矩阵乘的直觉', color: P.tealDark, fontSize: 11.5 });
  b += `<text x="790" y="464" font-size="12.5" fill="${P.text}">高亮第 t 行：A 的第 t 行是 T 个权重，</text>`;
  b += `<text x="790" y="484" font-size="12.5" fill="${P.text}">乘以 V 就是对 V 的 T 行做加权平均，</text>`;
  b += `<text x="790" y="504" font-size="12.5" font-weight="600" fill="${P.tealDark}">一次矩阵乘法就并行算完所有 T 个位置！</text>`;

  return wrapSvg({
    width, height,
    title: '缩放点积注意力：用矩阵形状看懂所有位置如何一次性并行计算',
    subtitle: '深色高亮行展示第 t 个位置（qₜ → 权重第 t 行 → 输出 oₜ）的数据流向',
    badge: '§7.2 矩阵计算',
    body: b,
  });
}

// 29: Causal Mask
function fig29() {
  const width = 1140, height = 570;
  const toks = ['我', '喜', '欢', '学', '习'];
  const raw = [
    [1.8, 0.9, 0.4, 0.7, 0.3],
    [1.1, 1.9, 1.4, 0.6, 0.5],
    [0.8, 1.7, 2.0, 1.2, 0.9],
    [0.5, 0.9, 1.3, 2.1, 1.8],
    [0.6, 0.8, 1.1, 1.9, 2.2],
  ];
  // Compute masked softmax accurately
  const soft = raw.map((row, i) => {
    const allowed = row.slice(0, i + 1);
    const maxV = Math.max(...allowed);
    const exps = allowed.map((v) => Math.exp(v - maxV));
    const sum = exps.reduce((a, c) => a + c, 0);
    return row.map((_, j) => (j <= i ? exps[j] / sum : 0));
  });

  let b = '';
  const cell = 52;

  function drawGrid({ x, y, title, sub, type }) {
    let out = `<g>`;
    out += `<text x="${x + 2.5 * cell}" y="${y - 44}" text-anchor="middle" font-size="15" font-weight="700" fill="${P.text}">${esc(title)}</text>`;
    out += `<text x="${x + 2.5 * cell}" y="${y - 25}" text-anchor="middle" font-size="11.5" fill="${P.textSec}">${esc(sub)}</text>`;
    toks.forEach((t, j) => {
      out += `<text x="${x + j * cell + cell / 2}" y="${y - 7}" text-anchor="middle" font-size="12.5" font-weight="600" fill="${P.textSec}">${t}</text>`;
    });
    for (let i = 0; i < 5; i++) {
      out += `<text x="${x - 10}" y="${y + i * cell + 31}" text-anchor="end" font-size="12.5" font-weight="600" fill="${P.text}">${toks[i]}</text>`;
      for (let j = 0; j < 5; j++) {
        const cx = x + j * cell, cy = y + i * cell;
        const future = j > i;
        let fill = '#FFFFFF', stroke = P.border, txt = '', txtCol = P.text, bold = false;
        if (type === 'raw') {
          fill = future ? '#F8FAFC' : P.bluePale;
          stroke = future ? P.border : P.blueLight;
          txt = raw[i][j].toFixed(1);
          txtCol = future ? P.textMuted : P.blueDark;
        } else if (type === 'mask') {
          fill = future ? P.roseLight : P.emeraldPale;
          stroke = future ? P.rose : P.emerald;
          txt = future ? '−∞' : '0';
          txtCol = future ? P.roseDark : P.tealDark;
          bold = true;
        } else {
          if (future) {
            fill = '#F1F5F9';
            stroke = '#E2E8F0';
            txt = '0.00';
            txtCol = '#94A3B8';
          } else {
            const v = soft[i][j];
            const op = Math.min(0.92, 0.14 + v * 0.9);
            fill = `rgba(37, 99, 235, ${op.toFixed(2)})`;
            stroke = P.blue;
            txt = v.toFixed(2);
            txtCol = v > 0.36 ? '#FFFFFF' : P.text;
            bold = v > 0.3;
          }
        }
        out += `<rect x="${cx + 2}" y="${cy + 2}" width="${cell - 4}" height="${cell - 4}" rx="6" fill="${fill}" stroke="${stroke}" stroke-width="1.2" />`;
        out += `<text x="${cx + cell / 2}" y="${cy + 31}" text-anchor="middle" font-size="12" font-weight="${bold ? 700 : 500}" fill="${txtCol}">${txt}</text>`;
      }
    }
    out += `</g>`;
    return out;
  }

  b += drawGrid({ x: 64, y: 184, title: '① 原始缩放分数 QKᵀ / √dₖ', sub: '所有位置两两打分（包含未来词）', type: 'raw' });

  b += `<circle cx="364" cy="314" r="18" fill="${P.rosePale}" stroke="${P.rose}" stroke-width="2" />`;
  b += `<text x="364" y="321" text-anchor="middle" font-size="22" font-weight="700" fill="${P.roseDark}">+</text>`;

  b += drawGrid({ x: 422, y: 184, title: '② 因果掩码矩阵 M', sub: '未来位置设 −∞，禁止“偷看答案”', type: 'mask' });

  b += arrow(696, 314, 772, 314, { color: P.blue, marker: 'arr-blue', sw: 2.5 });
  b += `<text x="734" y="302" text-anchor="middle" font-size="12" font-weight="700" fill="${P.blueDark}">Softmax</text>`;
  b += `<text x="734" y="334" text-anchor="middle" font-size="11" fill="${P.textSec}">e^(−∞) = 0</text>`;

  b += drawGrid({ x: 818, y: 184, title: '③ 最终注意力权重', sub: '上三角严格为 0，下三角每行和为 1', type: 'soft' });

  // Bottom insight cards
  b += box({ x: 38, y: 468, w: 520, h: 70, rx: 12, fill: P.bluePale, stroke: P.blueLight, shadow: false });
  b += `<text x="56" y="495" font-size="13.5" font-weight="700" fill="${P.blueDark}">🚀 训练阶段：整句一次并行计算</text>`;
  b += `<text x="56" y="518" font-size="12.5" fill="${P.text}">只需一次矩阵乘法 + 上三角掩码，5 个位置的下一词预测同时算完！</text>`;

  b += box({ x: 582, y: 468, w: 520, h: 70, rx: 12, fill: P.tealPale, stroke: P.tealLight, shadow: false });
  b += `<text x="600" y="495" font-size="13.5" font-weight="700" fill="${P.tealDark}">🔄 推理阶段：逐步向下扩展一行一列</text>`;
  b += `<text x="600" y="518" font-size="12.5" fill="${P.text}">第 t 个位置只依赖 1..t 的历史表示，这也正是 KV Cache 能够复用的数学前提。</text>`;

  return wrapSvg({
    width, height,
    title: '因果掩码（Causal Mask）：第 t 个位置只能读取 1..t',
    subtitle: '以 “我 喜 欢 学 习” 为例，展示未来位置如何被置零以确保自回归预测不泄露后文',
    badge: '§7.2 因果掩码',
    body: b,
  });
}

// 04: Scaled Dot-Product Attention + Multi-Head Attention
function fig04() {
  const width = 1140, height = 650;
  let b = '';

  // Left Panel: Scaled Dot-Product Attention
  b += box({ x: 34, y: 102, w: 400, h: 516, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += `<text x="234" y="132" text-anchor="middle" font-size="16" font-weight="700" fill="${P.text}">单头：Scaled Dot-Product Attention</text>`;
  b += `<text x="234" y="152" text-anchor="middle" font-size="12" fill="${P.textSec}">单个注意力头内部的完整计算流程</text>`;

  // Bottom inputs Q, K, V
  b += labelBox({ x: 74, y: 538, w: 80, h: 42, title: 'Q', sub: 'T×dₖ', fill: P.bluePale, stroke: P.blue, titleColor: P.blueDark });
  b += labelBox({ x: 194, y: 538, w: 80, h: 42, title: 'K', sub: 'T×dₖ', fill: P.tealPale, stroke: P.teal, titleColor: P.tealDark });
  b += labelBox({ x: 314, y: 538, w: 80, h: 42, title: 'V', sub: 'T×dᵥ', fill: P.amberPale, stroke: P.amber, titleColor: P.amberDark });

  // Flow boxes bottom-up
  b += labelBox({ x: 94, y: 454, w: 162, h: 42, title: 'MatMul (Q · Kᵀ)', fill: P.blueLight, stroke: P.blue, titleColor: P.blueDark, titleSize: 13 });
  b += labelBox({ x: 94, y: 384, w: 162, h: 40, title: 'Scale (÷ √dₖ)', fill: '#F8FAFC', stroke: P.slate, titleColor: P.text, titleSize: 13 });
  b += labelBox({ x: 94, y: 314, w: 162, h: 40, title: 'Mask (+ M，可选)', fill: P.rosePale, stroke: P.rose, titleColor: P.roseDark, titleSize: 12.5 });
  b += labelBox({ x: 94, y: 244, w: 162, h: 40, title: 'Softmax（逐行）', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 13 });
  b += labelBox({ x: 148, y: 174, w: 192, h: 44, title: 'MatMul (Weights · V)', sub: '输出 headᵢ (T × dᵥ)', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 13 });

  // Arrows in left panel
  b += pathArrow('M 114 538 L 114 516 L 145 516 L 145 498', { color: P.blue, marker: 'arr-blue' });
  b += pathArrow('M 234 538 L 234 516 L 205 516 L 205 498', { color: P.teal, marker: 'arr-teal' });
  b += arrow(175, 454, 175, 427, { color: P.slate, marker: 'arr-slate' });
  b += arrow(175, 384, 175, 357, { color: P.slate, marker: 'arr-slate' });
  b += arrow(175, 314, 175, 287, { color: P.rose, marker: 'arr-rose' });
  b += pathArrow('M 175 244 L 175 228 L 210 228 L 210 221', { color: P.violet, marker: 'arr-violet' });
  b += pathArrow('M 354 538 L 354 228 L 296 228 L 296 221', { color: P.amber, marker: 'arr-amber', sw: 2 });

  // Right Panel: Multi-Head Attention
  b += box({ x: 458, y: 102, w: 648, h: 516, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += `<text x="782" y="132" text-anchor="middle" font-size="16" font-weight="700" fill="${P.text}">多头：Multi-Head Attention（并行 h 个视角）</text>`;
  b += `<text x="782" y="152" text-anchor="middle" font-size="12" fill="${P.textSec}">每个头用独立的投影矩阵，同时捕捉语法、搭配、指代等不同关系</text>`;

  // Input X at bottom
  b += labelBox({ x: 642, y: 544, w: 280, h: 48, title: '输入序列表示 X', sub: '形状：T × d  （通常 dₖ = dᵥ = d / h）', fill: P.bluePale, stroke: P.blue, titleColor: P.blueDark, titleSize: 14 });

  // 3 illustrative heads + "... h"
  const heads = [
    { x: 492, title: 'Head 1', role: '例如：主谓语法', col: P.blue, bg: P.bluePale },
    { x: 676, title: 'Head 2', role: '例如：词组搭配', col: P.teal, bg: P.tealPale },
    { x: 904, title: 'Head h', role: '例如：长距指代', col: P.violet, bg: P.violetPale },
  ];

  heads.forEach((hd) => {
    const cx = hd.x + 78;
    // Projection box
    b += labelBox({ x: hd.x, y: 438, w: 156, h: 48, title: `线性投影 (${hd.title})`, sub: 'W_Q⁽ⁱ⁾, W_K⁽ⁱ⁾, W_V⁽ⁱ⁾', fill: '#F8FAFC', stroke: hd.col, titleColor: P.text, titleSize: 12, subSize: 11 });
    // Attention box
    b += labelBox({ x: hd.x, y: 344, w: 156, h: 60, title: 'Scaled Dot-Product', sub: hd.role, fill: hd.bg, stroke: hd.col, titleColor: hd.col, titleSize: 12, subSize: 11.5 });
    // Arrows from X -> Proj -> Attn -> Concat
    b += pathArrow(`M 782 544 L 782 514 L ${cx} 514 L ${cx} 489`, { color: hd.col, marker: hd.col === P.blue ? 'arr-blue' : (hd.col === P.teal ? 'arr-teal' : 'arr-violet'), sw: 1.8 });
    b += arrow(cx, 438, cx, 407, { color: hd.col, marker: hd.col === P.blue ? 'arr-blue' : (hd.col === P.teal ? 'arr-teal' : 'arr-violet'), sw: 1.8 });
    b += pathArrow(`M ${cx} 344 L ${cx} 316 L 782 316 L 782 301`, { color: hd.col, marker: 'arr-slate', sw: 1.8 });
  });

  b += `<text x="868" y="380" text-anchor="middle" font-size="20" font-weight="700" fill="${P.textMuted}">···</text>`;

  // Concat box
  b += labelBox({ x: 584, y: 252, w: 396, h: 46, title: 'Concat（按特征维拼接所有头）', sub: 'head₁ ∥ head₂ ∥ ··· ∥ headₕ   →   形状：T × (h · dᵥ)', fill: P.amberPale, stroke: P.amber, titleColor: P.amberDark, titleSize: 13.5 });
  b += arrow(782, 252, 782, 232, { color: P.amber, marker: 'arr-amber', sw: 2 });

  // Linear W_O box
  b += labelBox({ x: 634, y: 176, w: 296, h: 52, title: '输出投影 Linear (W_O)', sub: '融合各头信息，映射回 T × d', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 14 });

  // Zoom connector dashed line from Head 1 to Left Panel
  b += `<path d="M 492 374 L 434 374" stroke="${P.blue}" stroke-width="1.8" stroke-dasharray="5 4" />`;
  b += pill({ x: 422, y: 363, w: 50, h: 22, fill: P.blue, stroke: P.blueDark, text: '展开', color: '#FFFFFF', fontSize: 10.5 });

  return wrapSvg({
    width, height,
    title: '缩放点积注意力与多头注意力的组合方式',
    subtitle: '把 d 维空间拆成 h 个子空间并行注意，再拼接融合——总计算量与单头相近，但表达角度更丰富',
    badge: '§7.2 多头注意力',
    body: b,
  });
}

// 05: Positional Encoding & RoPE
function fig05() {
  const width = 1160, height = 660;
  let b = '';

  // Top strip: Why order matters
  b += box({ x: 34, y: 96, w: 1092, h: 52, rx: 10, fill: P.rosePale, stroke: P.roseLight, shadow: false });
  b += `<text x="54" y="127" font-size="13.5" font-weight="700" fill="${P.roseDark}">为什么必须加位置编码？</text>`;
  b += `<text x="228" y="127" font-size="13" fill="${P.text}">纯自注意力满足排列等变性：打乱词序只打乱输出，分不清「人咬狗」和「狗咬人」！</text>`;

  // Left Panel: Sinusoidal Positional Encoding
  b += box({ x: 34, y: 164, w: 532, h: 462, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += pill({ x: 54, y: 180, w: 248, h: 26, fill: P.bluePale, stroke: P.blue, text: '方案 A · 正弦位置编码（加到输入）', color: P.blueDark, fontSize: 12 });
  b += `<text x="54" y="226" font-size="14" font-weight="700" fill="${P.text}">x̃ₜ = xₜ + pₜ     (不同维度 = 不同频率的时钟)</text>`;
  b += `<text x="54" y="246" font-size="12" fill="${P.textSec}">pₜ,₂ⱼ = sin(t / 10000^(2j/d))，  pₜ,₂ⱼ₊₁ = cos(t / 10000^(2j/d))</text>`;

  // Plot 3 sine waves at different frequencies
  const px = 78, py = 274, pw = 456, ph = 186;
  b += `<rect x="${px}" y="${py}" width="${pw}" height="${ph}" rx="8" fill="#F8FAFC" stroke="${P.borderLight}" />`;
  // Zero line
  b += `<line x1="${px}" y1="${py + ph / 2}" x2="${px + pw}" y2="${py + ph / 2}" stroke="#CBD5E1" stroke-dasharray="4 4" />`;
  b += `<text x="${px - 8}" y="${py + 16}" text-anchor="end" font-size="10.5" fill="${P.textMuted}">+1</text>`;
  b += `<text x="${px - 8}" y="${py + ph / 2 + 4}" text-anchor="end" font-size="10.5" fill="${P.textMuted}">0</text>`;
  b += `<text x="${px - 8}" y="${py + ph - 6}" text-anchor="end" font-size="10.5" fill="${P.textMuted}">-1</text>`;

  const waves = [
    { freq: 0.72, color: P.blue, label: '低维 j=0 (高频·像秒针)' },
    { freq: 0.24, color: P.teal, label: '中维 j=8 (中频·像分针)' },
    { freq: 0.08, color: P.amber, label: '高维 j=24 (低频·像时针)' },
  ];
  waves.forEach((w) => {
    let pts = '';
    for (let i = 0; i <= 160; i++) {
      const t = (i / 160) * 32;
      const sx = px + (i / 160) * pw;
      const sy = py + ph / 2 - Math.sin(t * w.freq) * (ph * 0.38);
      pts += (i === 0 ? 'M ' : ' L ') + sx.toFixed(1) + ' ' + sy.toFixed(1);
    }
    b += `<path d="${pts}" fill="none" stroke="${w.color}" stroke-width="2.3" stroke-linecap="round" />`;
  });

  // X-axis ticks
  [0, 8, 16, 24, 32].forEach((tk, idx) => {
    const tx = px + (idx / 4) * pw;
    b += `<text x="${tx}" y="${py + ph + 16}" text-anchor="middle" font-size="11" fill="${P.textMuted}">t=${tk}</text>`;
  });

  // Legend for waves
  waves.forEach((w, idx) => {
    const lx = 58 + idx * 168;
    b += `<line x1="${lx}" y1="496" x2="${lx + 18}" y2="496" stroke="${w.color}" stroke-width="3" stroke-linecap="round" />`;
    b += `<text x="${lx + 24}" y="500" font-size="11" font-weight="600" fill="${P.textSec}">${w.label}</text>`;
  });

  // Additive injection mini flow
  b += box({ x: 54, y: 522, w: 492, h: 86, rx: 10, fill: P.bluePale, stroke: P.blueLight, shadow: false });
  b += `<text x="72" y="548" font-size="13" font-weight="700" fill="${P.blueDark}">特点：在输入层一次性“相加”注入绝对位置</text>`;
  b += `<text x="72" y="570" font-size="12" fill="${P.text}">• 每个位置有唯一向量指纹，相邻位置编码接近</text>`;
  b += `<text x="72" y="592" font-size="12" fill="${P.text}">• 无需训练参数；也可用可学习的 Learned Positional Embedding 替代</text>`;

  // Right Panel: RoPE (Rotary Position Embedding)
  b += box({ x: 590, y: 164, w: 536, h: 462, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += pill({ x: 610, y: 180, w: 298, h: 26, fill: P.violetPale, stroke: P.violet, text: '方案 B · 旋转位置编码 RoPE（现代 LLM 主流）', color: P.violetDark, fontSize: 12 });
  b += `<text x="610" y="226" font-size="14" font-weight="700" fill="${P.text}">qₜ′ = R(t)qₜ ,   kₛ′ = R(s)kₛ  （在每对二维平面旋转）</text>`;
  b += `<text x="610" y="246" font-size="12" fill="${P.textSec}">不改变向量长度，只把位置编码进旋转角度 t·θⱼ 中</text>`;

  // 2D rotation plane diagram
  const cx = 738, cy = 384, rad = 92;
  // Coordinate circle & axes
  b += `<circle cx="${cx}" cy="${cy}" r="${rad}" fill="#F8FAFC" stroke="${P.border}" stroke-width="1.3" stroke-dasharray="4 3" />`;
  b += `<line x1="${cx - rad - 18}" y1="${cy}" x2="${cx + rad + 22}" y2="${cy}" stroke="#94A3B8" stroke-width="1.2" marker-end="url(#arr-muted)" />`;
  b += `<line x1="${cx}" y1="${cy + rad + 16}" x2="${cx}" y2="${cy - rad - 18}" stroke="#94A3B8" stroke-width="1.2" marker-end="url(#arr-muted)" />`;
  b += `<text x="${cx + rad + 26}" y="${cy + 4}" font-size="10.5" fill="${P.textMuted}">dim 2j</text>`;
  b += `<text x="${cx + 8}" y="${cy - rad - 10}" font-size="10.5" fill="${P.textMuted}">dim 2j+1</text>`;

  // Original reference vector (faint dashed at 12 deg)
  const a0 = -12 * Math.PI / 180;
  const at = -44 * Math.PI / 180; // q'_t at t*theta
  const as = -114 * Math.PI / 180; // k'_s at s*theta
  const rVec = 82;

  // Angle wedge between q'_t and k'_s
  const rArc = 46;
  const ax1 = cx + rArc * Math.cos(at), ay1 = cy + rArc * Math.sin(at);
  const ax2 = cx + rArc * Math.cos(as), ay2 = cy + rArc * Math.sin(as);
  b += `<path d="M ${cx} ${cy} L ${ax1.toFixed(1)} ${ay1.toFixed(1)} A ${rArc} ${rArc} 0 0 0 ${ax2.toFixed(1)} ${ay2.toFixed(1)} Z" fill="${P.violetLight}" fill-opacity="0.75" stroke="${P.violet}" stroke-width="1.4" />`;

  // Original faint vector
  b += `<line x1="${cx}" y1="${cy}" x2="${(cx + rVec * Math.cos(a0)).toFixed(1)}" y2="${(cy + rVec * Math.sin(a0)).toFixed(1)}" stroke="#94A3B8" stroke-width="1.5" stroke-dasharray="4 3" />`;
  b += `<text x="${(cx + rVec * Math.cos(a0) + 6).toFixed(1)}" y="${(cy + rVec * Math.sin(a0) - 4).toFixed(1)}" font-size="10.5" fill="${P.textMuted}">初始方向</text>`;

  // Vector q'_t (blue)
  const qx = cx + rVec * Math.cos(at), qy = cy + rVec * Math.sin(at);
  b += arrow(cx, cy, qx, qy, { color: P.blue, marker: 'arr-blue', sw: 2.8 });
  b += `<text x="${(qx + 8).toFixed(1)}" y="${(qy - 6).toFixed(1)}" font-size="13" font-weight="700" fill="${P.blueDark}">qₜ′ (转 tθⱼ)</text>`;

  // Vector k'_s (teal)
  const kx = cx + rVec * Math.cos(as), ky = cy + rVec * Math.sin(as);
  b += arrow(cx, cy, kx, ky, { color: P.teal, marker: 'arr-teal', sw: 2.8 });
  b += `<text x="${(kx - 76).toFixed(1)}" y="${(ky - 8).toFixed(1)}" font-size="13" font-weight="700" fill="${P.tealDark}">kₛ′ (转 sθⱼ)</text>`;

  // Angle label (s-t)theta
  const amid = (at + as) / 2;
  b += `<text x="${(cx + 64 * Math.cos(amid)).toFixed(1)}" y="${(cy + 64 * Math.sin(amid)).toFixed(1)}" text-anchor="middle" font-size="12" font-weight="700" fill="${P.violetDark}">(s − t)θⱼ</text>`;

  // Right side callout next to circle
  b += box({ x: 940, y: 298, w: 168, h: 152, rx: 10, fill: P.violetPale, stroke: P.violetLight, shadow: false });
  b += `<text x="1024" y="324" text-anchor="middle" font-size="12.5" font-weight="700" fill="${P.violetDark}">几何直觉</text>`;
  b += `<text x="954" y="350" font-size="11.5" fill="${P.text}">两个指针一起旋转，</text>`;
  b += `<text x="954" y="370" font-size="11.5" fill="${P.text}">它们的夹角只取决于</text>`;
  b += `<text x="954" y="392" font-size="12" font-weight="700" fill="${P.violetDark}">相对距离 (s − t)！</text>`;
  b += `<text x="954" y="416" font-size="11.5" fill="${P.textSec}">与绝对位置 t, s 无关</text>`;
  b += `<text x="954" y="434" font-size="11.5" fill="${P.textSec}">长上下文外推更自然</text>`;

  // Key identity box at bottom right
  b += box({ x: 610, y: 522, w: 496, h: 86, rx: 10, fill: P.violetPale, stroke: P.violet, sw: 1.5, shadow: false });
  b += `<text x="858" y="551" text-anchor="middle" font-size="15.5" font-weight="700" fill="${P.violetDark}">qₜ′ᵀ kₛ′ = qₜᵀ R(t)ᵀ R(s) kₛ = qₜᵀ R(s − t) kₛ</text>`;
  b += `<text x="858" y="576" text-anchor="middle" font-size="12.5" fill="${P.text}">在每层计算 Attention 时直接作用于 Q 和 K，将相对位移无缝注入点积打分</text>`;
  b += `<text x="858" y="596" text-anchor="middle" font-size="11.5" fill="${P.textSec}">（Llama、Qwen、DeepSeek 等现代大模型普遍采用 RoPE）</text>`;

  return wrapSvg({
    width, height,
    title: '位置编码（Sinusoidal PE）与旋转位置编码（RoPE）对比',
    subtitle: '前者在输入端做加法注入绝对位置；后者在注意力内通过二维旋转把相对距离直接写进点积',
    badge: '§7.3 位置编码',
    body: b,
  });
}

export const figures = [
  { filename: '28_seq2seq-bottleneck.png', width: 1140, height: 560, render: fig28 },
  { filename: '01_original-transformer-architecture.png', width: 1140, height: 740, render: fig01 },
  { filename: '24_self-attention-score-heatmap.png', width: 1140, height: 620, render: fig24 },
  { filename: '02_self-attention-query-key-value.png', width: 1160, height: 650, render: fig02 },
  { filename: '03_scaled-dot-product-attention-matrices.png', width: 1160, height: 560, render: fig03 },
  { filename: '29_causal-mask.png', width: 1140, height: 570, render: fig29 },
  { filename: '04_scaled-dot-product-and-multi-head-attention.png', width: 1140, height: 650, render: fig04 },
  { filename: '05_positional-encoding-and-rope.png', width: 1160, height: 660, render: fig05 },
];
