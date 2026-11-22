"""Measure per-character advance widths in Chrome and cache them for figkit.

Run once (or when the font stack changes):
    <python> build/measure_font.py

Writes build/metrics.json: {"serifit": {"G": 72.3, ...}, ...} at 100 px.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CHARS = (
    "".join(chr(c) for c in range(32, 127))
    + "αβγδεζηθικλμνξοπρστυφχψω"
    + "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
    + "ΣΠ√∑×·−±≈≤≥→←↔⊕⊙‖∈ℝᵀᵏ²³¹⁰"
    + "₀₁₂₃₄₅₆₇₈₉ₜₛₖᵢⱼₙₐₑₒₓₕₗₘₚᵤᵥᵣ"
    + "ᾱεθμπσσ′…—“”‘’「」（）《》，。；：、"
)

SPECS = {
    "sans": "400 100px 'Segoe UI', sans-serif",
    "sans600": "600 100px 'Segoe UI', sans-serif",
    "serif": "400 100px 'Cambria Math', 'Times New Roman', serif",
    "serifit": "italic 400 100px 'Cambria Math', 'Times New Roman', serif",
}


def main():
    html = pathlib.Path(ROOT / ".tmp" / "measure.html")
    html.parent.mkdir(exist_ok=True)
    payload = json.dumps(CHARS, ensure_ascii=False)
    specs = json.dumps(SPECS, ensure_ascii=False)
    html.write_text(
        "<!doctype html><meta charset='utf-8'><body><pre id='out'>pending</pre>"
        "<script>\n"
        f"const chars = {payload};\n"
        f"const specs = {specs};\n"
        "const cv = document.createElement('canvas').getContext('2d');\n"
        "const out = {};\n"
        "for (const [k, f] of Object.entries(specs)) {\n"
        "  cv.font = f; out[k] = {};\n"
        "  for (const ch of chars) out[k][ch] = Math.round(cv.measureText(ch).width * 100) / 100;\n"
        "}\n"
        "document.getElementById('out').textContent = JSON.stringify(out);\n"
        "</script></body>",
        encoding="utf-8",
    )
    res = subprocess.run(
        [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--dump-dom",
         "--virtual-time-budget=1500", f"--user-data-dir={ROOT / '.chrome'}",
         html.resolve().as_uri()],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    m = re.search(r"<pre id=\"out\">(.*?)</pre>", res.stdout, re.S)
    if not m:
        raise SystemExit("measurement failed\n" + res.stderr[-1200:])
    data = json.loads(m.group(1))
    (ROOT / "metrics.json").write_text(json.dumps(data, ensure_ascii=False),
                                       encoding="utf-8")
    print("wrote build/metrics.json:", {k: len(v) for k, v in data.items()})


if __name__ == "__main__":
    main()
