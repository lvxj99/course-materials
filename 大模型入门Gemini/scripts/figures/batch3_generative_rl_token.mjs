import { PALETTE as P, wrapSvg, box, labelBox, pill, arrow, pathArrow, vecBars, noteBar, esc, seededRand } from '../lib/svg.mjs';

// 13: VAE Latent Sampling & Reparameterization Trick
function fig13() {
  const width = 1160, height = 640;
  let b = '';

  // Left Main Panel: VAE Training with Reparameterization Trick
  b += box({ x: 34, y: 100, w: 726, h: 454, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += pill({ x: 54, y: 116, w: 300, h: 26, fill: P.bluePale, stroke: P.blue, text: '训练阶段：编码为高斯分布 + 重参数化技巧', color: P.blueDark, fontSize: 12 });

  // Input x
  b += labelBox({ x: 54, y: 248, w: 74, h: 74, title: '输入 x', sub: '图像', fill: P.bluePale, stroke: P.blue, titleColor: P.blueDark, titleSize: 13.5 });
  b += arrow(130, 285, 166, 285, { color: P.blue, marker: 'arr-blue', sw: 2 });

  // Encoder trapezoid
  b += `<path d="M 170 218 L 284 242 L 284 328 L 170 352 Z" fill="${P.bluePale}" stroke="${P.blue}" stroke-width="2" filter="url(#shadow-sm)" />`;
  b += `<text x="227" y="280" text-anchor="middle" font-size="14" font-weight="700" fill="${P.blueDark}">Encoder</text>`;
  b += `<text x="227" y="299" text-anchor="middle" font-size="11.5" fill="${P.textSec}">q_φ(z | x)</text>`;

  // Outputs mu(x) and sigma(x)
  b += labelBox({ x: 318, y: 222, w: 86, h: 46, title: '均值 μ(x)', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 12.5 });
  b += labelBox({ x: 318, y: 302, w: 86, h: 46, title: '标准差 σ(x)', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 12.5 });
  b += pathArrow('M 284 268 L 302 268 L 302 245 L 315 245', { color: P.violet, marker: 'arr-violet', sw: 1.8 });
  b += pathArrow('M 284 302 L 302 302 L 302 325 L 315 325', { color: P.violet, marker: 'arr-violet', sw: 1.8 });

  // Reparameterization node z = mu + sigma * eps
  b += box({ x: 438, y: 244, w: 112, h: 82, rx: 12, fill: P.amberPale, stroke: P.amber, sw: 2.2 });
  b += `<text x="494" y="272" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.amberDark}">采样 z</text>`;
  b += `<text x="494" y="295" text-anchor="middle" font-size="13" font-weight="700" fill="${P.text}">μ + σ ⊙ ε</text>`;
  b += `<text x="494" y="314" text-anchor="middle" font-size="10.5" fill="${P.amberDark}">可微重参数化</text>`;

  b += pathArrow('M 404 245 L 422 245 L 422 272 L 435 272', { color: P.violet, marker: 'arr-violet', sw: 1.8 });
  b += pathArrow('M 404 325 L 422 325 L 422 298 L 435 298', { color: P.violet, marker: 'arr-violet', sw: 1.8 });

  // External noise eps ~ N(0, I)
  b += labelBox({ x: 438, y: 158, w: 112, h: 46, title: 'ε ~ N(0, I)', sub: '外部随机噪声', fill: '#F8FAFC', stroke: P.slate, titleColor: P.slate, titleSize: 12.5, subSize: 10.5 });
  b += arrow(494, 206, 494, 241, { color: P.slate, marker: 'arr-slate', sw: 1.8, dash: '4 3' });

  // Backprop gradient red dashed line bypassing eps!
  b += `<path d="M 556 352 L 368 352" stroke="${P.rose}" stroke-width="2" stroke-dasharray="5 3" marker-end="url(#arr-rose)" />`;
  b += `<text x="458" y="372" text-anchor="middle" font-size="11" font-weight="700" fill="${P.roseDark}">◀ 反向传播梯度畅通流回 μ, σ（绕开随机节点 ε）</text>`;

  // Decoder trapezoid
  b += arrow(552, 285, 582, 285, { color: P.teal, marker: 'arr-teal', sw: 2 });
  b += `<path d="M 586 242 L 664 218 L 664 352 L 586 328 Z" fill="${P.tealPale}" stroke="${P.teal}" stroke-width="2" filter="url(#shadow-sm)" />`;
  b += `<text x="625" y="280" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.tealDark}">Decoder</text>`;
  b += `<text x="625" y="299" text-anchor="middle" font-size="11" fill="${P.textSec}">p_θ(x | z)</text>`;

  // Output x_hat
  b += arrow(666, 285, 686, 285, { color: P.teal, marker: 'arr-teal', sw: 2 });
  b += labelBox({ x: 690, y: 248, w: 54, h: 74, title: 'x̂', sub: '重建', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 15 });

  // Two Loss terms card at bottom of left panel
  b += box({ x: 54, y: 396, w: 686, h: 140, rx: 12, fill: '#F8FAFC', stroke: P.borderLight, shadow: false });
  b += `<text x="397" y="422" text-anchor="middle" font-size="14" font-weight="700" fill="${P.text}">L_VAE(x) =  E[ −log p_θ(x | z) ]  +  D_KL( q_φ(z | x) ∥ N(0, I) )</text>`;

  b += box({ x: 70, y: 440, w: 316, h: 80, rx: 10, fill: P.emeraldPale, stroke: P.emerald, sw: 1.4, shadow: false });
  b += `<text x="228" y="464" text-anchor="middle" font-size="13" font-weight="700" fill="${P.tealDark}">① 重建损失（像输入）</text>`;
  b += `<text x="228" y="486" text-anchor="middle" font-size="11.5" fill="${P.text}">让 Decoder 从 z 尽量还原原图 x，</text>`;
  b += `<text x="228" y="505" text-anchor="middle" font-size="11.5" fill="${P.textSec}">避免潜在向量丢失关键语义信息。</text>`;

  b += box({ x: 408, y: 440, w: 316, h: 80, rx: 10, fill: P.violetPale, stroke: P.violet, sw: 1.4, shadow: false });
  b += `<text x="566" y="464" text-anchor="middle" font-size="13" font-weight="700" fill="${P.violetDark}">② KL 散度正则（整齐连续）</text>`;
  b += `<text x="566" y="486" text-anchor="middle" font-size="11.5" fill="${P.text}">把编码分布拉向标准正态 N(0, I)，</text>`;
  b += `<text x="566" y="505" text-anchor="middle" font-size="11.5" fill="${P.textSec}">消除潜在空间“空洞”，保证处处可采样！</text>`;

  // Right Panel: Generation Stage (Sampling from N(0, I))
  b += box({ x: 782, y: 100, w: 344, h: 454, rx: 14, fill: '#FFFFFF', stroke: P.teal, sw: 1.8 });
  b += pill({ x: 802, y: 116, w: 280, h: 26, fill: P.tealPale, stroke: P.teal, text: '生成阶段：直接从先验 N(0, I) 采样！', color: P.tealDark, fontSize: 12 });

  // 2D Gaussian contour rings
  const gcx = 954, gcy = 250;
  [84, 62, 40, 20].forEach((r, idx) => {
    b += `<circle cx="${gcx}" cy="${gcy}" r="${r}" fill="${P.violet}" fill-opacity="${0.08 + idx * 0.08}" stroke="${P.violet}" stroke-opacity="0.45" stroke-width="1.2" />`;
  });
  b += `<line x1="${gcx - 98}" y1="${gcy}" x2="${gcx + 98}" y2="${gcy}" stroke="#94A3B8" stroke-dasharray="3 3" />`;
  b += `<line x1="${gcx}" y1="${gcy - 92}" x2="${gcx}" y2="${gcy + 92}" stroke="#94A3B8" stroke-dasharray="3 3" />`;
  b += `<text x="${gcx}" y="${gcy - 72}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.violetDark}">平滑连续的 N(0, I) 潜在空间</text>`;

  // Sampled point z_new
  b += `<circle cx="${gcx + 32}" cy="${gcy + 20}" r="7" fill="${P.amber}" stroke="#FFFFFF" stroke-width="2" />`;
  b += `<text x="${gcx + 44}" y="${gcy + 24}" font-size="12" font-weight="700" fill="${P.amberDark}">新采样 z_new</text>`;

  b += arrow(gcx, 344, gcx, 384, { color: P.teal, marker: 'arr-teal', sw: 2.2 });
  b += labelBox({ x: 850, y: 388, w: 208, h: 52, title: '保留训练好的 Decoder', sub: '直接丢弃 Encoder，输入 z_new', fill: P.tealPale, stroke: P.teal, titleColor: P.tealDark, titleSize: 13 });
  b += arrow(gcx, 442, gcx, 476, { color: P.emerald, marker: 'arr-emerald', sw: 2.2 });
  b += labelBox({ x: 840, y: 480, w: 228, h: 54, title: '✨ 生成全新合理样本 x_new', sub: '在空间中平滑移动 z，生成图像也平滑过渡', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 13, subSize: 10.5 });

  // Bottom note
  b += noteBar({
    x: 34, y: 574, w: 1092, h: 42,
    text: 'AE vs VAE 的核心区别：普通 AE 把每张图压成一个孤立的点，随机取点往往解码出乱码；VAE 用 KL 散度把潜在空间“捏”成连续高斯分布，随时可采样生成！',
  });

  return wrapSvg({
    width, height,
    title: '变分自编码器（VAE）：把潜在空间变成可采样的概率分布',
    subtitle: '用均值 μ 和标准差 σ 表达概率分布，用重参数化技巧打通反向传播，实现“从噪声采样生成新样本”',
    badge: '§8.2 概率生成',
    body: b,
  });
}

// 14: GAN Generator vs Discriminator
function fig14() {
  const width = 1140, height = 600;
  let b = '';

  // Top flow: Random noise -> Generator -> Fake image
  b += labelBox({ x: 46, y: 152, w: 136, h: 72, title: '随机噪声 z', sub: 'z ~ N(0, I)', fill: P.violetPale, stroke: P.violet, titleColor: P.violetDark, titleSize: 14 });
  b += arrow(184, 188, 240, 188, { color: P.violet, marker: 'arr-violet', sw: 2.2 });

  b += labelBox({ x: 244, y: 140, w: 188, h: 96, title: '生成器 Generator G_θ', sub: '角色：“造假画师”\n努力生成逼真样本以假乱真', fill: P.bluePale, stroke: P.blue, titleColor: P.blueDark, titleSize: 14.5, subSize: 11.5, sw: 2 });
  b += arrow(434, 188, 492, 188, { color: P.blue, marker: 'arr-blue', sw: 2.2 });

  b += labelBox({ x: 496, y: 152, w: 134, h: 72, title: '生成样本 x̃', sub: 'x̃ = G_θ(z)（假）', fill: P.amberPale, stroke: P.amber, titleColor: P.amberDark, titleSize: 13.5 });

  // Bottom left: Real Dataset -> Real image
  b += labelBox({ x: 244, y: 312, w: 188, h: 74, title: '真实数据集（训练集）', sub: '真实照片 / 手写数字', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 14 });
  b += arrow(434, 349, 492, 349, { color: P.emerald, marker: 'arr-emerald', sw: 2.2 });
  b += labelBox({ x: 496, y: 312, w: 134, h: 74, title: '真实样本 x', sub: '来源标签 = 真 (1)', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 13.5 });

  // Both enter Discriminator
  b += pathArrow('M 632 188 L 672 188 L 672 246 L 708 246', { color: P.amber, marker: 'arr-amber', sw: 2.2 });
  b += pathArrow('M 632 349 L 672 349 L 672 292 L 708 292', { color: P.emerald, marker: 'arr-emerald', sw: 2.2 });

  b += labelBox({ x: 712, y: 214, w: 196, h: 110, title: '判别器 Discriminator D_ψ', sub: '角色：“鉴宝专家”\n输出样本为真的概率 D_ψ(·)', fill: P.rosePale, stroke: P.rose, titleColor: P.roseDark, titleSize: 14, subSize: 11.5, sw: 2 });

  // Output score
  b += arrow(910, 269, 956, 269, { color: P.rose, marker: 'arr-rose', sw: 2.2 });
  b += labelBox({ x: 960, y: 224, w: 142, h: 90, title: '真/假打分', sub: '真样本 → 趋近 1\n假样本 → 趋近 0', fill: '#FFFFFF', stroke: P.rose, titleColor: P.roseDark, titleSize: 14, subSize: 11.5 });

  // Training feedback loop 1: Update D
  b += pathArrow('M 1031 316 L 1031 416 L 810 416 L 810 328', { color: P.rose, marker: 'arr-rose', sw: 2, dash: '5 3' });
  b += pill({ x: 828, y: 403, w: 192, h: 26, fill: P.roseLight, stroke: P.rose, text: '① 冻结 G，更新判别器 D_ψ', color: P.roseDark, fontSize: 11.5 });

  // Training feedback loop 2: Update G through frozen D
  b += pathArrow('M 1031 222 L 1031 112 L 338 112 L 338 136', { color: P.blue, marker: 'arr-blue', sw: 2.2, dash: '6 3' });
  b += pill({ x: 544, y: 99, w: 294, h: 26, fill: P.bluePale, stroke: P.blue, text: '② 冻结 D，梯度经 D 回传更新生成器 G_θ（骗过 D！）', color: P.blueDark, fontSize: 11.5 });

  // Bottom panel: Why GAN is notoriously hard to train
  b += box({ x: 38, y: 454, w: 1064, h: 112, rx: 12, fill: P.amberPale, stroke: P.amberLight, sw: 1.5, shadow: false });
  b += `<text x="58" y="482" font-size="14" font-weight="700" fill="${P.amberDark}">⚠️ 交替博弈的代价：为什么 GAN 出了名的难训练？</text>`;

  const failures = [
    { x: 58, t: '模式崩溃（Mode Collapse）', d: '生成器只反复画少数最容易骗过 D 的样本，丧失多样性。' },
    { x: 406, t: '梯度消失（D 过强）', d: '判别器一眼识破真假，生成器收不到有效改进梯度。' },
    { x: 754, t: '训练震荡 & 超参敏感', d: '两个网络互相拉锯，损失剧烈波动，学习率稍偏即发散。' },
  ];
  failures.forEach((f) => {
    b += box({ x: f.x, y: 494, w: 326, h: 58, rx: 8, fill: '#FFFFFF', stroke: P.amberLight, shadow: false });
    b += `<text x="${f.x + 12}" y="516" font-size="12.5" font-weight="700" fill="${P.text}">${f.t}</text>`;
    b += `<text x="${f.x + 12}" y="537" font-size="11.5" fill="${P.textSec}">${f.d}</text>`;
  });

  return wrapSvg({
    width, height,
    title: '生成对抗网络（GAN）：生成器与判别器的左右互搏',
    subtitle: '不需要显式像素重建损失，直接由判别器提供动态学习反馈；生成时只保留生成器 G_θ',
    badge: '§8.3 对抗生成',
    body: b,
  });
}

// Helper for diffusion progressive noisy image tiles
function diffTile(x, y, size, noiseLevel, seed) {
  const rand = seededRand(seed);
  const n = 9;
  const cell = size / n;
  let out = `<rect x="${x}" y="${y}" width="${size}" height="${size}" rx="10" fill="#0F172A" stroke="${noiseLevel > 0.8 ? P.rose : P.blue}" stroke-width="1.8" />`;
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      // Base clean pattern: glowing sun & blue hills
      let cr = 30, cg = 58, cb = 138;
      const distSun = Math.hypot(r - 2.2, c - 6.2);
      if (distSun < 1.8) { cr = 250; cg = 204; cb = 21; }
      else if (r >= 6 || (r === 5 && c >= 1 && c <= 5)) { cr = 16; cg = 185; cb = 129; }
      else if (r <= 4) { cr = 96; cg = 165; cb = 250; }
      // Mix with Gaussian-like noise
      const nr = Math.floor(rand() * 255), ng = Math.floor(rand() * 255), nb = Math.floor(rand() * 255);
      const mr = Math.round(cr * (1 - noiseLevel) + nr * noiseLevel);
      const mg = Math.round(cg * (1 - noiseLevel) + ng * noiseLevel);
      const mb = Math.round(cb * (1 - noiseLevel) + nb * noiseLevel);
      out += `<rect x="${(x + c * cell + 1).toFixed(1)}" y="${(y + r * cell + 1).toFixed(1)}" width="${(cell - 2).toFixed(1)}" height="${(cell - 2).toFixed(1)}" rx="2" fill="rgb(${mr},${mg},${mb})" />`;
    }
  }
  return out;
}

