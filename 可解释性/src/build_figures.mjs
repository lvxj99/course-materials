// Regenerate the handout's SVGs with Node.js: node src/build_figures.mjs
import assert from 'node:assert/strict';
import { mkdirSync, writeFileSync } from 'node:fs';

const output = new URL('../assets/', import.meta.url);
mkdirSync(output, { recursive: true });

const W = 960;
const C = {
  ink: '#172b44', muted: '#485e75', faint: '#6d8093', axis: '#91a4b7',
  grid: '#dce5ef', paper: '#f7f9fc', white: '#ffffff',
  blue: '#2866a0', blueLight: '#e7f0fa', teal: '#087e78', tealLight: '#dff4ef',
  orange: '#a74b22', orangeLight: '#faecdf', purple: '#66529d', purpleLight: '#eee8f8',
};
const esc = (s) => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const round = (n) => typeof n === 'number' ? Number(n.toFixed(2)) : n;
const attr = (p) => Object.entries(p)
  .filter(([, v]) => v !== undefined)
  .map(([k, v]) => ' ' + k + '="' + esc(round(v)) + '"').join('');
const svg = (tag, p, body) => '<' + tag + attr(p)
  + (body === undefined ? '/>' : '>' + body + '</' + tag + '>');
const t = (x, y, text, opts = {}) => svg('text', {
  x, y, fill: opts.color ?? C.ink, 'font-size': opts.size ?? 23,
  'font-weight': opts.weight ?? 500, 'text-anchor': opts.anchor,
}, esc(text));
const mid = (x, y, s, opts = {}) => t(x, y, s, { ...opts, anchor: 'middle' });
const rect = (x, y, width, height, opts = {}) => svg('rect', {
  x, y, width, height, rx: opts.radius, fill: opts.fill ?? C.white,
  stroke: opts.stroke, 'stroke-width': opts.sw, opacity: opts.opacity,
});
const dot = (cx, cy, r, fill, stroke, sw = 2) => svg('circle', {
  cx, cy, r, fill, stroke, 'stroke-width': stroke && sw,
});
const line = (x1, y1, x2, y2, stroke = C.grid, sw = 2, dash) => svg('line', {
  x1, y1, x2, y2, stroke, 'stroke-width': sw, 'stroke-dasharray': dash,
  'stroke-linecap': 'round',
});
const shape = (pts, { fill = 'none', stroke, sw, dash, closed = false } = {}) =>
  svg(closed ? 'polygon' : 'polyline', {
    points: pts.map((pt) => pt.map(round).join(',')).join(' '), fill, stroke,
    'stroke-width': sw, 'stroke-dasharray': dash, 'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
  });
const panel = (x, y, width, height) => rect(x, y, width, height, {
  radius: 14, stroke: C.grid, sw: 1.4,
});
const heading = (x, y, text, color = C.ink) =>
  t(x, y, text, { size: 25, weight: 650, color });

function arrow(x1, y1, x2, y2, color = C.blue, sw = 3) {
  const angle = Math.atan2(y2 - y1, x2 - x1);
  const point = (offset) => [x2 - 12 * Math.cos(angle + offset), y2 - 12 * Math.sin(angle + offset)];
  return line(x1, y1, x2, y2, color, sw)
    + shape([point(-0.55), [x2, y2], point(0.55)], { stroke: color, sw });
}

function strip(y, message, color = C.blue, fill = C.blueLight) {
  return rect(36, y, 888, 51, { fill, radius: 11 })
    + mid(W / 2, y + 33, message, { color, size: 23, weight: 600 });
}

function legendLine(x, y, message, color, dash) {
  return line(x, y - 8, x + 28, y - 8, color, 3.5, dash)
    + t(x + 38, y, message, { size: 21, color: C.muted });
}

function figure(n, slug, title, subtitle, height, body) {
  const doc = svg('svg', {
    xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 ' + W + ' ' + height,
    width: W, height, role: 'img', 'aria-labelledby': 'title desc', 'xml:lang': 'zh-CN',
  }, [
    svg('title', { id: 'title' }, esc(title)),
    svg('desc', { id: 'desc' }, esc(subtitle)),
    svg('style', {}, 'text{font-family:"Microsoft YaHei","PingFang SC","Noto Sans CJK SC",'
      + '"WenQuanYi Zen Hei",system-ui,sans-serif;font-variant-numeric:tabular-nums}'),
    rect(0, 0, W, height, { fill: C.paper }),
    rect(36, 24, 64, 38, { fill: C.blueLight, radius: 9 }),
    mid(68, 50, '图 ' + n, { size: 19, color: C.blue, weight: 650 }),
    t(117, 53, title, { size: 33, weight: 700 }),
    t(36, 94, subtitle, { size: 22, color: C.muted }),
    ...body,
  ].join('\n'));
  writeFileSync(new URL('fig_' + String(n).padStart(2, '0') + '_' + slug + '.svg', output), doc + '\n', 'utf8');
}

function plot(left, top, width, height, xRange, yRange, xTicks, yTicks) {
  const x = (v) => left + width * (v - xRange[0]) / (xRange[1] - xRange[0]);
  const y = (v) => top + height * (yRange[1] - v) / (yRange[1] - yRange[0]);
  const bottom = top + height;
  const right = left + width;
  const grid = rect(left, top, width, height)
    + xTicks.map((v) => line(x(v), top, x(v), bottom, C.grid, 1.2)).join('')
    + yTicks.map((v) => line(left, y(v), right, y(v), C.grid, 1.2)).join('');
  const axes = line(left, top, left, bottom, C.axis, 1.6)
    + line(left, bottom, right, bottom, C.axis, 1.6)
    + xTicks.map((v) => mid(x(v), bottom + 28, tick(v), { size: 20, color: C.muted })).join('')
    + yTicks.map((v) => t(left - 13, y(v) + 7, tick(v), {
      size: 20, color: C.muted, anchor: 'end',
    })).join('');
  return { x, y, grid, axes, points: (pairs) => pairs.map(([a, b]) => [x(a), y(b)]) };
}

function tick(n) {
  return String(n).replace('-', '−');
}

function curve(p, from, to, f, n = 80) {
  return p.points(Array.from({ length: n + 1 }, (_, i) => {
    const x = from + (to - from) * i / n;
    return [x, f(x)];
  }));
}

