"""Build four editable SVG teaching figures using Python's standard library.

Run: python scripts/build_figures.py
The numeric examples are illustrative models, not instrument or process data.
"""
from pathlib import Path
from html import escape
from math import sqrt
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
C = {"ink": "#183247", "muted": "#60778a", "line": "#cfdae3",
     "blue": "#2563eb", "orange": "#d97706", "teal": "#0f766e",
     "paper": "#f5f8fb", "pale_blue": "#eaf1ff", "pale_orange": "#fff3df",
     "pale_teal": "#e7f5f1"}


def text(x, y, s, size=20, fill="ink", weight=400, anchor="start", **kwargs):
    attrs = " ".join(f'{k.replace("_", "-")}="{escape(str(v))}"' for k, v in kwargs.items())
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{C.get(fill, fill)}" '
            f'font-weight="{weight}" text-anchor="{anchor}" {attrs}>{escape(s)}</text>')


def rect(x, y, w, h, fill="paper", stroke="none", rx=14, sw=1):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{C.get(fill, fill)}" stroke="{C.get(stroke, stroke)}" stroke-width="{sw}"/>')


def line(x1, y1, x2, y2, color="line", width=1.5, dash="", marker=""):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{C.get(color, color)}" stroke-width="{width}" '
            f'stroke-dasharray="{dash}"' + (f' marker-end="url(#{marker})"' if marker else '') + '/>')


def circle(x, y, r=5, fill="blue", stroke="white", sw=2):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{C.get(fill, fill)}" stroke="{C.get(stroke, stroke)}" stroke-width="{sw}"/>'


def path(points, color="blue", width=3, dash=""):
    d = " ".join(("M" if i == 0 else "L") + f"{x:.3f},{y:.3f}" for i, (x, y) in enumerate(points))
    return f'<path d="{d}" fill="none" stroke="{C.get(color, color)}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="{dash}"/>'


def begin(title, subtitle, height, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" fill="#60778a"/></marker></defs>',
            '<g font-family="Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif">',
            rect(0, 0, 1200, height, "white", rx=0), text(40, 53, title, 29, weight=700),
            text(40, 89, subtitle, 19, "muted")]


def save(name, parts):
    source = "\n".join(parts + ["</g></svg>"])
    ET.fromstring(source)
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(source, encoding="utf-8")
    print(name)


def epe():
    p = begin("边缘为什么会偏：位置与线宽共同决定 EPE", "一维线条算例：目标左边缘 0 nm，右边缘 40 nm，目标中心 20 nm；坐标向右为正", 650,
              "三个面板分别展示纯平移、纯变宽及二者叠加。叠加时中心偏移4纳米、线宽增加6纳米，左边缘偏移1纳米、右边缘偏移7纳米。")
    examples = [("① 纯平移", 4, 44, "+4", "0", "+4", "+4"),
                ("② 纯变宽", -3, 43, "0", "+6", "−3", "+3"),
                ("③ 平移 + 变宽", 1, 47, "+4", "+6", "+1", "+7")]
    for i, (title, left, right, dc, dw, el, er) in enumerate(examples):
        x = 40 + 380 * i
        p += [rect(x, 122, 360, 430), text(x + 22, 158, title, 23, weight=700)]
        sx = lambda v: x + 67 + 5 * v
        p += [text(x + 22, 198, "目标", 17, "muted"),
              rect(sx(0), 214, 200, 37, "pale_blue", "blue", rx=0, sw=2),
              text(sx(0), 278, "0", 18, "blue", anchor="middle"),
              text(sx(40), 278, "40", 18, "blue", anchor="middle"),
              text(x + 22, 316, "实际", 17, "muted"),
              line(sx(0), 208, sx(0), 379, "blue", 1, "4 5"),
              line(sx(40), 208, sx(40), 379, "blue", 1, "4 5"),
              rect(sx(left), 332, 5 * (right - left), 37, "pale_orange", "orange", rx=0, sw=2),
              text(sx(left), 397, str(left).replace('-', '−'), 18, "orange", anchor="middle"),
              text(sx(right), 397, str(right), 18, "orange", anchor="middle"),
              text(x + 22, 440, f"中心误差 Δc = {dc} nm", 20),
              text(x + 22, 473, f"线宽误差 Δw = {dw} nm", 20),
              text(x + 22, 521, f"左 EPE {el} nm　右 EPE {er} nm", 20, "teal", 700)]
    p += [text(40, 594, "Δx左 = Δc − Δw / 2", 23, "blue", 600),
          text(430, 594, "Δx右 = Δc + Δw / 2", 23, "orange", 600),
          text(40, 628, "教学几何示意。Δc 是该线条相对目标的位置误差；两层相对位置才是 Overlay。", 17, "muted")]
    assert 24 - 46 / 2 == 1 and 24 + 46 / 2 == 47
    save("fig01_epe.svg", p)


