'use strict';
const {C,Plate,blend,softmax,grid,blockVector}=require('./drawing.cjs');
const assert=require('node:assert/strict');

function bottleneck() {
  const f=new Plate(28,'7.1','一句话怎样穿过固定宽度的瓶颈？',394,
    '原文每多一个词，就多一次状态更新。最后交给解码器的状态仍然只有固定的维数。',
    '从左向右追踪英文词。每读一个词，编码器就更新一次状态。翻译到“机器学习”时，解码器仍须利用早先传过来的定长摘要。');
  f.label(40,105,'编码器逐词读入');
  f.label(648,105,'解码器逐步译出',C.blue);
  const sx=[44,143,242,341],sw=79;
  ['I','love','machine','learning'].forEach((s,i)=>{
    const x=sx[i]; f.box(x,141,sw,37,s,'white',17,{outline:true});
    f.a(x+sw/2,181,x+sw/2,205,C.teal);
    f.box(x,210,sw,42,'h'+(i+1),'teal',20);
    if(i<3) f.a(x+sw+1,231,sx[i+1]-2,231,C.teal);
  });
  f.a(422,231,464,231,C.teal);
  f.rect(466,200,112,62,C.sand,C.rust,1.4,6);
  blockVector(f,476,216,[.4,.8,.2,.95,.45,.72,.33,.6],92,30,C.rust);
  f.mid(522,287,'固定维数 d',18,{color:C.rust,weight:650});
  f.a(580,231,636,231,C.rust,2.5);
  const tx=[641,753,865];
  ['我','喜欢','机器学习'].forEach((s,i)=>{
    const x=tx[i]; f.box(x,141,88,37,s,'white',17,{outline:true});
    f.box(x,210,88,42,'s'+(i+1),'blue',20);
    f.a(x+44,207,x+44,181,C.blue);
    if(i<2) {
      f.a(x+90,231,tx[i+1]-2,231,C.blue);
      f.a(x+74,181,tx[i+1]+12,208,C.blue,1.5,'4 3');
    }
  });
  f.t(44,311,'原文按示例切成 4 个词。',17,{color:C.muted});
  f.t(637,311,'虚线把上一步输出的词送入下一步。',17,{color:C.muted});
  return f;
}

function original() {
  const f=new Plate(1,'7.2','翻译时，解码器怎样找到原文？',546,
    '每个注意力或前馈子层都先把输入加回，再做 LayerNorm。这是原始 Transformer 的 Post-Norm。',
    '右列的因果自注意力只读已经给出的译文。交叉注意力另外接收整句原文的表示，为当前译文位置提取信息。');
  f.label(67,99,'原文 · 编码器',C.teal); f.label(628,99,'译文 · 解码器',C.blue);
  f.t(67,129,'I  love  machine  learning',19);
  f.t(628,129,'〈起始〉 我  喜欢  …',19);
  f.box(67,145,301,35,'词嵌入 ＋ 位置编码','grey',17);
  f.box(628,145,301,35,'右移的译文嵌入 ＋ 位置编码','grey',17);
  [217,778].forEach(x=>f.a(x,181,x,208));
  f.rect(48,211,338,114,'none',C.teal,1.5,8);
  f.rect(609,211,339,164,'none',C.blue,1.5,8);
  f.box(67,222,301,37,'双向自注意力','teal',18);
  f.box(67,276,301,37,'逐位置前馈网络','teal',18);
  f.a(217,260,217,274,C.teal);
  f.box(628,222,301,37,'因果自注意力','blue',18);
  f.box(628,273,301,37,'交叉注意力','rust',18);
  f.box(628,325,301,37,'逐位置前馈网络','blue',18);
  f.a(778,260,778,272,C.blue); f.a(778,311,778,324,C.blue);
  f.t(800,270,'Q',14,{color:C.blue,weight:650});
  f.a(217,326,217,361,C.teal);
  f.box(67,364,301,43,'各原文位置的最终表示','teal',18,{outline:true});
  f.arrow([[369,385],[490,385],[490,292],[626,292]],C.rust,2.8);
  f.t(507,280,'提供 K、V',18,{weight:650,color:C.rust});
  f.mid(217,449,'上述编码器层堆叠 6 次',17,{color:C.muted});
  f.a(778,376,778,398,C.blue);
  f.box(628,401,301,39,'线性层 ＋ softmax','grey',18);
  f.mid(778,464,'解码器堆叠 6 层后，预测下一个词。',17,{color:C.muted});
  return f;
}

