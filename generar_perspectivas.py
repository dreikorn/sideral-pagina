#!/usr/bin/env python3
"""
Rerunnable script that converts each article in perspectivas/add/<slug>/index.html
into a standalone article page perspectivas/<slug>.html (fully self-contained
template below) and adds a card for it (plus a JSON-LD BlogPosting entry) to
perspectivas/index.html and a <url> entry to sitemap.xml.

Usage: python3 generar_perspectivas.py
"""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ADD_DIR = ROOT / "perspectivas" / "add"
PERSP_DIR = ROOT / "perspectivas"
LISTING = ROOT / "perspectivas" / "index.html"
SITEMAP = ROOT / "sitemap.xml"
BASE_URL = "https://www.sideraltalent.com"

DOTALL = re.DOTALL

TEMPLATE_HTML = """<!DOCTYPE html>
<html lang="es-CL">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-DV1TP6ZE7R"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-DV1TP6ZE7R');
  </script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#4A7BB5">
  <meta name="author" content="Sideral Talent">
  <title>{{TITLE}} | Sideral Talent</title>
  <meta name="description" content="{{DESC}}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{{URL}}">

  <meta property="og:title" content="{{TITLE}}">
  <meta property="og:description" content="{{DESC}}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{{URL}}">
  <meta property="og:image" content="https://www.sideraltalent.com/logo-og.png">
  <meta property="og:image:alt" content="Sideral Talent">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="es_CL">
  <meta property="og:site_name" content="Sideral Talent">{{ARTICLE_META}}

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{{TITLE}} | Sideral Talent">
  <meta name="twitter:description" content="{{DESC}}">
  <meta name="twitter:image" content="https://www.sideraltalent.com/logo.png">
  <meta name="twitter:image:alt" content="Sideral Talent">

  <link rel="icon" href="../favicon.ico">
  <link rel="manifest" href="../site.webmanifest">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://cdn.jsdelivr.net">

  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@400;600&display=swap">
  <link rel="stylesheet" href="../styles.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@mdi/font@7.4.47/css/materialdesignicons.min.css">
</head>
<body>

  <script type="application/ld+json">
  {{JSONLD}}
  </script>

  <nav class="nav" id="nav">
    <div class="container nav-inner">
      <a href="/" class="nav-logo">
        <img src="../nav-logo.svg" alt="Sideral Talent" class="nav-logo-img" width="900" height="655" />
      </a>
      <ul class="nav-links">
        <li><a href="/#nosotros">Nosotros</a></li>
        <li><a href="/#servicios">Servicios</a></li>
        <li><a href="/#empresas">Empresas</a></li>
        <li><a href="/#candidatos">Candidatos</a></li>
        <li><a href="/busquedas-activas">B&uacute;squedas Activas</a></li>
        <li><a href="/perspectivas/">Perspectivas</a></li>
        <li><a href="/contacto" class="nav-cta">Contacto</a></li>
      </ul>
      <button class="mobile-toggle" id="mobileToggle" aria-label="Menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>

  <div class="page-wrapper" id="pageWrapper">

  <main>

    <!-- BLOG HERO: FEATURED ARTICLE -->
    <section class="blog-hero reveal-section" data-reveal>
      <img src="../spiral.svg" alt="" aria-hidden="true" class="hero-spiral" style="opacity:.14;" width="900" height="655" />
      <div class="hero-badge">
        <span class="badge-dot"></span> PERSPECTIVAS &middot; BLOG
      </div>
      <div class="blog-tags">
          <span class="blog-tag">{{TAG}}</span>
      </div>
      <h1>{{H1}}</h1>
      <p class="blog-excerpt">{{EXCERPT}}</p>
      <div class="blog-meta">
        <span class="blog-author">{{AUTHOR}}</span>
        <span>&middot; {{JOB_TITLE}} &middot; {{DATE_TEXT}}</span>
      </div>
      <a href="#articulo" class="btn btn-primary">Leer art&iacute;culo <i class="mdi mdi-arrow-down"></i></a>
    </section>

    <!-- ARTICLE -->
    <section class="article-section reveal-section" id="articulo" data-reveal>
      <div class="container">
        {{CONTENT}}
      </div>
    </section>

  </main>

    <footer class="footer">
      <div class="container footer-inner">
        <div class="footer-left">
          <span class="footer-logo">Sideral Talent</span>
          <span>&copy; 2026 Sideral Talent &middot; Santiago, Chile</span>
        </div>
        <div class="footer-right">
          <a href="/perspectivas/">Perspectivas</a>
          <a href="https://www.linkedin.com/company/sideral-talent" target="_blank" rel="noopener">LinkedIn</a>
        </div>
      </div>
    </footer>

  </div>

  <script src="../script.js" defer></script>
</body>
</html>
"""


MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def format_date_es(d):
    return f"{d.day} de {MESES_ES[d.month - 1]} de {d.year}"


def assign_dates(metas):
    """Distribute one publish date per week, starting today and going backward.

    Order of articles doesn't matter; each gets today, today-7, today-14, ...
    """
    today = date.today()
    for i, meta in enumerate(metas):
        d = today - timedelta(weeks=i)
        meta["date"] = d.isoformat()
        meta["date_text"] = format_date_es(d)


def grab(pattern, text, group=1):
    m = re.search(pattern, text, DOTALL)
    if not m:
        raise ValueError(f"Pattern not found: {pattern[:60]}...")
    return m.group(group).strip()


def extract_meta(source):
    meta = {}
    meta["og_title"] = grab(r'<meta property="og:title" content="([^"]*)"', source)
    meta["og_desc"] = grab(r'<meta property="og:description" content="([^"]*)"', source)
    meta["date"] = grab(r'<meta property="article:published_time" content="([^"]*)"', source)
    meta["h1"] = grab(r'<div class="kicker">.*?</div>\s*<h1>(.*?)</h1>', source)
    meta["kicker"] = grab(r'<div class="kicker">(.*?)</div>', source)
    meta["author"] = grab(r'<p class="byline"><strong>(.*?)</strong>', source)
    meta["date_text"] = grab(r'<time datetime="[^"]*">(.*?)</time>', source)
    try:
        meta["job_title"] = grab(r'"jobTitle":\s*"([^"]*)"', source)
    except ValueError:
        meta["job_title"] = "Fundadora"
    try:
        meta["keywords"] = grab(r'"keywords":\s*"([^"]*)"', source).split(", ")
    except ValueError:
        meta["keywords"] = []

    # Article body: inside <div class="art-body"> ... <div class="inner"> ... </div></div>
    body = grab(r'<div class="art-body">.*?<div class="inner">(.*?)</div></div>', source)

    # Signature line -> removed from body, reused later
    firma = grab(r'<p class="firma">(.*?)</p>', body)
    body = re.sub(r'<p class="firma">.*?</p>', "", body)

    # Class conversions to match the site style
    body = body.replace('class="tabla-fuente"', 'class="table-source"')
    body = body.replace('class="tabla"', 'class="table-wrap"')
    body = re.sub(r'\s+class="num"', "", body)

    # Sources section, appended to the article body
    fuentes = None
    m = re.search(r'<section class="fuentes".*?(<ul>.*?</ul>)\s*</div></div>\s*</section>', source, DOTALL)
    if m:
        fuentes = m.group(1).strip()

    # Author bio section (about Brenda)
    bio_name = bio_text = None
    m = re.search(r'<section class="author">.*?<h3>(.*?)</h3>\s*<p>(.*?)</p>', source, DOTALL)
    if m:
        bio_name = m.group(1).strip()
        bio_text = m.group(2).strip()
        # Use internal links instead of absolute URLs
        bio_text = bio_text.replace('href="https://sideraltalent.com/#', 'href="/')
        bio_text = bio_text.replace('href="https://sideraltalent.com/', 'href="/')
        bio_text = bio_text.replace('href="https://sideraltalent.com', 'href="/"')
    bio_mark = None
    m = re.search(r'<div class="author-mark"[^>]*>(.*?)</div>', source)
    if m:
        bio_mark = m.group(1).strip()

    meta["body"] = body.strip()
    meta["fuentes"] = fuentes
    meta["bio_name"] = bio_name
    meta["bio_text"] = bio_text
    meta["bio_mark"] = bio_mark or "".join(w[0] for w in meta["author"].split()[:2]).upper()
    meta["firma_name"] = re.sub(r"<[^>]+>", "", firma).strip()
    return meta


