# 强化学习拓展讲义

从序贯决策与 Bellman 方程，到策略梯度、PPO、RLHF、DPO、RLVR 和 GRPO。面向有机器学习基础的理工科研究生。

- 主文档：[强化学习_从序贯决策到大模型后训练.md](强化学习_从序贯决策到大模型后训练.md)
- 图册：[插图预览.html](插图预览.html)；浏览器直接打开即可，支持离线查看。
- 15 张独立 SVG：[images/](images/)
- 图片生成源码：[src/build-figures.mjs](src/build-figures.mjs)、[src/svg-core.mjs](src/svg-core.mjs)
- 数值实验：[examples/rl_toy_lab.py](examples/rl_toy_lab.py)
- 实验数据和数值检查：[examples/lab-data.json](examples/lab-data.json)
- 文档结构检查：[validation.json](validation.json)
- 浏览器图形检查：[src/qa/browser-validation.json](src/qa/browser-validation.json)

## 阅读与分享

Markdown 阅读器需要支持 LaTeX 数学公式与 SVG，例如配置了数学渲染的 VS Code Markdown 预览或其他数学 Markdown 阅读器。插图册直接用 Edge、Chrome 等浏览器打开，不需要安装运行环境。文字与 SVG 均可独立编辑。

复制整个 `强化学习拓展` 目录即可保留文档的图片和实验链接，阅读和重建都可以在这个目录内完成。

2026-11-08 修订补入了 bandit 入门、价值与优势手算、MC/TD 的奖励传播、同一经历下的 SARSA/Q-learning 对照，以及同一道题贯穿 SFT、DPO 与 GRPO 的讲解。图 4 同步加入了三步奖励传播的数值例子。

## 重现实验与重建插图

在本目录运行；Python 3.9+，Node.js 20+。这两步均只用标准库，不必安装额外包。

```bash
python examples/rl_toy_lab.py
node src/build-figures.mjs
node src/validate.cjs
```

实验脚本计算讲义中的小型 MDP、bandit 与解析公式，验证价值迭代、奖励传播、策略梯度、基线、GAE、PPO、DPO、GRPO 和 KL 正则化。`lab-data.json` 保存计算结果，图 4 和图 15 直接读取其中的数值。

## 可选浏览器检查

`src/qa.cjs` 需要 Playwright、Sharp，并使用安装好的 Microsoft Edge。它逐个渲染 SVG，检查文字越界、文字重叠、浏览器异常、图册加载与窄屏页面溢出，并输出 PNG/contact sheet。该检查不是重建或阅读的依赖。

```bash
node src/qa.cjs
```

## 配图与延伸阅读

主文档先通过小型任务建立直觉，再推导算法，最后连接大模型后训练。附录提供补充推导、符号表与带答案练习；正文中的论文链接可供进一步阅读。首次阅读可以先沿主线走完，再回头查看标为选读的估计器细节。

配图延续白底、细线、有限强调色、直接标注的 Distill 风格。颜色辅助区分信息，不是唯一编码；SVG 自带 title/desc，采用系统字体，不加载外部字体或脚本。
