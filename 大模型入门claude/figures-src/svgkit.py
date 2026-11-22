"""svgkit —— 讲义插图的极简 SVG 绘图工具（纯 Python，无第三方依赖）。

设计约定（所有图共享，保证全书风格统一）：
  * 白底、圆角浅色块、深灰文字；颜色只用来表达"语义"，不做装饰。
  * 语义色：Query=橙  Key=蓝  Value=绿  注意力/高亮=紫  损失/禁止=红
            FFN/变换=青  中性=灰   数据/样本=黄
  * 数学用 $...$ 包裹：字母斜体衬线，支持 _{下标} 与 ^{上标}。
"""
from __future__ import annotations

import base64
import math
import re
import struct
import zlib
from pathlib import Path
from xml.sax.saxutils import escape

# ----------------------------------------------------------------------------
# 字体与配色
# ----------------------------------------------------------------------------
FONT = "'PingFang SC','Microsoft YaHei','Noto Sans SC','Source Han Sans SC','Hiragino Sans GB',sans-serif"
MATH = "'Cambria Math','STIX Two Math','Latin Modern Math','Times New Roman',serif"
MONO = "'Cascadia Mono','Consolas','Menlo','DejaVu Sans Mono',monospace"

INK = "#1F2937"      # 正文
MUTED = "#6B7280"    # 次要文字
LINE = "#9CA3AF"     # 普通连线
BORDER = "#D1D5DB"   # 浅边框
PANEL = "#F6F7F9"    # 面板底色
WHITE = "#FFFFFF"

# 语义色：(主色, 浅底)
C = {
    "q": ("#E07B24", "#FDEBD8"),       # Query / 解码器侧 / 生成
    "k": ("#2F6FD0", "#DDE8FA"),       # Key / 编码器侧 / 输入
    "v": ("#2A9D66", "#D9F1E5"),       # Value / 正确 / 通过
    "attn": ("#7B4FC9", "#ECE4FA"),    # 注意力 / 高亮
    "loss": ("#D64545", "#FBE1E1"),    # 损失 / 禁止 / 错误
    "ffn": ("#14919B", "#D4F0F1"),     # FFN / 变换
    "gray": ("#6B7280", "#EEF0F3"),    # 中性模块
    "data": ("#C98A00", "#FFF3CC"),    # 数据 / 样本
    "pink": ("#C2417F", "#F9E0EC"),
}


def main(key):
    return C[key][0]


def light(key):
    return C[key][1]


def mix(c1: str, c2: str, t: float) -> str:
    """颜色线性插值，t=0 得 c1，t=1 得 c2。"""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    r = [round(a[i] + (b[i] - a[i]) * t) for i in range(3)]
    return "#%02X%02X%02X" % tuple(r)


def heat(t: float, key="attn") -> str:
    """0→白，1→语义主色（略加深），用于热图。"""
    t = max(0.0, min(1.0, t))
    return mix("#FFFFFF", mix(main(key), "#000000", 0.12), t ** 0.85)


# ----------------------------------------------------------------------------
# 文字宽度估算（用于自动排版；只求近似）
# ----------------------------------------------------------------------------
def _char_w(ch: str) -> float:
    o = ord(ch)
    if o > 0x2E80:
        return 1.0
    if ch in "il.,:;'|!·":
        return 0.3
    if ch in "mwMW":
        return 0.85
    if ch.isupper():
        return 0.66
    if ch == " ":
        return 0.3
    return 0.55


def text_width(s: str, size: float) -> float:
    plain = re.sub(r"[_^]\{([^}]*)\}", lambda m: m.group(1), s.replace("$", ""))
    return sum(_char_w(c) for c in plain) * size


# ----------------------------------------------------------------------------
# 富文本：$...$ 数学段，_{..} 下标，^{..} 上标
# ----------------------------------------------------------------------------
_GREEK_UP = set("ΣΠΔΩΘΛΞΦΨΓ")
_OPS = set("0123456789()[]{}=+−-×·,.;:|‖√∑∏∞→←≈≤≥<>/!'⊙⊤ ")


