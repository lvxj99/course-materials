'use strict';
const {C,Plate,blend,blockVector}=require('./drawing.cjs');

function scaling(){
  const f=new Plate(21,'11.1','多给一份计算预算，可以花在哪里？',470,
    '增加训练预算会影响随后得到的模型。增加单题推理预算，可以让同一模型多走几步、尝试多个候选并验证。',
    '左、中两栏改变训练时模型得到的数据或反馈。右栏展示推理深度与宽度，同一道题既可以沿一条路径继续检查，也可以并行比较多条路径。');
  const xs=[44,363,682];
  ['预训练','后训练','推理时'].forEach((s,i)=>f.t(xs[i],111,s,23,{weight:650,color:i===2?C.blue:C.teal}));
  f.line(333,88,333,381,C.faint);f.line(651,88,651,381,C.faint);
  f.t(45,148,'更多语料与模型容量',17,{color:C.muted});
  f.t(363,148,'更多示范、候选和反馈',17,{color:C.muted});
  f.t(682,148,'为当前问题多算几步',17,{color:C.muted});
  for(let i=0;i<4;i++){
    f.rect(48+i*4,181+i*12,96,44,C.white,C.teal,1.3,2);
    for(let j=0;j<2;j++) f.line(59+i*4,194+i*12+j*8,122+i*4-(j*9),194+i*12+j*8,'#a2b9b2',1.5);
  }
  f.a(164,218,203,218,C.teal);for(let i=0;i<4;i++) for(let j=0;j<4;j++)f.rect(210+j*17,184+i*17,15,15,blend(C.mint,C.teal,((i*3+j*5)%11+2)/14));
  f.mid(107,280,'训练文本',16,{color:C.muted});f.mid(243,280,'模型参数',16,{color:C.muted});
  f.box(366,187,92,38,'回答 A','teal',17);f.box(366,243,92,38,'回答 B','grey',17);
  f.arrow([[460,206],[477,206],[477,221],[495,221]],C.teal);
  f.arrow([[460,262],[477,262],[477,241],[495,241]],C.muted);
  f.box(498,210,127,43,'比较 / 验证','rust',17);f.a(561,254,561,274,C.rust);f.mid(561,299,'更新参数',16,{color:C.rust});
  const root=[694,230],check=[935,230];
  const branches=[[[745,189],[816,181],[869,183]],[[745,230],[816,230],[869,230]],[[745,271],[816,280],[869,277]]];
  branches.forEach((vertices,i)=>{
    const col=i===1?C.blue:'#a9beca';f.wire([root,...vertices],col,2);f.arrow([vertices[2],check],col,1.6);
    vertices.forEach(([x,y])=>f.circle(x,y,4.8,C.white,col,1.8));
  });
  f.circle(...root,6,C.blue);f.circle(...check,6,C.rust);
  f.t(683,311,'增加候选宽度，或延长推导深度',16,{color:C.muted});
  f.t(45,368,'学习基础表示与预测规律',18,{weight:600});
  f.t(363,368,'学习任务行为与回答偏好',18,{weight:600});
  f.t(682,368,'比较后选择本题的答案',18,{weight:600});
  return f;
}

