"""Render figures: build/figs/*.py -> <out>/svg/*.svg + <out>/*.png

Usage:
    python build/render.py                          # all figures -> images/
    python build/render.py 01 05 rope               # only names containing a token
    python build/render.py --svg-only
    python build/render.py --out=rl/images --modules=figs.rl_core,figs.rl_llm
"""

from __future__ import annotations

import importlib
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
TMP = BUILD / ".tmp"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
sys.path.insert(0, str(BUILD))

MODULES = ["figs.attn", "figs.pos_block", "figs.autoenc", "figs.genrl", "figs.llm", "figs.extra"]


def registry(modules=None):
    reg = {}
    for m in modules or MODULES:
        try:
            mod = importlib.import_module(m)
        except ModuleNotFoundError:
            continue
        except Exception as e:  # a half-written module must not block the others
            print(f"  !! skip {m}: {type(e).__name__}: {e}")
            continue
        reg.update(getattr(mod, "FIGURES", {}))
    return reg


def render(name, svg_text, w, h, out_dir, png=True, scale=2):
    svg_dir = out_dir / "svg"
    svg_dir.mkdir(parents=True, exist_ok=True)
    (svg_dir / f"{name}.svg").write_text(svg_text, encoding="utf-8")
    if not png:
        return
    html = TMP / f"{name}.html"
    html.write_text(
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<style>html,body{margin:0;padding:0;background:#fff;overflow:hidden}"
        "svg{display:block}</style></head><body>" + svg_text + "</body></html>",
        encoding="utf-8",
    )
    out = out_dir / f"{name}.png"
    cmd = [
        CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        "--no-first-run", "--no-default-browser-check", "--disable-sync",
        "--disable-extensions", "--disable-background-networking",
        "--disable-component-update", "--mute-audio", "--metrics-recording-only",
        "--run-all-compositor-stages-before-draw", "--virtual-time-budget=1200",
        f"--force-device-scale-factor={scale}",
        f"--window-size={w},{h}",
        f"--user-data-dir={BUILD / '.chrome'}",
        f"--screenshot={out}",
        html.resolve().as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if not out.exists():
        print(f"  !! chrome failed for {name}\n{res.stderr[-800:]}")
        return
    try:
        from PIL import Image

        im = Image.open(out)
        expect = (w * scale, h * scale)
        if im.size != expect:
            im.crop((0, 0, expect[0], expect[1])).save(out)
            im = Image.open(out)
        print(f"  png {out.name}  {im.size[0]}x{im.size[1]}")
    except Exception as e:  # noqa: BLE001
        print(f"  png {out.name} (size check skipped: {e})")


def main(argv):
    svg_only = "--svg-only" in argv
    out_dir = ROOT / "images"
    modules = MODULES
    tokens = []
    for a in argv[1:]:
        if a.startswith("--out="):
            out_dir = ROOT / a.split("=", 1)[1]
        elif a.startswith("--modules="):
            modules = [m.strip() for m in a.split("=", 1)[1].split(",") if m.strip()]
        elif a.startswith("--"):
            continue
        else:
            tokens.append(a)
    out_dir.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    reg = registry(modules)
    if not reg:
        print("no figures registered")
        return 1
    names = [n for n in sorted(reg) if not tokens or any(t in n for t in tokens)]
    t0 = time.time()
    print(f"rendering {len(names)} figure(s) -> {out_dir}")
    for n in names:
        c = reg[n]()
        print(f"- {n}  {c.w}x{c.h}")
        render(n, c.svg(), c.w, c.h, out_dir, png=not svg_only)
    print(f"done in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