function heatmap() {
  const f=new Plate(24,'7.3','读热图时，先选定一个查询位置',418,
    '沿同一行横着读。颜色越深、数值越大，这个位置的 Value 在本次汇总中占的权重越高。',
    '图中权重为教学示例。最后一行是 learning 对各词的读取权重，其中 machine 占 0.60。每行的权重之和都为 1。');
  const words=['I','love','machine','learning'];
  const a=[[.58,.19,.13,.10],[.44,.31,.15,.10],[.05,.05,.55,.35],[.05,.10,.60,.25]];
  f.label(38,100,'查询词 ↓'); f.t(164,100,'被读取的词 →',18,{color:C.muted});
  const x=151,y=147,w=91,h=43;
  words.forEach((s,i)=>f.mid(x+(i+.5)*w,132,s,17));
  a.forEach((row,i)=>{
    assert(Math.abs(row.reduce((u,v)=>u+v)-1)<1e-9);
    f.end(x-14,y+i*h+28,words[i],18,{weight:i===3?700:450,color:i===3?C.teal:C.ink});
    row.forEach((v,j)=>f.cell(x+j*w,y+i*h,w,h,v.toFixed(2),blend('#f5f7f3',C.teal,v/.7),v>.39?C.white:C.ink));
  });
  f.rect(x-2,y+3*h-1,4*w+4,h+2,'none',C.rust,2.4,1);
  f.label(580,119,'learning 这一行',C.rust);
  a[3].forEach((v,i)=>{
    const yy=151+i*39;
    f.t(582,yy+13,words[i],17);
    f.rect(668,yy,199,16,C.grey,'none',0,2);
    f.rect(668,yy,199*v,16,i===2?C.teal:'#80afa4','none',0,2);
    f.end(941,yy+14,(v*100).toFixed(0)+'%',17,{weight:600});
  });
  f.t(151,345,'双向注意力 · 单头教学示例',16,{color:C.muted});
  f.t(582,332,'满格为 100%，四个权重之和为 1。',17,{color:C.muted});
  return f;
}

function qkv() {
  const f=new Plate(2,'7.4','一次注意力读取，究竟汇总了什么？',410,
    'Query 和 Key 决定各位置的权重。沿每一行乘上对应的 Value，再把结果按分量相加。',
    '同一个 Query 与三个 Key 的缩放点积分数为 ln 6、ln 3 和 0。指数化后得到 6∶3∶1，三个 Value 的加权和为 [0.7, 0.7]。');
  const alpha=softmax([Math.log(6),Math.log(3),0]),values=[[1,0],[0,2],[1,1]];
  const total=values[0].map((_,j)=>values.reduce((s,v,i)=>s+v[j]*alpha[i],0));
  const xs=[57,198,407,610,820];
  ['被读位置','缩放点积分数','softmax 权重','Value 向量','加权贡献'].forEach((s,i)=>f.t(xs[i],111,s,19,{weight:650,color:i===2?C.teal:C.ink}));
  f.line(49,124,950,124);
  ['ln 6','ln 3','0'].forEach((s,i)=>{
    const yy=158+i*52;
    f.t(xs[0],yy,'位置 '+(i+1),19);
    f.t(xs[1]+12,yy,s,21);
    f.rect(407,yy-12,94,12,C.grey,'none',0,2);
    f.rect(407,yy-12,94*alpha[i],12,C.teal,'none',0,2);
    f.t(513,yy,alpha[i].toFixed(1),19,{color:C.teal,weight:650});
    f.t(xs[3]+7,yy,'['+values[i].join(',  ')+']',20);
    f.t(xs[4],yy,'['+values[i].map(v=>(v*alpha[i]).toFixed(1)).join(',  ')+']',20);
    f.line(49,yy+14,950,yy+14,C.faint,1);
  });
  f.t(58,318,'同一个 Query 比较三个 Key',19,{color:C.muted});
  f.t(607,318,'输出向量',19,{weight:600});
  f.box(775,287,171,46,'['+total.map(v=>v.toFixed(1)).join(',  ')+']','teal',22);
  return f;
}

