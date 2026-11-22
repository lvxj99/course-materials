# 1106.md 插图源码

全部插图由本目录的 Python 脚本生成（只用标准库），输出到 `../images/`。

```
python figures-src/build_all.py   # 重建全部 30 张 SVG
python figures-src/render.py      # 可选：用本机 Chrome 渲染 PNG 到 figures-src/_qa/ 检查效果
```

| 脚本 | 内容 |
|---|---|
| svgkit.py | 共用绘图工具：配色、字体、数学下标、箭头、网格、内嵌像素图 |
| figs_transformer.py | 01 原始架构、28 因果掩码、04 多头、05 位置编码/RoPE、06 Block、07 三类架构 |
| figs_attention.py | 24 注意力热图、02 Q/K/V 一次读取、03 矩阵形状 |
| figs_inference.py | 08 自回归、09 KV cache、25 合批、17 BPE、18 分词与嵌入、19 温度与 top-k/top-p |
| figs_generative.py | 10 AE、11 去噪 AE、12 MAE、13 VAE、14 GAN、15 Diffusion、16 SDE vs ODE |
| figs_llm.py | 27 RL 回路、20 训练流程、21 三类扩展、22 多模态、23 MoE、29 RAG、26 Agent、30 贝尔曼 |

配色约定：Query/生成=橙，Key/输入=蓝，Value/正确=绿，注意力/潜在=紫，FFN=青，损失/禁止=红。
图中的示例数值都在脚本里用 assert 校验；数字图像、重建结果等是手工构造的示意，未实际训练模型。