function waterfall(p, xs, levels, labels, width, font = 22) {
  const sections = levels.map((end, i) => {
    const total = i === 0 || i === levels.length - 1;
    const start = total ? 0 : levels[i - 1];
    const delta = end - start;
    const shade = total ? C.blue : delta < 0 ? C.orange : C.teal;
    const left = xs[i] - width / 2;
    const top = Math.min(p.y(start), p.y(end));
    const signed = total ? end.toFixed(1)
      : (delta < 0 ? '−' : '+') + Math.abs(delta).toFixed(1);
    return rect(left, top, width, Math.abs(p.y(start) - p.y(end)), { fill: shade, radius: 3 })
      + mid(xs[i], top - 12, signed, { color: shade, size: font, weight: 650 })
      + mid(xs[i], p.y(0) + 32, labels[i], { size: font, color: C.muted });
  });
  const connectors = xs.slice(0, -1).map((x, i) =>
    line(x + width / 2, p.y(levels[i]), xs[i + 1] - width / 2, p.y(levels[i]), C.axis, 1.6, '4 5'));
  return [...connectors, ...sections].join('');
}

function interpQuestions() {
  const center = [200, 278];
  const radius = 104;
  const sites = [];
  for (let i = -4; i <= 4; i++) {
    for (let j = -4; j <= 4; j++) {
      if (Math.hypot(i, j) * 0.225 <= 0.94) {
        sites.push(dot(center[0] + i * radius * 0.225, center[1] + j * radius * 0.225, 3.4, '#aabed1'));
      }
    }
  }
  const chosenX = center[0] + 0.9 * radius;
  const cards = [
    ['1', '这个 site 为什么预测偏大？', '拆开一条预测，看各项加了多少。', C.blue, C.blueLight],
    ['2', '温度在整批数据上有用吗？', '置换一列，看看测试误差升多少。', C.teal, C.tealLight],
    ['3', '调温度会让实测残差变小吗？', '在相近工况下，试两档温度。', C.purple, C.purpleLight],
  ];
  const right = cards.map(([n, title, sub, color, fill], i) => {
    const y = 126 + 113 * i;
    return panel(388, y, 536, 99)
      + dot(425, y + 34, 18, fill)
      + mid(425, y + 41, n, { size: 22, color, weight: 700 })
      + heading(457, y + 42, title, color)
      + t(457, y + 75, sub, { size: 22, color: C.muted });
  });
  figure(1, 'interp_questions', '一次预测，可以往三个方向查',
    '例子从一个边缘 site 的预测开始。', 479, [
      panel(36, 126, 328, 325),
      heading(59, 162, 'wafer 上的测点'),
      dot(...center, radius, '#f0f5fb', '#9bb4cb', 2),
      dot(...center, 60, 'none', '#d0dfed', 1),
      ...sites,
      dot(chosenX, center[1], 14, C.tealLight, C.teal, 2.4),
      dot(chosenX, center[1], 5, C.teal),
      mid(200, 424, '该点预测 +2.0 nm', { size: 25, color: C.teal, weight: 700 }),
      ...right,
    ]);
}

function linearAttribution() {
  const parts = [0.4 * 2, 2 * (0.9 - 0.5), -0.2 * 2];
  const levels = parts.reduce((acc, n) => [...acc, acc.at(-1) + n], [0.8]);
  assert.equal(round(levels.at(-1)), 2);
  const p = plot(115, 145, 766, 220, [0, 5], [0, 2.8], [], [0, 0.8, 1.6, 2.4]);
  figure(2, 'linear_attribution', '从参照值加到当前预测',
    '94 °C 的边缘测点 · 半径 0.9 · 压力高出参照 2 kPa', 486, [
      t(115, 131, '预测残差（nm）', { color: C.muted, size: 21 }),
      p.grid, p.axes,
      waterfall(p, [190, 345, 500, 655, 810], [...levels, levels.at(-1)],
        ['参照', '温度', '位置', '压力', '预测'], 94, 24),
      strip(420, '0.8  +  0.8  +  0.8  −  0.4  =  2.0 nm'),
    ]);
}

function treePath() {
  const node = (x, y, width, msg, active) => rect(x - width / 2, y, width, 58, {
    radius: 10, fill: active ? C.tealLight : C.white,
    stroke: active ? C.teal : C.grid, sw: active ? 2.3 : 1.6,
  }) + mid(x, y + 38, msg, { color: active ? C.teal : C.muted, size: 24, weight: 650 });
  figure(3, 'tree_path', '沿着条件走到叶子',
    '当前记录的温度为 94 °C，mark 类型为 AIM。', 474, [
      shape([[480, 191], [480, 224], [240, 224], [240, 252]], { stroke: C.axis, sw: 2.2 }),
      shape([[480, 191], [480, 224], [650, 224], [650, 252]], { stroke: C.teal, sw: 3.5 }),
      shape([[650, 309], [650, 341], [801, 341], [801, 373]], { stroke: C.axis, sw: 2.2 }),
      shape([[650, 309], [650, 341], [521, 341], [521, 373]], { stroke: C.teal, sw: 3.5 }),
      mid(343, 214, '否', { size: 22, color: C.muted }),
      mid(568, 214, '是', { size: 22, color: C.teal, weight: 700 }),
      mid(581, 331, '是', { size: 22, color: C.teal, weight: 700 }),
      mid(731, 331, '否', { size: 22, color: C.muted }),
      node(480, 133, 270, '温度 ≥ 93 °C？', true),
      node(240, 252, 206, '预测 +0.8 nm', false),
      node(650, 252, 242, 'mark 为 AIM？', true),
      node(521, 373, 215, '预测 +2.0 nm', true),
      node(801, 373, 203, '预测 +1.4 nm', false),
    ]);
}

