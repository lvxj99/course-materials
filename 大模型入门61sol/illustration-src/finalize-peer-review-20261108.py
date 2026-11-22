from pathlib import Path

root = Path(__file__).resolve().parents[1]
builder = root / 'illustration-src/build.mjs'
data = builder.read_text(encoding='utf-8')
before = '其余正文保留。本文是插图制作，不包含对原稿中所有最新产品、价格、型号或参数声明的全面事实审计。'
after = '2026-11-08 对照两份配套材料更新讲义：补充 top-k/top-p、GQA、LoRA、上下文预算与 Flow Matching 的具体例子，重写若干算法衔接，修复表格和附录编号。修订前版本另存于 ../illustration-src/1106.before-peer-review-20261108.md。校验脚本继续检查原有公式、图文链接和教学计算，并允许讲义正文持续修订。'
assert data.count(before) == 1
data = data.replace(before, after)
builder.write_bytes(data.encode('utf-8'))

md = root / '1106.md'
b = md.read_bytes()
old = '生成过程就很清楚了：**从先验采样一个新的潜在向量，再通过解码器得到样本**：'.encode()
new = '生成过程就很清楚了：**从先验采样一个新的潜在向量，再通过解码器得到样本**。也就是'.encode()
assert b.count(old) == 1
b = b.replace(old, new)
old = '梯度消失：判别器过强时，生成器几乎得不到有效梯度，无法继续学习。'.encode()
new = '梯度变弱：在某些损失设计下，判别器把生成样本判得过于确定，会让生成器难以得到有效的改进信号。'.encode()
assert b.count(old) == 1
b = b.replace(old, new)
md.write_bytes(b)
print('Updated generator notes and final wording.')