// 15: Diffusion Forward & Reverse Process
function fig15() {
  const width = 1140, height = 590;
  let b = '';

  const stages = [
    { x: 64, noise: 0.0, lbl: 'x₀（真实图像）', sub: 't = 0', seed: 11 },
    { x: 286, noise: 0.25, lbl: 'x_t₁（轻微噪声）', sub: 't = 250', seed: 22 },
    { x: 508, noise: 0.55, lbl: 'x_t（中度噪声）', sub: 't = 500', seed: 33 },
    { x: 730, noise: 0.82, lbl: 'x_t₂（重度噪声）', sub: 't = 750', seed: 44 },
    { x: 952, noise: 1.0, lbl: 'x_T（纯高斯噪声）', sub: 't = 1000 · N(0,I)', seed: 55 },
  ];

  // Top forward banner
  b += box({ x: 116, y: 104, w: 908, h: 52, rx: 12, fill: P.rosePale, stroke: P.roseLight, shadow: false });
  b += `<text x="570" y="126" text-anchor="middle" font-size="14" font-weight="700" fill="${P.roseDark}">前向加噪过程（Forward Process · 固定公式，无需学习）  ──▶</text>`;
  b += `<text x="570" y="146" text-anchor="middle" font-size="12.5" fill="${P.text}">xₜ = √ᾱₜ · x₀ + √(1 − ᾱₜ) · ε ,   ε ~ N(0, I)   （逐步用噪声淹没原始信号）</text>`;

  // Draw the 5 image tiles & bidirectional arrows between them
  stages.forEach((st, i) => {
    b += diffTile(st.x, 224, 124, st.noise, st.seed);
    b += `<text x="${st.x + 62}" y="210" text-anchor="middle" font-size="13" font-weight="700" fill="${i === 0 ? P.blueDark : (i === 4 ? P.roseDark : P.text)}">${st.lbl}</text>`;
    b += `<text x="${st.x + 62}" y="368" text-anchor="middle" font-size="11.5" font-weight="600" fill="${P.textSec}">${st.sub}</text>`;

    if (i < stages.length - 1) {
      const x1 = st.x + 130, x2 = stages[i + 1].x - 6;
      // Forward arrow (top, rightwards)
      b += arrow(x1, 256, x2, 256, { color: P.rose, marker: 'arr-rose', sw: 2.2 });
      b += `<text x="${(x1 + x2) / 2}" y="246" text-anchor="middle" font-size="10.5" font-weight="700" fill="${P.roseDark}">+ 噪声</text>`;
      // Reverse arrow (bottom, leftwards)
      b += arrow(x2, 314, x1, 314, { color: P.teal, marker: 'arr-teal', sw: 2.4 });
      b += `<text x="${(x1 + x2) / 2}" y="332" text-anchor="middle" font-size="10.5" font-weight="700" fill="${P.tealDark}">去噪 ε_θ</text>`;
    }
  });

  // Bottom reverse banner
  b += box({ x: 116, y: 392, w: 908, h: 58, rx: 12, fill: P.tealPale, stroke: P.teal, sw: 1.6, shadow: false });
  b += `<text x="570" y="416" text-anchor="middle" font-size="14" font-weight="700" fill="${P.tealDark}">◀──  反向去噪生成（Reverse Process · 神经网络 U-Net / DiT 学习）</text>`;
  b += `<text x="570" y="438" text-anchor="middle" font-size="12.5" fill="${P.text}">生成时：从新采样的纯噪声 x_T 出发，反复执行「预测噪声 ε_θ(xₜ, t) → 减去噪声 → 得到更清晰的 xₜ₋₁」</text>`;

  // Bottom two cards: Training loss & Why stable
  b += box({ x: 38, y: 472, w: 520, h: 86, rx: 12, fill: '#FFFFFF', stroke: P.blueLight, sw: 1.5 });
  b += pill({ x: 54, y: 484, w: 180, h: 24, fill: P.bluePale, stroke: P.blue, text: '训练目标：预测真实加入的噪声', color: P.blueDark, fontSize: 11.5 });
  b += `<text x="54" y="528" font-size="14" font-weight="700" fill="${P.blueDark}">L_diffusion = E[ ‖ ε − ε_θ(xₜ, t) ‖² ]</text>`;
  b += `<text x="54" y="547" font-size="11.5" fill="${P.textSec}">随机选时间步 t 和噪声 ε，让网络猜出刚才加进去的是什么噪声。</text>`;

  b += box({ x: 582, y: 472, w: 520, h: 86, rx: 12, fill: '#FFFFFF', stroke: P.emeraldLight, sw: 1.5 });
  b += pill({ x: 598, y: 484, w: 196, h: 24, fill: P.emeraldPale, stroke: P.emerald, text: '为什么比 GAN 稳定且画质细腻？', color: P.tealDark, fontSize: 11.5 });
  b += `<text x="598" y="526" font-size="12.5" fill="${P.text}">把“一步登天画整张图”拆成上百个简单的“去一点点噪”小步，</text>`;
  b += `<text x="598" y="546" font-size="12.5" fill="${P.textSec}">训练目标是简单均方误差，且可轻松融入文字提示做条件生成！</text>`;

  return wrapSvg({
    width, height,
    title: '扩散模型（Diffusion）：前向加噪与反向逐步去噪',
    subtitle: '把复杂的图像生成拆解为一系列平滑可控的去噪步骤，从简单的高斯分布逐步雕刻出清晰图像',
    badge: '§8.4 扩散模型',
    body: b,
  });
}