def _math_runs(s: str):
    """把数学串拆成 (text, italic) 片段：字母斜体，数字与符号正体。"""
    runs = []
    for ch in s:
        it = not (ch in _OPS or ch in _GREEK_UP or ord(ch) > 0x2E80)
        if runs and runs[-1][1] == it:
            runs[-1][0] += ch
        else:
            runs.append([ch, it])
    return runs


def rich(s: str, size: float) -> str:
    """把带标记的字符串转为 <tspan> 序列（不含外层 <text>）。"""
    out = []
    parts = re.split(r"(\$[^$]*\$)", s)
    for part in parts:
        if not part:
            continue
        is_math = part.startswith("$") and part.endswith("$") and len(part) >= 2
        body = part[1:-1] if is_math else part
        # 拆出上下标
        tokens = re.split(r"([_^]\{[^}]*\})", body)
        for tok in tokens:
            if not tok:
                continue
            if tok[0] in "_^" and tok[1:2] == "{":
                inner = tok[2:-1]
                small = size * 0.72
                dy = size * (0.28 if tok[0] == "_" else -0.38)
                segs = _math_runs(inner) if is_math else [[inner, False]]
                first = True
                for txt, it in segs:
                    attrs = f'font-size="{small:.1f}"'
                    if first:
                        attrs += f' dy="{dy:.1f}"'
                        first = False
                    if is_math:
                        attrs += f' font-family="{MATH}"' + (' font-style="italic"' if it else "")
                    out.append(f"<tspan {attrs}>{escape(txt)}</tspan>")
                # 复位基线（用一个零宽空格承载 dy）
                out.append(f'<tspan dy="{-dy:.1f}" font-size="{size:.1f}">​</tspan>')
            else:
                if is_math:
                    for txt, it in _math_runs(tok):
                        st = ' font-style="italic"' if it else ""
                        out.append(f'<tspan font-family="{MATH}"{st}>{escape(txt)}</tspan>')
                else:
                    out.append(escape(tok))
    return "".join(out)