function permutationImportance() {
  const temp = [0, 1, 2, 3];
  const perm = [2, 0, 3, 1].map((i) => temp[i]);
  const r = [0.2, 0.8, 0.4, 0.6];
  const y = [0.6, 2.4, 3, 4];
  const predict = (tempValues) => tempValues.map((v, i) => v + 2 * r[i]);
  const rmse = (values) => Math.sqrt(values.reduce((sum, v, i) => sum + (v - y[i]) ** 2, 0) / y.length);
  const score = rmse(predict(perm)) - rmse(predict(temp));
  assert.equal(score.toFixed(2), '1.19');

  function table(x, title, tempValues, color, tint) {
    const pred = predict(tempValues);
    const cellX = (i) => x + 43 + 84 * i;
    return panel(x, 127, 422, 305)
      + heading(x + 18, 164, title, color)
      + rect(cellX(1) - 39, 177, 78, 198, { fill: tint, radius: 8 })
      + ['site', '温差 t', '半径 r', '实测 y', '预测 ŷ'].map((s, i) =>
        mid(cellX(i), 202, s, { size: 20, weight: 650, color: i === 1 ? color : C.muted })).join('')
      + tempValues.map((v, i) => {
        const rowY = 241 + 39 * i;
        return line(x + 18, rowY - 25, x + 404, rowY - 25, C.grid, 1)
          + [i + 1, v, r[i].toFixed(1), y[i].toFixed(1), pred[i].toFixed(1)].map((value, col) =>
            mid(cellX(col), rowY, value, { size: 23, color: col === 1 ? color : C.ink })).join('');
      }).join('')
      + mid(x + 211, 411, 'RMSE  ' + rmse(pred).toFixed(2) + ' nm', {
        color, size: 25, weight: 650,
      });
  }

  figure(4, 'permutation_importance', '只换温差这一列的行顺序',
    '两边用同一个模型 f(t,r) = t + 2r，预测和实测均以 nm 记。', 508, [
      table(36, '原始留出集', temp, C.blue, C.blueLight),
      arrow(466, 274, 494, 274, C.orange),
      table(502, '一次随机置换', perm, C.orange, C.orangeLight),
      strip(445, '误差增量  ≈  1.39 − 0.20  =  1.19 nm', C.orange, C.orangeLight),
    ]);
}

function iceCurves() {
  const curves = [
    { press: -1.5, color: C.orange },
    { press: -0.5, color: C.purple },
    { press: 0.5, color: C.teal },
    { press: 1.5, color: C.blue },
  ];
  const temp = 1;
  const meanPress = curves.reduce((sum, { press }) => sum + press, 0) / curves.length;
  assert.equal(meanPress, 0);
  const p = plot(111, 171, 554, 270, [-2, 2], [-3.35, 3.35],
    [-2, -1, 0, 1, 2], [-3, -2, -1, 0, 1, 2, 3]);
  const signed = (v) => (v > 0 ? '+' : '') + tick(v);

  figure(5, 'ice_curves', '平均是平的，每条线仍在变化',
    '同一个 f(t,p) = t·p，每条线固定一条记录自己的压力偏差。', 536, [
      t(111, 155, '预测残差（nm）', { size: 21, color: C.muted }),
      p.grid,
      ...curves.map(({ press, color }) =>
        shape(p.points([[-2, -2 * press], [2, 2 * press]]), { stroke: color, sw: 3.5 })),
      line(p.x(-2), p.y(0), p.x(2), p.y(0), C.ink, 2.9, '8 7'),
      line(p.x(temp), 171, p.x(temp), 441, C.axis, 1.7, '5 5'),
      ...curves.map(({ press, color }) =>
        dot(p.x(temp), p.y(temp * press), 6.2, color, C.white, 1.6)),
      dot(p.x(temp), p.y(0), 5.6, C.ink, C.white, 1.6),
      p.axes,
      mid(388, 505, '温差 t', { size: 22, color: C.muted }),
      panel(704, 159, 220, 319),
      heading(725, 197, '在 t = 1 时'),
      mid(761, 230, '压力 p', { size: 20, color: C.muted }),
      mid(864, 230, '预测', { size: 20, color: C.muted }),
      ...curves.map(({ press, color }, i) => {
        const y = 266 + 38 * i;
        return mid(761, y, signed(press), { size: 23, color, weight: 650 })
          + mid(864, y, signed(temp * press), { size: 23, color, weight: 650 });
      }),
      line(724, 404, 903, 404, C.grid, 1.4),
      legendLine(727, 445, 'PDP 平均为 0', C.ink, '7 6'),
    ]);
}

function pdpAle() {
  const data = [];
  for (let i = -9; i <= 9; i++) {
    const temp = i * 0.20;
    const spread = 0.11 + Math.abs(i % 4) * 0.08;
    data.push([temp, temp - spread], [temp, temp + spread]);
  }
  const p = plot(96, 201, 323, 222, [-2.2, 2.2], [-2.25, 2.25],
    [-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2]);
  const q = plot(556, 201, 325, 222, [-2, 2], [-1, 1.6],
    [-2, -1, 0, 1, 2], [-1, 0, 1]);
  const replaced = data.filter((_, i) => i % 3 === 1);
  figure(6, 'pdp_ale', '把一列改成同一个值，还是只在附近比较？',
    '同一个模型 f(t,p) = t·p。温差 t 和压力偏差 p 通常一起变。', 542, [
      panel(36, 125, 432, 399), panel(492, 125, 432, 399),
      heading(57, 163, '先看输入组合'),
      t(96, 190, '压力偏差 p', { size: 20, color: C.muted }),
      p.grid,
      rect(p.x(0.5), 201, p.x(1) - p.x(0.5), 222, { fill: C.purpleLight, opacity: 0.8 }),
      ...data.map(([a, b]) => dot(p.x(a), p.y(b), 4.4, C.blue)),
      line(p.x(1.25), 201, p.x(1.25), 423, C.orange, 2, '5 5'),
      ...replaced.map(([, b]) => dot(p.x(1.25), p.y(b), 4.3, C.white, C.orange, 1.7)),
      p.axes,
      mid(258, 478, '温差 t', { size: 21, color: C.muted }),
      dot(66, 501, 5, C.white, C.orange, 1.8),
      t(79, 508, 'PDP 替换', { size: 20, color: C.orange }),
      rect(231, 492, 14, 16, { radius: 2, fill: C.purpleLight, stroke: C.purple }),
      t(253, 508, 'ALE 小区间', { size: 20, color: C.purple }),
      heading(513, 163, '再读两条响应曲线'),
      t(556, 190, '模型输出或效应（nm）', { size: 20, color: C.muted }),
      q.grid,
      shape(curve(q, -2, 2, (x) => x * x / 2 - 2 / 3), { stroke: C.purple, sw: 4 }),
      line(q.x(-2), q.y(0), q.x(2), q.y(0), C.orange, 3.4, '8 6'),
      q.axes,
      mid(720, 478, '温差 t', { size: 21, color: C.muted }),
      legendLine(545, 508, 'PDP', C.orange, '8 6'),
      legendLine(698, 508, 'ALE（居中）', C.purple),
    ]);
}

