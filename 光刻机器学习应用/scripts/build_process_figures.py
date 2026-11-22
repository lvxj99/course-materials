"""Rebuild the report's process, metrology and timing diagrams (standard library)."""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
C = {'ink':'#183247','muted':'#526477','blue':'#2563eb','orange':'#d97706','teal':'#0f766e','line':'#dbe3ec'}

class Fig:
    def __init__(self, title, subtitle, height=720):
        self.height=height
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img"><title>{escape(title)}</title><desc>{escape(subtitle)}</desc>',
            '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0 0 L8 4 L0 8Z" fill="context-stroke"/></marker></defs>',
            '<rect width="1200" height="100%" fill="#fff"/>',
            '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;fill:#183247} .small{font-size:18px}.body{font-size:21px}.head{font-size:24px;font-weight:600}</style>']
        self.text(40,48,title,30,weight=700)
        self.text(40,84,subtitle,19,color=C['muted'])
    def text(self,x,y,s,size=21,color=None,anchor='start',weight=400):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}"'+(f' style="fill:{color}"' if color else '')+f'>{escape(s)}</text>')
    def rect(self,x,y,w,h,fill='#f7f9fc',stroke=C['line'],r=12):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
    def line(self,x1,y1,x2,y2,color=C['muted'],width=2,arrow=False,dash=False):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(' marker-end="url(#arr)"' if arrow else '')+(' stroke-dasharray="6 5"' if dash else '')+'/>')
    def path(self,d,color=C['teal'],arrow=True):
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.5"'+(' marker-end="url(#arr)"' if arrow else '')+'/>')
    def box(self,x,y,w,h,title,lines,fill='#f7f9fc',color=C['ink']):
        self.rect(x,y,w,h,fill)
        self.text(x+w/2,y+32,title,23,color,anchor='middle',weight=650)
        for i,s in enumerate(lines):self.text(x+w/2,y+64+i*28,s,18,anchor='middle')
    def circle(self,x,y,r,color):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')
    def save(self,name):
        data=''.join(self.parts)+'</svg>'
        ET.fromstring(data)
        (OUT/name).write_text(data,encoding='utf-8')

def process():
    f=Fig('光刻机器学习：沿工艺链看输入、输出与反馈','读图顺序：先沿上方工艺流程向右，再看量测结果怎样回到后续工艺。',690)
    stages=[('设计版图',['目标边缘与结构']),('计算光刻',['OPC / ILT / SMO']),('曝光',['对准、调焦、剂量']),('烘烤与显影',['光刻胶形成图形']),('实际量测',['CD / Overlay / 缺陷'])]
    for i,(t,ls) in enumerate(stages):
        x=40+i*232
        f.box(x,150,192,100,t,ls,fill='#eef4ff' if i in [1,2] else '#f7f9fc')
        if i<4:f.line(x+194,200,x+226,200,arrow=True)
    f.text(40,126,'实际工艺',20,C['muted'],weight=600)
    f.box(40,320,285,122,'设计与仿真数据',['学习：掩模初始解、快速仿真','输出：更快的优化过程'])
    f.box(370,320,320,122,'当前晶圆的状态数据',['Alignment / Leveling / 设备信号','输出：曝光前的位置与状态估计'])
    f.box(735,320,425,122,'量测与完整工艺历史',['图像 / 光谱 / Scanner 与 Track 时序','输出：尺寸、位置、偏差与空间指纹'])
    f.path('M183 320 V282 H368 V252',C['blue'])
    f.path('M530 320 V282 H600 V252',C['blue'])
    f.line(1064,252,1064,318,C['orange'],arrow=True)
    f.box(370,505,525,100,'可执行的工艺调整',['选择能生效的晶圆与层次，计算设备支持的修正'],fill='#ecf8f4',color=C['teal'])
    f.path('M945 443 V555 H898',C['teal'])
    f.path('M370 554 H343 V470 H714 V280 H650 V252',C['teal'])
    f.text(40,550,'数据驱动的反馈',21,C['teal'],weight=650)
    f.text(40,580,'量测返回后，更新后续曝光',18,C['muted'])
    f.text(40,651,'数据还可用于重新校准成像与工艺模型；反馈生效时点见图 6。',18,C['muted'])
    f.save('fig00_process_map.svg')

def metrology():
    f=Fig('同样输出 Overlay，IBO 与 DBO 读取的信号不同','左：从两层图像估计相对位置。右：从叠层光栅的衍射响应反演相对位移。',790)
    f.rect(35,115,550,585)
    f.rect(615,115,550,585)
    f.text(65,155,'IBO：图像位置之差',25,weight=650)
    f.text(645,155,'DBO：设计偏置 + 级次强度差',25,weight=650)
    f.text(65,193,'示意图像：两层标记的投影',19,C['muted'])
    # A schematic box-in-box image, with physical image coordinates rather than an optical ray trace.
    f.rect(144,231,280,220,fill='#eff6ff',stroke=C['blue'],r=0)
    f.rect(161,248,246,186,fill='#f7f9fc',stroke=C['blue'],r=0)
    f.rect(230,282,145,120,fill='#fff3dd',stroke=C['orange'],r=0)
    f.rect(246,298,113,88,fill='#f7f9fc',stroke=C['orange'],r=0)
    f.line(284,214,284,480,C['blue'],dash=True)
    f.line(302.5,264,302.5,480,C['orange'],dash=True)
    f.text(120,487,'下层中心 x_b',18,C['blue'])
    f.text(322,487,'上层中心 x_t',18,C['orange'])
    f.line(284,511,302.5,511,C['ink'],2)
    f.path('M297 506 L302.5 511 L297 516',C['ink'],arrow=False)
    f.text(322,519,'O = x_t − x_b',22,weight=600)
    f.text(65,562,'ML 的位置：找标、分层、选焦点、估计位置',19)
    f.text(65,596,'图像处理引入的误差：δO = δx_t − δx_b',19)
    f.text(65,630,'两层共同移动会抵消；差分移动改变 Overlay。',18,C['muted'])
    f.text(65,670,'颜色表示两层，位移为放大的原理示意。',17,C['muted'])
    # two independent DBO subtargets, each with a top and bottom grating
    for x,delta,label in [(664,17,'+d 子目标：O + d'),(916,-9,'−d 子目标：O − d')]:
        f.text(x+94,203,label,18,anchor='middle')
        for k in range(5):
            f.rect(x+k*34,274,19,29,'#dbeafe',C['blue'],r=0)
            f.rect(x+k*34+delta,229,19,29,'#ffedd5',C['orange'],r=0)
        f.line(x-8,315,x+181,315,C['line'])
    f.text(645,353,'每个子目标测量 A = I₊₁ − I₋₁',21)
    # illustrative detector intensities: all intensities nonnegative
    for x,ip,im,label in [(685,0.62,0.38,'A₊ = +0.24'),(935,0.42,0.58,'A₋ = −0.16')]:
        f.line(x-10,466,x+145,466,C['muted'])
        for j,(val,s) in enumerate([(ip,'I₊₁'),(im,'I₋₁')]):
            xx=x+j*82
            f.rect(xx,466-val*128,48,val*128,'#7dd3c7' if j==0 else '#cbd5e1',stroke='none',r=2)
            f.text(xx+24,490,s,18,anchor='middle')
        f.text(x+65,525,label,21,anchor='middle',weight=600)
    f.text(645,570,'O = d (A₊ + A₋) / (A₊ − A₋)',24,weight=600)
    f.text(645,608,'本例 d = 10 nm，代入得到 O = 2 nm。',19)
    f.text(645,643,'ML 可联合利用像素、波长和结构敏感特征。',18,C['muted'])
    f.text(645,675,'A 的负号表示强度之差；两路光强均为正。',17,C['muted'])
    f.text(40,742,'原理依据：S37；右侧强度为线性模型算例。图中子目标与强度图不按实物比例绘制。',18,C['muted'])
    f.save('fig02_ibo_dbo.svg')

def timeline():
    f=Fig('预测与反馈的关键：数据什么时候真正到达','教学时间表 · 横向按事件顺序排列，间距不代表实际时长。',750)
    xs=[110,300,490,680,870,1060]
    times=['09:00','09:05','09:20','10:00','13:00','14:00']
    for x,t in zip(xs,times):
        f.text(x,140,t,22,anchor='middle',weight=600)
        f.line(x,158,x,575,C['line'],1,dash=True)
    f.line(70,175,1130,175,C['muted'],arrow=True)
    f.text(40,214,'当前晶圆 Wₙ',19,weight=650)
    for x,title,color in [(110,'对准完成',C['blue']),(300,'曝光',C['blue']),(490,'显影完成',C['orange']),(870,'量测返回',C['teal'])]:
        f.rect(x-75,235,150,56,'#f1f5f9')
        f.text(x,270,title,21,color,anchor='middle',weight=600)
    f.line(185,263,224,263,arrow=True)
    f.line(375,263,414,263,arrow=True)
    f.line(565,263,793,263,C['orange'],arrow=True)
    f.text(675,247,'等待加工与量测',17,C['muted'],anchor='middle')
    f.text(40,339,'模型可用的信息',19,weight=650)
    f.box(40,360,340,135,'曝光前预测',['已返回的前层量测与历史数据','当前 Alignment / Leveling','当前可用的设备状态'],fill='#eef4ff',color=C['blue'])
    f.box(416,360,340,135,'显影后虚拟量测',['加入本片曝光和 Track 时序','提前估计本层 CD / Overlay','用于安排复查和后续控制'],fill='#fff7ed',color=C['orange'])
    f.box(792,360,368,135,'实测反馈',['13:00 才收到本层真实量测','更新预测偏差与控制状态','用于此后仍能调整的晶圆'],fill='#ecf8f4',color=C['teal'])
    f.text(40,550,'后续晶圆',19,weight=650)
    f.rect(578,527,206,62,'#fff7ed')
    f.text(681,553,'Wₙ₊₁ 已在 10:00 曝光',17,anchor='middle')
    f.text(681,578,'当时用不到 13:00 的结果',16,C['muted'],anchor='middle')
    f.rect(957,527,206,62,'#ecf8f4')
    f.text(1060,553,'Wₙ₊₂ 在 14:00 曝光',17,anchor='middle')
    f.text(1060,578,'可采用 13:00 返回的反馈',16,C['muted'],anchor='middle')
    f.path('M870 292 V318 H1180 V510 H1060 V525',C['teal'])
    f.rect(40,629,1120,77,'#f7f9fc')
    f.text(65,660,'历史回放的做法：在每次决策时刻截取当时已经到达的数据，再计算预测与修正。',21,weight=600)
    f.text(65,690,'同时保存工艺发生时间和数据到达时间，便能区分本片前馈、结果预报与后续晶圆反馈。',18,C['muted'])
    f.save('fig05_timing.svg')

if __name__=='__main__':
    process();metrology();timeline()
    print('Built 3 diagrams; SVG XML parsed successfully.')
