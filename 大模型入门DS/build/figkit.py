"""figkit — a tiny SVG drawing kit for Distill-style lecture figures.

Design language (keep every figure inside these rules):
  * white background, no outer frame, 960 px design width
  * hairline strokes (1 px) in slate; 4-6 px corner radii
  * flat, low-saturation fills; accent colours carry meaning
  * one type scale: 11 / 12 / 13 / 16 / 20 px
  * arrows are 1.4 px with small solid heads; dashed lines mean "grouping"
  * captions live in the Markdown, never inside the figure

Colour semantics (reuse across figures):
  blue   Query / encoder / source of information
  orange Key / scoring
  teal   Value / carried content
  violet model, network block, LLM
  red    loss, noise, error, danger
  green  reward, verify-ok
  slate  data, tokens, neutral structure
"""

from __future__ import annotations

import math
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------
# tokens
# --------------------------------------------------------------------------

FONT_SANS = "'Segoe UI','Microsoft YaHei','PingFang SC','Helvetica Neue',Arial,sans-serif"
FONT_SERIF = "'Cambria Math','Times New Roman',Georgia,serif"
FONT_MONO = "'Cascadia Code','Consolas','SFMono-Regular',monospace"

P = {
    "ink": "#1f2a33",
    "ink2": "#44525e",
    "muted": "#7c8a97",
    "faint": "#b6c1ca",
    "rule": "#dde5ec",
    "panel": "#f6f9fb",
    "panel2": "#eef4f8",
    "white": "#ffffff",
    "blue": "#3a6ea5",
    "blue2": "#5b8dc2",
    "blueL": "#edf3f9",
    "blueM": "#c9dcee",
    "orange": "#c2703a",
    "orange2": "#dd9a63",
    "orangeL": "#fcf1e7",
    "orangeM": "#f0d2b7",
    "teal": "#2f8b7f",
    "teal2": "#58a89d",
    "tealL": "#e9f5f2",
    "tealM": "#bfe0d9",
    "violet": "#6f63a5",
    "violet2": "#9187bd",
    "violetL": "#f0eef8",
    "violetM": "#d6d0ea",
    "red": "#b04a4e",
    "red2": "#cf7b7e",
    "redL": "#faeeee",
    "redM": "#eccbcd",
    "green": "#4f8552",
    "greenL": "#edf5ec",
    "greenM": "#c6dcc4",
    "gold": "#b98b2e",
    "goldL": "#fbf3df",
    "goldM": "#ecd9a8",
}

