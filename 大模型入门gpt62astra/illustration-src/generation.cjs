'use strict';
const {C,Plate,blend,rng,normal}=require('./drawing.cjs');
const {digit,tile,cropPatch,corrupt,diffusionSamples}=require('./pixels.cjs');

function autoencoder(){
  const f=new Plate(10,'8.1','把 784 个像素压成 16 个数',404,
    '解码器只能看到短向量 z。把重建图与原图逐像素比较，误差会同时更新编码器和解码器。',
    '两端都是 28×28 的图像，中间只传递 16 个数。图中笔画和潜在向量是为说明重建任务而绘制的示例。');
  const x0=digit(2),pred=digit(2,.9);
  f.mid(115,112,'输入 x',20,{weight:650});f.mid(489,112,'紧凑表示 z',20,{color:C.rust,weight:650});f.mid(880,112,'重建图像',20,{weight:650});
  tile(f,49,140,134,x0);tile(f,813,140,134,pred);
  f.a(186,207,224,207,C.teal);
  f.poly([[228,145],[364,183],[364,232],[228,270]],C.mint,C.teal,1.4);
  f.mid(289,214,'编码器',21,{color:C.teal,weight:650});
  f.a(367,207,413,207,C.teal);
  const z=[.72,.23,.82,.51,.07,.65,.37,.96,.25,.48,.91,.19,.54,.87,.33,.62];
  z.forEach((v,i)=>f.rect(419+(i%8)*18,183+Math.floor(i/8)*24,16,21,blend(C.sand,C.rust,v)));
  f.a(565,207,626,207,C.blue);
  f.poly([[630,183],[768,145],[768,270],[630,232]],C.sky,C.blue,1.4);
  f.mid(703,214,'解码器',21,{color:C.blue,weight:650});
  f.a(771,207,810,207,C.blue);
  f.mid(116,304,'28 × 28 = 784',18);f.mid(491,266,'每个色块代表一个数',16,{color:C.muted});
  f.mid(881,304,'28 × 28 = 784',18);f.mid(489,327,'训练目标是让重建笔画接近原笔画。',17,{color:C.muted});
  return f;
}

function denoising(){
  const f=new Plate(11,'8.2','去噪训练到底拿哪张图当答案？',424,
    '网络读入受扰动的图像，训练目标来自加噪前的干净原图。两条路径来自同一个样本。',
    '先给原创数字添加随机像素扰动。沿上方路径看模型的输入与输出，沿下方路径看计算损失时使用的目标。重建笔画为教学示意。');
  const original=digit(2),noisy=corrupt(original,471);
  const px=[53,306,825],side=112;
  ['干净原图 x','扰动输入','重建结果'].forEach((s,i)=>f.mid(px[i]+56,122,s,20,{weight:650}));
  tile(f,px[0],146,side,original);tile(f,px[1],146,side,noisy);tile(f,px[2],146,side,digit(2,.6));
  f.a(170,201,301,201,C.rust,2.4); f.mid(234,183,'随机加噪',17,{color:C.rust});
  f.a(424,201,491,201,C.blue);f.box(495,178,197,48,'编码器 ＋ 解码器','blue',19);
  f.a(695,201,821,201,C.blue);f.mid(756,183,'预测',17,{color:C.blue});
  f.arrow([[109,261],[109,320],[753,320]],C.teal,2.4);
  f.arrow([[881,261],[881,291]],C.blue);
  f.box(757,294,194,50,'与原图逐像素比较','teal',18,{outline:true});
  f.t(285,306,'保留一份干净副本作为目标',18,{color:C.teal,weight:600});
  return f;
}