function shapWaterfall() {
  const f = (a, b) => 0.8 + 0.4 * a + 0.2 * b + 0.6 * a * b;
  const baseline = f(0, 0);
  const pred = f(1, 1);
  const orders = [
    { title: '先放入温度', between: f(1, 0), names: ['温度', '位置'] },
    { title: '先放入位置', between: f(0, 1), names: ['位置', '温度'] },
  ];
  const avgTemp = ((orders[0].between - baseline) + (pred - orders[1].between)) / 2;
  const avgPos = ((orders[1].between - baseline) + (pred - orders[0].between)) / 2;
  assert.equal(round(avgTemp), 0.7);
  assert.equal(round(avgPos), 0.5);
  assert.equal(round(baseline + avgTemp + avgPos), round(pred));
  const p = plot(551, 216, 348, 168, [0, 4], [0, 2.5], [], [0, 1, 2]);

  function path(order, y) {
    const amounts = [order.between - baseline, pred - order.between];
    const xs = [105, 263, 420];
    return heading(59, y, order.title)
      + [baseline, order.between, pred].map((value, i) =>
        rect(xs[i] - 33, y + 38, 66, 47, {
          fill: i === 1 ? C.paper : C.blueLight, radius: 8,
        }) + mid(xs[i], y + 69, value.toFixed(1), { size: 24, color: C.blue, weight: 650 })).join('')
      + amounts.map((value, i) => {
        const color = order.names[i] === '温度' ? C.teal : C.purple;
        return arrow(xs[i] + 39, y + 62, xs[i + 1] - 39, y + 62, color, 2.6)
          + mid((xs[i] + xs[i + 1]) / 2, y + 38,
            order.names[i] + ' +' + value.toFixed(1), { size: 19, color, weight: 600 });
      }).join('');
  }

  figure(7, 'shap_waterfall', '换个加入顺序，再平均每一项的贡献',
    '从低温、中心的参照走到高温、边缘的当前预测。', 514, [
      panel(36, 125, 449, 305), panel(505, 125, 419, 305),
      path(orders[0], 168),
      line(58, 273, 463, 273, C.grid, 1.4),
      path(orders[1], 313),
      heading(525, 167, '按顺序平均后的贡献'),
      t(551, 202, '预测残差（nm）', { size: 20, color: C.muted }),
      p.grid, p.axes,
      waterfall(p, [591, 678, 765, 852], [baseline, baseline + avgTemp, pred, pred],
        ['参照', '温度', '位置', '预测'], 55, 21),
      strip(445, '0.8  +  0.7  +  0.5  =  2.0 nm', C.teal, C.tealLight),
    ]);
}

function limeLocalSurrogate() {
  const f = (x) => 1.2 + 0.24 * x * x + 0.36 * Math.sin(1.7 * x);
  const target = 1.2;
  const width = 0.55;
  const rows = Array.from({ length: 29 }, (_, i) => {
    const x = -2.4 + 0.2 * i;
    return { x, y: f(x), w: Math.exp(-0.5 * ((x - target) / width) ** 2) };
  });
  const totalWeight = rows.reduce((sum, d) => sum + d.w, 0);
  const meanX = rows.reduce((sum, d) => sum + d.x * d.w, 0) / totalWeight;
  const meanY = rows.reduce((sum, d) => sum + d.y * d.w, 0) / totalWeight;
  const cov = rows.reduce((sum, d) => sum + d.w * (d.x - meanX) * (d.y - meanY), 0);
  const variance = rows.reduce((sum, d) => sum + d.w * (d.x - meanX) ** 2, 0);
  const g = (x) => meanY + cov / variance * (x - meanX);
  const p = plot(117, 158, 747, 240, [-2.5, 3.3], [0.55, 4], [-2, -1, 0, 1, 2, 3], [1, 2, 3, 4]);
  figure(8, 'lime_local_surrogate', '给近处的点更大的权重',
    '用一条局部直线，读温差 z = 1.2 附近的预测变化。', 504, [
      t(117, 144, '预测残差（nm）', { size: 20, color: C.muted }),
      p.grid,
      rect(p.x(target - 0.7), 158, p.x(target + 0.7) - p.x(target - 0.7), 240, {
        fill: C.orangeLight, opacity: 0.75,
      }),
      line(p.x(target), 158, p.x(target), 398, C.axis, 1.5, '5 5'),
      shape(curve(p, -2.5, 3.3, f), { stroke: C.blue, sw: 3.8 }),
      ...rows.map(({ x, y, w }) =>
        dot(p.x(x), p.y(y), 2.6 + 6.2 * Math.sqrt(w), C.blueLight, C.blue, 1.5)),
      shape(p.points([[0.43, g(0.43)], [1.97, g(1.97)]]), { stroke: C.orange, sw: 4.3 }),
      dot(p.x(target), p.y(f(target)), 11, 'none', C.ink, 2.6),
      p.axes,
      mid(491, 454, '温差 z', { size: 21, color: C.muted }),
      legendLine(117, 482, '原模型', C.blue),
      legendLine(327, 482, '局部拟合', C.orange),
      dot(576, 474, 7, C.blueLight, C.blue, 1.5),
      t(594, 482, '点越大，拟合权重越高', { size: 21, color: C.muted }),
    ]);
}