function matrices() {
  const f=new Plate(3,'7.5','把三次读取写成一次矩阵乘法',409,
    '权重矩阵的每一行对应一个查询位置。它有几行，输出就有几个位置。Value 的列数决定输出宽度。',
    '例中有 3 个位置，Key 和 Value 的宽度都是 2。先按行对缩放分数做 softmax，再用所得的 3×3 权重矩阵乘 3×2 的 Value。图中小数保留两位。');
  const Q=[[1,0],[0,1],[1,1]],K=[[1,0],[0,1],[1,1]],V=[[1,0],[0,2],[1,1]];
  const KT=K[0].map((_,i)=>K.map(r=>r[i]));
  const A=Q.map(q=>softmax(K.map(k=>q.reduce((s,v,i)=>s+v*k[i],0)/Math.sqrt(2))));
  const O=A.map(a=>V[0].map((_,j)=>V.reduce((s,v,i)=>s+a[i]*v[j],0)));
  const mats=[
    {x:43,a:Q,name:'Q',tone:C.mint,ink:C.teal},{x:179,a:KT,name:'Kᵀ',tone:C.mint,ink:C.teal},
    {x:423,a:A,name:'A',tone:C.sand,ink:C.rust},{x:624,a:V,name:'V',tone:C.sky,ink:C.blue},
    {x:811,a:O,name:'O',tone:C.mint,ink:C.teal}];
  const cw=49,ch=37,cy=205;
  mats.forEach(({x,a,name,tone,ink})=>{
    const w=a[0].length*cw,y=cy-a.length*ch/2;
    f.mid(x+w/2,125,name,27,{weight:650,color:ink});
    a.forEach((row,i)=>row.forEach((v,j)=>{
      const formatted=(name==='A'||name==='O')?v.toFixed(2):String(v);
      f.cell(x+j*cw,y+i*ch,cw,ch,formatted,(name==='A'||name==='O')&&i===1?blend(tone,ink,.26):tone,C.ink,{size:17});
    }));
    f.mid(x+w/2,289,a.length+' × '+a[0].length,17,{color:C.muted});
  });
  f.mid(159,213,'×',26); f.a(336,205,405,205,C.rust,2.5);
  f.mid(366,175,'缩放',16,{color:C.rust}); f.mid(366,238,'softmax',16,{color:C.rust});
  f.mid(595,213,'×',26); f.mid(762,213,'=',26);
  f.t(43,330,'例中所有位置都可见，分数矩阵为 QKᵀ / √2。',17,{color:C.muted});
  return f;
}