// 16: Flow Matching vs Diffusion Path Comparison
function fig16() {
  const width = 1160, height = 610;
  let b = '';

  function drawTransportPanel({ x, y, w, h, title, badge, badgeBg, badgeCol, mode }) {
    let out = box({ x, y, w, h, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
    out += pill({ x: x + 20, y: y + 16, w: 268, h: 26, fill: badgeBg, stroke: badgeCol, text: badge, color: badgeCol, fontSize: 12 });
    out += `<text x="${x + 20}" y="${y + 64}" font-size="15" font-weight="700" fill="${P.text}">${esc(title)}</text>`;

    // Plot area
    const px = x + 20, py = y + 84, pw = w - 40, ph = 276;
    out += `<rect x="${px}" y="${py}" width="${pw}" height="${ph}" rx="12" fill="#F8FAFC" stroke="${P.borderLight}" />`;

    // Left blob: Source Gaussian p1 = N(0, I)
    const sx = px + 68, sy = py + ph / 2;
    out += `<ellipse cx="${sx}" cy="${sy}" rx="42" ry="86" fill="${P.blue}" fill-opacity="0.14" stroke="${P.blue}" stroke-width="1.5" stroke-dasharray="4 3" />`;
    out += `<text x="${sx}" y="${py + 26}" text-anchor="middle" font-size="12" font-weight="700" fill="${P.blueDark}">源分布：高斯噪声</text>`;
    out += `<text x="${sx}" y="${py + ph - 12}" text-anchor="middle" font-size="11" fill="${P.textMuted}">p₁ = N(0, I)</text>`;

    // Right blobs: Bimodal Data distribution p0
    const dx = px + pw - 68;
    out += `<ellipse cx="${dx}" cy="${py + 88}" rx="40" ry="44" fill="${P.emerald}" fill-opacity="0.18" stroke="${P.emerald}" stroke-width="1.6" />`;
    out += `<ellipse cx="${dx}" cy="${py + 196}" rx="42" ry="42" fill="${P.emerald}" fill-opacity="0.18" stroke="${P.emerald}" stroke-width="1.6" />`;
    out += `<text x="${dx}" y="${py + 26}" text-anchor="middle" font-size="12" font-weight="700" fill="${P.tealDark}">目标：真实数据分布</text>`;
    out += `<text x="${dx}" y="${py + ph - 12}" text-anchor="middle" font-size="11" fill="${P.textMuted}">p₀ (图像/多模态)</text>`;

    // Sample points & trajectories
    const pairs = [
      [sy - 56, py + 72],
      [sy - 20, py + 102],
      [sy + 24, py + 182],
      [sy + 58, py + 214],
    ];

    if (mode === 'sde') {
      // Wiggly curved SDE trajectories with random kicks
      const rand = seededRand(99);
      pairs.forEach(([y0, y1], idx) => {
        const steps = 22;
        let d = `M ${sx + 10} ${y0}`;
        for (let s = 1; s < steps; s++) {
          const t = s / steps;
          const bx = sx + 10 + t * (dx - sx - 20);
          const arch = Math.sin(t * Math.PI) * (idx < 2 ? -24 : 26);
          const jitter = (rand() - 0.5) * 26;
          const by = y0 + (y1 - y0) * t + arch + jitter;
          d += ` L ${bx.toFixed(1)} ${by.toFixed(1)}`;
        }
        d += ` L ${dx - 10} ${y1}`;
        out += `<path d="${d}" fill="none" stroke="${P.rose}" stroke-width="2.1" stroke-opacity="0.82" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#arr-rose)" />`;
        out += `<circle cx="${sx + 10}" cy="${y0}" r="4.5" fill="${P.blue}" />`;
        out += `<circle cx="${dx - 10}" cy="${y1}" r="4.5" fill="${P.emerald}" />`;
      });
      // Footnote inside panel
      out += box({ x: px, y: py + ph + 14, w: pw, h: 74, rx: 10, fill: P.rosePale, stroke: P.roseLight, shadow: false });
      out += `<text x="${px + 14}" y="${py + ph + 37}" font-size="12.5" font-weight="700" fill="${P.roseDark}">特点：带随机扰动的曲线轨迹（SDE：dx = f dt + g dw）</text>`;
      out += `<text x="${px + 14}" y="${py + ph + 58}" font-size="12" fill="${P.text}">每步都有随机性且路径弯曲 → 采样需要更多步数（常见 50~1000 步）</text>`;
      out += `<text x="${px + 14}" y="${py + ph + 77}" font-size="11.5" fill="${P.textSec}">（注：通过 Probability Flow ODE 可去掉随机项，得到确定性曲线）</text>`;
    } else {
      // Background subtle vector field arrows
      for (let gx = sx + 66; gx <= dx - 66; gx += 58) {
        for (let gy = py + 58; gy <= py + ph - 50; gy += 48) {
          const dy = gy < sy ? -6 : 6;
          out += `<line x1="${gx - 10}" y1="${gy}" x2="${gx + 10}" y2="${gy + dy}" stroke="${P.violet}" stroke-opacity="0.32" stroke-width="1.4" marker-end="url(#arr-violet)" />`;
        }
      }
      // Straight deterministic ODE paths!
      pairs.forEach(([y0, y1]) => {
        out += `<line x1="${sx + 10}" y1="${y0}" x2="${dx - 14}" y2="${y1}" stroke="${P.violet}" stroke-width="2.6" stroke-linecap="round" marker-end="url(#arr-violet)" />`;
        // Show 3 discrete ODE steps as crisp dots along straight path
        [0.25, 0.5, 0.75].forEach((t) => {
          const mx = sx + 10 + t * (dx - sx - 24);
          const my = y0 + t * (y1 - y0);
          out += `<circle cx="${mx.toFixed(1)}" cy="${my.toFixed(1)}" r="3.5" fill="#FFFFFF" stroke="${P.violet}" stroke-width="1.8" />`;
        });
        out += `<circle cx="${sx + 10}" cy="${y0}" r="4.5" fill="${P.blue}" />`;
        out += `<circle cx="${dx - 10}" cy="${y1}" r="4.5" fill="${P.emerald}" />`;
      });
      out += box({ x: px, y: py + ph + 14, w: pw, h: 74, rx: 10, fill: P.violetPale, stroke: P.violetLight, shadow: false });
      out += `<text x="${px + 14}" y="${py + ph + 37}" font-size="12.5" font-weight="700" fill="${P.violetDark}">特点：直接学习确定性速度场 v_θ(x, t)（ODE 直线传输）</text>`;
      out += `<text x="${px + 14}" y="${py + ph + 58}" font-size="12" fill="${P.text}">路径近似直线 → 数值积分误差极小，少步即可高质量生成（如 10~30 步）</text>`;
      out += `<text x="${px + 14}" y="${py + ph + 77}" font-size="11.5" fill="${P.textSec}">（Flux、SD3 等新一代文生图/视频大模型广泛采用 Flow Matching）</text>`;
    }

    return out;
  }

  b += drawTransportPanel({
    x: 34, y: 100, w: 534, h: 468,
    badge: 'Diffusion · 反向扩散（SDE）',
    badgeBg: P.rosePale, badgeCol: P.roseDark,
    title: '弯曲且带随机抖动的去噪轨迹',
    mode: 'sde',
  });

  b += drawTransportPanel({
    x: 592, y: 100, w: 534, h: 468,
    badge: 'Flow Matching · 确定性向量场（ODE）',
    badgeBg: P.violetPale, badgeCol: P.violetDark,
    title: '沿着速度场沿直线高效传输',
    mode: 'ode',
  });

  return wrapSvg({
    width, height,
    title: 'Flow Matching 与 Diffusion 的生成路径对比',
    subtitle: '两者都把易采样的高斯噪声变换到复杂数据分布；Flow Matching 把弯曲随机路径拉直，大幅减少采样步数',
    badge: '§8.4 SDE vs ODE',
    body: b,
  });
}

// 27: Agent-Environment Reinforcement Learning Loop
function fig27() {
  const width = 1140, height = 580;
  let b = '';

  // Left main RL loop area
  b += box({ x: 34, y: 100, w: 660, h: 446, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });

  // Agent box (top center)
  b += box({ x: 214, y: 132, w: 300, h: 98, rx: 14, fill: P.bluePale, stroke: P.blue, sw: 2.2 });
  b += `<text x="364" y="164" text-anchor="middle" font-size="17" font-weight="700" fill="${P.blueDark}">智能体 Agent</text>`;
  b += `<text x="364" y="188" text-anchor="middle" font-size="13.5" font-weight="600" fill="${P.text}">策略 Policy：π_θ(aₜ | sₜ)</text>`;
  b += `<text x="364" y="212" text-anchor="middle" font-size="11.5" fill="${P.textSec}">根据当前状态选择最优动作（或生成下一词）</text>`;

  // Environment box (bottom center)
  b += box({ x: 214, y: 356, w: 300, h: 98, rx: 14, fill: P.tealPale, stroke: P.teal, sw: 2.2 });
  b += `<text x="364" y="388" text-anchor="middle" font-size="17" font-weight="700" fill="${P.tealDark}">环境 Environment</text>`;
  b += `<text x="364" y="412" text-anchor="middle" font-size="13" font-weight="600" fill="${P.text}">状态转移 + 奖励反馈</text>`;
  b += `<text x="364" y="436" text-anchor="middle" font-size="11.5" fill="${P.textSec}">执行动作后给出新状态 sₜ₊₁ 与奖励 rₜ₊₁</text>`;

  // Right loop arrow: Agent -> Environment (Action a_t)
  b += pathArrow('M 516 181 L 606 181 L 606 405 L 518 405', { color: P.blue, marker: 'arr-blue', sw: 2.8 });
  b += labelBox({ x: 544, y: 264, w: 124, h: 58, title: '动作 Action aₜ', sub: '执行选择/决策', fill: '#FFFFFF', stroke: P.blue, titleColor: P.blueDark, titleSize: 13, subSize: 11 });

  // Left loop arrows: Environment -> Agent (State s_{t+1} & Reward r_{t+1})
  b += pathArrow('M 212 388 L 118 388 L 118 198 L 210 198', { color: P.teal, marker: 'arr-teal', sw: 2.6 });
  b += pathArrow('M 212 424 L 82 424 L 82 166 L 210 166', { color: P.amberDark, marker: 'arr-amber', sw: 2.6 });

  // Time step boundary dashed line
  b += `<line x1="60" y1="292" x2="178" y2="292" stroke="${P.slate}" stroke-width="1.5" stroke-dasharray="5 3" />`;
  b += pill({ x: 64, y: 279, w: 112, h: 26, fill: '#F1F5F9', stroke: P.slate, text: '时间步 t → t+1', color: P.slate, fontSize: 11 });

  b += pill({ x: 128, y: 234, w: 100, h: 26, fill: P.tealPale, stroke: P.teal, text: '状态 sₜ₊₁', color: P.tealDark, fontSize: 12 });
  b += pill({ x: 56, y: 332, w: 100, h: 26, fill: P.amberLight, stroke: P.amber, text: '奖励 rₜ₊₁', color: P.amberDark, fontSize: 12 });

  // Trajectory ribbon at bottom of left panel
  b += box({ x: 58, y: 478, w: 612, h: 48, rx: 10, fill: P.violetPale, stroke: P.violetLight, shadow: false });
  b += `<text x="364" y="507" text-anchor="middle" font-size="13" font-weight="700" fill="${P.violetDark}">轨迹 Trajectory τ = ( s₀, a₀, r₁,  s₁, a₁, r₂,  s₂, a₂, r₃, ··· )</text>`;

  // Right Top Card: Optimization Objective (Return & Value)
  b += box({ x: 718, y: 100, w: 388, h: 210, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += pill({ x: 738, y: 116, w: 224, h: 26, fill: P.amberPale, stroke: P.amber, text: '学习目标：最大化期望长期回报', color: P.amberDark, fontSize: 12 });
  b += `<text x="738" y="168" font-size="14.5" font-weight="700" fill="${P.text}">Gₜ = rₜ₊₁ + γ rₜ₊₂ + γ² rₜ₊₃ + ···</text>`;
  b += `<text x="738" y="190" font-size="12" fill="${P.textSec}">折扣因子 γ ∈ [0, 1)：越接近 1 越看重长远收益</text>`;
  b += `<line x1="738" y1="208" x2="1084" y2="208" stroke="${P.borderLight}" />`;
  b += `<text x="738" y="232" font-size="12.5" font-weight="700" fill="${P.blueDark}">• Value-based：学 Q(s, a)，选分最高的动作</text>`;
  b += `<text x="738" y="256" font-size="12.5" font-weight="700" fill="${P.tealDark}">• Policy-based：直接优化参数化策略 π_θ</text>`;
  b += `<text x="738" y="280" font-size="12.5" font-weight="700" fill="${P.violetDark}">• Actor-Critic：Actor 选动作 + Critic 稳评价</text>`;

  // Right Bottom Card: Mapping to Large Language Models!
  b += box({ x: 718, y: 328, w: 388, h: 218, rx: 14, fill: P.bluePale, stroke: P.blue, sw: 1.6 });
  b += pill({ x: 738, y: 344, w: 244, h: 26, fill: P.blue, stroke: P.blueDark, text: '映射到 LLM 后训练（RLHF / RLVR）', color: '#FFFFFF', fontSize: 12 });

  const rows = [
    ['State sₜ', '当前已有的上下文 Prompt + 已生成词'],
    ['Action aₜ', '模型输出的下一个 Token'],
    ['Policy π_θ', '大语言模型本身（Transformer）'],
    ['Trajectory', '一整段完整回答或 CoT 解题过程'],
    ['Reward r', '人类偏好打分 / 数学答案或代码测试'],
  ];
  rows.forEach(([k, v], i) => {
    const ry = 392 + i * 29;
    b += `<rect x="738" y="${ry - 15}" width="88" height="22" rx="6" fill="#FFFFFF" stroke="${P.blueLight}" />`;
    b += `<text x="782" y="${ry}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${P.blueDark}">${k}</text>`;
    b += `<text x="836" y="${ry}" font-size="12" fill="${P.text}">${v}</text>`;
  });

  return wrapSvg({
    width, height,
    title: '强化学习（RL）基本回路：通过与环境交互的奖励反馈优化策略',
    subtitle: '没有每一步的“标准答案”，智能体在行动后观察状态变化与长期回报，逐步提高高分策略的概率',
    badge: '§8.6 强化学习',
    body: b,
  });
}

// 17: BPE Subword Tokenization
function fig17() {
  const width = 1140, height = 610;
  let b = '';

  // Step 0: Initial Corpus & Character Split
  b += box({ x: 34, y: 102, w: 256, h: 324, rx: 14, fill: '#FFFFFF', stroke: P.borderLight });
  b += pill({ x: 50, y: 118, w: 168, h: 24, fill: P.bluePale, stroke: P.blue, text: '初始：按单个字符切分', color: P.blueDark, fontSize: 11.5 });
  b += `<text x="50" y="162" font-size="12" font-weight="700" fill="${P.textSec}">${esc('语料词频统计（含词尾 </w>）：')}</text>`;
  const step0 = [
    ['l  o  w  </w>', '×5'],
    ['l  o  w  e  r  </w>', '×2'],
    ['n  e  w  e  s  t  </w>', '×6'],
    ['w  i  d  e  s  t  </w>', '×3'],
  ];
  step0.forEach(([w, f], i) => {
    const ry = 186 + i * 44;
    b += box({ x: 48, y: ry, w: 228, h: 34, rx: 7, fill: '#F8FAFC', stroke: P.border, shadow: false });
    b += `<text x="60" y="${ry + 21}" font-size="12" class="mono" fill="${P.text}">${esc(w)}</text>`;
    b += `<text x="264" y="${ry + 21}" text-anchor="end" font-size="12" font-weight="700" fill="${P.blueDark}">${f}</text>`;
  });
  b += `<text x="50" y="384" font-size="11.5" fill="${P.textSec}">最高频相邻对：</text>`;
  b += pill({ x: 50, y: 392, w: 224, h: 24, fill: P.amberLight, stroke: P.amber, text: '(e, s) 出现 6 + 3 = 9 次！', color: P.amberDark, fontSize: 11.5 });

  b += arrow(294, 260, 326, 260, { color: P.amber, marker: 'arr-amber', sw: 2.4 });

  // Step 1: Merge (e, s) -> es
  b += box({ x: 330, y: 102, w: 246, h: 324, rx: 14, fill: '#FFFFFF', stroke: P.amber, sw: 1.5 });
  b += pill({ x: 346, y: 118, w: 184, h: 24, fill: P.amberPale, stroke: P.amber, text: '第 1 轮合并：e + s → es', color: P.amberDark, fontSize: 11.5 });
  const step1 = [
    ['l  o  w  </w>', '×5', false],
    ['l  o  w  e  r  </w>', '×2', false],
    ['n  e  w  [es]  t  </w>', '×6', true],
    ['w  i  d  [es]  t  </w>', '×3', true],
  ];
  step1.forEach(([w, f, hi], i) => {
    const ry = 186 + i * 44;
    b += box({ x: 344, y: ry, w: 218, h: 34, rx: 7, fill: hi ? P.amberPale : '#F8FAFC', stroke: hi ? P.amber : P.border, shadow: false });
    b += `<text x="354" y="${ry + 21}" font-size="11.5" class="mono" font-weight="${hi ? 700 : 400}" fill="${hi ? P.amberDark : P.text}">${esc(w)}</text>`;
    b += `<text x="552" y="${ry + 21}" text-anchor="end" font-size="12" font-weight="700" fill="${P.blueDark}">${f}</text>`;
  });
  b += `<text x="346" y="162" font-size="12" fill="${P.textSec}">词表新增子词：<tspan font-weight="700" fill="${P.amberDark}">es</tspan></text>`;
  b += `<text x="346" y="384" font-size="11.5" fill="${P.textSec}">下一最高频相邻对：</text>`;
  b += pill({ x: 346, y: 392, w: 214, h: 24, fill: P.tealLight, stroke: P.teal, text: '(es, t) 出现 9 次！', color: P.tealDark, fontSize: 11.5 });

  b += arrow(580, 260, 612, 260, { color: P.teal, marker: 'arr-teal', sw: 2.4 });

  // Step 2: Merge (es, t) -> est
  b += box({ x: 616, y: 102, w: 236, h: 324, rx: 14, fill: '#FFFFFF', stroke: P.teal, sw: 1.5 });
  b += pill({ x: 632, y: 118, w: 194, h: 24, fill: P.tealPale, stroke: P.teal, text: '第 2 轮合并：es + t → est', color: P.tealDark, fontSize: 11.5 });
  b += `<text x="632" y="162" font-size="12" fill="${P.textSec}">词表新增子词：<tspan font-weight="700" fill="${P.tealDark}">est</tspan></text>`;
  const step2 = [
    ['l  o  w  </w>', '×5', false],
    ['l  o  w  e  r  </w>', '×2', false],
    ['n  e  w  [est]  </w>', '×6', true],
    ['w  i  d  [est]  </w>', '×3', true],
  ];
  step2.forEach(([w, f, hi], i) => {
    const ry = 186 + i * 44;
    b += box({ x: 630, y: ry, w: 208, h: 34, rx: 7, fill: hi ? P.tealPale : '#F8FAFC', stroke: hi ? P.teal : P.border, shadow: false });
    b += `<text x="640" y="${ry + 21}" font-size="11.5" class="mono" font-weight="${hi ? 700 : 400}" fill="${hi ? P.tealDark : P.text}">${esc(w)}</text>`;
    b += `<text x="828" y="${ry + 21}" text-anchor="end" font-size="12" font-weight="700" fill="${P.blueDark}">${f}</text>`;
  });
  b += `<text x="632" y="384" font-size="11.5" fill="${P.textSec}">继续合并直到预设词表大小：</text>`;
  b += pill({ x: 632, y: 392, w: 204, h: 24, fill: P.violetPale, stroke: P.violet, text: '(l,o)→lo, (lo,w)→low ···', color: P.violetDark, fontSize: 11.5 });

  b += arrow(856, 260, 888, 260, { color: P.violet, marker: 'arr-violet', sw: 2.4 });

  // Step 3: Final Subword Vocab Result
  b += box({ x: 892, y: 102, w: 214, h: 324, rx: 14, fill: P.violetPale, stroke: P.violet, sw: 1.8 });
  b += pill({ x: 908, y: 118, w: 182, h: 24, fill: P.violet, stroke: P.violetDark, text: '最终子词词表（Subword）', color: '#FFFFFF', fontSize: 11.5 });
  b += `<text x="908" y="164" font-size="12" font-weight="700" fill="${P.violetDark}">常见词整块保留，生僻词拆成词根：</text>`;

  // Visual tokens
  const toks = ['low', 'er', 'est', 'new', 'wid', 'align', 'ment', '温度', '<bos>', '<eos>'];
  toks.forEach((tk, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    b += pill({ x: 910 + col * 92, y: 184 + row * 40, w: 84, h: 28, fill: '#FFFFFF', stroke: P.violet, text: tk, color: P.violetDark, fontSize: 12 });
  });
  b += `<text x="999" y="408" text-anchor="middle" font-size="11.5" font-weight="600" fill="${P.textSec}">典型词表大小：32K ~ 150K</text>`;

  // Bottom comparison card: Why Subword (not Pure Word or Pure Char)
  b += box({ x: 34, y: 446, w: 1072, h: 126, rx: 12, fill: '#FFFFFF', stroke: P.borderLight });
  b += `<text x="56" y="474" font-size="14" font-weight="700" fill="${P.text}">为什么现代大模型普遍用 BPE 子词分词，而不是「纯按词」或「纯按字」？</text>`;

  const cmp = [
    { x: 56, bg: P.rosePale, st: P.roseLight, tc: P.roseDark, title: '纯按词（Word-level）', desc: '词形变化 + 专有名词导致词表爆炸，\n遇到未登录词直接变成 <UNK> 丢信息。' },
    { x: 404, bg: P.amberPale, st: P.amberLight, tc: P.amberDark, title: '纯按字符（Char-level）', desc: '词表虽小，但序列长度暴增数倍，\n注意力 O(T²) 成本极高且语义碎片化。' },
    { x: 752, bg: P.emeraldPale, st: P.emerald, tc: P.tealDark, title: 'BPE 子词（工程最佳折中 ✓）', desc: '高频词（如 low）合并成单 token，\n生僻词拆成有意义片段（align + ment）。' },
  ];
  cmp.forEach((c) => {
    b += box({ x: c.x, y: 488, w: 330, h: 70, rx: 9, fill: c.bg, stroke: c.st, sw: 1.3, shadow: false });
    b += `<text x="${c.x + 12}" y="510" font-size="12.5" font-weight="700" fill="${c.tc}">${c.title}</text>`;
    const [l1, l2] = c.desc.split('\n');
    b += `<text x="${c.x + 12}" y="530" font-size="11.5" fill="${P.text}">${esc(l1)}</text>`;
    b += `<text x="${c.x + 12}" y="547" font-size="11.5" fill="${P.textSec}">${esc(l2)}</text>`;
  });

  return wrapSvg({
    width, height,
    title: 'BPE（Byte Pair Encoding）：反复合并高频相邻对，构造子词词表',
    subtitle: '训练前预先统计语料并固化分词规则，训练与推理阶段必须严格使用同一套 Tokenizer',
    badge: '§9.1 分词原理',
    body: b,
  });
}

// 18: Tokenization & Embedding Lookup
function fig18() {
  const width = 1160, height = 560;
  let b = '';

  // Step 1: Raw text prompt
  b += box({ x: 34, y: 152, w: 152, h: 256, rx: 12, fill: '#FFFFFF', stroke: P.border });
  b += `<text x="110" y="136" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.text}">① 原始文本</text>`;
  b += labelBox({ x: 48, y: 230, w: 124, h: 86, title: '"alignment 温度"', sub: '人类可读的字符串', fill: P.bluePale, stroke: P.blue, titleColor: P.blueDark, titleSize: 13, subSize: 11 });

  b += arrow(188, 274, 224, 274, { color: P.blue, marker: 'arr-blue', sw: 2.2 });

  // Step 2: Tokenizer -> Tokens & Token IDs
  b += `<text x="336" y="136" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.text}">② Tokenizer 分词 → ID</text>`;
  b += box({ x: 228, y: 152, w: 216, h: 256, rx: 12, fill: '#FFFFFF', stroke: P.blue, sw: 1.5 });

  const tokList = [
    ['<bos>', '1', true],
    ['align', '1842', false],
    ['ment', '412', false],
    ['温', '3091', false],
    ['度', '2104', false],
  ];
  tokList.forEach(([tk, id, sp], i) => {
    const ry = 168 + i * 46;
    b += pill({ x: 242, y: ry, w: 82, h: 32, fill: sp ? '#F1F5F9' : P.bluePale, stroke: sp ? P.slate : P.blue, text: tk, color: sp ? P.slate : P.blueDark, fontSize: 12.5 });
    b += arrow(326, ry + 16, 354, ry + 16, { color: P.slate, marker: 'arr-slate', sw: 1.6 });
    b += box({ x: 358, y: ry, w: 72, h: 32, rx: 7, fill: P.amberPale, stroke: P.amber, sw: 1.3, shadow: false });
    b += `<text x="394" y="${ry + 21}" text-anchor="middle" font-size="12.5" font-weight="700" class="mono" fill="${P.amberDark}">${id}</text>`;
  });

  b += arrow(448, 274, 488, 274, { color: P.amber, marker: 'arr-amber', sw: 2.2 });
  b += `<text x="468" y="260" text-anchor="middle" font-size="11" font-weight="700" fill="${P.amberDark}">按行</text>`;
  b += `<text x="468" y="294" text-anchor="middle" font-size="11" font-weight="700" fill="${P.amberDark}">查表</text>`;

  // Step 3: Learnable Embedding Matrix E (|V| × d)
  b += `<text x="614" y="136" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.violetDark}">③ 嵌入矩阵 E ∈ ℝ^(|V| × d)</text>`;
  b += box({ x: 492, y: 152, w: 244, h: 256, rx: 12, fill: P.violetPale, stroke: P.violet, sw: 1.8 });
  b += `<text x="614" y="174" text-anchor="middle" font-size="11" font-weight="600" fill="${P.violetDark}">端到端可学习参数（如 10万行 × 4096维）</text>`;

  const eRows = [
    ['row 1', true, [0.8, 0.3, 0.6, 0.9, 0.4]],
    ['···', false, null],
    ['row 412', true, [0.3, 0.9, 0.5, 0.2, 0.8]],
    ['row 1842', true, [0.9, 0.7, 0.2, 0.6, 0.5]],
    ['row 2104', true, [0.5, 0.4, 0.9, 0.7, 0.3]],
    ['row 3091', true, [0.7, 0.8, 0.4, 0.9, 0.6]],
    ['···', false, null],
  ];
  eRows.forEach(([lbl, hi, vals], i) => {
    const ry = 188 + i * 30;
    b += `<text x="562" y="${ry + 16}" text-anchor="end" font-size="11" class="mono" font-weight="${hi ? 700 : 400}" fill="${hi ? P.violetDark : P.textMuted}">${lbl}</text>`;
    if (vals) {
      b += vecBars({ x: 572, y: ry + 2, vals, cellW: 26, cellH: 20, color: P.violet });
    } else {
      b += `<text x="640" y="${ry + 16}" text-anchor="middle" font-size="13" fill="${P.textMuted}">· · · · ·</text>`;
    }
  });

  b += arrow(740, 274, 780, 274, { color: P.violet, marker: 'arr-violet', sw: 2.2 });

  // Step 4: Input Matrix X (T × d)
  b += `<text x="884" y="136" text-anchor="middle" font-size="13.5" font-weight="700" fill="${P.tealDark}">④ 输入矩阵 X ∈ ℝ^(T × d)</text>`;
  b += box({ x: 784, y: 152, w: 200, h: 256, rx: 12, fill: P.tealPale, stroke: P.teal, sw: 1.8 });
  b += `<text x="884" y="174" text-anchor="middle" font-size="11" font-weight="600" fill="${P.tealDark}">5 个连续 d 维向量（T=5）</text>`;

  const xRows = [
    ['x₁ (<bos>)', [0.8, 0.3, 0.6, 0.9]],
    ['x₂ (align)', [0.9, 0.7, 0.2, 0.6]],
    ['x₃ (ment)', [0.3, 0.9, 0.5, 0.2]],
    ['x₄ (温)', [0.7, 0.8, 0.4, 0.9]],
    ['x₅ (度)', [0.5, 0.4, 0.9, 0.7]],
  ];
  xRows.forEach(([lbl, vals], i) => {
    const ry = 190 + i * 42;
    b += `<text x="862" y="${ry + 17}" text-anchor="end" font-size="11" font-weight="600" fill="${P.tealDark}">${esc(lbl)}</text>`;
    b += vecBars({ x: 870, y: ry + 2, vals, cellW: 22, cellH: 22, color: P.teal });
  });

  // Step 5: -> Transformer
  b += arrow(988, 274, 1022, 274, { color: P.emerald, marker: 'arr-emerald', sw: 2.2 });
  b += labelBox({ x: 1026, y: 208, w: 102, h: 132, title: 'Transformer\n各层', sub: '+ 位置编码\n→ Logits', fill: P.emeraldPale, stroke: P.emerald, titleColor: P.tealDark, titleSize: 13, subSize: 11 });

  // Bottom pipeline summary ribbon
  b += box({ x: 34, y: 438, w: 1092, h: 92, rx: 12, fill: '#FFFFFF', stroke: P.borderLight });
  b += `<text x="580" y="468" text-anchor="middle" font-size="14.5" font-weight="700" fill="${P.blueDark}">Prompt  ──▶  Tokenization  ──▶  Token IDs（离散整数） ──▶  Embedding 查表（连续向量） ──▶  Transformer</text>`;
  b += `<text x="580" y="494" text-anchor="middle" font-size="12.5" fill="${P.textSec}">离散的 Token ID 本身没有大小或远近关系（ID 412 和 413 并不相似）；查表变成连续向量后，语义相近的词才在空间中彼此靠近。</text>`;
  b += `<text x="580" y="516" text-anchor="middle" font-size="12" fill="${P.textMuted}">注意：上下文窗口上限、生成速度（tokens/s）和 API 计费，全部按这里的 Token 数量而非字符数计算！</text>`;

  return wrapSvg({
    width, height,
    title: '从文字到模型输入：分词（Tokenization）与词向量查表（Embedding）',
    subtitle: '把离散文本转换成连续矩阵 X ∈ ℝ^(T × d)，才能送入 Transformer 做矩阵运算',
    badge: '§9.1 输入链路',
    body: b,
  });
}

// 19: Temperature effect on next-token probability distribution
function fig19() {
  const width = 1160, height = 610;
  let b = '';

  const cands = ['机器学习', '深度学习', '编程', '阅读', '苹果'];
  const logits = [3.2, 2.3, 1.5, 0.8, 0.2];

  function softmaxTemp(arr, tau) {
    const scaled = arr.map((z) => z / tau);
    const maxV = Math.max(...scaled);
    const exps = scaled.map((v) => Math.exp(v - maxV));
    const sum = exps.reduce((a, c) => a + c, 0);
    return exps.map((e) => e / sum);
  }

  // Formula & Context banner
  b += box({ x: 34, y: 98, w: 1092, h: 50, rx: 10, fill: P.bluePale, stroke: P.blueLight, shadow: false });
  b += `<text x="56" y="128" font-size="13.5" font-weight="700" fill="${P.blueDark}">当前上下文：“我最喜欢学习 ___”</text>`;
  b += `<text x="348" y="128" font-size="13" fill="${P.text}">原始 Logits z = [3.2, 2.3, 1.5, 0.8, 0.2]</text>`;
  b += `<text x="1104" y="128" text-anchor="end" font-size="14" font-weight="700" fill="${P.violetDark}">p_τ(i | c) = exp(zᵢ / τ) / Σ exp(zⱼ / τ)</text>`;

  const panels = [
    {
      x: 34, tau: 0.4,
      title: '低温 τ = 0.4（尖锐 · 更确定）',
      sub: '放大 logit 差距，高概率词几乎垄断输出',
      use: '适合：代码生成、数学求解、事实提取',
      color: P.blue, bg: P.bluePale, stroke: P.blue
    },
    {
      x: 408, tau: 1.0,
      title: '标准 τ = 1.0（原始模型分布）',
      sub: '直接按模型学到的原始置信度采样',
      use: '适合：常规问答、自然对话与均衡输出',
      color: P.teal, bg: P.tealPale, stroke: P.teal
    },
    {
      x: 782, tau: 2.0,
      title: '高温 τ = 2.0（平缓 · 更有创意）',
      sub: '拉平概率差距，长尾词也有机会被抽中',
      use: '适合：头脑风暴、故事创作（过高易胡言乱语）',
      color: P.amber, bg: P.amberPale, stroke: P.amber
    },
  ];

  panels.forEach((pn) => {
    const probs = softmaxTemp(logits, pn.tau);
    b += box({ x: pn.x, y: 168, w: 344, h: 368, rx: 14, fill: '#FFFFFF', stroke: pn.stroke, sw: 1.6 });
    b += `<rect x="${pn.x}" y="168" width="344" height="44" rx="14" fill="${pn.bg}" />`;
    b += `<rect x="${pn.x}" y="198" width="344" height="14" fill="${pn.bg}" />`;
    b += `<text x="${pn.x + 172}" y="196" text-anchor="middle" font-size="15" font-weight="700" fill="${pn.color === P.amber ? P.amberDark : (pn.color === P.teal ? P.tealDark : P.blueDark)}">${pn.title}</text>`;
    b += `<text x="${pn.x + 172}" y="232" text-anchor="middle" font-size="11.5" fill="${P.textSec}">${pn.sub}</text>`;

    // Bar chart area
    const bx = pn.x + 36, by = 258, bw = 276, bh = 188;
    // Horizontal grid lines at 0%, 50%, 100%
    [0, 0.5, 1.0].forEach((lv) => {
      const gy = by + bh - lv * bh;
      b += `<line x1="${bx}" y1="${gy}" x2="${bx + bw}" y2="${gy}" stroke="#E2E8F0" stroke-dasharray="3 3" />`;
      b += `<text x="${bx - 6}" y="${gy + 4}" text-anchor="end" font-size="10" fill="${P.textMuted}">${Math.round(lv * 100)}%</text>`;
    });
    b += `<line x1="${bx}" y1="${by + bh}" x2="${bx + bw}" y2="${by + bh}" stroke="${P.slate}" stroke-width="1.4" />`;

    probs.forEach((pr, idx) => {
      const barW = 36;
      const gap = 18;
      const rx = bx + 14 + idx * (barW + gap);
      const rh = Math.max(4, pr * bh);
      const ry = by + bh - rh;
      const isTop = idx === 0;
      b += `<rect x="${rx}" y="${ry.toFixed(1)}" width="${barW}" height="${rh.toFixed(1)}" rx="5" fill="${pn.color}" fill-opacity="${isTop ? 0.92 : Math.max(0.32, pr * 1.6).toFixed(2)}" />`;
      b += `<text x="${rx + barW / 2}" y="${(ry - 6).toFixed(1)}" text-anchor="middle" font-size="11" font-weight="700" fill="${isTop ? P.text : P.textSec}">${(pr * 100).toFixed(1)}%</text>`;
      b += `<text x="${rx + barW / 2}" y="${by + bh + 18}" text-anchor="middle" font-size="11" font-weight="${isTop ? 700 : 500}" fill="${P.text}">${cands[idx]}</text>`;
    });

    b += pill({ x: pn.x + 18, y: 492, w: 308, h: 28, fill: pn.bg, stroke: pn.stroke, text: pn.use, color: pn.color === P.amber ? P.amberDark : (pn.color === P.teal ? P.tealDark : P.blueDark), fontSize: 11.5 });
  });

  b += noteBar({
    x: 34, y: 552, w: 1092, h: 38,
    text: '极端情况：当 τ → 0 时，最高分候选概率趋近 100%，等价于「贪心解码（Greedy Decoding）」；温度不改变模型权重，只改变采样时的“保守 vs 冒险”程度。',
  });

  return wrapSvg({
    width, height,
    title: '温度参数（Temperature τ）如何改变下一个 Token 的概率分布',
    subtitle: '同一组 Logits，在 τ = 0.4、1.0、2.0 下经过 Softmax 后的真实概率对比',
    badge: '§9.2 采样策略',
    body: b,
  });
}

export const figures = [
  { filename: '13_vae-latent-sampling.png', width: 1160, height: 640, render: fig13 },
  { filename: '14_gan-generator-discriminator.png', width: 1140, height: 600, render: fig14 },
  { filename: '15_diffusion-forward-reverse-process.png', width: 1140, height: 590, render: fig15 },
  { filename: '16_flow-matching-vs-diffusion.png', width: 1160, height: 610, render: fig16 },
  { filename: '27_agent-environment-reinforcement-loop.png', width: 1140, height: 580, render: fig27 },
  { filename: '17_bpe-tokenization.png', width: 1140, height: 610, render: fig17 },
  { filename: '18_tokenization-and-embedding.png', width: 1160, height: 560, render: fig18 },
  { filename: '19_temperature-next-token-distribution.png', width: 1160, height: 610, render: fig19 },
];