# ----------------------------------------------------------------------------
# SVG 画布
# ----------------------------------------------------------------------------
class SVG:
    def __init__(self, w: float, h: float, title: str = "", desc: str = ""):
        self.w, self.h = w, h
        self.title, self.desc = title, desc
        self.body: list[str] = []
        self.defs: dict[str, str] = {}

    # ---- 基础 ----
    def raw(self, s: str):
        self.body.append(s)

    def rect(self, x, y, w, h, fill=WHITE, stroke="none", sw=1.2, rx=0, dash=None, opacity=None, extra=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.raw(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{o} {extra}/>')

    def circle(self, cx, cy, r, fill=WHITE, stroke="none", sw=1.2, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.raw(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{o}/>')

    def line(self, x1, y1, x2, y2, color=LINE, sw=1.5, dash=None, cap="round", opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.raw(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
                 f'stroke-width="{sw}" stroke-linecap="{cap}"{d}{o}/>')

    def path(self, d, stroke=LINE, sw=1.5, fill="none", dash=None, opacity=None, extra=""):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.raw(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" '
                 f'stroke-linecap="round" stroke-linejoin="round"{da}{o} {extra}/>')

    def polyline(self, pts, stroke=LINE, sw=1.5, fill="none", dash=None, opacity=None):
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.path(d, stroke, sw, fill, dash, opacity)

    def text(self, x, y, s, size=15, color=INK, anchor="middle", weight="normal", italic=False,
             family=None, opacity=None, baseline="central"):
        fam = f' font-family="{family}"' if family else ""
        st = ' font-style="italic"' if italic else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        wt = f' font-weight="{weight}"' if weight != "normal" else ""
        self.raw(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
                 f'dominant-baseline="{baseline}"{wt}{st}{fam}{o}>{rich(s, size)}</text>')

    def lines(self, x, y, items, size=14, gap=None, **kw):
        """多行文字，items 为字符串列表，y 为第一行中心。"""
        gap = gap or size * 1.45
        for i, s in enumerate(items):
            self.text(x, y + i * gap, s, size=size, **kw)

    # ---- 复合元素 ----
    def box(self, x, y, w, h, label="", key="gray", sub=None, size=15, rx=8, fill=None, stroke=None,
            sw=1.4, weight="bold", color=None, dash=None, subsize=None):
        fill = fill or light(key)
        stroke = stroke or main(key)
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx, dash=dash)
        cx, cy = x + w / 2, y + h / 2
        color = color or INK
        if sub:
            subsize = subsize or size * 0.8
            self.text(cx, cy - subsize * 0.62, label, size=size, weight=weight, color=color)
            self.text(cx, cy + size * 0.68, sub, size=subsize, color=MUTED)
        elif label:
            self.text(cx, cy, label, size=size, weight=weight, color=color)

    def pill(self, x, y, s, key="gray", size=13, pad=9, h=None, fill=None, stroke=None, color=INK,
             anchor="middle", weight="normal", family=None):
        """文字胶囊（token 块）。返回 (x0, x1)。"""
        w = text_width(s, size) + 2 * pad
        h = h or size * 1.9
        x0 = x - w / 2 if anchor == "middle" else (x if anchor == "start" else x - w)
        self.rect(x0, y - h / 2, w, h, fill=fill or light(key), stroke=stroke or main(key), sw=1.1, rx=h / 2.6)
        self.text(x0 + w / 2, y, s, size=size, color=color, weight=weight, family=family)
        return x0, x0 + w

    def _marker(self, color: str, size: float = 1.0) -> str:
        mid = f"ah{color.strip('#')}{str(size).replace('.', '_')}"
        if mid not in self.defs:
            s = 9 * size
            self.defs[mid] = (f'<marker id="{mid}" viewBox="0 0 10 10" refX="8.6" refY="5" markerWidth="{s:.1f}" '
                              f'markerHeight="{s:.1f}" markerUnits="userSpaceOnUse" orient="auto-start-reverse">'
                              f'<path d="M0,0.8 L9.6,5 L0,9.2 L2.6,5 Z" fill="{color}"/></marker>')
        return mid

    def arrow(self, pts, color=LINE, sw=1.7, dash=None, head=1.0, both=False, curve=False, opacity=None):
        """折线箭头；curve=True 且 3 点时用二次贝塞尔。pts=[(x,y),...]"""
        mid = self._marker(color, head)
        if curve and len(pts) == 3:
            (x0, y0), (cx, cy), (x1, y1) = pts
            d = f"M{x0:.1f},{y0:.1f} Q{cx:.1f},{cy:.1f} {x1:.1f},{y1:.1f}"
        elif curve and len(pts) == 4:
            (x0, y0), (c1x, c1y), (c2x, c2y), (x1, y1) = pts
            d = f"M{x0:.1f},{y0:.1f} C{c1x:.1f},{c1y:.1f} {c2x:.1f},{c2y:.1f} {x1:.1f},{y1:.1f}"
        else:
            d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        start = f' marker-start="url(#{mid})"' if both else ""
        self.path(d, stroke=color, sw=sw, dash=dash, opacity=opacity,
                  extra=f'marker-end="url(#{mid})"{start}')

    def harrow(self, x1, x2, y, **kw):
        self.arrow([(x1, y), (x2, y)], **kw)

    def varrow(self, x, y1, y2, **kw):
        self.arrow([(x, y1), (x, y2)], **kw)

    def panel(self, x, y, w, h, title=None, key=None, size=15, fill=PANEL, rx=12, tag=None):
        """带标题的浅底面板。tag 为左上角小圆标号（如 '①'）。"""
        stroke = main(key) if key else BORDER
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.1, rx=rx)
        if title:
            tx = x + 16
            if tag:
                self.circle(x + 26, y + 22, 11, fill=main(key) if key else INK)
                self.text(x + 26, y + 22.5, tag, size=12.5, color=WHITE, weight="bold")
                tx = x + 44
            self.text(tx, y + 22, title, size=size, anchor="start", weight="bold", color=INK)

    def grid(self, x, y, rows, cols, cell, fills=None, stroke=WHITE, sw=1.2, values=None, vsize=None,
             vcolor=None, cellh=None, rx=0):
        """矩阵网格。fills/values 为 rows×cols 的二维列表或函数 f(i,j)。"""
        ch = cellh or cell
        for i in range(rows):
            for j in range(cols):
                f = fills(i, j) if callable(fills) else (fills[i][j] if fills else PANEL)
                self.rect(x + j * cell, y + i * ch, cell, ch, fill=f, stroke=stroke, sw=sw, rx=rx)
                if values is not None:
                    v = values(i, j) if callable(values) else values[i][j]
                    if v is None or v == "":
                        continue
                    col = vcolor(i, j) if callable(vcolor) else (vcolor or INK)
                    self.text(x + j * cell + cell / 2, y + i * ch + ch / 2, str(v),
                              size=vsize or min(cell, ch) * 0.36, color=col)

    def brace(self, x1, y1, x2, y2, label="", color=MUTED, size=13, depth=8, side=1):
        """简洁的方括号形标注线（水平或竖直）。side=+1 标签在下/右。"""
        if abs(y2 - y1) < 1e-6:  # 水平
            yy = y1 + side * depth
            self.path(f"M{x1:.1f},{y1:.1f} L{x1:.1f},{yy:.1f} L{x2:.1f},{yy:.1f} L{x2:.1f},{y1:.1f}", stroke=color, sw=1.2)
            if label:
                self.text((x1 + x2) / 2, yy + side * (size * 0.95), label, size=size, color=color)
        else:  # 竖直
            xx = x1 + side * depth
            self.path(f"M{x1:.1f},{y1:.1f} L{xx:.1f},{y1:.1f} L{xx:.1f},{y2:.1f} L{x1:.1f},{y2:.1f}", stroke=color, sw=1.2)
            if label:
                self.text(xx + side * 6, (y1 + y2) / 2, label, size=size, color=color,
                          anchor="start" if side > 0 else "end")

    def image(self, x, y, w, h, uri, pixelated=True, opacity=None):
        r = ' style="image-rendering:pixelated;image-rendering:crisp-edges"' if pixelated else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.raw(f'<image x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" href="{uri}" '
                 f'preserveAspectRatio="none"{r}{o}/>')

    def note(self, x, y, s, size=13, color=MUTED, anchor="start", **kw):
        self.text(x, y, s, size=size, color=color, anchor=anchor, **kw)

    def badge(self, cx, cy, s, key="gray", r=11, size=12.5):
        self.circle(cx, cy, r, fill=main(key))
        self.text(cx, cy + 0.5, s, size=size, color=WHITE, weight="bold")

    # ---- 输出 ----
    def to_string(self) -> str:
        defs = "".join(self.defs.values())
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w:.0f}" height="{self.h:.0f}" '
                f'viewBox="0 0 {self.w:.0f} {self.h:.0f}" font-family="{FONT}" role="img">')
        meta = f"<title>{escape(self.title)}</title>"
        if self.desc:
            meta += f"<desc>{escape(self.desc)}</desc>"
        bg = f'<rect width="{self.w:.0f}" height="{self.h:.0f}" fill="#FFFFFF"/>'
        return head + meta + (f"<defs>{defs}</defs>" if defs else "") + bg + "\n".join(self.body) + "</svg>\n"

    def save(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(self.to_string(), encoding="utf-8")


# ----------------------------------------------------------------------------
# 位图：纯 Python PNG 编码，嵌入为 data URI（用于数字图像、噪声等）
# ----------------------------------------------------------------------------
def png_uri(pixels, mode="L") -> str:
    """pixels: 二维列表，L 模式元素为 0..1 灰度（1=黑笔画），RGB 模式元素为 (r,g,b) 0..255。"""
    h = len(pixels)
    w = len(pixels[0])
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for p in row:
            if mode == "L":
                v = max(0.0, min(1.0, p))
                raw.append(int(round(255 * (1 - v))))
            else:
                raw.extend(bytes(int(max(0, min(255, c))) for c in p))
    color_type = 0 if mode == "L" else 2

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, color_type, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    return "data:image/png;base64," + base64.b64encode(png).decode()


def raster_strokes(strokes, n=28, width=1.6, soft=0.9):
    """把若干折线笔画（坐标 0..1）栅格化成 n×n 灰度图，模拟手写数字。"""
    img = [[0.0] * n for _ in range(n)]
    segs = []
    for st in strokes:
        for a, b in zip(st, st[1:]):
            segs.append((a[0] * n, a[1] * n, b[0] * n, b[1] * n))
    for i in range(n):
        for j in range(n):
            px, py = j + 0.5, i + 0.5
            dmin = 1e9
            for x1, y1, x2, y2 in segs:
                dx, dy = x2 - x1, y2 - y1
                L2 = dx * dx + dy * dy or 1e-9
                t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
                d = math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
                dmin = min(dmin, d)
            v = 1.0 - (dmin - width) / soft
            img[i][j] = max(0.0, min(1.0, v))
    return img


def arc_pts(cx, cy, rx, ry, a0, a1, k=14):
    """椭圆弧上的点（角度单位：度，0 度朝右，顺时针为正——SVG 坐标）。"""
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * t / k)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * t / k))) for t in range(k + 1)]