# sequential ramps, t in [0,1]
def _lerp(a, b, t):
    a = a.lstrip("#")
    b = b.lstrip("#")
    ca = [int(a[i : i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i : i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(ca[i] + (cb[i] - ca[i]) * t):02x}" for i in range(3))


def ramp(c0, c1):
    return lambda t: _lerp(c0, c1, max(0.0, min(1.0, t)))


BLUES = ramp("#f4f8fc", "#2b5d8c")
ORANGES = ramp("#fdf5ee", "#a85a28")
TEALS = ramp("#f0f8f6", "#226b61")
VIOLETS = ramp("#f6f4fb", "#554a8a")
REDS = ramp("#fdf2f2", "#963c40")
GREYS = ramp("#fbfcfd", "#55636f")
GOLDS = ramp("#fdf8ea", "#a3781f")


def _heur(s, size, family="sans", weight=None):
    k = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E80:            # CJK & fullwidth
            k += 1.0
        elif ch in " ":
            k += 0.28
        elif ch in "ilI.,:;'|!`":
            k += 0.30
        elif ch in "mwMW@%":
            k += 0.85
        elif ch in "fjrt()[]{}/\\-":
            k += 0.40
        elif ch.isupper() or ch.isdigit():
            k += 0.60
        else:
            k += 0.52
    w = k * size
    if family == "mono":
        w = len(s) * size * 0.60
    if weight in ("600", "700"):
        w *= 1.03
    return w


def _load_metrics():
    import json
    from pathlib import Path

    p = Path(__file__).resolve().parent / "metrics.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


_METRICS = _load_metrics()


def tw(s, size, family="sans", weight=None, italic=False):
    """Advance width of a string in px (measured metrics when available)."""
    if family == "mono":
        return len(s) * size * 0.60
    if _METRICS:
        if family == "serif":
            key = "serifit" if italic else "serif"
        else:
            key = "sans600" if weight in ("600", "700") else "sans"
        tbl = _METRICS.get(key)
        if tbl:
            total, missing = 0.0, []
            for ch in s:
                v = tbl.get(ch)
                if v is None:
                    missing.append(ch)
                else:
                    total += v
            if missing:
                total += _heur("".join(missing), 100, family, weight)
            return total * size / 100.0
    return _heur(s, size, family, weight)


class Canvas:
    def __init__(self, w, h, bg=P["white"]):
        self.w, self.h = w, h
        self.bg = bg
        self.parts: list[str] = []
        self.defs: list[str] = []

    # -- raw ------------------------------------------------------------
    def add(self, s):
        self.parts.append(s)
        return self

    # -- primitives -----------------------------------------------------
    def rect(self, x, y, w, h, fill="none", stroke=None, sw=1, rx=0, dash=None,
             opacity=None, id=None):
        a = [f'x="{x:.2f}"', f'y="{y:.2f}"', f'width="{max(w,0):.2f}"', f'height="{max(h,0):.2f}"']
        a.append(f'rx="{rx}"')
        a.append(f'fill="{fill}"')
        if stroke:
            a += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if dash:
            a.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            a.append(f'opacity="{opacity}"')
        if id:
            a.append(f'id="{id}"')
        self.add(f"<rect {' '.join(a)}/>")
        return self

    def line(self, x1, y1, x2, y2, stroke=P["ink2"], sw=1, dash=None, opacity=None,
             cap="butt"):
        a = [f'x1="{x1:.2f}"', f'y1="{y1:.2f}"', f'x2="{x2:.2f}"', f'y2="{y2:.2f}"',
             f'stroke="{stroke}"', f'stroke-width="{sw}"', f'stroke-linecap="{cap}"']
        if dash:
            a.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            a.append(f'opacity="{opacity}"')
        self.add(f"<line {' '.join(a)}/>")
        return self

    def path(self, d, fill="none", stroke=None, sw=1, dash=None, opacity=None,
             cap="butt", join="miter"):
        a = [f'd="{d}"', f'fill="{fill}"']
        if stroke:
            a += [f'stroke="{stroke}"', f'stroke-width="{sw}"',
                  f'stroke-linecap="{cap}"', f'stroke-linejoin="{join}"']
        if dash:
            a.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            a.append(f'opacity="{opacity}"')
        self.add(f"<path {' '.join(a)}/>")
        return self

    def circle(self, cx, cy, r, fill=P["ink"], stroke=None, sw=1, opacity=None):
        a = [f'cx="{cx:.2f}"', f'cy="{cy:.2f}"', f'r="{r:.2f}"', f'fill="{fill}"']
        if stroke:
            a += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if opacity is not None:
            a.append(f'opacity="{opacity}"')
        self.add(f"<circle {' '.join(a)}/>")
        return self

    def poly(self, pts, fill=P["ink"], stroke=None, sw=1, opacity=None):
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        a = [f'points="{d}"', f'fill="{fill}"']
        if stroke:
            a += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if opacity is not None:
            a.append(f'opacity="{opacity}"')
        self.add(f"<polygon {' '.join(a)}/>")
        return self

    def polyline(self, pts, stroke=P["ink2"], sw=1.4, dash=None, opacity=None):
        d = " ".join(("M" if i == 0 else "L") + f" {x:.2f} {y:.2f}" for i, (x, y) in enumerate(pts))
        return self.path(d, stroke=stroke, sw=sw, dash=dash, opacity=opacity,
                         cap="round", join="round")

    def text(self, x, y, s, size=13, fill=P["ink"], anchor="start", weight=None,
             family="sans", italic=False, ls=None, opacity=None, rotate=None,
             baseline=None):
        if s is None or s == "":
            return self
        fam = {"sans": FONT_SANS, "serif": FONT_SERIF, "mono": FONT_MONO}[family]
        a = [f'x="{x:.2f}"', f'y="{y:.2f}"', f'font-family="{fam}"',
             f'font-size="{size}"', f'text-anchor="{anchor}"']
        if fill != "none":
            a.append(f'fill="{fill}"')
        if weight:
            a.append(f'font-weight="{weight}"')
        if italic:
            a.append("font-style=\"italic\"")
        if ls is not None:
            a.append(f'letter-spacing="{ls}"')
        if opacity is not None:
            a.append(f'opacity="{opacity}"')
        if baseline:
            a.append(f'dominant-baseline="{baseline}"')
        if rotate is not None:
            a.append(f'transform="rotate({rotate[0]:.1f} {rotate[1]:.2f} {rotate[2]:.2f})"')
        self.add(f"<text {' '.join(a)}>{escape(s)}</text>")
        return self

    # -- composite ------------------------------------------------------
    def box(self, x, y, w, h, label=None, sub=None, fill=P["panel"], stroke=P["rule"],
            rx=6, size=13, weight="600", color=None, sw=1, dash=None, sub_size=11,
            sub_color=None, lh=None, italic=False):
        self.rect(x, y, w, h, fill=fill, stroke=stroke, rx=rx, sw=sw, dash=dash)
        if label is not None:
            cy = y + h / 2 + (0 if sub is None else -8)
            self.text(x + w / 2, cy, label, size=size, fill=color or P["ink"],
                      anchor="middle", weight=weight, italic=italic)
        if sub is not None:
            self.text(x + w / 2, y + h / 2 + 12, sub, size=sub_size,
                      fill=sub_color or P["muted"], anchor="middle")
        return self

    def mat(self, x, y, cols, rows, cell=14, fill=P["blueL"], stroke=P["blueM"],
            gap=0.8, rx=1, opacity=None):
        """Grid of matrix cells; returns dict with geometry helpers."""
        for r in range(rows):
            for c_ in range(cols):
                self.rect(x + c_ * cell, y + r * cell, cell - gap, cell - gap,
                          fill=fill, stroke=stroke, sw=0.5, rx=rx, opacity=opacity)
        return {"x": x, "y": y, "w": cols * cell, "h": rows * cell, "cell": cell,
                "cols": cols, "rows": rows}

    def bracket(self, x, y, h, side="left", color=P["ink2"], sw=1.2, arm=5):
        if side == "left":
            d = f"M {x+arm} {y} L {x} {y} L {x} {y+h} L {x+arm} {y+h}"
        else:
            d = f"M {x-arm} {y} L {x} {y} L {x} {y+h} L {x-arm} {y+h}"
        self.path(d, stroke=color, sw=sw, cap="round")
        return self

    def arrow(self, x1, y1, x2, y2, color=P["muted"], sw=1.4, head=6, dash=None,
              curve=0.0, start_head=False, shrink=0.85, opacity=None):
        """Straight or quadratic-curved arrow, head placed at (x2, y2)."""
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1e-6
        if curve:
            nx, ny = -dy / L, dx / L
            cx_, cy_ = (x1 + x2) / 2 + nx * curve, (y1 + y2) / 2 + ny * curve
            ang = math.atan2(y2 - cy_, x2 - cx_)
            ex, ey = x2 - head * shrink * math.cos(ang), y2 - head * shrink * math.sin(ang)
            d = f"M {x1:.2f} {y1:.2f} Q {cx_:.2f} {cy_:.2f} {ex:.2f} {ey:.2f}"
            self.path(d, stroke=color, sw=sw, dash=dash, opacity=opacity, cap="round")
        else:
            ang = math.atan2(dy, dx)
            ex, ey = x2 - head * shrink * math.cos(ang), y2 - head * shrink * math.sin(ang)
            self.line(x1, y1, ex, ey, stroke=color, sw=sw, dash=dash, opacity=opacity,
                      cap="round")
        hb = head * 0.62
        p1 = (x2, y2)
        p2 = (x2 - head * math.cos(ang) + hb * math.sin(ang),
              y2 - head * math.sin(ang) - hb * math.cos(ang))
        p3 = (x2 - head * math.cos(ang) - hb * math.sin(ang),
              y2 - head * math.sin(ang) + hb * math.cos(ang))
        self.poly([p1, p2, p3], fill=color, opacity=opacity)
        if start_head:
            a2 = ang + math.pi
            q1 = (x1, y1)
            q2 = (x1 - head * math.cos(a2) + hb * math.sin(a2),
                  y1 + head * math.sin(a2) + hb * math.cos(a2))
            q3 = (x1 - head * math.cos(a2) - hb * math.sin(a2),
                  y1 + head * math.sin(a2) - hb * math.cos(a2))
            self.poly([q1, q2, q3], fill=color, opacity=opacity)
        return self

    def arrow_path(self, d, color=P["muted"], sw=1.4, head=6, fill="none"):
        """Arrow head only, for hand-drawn curved connectors."""
        self.path(d, stroke=color, sw=sw, fill=fill, cap="round")

    def dot(self, x, y, r=3, fill=P["ink"]):
        return self.circle(x, y, r, fill=fill)

    def label(self, x, y, s, size=11, color=P["muted"], anchor="start", ls="0.06em",
              weight=None):
        return self.text(x, y, s, size=size, fill=color, anchor=anchor, ls=ls,
                         weight=weight)

    def heat(self, x, y, w, h, vals, cmap=BLUES, vmin=None, vmax=None, gap=0.8,
             cells_text=None, text_size=8, text_color=None, rx=1.5, stroke=None):
        nr, nc = len(vals), len(vals[0])
        vmin = min(min(r) for r in vals) if vmin is None else vmin
        vmax = max(max(r) for r in vals) if vmax is None else vmax
        cw, ch = w / nc, h / nr
        for i in range(nr):
            for j in range(nc):
                t = 0 if vmax == vmin else (vals[i][j] - vmin) / (vmax - vmin)
                self.rect(x + j * cw + gap / 2, y + i * ch + gap / 2, cw - gap, ch - gap,
                          fill=cmap(t), stroke=stroke, sw=0.5, rx=rx)
                if cells_text:
                    self.text(x + j * cw + cw / 2, y + i * ch + ch / 2 + text_size * 0.36,
                              cells_text[i][j], size=text_size,
                              fill=text_color or P["ink2"], anchor="middle")
        return {"x": x, "y": y, "w": w, "h": h, "cw": cw, "ch": ch}

    # -- math text ------------------------------------------------------
    def mtext(self, x, y, s, size=14, fill=P["ink"], anchor="start", color_var=None):
        """Very small math-mode renderer.

        Syntax:  _x  -> subscript single char, _{...} -> group,
                 ^x  -> superscript, ^{...} -> group,
                 \\i{...} -> italic, plain text is upright sans.
        """
        segs = _parse_math(s)
        small = size * 0.66

        def adv(t, k):
            if k in ("sub", "sup"):
                return tw(t, small, "serif", italic=True) + 0.4
            if k == "it":
                return tw(t, size, "serif", italic=True)
            return tw(t, size, "serif")

        total = sum(adv(t, k) for t, k in segs)
        cx = x - total / 2 if anchor == "middle" else (x - total if anchor == "end" else x)
        for t, k in segs:
            if k in ("sub", "sup"):
                dy = size * 0.22 if k == "sub" else -size * 0.38
                self.text(cx, y + dy, t, size=small, fill=fill, family="serif",
                          italic=True)
            elif k == "it":
                self.text(cx, y, t, size=size, fill=fill, family="serif", italic=True)
            else:
                self.text(cx, y, t, size=size, fill=fill, family="serif")
            cx += adv(t, k)
        return self

    # -- output ---------------------------------------------------------
    def svg(self):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">')
        bg = f'<rect width="{self.w}" height="{self.h}" fill="{self.bg}"/>'
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return "\n".join([head, bg, defs, *self.parts, "</svg>"])


def _split_letters(t):
    """Math convention: variables italic, digits/operators upright."""
    out, cur, cur_it = [], "", None
    for ch in t:
        is_it = ch.isalpha() and ch not in "ΣΠ"
        if cur_it is None or is_it == cur_it:
            cur += ch
            cur_it = is_it
        else:
            out.append((cur, "it" if cur_it else "txt"))
            cur, cur_it = ch, is_it
    if cur:
        out.append((cur, "it" if cur_it else "txt"))
    return out


def _parse_math(s):
    """Split a tiny math string into [(text, kind)] runs."""
    out, buf, i = [], "", 0

    def flush():
        nonlocal buf
        if buf:
            out.extend(_split_letters(buf))
            buf = ""

    while i < len(s):
        ch = s[i]
        if ch in "_^" and i + 1 < len(s):
            flush()
            i += 1
            kind = "sub" if ch == "_" else "sup"
            if s[i] == "{":
                j = s.index("}", i)
                out.append((s[i + 1 : j], kind))
                i = j + 1
            else:
                out.append((s[i], kind))
                i += 1
        elif s.startswith("\\i{", i):
            flush()
            j = s.index("}", i + 3)
            out.append((s[i + 3 : j], "it"))
            i = j + 1
        else:
            buf += ch
            i += 1
    flush()
    return out


# --------------------------------------------------------------------------
# axes
# --------------------------------------------------------------------------

class Axes:
    """Minimal plotting frame: pixel mapping, ticks, grid, lines."""

    def __init__(self, c: Canvas, x, y, w, h, xlim, ylim, xlog=False, ylog=False,
                 xlabel=None, ylabel=None, xticks=None, yticks=None, grid=True,
                 ytick_labels=None, xtick_labels=None, tick_size=10.5):
        self.c, self.x0, self.y0, self.w, self.h = c, x, y, w, h
        self.xlim, self.ylim = xlim, ylim
        self.xlog, self.ylog = xlog, ylog
        self.grid = grid
        self.tick_size = tick_size
        if xlog:
            self.lx0, self.lx1 = math.log10(xlim[0]), math.log10(xlim[1])
        else:
            self.lx0, self.lx1 = xlim
        if ylog:
            self.ly0, self.ly1 = math.log10(ylim[0]), math.log10(ylim[1])
        else:
            self.ly0, self.ly1 = ylim

        # frame: baseline + left axis only (Distill-ish)
        c.line(x, y + h, x + w, y + h, stroke=P["ink2"], sw=1)
        c.line(x, y, x, y + h, stroke=P["ink2"], sw=1)

        xt = xticks if xticks is not None else self._auto(xlim, xlog)
        yt = yticks if yticks is not None else self._auto(ylim, ylog)
        for i, v in enumerate(xt):
            px = self.X(v)
            c.line(px, y + h, px, y + h + 3, stroke=P["ink2"], sw=1)
            lab = xtick_labels[i] if xtick_labels else _fmt_tick(v, xlog)
            c.text(px, y + h + 15, lab, size=tick_size, fill=P["muted"], anchor="middle")
            if grid:
                c.line(px, y + h, px, y, stroke=P["rule"], sw=0.75, dash="2 3")
        for i, v in enumerate(yt):
            py = self.Y(v)
            c.line(x - 3, py, x, py, stroke=P["ink2"], sw=1)
            lab = ytick_labels[i] if ytick_labels else _fmt_tick(v, ylog)
            c.text(x - 7, py + 3.5, lab, size=tick_size, fill=P["muted"], anchor="end")
            if grid:
                c.line(x, py, x + w, py, stroke=P["rule"], sw=0.75, dash="2 3")
        if xlabel:
            c.text(x + w / 2, y + h + 32, xlabel, size=11.5, fill=P["ink2"], anchor="middle")
        if ylabel:
            c.text(x - 44, y + h / 2, ylabel, size=11.5, fill=P["ink2"], anchor="middle",
                   rotate=(-90, x - 44, y + h / 2))

    @staticmethod
    def _auto(lim, lg):
        lo, hi = lim
        if lg:
            lo, hi = math.log10(lo), math.log10(hi)
            step = max(1, round((hi - lo) / 4))
            vals = [lo + step * k for k in range(int((hi - lo) // step) + 1)]
            return [10 ** v for v in vals]
        raw = (hi - lo) / 4
        mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
        step = mag * (1 if raw / mag < 1.5 else 2 if raw / mag < 3.5 else 5 if raw / mag < 7.5 else 10)
        v = math.ceil(lo / step) * step
        out = []
        while v <= hi + 1e-9:
            out.append(round(v, 10))
            v += step
        return out

    def X(self, v):
        t = math.log10(v) if self.xlog else v
        return self.x0 + (t - self.lx0) / (self.lx1 - self.lx0) * self.w

    def Y(self, v):
        t = math.log10(v) if self.ylog else v
        return self.y0 + self.h - (t - self.ly0) / (self.ly1 - self.ly0) * self.h

    def line(self, pts, color=P["ink"], sw=1.8, dash=None, opacity=None):
        return self.c.polyline([(self.X(x), self.Y(y)) for x, y in pts], stroke=color,
                               sw=sw, dash=dash, opacity=opacity)

    def curve(self, f, a, b, n=160, **kw):
        pts = []
        for i in range(n + 1):
            t = a + (b - a) * i / n
            xv = 10 ** t if self.xlog else t
            yv = f(xv)
            pts.append((xv, yv))
        return self.line(pts, **kw)

    def area(self, pts, base, fill=P["blueL"], opacity=None):
        pp = [(self.X(x), self.Y(y)) for x, y in pts]
        pp += [(self.X(pts[-1][0]), self.Y(base)), (self.X(pts[0][0]), self.Y(base))]
        d = " ".join(("M" if i == 0 else "L") + f" {x:.2f} {y:.2f}" for i, (x, y) in enumerate(pp))
        self.c.path(d + " Z", fill=fill, opacity=opacity)
        return self

    def note(self, x, y, s, dx=0, dy=0, anchor="start", size=11, color=P["muted"]):
        self.c.text(x + dx, y + dy, s, size=size, fill=color, anchor=anchor)

    def vline(self, v, color=P["faint"], dash="3 3", sw=1):
        self.c.line(self.X(v), self.y0, self.X(v), self.y0 + self.h, stroke=color,
                    dash=dash, sw=sw)


def _fmt_tick(v, lg):
    if lg:
        e = math.log10(v)
        if abs(e - round(e)) < 1e-9:
            e = int(round(e))
            return {0: "1", 1: "10", 2: "100", 3: "1k", 4: "10k", 5: "100k",
                    6: "1M", 7: "10M", 8: "100M", 9: "1B"}.get(e, f"10^{e}")
    if abs(v - round(v)) < 1e-9:
        v = int(round(v))
    elif abs(v) >= 100:
        v = f"{v:.0f}"
    else:
        v = f"{v:g}"
    return str(v)


# --------------------------------------------------------------------------
# small shared glyphs
# --------------------------------------------------------------------------

def token_row(c, x, y, tokens, cell=30, gap=3, fill=P["panel2"], stroke=P["rule"],
              size=12, color=P["ink2"], colors=None, sub=None):
    """Row of token chips; returns list of (x, w) spans."""
    spans, cx = [], x
    for i, t in enumerate(tokens):
        w = max(cell, tw(t, size) + (14 if len(t) > 1 else 10))
        f = colors[i] if colors else fill
        s = stroke
        c.rect(cx, y, w, cell, fill=f, stroke=s, rx=4)
        c.text(cx + w / 2, y + cell / 2 + 4.2, t, size=size, fill=color, anchor="middle")
        if sub and sub[i]:
            c.text(cx + w / 2, y + cell + 12, sub[i], size=10, fill=P["muted"], anchor="middle")
        spans.append((cx, w))
        cx += w + gap
    return spans


def legend(c, x, y, items, size=11, swatch=9, gapx=18, gapy=16, color=None):
    """items: [(label, color)]"""
    cx, cy = x, y
    for i, (lab, col) in enumerate(items):
        if color is None and isinstance(col, int):
            pass
        c.rect(cx, cy - swatch / 2, swatch, swatch, fill=col, stroke="none", rx=2)
        c.text(cx + swatch + 5, cy + 3.5, lab, size=size, fill=P["ink2"])
        cx += swatch + 5 + tw(lab, size) + gapx
        if cx > x + 900:
            cx, cy = x, cy + gapy
    return cy + gapy


def panel_tag(c, x, y, s, color=P["muted"]):
    c.text(x, y, s, size=11.5, fill=color, weight="600", ls="0.08em")


def brace_v(c, x, y0, y1, color=P["faint"], w=6, sw=1.1):
    mid = (y0 + y1) / 2
    d = (f"M {x:.2f} {y0:.2f} q {w} 0 {w} {w} L {x+w:.2f} {mid-w:.2f} "
         f"q 0 {w} {w} {w} q {-w} 0 {-w} {w} L {x+w:.2f} {y1-w:.2f} q 0 {w} {-w} {w}")
    c.path(d, stroke=color, sw=sw, cap="round")


def brace_h(c, x0, x1, y, color=P["faint"], w=6, sw=1.1, up=True):
    mid = (x0 + x1) / 2
    s = -1 if up else 1
    d = (f"M {x0:.2f} {y:.2f} q 0 {s*w} {w} {s*w} L {mid-w:.2f} {y+s*w:.2f} "
         f"q {w} 0 {w} {-s*w} q 0 {s*w} {w} {s*w} L {x1-w:.2f} {y+s*w:.2f} "
         f"q {w} 0 {w} {-s*w}")
    c.path(d, stroke=color, sw=sw, cap="round")


def sparkline(c, x, y, w, h, vals, color=P["blue"], sw=1.2, fill=None):
    lo, hi = min(vals), max(vals)
    pts = [(x + i / (len(vals) - 1) * w,
            y + h - (v - lo) / (hi - lo or 1) * h) for i, v in enumerate(vals)]
    if fill:
        d = " ".join(("M" if i == 0 else "L") + f" {px:.2f} {py:.2f}" for i, (px, py) in enumerate(pts))
        c.path(d + f" L {x+w:.2f} {y+h:.2f} L {x:.2f} {y+h:.2f} Z", fill=fill)
    c.polyline(pts, stroke=color, sw=sw)
    return pts