function mae(){
  const f=new Plate(12,'8.3','遮掉十二块，编码器还能读到什么？',442,
    '编码器只接收 4 个可见块。解码器补入 12 个掩码标记，预测缺失位置，并在这些位置计算重建损失。',
    '同一幅数字被切成 4×4 块。沿绿色边框找出仍可见的四块，核对它们在中间的排列，再看最右侧 12 个橙色虚框对应哪些训练目标。');
  const input=digit(2),prediction=digit(2,.65),visible=[1,6,9,14],set=new Set(visible);
  const panels=[{x:45,y:152,a:input},{x:263,y:152,a:input},{x:801,y:152,a:prediction}],side=140,p=35;
  f.mid(115,112,'切成 16 块',20,{weight:650});f.mid(332,112,'随机遮住 75%',20,{weight:650});
  f.mid(587,112,'进入编码器的 4 块',20,{weight:650});f.mid(870,112,'解码并还原',20,{weight:650});
  panels.forEach(({x,y,a},g)=>{
    tile(f,x,y,side,a);
    for(let i=0;i<16;i++){
      const xx=x+(i%4)*p,yy=y+Math.floor(i/4)*p;
      if(g===1&&!set.has(i)){
        f.rect(xx,yy,p,p,C.grey,C.white,1);
        f.line(xx+11,yy+24,xx+24,yy+11,'#adbbbc',1.6);
      }else{
        if(g===2&&set.has(i))tile(f,xx,yy,p,cropPatch(input,i),{n:7,border:false});
        if(g===2&&!set.has(i)){
          f.path('M'+(xx+1)+' '+(yy+1)+'h'+(p-2)+'v'+(p-2)+'h-'+(p-2)+'z',C.rust,1.6,'none','4 2');
        }else{
          f.rect(xx+.6,yy+.6,p-1.2,p-1.2,'none',g===0?C.white:C.teal,g===0?1:1.7);
          if(g===2)f.poly([[xx+1,yy+1],[xx+9,yy+1],[xx+1,yy+9]],C.teal);
        }
      }
    }
  });
  f.a(189,224,257,224);f.a(407,224,486,224,C.teal);
  visible.forEach((index,i)=>{
    const x=493+i*51;
    tile(f,x,201,43,cropPatch(input,index),{n:7});
    f.rect(x,201,43,43,'none',C.teal,2);
    f.mid(x+21.5,269,'#'+(index+1),16,{color:C.teal});
  });
  f.a(695,224,794,224,C.rust);
  f.mid(115,324,'按行从 1 到 16 编号',16,{color:C.muted});
  f.mid(332,324,'斜线表示被遮挡',16,{color:C.muted});
  f.mid(590,324,'编码时保留位置信息',16,{color:C.muted});
  f.mid(869,324,'橙色虚框为预测位置',16,{color:C.rust});
  f.mid(499,363,'解码器按原位置放回可见块的表示，并为其余位置补上掩码标记。',17,{color:C.muted});
  return f;
}

function vae(){
  const f=new Plate(13,'8.4','VAE 训练和生成时，z 分别从哪里来？',479,
    '训练把重建误差和 KL 散度合在一起。生成时可以直接从先验抽取 z，再交给已经学好的解码器。',
    '取潜在空间的一维作图。训练时由输入得到后验近似 q(z|x)，用 z = μ + σε 取样。生成时从标准正态先验取样。曲线、样本点和笔画均为教学示例。');
  f.label(42,106,'训练',C.teal);f.label(42,272,'生成',C.blue);
  tile(f,43,125,72,digit(2)); f.a(119,161,152,161,C.teal);
  f.box(155,140,117,43,'编码器','teal',19);f.a(274,161,306,161,C.teal);
  f.t(43,225,'给定样本 x',16,{color:C.muted});
  f.t(42,315,'从先验 p(z) 抽样',19,{weight:600,color:C.blue});
  f.t(42,348,'取标准正态分布',17,{color:C.muted});
  function curve(y,mu,sigma,pick,color,label,parameters) {
    const left=311,width=227,map=z=>left+(z+2.5)/5*width,base=y+43;
    const densityHeight=z=>25/sigma*Math.exp(-.5*((z-mu)/sigma)**2);
    const points=Array.from({length:91},(_,i)=>{
      const z=-2.5+i/18;return [map(z),base-densityHeight(z)];
    });
    f.line(left,base,left+width,base,C.rule);
    f.wire(points,color,2.4);const px=map(pick),py=base-densityHeight(pick);
    f.line(px,base,px,py,color,1.3,'3 3');f.circle(px,py,4.5,color);
    f.mid(left+width/2,base+25,parameters,16,{color:C.muted});f.mid(left+width/2,y-22,label,18,{color,weight:600});
  }
  curve(149,.8,.45,.575,C.teal,'q(z | x)','μ = 0.8，σ = 0.45');
  curve(315,0,1,-.8,C.blue,'p(z)','μ = 0，σ = 1');
  f.a(542,163,616,163,C.teal);f.a(542,329,616,329,C.blue);
  f.mid(578,149,'z ≈ 0.58',15,{color:C.teal}); f.mid(578,315,'z = −0.8',15,{color:C.blue});
  f.box(620,140,121,47,'解码器','grey',19);
  f.box(620,306,121,47,'同一解码器','grey',17);
  f.a(744,163,814,163,C.teal);f.a(744,329,814,329,C.blue);
  tile(f,819,126,78,digit(2,.7)); tile(f,819,291,78,digit(3,-.3));
  f.mid(858,229,'重建输入样本',17);f.mid(858,396,'生成一个样本',17);
  f.line(40,247,955,247,C.faint,1.3);
  return f;
}