function causal() {
  const f=new Plate(29,'7.6','第 3 个位置能看到第 4 个词吗？',449,
    '掩码在 softmax 之前加进分数。未来位置的权重变成 0，训练时仍可把各行放在一起计算。',
    '左图每行列出一个查询位置的加法掩码。右图展开第 3 行，即便第 4 个位置原本分数最高，它也无法影响预测下一个词的表示。');
  f.label(42,105,'因果掩码 M'); f.label(489,105,'沿第 3 行做一次 softmax',C.rust);
  const x=133,y=155,s=48;
  for(let i=0;i<4;i++) {
    f.mid(x+(i+.5)*s,142,''+(i+1),18); f.end(118,y+i*s+31,'t = '+(i+1),17,{color:i===2?C.rust:C.muted});
  }
  grid(f,x,y,4,4,s,(i,j)=>({fill:j<=i?C.mint:C.grey,s:j<=i?'0':'−∞',ink:j<=i?C.teal:C.muted,font:18}));
  f.rect(x-2,y+2*s-1,s*4+4,s+2,'none',C.rust,2.5,1);
  f.mid(x+2*s,377,'列号表示被读取的位置',17,{color:C.muted});
  f.a(337,275,447,275,C.rust,2);
  const scores=[0,Math.log(2),Math.log(3),5],masked=scores.map((v,i)=>i===3?-Infinity:v),weights=softmax(masked);
  assert.equal(weights[3],0);
  const rows=[['原分数',['0','ln 2','ln 3','5']],['加掩码后',['0','ln 2','ln 3','−∞']],['权重',['1/6','2/6','3/6','0']]];
  rows.forEach(([label,items],i)=>{
    const yy=161+i*57;f.t(489,yy+24,label,17,{weight:600});
    items.forEach((v,j)=>f.cell(596+j*78,yy,74,37,v,j===3?C.sand:i===2?C.mint:C.grey,j===3?C.rust:C.ink));
  });
  f.t(489,367,'位置 3 的输出用于预测位置 4 的 token。',17,{color:C.muted});
  return f;
}

function heads() {
  const f=new Plate(4,'7.7','两个头可以从同一句话读出不同的信息',418,
    '每个头有自己的 Q、K、V 投影。先沿位置汇总各自的 Value，再沿特征维拼接，最后做输出投影。',
    '例中仅展开一个查询位置。两个头分配不同的示意权重，各自得到一个二维向量。拼接得到四个分量，输出投影再混合这四个分量。');
  f.t(39,110,'同一输入',18,{weight:650}); f.t(210,110,'各头独立投影',18,{weight:650});
  f.t(420,110,'三个位置的权重',18,{weight:650});
  f.t(641,110,'读取结果',18,{weight:650}); f.t(829,110,'拼接并投影',18,{weight:650});
  f.box(42,191,105,52,'输入 X','grey',20);
  f.wire([[148,217],[172,217],[172,166]],C.muted); f.arrow([[172,217],[172,265],[202,265]]);
  f.a(172,166,202,166);
  const rows=[[.6,.3,.1],[.1,.2,.7]],vals=[[[1,0],[0,2],[1,1]],[[0,1],[1,0],[2,1]]];
  rows.forEach((a,i)=>{
    const y=144+i*99,tone=i?'blue':'teal',ink=i?C.blue:C.teal;
    f.box(206,y,160,43,'头 '+(i+1)+' 的 Q / K / V',tone,16);
    f.a(368,y+21,411,y+21,ink);
    a.forEach((p,j)=>f.cell(416+j*51,y,49,43,p.toFixed(1),blend('#f6f8f6',ink,p*.9),p>.49?C.white:C.ink,{size:17}));
    f.a(572,y+21,627,y+21,ink);
    const v=[0,1].map(k=>a.reduce((sum,p,j)=>sum+p*vals[i][j][k],0));
    f.box(631,y,120,43,'['+v.map(n=>n.toFixed(1)).join(', ')+']',tone,18);
    f.arrow([[753,y+21],[781,y+21],[781,202+i*30],[812,202+i*30]],ink);
  });
  [0.7,0.7,1.6,0.8].forEach((v,i)=>f.cell(816+i*36,193,36,47,v.toFixed(1),i<2?C.mint:C.sky,i<2?C.teal:C.blue,{size:15}));
  f.a(881,248,881,271);f.box(817,274,130,39,'乘 Wₒ','grey',18);
  f.t(42,333,'示例宽度 d = 4，头数 h = 2，每个头输出 2 个分量。',17,{color:C.muted});
  return f;
}