function multimodal(){
  const f=new Plate(22,'11.2','怎样让模型同时读懂一句话和一张曲线图？',484,
    '不同输入先各自编码，再接到语言模型能处理的表示空间。本例把问题和曲线图的表示放进同一序列。',
    '实线追踪一次图文问答。文字提供问题，图中 B 曲线后段上升更快。下方另画出音频和视频的可选输入路径，具体模型只接入它支持的模态。');
  f.t(43,107,'输入',19,{weight:650});f.t(232,107,'各模态的编码方式',19,{weight:650});
  f.t(492,107,'接入语言模型',19,{weight:650});
  f.t(782,107,'本次图文问答',19,{weight:650,color:C.teal});
  const ys=[145,208,271,334];
  const labels=['文本嵌入','视觉编码器','音频编码器','时空编码器'];
  ys.forEach((y,i)=>{
    const tone=i<2?(i?'teal':'blue'):'grey',ink=i<2?(i?C.teal:C.blue):C.muted;
    f.a(191,y+18,223,y+18,ink,1.6,i<2?'':'4 3'); f.box(227,y,153,37,labels[i],tone,17);
    f.a(384,y+18,447,y+18,ink,1.6,i<2?'':'4 3');
    if(i===0)f.box(451,y,173,37,'文字向量',tone,17);
    else f.box(451,y,173,37,'投影为特征向量',tone,16);
  });
  f.t(44,171,'哪条线后段升得快？',16,{weight:600});
  const cx=79,cy=245;
  f.line(cx,cy,cx+97,cy,C.rule);f.line(cx,cy,cx,cy-35,C.rule);
  f.wire([[cx,cy-4],[cx+30,cy-14],[cx+59,cy-22],[cx+85,cy-24]],C.blue,2);
  f.wire([[cx,cy-4],[cx+30,cy-7],[cx+59,cy-11],[cx+85,cy-33]],C.teal,2.4);
  f.t(44,232,'图像',15,{color:C.muted});f.t(170,cy-15,'A',13,{color:C.blue});f.t(170,cy-36,'B',13,{color:C.teal});
  f.t(44,296,'音频',15,{color:C.muted});
  for(let i=0;i<34;i++){
    const x=83+i*2.7,h=2+12*Math.abs(Math.sin(i*.47))*Math.sin(Math.PI*i/33)**.6;f.line(x,290-h,x,290+h,'#8599a1',1.7);
  }
  f.t(44,359,'视频',15,{color:C.muted});
  for(let i=0;i<3;i++){const x=83+i*32;f.rect(x,342,27,21,C.grey,C.rule,1,2);f.circle(x+6+i*6,353-i*2,3.4,'#7a909a');}
  f.arrow([[627,163],[665,163],[665,189],[720,189]],C.blue,2);
  f.arrow([[627,226],[665,226],[665,207],[720,207]],C.teal,2);
  f.rect(724,167,228,68,'none',C.rule,1.5,5);
  blockVector(f,743,184,[.45,.7,.3],62,32,C.blue);
  blockVector(f,811,184,[.72,.35,.6,.85,.45,.62],123,32,C.teal);
  f.mid(838,261,'问题 token ＋ 图像特征',16,{color:C.muted});
  f.a(838,268,838,286,C.teal);
  f.box(747,289,182,40,'语言模型','teal',19);
  f.a(838,330,838,346,C.teal);f.mid(837,373,'“B 线后段升得更快。”',17,{weight:600});
  f.t(228,407,'虚线为音频或视频的可选输入路径。',16,{color:C.muted});
  return f;
}

