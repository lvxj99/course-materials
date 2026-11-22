import {Fig,C,save,source,glyph,rng,gaussian,mix} from './core.mjs';

{
 const f=new Fig(10,'Autoencoder：用一个瓶颈，重建整个输入','训练目标由输入本身提供；低维表示保留对重建有用的信息',580);
 glyph(f,54,237,136);f.text(122,210,'输入 x',21,C.ink,'middle');f.text(122,411,'28 × 28 = 784',18,C.muted,'middle');f.arrow(190,305,236,305);
 f.path('M250 217 L390 272 L390 338 L250 393 Z',C.teal,1.5,C.tealLight);f.text(307,313,'Encoder',20,C.teal,'middle');f.arrow(390,305,438,305);
 for(let i=0;i<8;i++)f.rect(450+i*10,254,8,102,mix(C.tealLight,C.teal,(i%4)/4),C.paper,1);
 f.text(490,210,'潜在向量 z',21,C.teal,'middle');f.text(490,411,'16 维',18,C.muted,'middle');f.arrow(536,305,580,305);
 f.path('M593 272 L733 217 L733 393 L593 338 Z',C.orange,1.5,C.orangeLight);f.text(675,313,'Decoder',20,C.orange,'middle');f.arrow(733,305,789,305);
 glyph(f,804,237,136,{variant:.7,noise:.02});f.text(872,210,'重建 x̂',21,C.ink,'middle');f.text(872,411,'784 → 28 × 28',18,C.muted,'middle');
 f.text(500,474,'训练：让重建误差 ‖x − x̂‖² 尽可能小',23,C.ink,'middle');
 f.footer('数字图案由解析笔画函数绘制；“重建图”只是教学示意，不是已训练网络的输出。','瓶颈的维数示例为 16；普通 AE 不自动给出一个可直接采样的潜在先验。');
 save(f,'autoencoder-reconstruction','编码器把 784 维输入映射到示例中的 16 维潜在向量，解码器再重建输入；两者通过重建损失联合训练。',['https://www.deeplearningbook.org/contents/autoencoders.html']);
}
{
 const f=new Fig(11,'去噪自编码器：输入受扰动，目标保持干净','网络学习稳定结构；训练时知道原始干净样本',605);
 glyph(f,58,216,127);glyph(f,307,216,127,{noise:.38});glyph(f,810,216,127,{noise:.025,variant:.3});
 f.text(122,191,'干净样本 x',20,C.ink,'middle');f.text(371,191,'扰动输入 x̃',20,C.orange,'middle');f.text(873,191,'预测 x̂',20,C.teal,'middle');
 f.arrow(185,280,292,280,C.orange);f.text(240,257,'加噪',18,C.orange,'middle');f.arrow(434,280,493,280);f.box(498,238,250,82,['Encoder → z → Decoder','只接收 x̃'],C.tealLight,C.teal,19);f.arrow(748,280,795,280);
 f.route([[122,343],[122,437],[707,437]],C.blue,2);f.text(327,422,'干净原图提供训练目标',19,C.blue);f.route([[873,343],[873,400],[835,400],[835,412]],C.teal);
 f.box(707,412,229,55,'L = ‖x − x̂‖²',C.orangeLight,C.orange,23);
 f.footer('损失比较的是预测与干净样本，而不是预测与带噪输入。','图像为代码构造的示意；实际去噪能力来自训练数据、扰动机制与模型。');
 save(f,'denoising-autoencoder','先对干净样本 x 加噪得到 x̃，模型根据 x̃ 预测干净图像；重建损失以原始 x 为目标。',['https://www.deeplearningbook.org/contents/autoencoders.html']);
}
{
 const f=new Fig(12,'MAE：只编码可见部分，再补全被遮住的内容','示例 16 个 patch：保留 4 个，遮住 12 个，即 75%',665);
 const visible=[0,6,9,15],hidden=Array.from({length:16},(_,i)=>i).filter(i=>!visible.includes(i));
 glyph(f,52,234,160,{mask:hidden,outlines:true});f.text(132,203,'随机遮挡',21,C.ink,'middle');f.text(132,427,'4 / 16 可见',18,C.teal,'middle');f.arrow(212,314,260,314);
 f.box(268,265,139,98,['Encoder','仅可见 patch'],C.tealLight,C.teal,17);f.arrow(407,314,445,314);
 for(let i=0;i<4;i++)f.rect(457+i*23,283,18,62,C.tealLight,C.teal,2);f.text(501,250,'4 个编码',18,C.teal,'middle');f.arrow(550,314,599,314);
 for(let i=0;i<16;i++)f.rect(611+(i%4)*24,267+Math.floor(i/4)*24,20,20,visible.includes(i)?C.tealLight:C.soft,visible.includes(i)?C.teal:C.rule,2);
 f.text(656,230,'恢复位置顺序',18,C.ink,'middle');f.text(656,400,'+ 12 个 mask token',17,C.muted,'middle');f.arrow(711,314,751,314);
 f.box(756,265,187,98,['轻量 Decoder','重建所有 patch'],C.orangeLight,C.orange,17);
 f.route([[851,363],[851,462],[617,462]],C.orange);glyph(f,453,421,132,{outlines:true,noise:.02});
 hidden.forEach(k=>f.rect(453+k%4*33,421+Math.floor(k/4)*33,33,33,'none',C.orange,0,'stroke-width="1.6"'));f.text(674,512,'只在被遮住的位置计算损失',18,C.orange);
 f.footer('编码器不处理 mask token；它们在解码阶段与可见 patch 的编码一起使用。','橙色边框 = 被遮住位置的重建目标；图案和预测均为示意。');
 save(f,'masked-autoencoder-mae','MAE 编码器只处理 25% 可见 patch；解码器接收其编码与 75% mask token，按原位置重建，损失在遮挡位置计算。',[source.mae]);
}
{
 const f=new Fig(13,'VAE：编码成分布，再通过采样解码','训练使用 qφ(z | x)，生成使用先验 p(z)；两者不要混淆',685);
 f.label(45,180,'训练');f.box(48,223,92,62,'输入 x',C.soft);f.arrow(140,254,183,254);f.box(187,210,147,90,['Encoder','μ(x), σ(x)'],C.tealLight,C.teal,19);f.arrow(334,255,381,255);
 f.box(387,216,242,78,['z = μ + σ ⊙ ε','ε ~ N(0, I)'],C.blueLight,C.blue,21);f.arrow(629,255,674,255);f.box(681,210,136,90,['Decoder','pθ(x | z)'],C.orangeLight,C.orange,18);f.arrow(817,255,866,255);f.text(910,262,'x̂',27,C.ink,'middle');
 f.text(507,329,'重参数化：随机性来自 ε，梯度流向 μ、σ',18,C.blue,'middle');
 const p=f.plot(99,400,254,120,{xmin:-3,xmax:3,ymin:0,ymax:.8,xticks:[-3,0,3],yticks:[],xlabel:'潜在变量 z 的一维切片',ylabel:''});
 const normal=(x,mu,s)=>Math.exp(-.5*((x-mu)/s)**2)/(s*Math.sqrt(2*Math.PI));f.curve(Array.from({length:81},(_,i)=>{const x=-3+6*i/80;return p(x,normal(x,0,1));}),C.muted,2,true);f.curve(Array.from({length:81},(_,i)=>{const x=-3+6*i/80;return p(x,normal(x,.9,.65));}),C.teal,3);f.text(95,383,'p(z)',17,C.muted);f.text(257,383,'qφ(z | x)',17,C.teal);
 f.text(431,403,'目标 = 重建负对数似然 + KL(qφ ‖ p)',21,C.ink);f.label(432,462,'生成');f.box(432,485,196,56,'z ~ N(0, I)',C.blueLight,C.blue,21);f.arrow(628,513,674,513);f.box(681,485,136,56,'Decoder',C.orangeLight,C.orange,18);f.arrow(817,513,866,513);f.text(903,520,'新样本',18,C.ink,'middle');
 f.footer('KL 项鼓励编码分布接近先验，并非强制每个样本的后验完全相同。','生成新样本时无需编码器；密度曲线是解析高斯示意，不是拟合结果。');
 save(f,'vae-latent-sampling','VAE 训练时由编码器给出均值和标准差，经重参数化采样后解码，同时最小化重建负对数似然与 KL；生成时直接从先验采样。',[source.vae]);
}
{
 const f=new Fig(14,'GAN：判别来源，也把梯度传回生成器','两个网络交替更新；实线是数据流，橙色虚线是生成器的学习反馈',625);
 f.box(57,300,109,65,['噪声 z','p(z)'],C.soft,C.rule,18);f.arrow(166,333,224,333);f.box(230,300,158,65,'生成器 Gθ',C.tealLight,C.teal,21);f.arrow(388,333,443,333);glyph(f,451,286,96,{noise:.03});f.text(499,416,'生成样本 Gθ(z)',18,C.teal,'middle');
 glyph(f,451,163,96);f.text(396,212,'真实数据',18,C.ink,'end');f.route([[547,211],[617,211],[617,301],[675,301]],C.blue);f.route([[547,333],[617,333],[617,333],[675,333]],C.teal);
 f.box(679,270,141,98,['判别器 Dψ','来源分数'],C.blueLight,C.blue,19);f.arrow(820,319,866,319);f.box(870,287,88,64,['真实？','生成？'],C.soft,C.rule,16);
 f.route([[748,368],[748,471],[309,471],[309,365]],C.orange,2.5,true);f.text(529,505,'更新 G：冻结 D 参数，但梯度仍穿过 D',20,C.orange,'middle');
 f.footer('更新 D：区分真实与生成，并断开生成样本到 G 参数的梯度。','更新 G：让 D 更倾向判为真实；生成阶段仅需 G。图像都是教学示意。');
 save(f,'gan-generator-discriminator','GAN 交替训练判别器与生成器；更新生成器时保持判别器权重不变，但保留经过判别器传向生成器的梯度。',[source.gan]);
}
{
 const f=new Fig(15,'Diffusion：训练学去噪，生成走反向采样','上：不同噪声等级的训练样本；下：从一份新的噪声开始生成',715);
 const xs=[67,265,463,661,859],sz=92,alphas=[1,.75,.4,.12,0];f.label(48,178,'前向加噪（预设，不学习）');
 xs.forEach((x,i)=>{glyph(f,x-5,210,sz,{signal:Math.sqrt(alphas[i]),noise:Math.sqrt(1-alphas[i]),seed:8+i,normalized:true});f.text(x+41,334,['x₀','xₜ₁','xₜ₂','xₜ₃','xT'][i],20,C.ink,'middle');if(i<4)f.arrow(x+87,255,x+178,255,C.muted);});
 f.text(500,378,'xₜ = √ᾱₜ x₀ + √(1 − ᾱₜ) ε，ε ~ N(0, I)',23,C.ink,'middle');
 f.label(48,421,'反向生成（模型预测 + 采样器更新）');
 xs.forEach((x,i)=>{glyph(f,x-5,451,sz,{signal:Math.sqrt(alphas[i]),noise:Math.sqrt(1-alphas[i]),seed:83+i,variant:2,normalized:true});f.text(x+41,574,i===0?'新样本':i===4?'新噪声':'中间状态',18,i===0?C.teal:C.muted,'middle');if(i<4)f.arrow(x+178,496,x+88,496,C.teal,2);});
 f.footer('上下两行图像是合成示意；上排按闭式边缘分布分别构造，不代表同一条马尔可夫轨迹。','反向更新需按噪声日程缩放，并可能注入随机噪声；并非简单反复做 x ← x − εθ。');
 save(f,'diffusion-forward-reverse-process','训练用已知噪声构造不同噪声等级的输入并训练噪声预测器；生成从独立的新噪声出发，经模型与采样器多步更新产生新样本。',[source.ddpm],'解析构造的灰度示意；未训练扩散模型，也未将插值图像声称为真实采样。');
}
{
 const f=new Fig(16,'Diffusion 与 Flow Matching：比较路径，也比较训练目标','二者都把简单分布变成数据分布；下方曲线仅是低维路径示意',705);
 const panels=[{x:53,title:'Diffusion · 随机反向 SDE',col:C.blue},{x:538,title:'Flow Matching · 确定性 ODE',col:C.teal}];
 panels.forEach(({x,title,col},idx)=>{f.label(x,180,title,col);f.line(x+25,419,x+365,419,C.rule);f.text(x+25,451,'噪声',17,C.muted);f.text(x+365,451,'数据',17,C.muted,'end');f.arrow(x+89,443,x+301,443,C.muted);
 const rr=rng(133);for(let k=0;k<3;k++){const pts=[];let jitter=0;for(let i=0;i<=75;i++){const t=i/75;jitter=.73*jitter+(rr()-.5)*12;const yy=257+k*58+30*Math.sin(t*Math.PI)*(k-1)+20*Math.sin(t*Math.PI*1.7)+(idx===0?jitter*Math.sin(Math.PI*t):0);pts.push([x+26+t*338,yy]);}f.curve(pts,col,2.3);f.circle(...pts[0],4,C.paper,col);f.circle(...pts.at(-1),4,col,col);}
 f.lines(x+10,490,idx===0?['模型学习 score / 噪声等量','选定起点后，后续仍含随机增量']:['模型拟合指定概率路径的速度场','选定起点后，按 ODE 数值积分'],18,C.muted,29);
 });
 f.box(83,559,834,48,'Diffusion 也可用概率流 ODE 采样；FM 的生成轨迹也不必是直线。',C.orangeLight,C.rule,19);
 f.footer('FM 可选择扩散路径，也可选择其他概率路径；“线性条件插值”不等于每条生成轨迹都直。','采样步数和速度取决于训练、路径、求解器与误差要求，不能仅凭曲线形状判断。');
 save(f,'flow-matching-vs-diffusion','对比随机反向 SDE 与 Flow Matching 的确定性 ODE；扩散模型亦有概率流 ODE，Flow Matching 可拟合多种路径，因此不能把两者简单等同于曲线与直线。',[source.flow,source.sde],'路径为低维概念示意，不用于比较生成质量或计算效率。');
}
{
 const f=new Fig(27,'强化学习：动作改变环境，反馈改变策略','统一时间记号：在 sₜ 采取 aₜ，随后收到 rₜ₊₁ 与 sₜ₊₁',605);
 f.box(93,252,263,139,['Agent','策略 πθ(a | s)','根据状态选择动作'],C.tealLight,C.teal,21);f.box(647,252,263,139,['Environment','状态转移 + 奖励','响应当前动作'],C.blueLight,C.blue,21);
 f.route([[356,288],[468,288],[468,214],[779,214],[779,252]],C.teal,2.5);f.text(540,194,'动作 aₜ',21,C.teal);
 f.route([[647,352],[542,352],[542,437],[225,437],[225,391]],C.orange,2.5);f.text(380,479,'奖励 rₜ₊₁ + 下一状态 sₜ₊₁',22,C.orange,'middle');
 f.text(498,514,'最大化 E[Gₜ]，Gₜ = rₜ₊₁ + γ rₜ₊₂ + γ² rₜ₊₃ + …',21,C.ink,'middle');
 f.footer('环境返回的是行动后果，通常没有逐动作的标准答案；训练依据长期累计奖励。','部分可观测任务中，Agent 接收观测 oₜ，并可能需要记忆历史，而非直接看到完整状态。');
 save(f,'agent-environment-reinforcement-loop','Agent 按策略选择动作 aₜ，环境返回奖励 rₜ₊₁ 和下一状态 sₜ₊₁；强化学习优化期望折扣回报。',[source.rl]);
}
{
 const f=new Fig(30,'贝尔曼递推：眼前奖励 + 下一状态价值','一个动作、两个可能后继状态；用概率做加权平均',630);
 f.circle(153,315,55,C.tealLight,C.teal);f.text(153,325,'s',34,C.teal,'middle');f.text(153,411,'固定动作 a',20,C.ink,'middle');
 f.arrow(208,302,422,230,C.blue,2);f.arrow(208,331,422,411,C.orange,2);f.text(302,224,'P = 0.75',19,C.blue,'middle');f.text(302,428,'P = 0.25',19,C.orange,'middle');
 f.box(435,184,203,95,['s₁：Vπ(s₁) = 4','即时奖励 r = 2'],C.blueLight,C.blue,19);f.box(435,369,203,95,['s₂：Vπ(s₂) = 1','即时奖励 r = −1'],C.orangeLight,C.orange,19);
 f.text(679,221,'2 + 0.9 × 4 = 5.6',21,C.blue);f.text(679,406,'−1 + 0.9 × 1 = −0.1',21,C.orange);
 f.rect(121,497,758,49,C.soft,C.rule);f.text(500,529,'Qπ(s, a) = 0.75 × 5.6 + 0.25 × (−0.1) = 4.175',22,C.ink,'middle');
 f.footer('此例 γ = 0.9；下一状态价值已经包含之后全部折扣奖励，不需要展开无限长轨迹。','Vπ(s) 再按 π(a | s) 对动作价值求平均；最优方程则在动作间取最大值。');
 save(f,'bellman-backup-example','固定动作后，对各后继状态的即时奖励与折扣价值按转移概率加权。例中 γ=0.9，Qπ(s,a)=4.175。',[source.rl],'补充图：手工 MDP 数值例，经计算验证。');
}
