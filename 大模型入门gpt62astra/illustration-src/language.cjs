'use strict';
const assert=require('node:assert/strict');
const {C,Plate,blend,softmax}=require('./drawing.cjs');

function chips(f,x,y,symbols,focus){
  let pos=x;
  symbols.forEach(s=>{
    const w=Math.max(27,s.length*10+15);
    f.box(pos,y,w,35,s,s===focus?'teal':'grey',17,{radius:4});pos+=w+4;
  });
}
function bpe(){
  const f=new Plate(17,'9.1','BPE 怎样从字母中学到一个子词？',425,
    '每一轮都按词频重新统计相邻符号对。在这个小语料里，先学得 lo，再把 lo 和 w 合并成 low。',
    'low 出现 4 次、lower 出现 2 次、lot 出现 1 次。首轮 l 和 o 相邻 7 次，下一轮 lo 和 w 相邻 6 次。绿色框标出本轮刚形成的 token。');
  const entries=[['low',4],['lower',2],['lot',1]].map(([word,count])=>({word,count,sym:[...word]}));
  const rounds=[entries.map(r=>r.sym.slice())],merges=[];
  for(let n=0;n<2;n++){
    const pairs=new Map();
    for(const {sym,count} of entries) for(let i=1;i<sym.length;i++){
      const pair=sym[i-1]+' '+sym[i];pairs.set(pair,(pairs.get(pair)||0)+count);
    }
    const [pair,count]=[...pairs].sort((a,b)=>b[1]-a[1])[0],joined=pair.replace(' ','');
    for(const row of entries){
      const out=[];
      for(let i=0;i<row.sym.length;i++){
        if(i+1<row.sym.length&&row.sym[i]+' '+row.sym[i+1]===pair){out.push(joined);i++;}
        else out.push(row.sym[i]);
      }
      row.sym=out;
    }
    merges.push([pair,count,joined]);rounds.push(entries.map(r=>r.sym.slice()));
  }
  assert.deepEqual(merges,[['l o',7,'lo'],['lo w',6,'low']]);
  const xs=[191,475,761];
  f.t(46,110,'语料与词频',18,{weight:650});f.t(xs[0],110,'初始符号',18,{weight:650});
  f.t(xs[1],110,'第 1 轮合并',18,{color:C.teal,weight:650});f.t(xs[2],110,'第 2 轮合并',18,{color:C.teal,weight:650});
  f.line(45,126,951,126);
  entries.forEach(({word,count},i)=>{
    const y=148+i*56;
    f.t(47,y+24,word+'  ×  '+count,18,{weight:600});
    rounds.forEach((stage,n)=>chips(f,xs[n],y,stage[i],n?merges[n-1][2]:''));
  });
  f.t(48,337,'统计时计入词频',17,{color:C.muted});
  f.t(473,337,'l + o 共出现 7 次',17,{color:C.teal});
  f.t(759,337,'lo + w 共出现 6 次',17,{color:C.teal});
  return f;
}

function embeddings(){
  const f=new Plate(18,'9.2','token 的编号怎样变成输入向量？',438,
    'token ID 是查表用的行号。按原序取出对应向量并堆成矩阵，两个 token 就得到两行表示。',
    '示例词表把“温度上升”切成两个 token，编号依次为 2 和 0。按这个顺序读取嵌入表的第 2 行和第 0 行，得到右侧的 2×3 矩阵。行号从 0 开始。');
  const E=[[.1,.8,-.2],[.3,-.7,.2],[.6,.1,.4]],words=['上升','下降','温度'],ids=[2,0];
  f.label(43,105,'文字 → token → ID');
  f.t(48,165,'温度上升',29,{weight:650});
  f.box(46,199,77,38,'温度','teal',18);f.box(132,199,77,38,'上升','blue',18);
  [84,170].forEach((x,i)=>{f.a(x,241,x,263,i?C.blue:C.teal);f.box(x-25,267,50,35,String(ids[i]),i?'blue':'teal',18);});
  f.t(45,352,'本图采用一个示例词表。',16,{color:C.muted});
  f.line(250,92,250,367,C.faint);
  f.label(277,105,'嵌入表 E');
  ['ID','token','维 1','维 2','维 3'].forEach((s,i)=>f.mid([301,365,447,505,563][i],153,s,16,{color:C.muted,weight:600}));
  E.forEach((row,i)=>{
    const y=170+i*52,col=i===2?C.teal:i===0?C.blue:C.muted,fill=i===2?C.mint:i===0?C.sky:C.grey;
    f.rect(277,y,314,40,fill,'none',0,3);f.mid(301,y+26,String(i),17,{color:col,weight:650});f.mid(365,y+26,words[i],17);
    row.forEach((v,j)=>f.mid(447+58*j,y+26,v.toFixed(1).replace('-','−'),17));
  });
  f.line(615,92,615,367,C.faint);f.label(645,105,'按 ID 顺序排列的输入 X');
  ids.forEach((id,i)=>{
    const y=174+i*72,fill=i?C.sky:C.mint,ink=i?C.blue:C.teal;
    f.t(648,y+29,'E['+id+']',18,{color:ink,weight:650});
    E[id].forEach((v,j)=>f.cell(718+j*70,y,68,43,v.toFixed(1).replace('-','−'),fill,C.ink,{size:19}));
  });
  f.t(644,352,'序列长度 T = 2，向量维数 d = 3。',16,{color:C.muted});
  return f;
}

