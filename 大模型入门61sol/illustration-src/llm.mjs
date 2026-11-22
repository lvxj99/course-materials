import {Fig,C,save,source,softmax,mix} from './core.mjs';

{
 const f=new Fig(17,'BPE：统计相邻符号对，逐轮合并','微型语料：low × 5，lower × 2，newest × 6，widest × 3',660);
 f.label(52,179,'语料中，每个词的次数都计入频率');
 const rows=[['初始','n e w e s t </w>','w i d e s t </w>'],['合并 e + s','n e w es t </w>','w i d es t </w>'],['合并 es + t','n e w est </w>','w i d est </w>'],['合并 est + </w>','n e w est</w>','w i d est</w>']];
 f.text(390,219,'newest × 6',20,C.teal,'middle');f.text(699,219,'widest × 3',20,C.blue,'middle');
 rows.forEach((r,i)=>{const y=243+i*75;f.text(51,y+27,r[0],17,C.muted);f.box(249,y,282,47,r[1],i?C.tealLight:C.soft,C.rule,19);f.box(559,y,282,47,r[2],i?C.blueLight:C.soft,C.rule,19);if(i)f.text(882,y+29,'9 次',19,C.orange);if(i<3){f.arrow(390,y+47,390,y+70);f.arrow(699,y+47,699,y+70);}});
 f.footer('这里用 </w> 表示词尾，采用词频加权计数；每次选中的符号对出现 6 + 3 = 9 次。','存在并列最高频时，按预定规则选一个；真实 BPE 的边界、预切分和字节处理依实现而异。');
 save(f,'bpe-tokenization','在给定带频次的小语料上，依次合并 e+s、es+t、est+词尾；每轮选中的相邻对都出现 9 次，合并结果加入词表。',[source.bpe],'明确词频、边界与并列选择的教学 BPE；计数由程序复核。');
}
{
 const f=new Fig(18,'从文字到向量：token id 是查表索引','示例词表和向量人工构造；真实 token 边界与 id 由 tokenizer 决定',625);
 f.box(48,196,214,61,'“我喜欢学习”',C.soft,C.rule,25);f.arrow(262,226,307,226);f.box(313,196,156,61,'Tokenizer',C.tealLight,C.teal,21);f.arrow(469,226,517,226);f.tokens(527,205,['我','喜欢','学习'],{w:122});
 const ids=[7,42,19],vecs=[[.2,-.4,.8,.1],[-.3,.5,.1,.7],[.6,.2,-.5,.4]];
 f.label(58,326,'Token ids');f.label(306,326,'查嵌入矩阵 E 的对应行');f.label(681,326,'输入 X：T × d');
 ids.forEach((v,i)=>{const y=355+i*55;f.box(69,y,87,37,String(v),C.soft,C.rule,20);f.arrow(156,y+18,230,y+18);f.text(254,y+26,`E[${v}, :]`,19,C.muted);vecs[i].forEach((z,j)=>{f.box(367+j*59,y,54,37,z.toFixed(1),z>0?C.tealLight:C.orangeLight,C.paper,17);});f.arrow(610,y+18,675,y+18);vecs[i].forEach((z,j)=>f.rect(690+j*45,y,40,37,mix(C.paper,z>0?C.teal:C.orange,Math.abs(z)),C.paper,2));});
 f.footer('Embedding 的形状是 |词表| × d；长度为 T 的 id 序列查表后得到 T × d。','id 的数值大小不代表语义距离；嵌入向量由训练学习，位置关系还需另行编码。');
 save(f,'tokenization-and-embedding','Tokenizer 将文本分成 token 并给出 id；Embedding 层以 id 为行索引查表，组成 T×d 的向量矩阵。id 和向量均为教学示例。',[source.transformer,source.bpe]);
}
{
 const f=new Fig(19,'温度：同一组 logits，不同的概率集中程度','所有柱高都由 softmax(z / τ) 计算；logits 固定为 [2, 1, 0, −1]',615);
 const temps=[.5,1,2],colors=[C.teal,C.blue,C.orange],names=['A','B','C','D'];
 temps.forEach((t,i)=>{const x=74+i*315,col=colors[i],probs=softmax([2,1,0,-1],t);f.text(x+115,185,`τ = ${t}`,25,col,'middle',600);const p=f.plot(x,244,230,229,{xmin:-.5,xmax:3.5,ymin:0,ymax:1,xticks:[],yticks:i===0?[0,.5,1]:[],ylabel:i===0?'概率':'',xlabel:''});probs.forEach((v,j)=>{const [xx,yy]=p(j,v),bw=37;f.rect(xx-bw/2,yy,bw,473-yy,col,'none',2,`data-prob="${v}"`);f.text(xx,yy-12,(100*v).toFixed(1)+'%',17,col,'middle');f.text(xx,502,names[j],18,C.muted,'middle');});});
 f.footer('τ > 0；低温使分布更集中，高温使分布更平坦，但不会改变各 logit 的排序。','当 τ → 0⁺ 且最大 logit 唯一时趋于贪心选择；温度控制采样，不提高事实正确率。');
 save(f,'temperature-next-token-distribution','固定 logits=[2,1,0,−1]，比较温度 0.5、1、2 下严格计算的 softmax 概率。温度越高，分布越平坦。',[],'解析计算；概率和为 1，显示百分比四舍五入。');
}
{
 const f=new Fig(20,'从预训练到使用：区分数据、信号与参数更新','后训练可组合多种方法，实际流程不要求把所有分支依次执行',720);
 f.box(50,198,234,67,['海量文本 / 代码等','预测下一个 token'],C.soft,C.rule,19);f.arrow(284,231,340,231);f.box(347,198,244,67,['预训练','建立基础能力'],C.tealLight,C.teal,20);f.arrow(591,231,645,231);f.box(652,198,291,67,'基座模型',C.tealLight,C.teal,22);
 f.route([[796,265],[796,298],[174,298],[174,339]],C.teal);f.box(50,342,249,80,['SFT：学习示范','指令 + 高质量回答'],C.blueLight,C.blue,19);f.arrow(299,381,357,381);
 f.rect(365,322,357,242,'#fbfcfc',C.rule);f.label(385,350,'继续优化（可选 / 可组合）');
 f.box(385,365,317,51,'偏好对 → DPO',C.purpleLight,C.rule,19);f.box(385,432,317,51,'偏好 → 奖励模型 → RL',C.purpleLight,C.rule,19);f.box(385,499,317,51,'可验证奖励 → RLVR',C.orangeLight,C.rule,19);
 f.route([[722,446],[795,446],[795,501]],C.teal);f.box(757,506,186,58,'可使用的模型',C.tealLight,C.teal,21);
 f.route([[850,564],[850,606],[668,606]],C.muted);f.box(56,580,608,51,'推理：提示 + 材料 + 解码设置 → 回答 / 工具调用',C.soft,C.rule,20);
 f.footer('预训练、SFT、偏好优化和 RL 通常更新参数；普通推理与上下文学习通常保持参数固定。','偏好信号关注相对可取性，可验证奖励关注可判定的结果；二者的目标不能混为一谈。');
 save(f,'training-to-usage-workflow','预训练建立基础能力，SFT 学习示范；DPO、基于奖励模型的 RL 和 RLVR 提供不同后训练路径，之后在固定权重下使用模型。',[source.dpo,'https://arxiv.org/abs/2203.02155']);
}
{
 const f=new Fig(21,'扩展能力的三处计算预算','比较计算花在何时、改变什么；不是三条统一且必然成立的增长曲线',625);
 const xs=[45,367,689];const titles=['预训练','后训练','推理时计算'];const cols=[C.teal,C.blue,C.orange];
 xs.forEach((x,i)=>{f.rect(x,171,265,350,C.paper,C.rule);f.text(x+132,209,titles[i],25,cols[i],'middle',600);});
 for(let i=0;i<4;i++)f.rect(78+i*43,360-i*20,29,65+i*20,mix(C.paper,C.teal,.28+i*.16),C.paper,2);f.lines(177,264,['数据量 · 参数量 · 训练步数'],16,C.muted,28,'middle');f.lines(177,451,['广泛任务与分布','改变模型参数'],19,C.ink,31,'middle');
 f.text(499,264,'更好的示范、偏好与奖励',17,C.muted,'middle');f.box(405,299,185,43,'生成候选回答',C.blueLight,C.blue,18);f.arrow(498,342,498,369);f.box(405,373,185,43,'评价 → 更新',C.blueLight,C.blue,18);f.lines(499,451,['对齐任务目标','改变模型参数'],19,C.ink,31,'middle');
 f.text(821,264,'更深的推导，或更多候选',17,C.muted,'middle');f.circle(732,347,7,C.orange,C.orange);for(let i=0;i<3;i++){f.arrow(741,347,790,300+i*47,C.orange);f.circle(799,300+i*47,7,C.orangeLight,C.orange);f.arrow(808,300+i*47,881,347,C.orange);}f.circle(891,347,9,C.orange,C.orange);f.lines(821,451,['一次任务内求解与验证','通常保持参数固定'],19,C.ink,31,'middle');
 f.footer('收益受数据质量、任务难度、预算分配与验证器质量影响；更多计算不保证更好的结果。','训练计算主要影响模型获得的能力；推理预算影响本次任务怎样使用已有能力。');
 save(f,'three-scaling-laws','预训练、后训练和推理时计算在不同阶段增加预算；前两者调整参数，后者通常在固定参数下加深求解或增加候选与验证。',['https://arxiv.org/abs/2203.15556','https://arxiv.org/abs/2408.03314'],'只作阶段与机制比较，不伪造 scaling-law 拟合曲线。');
}
{
 const f=new Fig(22,'多模态：把不同输入接到同一语言模型','一种常见连接方式；并不代表所有多模态模型都使用相同接口',660);
 const labels=[['文字','Tokenizer + Embedding'],['图像','视觉编码器 → 连接层'],['音频','音频编码器 → 连接层'],['视频','帧编码 + 时空位置']];const cols=[C.teal,C.blue,C.orange,C.purple];
 labels.forEach(([a,b],i)=>{const y=181+i*89,col=cols[i];f.box(49,y,93,51,a,mix(C.paper,col,.1),col,21);f.arrow(142,y+26,188,y+26);f.box(195,y,259,51,b,C.soft,C.rule,18);f.arrow(454,y+26,490,y+26);for(let j=0;j<5;j++)f.rect(498+j*19,y+8,14,35,mix(C.paper,col,.3+j*.1),C.paper,2);f.route([[595,y+25],[636,y+25],[636,341],[675,341]],col);});
 f.box(682,266,158,153,['LLM backbone','融合上下文','生成下个 token'],C.tealLight,C.teal,19);f.arrow(840,341,880,341);f.box(886,289,72,104,['文','本','输出'],C.soft,C.rule,18);
 f.text(492,578,'特征投影对齐维度，联合训练学习模态之间的对应关系',22,C.ink,'middle');
 f.footer('视频通常还需要时间信息；有些架构用交叉注意力而非把所有模态直接拼接。','生成语音或图像通常还需专门的输出头、解码器或生成模块，此图聚焦多模态理解。');
 save(f,'multimodal-model-architecture','文字经分词与嵌入，图像、音频、视频经各自编码与连接模块，把表示接入 LLM；图中展示常见的多模态理解模式。',[],'通用架构示意，不冒充特定商用模型的内部结构。');
}
{
 const f=new Fig(23,'MoE：每个 token 只调用少数专家','示例共有 4 个 FFN 专家，路由选择 top-2；各 token 的选择可以不同',660);
 f.box(42,290,111,68,['当前 token','向量 x'],C.soft,C.rule,18);f.arrow(153,324,201,324);f.box(207,281,162,86,['Router','计算分数并选择'],C.blueLight,C.blue,18);
 const scores=[.52,.28,.12,.08];scores.forEach((s,i)=>{const y=186+i*89,active=i<2;f.route([[369,324],[404,324],[404,y+27],[477,y+27]],active?C.teal:C.rule,active?2.3:1.2,!active);f.text(439,y+11,String(s),16,active?C.teal:C.muted,'middle');f.box(484,y,158,54,`专家 E${i+1}`,active?C.tealLight:C.soft,active?C.teal:C.rule,21);if(active){f.route([[642,y+27],[754,y+27],[754,324],[778,324]],C.teal,2.3);f.text(697,y+7,`权重 ${i===0?'.65':'.35'}`,17,C.teal,'middle');}else f.text(674,y+33,'不执行',17,C.muted);});
 f.circle(804,324,25,C.orangeLight,C.orange);f.text(804,333,'Σ',26,C.orange,'middle');f.arrow(829,324,882,324);f.text(917,332,'y',27,C.ink,'middle');
 f.text(502,568,'y = 0.65 E₁(x) + 0.35 E₂(x)',25,C.teal,'middle');
 f.footer('示例将选中权重重新归一化：0.52 / (0.52 + 0.28) = 0.65；不同架构可有不同路由规则。','全部专家占用存储；每 token 激活较少专家仍有共享层、路由、通信与负载均衡开销。');
 save(f,'mixture-of-experts-layer','四个 FFN 专家中为当前 token 选中两个，以归一化权重 0.65 和 0.35 汇总输出。专家不是预先指定的领域知识库。',[source.moe],'4 专家 top-2 的教学设置，不使用具体模型的参数量作泛化结论。');
}
{
 const f=new Fig(26,'Agent：让工具结果决定下一步','模型提出动作，执行器操作环境，再把观测写回上下文',640);
 f.box(45,278,147,76,['目标与约束','读取任务'],C.soft,C.rule,20);f.arrow(192,316,236,316);
 f.box(243,263,196,106,['理解当前状态','推理 / 制定计划','选择下一步'],C.tealLight,C.teal,19);f.arrow(439,316,479,316);
 f.box(486,278,169,76,['调用工具','明确参数'],C.blueLight,C.blue,20);f.arrow(655,316,697,316);
 f.box(704,263,242,106,['执行器 + 环境','读取文件 / 运行代码','返回结果或错误'],C.orangeLight,C.orange,19);
 f.route([[824,369],[824,451],[341,451],[341,369]],C.orange,2.5);f.text(581,487,'观察 → 检查证据 → 更新上下文',21,C.orange,'middle');
 f.route([[341,263],[341,204],[767,204]],C.teal,2);f.box(773,178,174,51,'满足完成条件',C.tealLight,C.teal,19);f.text(535,189,'检查后可以结束',17,C.teal,'middle');
 f.text(497,549,'循环可以重试、修正计划，或在信息不足时请求人工判断',21,C.ink,'middle');
 f.footer('普通 Agent 循环通过上下文与外部状态继续任务，通常不会在每一步更新模型权重。','工具调用要经过实际执行；生成一段“已完成”的文字本身并不意味着任务已经完成。');
 save(f,'agent-iterative-cycle','模型根据目标与当前观测选择工具动作，执行环境返回结果，再检查证据、更新上下文并继续，直到满足完成条件。',[],'概念性系统流程，不把推理阶段的循环误画成参数训练。');
}
{
 const f=new Fig(29,'RAG：先找到证据，再带着证据回答','把知识放进当前上下文；检索结果的质量决定了模型能读到什么',675);
 f.label(49,176,'资料准备');f.box(49,202,161,61,['原始资料','保留版本与出处'],C.soft,C.rule,18);f.arrow(210,232,256,232);f.box(263,202,178,61,['切分 + 索引','关键词 / 向量'],C.blueLight,C.blue,18);f.arrow(441,232,486,232);f.box(493,202,178,61,['可检索资料库','片段 + 来源'],C.blueLight,C.blue,18);
 f.label(49,329,'回答问题');f.box(49,362,161,61,'用户问题',C.soft,C.rule,21);f.arrow(210,392,255,392);f.box(263,362,178,61,'检索 + 筛选',C.blueLight,C.blue,21);f.route([[582,263],[582,314],[352,314],[352,362]],C.blue,2);f.arrow(441,392,486,392);
 f.box(493,345,178,95,['上下文','问题 + 证据片段','来源标识'],C.tealLight,C.teal,18);f.arrow(671,392,715,392);f.box(722,362,105,61,'LLM',C.tealLight,C.teal,22);f.arrow(827,392,866,392);f.box(874,345,82,95,['回答','+','引用'],C.orangeLight,C.orange,18);
 f.route([[128,423],[128,487],[581,487],[581,440]],C.muted,1.5);f.text(344,514,'原问题与检索片段一起进入上下文',19,C.muted,'middle');
 f.text(499,573,'资料可以独立更新；普通 RAG 推理不需要同步修改模型权重',21,C.ink,'middle');
 f.footer('引用必须确实支持对应结论；检索不到、文档过期或片段缺失时，应说明证据不足。','补充上下文与微调解决不同问题，也可以结合使用。');
 save(f,'rag-retrieval-evidence-generation','先将资料切分并保留出处，查询时检索相关片段，将问题与片段一起交给 LLM，生成可对应原文的回答与引用。',[source.rag],'补充图：展示资料准备、查询检索与有依据回答之间的数据流。');
}
