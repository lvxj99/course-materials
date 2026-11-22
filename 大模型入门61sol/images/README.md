# 《大模型入门》代码插图

已补全 27 个原始占位，新增 28（因果掩码）、29（RAG）、30（贝尔曼递推）。保留原文件名主体，引用改为 SVG。

- 讲义：../1106.md
- 离线浏览与两个交互实验：../插图预览.html
- 生成源码：../illustration-src/
- 修改前原稿：../illustration-src/1106.before-illustrations.md
- 清单、图解、来源与示意边界：manifest.json
- 验证结果：validation.json；浏览器检查：../illustration-src/qa/browser-validation.json

## 重建

需要 Node.js 20 或更新版本，不需要 npm 包：

```powershell
node illustration-src/build.mjs
node illustration-src/validate.mjs
```

第一次替换原稿引用使用 `node illustration-src/build.mjs --update-markdown`；重复执行是幂等的。生成器只修改明确匹配的图片引用、图解、三处新增图，以及与配图紧密相关的少量科学表述。原稿 UTF-8 与 CRLF 换行保持不变。

## 视觉约定

白底、细线、充足留白，深灰正文，青色表示主要信息流，蓝色表示读取或输入侧，橙色表示生成、损失或反馈。字体使用系统中文与无衬线字体；SVG 有独立 title/desc、嵌入样式，无外部图像、字体、脚本依赖。可直接插入 Markdown，亦可在支持 SVG 的演示软件中使用。不同系统字体替代可能略微改变字宽。

## 可信边界

热图、MoE 路由与贝尔曼例子是可核算的教学数值，不是某个模型内部测量。数字图案由解析笔画与伪随机噪声绘制，未运行 AE、VAE、GAN、Diffusion 训练；曲线与路径为概念示意。批处理曲线由公开写出的简化成本模型计算，不能用于设备或服务性能预测。温度分布、权重归一化、矩阵形状、BPE 合并计数和缓存容量均有程序校验。

## 图文科学修订

1. 为纯注意力的排列等变性补充无位置编码、无固定掩码条件，区分等变与不变。
2. 区分扩散的闭式边缘采样、离散链和连续时间 SDE。
3. 说明概率流 ODE 的相同边缘分布结论依赖精确 score 与理想求解；FM 不等于把随机轨迹拉直。
4. 统一强化学习交互中的奖励下标为 rₜ₊₁。

2026-11-08 对照两份配套材料更新讲义：补充 top-k/top-p、GQA、LoRA、上下文预算与 Flow Matching 的具体例子，重写若干算法衔接，修复表格和附录编号。修订前版本另存于 ../illustration-src/1106.before-peer-review-20261108.md。校验脚本继续检查原有公式、图文链接和教学计算，并允许讲义正文持续修订。

## 插图清单

| 编号 | 文件 | 内容 |
|---|---|---|
| 1 | [01_original-transformer-architecture.svg](01_original-transformer-architecture.svg) | Transformer：两条序列，三种注意力 |
| 24 | [24_self-attention-score-heatmap.svg](24_self-attention-score-heatmap.svg) | 自注意力热图：一行就是一次读取 |
| 2 | [02_self-attention-query-key-value.svg](02_self-attention-query-key-value.svg) | 一次注意力读取：先匹配，再汇总 |
| 3 | [03_scaled-dot-product-attention-matrices.svg](03_scaled-dot-product-attention-matrices.svg) | 把每个位置的读取，合成矩阵运算 |
| 28 | [28_causal-mask-and-shifted-targets.svg](28_causal-mask-and-shifted-targets.svg) | 因果掩码：并行计算，也不会偷看答案 |
| 4 | [04_scaled-dot-product-and-multi-head-attention.svg](04_scaled-dot-product-and-multi-head-attention.svg) | 多头注意力：并行读取，再混合 |
| 5 | [05_positional-encoding-and-rope.svg](05_positional-encoding-and-rope.svg) | 位置如何进入模型：相加，或旋转 |
| 6 | [06_transformer-block-residual-norm.svg](06_transformer-block-residual-norm.svg) | 一个 Pre-Norm Block 的两次残差更新 |
| 7 | [07_transformer-architectures-encoder-decoder.svg](07_transformer-architectures-encoder-decoder.svg) | 三类 Transformer：信息能流向哪里？ |
| 8 | [08_autoregressive-generation.svg](08_autoregressive-generation.svg) | 自回归生成：把刚选出的 token 接回去 |
| 9 | [09_parallel-processing-and-kv-cache.svg](09_parallel-processing-and-kv-cache.svg) | Prefill 与 Decode：历史 K、V 可以复用 |
| 25 | [25_batching-throughput-latency.svg](25_batching-throughput-latency.svg) | 合批的权衡：总吞吐与单请求延迟 |
| 10 | [10_autoencoder-reconstruction.svg](10_autoencoder-reconstruction.svg) | Autoencoder：用一个瓶颈，重建整个输入 |
| 11 | [11_denoising-autoencoder.svg](11_denoising-autoencoder.svg) | 去噪自编码器：输入受扰动，目标保持干净 |
| 12 | [12_masked-autoencoder-mae.svg](12_masked-autoencoder-mae.svg) | MAE：只编码可见部分，再补全被遮住的内容 |
| 13 | [13_vae-latent-sampling.svg](13_vae-latent-sampling.svg) | VAE：编码成分布，再通过采样解码 |
| 14 | [14_gan-generator-discriminator.svg](14_gan-generator-discriminator.svg) | GAN：判别来源，也把梯度传回生成器 |
| 15 | [15_diffusion-forward-reverse-process.svg](15_diffusion-forward-reverse-process.svg) | Diffusion：训练学去噪，生成走反向采样 |
| 16 | [16_flow-matching-vs-diffusion.svg](16_flow-matching-vs-diffusion.svg) | Diffusion 与 Flow Matching：比较路径，也比较训练目标 |
| 27 | [27_agent-environment-reinforcement-loop.svg](27_agent-environment-reinforcement-loop.svg) | 强化学习：动作改变环境，反馈改变策略 |
| 17 | [17_bpe-tokenization.svg](17_bpe-tokenization.svg) | BPE：统计相邻符号对，逐轮合并 |
| 18 | [18_tokenization-and-embedding.svg](18_tokenization-and-embedding.svg) | 从文字到向量：token id 是查表索引 |
| 19 | [19_temperature-next-token-distribution.svg](19_temperature-next-token-distribution.svg) | 温度：同一组 logits，不同的概率集中程度 |
| 20 | [20_training-to-usage-workflow.svg](20_training-to-usage-workflow.svg) | 从预训练到使用：区分数据、信号与参数更新 |
| 21 | [21_three-scaling-laws.svg](21_three-scaling-laws.svg) | 扩展能力的三处计算预算 |
| 22 | [22_multimodal-model-architecture.svg](22_multimodal-model-architecture.svg) | 多模态：把不同输入接到同一语言模型 |
| 23 | [23_mixture-of-experts-layer.svg](23_mixture-of-experts-layer.svg) | MoE：每个 token 只调用少数专家 |
| 29 | [29_rag-retrieval-evidence-generation.svg](29_rag-retrieval-evidence-generation.svg) | RAG：先找到证据，再带着证据回答 |
| 26 | [26_agent-iterative-cycle.svg](26_agent-iterative-cycle.svg) | Agent：让工具结果决定下一步 |
| 30 | [30_bellman-backup-example.svg](30_bellman-backup-example.svg) | 贝尔曼递推：眼前奖励 + 下一状态价值 |
