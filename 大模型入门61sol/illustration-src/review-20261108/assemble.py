from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parent.parent / '强化学习拓展'
original = (here / '强化学习.before-peer-review.md').read_bytes()
newline = '\r\n' if b'\r\n' in original else '\n'
parts = ['rl-intro.md', 'rl-ch01-08.md', 'rl-ch09-13.md', 'rl-ch14-20.md', 'rl-appendices.md']
text = '\n\n'.join((here / part).read_text(encoding='utf-8').strip() for part in parts) + '\n'
text = text.replace('第 6.4 节对终止和截断的区分', '第 6.5 节对终止和截断的区分')
destination = root / '强化学习_从序贯决策到大模型后训练.md'
destination.write_bytes(text.replace('\n', newline).encode('utf-8'))
print(f'Assembled {len(text)} characters; newline={newline!r}')
