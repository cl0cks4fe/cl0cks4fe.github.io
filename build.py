import re, shutil
from pathlib import Path
from datetime import datetime

TITLE   = "the city and the tower"
AUTHOR  = "cl0cks4fe"
FOOTER  = '<a href="mailto:{email}">{email}</a>'.format(email="cl0cks4fe@gmail.com")
OUT     = Path("_site")

PAGE = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE}</title><link rel="stylesheet" href="{{r}}style.css"></head>
<body><header><a href="{{r}}">{{title}}</a></header><main>{{body}}</main>
<footer>{FOOTER}</footer></body></html>"""

def parse(path):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', path.read_text(), re.S)
    if not m: raise ValueError(f"invalid format: {path}")
    meta = dict(re.findall(r'(\w+):\s*(.+)', m.group(1)))
    meta["slug"] = path.stem
    slug = re.sub(r'^\d{4}-\d{2}-\d{2}-?', '', meta["slug"]) or meta["slug"]
    dt = datetime.strptime(meta["date"], "%Y-%m-%d")
    meta["fdate"] = dt.strftime("%b %d, %Y")
    meta["href"] = f'{dt.year}/{dt.month:02d}/{dt.day:02d}/{slug}.html'
    return meta, m.group(2)

def md(t):
    t = re.sub(r'^```(\w*)\n(.*?)^```', lambda m: f'<pre><code>{m.group(2).replace("<","&lt;")}</code></pre>', t, flags=re.M|re.S)
    t = re.sub(r'^(?:> .+\n?)+', lambda m: f'<blockquote>{re.sub(r"^> ","",m.group(),flags=re.M).strip()}</blockquote>', t, flags=re.M)
    for n in (4,3,2,1): t = re.sub(rf'^{"#"*n} (.+)$', rf'<h{n}>\1</h{n}>', t, flags=re.M)
    for p, r in [(r'\*\*(.+?)\*\*', r'<strong>\1</strong>'), (r'\*(.+?)\*', r'<em>\1</em>'),
                 (r'`(.+?)`', r'<code>\1</code>'), (r'!\[([^\]]*)\]\((.+?)\)', r'<img src="\2" alt="\1">'),
                 (r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>')]: t = re.sub(p, r, t)
    t = re.sub(r'^- (.+)$', r'<li>\1</li>', t, flags=re.M)
    t = re.sub(r'(<li>.*?</li>\n?)+', lambda m: f'<ul>{m.group()}</ul>', t, flags=re.S)
    return "\n".join(f'<p>{b}</p>' if not b.startswith('<') else b for b in t.split("\n\n") if b.strip())

def build():
    shutil.rmtree(OUT, True); OUT.mkdir()
    shutil.copy("style.css", OUT/"style.css")
    for d in [Path("static")]:
        if d.is_dir(): shutil.copytree(d, OUT/d.name)

    posts = sorted([parse(f) for f in Path("posts").rglob("*.md")], key=lambda x: x[0]["date"], reverse=True)

    for m, body in posts:
        out_file = OUT / m["href"]
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(PAGE.format(
            title=TITLE,
            body=f'<article><h1>{m["title"]}</h1><time>{m["fdate"]}</time>{md(body)}</article>',
            r="../" * (len(out_file.relative_to(OUT).parts) - 1)))
        print(f"  {m['href']}")

    links = "\n".join(f'<li><a href="{m["href"]}">{m["title"]}</a><time>{m["fdate"]}</time></li>' for m,_ in posts)
    (OUT/"index.html").write_text(PAGE.format(title=TITLE, body=f"<ul class='posts'>{links}</ul>", r=""))
    print(f"  {len(posts)} posts → {OUT}/")

if __name__ == "__main__":
    build()
