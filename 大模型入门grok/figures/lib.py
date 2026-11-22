"""Distill-style SVG primitives for the lecture figures.

Color is a code, not decoration:
  blue   attention, queries, encoder stream
  teal   keys, memory, retrieval
  orange current token, values, decoder stream
  green  feed-forward, clean data, reconstruction
  purple position, normalization
  red    masks, constraints
  gold   rewards, selected operating points
  gray   frozen weights, cache, unselected paths
"""

from __future__ import annotations

import html
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images"

INK = "#1F2A30"
MUTED = "#526068"
FAINT = "#6A767C"
LINE = "#E3E0DA"
PAPER = "#FFFFFF"
PANEL = "#F6F5F2"

BLUE = "#4C78A8"
TEAL = "#3E9B96"
ORANGE = "#E07B2A"
GREEN = "#4E8C46"
PURPLE = "#8E6899"
RED = "#D4544E"
GOLD = "#C4922A"
GRAY = "#8A847C"

TONES = {
    "ink": INK,
    "blue": BLUE,
    "teal": TEAL,
    "orange": ORANGE,
    "green": GREEN,
    "purple": PURPLE,
    "red": RED,
    "gold": GOLD,
    "gray": GRAY,
    "neutral": "#C9C4BC",
}

SANS = "'Segoe UI', 'Microsoft YaHei', Helvetica, Arial, sans-serif"
SERIF = "Georgia, 'Palatino Linotype', 'Songti SC', serif"


def tone(name: str) -> str:
    return TONES.get(name, name)


def text_width(s: str, size: float) -> float:
    w = 0.0
    for ch in s:
        o = ord(ch)
        if ch == " ":
            w += size * 0.33
        elif ch in ".,;:|!'":
            w += size * 0.28
        elif ch in "il1":
            w += size * 0.32
        elif ch in "mwMW@%":
            w += size * 0.9
        elif o > 0x2E80:
            w += size * 1.02
        elif ch.isupper():
            w += size * 0.68
        else:
            w += size * 0.56
    return w


def wrap_text(text: str, width: float, size: float) -> list[str]:
    """Wrap on spaces and CJK boundaries, keeping ASCII words intact."""
    lines: list[str] = []
    for para in text.split("\n"):
        tokens: list[str] = []
        buf = ""
        for ch in para:
            if ord(ch) < 128 and not ch.isspace():
                buf += ch
            else:
                if buf:
                    tokens.append(buf)
                    buf = ""
                tokens.append(ch)
        if buf:
            tokens.append(buf)
        cur = ""
        for tok in tokens:
            trial = cur + tok
            if cur and text_width(trial, size) > width:
                lines.append(cur.rstrip())
                cur = "" if tok == " " else tok
            else:
                cur = trial
        lines.append(cur)
    return lines


