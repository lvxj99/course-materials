"""Shared figure-level helpers built on figkit."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from figkit import (  # noqa: E402,F401
    Axes, BLUES, GOLDS, GREYS, ORANGES, P, REDS, TEALS, VIOLETS,
    Canvas, brace_h, brace_v, legend, panel_tag, sparkline, token_row, tw,
)


def lines_text(c, cx, cy, lines, size=13, lh=1.32, fill=P["ink"], weight=None,
               anchor="middle", family="sans", sub_size=11, sub_fill=None):
    """Vertically-centred block of text lines."""
    n = len(lines)
    total = (n - 1) * size * lh
    y0 = cy - total / 2 + size * 0.34
    for i, ln in enumerate(lines):
        c.text(cx, y0 + i * size * lh, ln, size=size, fill=fill, anchor=anchor,
               weight=weight, family=family)
    return c


def two_line(c, cx, cy, l1, l2, size=12.8, size2=10.8, fill=P["ink"],
             fill2=None, dy=8):
    c.text(cx, cy - dy, l1, size=size, fill=fill, anchor="middle", weight="600")
    c.text(cx, cy + dy + 6, l2, size=size2, fill=fill2 or P["muted"], anchor="middle")
    return c


def block(c, x, y, w, h, l1, l2=None, fill=P["panel"], stroke=P["rule"], rx=5,
          size=12.8, size2=10.8, color=None, color2=None, sw=1, dash=None):
    c.rect(x, y, w, h, fill=fill, stroke=stroke, rx=rx, sw=sw, dash=dash)
    if l2 is None:
        c.text(x + w / 2, y + h / 2 + size * 0.34, l1, size=size,
               fill=color or P["ink"], anchor="middle", weight="600")
    else:
        c.text(x + w / 2, y + h / 2 - 2, l1, size=size, fill=color or P["ink"],
               anchor="middle", weight="600")
        c.text(x + w / 2, y + h / 2 + 12, l2, size=size2, fill=color2 or P["muted"],
               anchor="middle")
    return c


def tag(c, x, y, s, color=P["muted"], bg=P["white"], size=10.5, pad=5, h=16,
        stroke=None, anchor="start"):
    w = tw(s, size) + pad * 2
    x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    c.rect(x0, y - h / 2, w, h, fill=bg, stroke=stroke or "none", rx=h / 2)
    c.text(x0 + w / 2, y + 3.4, s, size=size, fill=color, anchor="middle")
    return w


def shape(c, cx, y, s, size=10, color=None):
    c.text(cx, y, s, size=size, fill=color or P["muted"], anchor="middle", family="mono")
    return c


def mat_block(c, x, y, cols, rows, cell=14, fill=P["blueL"], stroke=P["blueM"],
              gap=1.0):
    return c.mat(x, y, cols, rows, cell=cell, fill=fill, stroke=stroke, gap=gap)


def pad_grid(c, x, y, vals, cell=14, cmap=BLUES, vmin=0, vmax=1, gap=1.0,
             rows_label=None, cols_label=None):
    g = c.heat(x, y, len(vals[0]) * cell, len(vals) * cell, vals, cmap=cmap,
               vmin=vmin, vmax=vmax, gap=gap)
    return g


def plus_circle(c, cx, cy, r=9, label="+", fill=P["white"], stroke=P["ink2"]):
    c.circle(cx, cy, r, fill=fill, stroke=stroke, sw=1.1)
    c.text(cx, cy + 3.8, label, size=r * 1.35, fill=P["ink2"], anchor="middle")
    return c


def norm_box(c, x, y, w, h, label="Add & Norm", fill=P["goldL"], stroke=P["goldM"]):
    c.rect(x, y, w, h, fill=fill, stroke=stroke, rx=4)
    c.text(x + w / 2, y + h / 2 + 3.9, label, size=10.8, fill=P["gold"],
           anchor="middle", weight="600")
    return c


def sec_label(c, x, y, s, color=None):
    c.text(x, y, s, size=11.5, fill=color or P["ink2"], weight="600", ls="0.02em")
    return c


def note(c, x, y, s, size=11, color=None, anchor="start"):
    c.text(x, y, s, size=size, fill=color or P["muted"], anchor=anchor)
    return c


def chips(c, cx, y, toks, h=24, size=11.5, pad=10, gap=5, fill=P["panel"],
          stroke=P["rule"], colors=None, color=None, weight=None):
    """Centred row of rounded token chips; returns ([(x, w)], total_width)."""
    widths = [max(26, tw(t, size, weight=weight) + pad * 2) for t in toks]
    total = sum(widths) + gap * (len(toks) - 1)
    x = cx - total / 2
    spans = []
    for i, (t, w) in enumerate(zip(toks, widths)):
        c.rect(x, y, w, h, fill=(colors[i] if colors else fill), stroke=stroke, rx=4)
        c.text(x + w / 2, y + h / 2 + size * 0.36, t, size=size,
               fill=color or P["ink2"], anchor="middle")
        spans.append((x, w))
        x += w + gap
    return spans, total


def panel(c, x, y, w, h, title=None, fill=P["white"], stroke=P["rule"], rx=8,
          title_color=None):
    c.rect(x, y, w, h, fill=fill, stroke=stroke, rx=rx, sw=1)
    if title:
        c.text(x + 16, y + 20, title, size=11.5, fill=title_color or P["ink2"],
               weight="600")
    return c