def build_article_page(slug, meta):
    url = f"{BASE_URL}/perspectivas/{slug}"

    # Article-specific OpenGraph meta tags (SEO)
    article_meta = (
        f'\n  <meta property="article:published_time" content="{meta["date"]}">'
        f'\n  <meta property="article:modified_time" content="{meta["date"]}">'
        f'\n  <meta property="article:author" content="{meta["author"]}">'
        f'\n  <meta property="article:section" content="{meta["kicker"]}">'
        f'\n  <meta property="article:tag" content="{meta["kicker"]}">'
    )

    # Word count from the stripped body text
    body_text = re.sub(r"<[^>]+>", " ", meta["body"])
    word_count = len(body_text.split())

    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": meta["h1"],
        "description": meta["og_desc"],
        "datePublished": meta["date"],
        "dateModified": meta["date"],
        "author": {"@type": "Person", "name": meta["author"], "jobTitle": meta["job_title"]},
        "publisher": {
            "@type": "Organization",
            "name": "Sideral Talent",
            "logo": {"@type": "ImageObject", "url": f"{BASE_URL}/logo.png"},
        },
        "mainEntityOfPage": url,
        "image": f"{BASE_URL}/logo-og.png",
        "inLanguage": "es-CL",
        "wordCount": word_count,
        "articleSection": meta["kicker"],
        "keywords": meta["keywords"] or [meta["kicker"]],
    }
    jsonld = json.dumps(ld, ensure_ascii=False, indent=2)

    # Article content blocks
    fuentes_html = (
        f'\n          <div class="article-sources">\n'
        f"            <h2>Fuentes</h2>\n"
        f"            {meta['fuentes']}\n"
        f"          </div>\n"
        if meta["fuentes"] else ""
    )
    bio_html = (
        f'\n          <div class="article-author">\n'
        f'            <div class="article-author-mark" aria-hidden="true">{meta["bio_mark"]}</div>\n'
        f"            <div>\n"
        f"              <h3>{meta['bio_name']}</h3>\n"
        f"              <p>{meta['bio_text']}</p>\n"
        f"            </div>\n"
        f"          </div>\n"
        if meta["bio_name"] else ""
    )
    content = (
        f'<div class="article-content">\n\n'
        f"          {meta['body']}\n"
        f"{fuentes_html}"
        f"{bio_html}"
        f'\n          <div class="article-cta">\n'
        f"            <h3>&iquest;Necesitas apoyo en tu pr&oacute;ximo proceso de selecci&oacute;n?</h3>\n"
        f'            <a href="/servicios-para-empresas" class="btn btn-primary">Servicios para empresas</a>\n'
        f"          </div>\n"
        f"\n        </div>"
    )

    page = TEMPLATE_HTML
    replacements = {
        "{{TITLE}}": meta["og_title"],
        "{{DESC}}": meta["og_desc"],
        "{{URL}}": url,
        "{{ARTICLE_META}}": article_meta,
        "{{JSONLD}}": jsonld,
        "{{TAG}}": meta["kicker"],
        "{{H1}}": meta["h1"],
        "{{EXCERPT}}": meta["og_desc"],
        "{{AUTHOR}}": meta["author"],
        "{{JOB_TITLE}}": meta["job_title"],
        "{{DATE_TEXT}}": meta["date_text"],
        "{{CONTENT}}": content,
    }
    for token, value in replacements.items():
        page = page.replace(token, value)
    return page


