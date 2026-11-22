import { PALETTE as P, wrapSvg, box, labelBox, pill, arrow, pathArrow, vecBars, noteBar, esc, seededRand } from '../lib/svg.mjs';

// 06: Transformer Block (Pre-Norm, Residual, SwiGLU)
function fig06() {
  const width = 1140, height = 680;
  let b = '';

  // Left main panel: Pre-Norm Transformer Block
  b += box({ x: 34, y: 100, w: 540, h: 546, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += pill({ x: 54, y: 116, w: 288, h: 26, fill: P.bluePale, stroke: P.blue, text: 'Pre-Norm Transformer Block（现代 LLM 标配）', color: P.blueDark, fontSize: 12 });

  // Residual Highway vertical track on left
  b += `<line x1="112" y1="598" x2="112" y2="164" stroke="${P.amber}" stroke-width="5" stroke-opacity="0.35" stroke-linecap="round" />`;
  b += `<text x="76" y="388" text-anchor="middle" font-size="12" font-weight="700" fill="${P.amberDark}" transform="rotate(-90 76 388)">残差主干高速公路（梯度直通）</text>`;

  // Input H^(l) at bottom
  b += labelBox({ x: 204, y: 582, w: 264, h: 46, title: '输入 H⁽ˡ⁾ ∈ ℝ^(T × d)', sub: '第 ℓ 层输入序列表示', fill: P.bluePale, stroke: P.blue, titleColor: P.blueDark, titleSize: 13.5 });

  // First sub-block: Norm -> Multi-Head Attention -> +
  b += box({ x: 178, y: 404, w: 344, h: 146, rx: 12, fill: P.bluePale, stroke: P.blueLight, sw: 1.4, dash: '5 3', shadow: false });
  b += `<text x="506" y="424" text-anchor="end" font-size="11" font-weight="700" fill="${P.blueDark}">子层 1：位置间信息交互</text>`;
  b += labelBox({ x: 214, y: 492, w: 244, h: 42, title: 'Norm（LayerNorm / RMSNorm）', fill: P.amberPale, stroke: P.amber, titleColor: P.amberDark, titleSize: 12.5 });
  b += labelBox({ x: 214, y: 426, w: 244, h: 46, title: 'Multi-Head Attention', sub: '各位置按内容加权汇总上下文', fill: '#FFFFFF', stroke: P.blue, titleColor: P.blueDark, titleSize: 13.5 });

  // Add circle 1 (U)
  b += `<circle cx="336" cy="370" r="17" fill="${P.amberLight}" stroke="${P.amber}" stroke-width="2.2" />`;
  b += `<text x="336" y="376.5" text-anchor="middle" font-size="20" font-weight="700" fill="${P.amberDark}">+</text>`;
  b += `<text x="370" y="375" font-size="13" font-weight="700" fill="${P.text}">U = H⁽ˡ⁾ + MHA(Norm(H⁽ˡ⁾))</text>`;

  // Second sub-block: Norm -> FFN -> +
  b += box({ x: 178, y: 204, w: 344, h: 136, rx: 12, fill: P.violetPale, stroke: P.violetLight, sw: 1.4, dash: '5 3', shadow: false });
  b += `<text x="506" y="224" text-anchor="end" font-size="11" font-weight="700" fill="${P.violetDark}">子层 2：逐位置特征加工</text>`;
  b += labelBox({ x: 214, y: 286, w: 244, h: 40, title: 'Norm（独立可学习参数）', fill: P.amberPale, stroke: P.amber, titleColor: P.amberDark, titleSize: 12.5 });
  b += labelBox({ x: 214, y: 224, w: 244, h: 44, title: 'Position-wise FFN（如 SwiGLU）', sub: '对每一行独立做非线性变换', fill: '#FFFFFF', stroke: P.violet, titleColor: P.violetDark, titleSize: 13 });

  // Add circle 2 (H^{l+1})
  b += `<circle cx="336" cy="172" r="17" fill="${P.amberLight}" stroke="${P.amber}" stroke-width="2.2" />`;
  b += `<text x="336" y="178.5" text-anchor="middle" font-size="20" font-weight="700" fill="${P.amberDark}">+</text>`;
  b += `<text x="366" y="177" font-size="13" font-weight="700" fill="${P.emerald}">输出 H⁽ˡ⁺¹⁾ ∈ ℝ^(T × d)</text>`;

  // Arrows in main flow
  b += arrow(336, 582, 336, 536, { color: P.blue, marker: 'arr-blue', sw: 2 });
  b += arrow(336, 492, 336, 474, { color: P.blue, marker: 'arr-blue', sw: 2 });
  b += arrow(336, 426, 336, 390, { color: P.blue, marker: 'arr-blue', sw: 2 });
  b += arrow(336, 353, 336, 329, { color: P.violet, marker: 'arr-violet', sw: 2 });
  b += arrow(336, 286, 336, 271, { color: P.violet, marker: 'arr-violet', sw: 2 });
  b += arrow(336, 224, 336, 192, { color: P.violet, marker: 'arr-violet', sw: 2 });

  // Residual bypass arrows
  b += pathArrow('M 336 566 L 112 566 L 112 370 L 316 370', { color: P.amberDark, marker: 'arr-amber', sw: 2.2 });
  b += pathArrow('M 336 346 L 112 346 L 112 172 L 316 172', { color: P.amberDark, marker: 'arr-amber', sw: 2.2 });

  // Right Top Panel: SwiGLU FFN Zoom-In
  b += box({ x: 598, y: 100, w: 508, h: 278, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += pill({ x: 618, y: 116, w: 274, h: 26, fill: P.violetPale, stroke: P.violet, text: '展开：现代门控前馈网络 SwiGLU FFN', color: P.violetDark, fontSize: 12 });
  b += `<text x="618" y="164" font-size="13.5" font-weight="700" fill="${P.text}">FFN_SwiGLU(x) = [ SiLU(xW_g) ⊙ (xW_u) ] W_d</text>`;
  b += `<text x="618" y="183" font-size="11.5" fill="${P.textSec}">单条 token 向量 x ∈ ℝ^d 先升维到 d_ff，门控筛选后再映射回 d 维</text>`;

  // SwiGLU mini flow (left to right)
  b += labelBox({ x: 616, y: 244, w: 56, h: 52, title: 'x', sub: 'd 维', fill: P.bluePale, stroke: P.blue, titleColor: P.blueDark, titleSize: 14 });
  // Upper gate branch
  b += labelBox({ x: 706, y: 204, w: 84, h: 42, title: 'Linear W_g', sub: '升维 d_ff', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 11.5, subSize: 10 });
  b += labelBox({ x: 814, y: 204, w: 72, h: 42, title: 'SiLU', sub: '平滑门控', fill: P.amberPale, stroke: P.amber, titleColor: P.amberDark, titleSize: 12, subSize: 10 });
  // Lower value branch
  b += labelBox({ x: 706, y: 292, w: 180, h: 42, title: 'Linear W_u（待加工特征）', sub: '升维至 d_ff', fill: P.tealPale, stroke: P.teal, titleColor: P.tealDark, titleSize: 12, subSize: 10 });

  // Multiply node
  b += `<circle cx="932" cy="270" r="18" fill="${P.violetLight}" stroke="${P.violet}" stroke-width="2" />`;
  b += `<text x="932" y="276" text-anchor="middle" font-size="18" font-weight="700" fill="${P.violetDark}">⊙</text>`;

  // Down projection
  b += labelBox({ x: 976, y: 244, w: 110, h: 52, title: 'Linear W_d', sub: '降维回 d 维', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 12.5, subSize: 10.5 });

  // Arrows in SwiGLU
  b += pathArrow('M 672 260 L 688 260 L 688 225 L 703 225', { color: P.violet, marker: 'arr-violet', sw: 1.8 });
  b += pathArrow('M 672 280 L 688 280 L 688 313 L 703 313', { color: P.teal, marker: 'arr-teal', sw: 1.8 });
  b += arrow(790, 225, 811, 225, { color: P.violet, marker: 'arr-violet', sw: 1.8 });
  b += pathArrow('M 886 225 L 908 225 L 920 254', { color: P.amber, marker: 'arr-amber', sw: 1.8 });
  b += pathArrow('M 886 313 L 908 313 L 920 286', { color: P.teal, marker: 'arr-teal', sw: 1.8 });
  b += arrow(950, 270, 973, 270, { color: P.violet, marker: 'arr-violet', sw: 2 });
  b += `<text x="852" y="362" text-anchor="middle" font-size="11.5" fill="${P.textSec}">门控值按输入动态放大或抑制每个特征通道（Llama / Qwen / DeepSeek 广泛使用）</text>`;

  // Right Bottom Panel: Key Design Takeaways
  b += box({ x: 598, y: 398, w: 508, h: 248, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += pill({ x: 618, y: 414, w: 204, h: 26, fill: P.tealPale, stroke: P.teal, text: '为什么这样设计可以堆叠上百层？', color: P.tealDark, fontSize: 12 });

  const items = [
    { y: 468, tag: '1. 形状不变', col: P.blueDark, bg: P.bluePale, desc: '输入与输出始终保持 T × d，像乐高积木一样可以无缝堆叠 L 层（32~128 层）。' },
    { y: 526, tag: '2. 交替分工', col: P.violetDark, bg: P.violetPale, desc: 'Attention 让不同 Token 交换信息；FFN 在每个 Token 内部提炼与存储知识。' },
    { y: 584, tag: '3. Pre-Norm', col: P.amberDark, bg: P.amberPale, desc: '相比原始 Post-Norm，Pre-Norm 保持残差通路无阻碍，深层网络梯度更稳定。' },
  ];
  items.forEach((it) => {
    b += pill({ x: 618, y: it.y - 14, w: 96, h: 24, fill: it.bg, stroke: it.col, text: it.tag, color: it.col, fontSize: 11 });
    b += `<text x="726" y="${it.y + 3}" font-size="12.5" fill="${P.text}">${it.desc.slice(0, 23)}</text>`;
    b += `<text x="726" y="${it.y + 22}" font-size="12.5" fill="${P.textSec}">${it.desc.slice(23)}</text>`;
  });

  return wrapSvg({
    width, height,
    title: 'Transformer Block 内部结构：注意力、FFN、残差连接与 Norm',
    subtitle: '每个 Block 保持 T × d 形状不变，通过「残差累积 + 归一化稳定 + 注意力/FFN 交替」逐层精炼表示',
    badge: '§7.4 核心模块',
    body: b,
  });
}

// 07: Encoder-only, Encoder-decoder, Decoder-only
function fig07() {
  const width = 1160, height = 630;
  let b = '';

  function miniMask(x, y, mode, color) {
    const c = 18;
    let out = `<g>`;
    for (let i = 0; i < 4; i++) {
      for (let j = 0; j < 4; j++) {
        const active = mode === 'bi' ? true : j <= i;
        out += `<rect x="${x + j * c}" y="${y + i * c}" width="${c - 2}" height="${c - 2}" rx="3" fill="${active ? color : '#E2E8F0'}" fill-opacity="${active ? 0.78 : 0.7}" />`;
      }
    }
    out += `<text x="${x + 2 * c}" y="${y + 4 * c + 15}" text-anchor="middle" font-size="10.5" font-weight="600" fill="${P.textSec}">${mode === 'bi' ? '双向全可见' : '因果下三角'}</text>`;
    out += `</g>`;
    return out;
  }

  // Card 1: Encoder-only
  b += box({ x: 34, y: 102, w: 344, h: 494, rx: 14, fill: '#FFFFFF', stroke: P.blue, sw: 1.8 });
  b += `<rect x="34" y="102" width="344" height="46" rx="14" fill="${P.bluePale}" />`;
  b += `<rect x="34" y="134" width="344" height="14" fill="${P.bluePale}" />`;
  b += `<text x="206" y="132" text-anchor="middle" font-size="16" font-weight="700" fill="${P.blueDark}">1. Encoder-only（纯编码器）</text>`;

  // Architecture schematic
  b += labelBox({ x: 64, y: 178, w: 168, h: 44, title: '任务头（分类 / 向量）', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 12 });
  b += labelBox({ x: 64, y: 244, w: 168, h: 98, title: 'Encoder Stack × N', sub: '双向 Self-Attention + FFN', fill: P.bluePale, stroke: P.blue, titleColor: P.blueDark, titleSize: 13, subSize: 11 });
  b += pill({ x: 64, y: 368, w: 168, h: 30, fill: '#F8FAFC', stroke: P.border, text: '输入：整句文本 / 图像块', color: P.text, fontSize: 11.5 });
  b += arrow(148, 368, 148, 345, { color: P.blue, marker: 'arr-blue' });
  b += arrow(148, 244, 148, 225, { color: P.blue, marker: 'arr-blue' });
  // Mini mask
  b += miniMask(268, 250, 'bi', P.blue);

  b += `<line x1="56" y1="422" x2="356" y2="422" stroke="${P.borderLight}" />`;
  b += `<text x="56" y="448" font-size="12.5" font-weight="700" fill="${P.blueDark}">信息流动：每个位置都能看全文（双向）</text>`;
  b += `<text x="56" y="474" font-size="12.5" fill="${P.text}">• 代表模型：BERT、RoBERTa、ViT</text>`;
  b += `<text x="56" y="498" font-size="12.5" fill="${P.text}">• 擅长任务：文本分类、检索 Embedding、</text>`;
  b += `<text x="68" y="518" font-size="12.5" fill="${P.text}">情感分析、图像识别等理解类任务</text>`;
  b += pill({ x: 56, y: 546, w: 300, h: 28, fill: P.bluePale, stroke: P.blueLight, text: '核心优势：全局上下文表征能力强', color: P.blueDark, fontSize: 11.5 });

  // Card 2: Encoder-Decoder
  b += box({ x: 408, y: 102, w: 344, h: 494, rx: 14, fill: '#FFFFFF', stroke: P.teal, sw: 1.8 });
  b += `<rect x="408" y="102" width="344" height="46" rx="14" fill="${P.tealPale}" />`;
  b += `<rect x="408" y="134" width="344" height="14" fill="${P.tealPale}" />`;
  b += `<text x="580" y="132" text-anchor="middle" font-size="16" font-weight="700" fill="${P.tealDark}">2. Encoder–Decoder（编解码）</text>`;

  b += labelBox({ x: 432, y: 244, w: 122, h: 98, title: 'Encoder', sub: '双向读原文', fill: P.bluePale, stroke: P.blue, titleColor: P.blueDark, titleSize: 13, subSize: 11 });
  b += labelBox({ x: 598, y: 244, w: 130, h: 98, title: 'Decoder', sub: '因果 + 交叉注意', fill: P.tealPale, stroke: P.teal, titleColor: P.tealDark, titleSize: 13, subSize: 10.5 });
  b += pathArrow('M 554 292 L 595 292', { color: P.amberDark, marker: 'arr-amber', sw: 2.2 });
  b += `<text x="575" y="282" text-anchor="middle" font-size="10" font-weight="700" fill="${P.amberDark}">K,V</text>`;

  b += pill({ x: 432, y: 368, w: 122, h: 30, fill: '#F8FAFC', stroke: P.border, text: '源序列输入', color: P.text, fontSize: 11.5 });
  b += pill({ x: 598, y: 368, w: 130, h: 30, fill: '#F8FAFC', stroke: P.border, text: '已生成目标序列', color: P.text, fontSize: 11.5 });
  b += labelBox({ x: 598, y: 178, w: 130, h: 44, title: '预测下一词', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 12 });

  b += arrow(493, 368, 493, 345, { color: P.blue, marker: 'arr-blue' });
  b += arrow(663, 368, 663, 345, { color: P.teal, marker: 'arr-teal' });
  b += arrow(663, 244, 663, 225, { color: P.teal, marker: 'arr-teal' });

  b += `<line x1="430" y1="422" x2="730" y2="422" stroke="${P.borderLight}" />`;
  b += `<text x="430" y="448" font-size="12.5" font-weight="700" fill="${P.tealDark}">信息流动：源端双向读 + 目标端自回归写</text>`;
  b += `<text x="430" y="474" font-size="12.5" fill="${P.text}">• 代表模型：原始 Transformer、T5、BART</text>`;
  b += `<text x="430" y="498" font-size="12.5" fill="${P.text}">• 擅长任务：机器翻译、文档摘要、</text>`;
  b += `<text x="442" y="518" font-size="12.5" fill="${P.text}">语音转文字（Whisper）等 Seq2Seq 任务</text>`;
  b += pill({ x: 430, y: 546, w: 300, h: 28, fill: P.tealPale, stroke: P.tealLight, text: '核心优势：输入输出明确解耦，结构清晰', color: P.tealDark, fontSize: 11.5 });

  // Card 3: Decoder-only (Highlighted as Modern LLM mainstream)
  b += box({ x: 782, y: 102, w: 344, h: 494, rx: 14, fill: '#FFFFFF', stroke: P.violet, sw: 2.2 });
  b += `<rect x="782" y="102" width="344" height="46" rx="14" fill="${P.violetPale}" />`;
  b += `<rect x="782" y="134" width="344" height="14" fill="${P.violetPale}" />`;
  b += `<text x="954" y="132" text-anchor="middle" font-size="16" font-weight="700" fill="${P.violetDark}">3. Decoder-only（现代大模型主流）</text>`;

  b += labelBox({ x: 812, y: 178, w: 168, h: 44, title: '预测下一个 Token', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 12 });
  b += labelBox({ x: 812, y: 244, w: 168, h: 98, title: 'Decoder Stack × N', sub: '因果 Self-Attention + FFN', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 13, subSize: 11 });
  b += pill({ x: 812, y: 368, w: 168, h: 30, fill: '#F8FAFC', stroke: P.border, text: 'Prompt + 已生成内容', color: P.text, fontSize: 11.5 });
  b += arrow(896, 368, 896, 345, { color: P.violet, marker: 'arr-violet' });
  b += arrow(896, 244, 896, 225, { color: P.violet, marker: 'arr-violet' });
  // Mini mask
  b += miniMask(1016, 250, 'causal', P.violet);

  b += `<line x1="804" y1="422" x2="1104" y2="422" stroke="${P.borderLight}" />`;
  b += `<text x="804" y="448" font-size="12.5" font-weight="700" fill="${P.violetDark}">信息流动：Prompt 与回答统一为一条序列</text>`;
  b += `<text x="804" y="474" font-size="12.5" fill="${P.text}">• 代表模型：GPT、Llama、Qwen、DeepSeek</text>`;
  b += `<text x="804" y="498" font-size="12.5" fill="${P.text}">• 擅长任务：通用对话、代码、数学推理、</text>`;
  b += `<text x="816" y="518" font-size="12.5" fill="${P.text}">翻译与摘要几乎所有任务都能放进上下文</text>`;
  b += pill({ x: 804, y: 546, w: 300, h: 28, fill: P.violetPale, stroke: P.violetLight, text: '核心优势：极简统一、易于规模化 + KV Cache', color: P.violetDark, fontSize: 11.5 });

  return wrapSvg({
    width, height,
    title: 'Transformer 的三类主流架构对比',
    subtitle: '同样的 Transformer Block，按不同的注意力掩码与组织方式，衍生出三大模型家族',
    badge: '§7.4 架构家族',
    body: b,
  });
}

// 08: Autoregressive Generation
function fig08() {
  const width = 1140, height = 620;
  let b = '';

  const steps = [
    {
      step: 'Step 1',
      input: ['<bos>'],
      probs: [['我', 0.68], ['你', 0.14], ['今', 0.08]],
      picked: '我',
      y: 118,
    },
    {
      step: 'Step 2',
      input: ['<bos>', '我'],
      probs: [['喜', 0.52], ['想', 0.21], ['爱', 0.15]],
      picked: '喜',
      y: 224,
    },
    {
      step: 'Step 3',
      input: ['<bos>', '我', '喜'],
      probs: [['欢', 0.91], ['爱', 0.05], ['庆', 0.02]],
      picked: '欢',
      y: 330,
    },
    {
      step: 'Step 6（停止）',
      input: ['<bos>', '我', '喜', '欢', '学', '习'],
      probs: [['<eos>', 0.84], ['。', 0.10], ['！', 0.04]],
      picked: '<eos>',
      y: 454,
    },
  ];

  // Column headers
  b += `<text x="236" y="106" text-anchor="middle" font-size="13" font-weight="700" fill="${P.textSec}">当前上下文序列（越来越长）</text>`;
  b += `<text x="564" y="106" text-anchor="middle" font-size="13" font-weight="700" fill="${P.textSec}">模型前向计算</text>`;
  b += `<text x="772" y="106" text-anchor="middle" font-size="13" font-weight="700" fill="${P.textSec}">下一个 Token 概率分布</text>`;
  b += `<text x="1006" y="106" text-anchor="middle" font-size="13" font-weight="700" fill="${P.textSec}">采样并接回上下文</text>`;

  steps.forEach((st, idx) => {
    const isLast = idx === steps.length - 1;
    // Row background
    b += box({ x: 34, y: st.y, w: 1072, h: 86, rx: 12, fill: isLast ? P.emeraldPale : '#FFFFFF', stroke: isLast ? P.emerald : P.borderLight, sw: isLast ? 1.8 : 1.2 });

    // Step pill
    b += pill({ x: 48, y: st.y + 30, w: 96, h: 26, fill: isLast ? P.emerald : P.bluePale, stroke: isLast ? P.emerald : P.blue, text: st.step, color: isLast ? '#FFFFFF' : P.blueDark, fontSize: 11.5 });

    // Input token boxes
    st.input.forEach((tok, ti) => {
      const isNew = ti === st.input.length - 1 && idx > 0 && !isLast;
      const isSpecial = tok.startsWith('<');
      const tw = isSpecial ? 56 : 36;
      let tx = 160;
      for (let k = 0; k < ti; k++) tx += (st.input[k].startsWith('<') ? 56 : 36) + 6;
      b += box({
        x: tx, y: st.y + 24, w: tw, h: 38, rx: 7,
        fill: isNew ? P.amberLight : (isSpecial ? '#F1F5F9' : P.bluePale),
        stroke: isNew ? P.amber : (isSpecial ? P.slate : P.blue),
        sw: isNew ? 1.8 : 1.2, shadow: false
      });
      b += `<text x="${tx + tw / 2}" y="${st.y + 48}" text-anchor="middle" font-size="12.5" font-weight="700" fill="${isNew ? P.amberDark : P.text}">${esc(tok)}</text>`;
    });

    // Arrow to LLM
    b += arrow(452, st.y + 43, 494, st.y + 43, { color: P.slate, marker: 'arr-slate', sw: 2 });

    // LLM block
    b += labelBox({ x: 498, y: st.y + 18, w: 132, h: 50, title: 'Transformer', sub: 'p_θ(xₜ | x₁..ₜ₋₁)', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 13, subSize: 11 });

    // Arrow to probability distribution
    b += arrow(630, st.y + 43, 668, st.y + 43, { color: P.violet, marker: 'arr-violet', sw: 2 });

    // Mini probability bars (3 top candidates)
    st.probs.forEach(([cand, prob], pi) => {
      const py = st.y + 14 + pi * 21;
      const isTop = pi === 0;
      b += `<text x="716" y="${py + 12}" text-anchor="end" font-size="11.5" font-weight="${isTop ? 700 : 500}" fill="${isTop ? P.text : P.textSec}">${esc(cand)}</text>`;
      b += `<rect x="724" y="${py + 2}" width="116" height="12" rx="4" fill="#F1F5F9" />`;
      b += `<rect x="724" y="${py + 2}" width="${Math.round(prob * 116)}" height="12" rx="4" fill="${isTop ? (isLast ? P.emerald : P.blue) : '#94A3B8'}" />`;
      b += `<text x="846" y="${py + 12}" font-size="11" font-weight="${isTop ? 700 : 500}" fill="${isTop ? P.blueDark : P.textMuted}">${Math.round(prob * 100)}%</text>`;
    });

    // Arrow to picked token
    b += arrow(882, st.y + 43, 932, st.y + 43, { color: isLast ? P.emerald : P.amber, marker: isLast ? 'arr-emerald' : 'arr-amber', sw: 2 });

    // Picked token pill
    b += labelBox({
      x: 936, y: st.y + 20, w: 146, h: 46,
      title: isLast ? '输出 <eos> 结束' : `选中「${st.picked}」`,
      sub: isLast ? '生成完整回答！' : '追加到下一步输入末尾',
      fill: isLast ? P.emeraldLight : P.amberLight,
      stroke: isLast ? P.emerald : P.amber,
      titleColor: isLast ? P.tealDark : P.amberDark,
      titleSize: 13, subSize: 10.5
    });

    // Feedback connector arrow down-left to next step
    if (idx < 2) {
      b += pathArrow(`M 1009 ${st.y + 66} L 1009 ${st.y + 96} L 240 ${st.y + 96} L 240 ${steps[idx + 1].y + 22}`, { color: P.amber, marker: 'arr-amber', sw: 1.8, dash: '5 3' });
    }
  });

  // Ellipsis between Step 3 and Step 6
  b += `<text x="570" y="438" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.textMuted}">⋮   Step 4 生成「学」 · Step 5 生成「习」   ⋮</text>`;

  // Bottom summary bar
  b += noteBar({
    x: 34, y: 560, w: 1072, h: 40,
    text: '自回归（Autoregressive）的本质：把生成一整段文字拆成一连串“根据已有上文，预测下一个 Token”的循环，直到吐出结束符 <eos>。',
  });

  return wrapSvg({
    width, height,
    title: '自回归生成（Autoregressive Generation）：逐步吐词直到结束标记',
    subtitle: '训练时整句并行计算；生成时每步输出一个词并接回上下文，成为下一步的新输入',
    badge: '§7.5 自回归生成',
    body: b,
  });
}

// 09: Parallel Processing (Prefill) & KV Cache (Decode)
function fig09() {
  const width = 1160, height = 670;
  let b = '';

  // Top Panel: Phase 1 - Prefill (Parallel)
  b += box({ x: 34, y: 100, w: 1092, h: 214, rx: 14, fill: '#FFFFFF', stroke: P.blue, sw: 1.6 });
  b += pill({ x: 52, y: 114, w: 292, h: 26, fill: P.blue, stroke: P.blueDark, text: '阶段一：Prefill（预填充 · 并行处理全部 Prompt）', color: '#FFFFFF', fontSize: 12 });
  b += pill({ x: 834, y: 114, w: 274, h: 26, fill: P.bluePale, stroke: P.blueLight, text: '决定首字延迟 TTFT（Time To First Token）', color: P.blueDark, fontSize: 11.5 });

  // Prompt tokens in parallel
  const promptToks = ['我', '喜', '欢'];
  promptToks.forEach((tok, i) => {
    const ty = 158 + i * 48;
    b += pill({ x: 56, y: ty, w: 66, h: 34, fill: P.bluePale, stroke: P.blue, text: tok, color: P.blueDark, fontSize: 14 });
    b += arrow(124, ty + 17, 178, ty + 17, { color: P.blue, marker: 'arr-blue', sw: 1.8 });
  });

  // Big parallel block
  b += labelBox({ x: 182, y: 156, w: 230, h: 132, title: '并行计算所有 Q, K, V', sub: '一次矩阵乘法 + 因果掩码', fill: P.bluePale, stroke: P.blue, titleColor: P.blueDark, titleSize: 14.5, subSize: 12 });
  b += `<text x="297" y="256" text-anchor="middle" font-size="11.5" fill="${P.textSec}">同时产出 (K₁,V₁), (K₂,V₂), (K₃,V₃)</text>`;

  // Arrow into KV Cache bank
  b += arrow(414, 222, 488, 222, { color: P.teal, marker: 'arr-teal', sw: 2.4 });
  b += `<text x="451" y="210" text-anchor="middle" font-size="11" font-weight="700" fill="${P.tealDark}">写入缓存</text>`;

  // KV Cache Memory Bank (3 slots filled)
  b += box({ x: 492, y: 154, w: 334, h: 136, rx: 12, fill: P.tealPale, stroke: P.teal, sw: 1.8 });
  b += `<text x="659" y="178" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.tealDark}">显存中的 KV Cache（每层独立保存）</text>`;
  [['K₁, V₁', '（我）'], ['K₂, V₂', '（喜）'], ['K₃, V₃', '（欢）']].forEach(([kv, tok], i) => {
    b += box({ x: 510 + i * 102, y: 196, w: 94, h: 74, rx: 8, fill: '#FFFFFF', stroke: P.teal, sw: 1.4, shadow: false });
    b += `<text x="${557 + i * 102}" y="227" text-anchor="middle" font-size="12.5" font-weight="700" fill="${P.tealDark}">${kv}</text>`;
    b += `<text x="${557 + i * 102}" y="251" text-anchor="middle" font-size="11.5" fill="${P.textSec}">${tok}</text>`;
  });

  // Output first token
  b += arrow(828, 222, 888, 222, { color: P.emerald, marker: 'arr-emerald', sw: 2.4 });
  b += labelBox({ x: 892, y: 184, w: 210, h: 76, title: '吐出第 1 个生成词「学」', sub: 'Prefill 结束，进入 Decode 循环', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 13.5, subSize: 11 });

  // Bottom Panel: Phase 2 - Decode with KV Cache
  b += box({ x: 34, y: 332, w: 1092, h: 244, rx: 14, fill: '#FFFFFF', stroke: P.violet, sw: 1.8 });
  b += pill({ x: 52, y: 346, w: 320, h: 26, fill: P.violet, stroke: P.violetDark, text: '阶段二：Decode（解码 · 借助 KV Cache 逐词生成）', color: '#FFFFFF', fontSize: 12 });
  b += pill({ x: 834, y: 346, w: 274, h: 26, fill: P.violetPale, stroke: P.violetLight, text: '决定生成速度 TPOT（每词生成耗时）', color: P.violetDark, fontSize: 11.5 });

  // Single new token input
  b += labelBox({ x: 54, y: 422, w: 108, h: 72, title: '仅新词「学」', sub: 't = 4', fill: P.amberLight, stroke: P.amber, titleColor: P.amberDark, titleSize: 13.5 });
  b += arrow(164, 458, 212, 458, { color: P.amber, marker: 'arr-amber', sw: 2.2 });

  // Compute ONLY q4, k4, v4
  b += labelBox({ x: 216, y: 406, w: 176, h: 104, title: '只算新位置的 q₄, k₄, v₄', sub: '历史 1..3 绝不重复计算！', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 13, subSize: 11.5 });

  // KV Cache reused + appended slot
  b += box({ x: 432, y: 392, w: 378, h: 106, rx: 12, fill: P.tealPale, stroke: P.teal, sw: 1.6 });
  b += `<text x="621" y="413" text-anchor="middle" font-size="12" font-weight="700" fill="${P.tealDark}">直接复用历史 KV（省去 O(T) 重算）  +  追加新槽位</text>`;
  ['K₁,V₁', 'K₂,V₂', 'K₃,V₃'].forEach((lbl, i) => {
    b += box({ x: 446 + i * 86, y: 426, w: 78, h: 56, rx: 7, fill: '#FFFFFF', stroke: P.teal, sw: 1.3, shadow: false });
    b += `<text x="${485 + i * 86}" y="451" text-anchor="middle" font-size="12" font-weight="700" fill="${P.tealDark}">${lbl}</text>`;
    b += `<text x="${485 + i * 86}" y="470" text-anchor="middle" font-size="10" fill="${P.textMuted}">已缓存复用</text>`;
  });
  // New appended slot k4,v4
  b += box({ x: 704, y: 426, w: 92, h: 56, rx: 7, fill: P.amberLight, stroke: P.amber, sw: 2, shadow: false });
  b += `<text x="750" y="451" text-anchor="middle" font-size="12" font-weight="700" fill="${P.amberDark}">k₄, v₄</text>`;
  b += `<text x="750" y="470" text-anchor="middle" font-size="10" font-weight="700" fill="${P.amberDark}">新追加！</text>`;

  // Branch k4, v4 to append to KV Cache (drawn on top for crisp arrowhead)
  b += pathArrow('M 392 486 L 414 486 L 414 522 L 750 522 L 750 485', { color: P.amber, marker: 'arr-amber', sw: 2.2 });
  b += `<text x="582" y="541" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.amberDark}">将新的 (k₄, v₄) 追加到缓存末尾</text>`;

  // q4 attends to all K1..K4, V1..V4
  b += pathArrow('M 392 432 L 414 432 L 414 380 L 844 380 L 844 430 L 866 430', { color: P.blue, marker: 'arr-blue', sw: 2 });
  b += `<text x="624" y="374" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.blueDark}">用 q₄ 一次性读取全部缓存 [K₁..K₄, V₁..V₄]</text>`;
  b += arrow(810, 456, 866, 456, { color: P.teal, marker: 'arr-teal', sw: 2.2 });

  // Output next token
  b += labelBox({ x: 870, y: 406, w: 232, h: 92, title: 'Attention(q₄, K₁..₄, V₁..₄)', sub: '预测下一个词「习」→ 继续循环', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 13, subSize: 11.5 });

  // Bottom Formula Bar (Memory cost)
  b += box({ x: 34, y: 594, w: 1092, h: 52, rx: 10, fill: P.amberPale, stroke: P.amberLight, shadow: false });
  b += `<text x="54" y="617" font-size="13" font-weight="700" fill="${P.amberDark}">💾 显存代价估算：KV Cache ≈ 2 · B · L · T · H_kv · d_head · b</text>`;
  b += `<text x="54" y="636" font-size="12" fill="${P.text}">例：B=1, L=32层, T=8192, H_kv=8 (GQA), d_head=128, FP16(2字节) → 约占 1 GiB；用 GQA / MQA 减少 KV 头数可大幅省显存！</text>`;

  return wrapSvg({
    width, height,
    title: '并行预填充（Prefill）与 KV Cache 增量解码（Decode）',
    subtitle: '以空间换时间：把历史位置算好的 Key 和 Value 存进显存，每生成一个新词都无需重算前文',
    badge: '§7.5 推理加速',
    body: b,
  });
}

// 25: Batching Throughput vs P95 Latency
function fig25() {
  const width = 1140, height = 600;
  let b = '';

  // Left Panel: Hardware intuition (Batch=1 vs Batch=N)
  b += box({ x: 34, y: 102, w: 462, h: 462, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += `<text x="56" y="132" font-size="15.5" font-weight="700" fill="${P.text}">为什么合批（Batching）能省钱？</text>`;
  b += `<text x="56" y="152" font-size="12" fill="${P.textSec}">Decode 阶段瓶颈在「显存带宽」而非算力</text>`;

  // Case A: Batch = 1
  b += box({ x: 54, y: 172, w: 422, h: 162, rx: 12, fill: P.rosePale, stroke: P.roseLight, shadow: false });
  b += pill({ x: 68, y: 184, w: 186, h: 24, fill: P.rose, stroke: P.roseDark, text: 'Batch = 1（单条请求）', color: '#FFFFFF', fontSize: 11.5 });
  b += labelBox({ x: 68, y: 222, w: 138, h: 52, title: '搬运整个模型权重', sub: '数十 GB 从 HBM 读入', fill: '#FFFFFF', stroke: P.rose, titleColor: P.roseDark, titleSize: 12, subSize: 10.5 });
  b += arrow(208, 248, 250, 248, { color: P.rose, marker: 'arr-rose', sw: 2 });
  b += labelBox({ x: 254, y: 222, w: 114, h: 52, title: '仅算 1 个 token', sub: '矩阵-向量乘', fill: '#FFFFFF', stroke: P.border, titleColor: P.text, titleSize: 12, subSize: 10.5 });
  // GPU utilization meter
  b += `<text x="68" y="302" font-size="11.5" font-weight="700" fill="${P.roseDark}">GPU 算力利用率：~12%</text>`;
  b += `<rect x="218" y="290" width="240" height="14" rx="7" fill="#FFFFFF" stroke="${P.roseLight}" />`;
  b += `<rect x="218" y="290" width="32" height="14" rx="7" fill="${P.rose}" />`;
  b += `<text x="68" y="322" font-size="11.5" fill="${P.textSec}">绝大部分时间都在空等数据搬运，单位 token 成本极高</text>`;

  // Case B: Batch = N
  b += box({ x: 54, y: 354, w: 422, h: 188, rx: 12, fill: P.emeraldPale, stroke: P.emeraldLight, shadow: false });
  b += pill({ x: 68, y: 366, w: 222, h: 24, fill: P.emerald, stroke: P.tealDark, text: 'Batch = N（多条请求合批并行）', color: '#FFFFFF', fontSize: 11.5 });
  b += labelBox({ x: 68, y: 404, w: 138, h: 64, title: '权重仍只搬运 1 次！', sub: '多条请求摊薄带宽开销', fill: '#FFFFFF', stroke: P.emerald, titleColor: P.tealDark, titleSize: 12, subSize: 10.5 });
  b += arrow(208, 436, 250, 436, { color: P.emerald, marker: 'arr-emerald', sw: 2.2 });
  // Stacked tokens
  for (let k = 0; k < 4; k++) {
    b += `<rect x="${254 + k * 5}" y="${404 + k * 6}" width="188" height="42" rx="7" fill="#FFFFFF" stroke="${P.teal}" stroke-width="1.4" />`;
  }
  b += `<text x="364" y="440" text-anchor="middle" font-size="12" font-weight="700" fill="${P.tealDark}">同时算 N 条请求的 token</text>`;
  b += `<text x="364" y="457" text-anchor="middle" font-size="10.5" fill="${P.textSec}">矩阵-矩阵乘（算术强度大增）</text>`;

  b += `<text x="68" y="504" font-size="11.5" font-weight="700" fill="${P.tealDark}">GPU 算力利用率：~75%</text>`;
  b += `<rect x="218" y="492" width="240" height="14" rx="7" fill="#FFFFFF" stroke="${P.tealLight}" />`;
  b += `<rect x="218" y="492" width="182" height="14" rx="7" fill="${P.emerald}" />`;
  b += `<text x="68" y="528" font-size="11.5" fill="${P.textSec}">总吞吐暴涨，但单请求要排队等凑批 + 单步变慢 → 延迟上升</text>`;

  // Right Panel: Dual-axis Chart (Batch Size vs Throughput & P95 Latency)
  b += box({ x: 520, y: 102, w: 586, h: 462, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += `<text x="546" y="132" font-size="15.5" font-weight="700" fill="${P.text}">吞吐量（Throughput）与 P95 延迟的权衡曲线</text>`;
  b += `<text x="546" y="152" font-size="12" fill="${P.textSec}">同一块 GPU，服务商按不同 Batch 区间切出 Fast 模式与标准模式</text>`;

  const cx = 588, cy = 192, cw = 446, ch = 266;
  // Shaded operating zones
  b += `<rect x="${cx}" y="${cy}" width="112" height="${ch}" fill="${P.bluePale}" fill-opacity="0.7" />`;
  b += `<rect x="${cx + 224}" y="${cy}" width="142" height="${ch}" fill="${P.emeraldPale}" fill-opacity="0.7" />`;
  b += `<text x="${cx + 56}" y="${cy + 22}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.blueDark}">Fast 模式区</text>`;
  b += `<text x="${cx + 56}" y="${cy + 38}" text-anchor="middle" font-size="10.5" fill="${P.textSec}">低延迟 · 单价高</text>`;
  b += `<text x="${cx + 295}" y="${cy + 16}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.tealDark}">标准模式区</text>`;
  b += `<text x="${cx + 295}" y="${cy + 31}" text-anchor="middle" font-size="10.5" fill="${P.textSec}">高吞吐 · 成本低</text>`;

  // Grid lines
  for (let i = 0; i <= 4; i++) {
    const gy = cy + (i / 4) * ch;
    b += `<line x1="${cx}" y1="${gy}" x2="${cx + cw}" y2="${gy}" stroke="#E2E8F0" stroke-dasharray="3 3" />`;
  }
  // Axes
  b += `<line x1="${cx}" y1="${cy + ch}" x2="${cx + cw}" y2="${cy + ch}" stroke="${P.slate}" stroke-width="1.8" />`;
  b += `<line x1="${cx}" y1="${cy}" x2="${cx}" y2="${cy + ch}" stroke="${P.blue}" stroke-width="2" />`;
  b += `<line x1="${cx + cw}" y1="${cy}" x2="${cx + cw}" y2="${cy + ch}" stroke="${P.rose}" stroke-width="2" />`;

  // Axis titles
  b += `<text x="${cx - 10}" y="${cy - 8}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.blueDark}">总吞吐</text>`;
  b += `<text x="${cx + cw + 6}" y="${cy - 8}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.roseDark}">P95 延迟</text>`;
  b += `<text x="${cx + cw / 2}" y="${cy + ch + 38}" text-anchor="middle" font-size="12.5" font-weight="700" fill="${P.text}">批次大小（Batch Size）→</text>`;

  // X ticks
  ['1', '8', '32', '64', '128', '256'].forEach((lbl, i) => {
    const tx = cx + (i / 5) * cw;
    b += `<text x="${tx}" y="${cy + ch + 18}" text-anchor="middle" font-size="11" fill="${P.textMuted}">${lbl}</text>`;
  });

  // Throughput curve (smooth concave saturating: 1 - exp(-k*t))
  let tpD = '';
  for (let i = 0; i <= 80; i++) {
    const t = i / 80;
    const v = 0.07 + 0.78 * (1 - Math.exp(-3.8 * t));
    const px = cx + t * cw, py = cy + ch - v * (ch - 26);
    tpD += (i === 0 ? 'M ' : ' L ') + px.toFixed(1) + ' ' + py.toFixed(1);
  }
  b += `<path d="${tpD}" fill="none" stroke="${P.blue}" stroke-width="3.2" stroke-linecap="round" />`;
  [0, 0.2, 0.4, 0.6, 0.8, 1.0].forEach((t) => {
    const v = 0.07 + 0.78 * (1 - Math.exp(-3.8 * t));
    b += `<circle cx="${(cx + t * cw).toFixed(1)}" cy="${(cy + ch - v * (ch - 26)).toFixed(1)}" r="4.5" fill="#FFFFFF" stroke="${P.blue}" stroke-width="2.2" />`;
  });

  // Saturation ceiling dashed line (cleanly below "标准模式区" header)
  const ceilY = cy + ch - 0.87 * (ch - 26);
  b += `<line x1="${cx + 205}" y1="${ceilY.toFixed(1)}" x2="${cx + cw - 4}" y2="${ceilY.toFixed(1)}" stroke="${P.blue}" stroke-width="1.3" stroke-dasharray="5 3" />`;
  b += `<rect x="${cx + 236}" y="${(ceilY - 17).toFixed(1)}" width="194" height="16" rx="4" fill="#FFFFFF" fill-opacity="0.88" />`;
  b += `<text x="${cx + cw - 12}" y="${(ceilY - 5).toFixed(1)}" text-anchor="end" font-size="10.5" font-weight="600" fill="${P.blueDark}">算力/带宽上限（继续增大无收益）</text>`;

  // P95 Latency curve (smooth convex rising: 0.08 + 0.86 * t^2.3)
  let latD = '';
  for (let i = 0; i <= 80; i++) {
    const t = i / 80;
    const v = 0.08 + 0.86 * Math.pow(t, 2.3);
    const px = cx + t * cw, py = cy + ch - v * (ch - 26);
    latD += (i === 0 ? 'M ' : ' L ') + px.toFixed(1) + ' ' + py.toFixed(1);
  }
  b += `<path d="${latD}" fill="none" stroke="${P.rose}" stroke-width="3.2" stroke-linecap="round" />`;
  [0, 0.2, 0.4, 0.6, 0.8, 1.0].forEach((t) => {
    const v = 0.08 + 0.86 * Math.pow(t, 2.3);
    b += `<circle cx="${(cx + t * cw).toFixed(1)}" cy="${(cy + ch - v * (ch - 26)).toFixed(1)}" r="4.5" fill="#FFFFFF" stroke="${P.rose}" stroke-width="2.2" />`;
  });

  // Legend below chart
  b += `<line x1="590" y1="528" x2="622" y2="528" stroke="${P.blue}" stroke-width="3.2" stroke-linecap="round" />`;
  b += `<text x="630" y="532" font-size="12" font-weight="700" fill="${P.blueDark}">总吞吐（tokens/s）— 越高越省钱</text>`;
  b += `<line x1="852" y1="528" x2="884" y2="528" stroke="${P.rose}" stroke-width="3.2" stroke-linecap="round" />`;
  b += `<text x="892" y="532" font-size="12" font-weight="700" fill="${P.roseDark}">P95 延迟（ms）— 越低越快</text>`;

  return wrapSvg({
    width, height,
    title: '推理服务中的合批（Batching）：高吞吐与低延迟的权衡',
    subtitle: '把多条请求合批可把权重搬运开销分摊给更多 token，但会拉长排队等待和单步计算时间',
    badge: '§7.5 推理系统',
    body: b,
  });
}

// Helper to render crisp 7x7 pixelated digit icon
function pixelDigit(x, y, size, grid, color = '#0F172A', noisy = false, soft = false) {
  const cell = size / 7;
  const rand = seededRand(42);
  let out = `<rect x="${x}" y="${y}" width="${size}" height="${size}" rx="8" fill="#0F172A" stroke="${P.border}" stroke-width="1.5" />`;
  for (let r = 0; r < 7; r++) {
    for (let c = 0; c < 7; c++) {
      let val = grid[r][c];
      if (soft && val === 0) val = 0.08;
      if (soft && val > 0) val = Math.min(1, val * 0.85);
      if (noisy) {
        const n = rand();
        if (n < 0.24) val = 0.78;
        else if (n < 0.36) val = 0.1;
      }
      if (val > 0.04) {
        out += `<rect x="${(x + c * cell + 1.5).toFixed(1)}" y="${(y + r * cell + 1.5).toFixed(1)}" width="${(cell - 3).toFixed(1)}" height="${(cell - 3).toFixed(1)}" rx="2" fill="${color}" fill-opacity="${val.toFixed(2)}" />`;
      }
    }
  }
  return out;
}

const DIGIT_7 = [
  [0, 1, 1, 1, 1, 1, 0],
  [0, 0, 0, 0, 1, 1, 0],
  [0, 0, 0, 1, 1, 0, 0],
  [0, 0, 1, 1, 0, 0, 0],
  [0, 0, 1, 1, 0, 0, 0],
  [0, 1, 1, 0, 0, 0, 0],
  [0, 1, 1, 0, 0, 0, 0],
];

const DIGIT_3 = [
  [0, 1, 1, 1, 1, 0, 0],
  [0, 0, 0, 0, 1, 1, 0],
  [0, 0, 0, 0, 1, 1, 0],
  [0, 0, 1, 1, 1, 0, 0],
  [0, 0, 0, 0, 1, 1, 0],
  [0, 0, 0, 0, 1, 1, 0],
  [0, 1, 1, 1, 1, 0, 0],
];

// 10: Autoencoder Reconstruction
function fig10() {
  const width = 1140, height = 560;
  let b = '';

  // Input image x
  b += `<text x="116" y="136" text-anchor="middle" font-size="14" font-weight="700" fill="${P.text}">输入图像 x</text>`;
  b += `<text x="116" y="155" text-anchor="middle" font-size="11.5" fill="${P.textSec}">28×28 = 784 维</text>`;
  b += pixelDigit(64, 174, 104, DIGIT_7, '#60A5FA');

  b += arrow(174, 226, 224, 226, { color: P.blue, marker: 'arr-blue', sw: 2.4 });

  // Encoder trapezoid
  b += `<path d="M 230 138 L 466 184 L 466 268 L 230 314 Z" fill="${P.bluePale}" stroke="${P.blue}" stroke-width="2" filter="url(#shadow-sm)" />`;
  b += `<text x="348" y="218" text-anchor="middle" font-size="16" font-weight="700" fill="${P.blueDark}">Encoder  f_φ(x)</text>`;
  b += `<text x="348" y="242" text-anchor="middle" font-size="12" fill="${P.textSec}">逐层压缩提取共同结构</text>`;
  b += `<text x="348" y="260" text-anchor="middle" font-size="11" fill="${P.blue}">(MLP / CNN / Transformer)</text>`;

  b += arrow(468, 226, 514, 226, { color: P.violet, marker: 'arr-violet', sw: 2.4 });

  // Bottleneck Latent z
  b += box({ x: 518, y: 158, w: 104, h: 136, rx: 12, fill: P.amberPale, stroke: P.amber, sw: 2.4 });
  b += `<text x="570" y="182" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.amberDark}">潜在表示 z</text>`;
  b += `<text x="570" y="200" text-anchor="middle" font-size="11.5" font-weight="600" fill="${P.amber}">16 维瓶颈</text>`;
  b += vecBars({ x: 540, y: 212, vals: [0.9, 0.35, 0.75, 0.55], cellW: 13, cellH: 36, color: P.amber });
  b += `<text x="570" y="274" text-anchor="middle" font-size="10.5" font-weight="700" fill="${P.amberDark}">Bottleneck</text>`;

  b += arrow(624, 226, 670, 226, { color: P.teal, marker: 'arr-teal', sw: 2.4 });

  // Decoder trapezoid
  b += `<path d="M 674 184 L 910 138 L 910 314 L 674 268 Z" fill="${P.tealPale}" stroke="${P.teal}" stroke-width="2" filter="url(#shadow-sm)" />`;
  b += `<text x="792" y="218" text-anchor="middle" font-size="16" font-weight="700" fill="${P.tealDark}">Decoder  g_θ(z)</text>`;
  b += `<text x="792" y="242" text-anchor="middle" font-size="12" fill="${P.textSec}">从压缩向量恢复图像</text>`;
  b += `<text x="792" y="260" text-anchor="middle" font-size="11" fill="${P.teal}">尝试还原笔画、位置、粗细</text>`;

  b += arrow(912, 226, 962, 226, { color: P.teal, marker: 'arr-teal', sw: 2.4 });

  // Reconstructed output x_hat
  b += `<text x="1024" y="136" text-anchor="middle" font-size="14" font-weight="700" fill="${P.text}">重建图像 x̂</text>`;
  b += `<text x="1024" y="155" text-anchor="middle" font-size="11.5" fill="${P.textSec}">28×28 = 784 维</text>`;
  b += pixelDigit(972, 174, 104, DIGIT_7, '#34D399', false, true);

  // Reconstruction loss arc underneath connecting x and x_hat
  b += `<path d="M 116 286 L 116 376 L 414 376" fill="none" stroke="${P.rose}" stroke-width="2" stroke-dasharray="5 3" marker-end="url(#arr-rose)" />`;
  b += `<path d="M 1024 286 L 1024 376 L 726 376" fill="none" stroke="${P.rose}" stroke-width="2" stroke-dasharray="5 3" marker-end="url(#arr-rose)" />`;
  b += labelBox({ x: 418, y: 344, w: 304, h: 62, title: '重建损失  L_AE = ‖x − x̂‖²', sub: '无监督学习：输入图像本身就是监督目标！', fill: P.rosePale, stroke: P.rose, titleColor: P.roseDark, titleSize: 14, subSize: 11.5 });

  // Bottom two usage cards
  b += box({ x: 38, y: 432, w: 522, h: 98, rx: 12, fill: '#FFFFFF', stroke: P.blueLight, sw: 1.5 });
  b += pill({ x: 54, y: 446, w: 174, h: 24, fill: P.bluePale, stroke: P.blue, text: '用法 1 · 保留 Encoder', color: P.blueDark, fontSize: 11.5 });
  b += `<text x="54" y="492" font-size="13" fill="${P.text}">把高维数据压缩成低维特征 z，用于可视化、聚类、检索，</text>`;
  b += `<text x="54" y="514" font-size="13" fill="${P.textSec}">或作为下游分类、回归任务的高质量表示（非线性版 PCA）。</text>`;

  b += box({ x: 580, y: 432, w: 522, h: 98, rx: 12, fill: '#FFFFFF', stroke: P.tealLight, sw: 1.5 });
  b += pill({ x: 596, y: 446, w: 194, h: 24, fill: P.tealPale, stroke: P.teal, text: '用法 2 · 利用重建与残差', color: P.tealDark, fontSize: 11.5 });
  b += `<text x="596" y="492" font-size="13" fill="${P.text}">利用 Decoder 去噪、补全；在正常样本上训练后，</text>`;
  b += `<text x="596" y="514" font-size="13" fill="${P.textSec}">若新样本重建误差 ‖x−x̂‖² 很大，往往意味着出现了异常！</text>`;

  return wrapSvg({
    width, height,
    title: '自编码器（Autoencoder）：通过「压缩—重建」学习紧凑表示',
    subtitle: '低维瓶颈强迫模型丢弃无关冗余，只保留能够恢复原始数据的核心结构信息',
    badge: '§8.1 表示学习',
    body: b,
  });
}

// 11: Denoising Autoencoder
function fig11() {
  const width = 1140, height = 520;
  let b = '';

  // Clean input x
  b += `<text x="98" y="156" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.text}">干净原图 x</text>`;
  b += pixelDigit(52, 170, 92, DIGIT_3, '#60A5FA');

  // Corrupt arrow + badge
  b += arrow(150, 216, 224, 216, { color: P.rose, marker: 'arr-rose', sw: 2.2 });
  b += pill({ x: 152, y: 180, w: 72, h: 24, fill: P.roseLight, stroke: P.rose, text: '+ 噪声扰动', color: P.roseDark, fontSize: 11 });

  // Noisy input x_tilde
  b += `<text x="276" y="156" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.roseDark}">受扰动输入 x̃</text>`;
  b += pixelDigit(230, 170, 92, DIGIT_3, '#FB7185', true);

  b += arrow(328, 216, 372, 216, { color: P.blue, marker: 'arr-blue', sw: 2.2 });

  // Encoder
  b += `<path d="M 376 146 L 542 182 L 542 250 L 376 286 Z" fill="${P.bluePale}" stroke="${P.blue}" stroke-width="2" filter="url(#shadow-sm)" />`;
  b += `<text x="459" y="212" text-anchor="middle" font-size="15" font-weight="700" fill="${P.blueDark}">Encoder f_φ</text>`;
  b += `<text x="459" y="234" text-anchor="middle" font-size="11.5" fill="${P.textSec}">过滤噪声，提取主干</text>`;

  b += arrow(544, 216, 582, 216, { color: P.amber, marker: 'arr-amber', sw: 2.2 });

  // Latent z
  b += box({ x: 586, y: 168, w: 78, h: 96, rx: 10, fill: P.amberPale, stroke: P.amber, sw: 2 });
  b += `<text x="625" y="192" text-anchor="middle" font-size="13" font-weight="700" fill="${P.amberDark}">表示 z</text>`;
  b += vecBars({ x: 601, y: 204, vals: [0.85, 0.4, 0.9], cellW: 13, cellH: 42, color: P.amber });

  b += arrow(666, 216, 704, 216, { color: P.teal, marker: 'arr-teal', sw: 2.2 });

  // Decoder
  b += `<path d="M 708 182 L 874 146 L 874 286 L 708 250 Z" fill="${P.tealPale}" stroke="${P.teal}" stroke-width="2" filter="url(#shadow-sm)" />`;
  b += `<text x="791" y="212" text-anchor="middle" font-size="15" font-weight="700" fill="${P.tealDark}">Decoder g_θ</text>`;
  b += `<text x="791" y="234" text-anchor="middle" font-size="11.5" fill="${P.textSec}">还原干净图像</text>`;

  b += arrow(876, 216, 922, 216, { color: P.emerald, marker: 'arr-emerald', sw: 2.2 });

  // Clean reconstructed x_hat
  b += `<text x="974" y="156" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.tealDark}">去噪输出 x̂</text>`;
  b += pixelDigit(928, 170, 92, DIGIT_3, '#34D399');

  // Key difference arc: compare x_hat with ORIGINAL CLEAN x (NOT noisy x_tilde!)
  b += `<path d="M 98 268 L 98 378 L 414 378" fill="none" stroke="${P.emerald}" stroke-width="2.4" stroke-dasharray="6 3" marker-end="url(#arr-emerald)" />`;
  b += `<path d="M 974 268 L 974 378 L 726 378" fill="none" stroke="${P.emerald}" stroke-width="2.4" stroke-dasharray="6 3" marker-end="url(#arr-emerald)" />`;

  b += labelBox({
    x: 418, y: 342, w: 304, h: 72,
    title: '关键对比：L = ‖ 干净原图 x − 重建 x̂ ‖²',
    sub: '绝不是去拟合噪声输入 x̃，而是逼迫网络学会“数据流形”',
    fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 13.5, subSize: 11
  });

  // Annotation callout
  b += noteBar({
    x: 34, y: 446, w: 1072, h: 44,
    text: '直觉桥梁：这种“人为加噪 → 训练网络恢复干净原图”的思想，进一步推广到多级噪声迭代，就引出了 §8.4 的扩散模型（Diffusion）！',
  });

  return wrapSvg({
    width, height,
    title: '去噪自编码器（Denoising Autoencoder）：从扰动输入恢复干净结构',
    subtitle: '主动破坏输入、但用干净原图做目标，促使网络学习数据中稳定且抗干扰的本质特征',
    badge: '§8.1 去噪自编码',
    body: b,
  });
}

// 12: Masked Autoencoder (MAE)
function fig12() {
  const width = 1160, height = 560;
  let b = '';

  // Helper to draw 4x4 patch grid of a simple scenic illustration (sun + sky + mountains + lake)
  const patchColors = [
    '#93C5FD', '#93C5FD', '#FDE047', '#93C5FD',
    '#BFDBFE', '#60A5FA', '#93C5FD', '#BFDBFE',
    '#60A5FA', '#34D399', '#10B981', '#059669',
    '#3B82F6', '#047857', '#065F46', '#1D4ED8',
  ];
  const visibleIdx = new Set([2, 5, 10, 14]); // 4 visible out of 16 = 25% visible, 75% masked!

  function patchGrid(x, y, mode) {
    const c = 34, gap = 3;
    let out = `<g>`;
    for (let i = 0; i < 16; i++) {
      const r = Math.floor(i / 4), col = i % 4;
      const px = x + col * (c + gap), py = y + r * (c + gap);
      const isVis = visibleIdx.has(i);
      if (mode === 'orig') {
        out += `<rect x="${px}" y="${py}" width="${c}" height="${c}" rx="4" fill="${patchColors[i]}" stroke="#FFFFFF" stroke-width="1" />`;
      } else if (mode === 'masked') {
        out += `<rect x="${px}" y="${py}" width="${c}" height="${c}" rx="4" fill="${isVis ? patchColors[i] : '#CBD5E1'}" stroke="${isVis ? P.blue : '#94A3B8'}" stroke-width="${isVis ? 2 : 1}" />`;
        if (!isVis) {
          out += `<text x="${px + c / 2}" y="${py + 21}" text-anchor="middle" font-size="11" fill="#64748B">?</text>`;
        }
      } else if (mode === 'recon') {
        out += `<rect x="${px}" y="${py}" width="${c}" height="${c}" rx="4" fill="${patchColors[i]}" fill-opacity="${isVis ? 0.55 : 0.95}" stroke="${isVis ? '#94A3B8' : P.rose}" stroke-width="${isVis ? 1 : 2}" />`;
      }
    }
    out += `</g>`;
    return out;
  }

  // Step 1: Original Image -> 4x4 Patches
  b += `<text x="110" y="138" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.text}">① 图像切分为 Patch</text>`;
  b += `<text x="110" y="156" text-anchor="middle" font-size="11.5" fill="${P.textSec}">共 16 个图像块</text>`;
  b += patchGrid(38, 174, 'orig');

  b += arrow(190, 248, 250, 248, { color: P.rose, marker: 'arr-rose', sw: 2.2 });
  b += `<text x="220" y="232" text-anchor="middle" font-size="11" font-weight="700" fill="${P.roseDark}">随机遮住</text>`;
  b += `<text x="220" y="268" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.roseDark}">75%</text>`;

  // Step 2: 75% Masked Grid
  b += `<text x="326" y="138" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.roseDark}">② 随机高比例遮挡</text>`;
  b += `<text x="326" y="156" text-anchor="middle" font-size="11.5" fill="${P.textSec}">仅剩 4 个可见块 (25%)</text>`;
  b += patchGrid(254, 174, 'masked');

  // Arrow picking ONLY the 4 visible patches into ViT Encoder
  b += arrow(406, 248, 444, 248, { color: P.blue, marker: 'arr-blue', sw: 2.2 });
  b += `<text x="425" y="232" text-anchor="middle" font-size="10.5" font-weight="700" fill="${P.blueDark}">仅送入</text>`;
  b += `<text x="425" y="268" text-anchor="middle" font-size="10.5" font-weight="700" fill="${P.blueDark}">可见块</text>`;

  // Step 3: ViT Encoder (processes ONLY 4 visible patches!)
  b += box({ x: 448, y: 162, w: 182, h: 172, rx: 14, fill: P.bluePale, stroke: P.blue, sw: 2 });
  b += `<text x="539" y="188" text-anchor="middle" font-size="14.5" font-weight="700" fill="${P.blueDark}">ViT Encoder</text>`;
  b += `<text x="539" y="208" text-anchor="middle" font-size="11.5" fill="${P.textSec}">只处理 25% 可见块</text>`;
  // Show the 4 visible blocks neatly inside
  [2, 5, 10, 14].forEach((pi, k) => {
    b += `<rect x="${468 + k * 38}" y="226" width="28" height="28" rx="5" fill="${patchColors[pi]}" stroke="${P.blueDark}" stroke-width="1.5" />`;
  });
  b += pill({ x: 466, y: 274, w: 146, h: 24, fill: '#FFFFFF', stroke: P.blue, text: '⚡ 训练提速 3~4 倍', color: P.blueDark, fontSize: 11 });
  b += `<text x="539" y="320" text-anchor="middle" font-size="10.5" fill="${P.textSec}">（下游微调时只保留它）</text>`;

  // Step 4: Re-insert Mask Tokens + Lightweight Decoder
  b += arrow(632, 248, 678, 248, { color: P.violet, marker: 'arr-violet', sw: 2.2 });
  b += box({ x: 682, y: 152, w: 214, h: 192, rx: 14, fill: P.violetPale, stroke: P.violet, sw: 1.8 });
  b += `<text x="789" y="178" text-anchor="middle" font-size="14" font-weight="700" fill="${P.violetDark}">补回 [Mask] + 轻量 Decoder</text>`;
  b += `<text x="789" y="198" text-anchor="middle" font-size="11.5" fill="${P.textSec}">按原始二维位置拼回全部 16 块</text>`;

  // Mini sequence showing visible + [M] tokens
  for (let k = 0; k < 8; k++) {
    const isV = k === 1 || k === 5;
    b += `<rect x="${698 + k * 23}" y="216" width="18" height="22" rx="3" fill="${isV ? P.blue : '#CBD5E1'}" />`;
    b += `<text x="${707 + k * 23}" y="231" text-anchor="middle" font-size="9.5" font-weight="700" fill="${isV ? '#FFFFFF' : '#475569'}">${isV ? 'V' : 'M'}</text>`;
  }
  b += labelBox({ x: 706, y: 256, w: 166, h: 52, title: '轻量级 Transformer', sub: '仅用于预训练阶段重建像素', fill: '#FFFFFF', stroke: P.violet, titleColor: P.violetDark, titleSize: 12.5, subSize: 10.5 });

  // Step 5: Reconstructed Image (Loss ONLY on masked patches)
  b += arrow(898, 248, 946, 248, { color: P.teal, marker: 'arr-teal', sw: 2.2 });
  b += `<text x="1024" y="138" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.tealDark}">③ 重建缺失像素</text>`;
  b += `<text x="1024" y="156" text-anchor="middle" font-size="11.5" fill="${P.roseDark}">仅在红框遮挡处算 Loss</text>`;
  b += patchGrid(952, 174, 'recon');

  // Loss arc comparing original (1) and recon (5)
  b += `<path d="M 114 330 L 114 406 L 408 406" fill="none" stroke="${P.rose}" stroke-width="2" stroke-dasharray="5 3" marker-end="url(#arr-rose)" />`;
  b += `<path d="M 1024 330 L 1024 406 L 752 406" fill="none" stroke="${P.rose}" stroke-width="2" stroke-dasharray="5 3" marker-end="url(#arr-rose)" />`;
  b += labelBox({
    x: 412, y: 376, w: 336, h: 58,
    title: 'MSE 重建损失（仅计算被遮住的 75% Patch）',
    sub: '靠局部像素插值蒙混过关不了 → 必须理解物体的全局语义！',
    fill: P.rosePale, stroke: P.rose, titleColor: P.roseDark, titleSize: 13, subSize: 11
  });

  // Bottom summary note
  b += noteBar({
    x: 34, y: 472, w: 1092, h: 44,
    text: '为什么遮挡比例高达 75%？图像信息高度冗余，如果只遮 15%，模型看周围像素就能轻松“抄答案”；遮掉 75% 才能逼出真正的视觉语义理解。',
  });

  return wrapSvg({
    width, height,
    title: '掩码自编码器（Masked Autoencoder, MAE）：遮住 75% 逼出语义理解',
    subtitle: '非对称设计：重型编码器只看 25% 可见块，轻型解码器负责脑补被遮挡的 75% 区域',
    badge: '§8.1 自监督视觉',
    body: b,
  });
}

export const figures = [
  { filename: '06_transformer-block-residual-norm.png', width: 1140, height: 680, render: fig06 },
  { filename: '07_transformer-architectures-encoder-decoder.png', width: 1160, height: 630, render: fig07 },
  { filename: '08_autoregressive-generation.png', width: 1140, height: 620, render: fig08 },
  { filename: '09_parallel-processing-and-kv-cache.png', width: 1160, height: 670, render: fig09 },
  { filename: '25_batching-throughput-latency.png', width: 1140, height: 600, render: fig25 },
  { filename: '10_autoencoder-reconstruction.png', width: 1140, height: 560, render: fig10 },
  { filename: '11_denoising-autoencoder.png', width: 1140, height: 520, render: fig11 },
  { filename: '12_masked-autoencoder-mae.png', width: 1160, height: 560, render: fig12 },
];