def axes(p, x, y, w, h, xr, yr, xticks, yticks, xlabel, ylabel):
    sx = lambda z: x + (z - xr[0]) / (xr[1] - xr[0]) * w
    sy = lambda z: y + h - (z - yr[0]) / (yr[1] - yr[0]) * h
    for v in yticks:
        p += [line(x, sy(v), x + w, sy(v), "line", 1), text(x - 12, sy(v) + 6, f"{v:g}".replace('-', '−'), 16, "muted", anchor="end")]
    for v in xticks:
        p += [line(sx(v), y + h, sx(v), y + h + 6, "muted", 1.2), text(sx(v), y + h + 28, f"{v:g}".replace('-', '−'), 16, "muted", anchor="middle")]
    p += [line(x, y, x, y + h, "muted", 1.5), line(x, y + h, x + w, y + h, "muted", 1.5),
          text(x, y - 16, ylabel, 17, "muted"), text(x + w / 2, y + h + 58, xlabel, 17, "muted", anchor="middle")]
    return sx, sy


def correctability():
    xs = [-1, -.5, 0, .5, 1]
    residual = [1, -2, 2, -2, 1]
    fit = [3 + 2*x for x in xs]
    total = [a+b for a,b in zip(fit, residual)]
    assert sum(residual) == 0 and sum(x*r for x,r in zip(xs,residual)) == 0
    p = begin("预测出来的误差，设备能修正多少？", "五个测点等权；设备的补偿模型仅包含平移项和线性项", 700,
              "总误差2、0、5、2、6纳米，分解为线性可补偿项1、2、3、4、5纳米与残差1、负2、2、负2、1纳米。修正参数为平移负3纳米和线性项负2纳米每单位归一化坐标。")
    series = [("① 预测总误差 u", total, "blue", "[2, 0, 5, 2, 6] nm"),
              ("② 可补偿部分 3 + 2x", fit, "teal", "[1, 2, 3, 4, 5] nm"),
              ("③ 补偿后的残差 r", residual, "orange", "[1, −2, 2, −2, 1] nm")]
    for i, (title, values, color, nums) in enumerate(series):
        x=40+380*i
        p += [rect(x, 122, 360, 438), text(x+20, 158, title, 22, weight=700)]
        sx,sy=axes(p,x+48,201,285,267,(-1.1,1.1),(-3,7),[-1,0,1],[-2,0,2,4,6],"归一化位置 x","位移 / nm")
        p += [line(sx(-1.1),sy(0),sx(1.1),sy(0),"muted",1.3,"5 4"), path([(sx(a),sy(b)) for a,b in zip(xs,values)],color)]
        p += [circle(sx(a),sy(b),5.5,color) for a,b in zip(xs,values)]
        p += [text(x+180,548,nums,19,color,600,anchor="middle")]
    rms_before=sqrt(sum(y*y for y in total)/5)
    rms_after=sqrt(sum(y*y for y in residual)/5)
    p += [text(40,603,"执行修正：c₀ = −3 nm，c₁ = −2 nm / 单位 x",22,"ink",600),
          text(40,639,f"修正前 RMS {rms_before:.2f} nm → 修正后 {rms_after:.2f} nm；剩余起伏需要其他工艺措施。",21,"teal",600),
          text(40,676,"教学离散模型。折线仅连接测点；残差与常量项、线性项均正交。",17,"muted")]
    save("fig03_correctability.svg",p)