def _hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def lerp(a: str, b: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    ar, ag, ab = _hex_rgb(a)
    br, bg, bb = _hex_rgb(b)
    r = round(ar + (br - ar) * t)
    g = round(ag + (bg - ag) * t)
    bch = round(ab + (bb - ab) * t)
    return f"#{r:02x}{g:02x}{bch:02x}"


def rel_lum(h: str) -> float:
    def f(c: int) -> float:
        x = c / 255
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4

    r, g, b = _hex_rgb(h)
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ink_on(fill: str) -> str:
    return INK if rel_lum(fill) > 0.42 else "#FFFFFF"


def seq_color(t: float) -> str:
    return lerp("#F4F1EA", "#2C5E94", t)


def div_color(v: float) -> str:
    v = max(-1.0, min(1.0, v))
    if v >= 0:
        return lerp("#F7F6F3", "#E07B2A", v)
    return lerp("#F7F6F3", "#2C5E94", -v)


class Fig:
    def __init__(self, width: float, title: str, desc: str):
        self.w = width
        self.title = title
        self.desc = desc
        self.parts: list[str] = []
        self.max_y = 0.0
        self.markers: set[str] = set(TONES.values())

    def mark(self, y: float) -> None:
        if y > self.max_y:
            self.max_y = y

    def add(self, s: str) -> None:
        self.parts.append(s)

    def under(self, s: str) -> None:
        """Paint before subsequently drawn shapes."""
        self.parts.insert(0, s)

    def rect(
        self,
        x,
        y,
        w,
        h,
        fill=PAPER,
        stroke=None,
        sw=1.25,
        rx=0,
        fo=1.0,
        so=1.0,
    ) -> None:
        st = f' stroke="{stroke}" stroke-width="{sw}" stroke-opacity="{so}"' if stroke else ' stroke="none"'
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" fill-opacity="{fo}"{st}/>'
        )
        self.mark(y + h)

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.35, dash=None, arrow=False) -> None:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        end = f' marker-end="url(#{self._mid(stroke)})"' if arrow else ""
        if arrow:
            self.markers.add(stroke)
        self.add(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{dash_attr}{end}/>'
        )
        self.mark(max(y1, y2))

    def poly(self, pts, stroke=INK, sw=1.5, fill="none", dash=None, arrow=False, fo=1.0) -> None:
        if arrow:
            self.markers.add(stroke)
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        end = f' marker-end="url(#{self._mid(stroke)})"' if arrow else ""
        self.add(
            f'<polyline points="{d}" fill="{fill}" fill-opacity="{fo}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{dash_attr}{end}/>'
        )
        self.mark(max(y for _, y in pts))

    def path(self, d, stroke=INK, sw=1.35, fill="none", dash=None, arrow=False, fo=1.0) -> None:
        if arrow:
            self.markers.add(stroke)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        end = f' marker-end="url(#{self._mid(stroke)})"' if arrow else ""
        self.add(
            f'<path d="{d}" fill="{fill}" fill-opacity="{fo}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linejoin="round" stroke-linecap="round"{dash_attr}{end}/>'
        )

    def circle(self, cx, cy, r, fill=PAPER, stroke=None, sw=1.25, fo=1.0) -> None:
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ' stroke="none"'
        self.add(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" fill-opacity="{fo}"{st}/>'
        )
        self.mark(cy + r)

    def text(
        self,
        x,
        y,
        s,
        size=13,
        color=INK,
        anchor="start",
        weight=400,
        style="normal",
        font="sans",
        baseline="auto",
        opacity=1.0,
    ) -> None:
        family = SERIF if font == "serif" else SANS
        base = ""
        if baseline == "middle":
            base = ' dominant-baseline="middle"'
        elif baseline == "hanging":
            base = ' dominant-baseline="hanging"'
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" fill-opacity="{opacity}" font-size="{size}" '
            f'font-weight="{weight}" font-style="{style}" font-family="{family}" '
            f'text-anchor="{anchor}"{base}>{html.escape(str(s))}</text>'
        )
        self.mark(y + size * 0.4)

    def rich(self, x, y, runs, anchor="start") -> None:
        norm = []
        for r in runs:
            if isinstance(r, str):
                norm.append(
                    {"t": r, "size": 13, "style": "normal", "dy": 0, "weight": 400, "color": INK, "font": "sans"}
                )
            else:
                norm.append(
                    {
                        "t": r[0],
                        "size": r[1] if len(r) > 1 else 13,
                        "style": r[2] if len(r) > 2 else "normal",
                        "dy": r[3] if len(r) > 3 else 0,
                        "weight": r[4] if len(r) > 4 else 400,
                        "color": r[5] if len(r) > 5 else INK,
                        "font": r[6] if len(r) > 6 else "serif",
                    }
                )
        widths = [text_width(r["t"], r["size"]) for r in norm]
        total = sum(widths)
        if anchor == "middle":
            x -= total / 2
        elif anchor == "end":
            x -= total
        tspans = []
        cur = 0.0
        for r in norm:
            dy = r["dy"] - cur
            cur = r["dy"]
            dyattr = f' dy="{dy:.2f}"' if abs(dy) > 0.01 else ""
            family = SERIF if r["font"] == "serif" else SANS
            tspans.append(
                f'<tspan font-size="{r["size"]}" font-style="{r["style"]}" font-weight="{r["weight"]}" '
                f'fill="{r["color"]}" font-family="{family}"{dyattr}>{html.escape(str(r["t"]))}</tspan>'
            )
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="start">{"".join(tspans)}</text>')
        self.mark(y + 10)

    def g_open(self, opacity=1.0, translate=None) -> None:
        tr = f' transform="translate({translate[0]:.1f} {translate[1]:.1f})"' if translate else ""
        self.add(f'<g opacity="{opacity}"{tr}>')

    def g_close(self) -> None:
        self.add("</g>")

    def _mid(self, color: str) -> str:
        return "mk" + color.replace("#", "")

    def arrow(self, x1, y1, x2, y2, color=INK, sw=1.55, dash=None) -> None:
        self.line(x1, y1, x2, y2, stroke=color, sw=sw, dash=dash, arrow=True)

    def elbow(self, pts, color=INK, sw=1.55, dash=None) -> None:
        self.poly(pts, stroke=color, sw=sw, dash=dash, arrow=True)
        self.mark(max(p[1] for p in pts))

    def card(self, x, y, w, h, title, sub=None, tone_name="blue", title_size=14, sub_size=11.5) -> None:
        col = tone(tone_name)
        self.rect(x, y, w, h, fill=col, fo=0.14, stroke=col, sw=1.35, rx=6)
        cx = x + w / 2
        max_w = w - 18
        if sub:
            ts = title_size
            while text_width(title, ts) > max_w and ts > 11:
                ts -= 0.5
            ss = sub_size
            while text_width(sub, ss) > max_w and ss > 10:
                ss -= 0.5
            self.text(cx, y + h / 2 - 9, title, size=ts, weight=600, anchor="middle", baseline="middle")
            self.text(cx, y + h / 2 + 11, sub, size=ss, anchor="middle", baseline="middle", color=MUTED)
        else:
            ts = title_size
            while text_width(title, ts) > max_w and ts > 11:
                ts -= 0.5
            self.text(cx, y + h / 2, title, size=ts, weight=600, anchor="middle", baseline="middle")

    def chip(self, x, y, label, tone_name="neutral", h=30, emphasize=False, min_w=0, size=13) -> float:
        col = tone(tone_name)
        tw = text_width(label, size)
        w = max(min_w, tw + 22)
        if tone_name == "neutral":
            fill, fo, stroke, tc = "#F4F2EE", 1.0, "#D9D5CE", INK
        else:
            fill, fo, stroke, tc = col, 0.18 if emphasize else 0.12, col, INK
        sw = 1.7 if emphasize else 1.2
        self.rect(x, y, w, h, fill=fill, fo=fo, stroke=stroke, sw=sw, rx=5)
        self.text(x + w / 2, y + h / 2, label, size=size, weight=600 if emphasize else 500, anchor="middle", baseline="middle", color=tc)
        return w

    def chips(self, x, y, labels, tone_name="neutral", tones=None, h=30, gap=8, emphasize=None, size=13) -> float:
        cx = x
        emphasize = emphasize or [False] * len(labels)
        for i, lab in enumerate(labels):
            tn = tones[i] if tones else tone_name
            w = self.chip(cx, y, lab, tn, h=h, emphasize=emphasize[i], size=size)
            cx += w + gap
        return cx - gap

    def plus(self, x, y, r=9, color=INK) -> None:
        self.circle(x, y, r, fill=PAPER, stroke=color, sw=1.35)
        self.line(x - 4.5, y, x + 4.5, y, stroke=color, sw=1.35)
        self.line(x, y - 4.5, x, y + 4.5, stroke=color, sw=1.35)

    def region(self, x, y, w, h, fill=PANEL) -> None:
        self.rect(x, y, w, h, fill=fill, stroke=LINE, sw=1, rx=10)

    def lead(self, x, y, letter, title) -> float:
        self.text(x, y, f"({letter})", size=13, font="serif", style="italic", color=MUTED, baseline="middle")
        self.text(x + 28, y, title, size=15, weight=650, baseline="middle")
        return y + 16

    def footnote(self, y, text, x=28, width=904, size=11.5, color=MUTED) -> float:
        lines = wrap_text(text, width, size)
        for i, line in enumerate(lines):
            self.text(x, y + i * (size + 6), line, size=size, color=color)
        end = y + max(0, len(lines) - 1) * (size + 6) + 4
        self.mark(end)
        return end

    def vbracket(self, x, y, h, label, side="right") -> None:
        if side == "right":
            self.path(f"M {x:.1f} {y:.1f} H {x+8:.1f} V {y+h:.1f} H {x:.1f}", stroke=INK, sw=1.4, fill="none")
            self.text(x + 14, y + h / 2, label, baseline="middle", size=13, weight=650)
        else:
            self.path(f"M {x:.1f} {y:.1f} H {x-8:.1f} V {y+h:.1f} H {x:.1f}", stroke=INK, sw=1.4, fill="none")
            self.text(x - 14, y + h / 2, label, baseline="middle", size=13, weight=650, anchor="end")

    def callout(self, x, y, w, lines, tone_name="gold") -> float:
        col = tone(tone_name)
        h = 14 + len(lines) * 18
        self.rect(x, y, w, h, fill=col, fo=0.12, stroke=col, sw=1.15, rx=6)
        for i, line in enumerate(lines):
            self.text(x + 12, y + 16 + i * 18, line, size=12, baseline="middle", color=INK)
        return h

    def heatmap(
        self,
        x,
        y,
        matrix,
        row_labels,
        col_labels,
        cell=48,
        vmin=0.0,
        vmax=1.0,
        highlight_row=None,
        fmt="{:.2f}",
        cbar=True,
    ) -> tuple[float, float]:
        n = len(matrix)
        m = len(matrix[0])
        lab_w = max(text_width(s, 13) for s in row_labels) + 16
        top = 26
        for c, lab in enumerate(col_labels):
            fs = 12.5
            while text_width(lab, fs) > cell - 8 and fs > 9:
                fs -= 0.5
            self.text(x + lab_w + c * cell + cell / 2, y + 8, lab, anchor="middle", baseline="middle", size=fs, color=MUTED)
        for r, lab in enumerate(row_labels):
            weight = 700 if r == highlight_row else 500
            color = ORANGE if r == highlight_row else INK
            self.text(x + lab_w - 10, y + top + r * cell + cell / 2, lab, anchor="end", baseline="middle", size=13, weight=weight, color=color)
            for c in range(m):
                v = matrix[r][c]
                t = 0 if vmax == vmin else (v - vmin) / (vmax - vmin)
                fill = seq_color(t)
                self.rect(x + lab_w + c * cell + 2, y + top + r * cell + 2, cell - 4, cell - 4, fill=fill, rx=3)
                self.text(
                    x + lab_w + c * cell + cell / 2,
                    y + top + r * cell + cell / 2,
                    fmt.format(v),
                    anchor="middle",
                    baseline="middle",
                    size=12,
                    weight=600,
                    color=ink_on(fill),
                )
        if highlight_row is not None:
            self.rect(
                x + lab_w + 0.5,
                y + top + highlight_row * cell + 0.5,
                m * cell - 1,
                cell - 1,
                fill="none",
                stroke=ORANGE,
                sw=2,
                rx=4,
            )
        grid_w = lab_w + m * cell
        grid_h = top + n * cell
        if cbar:
            bx = x + grid_w + 18
            by = y + top
            bh = n * cell - 4
            bw = 12
            steps = 40
            for i in range(steps):
                t = 1 - (i + 0.5) / steps
                self.rect(bx, by + bh * i / steps, bw, bh / steps + 0.4, fill=seq_color(t))
            self.rect(bx, by, bw, bh, fill="none", stroke=LINE, sw=1, rx=2)
            self.text(bx + bw + 6, by + 4, f"{vmax:g}", size=11, baseline="middle", color=MUTED)
            self.text(bx + bw + 6, by + bh, f"{vmin:g}", size=11, baseline="middle", color=MUTED)
            grid_w = bx + bw + 36 - x
        return {
            "w": grid_w,
            "h": grid_h,
            "lab_w": lab_w,
            "top": top,
            "cell": cell,
            "rows": n,
            "cols": m,
        }

    def matrix_symbols(self, x, y, labels, cell=36, palette=None) -> tuple[float, float]:
        n = len(labels)
        m = len(labels[0])
        palette = palette or {}
        for r in range(n):
            for c in range(m):
                lab = labels[r][c]
                col = palette.get(lab, PANEL)
                self.rect(x + c * cell + 1.5, y + r * cell + 1.5, cell - 3, cell - 3, fill=col, fo=0.22 if lab in palette else 1, stroke=LINE, sw=1, rx=3)
                self.text(x + c * cell + cell / 2, y + r * cell + cell / 2, lab, size=11, anchor="middle", baseline="middle", weight=600)
        return m * cell, n * cell

    def glyph(self, x, y, bitmap, cell=8, noise=0.0, seed=0, gap=1.0) -> tuple[float, float]:
        import random

        rng = random.Random(seed)
        h = len(bitmap)
        w = len(bitmap[0])
        for r in range(h):
            for c in range(w):
                signal = 0.16 if bitmap[r][c] else 0.94
                rnd = rng.random()
                val = (1 - noise) * signal + noise * rnd
                val = max(0.0, min(1.0, val))
                gch = round(val * 255)
                fill = f"#{gch:02x}{gch:02x}{gch:02x}"
                self.rect(x + c * cell, y + r * cell, cell - gap, cell - gap, fill=fill, rx=0.6)
        return w * cell, h * cell

    def colorbar_div(self, x, y, h, vmin=-1, vmax=1) -> None:
        steps = 48
        bw = 12
        for i in range(steps):
            v = vmax + (vmin - vmax) * (i + 0.5) / steps
            self.rect(x, y + h * i / steps, bw, h / steps + 0.4, fill=div_color(v))
        self.rect(x, y, bw, h, fill="none", stroke=LINE, sw=1)
        self.text(x + 16, y + 4, f"{vmax:g}", size=11, baseline="middle", color=MUTED)
        self.text(x + 16, y + h / 2, "0", size=11, baseline="middle", color=MUTED)
        self.text(x + 16, y + h, f"{vmin:g}", size=11, baseline="middle", color=MUTED)

    def plot_curve(self, x, y, w, h, pts, color, xlabel, ylabel) -> None:
        """pts are in unit square, y up. (x, y) is the top-left of the plot box."""
        self.rect(x, y, w, h, fill="#FBFBFA", stroke=LINE, sw=1, rx=6)
        left, right, top, bot = x + 36, x + w - 14, y + 16, y + h - 28
        self.line(left, top, left, bot, stroke="#C9C4BC", sw=1.1)
        self.line(left, bot, right, bot, stroke="#C9C4BC", sw=1.1)
        mapped = []
        for px, py in pts:
            mapped.append((left + px * (right - left), bot - py * (bot - top)))
        self.poly(mapped, stroke=color, sw=2.25)
        self.text((left + right) / 2, bot + 16, xlabel, size=11.5, anchor="middle", color=MUTED)
        self.text(x + 8, top - 2, ylabel, size=11.5, color=MUTED)
        self._plot_box = (left, right, top, bot)

    def plot_dot(self, px, py, label, color, dx=8, dy=-10) -> None:
        left, right, top, bot = self._plot_box
        cx = left + px * (right - left)
        cy = bot - py * (bot - top)
        self.circle(cx, cy, 4.5, fill=color, stroke=PAPER, sw=1.4)
        self.text(cx + dx, cy + dy, label, size=11.5, weight=650, color=color, anchor="start")

    def save(self, name: str) -> Path:
        h = math.ceil(self.max_y + 26)
        marker_defs = []
        for col in sorted(self.markers):
            mid = self._mid(col)
            marker_defs.append(
                f'<marker id="{mid}" viewBox="0 0 12 10" refX="10" refY="5" markerWidth="8" '
                f'markerHeight="7" orient="auto" markerUnits="userSpaceOnUse">'
                f'<path d="M0,0 L12,5 L0,10 Z" fill="{col}"/></marker>'
            )
        svg = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w:.0f}" height="{h}" '
            f'viewBox="0 0 {self.w:.0f} {h}" role="img">\n'
            f"<title>{html.escape(self.title)}</title>\n"
            f"<desc>{html.escape(self.desc)}</desc>\n"
            f'<rect width="100%" height="100%" fill="{PAPER}"/>\n'
            f"<defs>{''.join(marker_defs)}</defs>\n"
            + "\n".join(self.parts)
            + "\n</svg>\n"
        )
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / name
        path.write_text(svg, encoding="utf-8")
        return path


DIGIT_5 = [
    "11111110",
    "10000000",
    "10000000",
    "11111100",
    "00000110",
    "00000010",
    "10000110",
    "01111000",
]
DIGIT_3 = [
    "01111100",
    "00000010",
    "00000100",
    "00111100",
    "00000010",
    "00000010",
    "10000100",
    "01111000",
]
DIGIT_8 = [
    "01111100",
    "10000010",
    "10000010",
    "01111100",
    "10000010",
    "10000010",
    "10000010",
    "01111100",
]


def bits(rows: list[str]) -> list[list[int]]:
    return [[1 if ch == "1" else 0 for ch in row] for row in rows]


def softmax(scores: list[float]) -> list[float]:
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    z = sum(exps)
    return [e / z for e in exps]
