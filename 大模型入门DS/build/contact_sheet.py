"""Build one contact sheet of every figure for a quick consistency review."""

from __future__ import annotations

import pathlib
import subprocess

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
COLS = 3
CELL = 460


def main():
    files = sorted(p for p in IMG.glob("*.png") if not p.name.startswith("tmp_"))
    sized = []
    for p in files:
        im = Image.open(p)
        sized.append((p, int(CELL * im.size[1] / im.size[0])))

    rows = [sized[i:i + COLS] for i in range(0, len(sized), COLS)]
    html = ["<!doctype html><meta charset='utf-8'><style>",
            "body{margin:0;background:#fff;font-family:'Segoe UI','Microsoft YaHei',sans-serif}",
            "table{border-collapse:collapse}",
            "td{padding:4px 8px 12px 4px;vertical-align:top}",
            f"img{{width:{CELL}px;border:1px solid #e6ecf2;display:block}}",
            ".n{font-size:9px;color:#7c8a97;margin-bottom:2px}",
            "</style><table>"]
    total_h = 8
    for row in rows:
        html.append("<tr>")
        for p, h in row:
            html.append(f"<td><div class='n'>{p.stem}</div>"
                        f"<img src='{p.as_uri()}'></td>")
        html.append("</tr>")
        total_h += max(h for _, h in row) + 34
    html.append("</table>")

    page = ROOT / "build" / ".tmp" / "sheet.html"
    page.write_text("".join(html), encoding="utf-8")
    w = COLS * (CELL + 12) + 10
    out = ROOT / "build" / ".tmp" / "sheet.png"
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={w},{total_h}",
                    f"--user-data-dir={ROOT / 'build' / '.chrome'}",
                    f"--screenshot={out}", page.as_uri()], capture_output=True)
    print("sheet:", out, f"{w}x{total_h}", len(files), "figures")


if __name__ == "__main__":
    main()