function experts(){
  const f=new Plate(23,'11.3','一个 token 在 MoE 层到底调用了谁？',457,
    '本例只执行 E1 和 E3。按选中专家的归一化权重混合输出，再把这个 token 的新向量传给下一层。',
    '路由器给四个专家打分，Top-2 选出 0.56 和 0.24。重新归一化得到 0.70 和 0.30，因此 [2,0] 与 [0,2] 的加权结果为 [1.4,0.6]。');
  const score=[.56,.12,.24,.08],top=[...score.keys()].sort((a,b)=>score[b]-score[a]).slice(0,2),mass=top.reduce((a,i)=>a+score[i],0);
  const expertValues=[[2,0],null,[0,2],null];
  f.t(43,109,'当前 token',19,{weight:650});f.t(235,109,'路由器分数',19,{weight:650});
  f.t(522,109,'本步的专家网络',19,{weight:650});f.t(804,109,'加权汇总',19,{weight:650});
  f.box(42,218,106,47,'向量 h','blue',19);f.a(152,241,203,241,C.blue);
  f.line(208,159,208,324,C.rule);
  score.forEach((p,i)=>{
    const yy=143+i*55,active=top.includes(i),ink=active?C.teal:C.muted;
    f.line(208,yy+17,226,yy+17,C.rule);
    f.t(235,yy+23,'E'+(i+1),18,{color:ink,weight:600});
    f.rect(286,yy+9,95,15,C.grey,'none',0,2);f.rect(286,yy+9,95*p,15,active?C.teal:'#adbaba','none',0,2);
    f.t(394,yy+23,p.toFixed(2),18,{color:ink});
    if(active) f.a(447,yy+16,511,yy+16,C.teal,2.2);
    f.box(516,yy-3,149,39,'专家 E'+(i+1)+(active?' · 执行':' · 跳过'),active?'teal':'grey',17);
    if(active){
      f.t(682,yy+22,expertValues[i].join(', '),16,{color:C.teal});
      f.arrow([[723,yy+16],[754,yy+16],[754,216+i*14],[802,216+i*14]],C.teal,2);
    }
  });
  const weights=top.map(i=>score[i]/mass),out=[0,1].map(k=>top.reduce((s,i,j)=>s+weights[j]*expertValues[i][k],0));
  f.box(807,196,145,62,'['+out.map(v=>v.toFixed(1)).join(', ')+']','rust',21,{outline:true});
  f.t(806,287,'0.70 E1 + 0.30 E3',16,{color:C.rust});
  f.t(44,379,'所有专家的参数都保存在模型中，路由选择按 token 进行。',17,{color:C.muted});
  return f;
}

function contextWindow(){
  const f=new Plate(32,'11.4','同一个上下文窗口里，谁占了多少位置？',471,
    '在 8,192 个 token 的窗口里多放 1,024 个检索 token，就必须从其他部分腾出同样多的位置。',
    '上排的输入和输出预留刚好占满窗口。下排把检索片段从 3,072 增到 4,096，合计变成 9,216。若其余输入都要保留，输出预留只能降到 1,536。');
  const names=['系统提示','对话历史','检索片段','当前问题','输出预留'];
  const inks=['#5f798a','#4875a2',C.teal,'#7c648c',C.rust],fills=['#dbe4e9','#d8e7f4','#c3e2d7','#e9dfec','#f3ddcb'];
  names.forEach((s,i)=>{const x=47+i*179;f.rect(x,91,15,15,fills[i],inks[i],1);f.t(x+24,105,s,17);});
  const left=48,right=946,scale=(right-left)/9216,limit=left+8192*scale;
  const base=[512,1536,3072,512,2560],more=[512,1536,4096,512,2560];
  f.t(47,157,'原请求',20,{weight:650});f.t(47,268,'再加入 1,024 个检索 token',20,{weight:650});
  [base,more].forEach((values,r)=>{
    let x=left;const y=176+r*110;
    values.forEach((v,i)=>{
      const w=v*scale;f.rect(x,y,w,42,fills[i],C.white,2);
      f.mid(x+w/2,y+27,v.toLocaleString('en-US'),16,{color:C.ink,weight:600});
      x+=w;
    });
  });
  f.line(limit,148,limit,337,C.rust,2,'4 4');f.end(limit-7,149,'窗口上限 8,192',18,{color:C.rust,weight:650});
  f.path('M'+limit+' 340v8H'+right+'v-8',C.rust,1.8);
  f.mid((limit+right)/2,372,'超出 1,024',16,{color:C.rust,weight:650});
  f.t(48,395,'图中单位均为 token。输出预留表示本次允许生成的最大长度。',16,{color:C.muted});
  return f;
}

