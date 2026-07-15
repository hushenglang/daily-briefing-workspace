#!/usr/bin/env python3
"""Generate a GitHub Pages index for every HTML file in this directory."""

from __future__ import annotations

import html
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"


def extract(pattern: str, source: str, fallback: str) -> str:
    match = re.search(pattern, source, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return fallback
    value = re.sub(r"<[^>]+>", "", match.group(1))
    return html.unescape(re.sub(r"\s+", " ", value)).strip()


def page_info(path: Path) -> dict[str, str]:
    source = path.read_text(encoding="utf-8")
    title = extract(r"<title[^>]*>(.*?)</title>", source, path.stem)
    summary = extract(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
        source,
        "",
    ) or extract(r'<p[^>]+class=["\'][^"\']*deck[^"\']*["\'][^>]*>(.*?)</p>', source, "点击查看完整内容")
    date_match = re.search(r"(20\d{2})[-_](\d{2})[-_](\d{2})", path.name)
    date = "-".join(date_match.groups()) if date_match else ""
    return {"file": path.name, "title": title, "summary": summary, "date": date}


def render() -> str:
    pages = [page_info(path) for path in ROOT.glob("*.html") if path.name != INDEX.name]
    pages.sort(key=lambda item: (item["date"], item["file"]), reverse=True)

    cards = "\n".join(
        f'''      <article class="card">
        <div class="date">{html.escape(page["date"] or "HTML 页面")}</div>
        <h2>{html.escape(page["title"])}</h2>
        <p>{html.escape(page["summary"])}</p>
        <a href="{html.escape(page["file"], quote=True)}">阅读简报 <span aria-hidden="true">→</span></a>
      </article>'''
        for page in pages
    ) or '      <p class="empty">暂时还没有可展示的 HTML 页面。</p>'

    updated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    return f'''<!doctype html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="AI 新闻简报归档">
  <title>AI 新闻简报归档</title>
  <style>
    :root {{ color-scheme: light; --ink: #172033; --muted: #687386; --line: #dfe4eb; --paper: #f4f6f9; --accent: #3157d5; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: var(--ink); background: var(--paper); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    main {{ width: min(1080px, calc(100% - 32px)); margin: 0 auto; padding: 72px 0 88px; }}
    header {{ max-width: 760px; margin-bottom: 42px; }}
    .eyebrow, .date {{ color: var(--accent); font-size: .78rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }}
    h1 {{ margin: 10px 0 14px; font-size: clamp(2.4rem, 7vw, 5.4rem); line-height: .98; letter-spacing: -.055em; }}
    header p {{ margin: 0; color: var(--muted); font-size: 1.08rem; line-height: 1.7; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 310px), 1fr)); gap: 18px; }}
    .card {{ display: flex; min-height: 280px; flex-direction: column; padding: 26px; border: 1px solid var(--line); border-radius: 18px; background: #fff; box-shadow: 0 10px 30px rgba(23, 32, 51, .05); transition: transform .2s ease, box-shadow .2s ease; }}
    .card:hover {{ transform: translateY(-3px); box-shadow: 0 16px 38px rgba(23, 32, 51, .09); }}
    h2 {{ margin: 18px 0 12px; font-size: 1.45rem; line-height: 1.25; letter-spacing: -.025em; }}
    .card p {{ display: -webkit-box; margin: 0 0 24px; overflow: hidden; color: var(--muted); line-height: 1.65; -webkit-box-orient: vertical; -webkit-line-clamp: 4; }}
    .card a {{ margin-top: auto; color: var(--accent); font-weight: 700; text-decoration: none; }}
    footer {{ margin-top: 36px; color: var(--muted); font-size: .82rem; }}
    .empty {{ color: var(--muted); }}
    @media (max-width: 560px) {{ main {{ padding-top: 46px; }} .card {{ min-height: 250px; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="eyebrow">Daily Intelligence Archive</div>
      <h1>AI 新闻简报</h1>
      <p>按日期浏览已发布的每日简报，最新一期排在最前。</p>
    </header>
    <section class="grid" aria-label="简报列表">
{cards}
    </section>
    <footer>共 {len(pages)} 期 · 首页生成于 {html.escape(updated)}</footer>
  </main>
</body>
</html>
'''


if __name__ == "__main__":
    INDEX.write_text(render(), encoding="utf-8")
    print(f"Generated {INDEX.name}")
