#!/usr/bin/env python3
import re, shutil
from pathlib import Path
from datetime import datetime

TITLE   = "the city and the tower"
AUTHOR  = "cl0cks4fe"
EMAIL   = "cl0cks4fe@gmail.com"
FOOTER  = '<a href="mailto:{email}">{email}</a>'.format(email=EMAIL)
OUT     = Path("_site")
DATEFMT = "%b %d, %Y"

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><link rel="stylesheet" href="{r}style.css"></head>
<body><header><a href="{r}">{site}</a></header><main>{body}</main>
<footer>{footer}</footer></body></html>"""

def parse(path):
    text = path.read_text(); m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.S)
    meta = dict(re.findall(r'(\w+):\s*(.+)', m.group(1))) if m else {}
    meta |= {"slug": path.stem, "date": meta.get("date", "2000-01-01")}
    meta.setdefault("title", meta["slug"].replace("-", " ").title())
    return meta, (m.group(2) if m else text)

def md(t):
    t = re.sub(r'^```(\w*)\n(.*?)^```', lambda m: f'<pre><code>{m.group(2).replace("<","&lt;")}</code></pre>', t, flags=re.M|re.S)
    t = re.sub(r'^(?:> .+\n?)+', lambda m: f'<blockquote><p>{re.sub(r"^> ","",m.group(),flags=re.M).strip()}</p></blockquote>', t, flags=re.M)
    for n in (4,3,2,1): t = re.sub(rf'^{"#"*n} (.+)$', rf'<h{n}>\1</h{n}>', t, flags=re.M)
    t = re.sub(r'^---+$', '<hr>', t, flags=re.M)
    for p, r in [(r'\*\*(.+?)\*\*', r'<strong>\1</strong>'), (r'\*(.+?)\*', r'<em>\1</em>'),
                 (r'`(.+?)`', r'<code>\1</code>'), (r'!\[([^\]]*)\]\((.+?)\)', r'<img src="\2" alt="\1">'),
                 (r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>')]: t = re.sub(p, r, t)
    t = re.sub(r'^- (.+)$', r'<li>\1</li>', t, flags=re.M)
    t = re.sub(r'(<li>.*?</li>\n?)+', lambda m: f'<ul>{m.group()}</ul>', t, flags=re.S)
    return "\n".join(f'<p>{b}</p>' if not b.startswith('<') else b for b in t.split("\n\n") if b.strip())

def render(title, body, root=""):
    fdate = lambda d: datetime.strptime(d,"%Y-%m-%d").strftime(DATEFMT)
    tab = TITLE if title == TITLE else f"{title} — {TITLE}"
    return PAGE.format(title=tab, site=TITLE, body=body, r=root,
                        footer=FOOTER, y=datetime.now().year, author=AUTHOR)

def build():
    shutil.rmtree(OUT, True); OUT.mkdir(); (OUT/"posts").mkdir()
    shutil.copy("style.css", OUT/"style.css")
    for d in [Path("static")]:
        if d.is_dir(): shutil.copytree(d, OUT/d.name)

    posts = sorted([parse(f) for f in Path("posts").glob("*.md")], key=lambda x: x[0]["date"], reverse=True)
    fdate = lambda d: datetime.strptime(d, "%Y-%m-%d").strftime(DATEFMT)
    for m, body in posts:
        print('!',m)
        html = f'<article><h1>{m["title"]}</h1><time>{fdate(m["date"])}</time>{md(body)}</article>'
        (OUT/f'posts/{m["slug"]}.html').write_text(render(m["title"], html, "../"))
        print(f"  posts/{m['slug']}.html")

    links = "\n".join(f'<li><a href="posts/{m["slug"]}.html">{m["title"]}</a><time>{fdate(m["date"])}</time></li>' for m,_ in posts)
    (OUT/"index.html").write_text(render(TITLE, f"<ul class='posts'>{links}</ul>" if posts else "<p>Nothing here</p>"))
    print(f"  index.html\n\n✓ {len(posts)} posts → {OUT}/")

if __name__ == "__main__":
    build()