function gan(){
  const f=new Plate(14,'8.5','GAN 的判别分数怎样训练生成器？',465,
    '更新判别器时，用样本的来源作为标签。更新生成器时，保持判别器参数固定，让梯度穿过它回传。',
    '实线送入图像，虚线回传生成器所需的梯度。真实分支来自示意样本库，生成分支从随机向量出发。使用阶段只需保留生成器。');
  f.label(46,105,'两个来源'); f.label(733,105,'同一个判别器',C.blue);
  f.t(47,163,'示意样本库',19,{weight:600}); f.a(165,155,363,155,C.teal);
  tile(f,368,122,65,digit(3));f.t(451,160,'真实样本 x',18,{color:C.teal,weight:600});
  f.t(47,273,'随机向量 z',19,{weight:600});f.a(165,266,193,266,C.rust);
  f.box(196,244,136,43,'生成器 G','rust',19);f.a(335,266,363,266,C.rust);
  tile(f,368,233,65,digit(2,1.3));f.t(451,272,'生成样本 G(z)',18,{color:C.rust,weight:600});
  f.arrow([[574,155],[639,155],[639,195],[708,195]],C.teal,2);
  f.arrow([[574,266],[639,266],[639,215],[708,215]],C.rust,2);
  f.box(712,180,155,47,'判别器 D','blue',20);f.a(871,203,939,203,C.blue);
  f.mid(890,246,'真实性分数',17,{color:C.blue});
  f.arrow([[790,232],[790,346],[264,346],[264,292]],C.rust,2.5,'7 5');
  f.mid(525,376,'生成器的梯度沿虚线方向传回',18,{color:C.rust,weight:600});
  return f;
}

function diffusion(){
  const f=new Plate(15,'8.6','扩散从图像走向噪声，生成从新噪声出发',449,
    '上排按已知规则加噪。下排从独立抽取的噪声出发，逐步采样更清晰的图像，得到一个新样本。',
    '上排从数字 2 向右逐步加噪。下排从另一份噪声向左采样，这次得到数字 3。示例只含两个原创数字模板，因此可以直接计算反向采样的条件概率。');
  const {forward,reverse}=diffusionSamples(),left=228,dx=159,side=80;
  f.t(40,147,'构造训练数据',20,{weight:650,color:C.teal});
  f.t(40,176,'从左向右加噪 →',17,{color:C.teal});
  f.t(40,302,'生成一个样本',20,{weight:650,color:C.blue});
  f.t(40,331,'← 从右向左采样',17,{color:C.blue});
  ['t = 0','t = 1','t = 2','t = 3','t = 4'].forEach((s,i)=>{
    const x=left+dx*i; f.mid(x+side/2,110,s,19,{weight:600});
    tile(f,x,124,side,forward[i]);tile(f,x,258,side,reverse[i]);
    if(i<4){f.a(x+side+5,164,x+dx-6,164,C.teal);f.a(x+dx-6,298,x+side+5,298,C.blue);}
  });
  f.line(40,231,955,231,C.faint,1.3);
  f.mid(left+40,369,'采样结果',16,{color:C.blue});f.mid(left+4*dx+40,369,'新高斯噪声',16,{color:C.blue});
  f.mid(584,370,'两种数字模板上的解析采样示例',16,{color:C.muted});
  return f;
}

