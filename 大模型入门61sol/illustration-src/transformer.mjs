import {Fig,C,save,source,softmax,mix} from './core.mjs';

{
 const f=new Fig(1,'Transformer：两条序列，三种注意力','原始 2017 架构 · Post-Norm · 每个堆栈重复 N 次',850);
 f.rect(88,277,326,330,'#fbfcfc',C.rule,9);f.rect(559,221,339,386,'#fbfcfc',C.rule,9);
 f.label(100,258,'编码器 × N');f.label(572,202,'解码器 × N');
 const sub=(x,y,label,fill,w=238)=>f.box(x,y,w,44,label,fill);
 sub(129,536,'双向自注意力',C.tealLight);sub(129,485,'Add & Norm',C.soft);sub(129,401,'逐位置 FFN',C.orangeLight);sub(129,350,'Add & Norm',C.soft);
 f.arrow(248,536,248,529);f.arrow(248,485,248,445);f.arrow(248,401,248,394);
 f.route([[248,595],[110,595],[110,507],[129,507]],C.muted);f.route([[248,467],[110,467],[110,372],[129,372]],C.muted);
 f.arrow(248,350,248,315);f.box(152,283,192,32,'原文表示',C.tealLight,C.teal,17);
 sub(605,546,'因果自注意力',C.tealLight);sub(605,495,'Add & Norm',C.soft);sub(605,411,'交叉注意力',C.blueLight);sub(605,360,'Add & Norm',C.soft);sub(605,276,'逐位置 FFN',C.orangeLight);sub(605,225,'Add & Norm',C.soft);
 for(const [a,b]of [[546,539],[495,455],[411,404],[360,320],[276,269]])f.arrow(724,a,724,b);
 for(const [a,b]of [[600,517],[478,382],[343,247]])f.route([[724,a],[879,a],[879,b],[843,b]],C.muted);
 f.route([[344,299],[470,299],[470,433],[605,433]],C.blue,2.2);f.label(441,282,'K, V',C.blue);f.text(738,479,'Q',17,C.blue);
 f.arrow(724,225,724,176);f.box(621,146,206,30,'Linear → softmax',C.purpleLight,C.rule,17);
 for(const x of [248,724]){f.box(x-119,635,238,44,'Embedding + 位置编码',C.soft,C.rule,17);f.arrow(x,635,x,x===248?580:590);}
 f.text(248,724,'I  love  machine  learning',19,C.ink,'middle');f.arrow(248,700,248,679);
 f.text(724,724,'〈BOS〉 我 喜欢 机器 …',19,C.ink,'middle');f.arrow(724,700,724,679);
 f.text(724,755,'目标序列右移一位',17,C.muted,'middle');
 f.footer('Add & Norm = LayerNorm(x + Sublayer(x))；图中省略 dropout。','解码器的 Q 来自输出侧，交叉注意力的 K、V 来自编码器；训练可并行，生成逐步进行。');
 save(f,'original-transformer-architecture','编码器用双向自注意力形成原文表示；解码器先做因果自注意力，再用交叉注意力读取原文。原始 Transformer 使用 Post-Norm。',[source.transformer]);
}
{
 const f=new Fig(2,'一次注意力读取：先匹配，再汇总','固定一个 Query，观察它怎样从三个 Value 中读取信息',580);
 f.box(45,214,145,64,['当前 Query','qₜ'],C.tealLight,C.teal);
 const weights=[.6,.3,.1],vals=[[1,0],[0,1],[1,1]],ys=[180,287,394];
 ys.forEach((y,i)=>{f.box(252,y,115,44,`Key k${i+1}`,C.blueLight);f.arrow(190,246,252,y+22,C.blue);f.arrow(367,y+22,424,y+22);f.box(424,y,123,44,`α${i+1} = ${weights[i].toFixed(1)}`,C.tealLight,C.teal);f.box(611,y,138,44,`v${i+1} = [${vals[i]}]`,C.orangeLight);f.arrow(547,y+22,591,y+22);f.text(594,y+29,'×',23,C.muted);f.arrow(749,y+22,806,310,C.orange,1.5+weights[i]*3);});
 f.label(248,160,'① 点积比较');f.label(424,160,'② softmax');f.label(613,160,'③ 加权求和');
 f.circle(831,310,25,C.orangeLight,C.orange);f.text(831,318,'Σ',25,C.orange,'middle');f.arrow(856,310,897,310);f.text(929,303,'oₜ',25,C.ink,'middle');f.text(929,332,'[0.7, 0.4]',16,C.ink,'middle');
 f.text(424,473,'0.6 × [1, 0] + 0.3 × [0, 1] + 0.1 × [1, 1] = [0.7, 0.4]',20,C.ink,'middle');
 f.footer('权重总和为 1；每个 Value 是向量，汇总结果也是向量。','数值为手工构造的教学例子；Query、Key、Value 的投影参数由训练学习。');
 save(f,'self-attention-query-key-value','注意力先把 Query 与 Key 的匹配分数变为归一化权重，再按权重汇总 Value。例中输出严格等于 [0.7, 0.4]。',[source.transformer],'手工数值例；权重归一化与加权和经代码验证。');
}
{
 const f=new Fig(3,'把每个位置的读取，合成矩阵运算','示例尺寸 T = 4，dₖ = 3，dᵥ = 2；颜色只用于区分矩阵',585);
 const mat=(x,y,r,c,col,title,shape)=>{f.matrix(x,y,Array.from({length:r},(_,i)=>Array.from({length:c},(_,j)=>.12+.6*((i*3+j*2)%7)/6)),27,{show:false,color:col});f.text(x+c*27/2,y-20,title,25,col,'middle');f.text(x+c*27/2,y+r*27+28,shape,17,C.muted,'middle');};
 mat(61,209,4,3,C.teal,'Q','T × dₖ');f.text(158,270,'×',25);mat(195,209,3,4,C.blue,'Kᵀ','dₖ × T');f.arrow(319,261,361,261);mat(380,209,4,4,C.purple,'S','T × T');f.text(434,380,'S = QKᵀ / √dₖ + M',18,C.purple,'middle');
 f.arrow(504,261,570,261);f.text(537,198,'逐行',16,C.muted,'middle');f.text(537,222,'softmax',16,C.muted,'middle');
 const att=[[1,0,0,0],[.4,.6,0,0],[.2,.3,.5,0],[.1,.2,.3,.4]];f.matrix(591,209,att,27,{show:false,color:C.teal});f.text(645,189,'A',25,C.teal,'middle');f.text(645,345,'T × T',17,C.muted,'middle');f.text(716,270,'×',25);mat(750,209,4,2,C.orange,'V','T × dᵥ');f.arrow(815,261,858,261);mat(885,209,4,2,C.teal,'O','T × dᵥ');
 f.rect(72,405,856,80,C.soft,C.rule);f.text(500,438,'O = softmax(QKᵀ / √dₖ + M) V',25,C.ink,'middle');f.text(500,469,'A 的每一行是一次读取：行和为 1，屏蔽位置的权重为 0',18,C.muted,'middle');
 f.footer('行 = 发起读取的位置；列 = 被读取的位置。这里展示带因果掩码的 A。','交叉注意力中，Q 有 T 行，K、V 有 S 行，权重矩阵相应为 T × S。');
 save(f,'scaled-dot-product-attention-matrices','形状依次为 (T×dₖ)(dₖ×T)→T×T，经逐行 softmax 后乘 T×dᵥ 的 V，输出 T×dᵥ。',[source.transformer]);
}
{
 const f=new Fig(4,'多头注意力：并行读取，再混合','各头有独立投影参数；每一头都完成同一种缩放点积注意力',580);
 f.box(45,289,120,70,['输入 X','T × d'],C.soft);const ys=[166,283,400],colors=[C.tealLight,C.blueLight,C.purpleLight];
 ys.forEach((y,i)=>{f.route([[165,324],[196,324],[196,y+30],[230,y+30]]);f.box(230,y,200,60,[`头 ${i+1}：独立投影`,'Qᵢ, Kᵢ, Vᵢ'],colors[i],C.rule,18);f.arrow(430,y+30,475,y+30);f.box(475,y,225,60,['softmax(QᵢKᵢᵀ / √dₖ + M)Vᵢ','输出 T × dᵥ'],colors[i],C.rule,16);f.route([[700,y+30],[738,y+30],[738,324],[779,324]]);});
 f.box(779,284,92,80,['拼接','Concat'],C.orangeLight,C.rule,17);f.arrow(871,324,907,324);f.box(910,284,55,80,['Wₒ','投影'],C.orangeLight,C.rule,17);
 f.text(820,400,'T × (h dᵥ)',18,C.muted,'middle');f.text(936,400,'T × d',18,C.muted,'middle');
 f.footer('图示 h = 3；常见等宽设置 dₖ = dᵥ = d / h。','不同头可以学到不同关系，但不预先指定“语法头”“语义头”等固定职责。');
 save(f,'scaled-dot-product-and-multi-head-attention','多个注意力头独立投影并读取，将各头输出沿特征维拼接，再经 Wₒ 映射回模型维度 d。',[source.transformer]);
}
{
 const f=new Fig(5,'位置如何进入模型：相加，或旋转','左：原始正弦位置编码；右：RoPE 在每个二维子空间旋转 Q、K',640);
 f.label(55,178,'A  把位置向量加到输入');f.label(535,178,'B  让点积感知相对位移');f.line(492,165,492,534,C.rule);
 const p=f.plot(83,232,346,175,{xmin:0,xmax:30,ymin:-1,ymax:1,xticks:[0,10,20,30],yticks:[-1,0,1],xlabel:'位置 t',ylabel:''});
 [.65,.2,.05].forEach((freq,i)=>{const col=[C.teal,C.blue,C.orange][i];f.curve(Array.from({length:121},(_,j)=>p(j/4,Math.sin(j/4*freq))),col);f.text(110+i*110,211,`ω = ${freq}`,15,col);});
 f.text(255,506,'x̃ₜ = xₜ + pₜ',25,C.teal,'middle');
 const cx=699,cy=351;f.circle(cx,cy,104,'none',C.rule);f.line(cx-128,cy,cx+128,cy,C.rule);f.line(cx,cy-126,cx,cy+122,C.rule);
 f.arrow(cx,cy,cx+98,cy,C.muted,2);f.text(cx+107,cy+25,'q',20,C.muted);let aq=.92,ak=.28;
 f.arrow(cx,cy,cx+98*Math.cos(aq),cy-98*Math.sin(aq),C.teal,3);f.text(750,252,'R(t)q',20,C.teal);
 f.arrow(cx,cy,cx+81*Math.cos(ak),cy-81*Math.sin(ak),C.orange,3);f.text(795,322,'R(s)k',20,C.orange);
 f.path(`M${cx+52},${cy} A52,52 0 0 0 ${cx+52*Math.cos(aq)},${cy-52*Math.sin(aq)}`,C.teal,1.7);f.text(620,479,'一对维度 = 一个旋转平面',17,C.muted);
 f.text(740,514,'q′ₜᵀk′ₛ = qₜᵀR(s − t)kₛ',22,C.teal,'middle');
 f.footer('曲线频率与旋转角度仅用于示意；实际频率按模型定义设置。','RoPE 通常旋转 Q、K；相对位置进入点积，不保证超出训练长度后的效果。');
 save(f,'positional-encoding-and-rope','加法位置编码把 pₜ 加到输入；RoPE 在二维子空间旋转 Q、K，使点积显式依赖相对位移 s−t。',[source.transformer,source.rope]);
}
{
 const f=new Fig(6,'一个 Pre-Norm Block 的两次残差更新','Norm 在子层之前；残差主干保留未经该子层变换的输入',610);
 const stage=(y,left,op,right,col)=>{f.box(47,y+35,112,52,left,C.soft);f.arrow(159,y+61,225,y+61);f.box(225,y+35,140,52,'Norm',C.soft);f.arrow(365,y+61,423,y+61);f.box(423,y+35,242,52,op,col);f.arrow(665,y+61,746,y+61);f.circle(767,y+61,20,C.paper,C.teal);f.text(767,y+69,'+',25,C.teal,'middle');f.arrow(787,y+61,843,y+61);f.box(843,y+35,115,52,right,C.soft);f.route([[186,y+61],[186,y],[767,y],[767,y+41]],C.teal,2);};
 stage(186,'H⁽ℓ⁾','多头自注意力','U',C.tealLight);stage(361,'U','逐位置 FFN','H⁽ℓ⁺¹⁾',C.orangeLight);
 f.text(499,307,'U = H⁽ℓ⁾ + Attention(Norm(H⁽ℓ⁾))',22,C.ink,'middle');f.text(499,482,'H⁽ℓ⁺¹⁾ = U + FFN(Norm(U))',22,C.ink,'middle');
 f.footer('每个节点保持 T × d；FFN 独立处理每一行，并在各位置共享同一组参数。','两次 Norm 各自带参数；原始 Transformer 的 Post-Norm 则是在残差相加之后归一化。');
 save(f,'transformer-block-residual-norm','Pre-Norm Block 的注意力和 FFN 都先做归一化，再通过残差相加更新表示。注意力交换位置信息，FFN 变换每个位置的特征。',[source.transformer,'https://arxiv.org/abs/2002.04745']);
}
{
 const f=new Fig(7,'三类 Transformer：信息能流向哪里？','小矩阵中，行是读取者，列是被读取者；实色表示允许读取',625);
 const names=['Encoder-only','Encoder–decoder','Decoder-only'];const xs=[42,366,690];
 xs.forEach((x,i)=>{f.rect(x,168,268,349,C.paper,C.rule);f.text(x+134,201,names[i],22,C.ink,'middle',600);});
 f.matrix(105,239,Array.from({length:4},()=>[.45,.45,.45,.45]),36,{show:false});f.text(176,409,'双向读取输入',19,C.teal,'middle');f.lines(176,451,['BERT / ViT','分类、检索表示'],18,C.muted,30,'middle');
 f.matrix(390,241,Array.from({length:3},()=>[.4,.4,.4]),24,{show:false,color:C.blue});f.matrix(538,241,Array.from({length:3},(_,i)=>Array.from({length:3},(_,j)=>j<=i?.5:null)),24,{show:false});f.arrow(465,273,532,273,C.blue);f.text(499,327,'输入 → 交叉注意力 → 输出',16,C.blue,'middle');f.text(499,409,'双向编码 + 因果解码',19,C.teal,'middle');f.lines(499,451,['原始 Transformer / T5','翻译、摘要'],18,C.muted,30,'middle');
 f.matrix(753,239,Array.from({length:4},(_,i)=>Array.from({length:4},(_,j)=>j<=i?.55:null)),36,{show:false});f.text(824,409,'只读自己与先前位置',19,C.teal,'middle');f.lines(824,451,['GPT 类模型','提示与回答处于同一序列'],18,C.muted,30,'middle');
 f.footer('这里比较典型注意力拓扑；具体模型还会改变归一化、位置编码、FFN 等组件。','右侧因果结构适合自回归生成；并不意味着网络能同时知道尚未生成的后续 token。');
 save(f,'transformer-architectures-encoder-decoder','Encoder-only 双向理解输入；Encoder–decoder 通过交叉注意力连接输入和输出；Decoder-only 沿同一序列因果生成。',[source.transformer]);
}
{
 const f=new Fig(8,'自回归生成：把刚选出的 token 接回去','每一行是一次模型调用；后一步的输入依赖前一步选出的结果',625);
 const seq=['〈BOS〉','我','喜欢','学习','〈EOS〉'];
 for(let i=0;i<4;i++){const y=174+i*83;f.text(48,y+26,`步骤 ${i+1}`,17,C.muted);f.tokens(132,y,seq.slice(0,i+1),{w:93,gap:8,active:i});f.arrow(551,y+20,602,y+20);f.box(605,y,118,40,'同一个模型',C.tealLight,C.teal,17);f.arrow(723,y+20,769,y+20);f.box(780,y,154,40,seq[i+1],C.orangeLight,C.orange);if(i<3)f.route([[858,y+40],[858,y+61],[130+(i+1)*101+47,y+61],[130+(i+1)*101+47,y+83]],C.orange,1.3);}
 f.footer('模型输出词表分布，再按贪心或采样规则选出一个 token；生成结束标记后停止。','图中按词分组只是教学示意，真实切分由 tokenizer 决定；各步共用同一组模型权重。');
 save(f,'autoregressive-generation','从起始标记开始，每次把新选出的 token 加入已有上下文，重新预测下一个 token，直到结束标记或长度上限。',[source.transformer]);
}
{
 const f=new Fig(9,'Prefill 与 Decode：历史 K、V 可以复用','示意单层、单头；实际每一层分别维护自己的 KV cache',650);
 f.label(49,177,'① Prefill：一起处理已知提示');f.tokens(57,199,['A','B','C'],{w:71});f.arrow(174,239,174,274);f.box(68,277,212,51,'并行计算 Q、K、V',C.tealLight,C.teal,18);f.arrow(174,328,174,366);
 f.text(56,359,'写入缓存',16,C.muted);f.tokens(57,378,['K₁','K₂','K₃'],{w:71,color:C.blue});f.tokens(57,430,['V₁','V₂','V₃'],{w:71,color:C.orange});
 f.line(332,165,332,519,C.rule);f.label(370,177,'② Decode：只计算新位置');f.box(379,200,124,43,'新 token D',C.orangeLight,C.orange,17);f.arrow(503,221,559,221);f.box(562,200,214,43,'得到 q₄、k₄、v₄',C.tealLight,C.teal,18);
 f.tokens(391,313,['K₁','K₂','K₃','k₄'],{w:76,active:3,color:C.blue});f.tokens(391,365,['V₁','V₂','V₃','v₄'],{w:76,active:3,color:C.orange});f.text(506,435,'复用历史',18,C.muted,'middle');f.text(682,435,'追加',18,C.orange,'middle');
 f.rect(638,307,88,104,'none',C.teal,5);f.route([[704,243],[704,271],[682,271],[682,307]],C.blue);f.route([[776,221],[839,221],[839,293]],C.teal);f.box(786,296,150,110,['新 q₄ 读取','全部 K、V','含当前第 4 项'],C.tealLight,C.teal,17);f.arrow(727,335,786,335,C.blue);f.arrow(727,387,786,379,C.orange);f.arrow(861,406,861,457);f.text(861,483,'预测第 5 个 token',17,C.ink,'middle');
 f.text(500,544,'缓存量 ≈ 2 B L T Hₖᵥ dₕₑₐd b',24,C.ink,'middle');
 f.footer('历史 Query 通常不用缓存；追加新位置不会改变因果模型中历史位置的表示。','例：B=1，L=32，T=8192，Hₖᵥ=8，dₕₑₐd=128，b=2 字节 ⇒ KV 张量约 1 GiB。');
 save(f,'parallel-processing-and-kv-cache','Prefill 并行计算提示各位置并建立缓存；Decode 只计算新位置的 Q、K、V，新 Q 读取已缓存与新追加的 K、V。',[source.kv]);
}
{
 const f=new Fig(24,'自注意力热图：一行就是一次读取','这里显示 softmax 后的注意力权重 α，而非未经归一化的分数',610);
 const toks=['I','love','machine','learning'];const a=[[.55,.20,.15,.10],[.15,.55,.20,.10],[.05,.10,.35,.50],[.05,.10,.60,.25]];
 const x=200,y=222,c=64;f.matrix(x,y,a,c,{highlight:3});toks.forEach((t,i)=>{f.text(x+i*c+30,y-17,t,16,C.muted,'middle');f.text(x-20,y+i*c+39,t,17,i===3?C.orange:C.muted,'end');});f.text(329,175,'Key：被读取的位置',19,C.blue,'middle');f.text(45,197,'Query',18,C.teal);
 f.label(529,245,'选中 learning 这一行');f.lines(529,284,['0.05 vI + 0.10 vlove','+ 0.60 vmachine + 0.25 vlearning'],20,C.ink,33);f.text(529,379,'与 machine 的权重最大：0.60',20,C.teal);f.text(529,417,'四个权重相加 = 1.00',20,C.ink);
 for(let i=0;i<60;i++)f.rect(529+i*5,457,5,15,mix('#f2f7f7',C.teal,i/59),'none',0);f.text(529,494,'0',15,C.muted);f.text(829,494,'1',15,C.muted,'end');
 f.footer('这是可双向读取的单头、单层示意；数值人工构造，不是某个真实模型的测量结果。','高注意力权重表示该头更多读取该 Value，并不能单独证明语义关系或因果解释。');
 save(f,'self-attention-score-heatmap','高亮 learning 作为 Query 的一行；其对 machine 的归一化权重为 0.60。图中是人工构造的注意力权重，不是真实模型观测。',[source.transformer],'手工教学热图；每行和为 1。');
}
{
 const f=new Fig(25,'合批的权衡：总吞吐与单请求延迟','同一组简化成本模型，分别看单位时间产出和尾部延迟',640);
 const bs=[1,2,4,8,16,32,64],step=b=>5+.25*b,wait=b=>.4*(b-1),through=b=>1000*b/step(b),lat=b=>step(b)+wait(b);
 const p=f.plot(91,238,346,233,{xmin:0,xmax:64,ymin:0,ymax:3200,xticks:[0,16,32,64],yticks:[0,800,1600,2400,3200],xlabel:'批次大小 B',ylabel:'总吞吐（token / s）'});const q=f.plot(589,238,346,233,{xmin:0,xmax:64,ymin:0,ymax:50,xticks:[0,16,32,64],yticks:[0,10,20,30,40,50],xlabel:'批次大小 B',ylabel:'P95 延迟示意（ms / step）'});
 f.label(91,179,'更多 token 分摊固定开销');f.label(589,179,'计算步长 + 等待组批');
 f.curve(Array.from({length:64},(_,i)=>p(i+1,through(i+1))),C.teal,3);f.curve(Array.from({length:64},(_,i)=>q(i+1,lat(i+1))),C.orange,3);
 bs.forEach(b=>{let a=p(b,through(b)),d=q(b,lat(b));f.circle(...a,3.5,C.teal,C.paper);f.circle(...d,3.5,C.orange,C.paper);});
 f.text(91,550,'step(B) = 5 + 0.25B ms',17,C.teal);f.text(589,550,'P95 示意 = step(B) + 0.4(B−1) ms',16,C.orange);
 f.footer('以上是教学成本模型，不是硬件实测，也不是某服务的价格或延迟保证。','实际 P95 取决于到达负载、调度、序列长度与硬件；合批并非在所有条件下都会增加延迟。');
 save(f,'batching-throughput-latency','教学模型展示批次增大时总吞吐上升并趋于饱和，而较长计算步与等待组批可能推高延迟。曲线不代表真实服务测量。',[],'合成成本模型；每步生成 B 个 token；不把手工曲线解释为实测分位数。');
}
{
 const f=new Fig(28,'因果掩码：并行计算，也不会偷看答案','输入右移一位；第 t 行读取 ≤ t 的输入，用来预测下一个 token',610);
 const toks=['〈BOS〉','我','喜欢','学习'];const x=214,y=222,c=62;f.matrix(x,y,Array.from({length:4},(_,i)=>Array.from({length:4},(_,j)=>j<=i?.4:null)),c,{show:false,highlight:2});
 toks.forEach((t,i)=>{f.text(x+i*c+29,y-17,t,17,C.muted,'middle');f.text(x-17,y+i*c+36,t,17,i===2?C.orange:C.muted,'end');});f.text(337,176,'允许读取的输入列',18,C.blue,'middle');
 f.label(533,216,'例如：位置 3 的输入是「喜欢」');f.tokens(535,245,['〈BOS〉','我','喜欢'],{w:108,active:2});f.arrow(710,286,710,326);f.box(585,329,250,49,'预测目标：学习',C.orangeLight,C.orange,20);f.lines(533,426,['「学习」作为第 4 个输入存在，','但第 3 行无法读取这一列。'],19,C.muted,29);
 f.footer('允许位置 Mₜₛ = 0；未来位置 Mₜₛ = −∞，softmax 后权重为 0。','训练时四行可以在同一层并行计算；生成时下一步输入仍须等待本步选出 token。');
 save(f,'causal-mask-and-shifted-targets','因果掩码禁止读取未来输入。示例中“喜欢”所在行可读取 BOS、我、喜欢，并预测“学习”；训练目标与输入错开一位。',[source.transformer],'补充图：澄清训练并行和生成串行的区别。');
}