def focus_dose():
    p=begin("Focus 与 Dose：多测一个信号，何时才有帮助？", "单一尺寸可能对应多个曝光条件；不同敏感方向的信号，才能共同确定局部状态",740,
            "左图用二次离焦和线性剂量的教学模型展示同一CD对应多个Focus Dose组合。右图在原点附近用两个线性响应的等值线交点说明局部可辨识性。")
    p += [rect(40,122,550,485),rect(610,122,550,485),text(62,160,"① 单个 CD：多个解",24,weight=700),text(632,160,"② 两个独立响应：局部交点",24,weight=700)]
    sx,sy=axes(p,100,244,435,260,(-1,1),(-2,4),[-1,-.5,0,.5,1],[-2,0,2,4],"归一化离焦 f","ΔCD / nm")
    for d,c in [(-.5,"orange"),(0,"blue"),(.5,"teal")]:
        pts=[(-1+2*j/160,2*(-1+2*j/160)**2-3*d) for j in range(161)]
        p+=[path([(sx(a),sy(b)) for a,b in pts],c,3)]
    p += [line(sx(-1),sy(0),sx(1),sy(0),"muted",1.4,"5 4")]
    for f in [-sqrt(.75),0,sqrt(.75)]:
        p += [circle(sx(f),sy(0),6,"teal" if f else "blue")]
    for x,d,c in [(72,"−0.5","orange"),(244,"0","blue"),(385,"+0.5","teal")]:
        p += [line(x,195,x+24,195,c,3),text(x+31,202,"d = "+d,17,c)]
    p += [text(315,588,"同一条 ΔCD = 0 线穿过多个条件",18,"muted",anchor="middle")]
    sx2,sy2=axes(p,690,244,400,260,(-.35,.35),(-.35,.35),[-.3,0,.3],[-.3,0,.3],"归一化离焦 f","归一化剂量变化 d")
    p += [line(sx2(-.35),sy2(0),sx2(.35),sy2(0),"blue",3.5),
          line(sx2(-.35),sy2(.35),sx2(.35),sy2(-.35),"teal",3.5),circle(sx2(0),sy2(0),7,"orange"),
          text(sx2(.03),sy2(.04),"(0, 0)",17,"orange",600),
          line(663,195,687,195,"blue",3),text(695,202,"s₁ = 0",17,"blue"),
          line(890,195,914,195,"teal",3),text(922,202,"s₂ = 0",17,"teal"),
          text(885,588,"局部线性化：s₁ = −3d，s₂ = f + d",18,"muted",anchor="middle")]
    p += [text(40,645,"教学模型：ΔCD / nm = 2f² − 3d；f = F / (50 nm)，d = (D − D₀) / (0.02D₀)。",20),
          text(40,681,"右图取 s₁ = ΔCD / nm、s₂ = f + d，在 (0,0) 处灵敏度矩阵的两行分别为 [0,−3]、[1,1]。",18),
          text(40,719,"右图只表示原点附近（|f|、|d| ≤ 0.35）的局部线性关系；曲线与尺度均为教学设定。",17,"muted")]
    save("fig04_focus_dose.svg",p)


def mini_image(p,x,y,label,color):
    p += [rect(x,y,100,76,"white",color,rx=8,sw=1.8)]
    for j in range(5):
        p += [rect(x+15+15*j,y+14,7,39,color,rx=1)]
    p += [text(x+50,y+68,label,13,"muted",anchor="middle")]


def data_split():
    p=begin("训练集怎样拆，决定测试结果回答什么问题", "目标：预测后续批次。划分单位应覆盖整片晶圆，并保留时间顺序。",740,
            "上图展示同一Mark重复图像被随机分入训练集和测试集造成信息泄漏。下图按批次与时间整体留出训练、校准、最终测试，并只用训练数据拟合预处理。")
    p += [rect(40,122,1120,223,"pale_orange"),text(62,157,"随机拆图片",24,"orange",700),
          text(62,198,"同一 Mark",21,weight=600),text(62,231,"同一片 Wafer",19,"muted"),
          line(242,218,310,218,"muted",1.8,marker="arrow")]
    for x,label,tag,color in [(330,"重复采集 A","训练","blue"),(510,"重复采集 B","训练","blue"),(690,"重复采集 C","测试","orange")]:
        mini_image(p,x,177,label,color)
        p += [rect(x,264,100,33,"pale_blue" if color=="blue" else "white",rx=5),text(x+50,288,tag,18,color,600,anchor="middle")]
    p += [text(848,206,"相同结构与采集背景",20),text(848,240,"已进入训练集",20),
          text(62,328,"测试可能只是再次识别熟悉的样本，无法代表新批次的表现。",18,"orange")]
    p += [text(40,393,"按 Lot / 时间整体留出",24,"teal",700),
          line(575,385,1135,385,"muted",1.6,marker="arrow"),text(850,373,"生产时间 →",17,"muted",anchor="middle")]
    for i,(lot,role,color,pale) in enumerate([("Lot 1","训练","blue","pale_blue"),("Lot 2","训练","blue","pale_blue"),("Lot 3","校准 / 调参","teal","pale_teal"),("Lot 4","最终测试","orange","pale_orange")]):
        x=40+285*i
        p += [rect(x,420,265,166,pale),text(x+20,453,lot,21,weight=600),text(x+20,486,role,20,color,600)]
        for j in range(3):
            xx=x+23+76*j
            p += [rect(xx,508,66,54,"white",color,rx=6),text(xx+33,542,f"W{j+1}",18,color,anchor="middle")]
    p += [text(40,618,"同一 Wafer 的重复图像与重叠 ROI 留在同一组；最终测试集只用于最后评价。",19),
          rect(40,641,1120,58,"paper"),text(60,677,"归一化 / 特征选择 / 降维：仅在训练集拟合 → 固定参数后应用于校准集和测试集",20,"teal",600),
          text(40,727,"示意划分。若实际目标是跨设备或跨结构迁移，还需按对应设备或结构族留出。",17,"muted")]
    save("fig06_data_split.svg",p)


if __name__ == "__main__":
    epe()
    correctability()
    focus_dose()
    data_split()