function counterfactual() {
  const current = [2, 0];
  const normal = [2, -1]; // The target boundary is 2t - d = 1.
  const excess = normal[0] * current[0] + normal[1] * current[1] - 1;
  const normalSq = normal[0] ** 2 + normal[1] ** 2;
  const near = current.map((v, i) => v - normal[i] * excess / normalSq);
  const feasible = [1, 1];
  const f = (temp, dose) => 0.8 + 0.4 * temp - 0.2 * dose;
  assert.deepEqual(near.map(round), [0.8, 0.6]);
  assert.deepEqual([current, near, feasible].map((pt) => round(f(...pt))), [1.6, 1, 1]);
  const p = plot(108, 164, 420, 350, [0.3, 3.3], [0, 2.5],
    [0.5, 1, 1.5, 2, 2.5, 3], [0, 1, 2]);
  const point = (pt, n, color) => dot(p.x(pt[0]), p.y(pt[1]), 12, color, C.white, 1.6)
    + mid(p.x(pt[0]), p.y(pt[1]) + 6, n, { size: 16, weight: 700, color: C.white });
  const description = (y, number, title, sub, color) => dot(609, y - 8, 13, color)
    + mid(609, y - 2, number, { size: 17, color: C.white, weight: 700 })
    + t(631, y, title, { size: 22, weight: 650, color })
    + t(631, y + 31, sub, { size: 20, color: C.muted });

  figure(9, 'counterfactual', '找得到达标点，还要看能调到哪里',
    '目标是预测 ≤ 1.0 nm。绿区表示达标，蓝框表示允许的设定。', 603, [
      t(108, 149, '剂量设定 d', { size: 21, color: C.muted }),
      p.grid,
      shape(p.points([[0.3, 0], [0.5, 0], [1.75, 2.5], [0.3, 2.5]]), {
        closed: true, fill: C.tealLight,
      }),
      shape(p.points([[1, 1], [1.5, 2], [1, 2]]), { closed: true, fill: '#98d8c5' }),
      shape(p.points([[0.5, 0], [1.75, 2.5]]), { stroke: C.teal, sw: 2.7 }),
      rect(p.x(1), p.y(2), p.x(3) - p.x(1), p.y(0) - p.y(2), {
        fill: 'none', stroke: C.blue, sw: 2.4,
      }),
      p.axes,
      shape(p.points([current, near]), { stroke: C.orange, sw: 2.9, dash: '7 6' }),
      shape(p.points([current, feasible]), { stroke: C.blue, sw: 3 }),
      point(current, '1', C.ink), point(near, '2', C.orange), point(feasible, '3', C.blue),
      mid(318, 574, '温度设定 t', { size: 21, color: C.muted }),
      description(213, '1', '当前设定 (2, 0)', '预测 1.6 nm', C.ink),
      description(319, '2', '最近达标点 (0.8, 0.6)', '越过温度下限', C.orange),
      description(425, '3', '可调范围内最近 (1, 1)', '预测 1.0 nm', C.blue),
    ]);
}

function integratedGradients() {
  const f = (s) => 2 * s - s * s;
  const df = (s) => 2 - 2 * s;
  assert.equal((df(0) + df(1)) / 2, f(1) - f(0));
  const p = plot(98, 206, 328, 182, [0, 1], [0, 1.2], [0, 0.5, 1], [0, 0.5, 1]);
  const q = plot(554, 206, 328, 182, [0, 1], [0, 2.2], [0, 0.5, 1], [0, 1, 2]);
  figure(10, 'integrated_gradients', '终点已经平了，路上仍然有变化',
    '从参照 s = 0 走到输入 s = 1，比较输出高度和沿途斜率。', 486, [
      panel(36, 125, 432, 338), panel(492, 125, 432, 338),
      heading(59, 165, '输出  f(s) = 2s − s²'),
      p.grid,
      shape(curve(p, 0, 1, f), { stroke: C.blue, sw: 4 }),
      line(p.x(0.56), p.y(1), p.x(1), p.y(1), C.orange, 2.3, '6 5'),
      p.axes,
      dot(p.x(0), p.y(0), 5.5, C.blue, C.white, 1),
      dot(p.x(1), p.y(1), 6, C.orange, C.white, 1),
      t(202, 222, '终点斜率 = 0', { size: 21, color: C.orange, weight: 650 }),
      mid(262, 442, '输入 s', { size: 21, color: C.muted }),
      heading(514, 165, '斜率  f′(s) = 2 − 2s'),
      q.grid,
      shape(q.points([[0, 0], [0, 2], [1, 0]]), { closed: true, fill: C.tealLight }),
      shape(curve(q, 0, 1, df, 1), { stroke: C.teal, sw: 4 }),
      q.axes,
      t(595, 357, '面积 = 1', { size: 24, color: C.teal, weight: 700 }),
      mid(717, 442, '路径位置 s', { size: 21, color: C.muted }),
    ]);
}

function attentionWeightValue() {
  const weights = [0.8, 0.2];
  const values = [0.2, 2];
  const products = weights.map((a, i) => a * values[i]);
  const total = products.reduce((sum, v) => sum + v, 0);
  assert.equal(round(total), 0.56);
  const cols = [338, 548, 764];
  function valueBar(x, y, value, max, color, tint) {
    return mid(x, y + 43, value.toFixed(2), { size: 29, color, weight: 700 })
      + rect(x - 65, y + 58, 130, 10, { fill: tint, radius: 5 })
      + rect(x - 65, y + 58, 130 * value / max, 10, { fill: color, radius: 5 });
  }
  figure(11, 'attention_weight_value', '权重乘上值，才是传来的量',
    '一个注意力头读两个位置。用标量演示一次加权求和。', 464, [
      ...['权重 aᵢ', '值 vᵢ', '乘积 aᵢvᵢ'].map((name, i) =>
        mid(cols[i], 153, name, { size: 24, color: C.muted, weight: 650 })),
      ...weights.map((a, i) => {
        const y = 173 + 104 * i;
        return panel(36, y, 888, 92)
          + heading(63, y + 53, '位置 ' + (i + 1))
          + valueBar(cols[0], y, a, 1, C.blue, C.blueLight)
          + mid(441, y + 49, '×', { size: 27, color: C.faint })
          + valueBar(cols[1], y, values[i], 2, C.teal, C.tealLight)
          + mid(656, y + 49, '=', { size: 27, color: C.faint })
          + valueBar(cols[2], y, products[i], 0.5, C.purple, C.purpleLight);
      }),
      strip(390, '相加得到这个头的输出  0.16 + 0.40 = ' + total.toFixed(2), C.purple, C.purpleLight),
    ]);
}

