"""一键重建讲义 1106.md 的全部插图（输出到 ../images/）。

    python figures-src/build_all.py          # 生成全部 SVG
    python figures-src/render.py             # （可选）渲染 PNG 到 figures-src/_qa/ 以便检查

只依赖 Python 3 标准库；所有示例数值都在脚本里用 assert 校验。
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = ["figs_transformer.py", "figs_attention.py", "figs_inference.py", "figs_generative.py", "figs_llm.py"]

for name in SCRIPTS:
    print("==>", name)
    subprocess.run([sys.executable, str(HERE / name)], cwd=HERE, check=True)
print("done:", len(list((HERE.parent / "images").glob("*.svg"))), "SVG files")
