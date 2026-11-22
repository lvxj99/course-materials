"""Rasterize lecture SVGs with headless Chrome for visual checks."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"
PREVIEW = Path(__file__).resolve().parent / "_preview"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")


def main() -> None:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    key = sys.argv[1] if len(sys.argv) > 1 else ""
    svgs = [p for p in sorted(IMAGES.glob("*.svg")) if key in p.name]
    for svg in svgs:
        text = svg.read_text(encoding="utf-8")
        match = re.search(r'width="(\d+)" height="(\d+)"', text)
        if not match:
            raise SystemExit(f"no size in {svg.name}")
        w, h = int(match.group(1)), int(match.group(2))
        html = PREVIEW / f"{svg.stem}.html"
        html.write_text(
            "<!doctype html><meta charset='utf-8'>"
            "<style>html,body{margin:0;background:#fff;overflow:hidden}</style>"
            f"<img src='../../images/{svg.name}' width='{w}' height='{h}'>",
            encoding="utf-8",
        )
        png = PREVIEW / f"{svg.stem}.png"
        url = "http://127.0.0.1:8765/figures/_preview/" + html.name
        subprocess.run(
            [
                str(CHROME),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                f"--window-size={w},{h}",
                f"--screenshot={png}",
                url,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"{svg.stem} {w}x{h}")


if __name__ == "__main__":
    main()
