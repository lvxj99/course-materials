# 插图生成流程（build/）

讲义 `1106.md` 里所有 `images/*.png` 都由本目录的脚本生成，不依赖任何绘图软件。
强化学习拓展讲义 `rl/强化学习拓展.md` 的插图同理，输出到 `rl/images/`。

## 结构

```
build/
  figkit.py          SVG 画布工具：Canvas、调色板 P、Axes、热图、矩阵、箭头、字体度量
  figs/common.py     图级助手：chips、block、tag、norm_box、panel …
  figs/attn.py       7.1–7.2：Transformer 架构、QKV、矩阵形状、多头、热图、因果掩码
  figs/pos_block.py  7.3–7.5：位置编码、Block、三类架构、自回归、KV cache、合批
  figs/autoenc.py    8.1–8.3：AE、DAE、MAE、VAE、GAN
  figs/genrl.py      8.4–8.6：Diffusion、Flow Matching、RL、seq2seq 瓶颈
  figs/llm.py        9–10：BPE、tokenization、温度、训练流程
  figs/extra.py      11 + 补充：三类扩展、多模态、MoE、Agent、RAG、top-k/p、上下文预算
  figs/rl_core.py    RL 讲义上半部分：老虎机、MDP、价值、贝尔曼、MC/TD、Q-learning、DQN、策略梯度、PPO
  figs/rl_llm.py     RL 讲义下半部分：token MDP、RLHF、DPO、GRPO、RL 对分布的影响、算法地图
  render.py          渲染入口（SVG + 2×PNG），--out / --modules 可切换输出与模块
  rl_sheet.py        RL 图的联系表（rl/overview.png）
  measure_font.py    用 Chrome 量一次字体宽度，写入 metrics.json（供 mtext 排版用）
  contact_sheet.py   把所有图拼成一张总览图，便于检查风格一致性
```

## 重新生成

```powershell
$py = "C:\Users\lvxin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
& $py build/render.py            # 全部（主讲义）
& $py build/render.py 05_ 17_    # 只渲染文件名含 05_ 或 17_ 的图
& $py build/contact_sheet.py     # 总览图 build/.tmp/sheet.png

# 强化学习讲义（输出到 rl/images，只加载 rl_* 模块）
& $py build/render.py --out=rl/images --modules=figs.rl_core,figs.rl_llm
& $py build/rl_sheet.py          # 总览图 rl/overview.png
```

`render.py` 会同时写出 `images/svg/<name>.svg`（矢量源文件）和 `images/<name>.png`
（2 倍分辨率，讲义里引用的就是它）。

## 约定

- 画布宽固定 960，白底、1 px 细线、5–6 px 圆角、低饱和填充。
- 颜色语义：蓝 = Query/编码器，橙 = Key/打分，青 = Value/输出，
  紫 = 模型/网络，红 = 损失/噪声，绿 = 奖励，slate = 数据/token。
- 图内不放标题和图注（caption 写在 Markdown 里），只用 ①②③、A/B 作分栏标签。
- 公式尽量用 Unicode 下标（ₜ ₛ ₖ ₊），比自绘排版更稳；复杂公式直接写进 Markdown 的 LaTeX。
