"""把 images/ 下的 SVG 用无头 Chrome 渲染成 PNG（仅用于检查效果）。

用法：python figures-src/render.py [文件名关键字 ...]
输出：figures-src/_qa/*.png
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "images"
QA = Path(__file__).resolve().parent / "_qa"
CHROMES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def main():
    QA.mkdir(exist_ok=True)
    chrome = next(c for c in CHROMES if Path(c).exists())
    keys = sys.argv[1:]
    for svg in sorted(IMG.glob("*.svg")):
        if keys and not any(k in svg.name for k in keys):
            continue
        head = svg.read_text(encoding="utf-8")[:400]
        m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', head)
        w, h = int(float(m.group(1))), int(float(m.group(2)))
        out = QA / (svg.stem + ".png")
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={w},{h}", "--force-device-scale-factor=1",
                        f"--screenshot={out}", svg.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("rendered", out.name, f"{w}x{h}")


if __name__ == "__main__":
    main()