function temperature(){
  const f=new Plate(19,'9.3','温度改变的是概率分布的形状',416,
    '三个面板使用同一组 logits。温度调低后，最可能的词更加突出。调高后，其余候选被抽到的机会增加。',
    '假设在温度 1 时，“上升、下降、波动”的概率分别为 0.7、0.2、0.1。每一列都用同一组 logits 除以该列温度，再做 softmax。三个图共用 0–100% 的刻度。');
  const logits=[.7,.2,.1].map(Math.log),words=['上升','下降','波动'],colors=[C.teal,'#558497','#8999a2'];
  f.t(44,104,'上下文为“温度正在…”，假设只有以下三个候选词。',17,{color:C.muted});
  [.5,1,2].forEach((tau,g)=>{
    const left=42+g*319,x=left+61,w=176,probs=softmax(logits,tau);
    f.t(left,150,'τ = '+tau,22,{weight:650,color:C.teal});
    f.t(left+85,150,['低温','基准','高温'][g],18,{color:C.muted});
    probs.forEach((p,i)=>{
      const y=175+i*46;f.t(left,y+17,words[i],17);
      f.rect(x,y,w,19,C.grey,'none',0,2);f.rect(x,y,w*p,19,colors[i],'none',0,2);
      f.end(left+299,y+17,(100*p).toFixed(1)+'%',17,{weight:600});
    });
    f.line(x,309,x+w,309);[0,.5,1].forEach(v=>{f.line(x+w*v,306,x+w*v,313);f.mid(x+w*v,333,(v*100)+'%',14,{color:C.muted});});
  });
  return f;
}

function truncation(){
  const f=new Plate(31,'9.4','top-k 数个数，top-p 累加概率',471,
    'top-p 按概率从高到低累加，保留首次达到阈值的最短前缀。两种截断都要把保留的概率重新归一化。',
    '分别使用 top-k（k = 2）和 top-p（p = 0.80）。集中分布的 A 已占 82%，单独就达到 top-p 阈值。平缓分布前三项只有 71%，加上 D 才达到 87%。top-k 在两种情况下都保留两个词。');
  const rows=[{title:'集中分布',p:[.82,.08,.05,.03,.02]},{title:'平缓分布',p:[.27,.24,.20,.16,.13]}],names=['A','B','C','D','E'];
  f.t(40,108,'候选词',18,{weight:650});f.t(170,108,'按概率降序排列',18,{weight:650});
  f.t(558,108,'top-k · k = 2',19,{color:C.blue,weight:650});
  f.t(755,108,'top-p · p = 0.80',19,{color:C.rust,weight:650});
  rows.forEach(({title,p},i)=>{
    const yy=143+i*123;f.t(40,yy+42,title,19,{weight:600});
    p.forEach((v,j)=>{
      const x=168+j*67;
      f.mid(x+29,yy+13,names[j],16,{color:C.muted});
      f.cell(x,yy+22,59,35,v.toFixed(2),blend(C.grey,C.teal,v*.67),v>.6?C.white:C.ink,{size:16});
    });
    let count=0,mass=0;while(mass<.8-1e-10){mass+=p[count++];}
    f.box(556,yy+21,131,39,'A、B','blue',17);
    f.t(556,yy+86,'保留 2 项',16,{color:C.blue});
    f.box(751,yy+21,195,39,names.slice(0,count).join('、'),'rust',17);
    f.t(751,yy+86,'累计 '+Math.round(mass*100)+'%，保留 '+count+' 项',16,{color:C.rust});
    if(!i)f.line(40,yy+102,950,yy+102,C.faint);
  });
  f.t(44,391,'平缓分布采用 top-p 后，A 的采样概率为 0.27 / 0.87 ≈ 31%。',17,{color:C.muted});
  return f;
}

function training(){
  const f=new Plate(20,'10.1','从训练到使用，同一道题扮演什么角色？',465,
    '预训练、指令微调和反馈训练把信息写进参数。使用时，当前问题进入上下文，模型凭已有参数生成答案。',
    '沿“3×4”这个例子看不同信号。语料提供下一个 token，示范提供目标回答，偏好比较或可验证规则提供后训练反馈。后训练方法可按任务组合。');
  f.label(43,105,'训练 · 更新参数');f.label(791,105,'使用 · 固定参数',C.blue);
  f.line(763,91,763,374,C.rule,1.5,'5 6');
  const xs=[43,266,509,788];
  ['预训练','指令微调','偏好或可验证反馈','推理'].forEach((s,i)=>f.t(xs[i],156,s,20,{weight:650,color:i===3?C.blue:C.teal}));
  f.box(43,177,168,47,'前缀  3 × 4 =','grey',19);f.t(46,255,'语料的下一项为 12',17);
  f.box(266,177,188,47,'问  3 × 4 等于几？','grey',17);f.box(266,233,188,42,'示范  等于 12','teal',16);
  f.box(509,177,210,43,'偏好对 · 哪个回答更清晰','teal',16);
  f.box(509,230,210,43,'规则 · 数值是否等于 12','rust',16);
  f.box(788,177,167,45,'新问题  5 × 4？','blue',17);
  f.box(788,237,167,39,'生成回答  20','blue',17);
  f.a(214,200,259,200);f.a(457,200,501,200);f.a(722,200,757,200);
  f.a(871,224,871,235,C.blue);
  const notes=[['真实后续','学习续写规律'],['示范答案','学习按指令回答'],['比较或测试结果','改变回答的倾向'],['当前上下文','决定本次任务']];
  notes.forEach(([a,b],i)=>{f.t(xs[i],323,a,18,{weight:650});f.t(xs[i],353,b,17,{color:C.muted});});
  return f;
}
module.exports=[bpe,embeddings,temperature,truncation,training];
