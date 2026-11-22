import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {Fig,C,save,figures,esc,mix} from './svg-core.mjs';
const ROOT=fileURLToPath(new URL('../',import.meta.url));
const data=JSON.parse(readFileSync(path.join(ROOT,'examples/lab-data.json'),'utf8'));
const out=path.join(ROOT,'images');mkdirSync(out,{recursive:true});
{
 const f=new Fig(1,'强化学习：行动产生数据，数据改变策略','奖励评价后果；策略决定在当前情境中怎样行动',600);
 f.box(80,225,220,105,['策略 πθ','输入状态 / 历史','选择动作'],C.tealLight,C.teal,21);
 f.box(663,225,250,105,['环境','执行转移','返回奖励与新状态'],C.blueLight,C.blue,21);
 f.arrow(300,253,663,253,C.teal,2.5);f.text(482,230,'动作 aₜ',21,C.teal,'middle');
 f.route([[663,303],[491,303],[491,382],[190,382],[190,330]],C.blue,2);f.text(491,421,'经验 (sₜ, aₜ, rₜ₊₁, sₜ₊₁)',21,C.blue,'middle');
 f.box(635,432,278,57,'学习器：更新 θ',C.orangeLight,C.orange,21);f.route([[491,382],[774,382],[774,432]],C.orange,2);f.route([[635,460],[80,460],[80,330]],C.orange,2,true);
 f.footer('蓝色回路是与环境交互；橙色虚线是训练更新。部署时可固定参数，只运行交互回路。','反馈可能延迟，且当前策略决定下一批会遇到什么数据。');
 save(f,'rl-feedback-loop','行动、环境反馈与学习更新构成闭环。参数更新与部署时执行策略可以分开。');
}
{
 const f=new Fig(2,'两状态 MDP：现在提交，还是继续完善？','奖励与概率是明确设定的教学环境；γ = 0.9',660);
 f.circle(226,332,70,C.tealLight,C.teal,2);f.text(226,326,'s₀',32,C.teal,'middle');f.text(226,360,'粗稿',21,C.ink,'middle');
 f.circle(729,332,70,C.blueLight,C.blue,2);f.text(729,326,'s₁',32,C.blue,'middle');f.text(729,360,'已完善',21,C.ink,'middle');
 f.arrow(296,332,659,332,C.teal,2.5);f.text(477,307,'完善：r = −1，P = 0.8',21,C.teal,'middle');
 f.path('M190 271 C70 190 355 190 260 271',C.teal,2,'none',`marker-end="url(#arrow-${C.teal.slice(1)})"`);f.text(226,180,'完善失败：r = −1，P = 0.2',18,C.teal,'middle');
 f.path('M693 271 C573 190 858 190 763 271',C.blue,2,'none',`marker-end="url(#arrow-${C.blue.slice(1)})"`);f.text(729,180,'再次完善：r = −1，P = 1',18,C.blue,'middle');
 f.box(386,474,220,64,'终止 ⊥：V = 0',C.soft,C.rule,22);f.arrow(265,390,418,474,C.orange,2);f.arrow(690,390,573,474,C.orange,2);f.text(280,445,'提交：+2',20,C.orange,'middle');f.text(713,445,'提交：+8',20,C.orange,'middle');
 f.footer('动作由 Agent 选择；成功还是失败由转移概率决定。图中每个状态—动作的概率和为 1。','立即提交粗稿得 2；先完善一次再提交，期望折扣回报为 −1 + 0.9(0.8×8 + 0.2×2) = 5.12。');
 save(f,'two-state-mdp','两状态任务完整标出奖励、概率与终止，支持手算价值函数。');
}
{
 const f=new Fig(3,'Bellman 备份：用下一状态价值概括未来','固定策略：粗稿继续完善，完善后提交',620);
 f.box(52,266,150,91,['V(s₀)','未知量'],C.tealLight,C.teal,23);
 f.arrow(202,294,379,221,C.blue,2);f.arrow(202,332,379,408,C.orange,2);f.text(284,226,'0.8',21,C.blue,'middle');f.text(284,411,'0.2',21,C.orange,'middle');
 f.box(387,176,226,88,['成功 → s₁','V(s₁) = 8'],C.blueLight,C.blue,23);f.box(387,368,226,88,['失败 → s₀','V(s₀) 仍待求'],C.orangeLight,C.orange,21);
 f.text(660,224,'−1 + 0.9 × 8',24,C.blue);f.text(660,415,'−1 + 0.9 × V(s₀)',23,C.orange);
 f.rect(72,482,856,54,C.soft,C.rule);f.text(500,516,`V(s₀) = −1 + 0.9[0.8×8 + 0.2V(s₀)] = ${data.mdp.exact_v0.toFixed(6)}…`,21,C.ink,'middle');
 f.footer('两个分支都支付当前成本 −1；概率加权后的成本仍为 −1。','失败分支上的价值递归已经包含之后所有可能的再次尝试。');
 save(f,'bellman-backup','Bellman 方程把递归的期望未来压缩为一个可解方程；解析值约为 5.804878。');
}
{
 const f=new Fig(4,'MC、TD 与多步：奖励怎样传回前面？','观测奖励用橙色；尚未展开的未来用价值估计表示',950);
 const rows=[{y:201,name:'TD(0)',parts:['rₜ₊₁','γ V(sₜ₊₁)'],colors:[C.orangeLight,C.tealLight]},
 {y:310,name:'3-step',parts:['rₜ₊₁','γ rₜ₊₂','γ² rₜ₊₃','γ³ V(sₜ₊₃)'],colors:[C.orangeLight,C.orangeLight,C.orangeLight,C.tealLight]},
 {y:419,name:'MC',parts:['rₜ₊₁','γ rₜ₊₂','…','到真实终止'],colors:[C.orangeLight,C.orangeLight,C.orangeLight,C.orangeLight]}];
 rows.forEach(({y,name,parts,colors})=>{f.text(53,y+33,name,23,C.ink);parts.forEach((s,i)=>{f.box(208+i*182,y,160,57,s,colors[i],C.rule,19);if(i<parts.length-1)f.text(379+i*182,y+37,'+',23,C.muted,'middle');});});
 f.line(53,505,947,505,C.rule,1);f.label(53,538,'看一个完整例子：a → b → c → 终止，奖励依次为 0、0、1');
 f.text(53,571,'γ = 0.9；初始价值全为 0；步长 α = 1；每轮按 a、b、c 顺序更新',18,C.muted);
 const cols=[405,605,805];['V(a)','V(b)','V(c)'].forEach((s,i)=>f.text(cols[i],617,s,21,C.ink,'middle'));
 const samples=[['MC：一轮完整回报',data.td_propagation.mc,C.orange],...data.td_propagation.td_passes.map((v,i)=>[`TD：第 ${i+1} 轮之后`,v,C.teal])];
 samples.forEach(([label,vals,color],i)=>{const y=641+i*49;f.text(72,y+25,label,19,color);vals.forEach((v,j)=>f.box(cols[j]-73,y,146,37,Number(v.toFixed(2)).toString(),v>0?mix(C.paper,color,.12):C.soft,C.rule,20));});
 f.footer('MC 等到结局后，一轮就能算出所有回报；一步 TD 让已经学到的价值每轮向前传一站。','上表是确定性三步轨迹的实际计算。多步 TD 则一次使用更多步奖励，连接这两种做法。');
 save(f,'mc-td-returns','从目标公式到三步算例：MC 使用完整回报，TD 每轮把已学到的后继价值向前传递。');
}
{
 const f=new Fig(5,'DQN：预测在学习，目标慢一点变化','经验回放减少相关性；目标网络降低目标快速漂移',665);
 f.box(52,185,205,69,['环境交互','收集转移样本'],C.soft,C.rule,20);f.arrow(257,220,344,220);f.box(351,185,235,69,['经验回放池 D','(s, a, r, s′, done)'],C.blueLight,C.blue,19);f.arrow(586,220,670,220);f.box(678,185,271,69,'随机抽取 minibatch',C.soft,C.rule,20);
 f.route([[814,254],[814,300],[260,300],[260,341]],C.blue);f.box(79,346,361,70,['当前网络 Qθ(s, a)','梯度更新 θ'],C.tealLight,C.teal,22);
 f.arrow(814,254,814,345,C.blue);f.box(594,346,355,70,['目标网络 Qθ̄(s′, a′)','y = r + γ(1−d) max Qθ̄'],C.orangeLight,C.orange,19);
 f.route([[260,416],[260,479],[443,479]],C.teal);f.route([[771,416],[771,479],[657,479]],C.orange);f.box(447,447,207,64,'(Qθ − stopgrad(y))²',C.soft,C.rule,18);
 f.route([[447,479],[351,479],[351,416]],C.teal,2,true);f.text(233,522,'反向传播只更新当前预测',17,C.teal,'middle');f.route([[440,380],[594,380]],C.muted,1.5,true);f.text(517,345,'定期 / 缓慢同步',16,C.muted,'middle');
 f.footer('本次更新把目标 y 当作固定答案，梯度只调整当前网络的预测。','隔一段时间再同步目标网络，让预测逐渐追上目标，而目标也有序地向前移动。');
 save(f,'dqn-learning-loop','当前 Q 网络拟合从慢目标网络计算的 TD 目标；训练目标停止梯度，经验由回放池提供。');
}
{
 const f=new Fig(6,'策略梯度：平均方向不变，采样波动可以变小','两动作 bandit：P(A)=0.3，奖励 A=1、B=0；θ 是 A 的 logit',620);
 f.label(63,183,'不使用 baseline');f.label(540,183,'减去 baseline b = 0.3');
 const cards=[{x:63,vals:['A：0.7（概率 0.3）','B：0.0（概率 0.7）'],v:'0.1029'},{x:540,vals:['A：0.49（概率 0.3）','B：0.09（概率 0.7）'],v:'0.0336'}];
 cards.forEach(({x,vals,v})=>{f.box(x,209,393,104,vals,C.soft,C.rule,22);f.text(x+196,359,'期望梯度 = 0.21',25,C.teal,'middle');f.text(x+196,407,`梯度估计方差 = ${v}`,22,C.muted,'middle');});
 f.rect(110,455,780,52,C.tealLight,C.rule);f.text(500,488,'直接求导：dJ/dθ = p(1 − p) = 0.3 × 0.7 = 0.21',23,C.teal,'middle');
 f.footer('单样本估计为 (R − b) ∂logπ(a)/∂θ；同一状态下，各个动作减去相同的基线。','失败样本也能提供方向：降低 B 的概率，同样会提高 A 的概率。两种估计平均都指向 0.21。');
 save(f,'policy-gradient-baseline','直接求导、无基线 REINFORCE 与减基线估计具有相同期望，方差不同。');
}
{
 const f=new Fig(7,'GAE：让终局反馈沿时间往前传','γ = 1，λ = 0.9；用一条三步轨迹完整计算',640);
 const xs=[100,390,680];const rs=data.gae.rewards,vs=data.gae.values,ds=data.gae.delta,as=data.gae.advantages;
 xs.forEach((x,i)=>{f.text(x+105,180,`时刻 t = ${i}`,21,C.muted,'middle');f.box(x,211,210,52,`V(s${i}) = ${vs[i]}`,C.tealLight,C.teal,22);f.text(x+105,306,`r${i+1} = ${rs[i]}`,22,C.orange,'middle');f.box(x,340,210,52,`δ${i} = ${ds[i].toFixed(1)}`,C.orangeLight,C.orange,22);f.box(x,448,210,60,`Â${i} = ${as[i].toFixed(3)}`,C.tealLight,C.teal,24);f.arrow(x+105,392,x+105,448,C.orange);if(i<2)f.arrow(x+210,237,x+290,237,C.muted);});
 f.arrow(680,478,600,478,C.teal,2.5);f.arrow(390,478,310,478,C.teal,2.5);f.text(640,431,'× 0.9',18,C.teal,'middle');f.text(350,431,'× 0.9',18,C.teal,'middle');
 f.footer('δₜ = rₜ₊₁ + V(sₜ₊₁) − V(sₜ)，终止 V(s₃)=0；Âₜ = δₜ + 0.9 Âₜ₊₁。','λ=1 时得到 [0.6, 0.5, 0.4]，等于终局回报 1 减去各位置价值。');
 save(f,'gae-credit-assignment','GAE 从后往前递推，把最终奖励通过 TD 误差传播到早期动作。');
}
{
 const f=new Fig(8,'PPO 裁剪：正优势截右侧，负优势截左侧','ε = 0.2；实线为 min(ρA, clip(ρ, 0.8, 1.2)A)，虚线为 ρA',630);
 for(const [i,A]of [1,-1].entries()){const x=85+i*490,col=i?C.orange:C.teal;f.text(x+165,183,`A = ${A>0?'+1':'−1'}`,25,col,'middle');const p=f.plot(x,235,330,235,{xmin:.4,xmax:1.6,ymin:i?-1.8:0,ymax:i?0:1.8,xticks:[.4,.8,1,1.2,1.6],yticks:i?[-1.6,-.8,0]:[0,.8,1.6],xlabel:'概率比 ρ = πθ / πold',ylabel:'代理目标'});const xs=Array.from({length:121},(_,j)=>.4+j*.01);f.curve(xs.map(r=>p(r,r*A)),C.muted,1.6,true);f.curve(xs.map(r=>p(r,Math.min(r*A,Math.min(1.2,Math.max(.8,r))*A))),col,3);for(const r of [.8,1.2]){const xx=p(r,0)[0];f.line(xx,235,xx,470,C.rule,1,'stroke-dasharray="4 5"');}}
 f.footer('最大化该目标：正优势动作增概率，负优势动作减概率；反方向恶化仍会受到惩罚。','平段让这个样本停止追加鼓励；其他样本仍可通过共享参数改变它的概率。');
 save(f,'ppo-clipping','正负优势下的 PPO surrogate 曲线由公式直接计算，显示两侧不同的饱和方向。');
}
{
 const f=new Fig(9,'算法演进：三种问题，反复连接','顺着三列阅读：估计未来 → 改变行动 → 控制更新',680);
 const xs=[45,367,689];['怎样估计未来？','怎样改变行动？','怎样控制偏离？'].forEach((s,i)=>f.label(xs[i]+15,179,s));
 f.box(45,207,265,63,'Bellman → MC / TD',C.blueLight,C.blue,21);f.box(45,319,265,63,'Q-learning → DQN',C.blueLight,C.blue,21);f.arrow(177,270,177,319,C.blue);
 f.box(367,207,265,63,'REINFORCE',C.tealLight,C.teal,22);f.box(367,319,265,63,'Actor–Critic + GAE',C.tealLight,C.teal,21);f.arrow(499,270,499,319,C.teal);f.arrow(310,239,367,350,C.blue);
 f.box(689,207,265,63,'TRPO → PPO',C.orangeLight,C.orange,22);f.box(689,319,265,63,'概率比 / 裁剪 / KL',C.orangeLight,C.orange,20);f.arrow(821,270,821,319,C.orange);f.arrow(632,350,689,350,C.teal);
 f.route([[499,382],[499,437],[245,437],[245,481]],C.teal);f.route([[821,382],[821,437],[755,437],[755,481]],C.orange);
 f.box(101,485,290,69,['Critic 路线','PPO 式 RLHF / RLVR'],C.tealLight,C.teal,21);f.box(610,485,290,69,['组内比较路线','GRPO 等'],C.orangeLight,C.orange,21);
 f.footer('DPO 从 KL 正则化目标推导偏好损失，直接学习同题回答之间的比较。','连续控制、模型规划与离线 RL 则沿着不同任务需求发展出各自的方法。');
 save(f,'algorithm-map','价值、策略梯度与更新约束的联系，解释 PPO 和 GRPO 等后训练方法的共同基础。');
}
{
 const f=new Fig(10,'一段回答，就是一条决策轨迹','状态是 prompt + 已生成前缀；动作是下一个 token',640);
 f.box(47,213,149,63,'Prompt x',C.soft,C.rule,23);f.arrow(196,245,247,245);
 const tok=['先','检查','…','答案','〈EOS〉'];tok.forEach((s,i)=>{const x=255+i*139;f.box(x,213,113,63,s,i===4?C.orangeLight:C.tealLight,i===4?C.orange:C.teal,21);f.text(x+56,314,`动作 y${i+1}`,17,C.muted,'middle');if(i<4)f.arrow(x+113,245,x+139,245,C.teal);});
 f.text(500,371,'log πθ(y | x) = Σᵢ log πθ(yᵢ | x, y<ᵢ)',25,C.ink,'middle');
 f.route([[924,276],[924,431],[191,431]],C.orange,2);f.box(48,400,140,63,'终局奖励 R',C.orangeLight,C.orange,20);for(const x of [311,450,589,728,867])f.arrow(x,431,x,459,C.orange,1.5);f.text(585,492,'回报 / advantage 为生成动作提供训练权重',20,C.orange,'middle');
 f.footer('图中用词组示意生成位置；通常取 γ=1，终局回报沿整段回答提供学习信号。','动作损失计算在模型生成的位置；prompt 与工具结果通过上下文影响后续动作概率。');
 save(f,'llm-token-mdp','回答概率分解为逐 token 概率，终局奖励通过加权 log-probability 梯度影响整段生成行为。');
}
{
 const f=new Fig(11,'RLHF 里的不同模型，各自估计什么？','Actor、Critic、Reward、Reference，加上本轮采样的 Old policy',770);
 f.box(49,200,209,76,['Actor πθ','当前可训练策略'],C.tealLight,C.teal,21);f.arrow(258,238,337,238);f.box(345,200,223,76,['生成回答 y','保留各 token 前缀'],C.soft,C.rule,20);f.arrow(568,238,669,238);f.box(677,200,270,76,['Reward model / Verifier','完整回答 → 任务分'],C.orangeLight,C.orange,18);
 f.box(49,357,209,83,['Old πold','本轮采样 logprob'],C.blueLight,C.blue,19);f.box(345,357,223,83,['Critic Vφ','前缀 → 预计回报'],C.blueLight,C.blue,20);f.box(677,357,270,83,['Reference πref','回答 → 参考 logprob'],C.purpleLight,C.purple,19);
 f.arrow(456,276,456,357,C.blue);f.route([[568,254],[618,254],[618,397],[677,397]],C.purple);f.route([[153,276],[153,309],[79,309],[79,357]],C.muted,1.5,true);f.text(252,327,'采样时保存',16,C.muted,'middle');
 f.box(192,547,616,78,['PPO 更新：概率比 × advantage；参考 KL 控制行为偏离','Critic 另用回报目标训练'],C.tealLight,C.teal,20);
 f.route([[153,440],[153,515],[304,515],[304,547]],C.blue);f.arrow(456,440,456,547,C.blue);f.route([[812,440],[812,515],[701,515],[701,547]],C.purple);f.route([[947,238],[965,238],[965,489],[568,489],[568,547]],C.orange);
 f.route([[192,586],[29,586],[29,238],[49,238]],C.teal,2,true);f.text(500,665,'πold 随采样轮次刷新；πref 在当前训练阶段保持固定。',21,C.ink,'middle');
 f.footer('Critic 预测当前策略继续行动的回报；Reward 评价完成后的结果。','图中按职责分开绘制；实现时可以共享骨干，并把旧概率保存为数据。');
 save(f,'rlhf-model-roles','五种逻辑角色分别负责行动、未来估计、评分、参考正则和采样概率比。');
}
{
 const f=new Fig(12,'DPO：把奖励差，改写成策略概率比之差','从固定奖励下的 KL 正则化最优解出发，再连接偏好模型',660);
 const steps=[{y:185,title:'① 理想分布优化',s:'maxπ  Eπ[r] − β KL(π || πref)',c:C.tealLight},
 {y:293,title:'② 重排最优解',s:'r(x,y) = β log(π*(y|x) / πref(y|x)) + β log Z(x)',c:C.blueLight},
 {y:401,title:'③ 同题比较消去 Z(x)',s:'P(yw ≻ yl | x) = σ(β Δθ)',c:C.orangeLight}];
 steps.forEach(({y,title,s,c},i)=>{f.text(50,y+34,title,19,C.ink);f.box(300,y,648,66,s,c,C.rule,i===1?20:23);if(i<2)f.arrow(625,y+66,625,y+108);});
 f.text(500,530,'Δθ = log(πθ(yw|x)/πref(yw|x)) − log(πθ(yl|x)/πref(yl|x))',20,C.ink,'middle');
 f.footer('损失 L = −log σ(βΔθ)；Δθ 衡量胜者相对败者的概率比，比参考策略提高了多少。','同一题的 Z(x) 对两个回答相同，相减后消失；于是可以直接用偏好数据训练策略。');
 save(f,'dpo-reparameterization','DPO 把 KL 奖励最优策略关系代入偏好模型，使用同题比较消去未知归一化常数。');
}
{
 const f=new Fig(13,'GRPO：同一道题，让候选互相作参照','示例组大小 G = 4；使用总体标准差，忽略防除零小量',650);
 f.box(43,286,118,70,['同一题','Prompt x'],C.soft,C.rule,20);const rs=data.grpo.rewards;
 rs.forEach((r,i)=>{const y=185+i*84,col=r?C.teal:C.orange;f.route([[161,321],[195,321],[195,y+26],[237,y+26]],C.muted);f.box(244,y,175,50,`候选回答 ${i+1}`,mix(C.paper,col,.1),col,20);f.arrow(419,y+25,478,y+25);f.box(486,y,130,50,`R${i+1} = ${r}`,C.soft,C.rule,21);f.arrow(616,y+25,721,y+25,col);f.box(729,y,210,50,`Â${i+1} = ${r?'+1':'−1'}`,mix(C.paper,col,.1),col,24);});
 f.text(500,568,'均值 R̄ = 0.5，标准差 sR = 0.5；Âᵢ = (Rᵢ − R̄) / sR',22,C.ink,'middle');
 f.footer('同一回答的生成 token 共用终局优势；再通过 PPO 风格概率比与裁剪更新。','全对或全错时，这个相对奖励项为零；KL 等其他项仍可能更新。');
 save(f,'grpo-group-advantages','同题候选奖励经组内标准化得到相对优势，用于加权各回答的生成 token。');
}
{
 const f=new Fig(14,'完整后训练闭环：从尝试到反馈，再到更新','采样 → 打分 → 比较表现 → 调整概率 → 再试一次',670);
 const ys=205;const labels=[['Prompt 分布','按题取样'],['Rollout','记录行为概率'],['Reward','规则 / 模型评分'],['优势估计','GAE 或组内比较']];
 labels.forEach((ls,i)=>{const x=47+i*240;f.box(x,ys,195,78,ls,i<2?C.blueLight:C.orangeLight,C.rule,20);if(i<3)f.arrow(x+195,ys+39,x+240,ys+39);});
 f.route([[864,283],[864,354],[731,354],[731,390]],C.teal);f.box(574,395,312,78,['更新 Actor / 可选 Critic','裁剪、KL、掩码与归一化'],C.tealLight,C.teal,20);
 f.route([[574,434],[265,434],[265,322],[385,322],[385,283]],C.teal,2);f.text(421,419,'同步新策略，再采样',20,C.teal,'middle');
 f.arrow(731,473,731,533,C.muted);f.box(386,536,549,48,'独立题目 + 固定推理预算 + 失败样本审计',C.purpleLight,C.purple,20);f.text(59,566,'评估',22,C.purple);
 f.footer('训练题目提供反馈；新题目帮助我们看清学到的方法能否迁移。','采样和训练分开运行时，保存采样版本及其概率，便于计算本轮更新使用的比率。');
 save(f,'posttraining-dataflow','沿着一批回答，连接采样、打分、优势估计、策略更新与新题目评测。');
}
{
 const f=new Fig(15,'一个能求出精确答案的 KL 正则化实验','两回答 A / B：奖励为 1 / 0，参考概率为 0.5 / 0.5',640);
 f.label(75,178,'固定 β = 0.5，实际梯度上升');f.label(570,178,'改变 β，精确最优策略怎样变化');
 const p=f.plot(84,235,345,235,{xmin:0,xmax:2000,ymin:.45,ymax:1,xticks:[0,1000,2000],yticks:[.5,.75,1],xlabel:'梯度更新次数',ylabel:'P(A)'});
 f.curve(data.bandit.trace.map(([t,v])=>p(t,v)),C.teal,2.7);f.curve([p(0,data.bandit.optimum),p(2000,data.bandit.optimum)],C.orange,1.7,true);f.text(100,556,'虚线：解析最优 P(A) = 0.880797',17,C.orange);
 const q=f.plot(581,235,345,235,{xmin:.1,xmax:2,ymin:.45,ymax:1,xticks:[.1,.5,1,1.5,2],yticks:[.5,.75,1],xlabel:'参考 KL 强度 β',ylabel:'最优 P*(A)'});
 f.curve(data.bandit.beta_curve.map(([b,v])=>q(b,v)),C.blue,2.7);f.text(597,556,'P*(A) = sigmoid(1 / β)',21,C.blue);
 f.footer('曲线由 examples/rl_toy_lab.py 的解析公式与梯度迭代产生。','左图看优化怎样接近目标；右图看 KL 系数怎样改变目标本身。');
 save(f,'kl-bandit-experiment','数值梯度上升收敛至 KL 正则化目标的解析最优值；改变正则强度会改变最优策略。');
}
for(const f of figures)writeFileSync(path.join(out,f.file),f.svg,'utf8');
writeFileSync(path.join(out,'manifest.json'),JSON.stringify(figures.map(({svg,...f})=>f),null,2)+'\n','utf8');
const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>强化学习 · 插图册</title><style>*{box-sizing:border-box}body{margin:0;color:#26343b;background:#fff;font:17px/1.8 "Segoe UI","Microsoft YaHei",sans-serif}header,main,footer{max-width:1080px;margin:auto;padding:32px 30px}header{padding-top:70px;border-bottom:1px solid #d9dfdf}h1{font:42px/1.4 Georgia,"SimSun",serif}header p{color:#647079}a{color:#227d82;text-underline-offset:4px}.tag{font-size:13px;letter-spacing:3px;color:#227d82}.toc{columns:2;font-size:15px}.toc a{display:block;margin:7px 0;break-inside:avoid}article{margin:20px 0 55px}.canvas{overflow:auto;border:1px solid #d9dfdf;border-radius:5px}.canvas img{display:block;width:100%;height:auto}figcaption{margin:13px 0;font-size:16px}footer{border-top:1px solid #d9dfdf;font-size:14px}a:focus-visible,.canvas:focus-visible{outline:3px solid #b76343;outline-offset:3px}@media(max-width:600px){header,main,footer{padding:24px 16px}h1{font-size:32px}.toc{columns:1}.canvas img{min-width:760px}}@media print{.toc{display:none}article{break-inside:avoid}.canvas img{min-width:0}}</style></head><body><header><div class="tag">REINFORCEMENT LEARNING · 15 FIGURES</div><h1>从行动的后果，学会更好的选择</h1><p>强化学习拓展讲义配套插图。所有 SVG 由本地代码生成，数值示例与实验脚本相互校验。手机可在图内横向滚动，或打开独立 SVG 放大。</p><p><a href="强化学习_从序贯决策到大模型后训练.md">Markdown 讲义</a>　·　<a href="README.md">源码与验证说明</a></p><div class="toc">${figures.map(f=>`<a href="#f${f.id}">${String(f.id).padStart(2,'0')} · ${esc(f.title)}</a>`).join('')}</div></header><main>${figures.map(f=>`<article id="f${f.id}"><div class="canvas" tabindex="0" aria-label="${esc(f.title)}，可横向滚动"><img src="images/${f.file}" alt="${esc(f.caption)}" width="1000" height="${f.height}"></div><figcaption>${esc(f.caption)}　<a href="images/${f.file}" target="_blank">打开 SVG ↗</a></figcaption></article>`).join('')}</main><footer>不使用 CDN、远程字体或外部图片。重建图片：node src/build-figures.mjs；重算实验：python examples/rl_toy_lab.py。</footer></body></html>`;
writeFileSync(path.join(ROOT,'插图预览.html'),html,'utf8');
console.log(JSON.stringify({count:figures.length,root:ROOT},null,2));