def digit_strokes(d: int):
    """几个手写风格数字的笔画（0..1 坐标）。"""
    if d == 3:
        return [arc_pts(0.5, 0.33, 0.2, 0.15, 200, 445, 16), arc_pts(0.5, 0.64, 0.23, 0.18, 270, 520, 16)]
    if d == 7:
        return [[(0.25, 0.22), (0.76, 0.22), (0.47, 0.84)], [(0.38, 0.52), (0.66, 0.52)]]
    if d == 2:
        return [arc_pts(0.5, 0.35, 0.2, 0.15, 190, 380, 14) + [(0.28, 0.78), (0.76, 0.78)]]
    if d == 0:
        return [arc_pts(0.5, 0.5, 0.2, 0.3, 0, 360, 28)]
    if d == 8:
        return [arc_pts(0.5, 0.32, 0.16, 0.13, 0, 360, 24), arc_pts(0.5, 0.65, 0.2, 0.17, 0, 360, 24)]
    if d == 1:
        return [[(0.4, 0.3), (0.53, 0.2), (0.53, 0.8)]]
    if d == 5:
        return [[(0.7, 0.2), (0.35, 0.2), (0.32, 0.47)] + arc_pts(0.5, 0.62, 0.21, 0.18, 230, 500, 14)]
    raise ValueError(d)


def blur(img, r=1):
    """简单方框模糊（模拟重建结果略模糊）。"""
    n, m = len(img), len(img[0])
    out = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            s, c = 0.0, 0
            for di in range(-r, r + 1):
                for dj in range(-r, r + 1):
                    ii, jj = i + di, j + dj
                    if 0 <= ii < n and 0 <= jj < m:
                        s += img[ii][jj]
                        c += 1
            out[i][j] = s / c
    return out


class RNG:
    """可复现的伪随机数（避免依赖 random 的跨版本差异）。"""

    def __init__(self, seed=1):
        self.s = seed & 0xFFFFFFFF or 1

    def u(self):
        self.s ^= (self.s << 13) & 0xFFFFFFFF
        self.s ^= self.s >> 17
        self.s ^= (self.s << 5) & 0xFFFFFFFF
        return (self.s & 0xFFFFFFFF) / 4294967296.0

    def normal(self):
        u1 = max(self.u(), 1e-12)
        u2 = self.u()
        return math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)


def softmax(xs, tau=1.0):
    m = max(xs)
    e = [math.exp((x - m) / tau) for x in xs]
    s = sum(e)
    return [v / s for v in e]


OUT = Path(__file__).resolve().parents[1] / "images"
