#!/usr/bin/env python3
"""Build the GitHub Pages site into _site/.

courses/<course>/**/*.html  ->  copied as-is (the live demo), plus a
"<name>.src.html" page that shows the escaped source code, plus a generated
index.html listing every course and its demos.
"""
import html
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / "courses"
OUT = ROOT / "_site"

PAGE = """<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
body{{font-family:system-ui,"Noto Sans TC",sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;line-height:1.6}}
h2{{border-bottom:2px solid #ddd;padding-bottom:.3rem;margin-top:2rem}}
li{{margin:.4rem 0}} .src{{font-size:.85em;margin-left:.6rem}}
pre{{background:#f6f8fa;padding:1rem;overflow:auto;border-radius:6px}}
</style></head><body>{body}</body></html>
"""


def title_of(path: Path) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", path.read_text("utf-8", "replace"), re.I | re.S)
    return html.unescape(m.group(1).strip()) if m and m.group(1).strip() else path.stem


def href(rel: Path) -> str:
    return "/".join(quote(p) for p in rel.parts)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / ".nojekyll").touch()
    sections = []
    for course in sorted(p for p in COURSES.iterdir() if p.is_dir() and not p.name.startswith(".")):
        items = []
        for f in sorted(course.rglob("*.html")):
            rel = f.relative_to(ROOT)
            dest = OUT / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            src_rel = rel.with_suffix(".src.html")
            code = html.escape(f.read_text("utf-8", "replace"))
            (OUT / src_rel).write_text(PAGE.format(
                title=f"原始碼 - {f.name}",
                body=f'<p><a href="./{quote(f.name)}">▶ 展示</a> · <a href="{"../" * (len(rel.parts) - 1)}index.html">回索引</a></p><h1>{html.escape(f.name)}</h1><pre><code>{code}</code></pre>'),
                "utf-8")
            items.append(f'<li><a href="{href(rel)}">{html.escape(title_of(f))}</a>'
                         f'<a class="src" href="{href(src_rel)}">原始碼</a></li>')
        # copy non-HTML assets (images, js, css) next to the pages
        for a in course.rglob("*"):
            if a.is_file() and a.suffix.lower() != ".html":
                d = OUT / a.relative_to(ROOT)
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(a, d)
        if items:
            sections.append(f"<h2>{html.escape(course.name)}</h2><ul>{''.join(items)}</ul>")
    body = "<h1>課程 HTML5 / Canvas 展示</h1>" + ("".join(sections) or "<p>尚無內容。</p>")
    (OUT / "index.html").write_text(PAGE.format(title="課程展示索引", body=body), "utf-8")
    print(f"built {len(sections)} course(s) into {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
