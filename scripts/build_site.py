#!/usr/bin/env python3
"""Build the GitHub Pages site into _site/.

Source layout:
    courses/<course>/**/*.html

For every HTML file this builder:
1. Copies the live demo into _site/ with the same relative path.
2. Generates a sibling "<name>.src.html" page showing escaped source code.
3. Copies non-HTML assets next to their source pages.
4. Generates a hierarchical index grouped as Course -> Topic -> Page.

A "topic" is the HTML file's parent directory relative to the course root.
Files placed directly under courses/<course>/ are grouped under "General".
"""
import html
import re
import shutil
import sys
from collections import defaultdict
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
:root{{--border:#d8dee4;--muted:#667085;--panel:#f7f9fc;--link:#0969da}}
body{{font-family:system-ui,"Noto Sans TC",sans-serif;max-width:980px;margin:2rem auto;padding:0 1rem;line-height:1.6;color:#1f2328}}
h1{{margin-bottom:1.5rem}}
h2{{border-bottom:2px solid var(--border);padding-bottom:.35rem;margin-top:2.4rem}}
h3{{margin:1.35rem 0 .45rem;padding:.45rem .7rem;background:var(--panel);border-left:4px solid #8c959f;border-radius:4px}}
.topic-path{{font-size:.8em;color:var(--muted);font-weight:500;margin-left:.5rem}}
ul{{margin-top:.35rem}}
li{{margin:.42rem 0}}
a{{color:var(--link);text-decoration:none}}
a:hover{{text-decoration:underline}}
.src{{font-size:.85em;margin-left:.65rem;color:var(--muted)}}
.course-toc{{display:flex;flex-wrap:wrap;gap:.45rem .8rem;margin:.25rem 0 1rem;padding:0;list-style:none}}
.course-toc li{{margin:0}}
.course-toc a{{display:inline-block;background:var(--panel);border:1px solid var(--border);border-radius:999px;padding:.18rem .65rem}}
.empty{{color:var(--muted)}}
pre{{background:#f6f8fa;padding:1rem;overflow:auto;border-radius:6px}}
</style></head><body>{body}</body></html>
"""


def title_of(path: Path) -> str:
    m = re.search(
        r"<title[^>]*>(.*?)</title>",
        path.read_text("utf-8", "replace"),
        re.I | re.S,
    )
    return html.unescape(m.group(1).strip()) if m and m.group(1).strip() else path.stem


def href(rel: Path) -> str:
    return "/".join(quote(p) for p in rel.parts)


def topic_of(file_path: Path, course: Path) -> tuple[str, str]:
    """Return (stable topic key, human-readable label)."""
    parent = file_path.parent.relative_to(course)
    if parent == Path("."):
        return "", "General"
    parts = parent.parts
    return parent.as_posix(), " / ".join(parts)


def build_demo_and_source(f: Path) -> tuple[Path, Path]:
    rel = f.relative_to(ROOT)
    dest = OUT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, dest)

    src_rel = rel.with_suffix(".src.html")
    code = html.escape(f.read_text("utf-8", "replace"))
    back_to_index = "../" * (len(rel.parts) - 1) + "index.html"
    (OUT / src_rel).write_text(
        PAGE.format(
            title=f"原始碼 - {f.name}",
            body=(
                f'<p><a href="./{quote(f.name)}">▶ 展示</a> · '
                f'<a href="{back_to_index}">回索引</a></p>'
                f"<h1>{html.escape(f.name)}</h1>"
                f"<pre><code>{code}</code></pre>"
            ),
        ),
        "utf-8",
    )
    return rel, src_rel


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / ".nojekyll").touch()

    sections = []
    course_count = 0
    page_count = 0

    if not COURSES.exists():
        COURSES.mkdir(parents=True)

    for course in sorted(
        p for p in COURSES.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    ):
        course_count += 1
        topics = defaultdict(list)

        for f in sorted(course.rglob("*.html")):
            rel, src_rel = build_demo_and_source(f)
            topic_key, topic_label = topic_of(f, course)
            topics[topic_key].append(
                (
                    topic_label,
                    title_of(f),
                    rel,
                    src_rel,
                )
            )
            page_count += 1

        # Copy non-HTML assets (images, js, css, data, etc.) next to the pages.
        for a in course.rglob("*"):
            if a.is_file() and a.suffix.lower() != ".html":
                d = OUT / a.relative_to(ROOT)
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(a, d)

        course_html = [f'<h2 id="course-{html.escape(course.name)}">{html.escape(course.name)}</h2>']

        if not topics:
            course_html.append('<p class="empty">尚無內容。</p>')
        else:
            # Topic chips make large courses easier to scan.
            topic_links = []
            for topic_key in sorted(topics, key=lambda k: (k != "", k.lower())):
                label = topics[topic_key][0][0]
                anchor = f"{course.name}-{topic_key or 'general'}"
                topic_links.append(
                    f'<li><a href="#{quote(anchor)}">{html.escape(label)}</a></li>'
                )
            course_html.append(f'<ul class="course-toc">{"".join(topic_links)}</ul>')

            # Render Course -> Topic -> Pages.
            for topic_key in sorted(topics, key=lambda k: (k != "", k.lower())):
                entries = topics[topic_key]
                topic_label = entries[0][0]
                anchor = f"{course.name}-{topic_key or 'general'}"

                if topic_key:
                    path_note = (
                        f'<span class="topic-path">{html.escape(topic_key)}</span>'
                        if topic_label != topic_key
                        else ""
                    )
                else:
                    path_note = ""

                course_html.append(
                    f'<h3 id="{html.escape(anchor)}">{html.escape(topic_label)}{path_note}</h3>'
                )

                items = []
                for _, page_title, rel, src_rel in entries:
                    items.append(
                        f'<li><a href="{href(rel)}">{html.escape(page_title)}</a>'
                        f'<a class="src" href="{href(src_rel)}">原始碼</a></li>'
                    )
                course_html.append(f'<ul>{"".join(items)}</ul>')

        sections.append("".join(course_html))

    body = (
        "<h1>課程 HTML5 / Canvas 展示</h1>"
        + ("".join(sections) if sections else '<p class="empty">尚無內容。</p>')
    )
    (OUT / "index.html").write_text(
        PAGE.format(title="課程展示索引", body=body),
        "utf-8",
    )

    print(
        f"built {course_count} course(s), {page_count} page(s) into {OUT}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
