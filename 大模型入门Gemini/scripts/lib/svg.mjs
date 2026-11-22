// Shared design system & SVG helper utilities for "大模型入门" lecture figures

export const PALETTE = {
  bg: '#FFFFFF',
  canvas: '#F8FAFC',
  card: '#FFFFFF',
  cardAlt: '#F1F5F9',
  border: '#CBD5E1',
  borderLight: '#E2E8F0',
  text: '#0F172A',
  textSec: '#475569',
  textMuted: '#64748B',

  blue: '#2563EB',
  blueDark: '#1D4ED8',
  blueLight: '#DBEAFE',
  bluePale: '#EFF6FF',

  teal: '#0D9488',
  tealDark: '#0F766E',
  tealLight: '#CCFBF1',
  tealPale: '#F0FDFA',

  amber: '#D97706',
  amberDark: '#B45309',
  amberLight: '#FEF3C7',
  amberPale: '#FFFBEB',

  violet: '#7C3AED',
  violetDark: '#6D28D9',
  violetLight: '#EDE9FE',
  violetPale: '#F5F3FF',

  rose: '#E11D48',
  roseDark: '#BE123C',
  roseLight: '#FFE4E6',
  rosePale: '#FFF1F2',

  emerald: '#059669',
  emeraldLight: '#D1FAE5',
  emeraldPale: '#ECFDF5',

  slate: '#334155',
  slateLight: '#E2E8F0',
};

export const FONT_SANS = "'Noto Sans SC', 'Microsoft YaHei', 'Segoe UI', sans-serif";
export const FONT_MONO = "'Consolas', 'Cascadia Code', monospace";

export function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function wrapSvg({ width = 1120, height = 640, title = '', subtitle = '', defs = '', body = '', badge = '' }) {
  const headerH = title ? (subtitle ? 74 : 52) : 0;
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    width: ${width}px;
    height: ${height}px;
    overflow: hidden;
    background: ${PALETTE.bg};
    font-family: ${FONT_SANS};
    -webkit-font-smoothing: antialiased;
  }
  svg { display: block; width: ${width}px; height: ${height}px; }
  text { font-family: ${FONT_SANS}; }
  .mono { font-family: ${FONT_MONO}; }
</style>
</head>
<body>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">
  <defs>
    <filter id="shadow-sm" x="-10%" y="-10%" width="125%" height="130%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0F172A" flood-opacity="0.06"/>
    </filter>
    <filter id="shadow-md" x="-12%" y="-12%" width="130%" height="135%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0F172A" flood-opacity="0.09"/>
    </filter>
    ${markerDef('arr-slate', '#475569')}
    ${markerDef('arr-blue', PALETTE.blue)}
    ${markerDef('arr-teal', PALETTE.teal)}
    ${markerDef('arr-amber', PALETTE.amber)}
    ${markerDef('arr-violet', PALETTE.violet)}
    ${markerDef('arr-rose', PALETTE.rose)}
    ${markerDef('arr-emerald', PALETTE.emerald)}
    ${markerDef('arr-muted', '#94A3B8')}
    ${defs}
  </defs>

  <!-- Background -->
  <rect x="0" y="0" width="${width}" height="${height}" fill="${PALETTE.bg}" />
  <rect x="12" y="12" width="${width - 24}" height="${height - 24}" rx="16" fill="${PALETTE.canvas}" stroke="${PALETTE.borderLight}" stroke-width="1.5" />

  ${title ? `
  <!-- Header -->
  <rect x="28" y="26" width="5" height="${subtitle ? 44 : 26}" rx="2.5" fill="${PALETTE.blue}" />
  <text x="44" y="47" font-size="21" font-weight="700" fill="${PALETTE.text}">${esc(title)}</text>
  ${subtitle ? `<text x="44" y="68" font-size="13.5" fill="${PALETTE.textSec}">${esc(subtitle)}</text>` : ''}
  ${badge ? `
  <rect x="${width - 178}" y="28" width="146" height="28" rx="14" fill="${PALETTE.bluePale}" stroke="${PALETTE.blueLight}" stroke-width="1.2" />
  <text x="${width - 105}" y="46.5" text-anchor="middle" font-size="12" font-weight="600" fill="${PALETTE.blueDark}">${esc(badge)}</text>
  ` : ''}
  <line x1="28" y1="${headerH + 10}" x2="${width - 28}" y2="${headerH + 10}" stroke="${PALETTE.borderLight}" stroke-width="1.2" />
  ` : ''}

  ${body}