function position() {
  const f=new Plate(5,'7.8','把位置加进向量，或把位置转成角度',461,
    '绝对位置编码改变输入向量。RoPE 在 Q 和 K 的成对维度上做旋转，让点积感知两个位置之差。',
    '左图取正弦位置编码的第一对分量。右图让两个原始单位向量同向，每前进一格多转 20°。两个位置一同平移，夹角仍为 40°。');
  f.line(504,88,504,381,C.rule,1.2);
  f.label(40,107,'加法位置编码'); f.label(529,107,'旋转位置编码 RoPE',C.blue);
  f.t(40,142,'同一个词的内容向量取 [0.20, 0.70]。',17,{color:C.muted});
  f.t(529,142,'令原始 Q、K 都朝右，每个位置转 20°。',17,{color:C.muted});
  ['位置','位置向量 p','相加后的输入'].forEach((v,i)=>f.t([46,137,310][i],193,v,17,{weight:600}));
  [0,2].forEach((pos,i)=>{
    const v=[Math.sin(pos),Math.cos(pos)],sum=[.2+v[0],.7+v[1]],y=211+i*53;
    f.t(48,y+26,'t = '+pos,18,{weight:600}); f.t(134,y+26,'['+v.map(n=>n.toFixed(2)).join(', ')+']',18);
    f.box(305,y,164,39,'['+sum.map(n=>n.toFixed(2)).join(', ')+']','teal',17);
  });
  f.t(43,359,'第一对维度取 [sin(t), cos(t)]。',17,{color:C.muted});
  const R=61,cy=244;
  [[638,1,3],[847,3,5]].forEach(([cx,t,s])=>{
    f.circle(cx,cy,R,'none',C.rule,1.2);f.line(cx-R-5,cy,cx+R+5,cy,C.faint,1.4);
    f.line(cx,cy+R+3,cx,cy-R-3,C.faint,1.4);
    const xy=(a,r)=>[cx+r*Math.cos(a*Math.PI/180),cy-r*Math.sin(a*Math.PI/180)];
    const midR=27,pa=xy(t*20,midR),pb=xy(s*20,midR);
    f.path('M'+pa.join(' ')+' A'+midR+' '+midR+' 0 0 0 '+pb.join(' '),C.rust,2.5);
    f.arrow([[cx,cy],xy(t*20,R-2)],C.teal,3);f.arrow([[cx,cy],xy(s*20,R-2)],C.blue,3);
    f.circle(cx,cy,3,C.ink);
    f.mid(cx,332,'Q 在 '+t+'，K 在 '+s,17,{weight:600});
    f.mid(cx,359,'夹角 40°',17,{color:C.rust});
  });
  f.line(623,385,644,385,C.teal,3);f.t(652,391,'Q',16,{color:C.teal});
  f.line(760,385,781,385,C.blue,3);f.t(789,391,'K',16,{color:C.blue});
  return f;
}

function block() {
  const f=new Plate(6,'7.9','一个 Transformer Block 怎样更新表示？',401,
    '两条上方支路都传递原表示。下方计算给出更新量，两者在加号处汇合。每次相加前后的形状相同。',
    '沿绿色支路读取多头注意力的输入与输出，再沿蓝色支路读 FFN。这里画的是 Pre-Norm，归一化分别位于两个子层之前。');
  f.label(41,107,'Pre-Norm · 从左向右读');
  const y=226;
  f.mid(250,148,'保留输入 H',17,{color:C.teal});f.mid(658,148,'保留中间表示 U',17,{color:C.blue});
  f.arrow([[83,y],[83,161],[408,161],[408,y-19]],C.teal,2.3);
  f.arrow([[509,y],[509,161],[821,161],[821,y-19]],C.blue,2.3);
  f.t(37,y+7,'H',24,{weight:650});f.a(60,y,113,y);
  f.box(116,205,85,42,'Norm','grey',18); f.a(204,y,226,y);
  f.box(229,205,129,42,'多头注意力','teal',18);f.a(361,y,388,y,C.teal);
  f.circle(408,y,17,C.white,C.teal,2);f.mid(408,y+6,'+',24,{color:C.teal});
  f.a(426,y,465,y); f.mid(479,y+7,'U',21,{weight:650});f.a(495,y,529,y);
  f.box(532,205,85,42,'Norm','grey',18);f.a(620,y,644,y);
  f.box(647,205,124,42,'逐位置 FFN','blue',17);f.a(774,y,801,y,C.blue);
  f.circle(821,y,17,C.white,C.blue,2);f.mid(821,y+6,'+',24,{color:C.blue});
  f.a(840,y,873,y);f.t(882,y+6,'下一层 H',18,{weight:650});
  f.mid(249,292,'不同位置之间交换信息',18,{color:C.teal});
  f.mid(669,292,'各位置分别变换特征',18,{color:C.blue});
  f.mid(480,329,'输入、中间表示和输出都是 T × d。',17,{color:C.muted});
  return f;
}