def build_card(slug, meta):
    return (
        f'\n            <article class="card article-card">\n'
        f'              <div class="article-card-tags">\n'
        f'                <span class="blog-tag">{meta["kicker"]}</span>\n'
        f"              </div>\n"
        f'              <h3><a href="/perspectivas/{slug}">{meta["h1"]}</a></h3>\n'
        f'              <p class="article-card-meta"><strong>{meta["author"]}</strong> &middot; {meta["date_text"]}</p>\n'
        f'              <p class="article-card-excerpt">{meta["og_desc"]}</p>\n'
        f'              <a href="/perspectivas/{slug}" class="article-card-link">Leer art&iacute;culo <i class="mdi mdi-arrow-right"></i></a>\n'
        f"            </article>\n"
    )


def update_listing(metas):
    text = LISTING.read_text(encoding="utf-8")

    # JSON-LD blogPost entries: upsert, then sort newest first
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, DOTALL)
    if not m:
        raise ValueError("JSON-LD block not found in perspectivas/index.html")
    ld = json.loads(m.group(1))
    for meta in metas:
        url = f"{BASE_URL}/perspectivas/{meta['slug']}"
        entry = next((e for e in ld["blogPost"] if e.get("url") == url), None)
        if entry is None:
            ld["blogPost"].append({
                "@type": "BlogPosting",
                "headline": meta["h1"],
                "datePublished": meta["date"],
                "author": {"@type": "Person", "name": meta["author"]},
                "url": url,
            })
        else:
            entry["datePublished"] = meta["date"]
    ld["blogPost"].sort(key=lambda e: e["datePublished"], reverse=True)
    text = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        "<script type=\"application/ld+json\">\n  " + json.dumps(ld, ensure_ascii=False, indent=2) + "\n  </script>",
        text,
        flags=DOTALL,
        count=1,
    )

    # Cards: rebuild the grid with all known cards, newest first
    sorted_metas = sorted(metas, key=lambda m: m["date"], reverse=True)
    cards = "".join(build_card(m["slug"], m) for m in sorted_metas)
    text = re.sub(
        r'<div class="article-grid" data-reveal-stagger>.*?</section>',
        '<div class="article-grid" data-reveal-stagger>\n'
        + cards.rstrip() + "\n          </div>\n        </div>\n      </section>",
        text,
        flags=DOTALL,
        count=1,
    )
    LISTING.write_text(text, encoding="utf-8")


def update_sitemap(slug, meta):
    text = SITEMAP.read_text(encoding="utf-8")
    loc = f"{BASE_URL}/perspectivas/{slug}"
    m = re.search(
        r'(<loc>' + re.escape(loc) + r'</loc>\n    <lastmod>)[^<]*(</lastmod>)', text
    )
    if m:
        text = text[:m.start()] + m.group(1) + meta["date"] + m.group(2) + text[m.end():]
        SITEMAP.write_text(text, encoding="utf-8")
        return
    entry = (
        f"  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{meta['date']}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n"
        f"    <priority>0.7</priority>\n"
        f"  </url>\n"
    )
    # Insert after the last existing perspectivas entry (keeps blog URLs grouped)
    blocks = list(re.finditer(r"  <url>.*?</url>\n", text, DOTALL))
    insert_at = None
    for m in blocks:
        if "/perspectivas" in m.group(0):
            insert_at = m.end()
    if insert_at is None:
        insert_at = text.index("</urlset>")
    SITEMAP.write_text(text[:insert_at] + entry + text[insert_at:], encoding="utf-8")


def main():
    sources = sorted(p for p in ADD_DIR.glob("*/index.html") if p.is_file())
    if not sources:
        print(f"No articles found in {ADD_DIR}")
        return 0
    metas = []
    for src in sources:
        meta = extract_meta(src.read_text(encoding="utf-8"))
        meta["slug"] = src.parent.name
        metas.append(meta)
    assign_dates(metas)
    for meta in metas:
        slug = meta["slug"]
        (PERSP_DIR / f"{slug}.html").write_text(build_article_page(slug, meta), encoding="utf-8")
        update_sitemap(slug, meta)
        print(f"OK  perspectivas/{slug}.html  ({meta['og_title']})")
    update_listing(metas)
    print(f"Done: {len(sources)} article(s) processed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
