## 附录 A：Bellman 压缩性与策略改进的依据

令 $D=V-W$。对任意状态，

$$
\begin{aligned}
|(T^\pi V)(s)-(T^\pi W)(s)|
&=\left|\gamma\sum_{a,s'}\pi(a\mid s)P(s'\mid s,a)D(s')\right|\\
&\leq\gamma\sum_{a,s'}\pi(a\mid s)P(s'\mid s,a)\|D\|_\infty\\
&=\gamma\|D\|_\infty.
\end{aligned}
$$

对所有状态取最大值，即得压缩性。最优算子也满足同样的界，因为

$$
|\max_a f(a)-\max_a g(a)|\leq\max_a|f(a)-g(a)|.
$$

策略改进则利用单调性。若新策略 $\pi'$ 在每个状态选择使 $Q^\pi(s,a)$ 最大的动作，那么

$$
T^{\pi'}V^\pi\geq V^\pi.
$$

反复应用保持不等式的 $T^{\pi'}$，再取收敛极限，得到 $V^{\pi'}\geq V^\pi$。这就给出了第 5 节策略改进的依据：准确评估旧策略后，在每个状态选取更好的动作，能够提高或保持各状态的价值。

矩阵形式也有帮助。令 $P^\pi$ 为策略诱导的状态转移矩阵，$r^\pi$ 为期望立即奖励向量，则

$$
V^\pi=r^\pi+\gamma P^\pi V^\pi,
\qquad
V^\pi=(I-\gamma P^\pi)^{-1}r^\pi.
$$

终止状态可以作为零奖励吸收态。对大状态空间直接求逆通常不现实，迭代与采样方法则避免显式构造这个逆。

## 附录 B：一页符号表

| 符号 | 含义 | 在哪里用到 |
|---|---|---|
| $r_{t+1}$ | 执行动作后得到的单步奖励 | 构造回报与 TD 目标 |
| $G_t$ | 从时刻 $t$ 开始的折扣回报 | MC、REINFORCE；GRPO 的 $G$ 则表示组大小 |
| $V^\pi,Q^\pi$ | 当前策略的状态价值、动作价值 | 预测未来回报与选择动作 |
| $A^\pi$ | 动作比当前策略平均表现好多少 | 给策略梯度提供相对权重 |
| $\gamma$ | 回报折扣因子 | 定义未来奖励的权重 |
| $\lambda$（GAE） | 多步估计的衰减参数 | 调节 TD 误差向前传播的范围 |
| $\alpha$ | 学习率 | 控制每次更新的步长 |
| $\epsilon$ | PPO 概率比裁剪宽度 | 决定代理目标在哪里进入平段 |
| $\varepsilon_{\mathrm{num}}$ | 数值稳定小量 | GRPO 标准化时防止除零 |
| $\rho$ | 当前策略与采样旧策略的动作概率比 | 在旧数据上构造代理目标 |
| $\beta$ | 参考 KL 强度、DPO 中对应的系数 | 连接奖励优化与参考策略 |
| $\pi_{\mathrm{old}}$ | 本轮采样策略 | 每轮刷新，用于概率比 |
| $\pi_{\mathrm{ref}}$ | 参考行为分布 | 通常在一个训练阶段保持固定，用于正则化 |
| $\theta,\phi,\psi$ | Actor、Critic、reward model 参数 | 分别学习行动、预测回报与评价结果 |

## 附录 C：组均值基线的一个细节

固定 prompt，独立采样 $G$ 个回答，令 $g_i=\nabla\log\pi(y_i)$，单个奖励为 $R_i$，真实梯度为 $g=\mathbb E[R_i g_i]$。因为 $\mathbb E[g_i]=0$，且 $j\neq i$ 时 $R_j$ 与 $g_i$ 独立，

$$
\mathbb E\left[\left(R_i-\frac1G\sum_jR_j\right)g_i\right]
=\left(1-\frac1G\right)g.
$$

如果改用 $b_{-i}=\frac1{G-1}\sum_{j\neq i}R_j$，则 $\mathbb E[(R_i-b_{-i})g_i]=g$。前一种做法把自己也放进均值，梯度期望缩小了 $1/G$；后一种只用其他回答作参照，恢复了原来的期望梯度。

这个结果帮助我们单独看清“减去组均值”的作用。进一步除以组标准差，会改变不同组的相对权重；裁剪与长度归一化则分别改变更新幅度和各条回答的贡献。分析完整的 GRPO 目标时，可以按这个顺序逐项理解。

## 附录 D：带答案的理解练习

**1. 折扣改变选择。** 在两状态例子中，粗稿坚持完善的价值何时高于立即提交的 $2$？

答案：$V(s_0)=(-1+6.4\gamma)/(1-0.2\gamma)$。对 $0\leq\gamma<1$，分母为正；比较得到 $\gamma>3/6.8\approx0.441176$。等号时两者相同。折扣较大时，继续完善带来的未来收益才值得当前这一步成本。

**2. 终止与截断。** 若一步奖励为 $1$，下一状态估计价值为 $10$，$\gamma=0.9$，真实终止和采样截断的 TD 目标分别是多少？

答案：真实终止为 $1$；底层任务继续但采样停止时为 $1+0.9\times10=10$。若时间上限本身就是任务终点，则应按真实终止处理。

**3. PPO 的负优势。** $A=-2,\epsilon=0.2,\rho=1.5$，代理项是多少？是否被截成 $-2.4$？

答案：$\min(-3,-2.4)=-3$。坏动作的概率反而提高，仍应惩罚；裁剪不是对所有方向都置平。

**4. GRPO 全错。** 一组四个回答都得零分，还会更新参数吗？

答案：基本组内终局 advantage 全零，奖励驱动项没有梯度；但 KL、熵或其他训练项仍可能更新。因此观察训练时，可以把任务奖励项和正则项分开看。

**5. 一个 token 的 log-ratio 为负，KL 公式错了吗？**

答案：没有。采样量 $\log\pi_\theta(a\mid s)-\log\pi_{\mathrm{ref}}(a\mid s)$ 可以为负；在 $a\sim\pi_\theta$ 下求完整期望才是非负 KL。

**6. 去掉 Critic 是否意味着 GRPO 不需要评价？**

答案：仍需奖励模型、规则验证器或其他评价。去掉的是一个拟合前缀未来回报的价值网络，不是评价回答好坏的机制。

**7. 用优质回答做 SFT 与 DPO 有何不同？**

答案：SFT 提高示范 log-probability；DPO 使用同题胜负回答及参考策略，优化相对概率比的差。只保留赢家再 SFT 会丢失比较信息，也不是 DPO 损失的等价实现。

## 附录 E：可运行的小实验

随讲义提供 [examples/rl_toy_lab.py](examples/rl_toy_lab.py)，只使用 Python 标准库。在本讲义目录运行：

```bash
python examples/rl_toy_lab.py
```

它会计算并校验：两状态 MDP 的价值迭代与解析解、TD 单步更新、策略梯度的有限差分、baseline 的期望与方差、GAE、PPO 正负 advantage、DPO 损失与导数、GRPO 组内标准化，以及 KL 正则化 bandit 的最优策略。

最后一个实验只含两种回答：A 奖励 $1$，B 奖励 $0$，参考策略各占 $0.5$。取 $\beta=0.5$，理想最优策略为

$$
\pi^*(A)=\frac{e^{1/\beta}}{e^{1/\beta}+1}
=\sigma(2)\approx0.880797.
$$

它没有把全部概率压到 A，因为 KL 正则为偏离参考策略收取代价。脚本在这个可完全求解的目标上执行梯度上升，并与解析最优解比较。这样可以把“KL 系数改变目标，梯度更新逐渐接近目标”直接画出来。

![可求解的 KL 正则化小实验](images/15_kl-bandit-experiment.svg)

*图 15：曲线来自配套脚本的实际数值迭代。固定奖励下，增加正则强度使策略更接近参考分布；训练轨迹应向对应的解析最优值收敛。*

最简化的核心更新如下，其中 $\theta$ 是 A 相对 B 的 logit，$p=\sigma(\theta)$：

```python
from math import exp

theta, beta, learning_rate = 0.0, 0.5, 0.2
for _ in range(1000):
    p = 1.0 / (1.0 + exp(-theta))
    # J = p - beta * KL(Bernoulli(p) || Bernoulli(0.5))
    grad = p * (1.0 - p) * (1.0 - beta * theta)
    theta += learning_rate * grad
print(1.0 / (1.0 + exp(-theta)))  # 接近 0.880797
```

这段代码直接计算完整期望梯度，因此没有 Monte Carlo 采样噪声。把它与第 9 节的单样本梯度对比，可以清楚看到：优化目标、精确梯度与采样估计，是三个不同层次。

## 参考阅读与使用说明

基础部分的系统教材是 Sutton 与 Barto 的 [Reinforcement Learning: An Introduction, 2nd edition](http://incompleteideas.net/book/the-book-2nd.html)。本讲义的两状态任务、数值练习与可求解 bandit 为独立构造，用于把定义、推导和程序结果联系起来。

经典算法建议依次阅读 [DQN](https://www.nature.com/articles/nature14236)、[Double DQN](https://arxiv.org/abs/1509.06461)、[TRPO](https://arxiv.org/abs/1502.05477)、[GAE](https://arxiv.org/abs/1506.02438) 与 [PPO](https://arxiv.org/abs/1707.06347)。想理解直接优化策略的历史，可读 Williams 的 [REINFORCE](https://doi.org/10.1007/BF00992696) 与 Sutton 等人的 [Policy Gradient Methods for Reinforcement Learning with Function Approximation](https://proceedings.neurips.cc/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html)。

大模型后训练建议把 [InstructGPT](https://arxiv.org/abs/2203.02155)、[DPO](https://arxiv.org/abs/2305.18290)、[DeepSeekMath](https://arxiv.org/abs/2402.03300) 与 [DeepSeek-R1 原始报告](https://arxiv.org/abs/2501.12948v1) 连起来读：它们分别帮助理解反馈建模、偏好重参数化、组内优势与多阶段推理训练。读第 19 节的后续研究时，可以沿着估计器、归一化与系统设计这几条线继续追问。

全部配图是本地代码生成的独立 SVG，无远程图片或字体依赖。图片、生成源码与数值实验随文档一起交付；移动或分享时保留相对目录结构即可。可打开 [插图预览.html](插图预览.html) 逐张放大查看；生成与校验步骤见 [README.md](README.md)。
