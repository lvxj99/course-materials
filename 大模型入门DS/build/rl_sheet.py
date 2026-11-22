import pathlib
import subprocess

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "rl" / "images"
OUT = ROOT / "rl" / "overview.png"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
COLS, CELL = 3, 460

files = sorted(IMG.glob("*.png"))
rows = [files[i:i + COLS] for i in range(0, len(files), COLS)]
html = ["<!doctype html><meta charset='utf-8'><style>",
        "body{margin:0;background:#fff;font-family:'Segoe UI','Microsoft YaHei',sans-serif}",
        "table{border-collapse:collapse}td{padding:4px 8px 12px 4px;vertical-align:top}",
        f"img{{width:{CELL}px;border:1px solid #e6ecf2;display:block}}",
        ".n{font-size:9px;color:#7c8a97;margin-bottom:2px}",
        "</style><table>"]
total = 8
for row in rows:
    html.append("<tr>")
    hs = []
    for p in row:
        im = Image.open(p)
        h = int(CELL * im.size[1] / im.size[0])
        hs.append(h)
        html.append(f"<td><div class='n'>{p.stem}</div>"
                    f"<img src='{p.as_uri()}'></td>")
    html.append("</tr>")
    total += max(hs) + 34
html.append("</table>")

page = ROOT / "build" / ".tmp" / "rl_sheet.html"
page.write_text("".join(html), encoding="utf-8")
w = COLS * (CELL + 12) + 10
subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
                "--hide-scrollbars", "--force-device-scale-factor=1",
                f"--window-size={w},{total}",
                f"--user-data-dir={ROOT / 'build' / '.chrome'}",
                f"--screenshot={OUT}", page.as_uri()], capture_output=True)
print("sheet:", OUT, f"{w}x{total}", len(files), "figures")