function flow(){
  const f=new Plate(16,'8.7','同一噪声起点，会走出几条采样轨迹？',467,
    '扩散也可以用确定性的概率流 ODE 采样。Flow Matching 学习速度场，样本随速度场前进，路径可以是弯的。',
    '横轴都是从噪声到数据的采样进度，纵轴是一维样本值。同一初值在左图遇到不同随机扰动可走出不同轨迹，在右图给定同一速度场后轨迹唯一。两图为解析分布上的算例。');
  const mean=t=>1.22*t+.19*Math.sin(2*Math.PI*t),sd=t=>1-.45*t;
  const v=(t,x)=>1.22+.38*Math.PI*Math.cos(2*Math.PI*t)-.45*(x-mean(t))/sd(t);
  const g=.72;
  function sample(seed){
    const rnd=rng(seed),n=96,dt=1/n,points=[[0,0]];let x=0;
    for(let i=0;i<n;i++){
      const t=i/n,score=-(x-mean(t))/sd(t)**2;
      x+=(v(t,x)+.5*g*g*score)*dt+g*Math.sqrt(dt)*normal(rnd);
      points.push([(i+1)/n,x]);
    }
    return points;
  }
  const groups=[
    {x:81,title:'反向扩散 · 随机微分方程',color:C.teal,paths:[sample(22),sample(51),sample(78)]},
    {x:572,title:'Flow Matching · 速度场的 ODE',color:C.blue,paths:[-.72,0,.72].map(z=>Array.from({length:97},(_,i)=>[i/96,mean(i/96)+sd(i/96)*z]))}];
  groups.forEach(({x,title,color,paths},which)=>{
    f.t(x-36,107,title,20,{color,weight:650});
    const w=356,top=146,base=314,lo=-1.35,hi=2.35,xx=t=>x+t*w,yy=z=>base-(z-lo)*(base-top)/(hi-lo);
    [-1,0,1,2].forEach(n=>{f.line(x,yy(n),x+w,yy(n),C.faint,1);f.end(x-9,yy(n)+4,String(n),14,{color:C.muted});});
    f.line(x,top,x,base);f.line(x,base,x+w,base);
    f.t(x-24,137,'x',16,{color:C.muted});f.t(x,base+25,'噪声端',16);f.end(x+w,base+25,'数据端',16);
    if(which){
      for(let i=1;i<9;i++) for(const z of [-.85,-.2,.5,1.25,1.95]){
        const t=i/10,dx=.032;
        f.a(xx(t)-4,yy(z),xx(t+dx)-4,yy(z+v(t,z)*dx),'#b9cdd9',1);
      }
    }
    paths.forEach((p,i)=>{
      const col=which===0?[C.teal,'#54998c','#af6239'][i]:['#9db9ca',C.blue,'#729baf'][i];
      const xy=p.map(([t,z])=>[xx(t),yy(z)]);
      f.wire(xy,col,i===1?2.7:1.9);f.circle(...xy[0],3.8,col);f.circle(...xy.at(-1),3.4,col);
    });
    f.mid(x+w/2,376,which?'三条曲线从三个不同的初值出发。':'三次采样从同一个初值出发。',17,{color:C.muted});
  });
  return f;
}

function reinforcement(){
  const f=new Plate(27,'8.8','走一步之后，奖励和新状态从哪里来？',435,
    '策略根据当前状态选择动作，环境在动作之后给出奖励和新状态。反复交互形成一条轨迹。',
    '格子例中，从第 2 格向右走到第 3 格，当前奖励为 0。再向右进入终点才得到 +1。动作发生在 t，图中的反馈记为 rₜ₊₁，与后文回报公式一致。');
  f.label(47,110,'智能体');f.label(694,110,'环境');
  f.rect(43,137,237,118,C.mint,C.teal,1.4,8);
  f.t(63,176,'读取状态 sₜ',19,{weight:600,color:C.teal});f.t(63,219,'按策略 π(a | sₜ) 选动作',17);
  f.rect(689,137,266,118,C.sky,C.blue,1.4,8);
  f.t(708,176,'执行动作，更新位置',19,{weight:600,color:C.blue});f.t(708,219,'返回状态和这一步的奖励',17);
  f.a(285,161,684,161,C.teal,2.5);f.mid(481,145,'动作 aₜ · 向右走',18,{color:C.teal,weight:600});
  f.a(684,229,285,229,C.blue,2.5);f.mid(484,216,'新状态 sₜ₊₁，奖励 rₜ₊₁',18,{color:C.blue,weight:600});
  f.t(48,322,'一次转移',19,{weight:650});
  const cells=['第 1 格','起点 2','到达 3','终点 4'];
  cells.forEach((s,i)=>f.box(177+i*117,296,108,43,s,['grey','teal','blue','rust'][i],17));
  f.t(682,313,'本步奖励 0',18,{weight:600});
  f.t(682,345,'下步若进入终点，奖励 +1。',16,{color:C.muted});
  return f;
}
module.exports=[autoencoder,denoising,mae,vae,gan,diffusion,flow,reinforcement];