function rag(){
  const f=new Plate(30,'11.5','RAG 怎样把答案连回资料中的原句？',493,
    '文档更新时重新处理受影响的索引条目。提问时把命中的原文与问题一起交给模型，读者可以按条款号核对。',
    '上排用一份虚构规范说明离线建索引，下排追踪一次提问。回答中的“10 分钟”来自检索命中的 §3.2。读者可以回到这个条款核对数字。');
  f.label(43,106,'离线 · 整理资料'); f.label(43,277,'在线 · 回答当前问题',C.blue);
  f.rect(45,125,183,91,C.white,C.rule,1.4,4);f.t(58,154,'《示例规范》v2',18,{weight:650});
  [76,135,108].forEach((w,i)=>f.line(59,171+i*10,59+w,171+i*10,C.rule,2));
  f.a(233,171,272,171,C.teal);f.t(282,149,'§2.1  温度校准流程',17,{color:C.muted});
  f.t(282,190,'§3.2  A 样品保温 10 分钟',17,{color:C.teal,weight:600});
  f.a(507,171,560,171,C.teal);
  f.box(565,147,143,47,'按片段建索引','teal',17);
  f.a(712,171,759,171,C.teal);
  f.box(764,145,183,51,'可更新的索引','teal',18,{outline:true});
  f.arrow([[856,198],[856,248],[368,248],[368,299]],C.teal,1.7);
  f.t(575,238,'供在线检索',15,{color:C.teal});
  f.box(44,307,195,60,'A 样品应保温多久？','blue',17);
  f.a(242,337,276,337,C.blue);f.box(280,302,175,70,'检索命中 §3.2','teal',18);
  f.a(458,337,492,337,C.teal);
  f.rect(496,297,227,80,C.sky,'none',0,5);f.t(510,327,'上下文 = 问题 ＋',17,{weight:600,color:C.blue});
  f.t(510,354,'“A 样品保温 10 分钟”',17,{color:C.blue});
  f.a(727,337,759,337,C.blue);
  f.rect(764,297,183,80,C.sand,'none',0,5);
  f.mid(856,326,'模型生成回答',16,{color:C.rust});f.mid(856,355,'10 分钟［§3.2］',18,{weight:650,color:C.rust});
  f.arrow([[142,369],[142,405],[609,405],[609,380]],C.blue,1.6,'5 4');
  f.t(293,395,'原问题随片段一起送入',15,{color:C.blue});
  return f;
}

function agent(){
  const f=new Plate(26,'11.6','工具返回的结果，怎样改变 Agent 的下一步？',465,
    '工具返回值进入下一轮观察。算出的平均值已经满足目标，系统便可结束循环并把结果交给读者。',
    '示例任务是求表中有效温度的平均值。第一次读表发现一个空值，第二次据此选取 80 和 84 计算，得到 82 ℃。两轮工具调用由实际观察连接。');
  f.t(43,105,'任务目标',18,{color:C.teal,weight:650});
  f.t(143,105,'计算表中有效温度的平均值，并报告单位。',18);
  const xs=[44,284,527,769],w=186;
  ['感知当前状态','判断并规划','执行工具','观察工具返回'].forEach((s,i)=>f.t(xs[i],156,s,19,{weight:650,color:i===3?C.rust:C.ink}));
  const top=['收到一份温度表','先弄清表中有哪些值','读取温度列','80、空值、84 ℃'];
  const bottom=['发现一个空值','选取两个有效数值','计算 (80 + 84) / 2','82 ℃'];
  [top,bottom].forEach((row,r)=>{
    const y=176+r*108;
    row.forEach((s,i)=>{
      f.box(xs[i],y,w,44,s,i===3?'rust':i===2?'blue':'teal',16,{weight:600});
      if(i<3) f.a(xs[i]+w+3,y+22,xs[i+1]-5,y+22);
    });
  });
  f.arrow([[862,223],[862,253],[137,253],[137,280]],C.rust,2.1);
  f.rect(396,239,209,25,C.white);f.mid(500,258,'返回值成为下一轮输入',16,{color:C.rust});
  f.arrow([[862,331],[862,358],[697,358]],C.teal,2);
  f.end(685,364,'目标已满足，提交结果并结束。',17,{color:C.teal,weight:600});
  return f;
}
module.exports=[scaling,multimodal,experts,contextWindow,rag,agent];
