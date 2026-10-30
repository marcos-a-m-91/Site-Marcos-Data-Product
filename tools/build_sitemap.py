import os
import glob
from datetime import datetime
import yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT_DIR, 'content', 'posts')
BLOG_OUT_DIR = os.path.join(ROOT_DIR, 'blog')
SITEMAP_FILE = os.path.join(ROOT_DIR, 'sitemap.xml')
SITE_URL = 'https://marcosdataproduct.com'

# Páginas públicas oficiais (sem páginas privadas, de teste, 404 ou noindex)
PUBLIC_PAGES = [
    {'url': '/', 'file': 'index.html', 'changefreq': 'weekly', 'priority': '1.0'},
    {'url': '/sobre', 'file': 'sobre.html', 'changefreq': 'monthly', 'priority': '0.9'},
    {'url': '/blog', 'file': 'blog.html', 'changefreq': 'weekly', 'priority': '0.9'},
    {'url': '/projetos', 'file': 'projetos.html', 'changefreq': 'monthly', 'priority': '0.8'},
    {'url': '/biblioteca', 'file': 'biblioteca.html', 'changefreq': 'monthly', 'priority': '0.8'},
]


def _file_lastmod(filepath):
    if os.path.exists(filepath):
        ts = os.path.getmtime(filepath)
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    return datetime.now().strftime('%Y-%m-%d')


def _parse_post_meta(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        raw = f.read()
    if not raw.startswith('---'):
        return None
    parts = raw.split('---', 2)
    if len(parts) < 3:
        return None
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except Exception:
        return None
    return meta


def build_sitemap():
    today_str = datetime.now().strftime('%Y-%m-%d')
    entries = []

    for page in PUBLIC_PAGES:
        full_file = os.path.join(ROOT_DIR, page['file'])
        if not os.path.exists(full_file):
            continue
        loc = f"{SITE_URL}{page['url']}"
        entries.append({
            'loc': loc,
            'lastmod': _file_lastmod(full_file),
            'changefreq': page['changefreq'],
            'priority': page['priority'],
        })

    if os.path.exists(POSTS_DIR):
        md_files = sorted(glob.glob(os.path.join(POSTS_DIR, '*.md')))
        post_entries = []
        for md_path in md_files:
            meta = _parse_post_meta(md_path)
            if not meta:
                continue
            if meta.get('draft') is True or meta.get('noindex') is True:
                continue
            slug = str(meta.get('slug', '')).strip()
            if not slug:
                continue
            date_str = str(meta.get('date', '')).strip()[:10]
            if date_str and len(date_str) == 10 and date_str > today_str:
                continue
            html_out = os.path.join(BLOG_OUT_DIR, f'{slug}.html')
            if not os.path.exists(html_out):
                continue
            lastmod = str(meta.get('updated_at') or date_str or _file_lastmod(html_out)).strip()[:10]
            post_entries.append({
                'loc': f'{SITE_URL}/blog/{slug}',
                'lastmod': lastmod,
                'changefreq': 'monthly',
                'priority': '0.7',
                '_sort_date': date_str or lastmod,
            })

        post_entries.sort(key=lambda x: x['_sort_date'], reverse=True)
        for item in post_entries:
            item.pop('_sort_date', None)
            entries.append(item)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for entry in entries:
        lines.extend([
            '  <url>',
            f"    <loc>{entry['loc']}</loc>",
            f"    <lastmod>{entry['lastmod']}</lastmod>",
            f"    <changefreq>{entry['changefreq']}</changefreq>",
            f"    <priority>{entry['priority']}</priority>",
            '  </url>',
        ])
    lines.append('</urlset>\n')

    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"[OK] sitemap.xml gerado com {len(entries)} URLs publicas em {SITEMAP_FILE}")
    return len(entries)


if __name__ == '__main__':
    build_sitemap()