function observeIntervene() {
  const states = [
    { name: '常态', low: 1.0, high: 0.6, color: C.blue },
    { name: '偏移态', low: 2.2, high: 1.8, color: C.orange },
  ];
  const groups = [
    { name: '低温日志', counts: [8, 2], setting: 'low' },
    { name: '高温日志', counts: [2, 8], setting: 'high' },
  ];
  const mean = (counts, setting) => counts.reduce((sum, n, i) => sum + n * states[i][setting], 0)
    / counts.reduce((sum, n) => sum + n, 0);
  const balanced = ['low', 'high'].map((setting) => mean([5, 5], setting));
  assert.deepEqual(groups.map((g) => round(mean(g.counts, g.setting))), [1.24, 1.56]);
  assert.deepEqual(balanced.map(round), [1.6, 1.2]);
  const p = plot(554, 209, 330, 194, [-0.24, 1.24], [0.4, 2.5], [], [0.5, 1, 1.5, 2, 2.5]);
  const lines = [
    ...states.map(({ low, high, color }) => ({ ends: [low, high], color })),
    { ends: balanced, color: C.purple, dash: '7 6' },
  ];
  figure(12, 'observe_intervene', '工况占比一变，总平均的方向也会变',
    '把不同工况混在一起看，与让两组面对同样工况，得到两个方向。', 546, [
      panel(36, 125, 432, 400), panel(492, 125, 432, 400),
      heading(57, 164, '直接比较两组日志'),
      ...groups.map((g, i) => {
        const y = 206 + 125 * i;
        return t(64, y, g.name, { size: 24, weight: 650 })
          + Array.from({ length: 10 }, (_, j) =>
            rect(66 + j * 34, y + 17, 24, 24, {
              fill: states[j < g.counts[0] ? 0 : 1].color, radius: 4,
            })).join('')
          + t(64, y + 78, '平均 ' + mean(g.counts, g.setting).toFixed(2) + ' nm',
            { size: 25, color: C.ink, weight: 650 });
      }),
      line(62, 305, 436, 305, C.grid, 1.3),
      rect(65, 477, 17, 17, { fill: C.blue, radius: 3 }),
      t(92, 493, '常态', { size: 22, color: C.muted }),
      rect(228, 477, 17, 17, { fill: C.orange, radius: 3 }),
      t(255, 493, '偏移态', { size: 22, color: C.muted }),
      heading(513, 164, '在相同工况内比较'),
      t(554, 198, '实测残差（nm）', { size: 20, color: C.muted }),
      p.grid,
      ...lines.map(({ ends, color, dash }) =>
        shape(p.points(ends.map((v, i) => [i, v])), { stroke: color, sw: 3.6, dash })
        + ends.map((v, i) => dot(p.x(i), p.y(v), 5.4, color, C.white, 1.3)
          + t(p.x(i) + 12, p.y(v) - 12, v.toFixed(2), {
            size: 20, color, weight: 650,
          })).join('')),
      p.axes,
      mid(p.x(0), 438, '低温', { size: 22, color: C.muted }),
      mid(p.x(1), 438, '高温', { size: 22, color: C.muted }),
      legendLine(555, 493, '两种工况各占一半', C.purple, '7 6'),
    ]);
}

function permutations(items) {
  if (items.length === 0) return [[]];
  return items.flatMap((item, i) =>
    permutations(items.filter((_, j) => i !== j)).map((rest) => [item, ...rest]));
}

function correlatedAttribution() {
  const temp = [-1, -1, 1, 1];
  const orders = permutations([0, 1, 2, 3]);
  function permutationMse(tempWeight, backupWeight) {
    const average = orders.reduce((sum, order) => {
      const mse = temp.reduce((rowSum, value, i) =>
        rowSum + ((tempWeight + backupWeight) * (temp[order[i]] - value)) ** 2, 0) / temp.length;
      return sum + mse;
    }, 0) / orders.length;
    return average;
  }
  const bars = [
    ['模型 A · 温度', permutationMse(3, 0), C.blue],
    ['模型 B · 温度', permutationMse(1.5, 0), C.teal],
    ['模型 B · 备份', permutationMse(0, 1.5), C.teal],
    ['模型 B · 两列成组', permutationMse(1.5, 1.5), C.purple],
  ];
  assert.deepEqual(bars.map((bar) => bar[1]), [18, 4.5, 4.5, 18]);
  const p = plot(281, 132, 538, 252, [0, 18], [0, 4], [0, 4.5, 9, 13.5, 18], []);
  figure(13, 'correlated_attribution', '重复的温度信息，分到两列以后',
    'A 只用温度。B 同时用温度和完全相同的备份。两个模型的原始 MSE 都为 0。', 482, [
      panel(36, 119, 888, 343),
      p.grid,
      ...bars.map(([name, value, color], i) => {
        const y = 165 + 61 * i;
        return t(57, y + 8, name, { size: 23, color })
          + rect(p.x(0), y - 15, p.x(value) - p.x(0), 30, { fill: color, radius: 4 })
          + t(p.x(value) + 12, y + 8, tick(value), { size: 23, weight: 650, color });
      }),
      p.axes,
      mid(550, 445, '打乱后的 MSE 增量（nm²）', { size: 22, color: C.muted }),
    ]);
}

function faithfulnessDeletion() {
  const score = ([temp, press]) => 0.8 + 0.8 * temp + 0.4 * press;
  const after = (order, k) => {
    const x = [1, 1, 1];
    order.slice(0, k).forEach((j) => { x[j] = 0; });
    return score(x);
  };
  const order = [0, 1, 2];
  const all = permutations(order);
  const steps = [0, 1, 2, 3];
  const byExplain = steps.map((k) => after(order, k));
  const atRandom = steps.map((k) => all.reduce((sum, ord) => sum + after(ord, k), 0) / all.length);
  assert.deepEqual(byExplain.map(round), [2, 1.2, 0.8, 0.8]);
  assert.deepEqual(atRandom.map(round), [2, 1.6, 1.2, 0.8]);
  const p = plot(118, 167, 747, 226, [-0.10, 3.10], [0.62, 2.18],
    steps, [0.8, 1.2, 1.6, 2]);
  figure(14, 'faithfulness_deletion', '按解释指出的顺序替换，分数降得多快？',
    '固定一条样本和一个模型，每次再把一项替换成参照值 0。', 492, [
      t(118, 151, '预测残差（nm）', { size: 21, color: C.muted }),
      legendLine(448, 151, '解释顺序', C.blue),
      legendLine(642, 151, '随机顺序平均', C.purple, '8 6'),
      p.grid,
      shape(p.points(steps.map((k) => [k, byExplain[k]])), { stroke: C.blue, sw: 4.2 }),
      shape(p.points(steps.map((k) => [k, atRandom[k]])), { stroke: C.purple, sw: 3.5, dash: '8 6' }),
      ...steps.map((k) => dot(p.x(k), p.y(atRandom[k]), 7.6, C.white, C.purple, 2.6)
        + dot(p.x(k), p.y(byExplain[k]), 5.3, C.blue, C.white, 0.9)),
      p.axes,
      mid(492, 459, '已替换为参照值的项数', { size: 22, color: C.muted }),
    ]);
}