</svg>
</body>
</html>`;
}

export function markerDef(id, color) {
  return `<marker id="${id}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 1 1.5 L 9 5 L 1 8.5 z" fill="${color}" />
  </marker>`;
}

export function box({ x, y, w, h, rx = 10, fill = '#FFFFFF', stroke = PALETTE.border, sw = 1.5, shadow = true, dash = '' }) {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" ${dash ? `stroke-dasharray="${dash}"` : ''} ${shadow ? 'filter="url(#shadow-sm)"' : ''} />`;
}

export function pill({ x, y, w, h = 26, fill = PALETTE.bluePale, stroke = PALETTE.blueLight, text = '', color = PALETTE.blueDark, fontSize = 12, bold = true }) {
  return `<g>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${h / 2}" fill="${fill}" stroke="${stroke}" stroke-width="1.2" />
    <text x="${x + w / 2}" y="${y + h / 2 + fontSize * 0.35}" text-anchor="middle" font-size="${fontSize}" font-weight="${bold ? 600 : 500}" fill="${color}">${esc(text)}</text>
  </g>`;
}

export function labelBox({ x, y, w, h, title, sub = '', fill = '#FFFFFF', stroke = PALETTE.border, titleColor = PALETTE.text, subColor = PALETTE.textSec, rx = 10, titleSize = 14, subSize = 11.5, shadow = true, sw = 1.6 }) {
  const cx = x + w / 2;
  const cy = y + h / 2;
  const tLines = String(title).split('\n');
  const sLines = sub ? String(sub).split('\n') : [];
  const tLineH = titleSize * 1.28;
  const sLineH = subSize * 1.38;
  const gap = sLines.length > 0 ? 5 : 0;
  const totalH = tLines.length * tLineH + gap + sLines.length * sLineH;
  let curY = cy - totalH / 2 + titleSize * 0.86;
  let textHtml = '';
  tLines.forEach((line, idx) => {
    textHtml += `<text x="${cx}" y="${(curY + idx * tLineH).toFixed(1)}" text-anchor="middle" font-size="${titleSize}" font-weight="700" fill="${titleColor}">${esc(line)}</text>`;
  });
  if (sLines.length > 0) {
    const sStart = curY + (tLines.length - 1) * tLineH + gap + sLineH * 0.85;
    sLines.forEach((line, idx) => {
      textHtml += `<text x="${cx}" y="${(sStart + idx * sLineH).toFixed(1)}" text-anchor="middle" font-size="${subSize}" fill="${subColor}">${esc(line)}</text>`;
    });
  }
  return `<g>
    ${box({ x, y, w, h, rx, fill, stroke, sw, shadow })}
    ${textHtml}
  </g>`;
}

export function arrow(x1, y1, x2, y2, { color = '#475569', marker = 'arr-slate', sw = 2, dash = '' } = {}) {
  return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${sw}" ${dash ? `stroke-dasharray="${dash}"` : ''} marker-end="url(#${marker})" />`;
}

export function pathArrow(d, { color = '#475569', marker = 'arr-slate', sw = 2, dash = '' } = {}) {
  return `<path d="${d}" fill="none" stroke="${color}" stroke-width="${sw}" ${dash ? `stroke-dasharray="${dash}"` : ''} stroke-linecap="round" stroke-linejoin="round" marker-end="url(#${marker})" />`;
}

export function vecBars({ x, y, vals, cellW = 14, cellH = 14, vertical = false, color = PALETTE.blue, stroke = '#FFFFFF', rx = 2 }) {
  let out = '<g>';
  vals.forEach((v, i) => {
    const opacity = Math.max(0.15, Math.min(1, v));
    const cx = vertical ? x : x + i * (cellW + 2);
    const cy = vertical ? y + i * (cellH + 2) : y;
    out += `<rect x="${cx}" y="${cy}" width="${cellW}" height="${cellH}" rx="${rx}" fill="${color}" fill-opacity="${opacity.toFixed(2)}" stroke="${stroke}" stroke-width="1" />`;
  });
  out += '</g>';
  return out;
}

export function noteBar({ x, y, w, h = 42, text, icon = '💡', fill = PALETTE.amberPale, stroke = PALETTE.amberLight, color = PALETTE.amberDark, fontSize = 13 }) {
  return `<g>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="${fill}" stroke="${stroke}" stroke-width="1.3" />
    <text x="${x + 16}" y="${y + h / 2 + 5}" font-size="${fontSize}" font-weight="600" fill="${color}">${esc(icon)}  ${esc(text)}</text>
  </g>`;
}

export function seededRand(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}