function architectures() {
  const f=new Plate(7,'7.10','三类架构，分别允许谁读取谁？',458,
    '每一行是读取者，每一列是信息来源。编码器—解码器一栏合并展示两套堆栈各子层的可见范围。',
    'S 表示原文，T 表示译文。编码器可双向读原文，解码器可读已有译文，还可通过交叉注意力读原文。单独的生成式解码器只读同一序列的前缀。');
  const groups=[
    {x:41,title:'仅编码器',sub:'Encoder-only',tokens:['1','2','3','4'],case:'取整段表示，用于分类 / 检索'},
    {x:367,title:'编码器—解码器',sub:'Encoder–decoder',tokens:['S1','S2','T1','T2'],case:'读取原文，逐步译出目标句'},
    {x:695,title:'仅解码器',sub:'Decoder-only',tokens:['1','2','3','4'],case:'读已有前缀，续写下一个词'}];
  groups.forEach(({x,title,sub,tokens,case:usage},g)=>{
    const cx=x+132,gx=x+69,gy=190,s=33;
    f.mid(cx,108,title,22,{weight:650});f.mid(cx,135,sub,16,{color:C.muted});
    tokens.forEach((v,i)=>{f.mid(gx+(i+.5)*s,179,v,15);f.end(gx-9,gy+i*s+22,v,15);});
    grid(f,gx,gy,4,4,s,(i,j)=>{
      const cross=g===1&&i>=2&&j<2;
      const allowed=g===0||(g===2?j<=i:((i<2&&j<2)||(i>=2&&j<=i)));
      return {fill:cross?C.sand:allowed?C.mint:C.grey,s:allowed?'●':'×',ink:cross?C.rust:allowed?C.teal:'#879498',font:15};
    });
    f.mid(cx,354,usage,17,{color:C.muted});
  });
  f.line(338,88,338,365,C.faint);f.line(661,88,661,365,C.faint);
  f.mid(500,389,'绿色 ● 自注意力可见       橙色 ● 交叉注意力可见       灰色 × 不可见',16,{color:C.muted});
  return f;
}

function autoregression() {
  const f=new Plate(8,'7.11','每一步只选一个新 token',442,
    '当步选出的 token 会进入下一步的前缀。选到结束标记 EOS，或达到长度上限时，生成停止。',
    '按词切分的示例，依次选出“我”“喜欢”“学习”和 EOS。蓝框是已有内容，橙框是本步新选中的 token。');
  f.label(45,106,'生成步'); f.label(179,106,'已经给定的前缀',C.blue);
  f.t(680,106,'橙框标出本步的选择',17,{color:C.rust,weight:600});
  const sentence=['BOS','我','喜欢','学习','EOS'],start=182,dx=116;
  for(let i=0;i<4;i++){
    const y=135+54*i;
    f.t(49,y+25,'第 '+(i+1)+' 步',18);
    for(let j=0;j<=i;j++) f.box(start+j*dx,y,97,37,sentence[j],'blue',18);
    const last=start+i*dx,next=last+dx+32;
    f.a(last+100,y+18,next-4,y+18,C.rust);
    f.box(next,y,97,37,sentence[i+1],'rust',18,{outline:true});
    if(i===3) f.t(next+109,y+25,'停止',17,{color:C.rust,weight:600});
  }
  f.t(47,364,'BOS 表示开始，EOS 表示结束。示例采用按词切分的词表。',17,{color:C.muted});
  return f;
}