function waferDiagnosis() {
  const settings = [
    { t: -1, p: -1, count: 3 },
    { t: -1, p: 1, count: 1 },
    { t: 1, p: -1, count: 1 },
    { t: 1, p: 1, count: 3 },
  ].flatMap(({ t, p, count }) => Array.from({ length: count }, () => ({ t, p })));

  const batch = (firstWafer) => settings.flatMap(({ t, p }, i) =>
    Array.from({ length: 8 }, (_, j) => {
      const e = Number(j >= 6);
      const noise = j % 2 === 0 ? -0.1 : 0.1;
      return { wafer: firstWafer + i, t, p, e, y: 2 + 0.6 * t + 0.4 * p + 0.4 * e + 0.8 * t * e + noise };
    }));
  const training = batch(1);
  const diagnosis = batch(9);
  const final = batch(17);
  assert.equal(new Set([...training, ...diagnosis, ...final].map(({ wafer }) => wafer)).size, 24);

  const mean = (rows, read) => rows.reduce((sum, row) => sum + read(row), 0) / rows.length;
  const measure = (rows) => mean(rows, (row) => row.y);
  const byRegion = (rows, edge) => rows.filter(({ e }) => e === edge);
  const tempResponse = (rows) =>
    measure(rows.filter(({ t, p }) => t === 1 && p === 1))
      - measure(rows.filter(({ t, p }) => t === -1 && p === 1));
  const regionSlopes = [0, 1].map((e) => tempResponse(byRegion(training, e)) / 2);
  const center = measure(byRegion(training, 0));
  const edgeOffset = measure(byRegion(training, 1)) - center;
  const pressureSlope = (measure(training.filter(({ t, p }) => t === 1 && p === 1))
    - measure(training.filter(({ t, p }) => t === 1 && p === -1))) / 2;
  const tempSlope = mean(training, ({ e }) => regionSlopes[e]);
  const predict = ({ t, p, e }) => center + tempSlope * t + pressureSlope * p + edgeOffset * e;
  const refit = ({ t, p, e }) => center + regionSlopes[e] * t + pressureSlope * p + edgeOffset * e;

  // In this balanced design the group contrasts give the least-squares fits.
  const linearColumns = [() => 1, ({ t }) => t, ({ p }) => p, ({ e }) => e];
  for (const read of linearColumns) {
    assert.ok(Math.abs(mean(training, (row) => (row.y - predict(row)) * read(row))) < 1e-10);
  }
  for (const read of [...linearColumns, ({ t, e }) => t * e]) {
    assert.ok(Math.abs(mean(training, (row) => (row.y - refit(row)) * read(row))) < 1e-10);
  }
  assert.deepEqual([center, tempSlope, pressureSlope, edgeOffset, ...regionSlopes].map(round),
    [2, 0.8, 0.4, 0.4, 0.6, 1.4]);

  const mse = (rows, f) => mean(rows, (row) => (row.y - f(row)) ** 2);
  const baseline = mse(diagnosis, predict);
  const byPosition = [0, 1].map((e) => Math.sqrt(mse(byRegion(diagnosis, e), predict)));
  assert.deepEqual([baseline, Math.sqrt(baseline), ...byPosition].map(round), [0.13, 0.36, 0.22, 0.61]);

  function permutedMse(copyTemp, copyPressure) {
    // Each recipient wafer gets each donor once, as it does in the uniform permutation average.
    return mean(diagnosis, (row) => mean(settings, (donor) => {
      const t = copyTemp ? donor.t : row.t;
      const p = copyPressure ? donor.p : row.p;
      return (row.y - predict({ t, p, e: row.e })) ** 2;
    }));
  }
  assert.deepEqual([permutedMse(true, false), permutedMse(false, true), permutedMse(true, true)].map(round),
    [1.41, 0.45, 2.37]);
  assert.deepEqual([predict({ t: 0, p: 0, e: 0.25 }), predict({ t: 1, p: 1, e: 1 }),
    predict({ t: -1, p: -1, e: 1 })].map(round), [2.1, 3.6, 1.2]);
  assert.ok(diagnosis.some(({ t, p, e, y }) => t === 1 && p === 1 && e === 1 && round(y) === 4.3));

  const changes = [0, 1].map((e) => tempResponse(byRegion(diagnosis, e)));
  const predictedChanges = [0, 1].map((e) => predict({ t: 1, p: 1, e }) - predict({ t: -1, p: 1, e }));
  assert.deepEqual([...changes, ...predictedChanges].map(round), [1.2, 2.8, 1.6, 1.6]);
  assert.deepEqual([Math.sqrt(mse(final, predict)), Math.sqrt(mse(final, refit))].map(round), [0.36, 0.10]);

  const p = plot(104, 200, 295, 220, [0, 2], [0, 0.72], [], [0, 0.2, 0.4, 0.6]);
  const q = plot(610, 200, 260, 220, [0, 3], [0, 4], [0, 1, 2, 3], []);
  const regions = ['中心区', '边缘'];
  const colors = [C.blue, C.orange];

  figure(15, 'wafer_diagnosis', '边缘误差大，温度响应差在哪儿',
    '同一批诊断 wafer，左侧按位置看误差，右侧比较低温到高温的变化。', 534, [
      panel(36, 125, 432, 382), panel(492, 125, 432, 382),
      heading(57, 165, '按位置拆开 RMSE'),
      t(104, 190, 'RMSE（nm）', { size: 21, color: C.muted }),
      p.grid,
      ...byPosition.map((value, i) => {
        const x = 183 + 143 * i;
        return rect(x - 40, p.y(value), 80, p.y(0) - p.y(value), { fill: colors[i], radius: 4 })
          + mid(x, p.y(value) - 11, value.toFixed(2), { size: 23, color: colors[i], weight: 650 })
          + mid(x, 451, regions[i], { size: 22, color: C.muted });
      }),
      p.axes,
      mid(252, 484, '全部测点的 RMSE 为 ' + Math.sqrt(baseline).toFixed(2) + ' nm',
        { size: 21, color: C.muted }),
      heading(513, 165, '固定高压档，比温差响应'),
      t(610, 190, '低温到高温的增量（nm）', { size: 20, color: C.muted }),
      q.grid,
      ...changes.map((value, i) => {
        const y = 229 + 106 * i;
        const bar = (amount, barY, color) =>
          rect(q.x(0), barY, q.x(amount) - q.x(0), 21, { fill: color, radius: 4 })
          + t(q.x(amount) + 9, barY + 18, amount.toFixed(1), { size: 20, color, weight: 650 });
        return t(514, y + 28, regions[i], { size: 22, color: C.ink })
          + bar(value, y, C.blue) + bar(predictedChanges[i], y + 33, C.purple);
      }),
      q.axes,
      rect(527, 468, 23, 15, { fill: C.blue, radius: 3 }),
      t(559, 483, '量测均值增量', { size: 20, color: C.muted }),
      rect(716, 468, 23, 15, { fill: C.purple, radius: 3 }),
      t(748, 483, '加法模型', { size: 20, color: C.muted }),
    ]);
}

function activationPatching() {
  const reference = 3;
  const control = -2;
  const patched = 1.5;
  const restored = (patched - control) / (reference - control);
  assert.equal(restored, 0.7);
  const signed = (n) => (n < 0 ? '−' : '+') + Math.abs(n).toFixed(1);
  const runs = [
    { name: '参考', prompt: 'A 递文件', state: '参考向量', score: reference, color: C.blue, tint: C.blueLight },
    { name: '对照', prompt: 'B 递文件', state: '对照向量', score: control, color: C.orange, tint: C.orangeLight },
    { name: '替换后', prompt: 'B 递文件', state: '参考向量', score: patched, color: C.teal, tint: C.tealLight },
  ];
  const rowTop = [164, 263, 362];

  figure(16, 'activation_patching', '只替换一格，再看答案分数',
    '把参考运行中读到的向量，放进对照运行的同一层、同一位置。', 540, [
      ...runs.map((_, i) => panel(36, rowTop[i], 888, 80)),
      mid(111, 145, '运行', { size: 21, color: C.muted }),
      mid(251, 145, '提示里的改动', { size: 21, color: C.muted }),
      mid(507, 145, '第 ℓ 层 · 答案槽前', { size: 21, color: C.muted }),
      mid(805, 145, 'B − A 的 logit 差', { size: 21, color: C.muted }),
      shape([[614, 204], [661, 204], [661, 402]], { stroke: C.blue, sw: 2.5, dash: '5 5' }),
      arrow(661, 402, 614, 402, C.blue, 2.6),
      mid(661, 190, '复制', { size: 19, color: C.blue, weight: 650 }),
      ...runs.map((run, i) => {
        const y = rowTop[i];
        const fromControl = i === 1;
        return rect(56, y + 21, 110, 38, { fill: run.tint, radius: 8 })
          + mid(111, y + 48, run.name, { size: 23, color: run.color, weight: 650 })
          + mid(251, y + 48, run.prompt, { size: 25, weight: 600 })
          + arrow(327, y + 40, 381, y + 40, C.axis, 2.2)
          + rect(401, y + 15, 212, 50, { fill: fromControl ? C.orangeLight : C.blueLight, radius: 9 })
          + mid(507, y + 48, run.state, {
            size: 24, color: fromControl ? C.orange : C.blue, weight: 650,
          })
          + arrow(697, y + 40, 736, y + 40, C.axis, 2.2)
          + mid(805, y + 51, signed(run.score), { size: 32, color: run.color, weight: 700 });
      }),
      strip(468, '恢复比例  (1.5 − (−2.0)) ÷ (3.0 − (−2.0)) = ' + (100 * restored).toFixed(0) + '%',
        C.teal, C.tealLight),
    ]);
}

function sparseFeatureDirections() {
  const features = [
    { name: 'd₁', direction: [1, 0], amount: 1, amountName: 'z₁', color: C.teal, tint: C.tealLight },
    { name: 'd₂', direction: [0, 1], amount: 0, amountName: 'z₂', color: C.muted, tint: C.paper },
    { name: 'd₃', direction: [0.6, 0.8], amount: 0.5, amountName: 'z₃', color: C.purple, tint: C.purpleLight },
  ];
  const h = [0, 1].map((i) =>
    features.reduce((sum, feature) => sum + feature.amount * feature.direction[i], 0));
  const withoutThird = h.map((v, i) => v - features[2].amount * features[2].direction[i]);
  assert.deepEqual(h.map(round), [1.3, 0.4]);
  assert.deepEqual(withoutThird.map(round), [1, 0]);

  const p = plot(99, 198, 325, 213, [-0.1, 1.525], [-0.15, 0.915], [0, 0.5, 1, 1.5], [0, 0.4, 0.8]);
  const vector = (start, end, color) => arrow(p.x(start[0]), p.y(start[1]), p.x(end[0]), p.y(end[1]), color, 3.4);
  figure(17, 'sparse_feature_directions', '把一条激活向量拆成少量方向',
    '字典里有三个方向。这次取两个方向，各自乘上激活量再相加。', 534, [
      panel(36, 125, 432, 328), panel(492, 125, 432, 328),
      heading(57, 165, '沿两个方向相加'),
      p.grid,
      line(p.x(0), p.y(-0.15), p.x(0), p.y(0.915), C.axis, 1.5),
      line(p.x(-0.1), p.y(0), p.x(1.525), p.y(0), C.axis, 1.5),
      vector([0, 0], h, C.blue),
      vector([0, 0], withoutThird, C.teal),
      vector(withoutThird, h, C.purple),
      p.axes,
      dot(p.x(0), p.y(0), 4.5, C.ink),
      mid(212, 329, 'h = (1.3, 0.4)', { size: 21, color: C.blue, weight: 650 }),
      mid(227, 405, '1.0 d₁', { size: 20, color: C.teal, weight: 650 }),
      t(364, 364, '0.5 d₃', { size: 20, color: C.purple, weight: 650 }),
      heading(513, 165, '这次亮了哪几项'),
      mid(625, 204, '字典方向', { size: 21, color: C.muted }),
      mid(817, 204, '激活量', { size: 21, color: C.muted }),
      ...features.map((feature, i) => {
        const y = 218 + i * 70;
        return rect(512, y, 390, 54, { fill: feature.tint, radius: 9 })
          + mid(625, y + 35, feature.name + ' = (' + feature.direction.join(', ') + ')', {
            size: 24, color: feature.color, weight: 650,
          })
          + mid(817, y + 35, feature.amountName + ' = ' + feature.amount.toFixed(1), {
            size: 24, color: feature.color, weight: 650,
          });
      }),
      strip(468, '把 z₃ 设为 0，从 h 中减去 0.5 d₃，得到 h′ = (1, 0)', C.purple, C.purpleLight),
    ]);
}

interpQuestions();
linearAttribution();
treePath();
permutationImportance();
iceCurves();
pdpAle();
shapWaterfall();
limeLocalSurrogate();
counterfactual();
integratedGradients();
attentionWeightValue();
observeIntervene();
correlatedAttribution();
faithfulnessDeletion();
waferDiagnosis();
activationPatching();
sparseFeatureDirections();