function kv() {
  const f=new Plate(9,'7.12','KV cache 在哪一步省下了计算？',455,
    '预填充并行处理提示。逐步解码时，只为新位置计算 Q、K、V，并用新 Q 读取本层截至当前位置的全部 K、V。',
    '沿一列向下看，同一位置的 K、V 在后续步中被复用。最后一列选出的词要到下一次送入模型时，才会在本层拥有自己的缓存条目。');
  const tok=['我','喜欢','机器','学习','。','EOS'];
  f.t(42,110,'本层的一次前向计算',18,{weight:650});
  f.t(307,110,'缓存中的位置',18,{weight:650});f.t(832,110,'选出的下个词',18,{weight:650});
  const x=294,dx=101;
  for(let j=0;j<5;j++)f.mid(x+j*dx+45,146,tok[j],18);
  [3,4,5].forEach((n,row)=>{
    const yy=164+row*69;
    f.t(41,yy+19,['预填充','解码第 1 步','解码第 2 步'][row],20,{weight:600});
    f.t(41,yy+44,['一次读入三个提示词','新输入为“学习”','新输入为“。”'][row],16,{color:C.muted});
    for(let j=0;j<n;j++){
      const fresh=row===0||j===n-1;
      f.box(x+dx*j,yy,90,46,'K'+(j+1)+'  V'+(j+1),fresh?'rust':'teal',17,{outline:fresh});
    }
    f.a(x+dx*(n-1)+94,yy+23,826,yy+23);
    f.box(832,yy,99,46,tok[n],'blue',18);
  });
  f.rect(294,373,15,15,C.sand,C.rust); f.t(318,386,'本步新算并写入',16,{color:C.rust});
  f.rect(531,373,15,15,C.mint,C.teal);f.t(555,386,'从历史缓存读取',16,{color:C.teal});
  return f;
}

function batching() {
  const f=new Plate(25,'7.13','增加批大小，吞吐量和延迟怎样变化？',466,
    '在这个固定长度的教学算例中，B = 8 时每秒生成 800 个 token，一条请求的 P95 延迟为 134 ms。',
    '示意服务每批有 B 条请求，每条生成 12 个 token。每步耗时取 6 + 0.5B 毫秒，P95 排队时间取 2(B−1) 毫秒，忽略预填充。两幅图都由这些假设计算。');
  const bs=[1,2,4,8,16,32],step=b=>6+.5*b;
  const series=[{x:89,max:1600,ticks:[0,400,800,1200,1600],v:b=>1000*b/step(b),label:'总吞吐量（token/s）',paint:C.teal,selected:'800'},
    {x:582,max:400,ticks:[0,100,200,300,400],v:b=>2*(b-1)+12*step(b),label:'单请求 P95 延迟（ms）',paint:C.rust,selected:'134'}];
  series.forEach(({x,max,ticks,v,label,paint,selected})=>{
    f.t(x-39,105,label,20,{color:paint,weight:650});
    const top=143,bottom=299,w=333,xx=i=>x+i*w/5,yy=n=>bottom-(bottom-top)*n/max;
    ticks.forEach(n=>{f.line(x,yy(n),x+w,yy(n),C.faint,1);f.end(x-10,yy(n)+5,String(n),14,{color:C.muted});});
    f.line(x,top,x,bottom);f.line(x,bottom,x+w,bottom);
    const points=bs.map((b,i)=>[xx(i),yy(v(b))]);f.wire(points,paint,3);
    points.forEach(([a,b],i)=>{f.circle(a,b,i===3?5.2:3.5,C.white,paint,2.1);f.mid(a,bottom+22,String(bs[i]),15);});
    const [px,py]=points[3];f.mid(px,py-13,selected,17,{color:paint,weight:650});
    f.mid(x+w/2,348,'批大小 B（每格翻倍）',16,{color:C.muted});
  });
  f.t(47,388,'假设每步耗时 6 + 0.5B 毫秒，每条请求生成 12 个 token，P95 排队时间为 2(B − 1) 毫秒。',16,{color:C.muted});
  return f;
}

module.exports=[bottleneck,original,heatmap,qkv,matrices,causal,heads,position,block,architectures,autoregression,kv,batching];
