import os
import re
import glob
import json
import html
import subprocess
from datetime import datetime
import yaml
import markdown

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
POSTS_DIR = os.path.join(ROOT_DIR, 'content', 'posts')
BLOG_OUT_DIR = os.path.join(ROOT_DIR, 'blog')
BLOG_HUB_FILE = os.path.join(ROOT_DIR, 'blog.html')
INDEX_FILE = os.path.join(ROOT_DIR, 'index.html')
TOOLS_DIR = os.path.join(ROOT_DIR, 'tools')

os.makedirs(BLOG_OUT_DIR, exist_ok=True)

# Importar gerador de sitemap
sys_path_added = False
if TOOLS_DIR not in os.sys.path:
    os.sys.path.append(TOOLS_DIR)
from build_sitemap import build_sitemap

# Meses em português
MESES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

def format_date_pt(date_str):
    try:
        dt = datetime.strptime(str(date_str).strip(), '%Y-%m-%d')
        return f"{dt.day} de {MESES[dt.month]} de {dt.year}"
    except Exception:
        return str(date_str)

def get_badge_class(color):
    c = str(color).lower()
    if 'amber' in c or 'amarelo' in c or 'power' in c:
        return 'badge-amber', '#9a6700', 'bg-[#9a6700]/10 border-[#9a6700]/30 text-[#9a6700]'
    if 'emerald' in c or 'green' in c or 'verde' in c or 'viz' in c:
        return 'badge-emerald', '#1a7f37', 'bg-[#1a7f37]/10 border-[#1a7f37]/30 text-[#1a7f37]'
    if 'purple' in c or 'roxo' in c:
        return 'badge-purple', '#8250df', 'bg-[#8250df]/10 border-[#8250df]/30 text-[#8250df]'
    return 'badge-blue', '#11376e', 'bg-[#11376e]/10 border-[#11376e]/30 text-[#11376e]'

def parse_post(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.lstrip('\ufeff')
    meta = {}
    body = content

    fm_match = re.match(r'^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$', content, re.DOTALL)
    if fm_match:
        try:
            meta = yaml.safe_load(fm_match.group(1)) or {}
            body = fm_match.group(2).strip()
        except Exception as e:
            print(f"Erro ao parsear frontmatter em {file_path}: {e}")
    elif content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()

    slug = meta.get('slug')
    if not slug:
        base = os.path.splitext(os.path.basename(file_path))[0]
        slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', base)

    slug = re.sub(r'-+', '-', str(slug)).strip('-')

    meta['slug'] = slug
    meta['raw_body'] = body
    meta['formatted_date'] = format_date_pt(meta.get('date', ''))
    return meta

def convert_markdown(body):
    type_map = {
        'NOTE': ('badge-blue', 'info', 'Nota Informativa', 'border-l-4 border-blue-500 bg-blue-50/70 text-blue-950'),
        'TIP': ('badge-emerald', 'lightbulb', 'Dica Prática', 'border-l-4 border-emerald-500 bg-emerald-50/70 text-emerald-950'),
        'WARNING': ('badge-amber', 'alert-triangle', 'Atenção', 'border-l-4 border-amber-500 bg-amber-50/70 text-amber-950'),
        'IMPORTANT': ('badge-purple', 'alert-circle', 'Importante', 'border-l-4 border-purple-500 bg-purple-50/70 text-purple-950')
    }

    def alert_sub(match):
        atype = match.group(1).upper()
        raw_lines = match.group(2)
        cleaned_lines = []
        for line in raw_lines.splitlines():
            cleaned_lines.append(re.sub(r'^>\s?', '', line))
        raw_text = "\n".join(cleaned_lines).strip()
        raw_text = re.sub(r'(:\s*)\n(-|\*|\d+\.)', r'\1\n\n\2', raw_text)
        inner_html = markdown.markdown(raw_text, extensions=['extra'])
        cls, icon, default_label, box_style = type_map.get(atype, type_map['NOTE'])
        return f'<div class="callout-box my-6 p-4 rounded-r-xl {box_style}"><div class="flex items-center gap-2 font-bold mb-2 text-sm"><i data-lucide="{icon}" class="w-4 h-4"></i> {default_label}</div><div class="text-sm leading-relaxed callout-content">{inner_html}</div></div>\n'

    def aside_sub(match):
        raw_aside = match.group(1).strip()
        icon = "info"
        label = "Destaque"
        if "⚠️" in raw_aside:
            icon = "alert-triangle"
            label = "Leitura recomendada"
            raw_aside = raw_aside.replace("⚠️", "").replace("Leitura recomendada", "").strip()
        elif "💡" in raw_aside:
            icon = "lightbulb"
            label = "Dica"
            raw_aside = raw_aside.replace("💡", "").strip()
        inner = markdown.markdown(raw_aside, extensions=['extra'])
        return f'<div class="callout-box my-6 p-4 rounded-r-xl border-l-4 border-blue-500 bg-blue-50/70 text-blue-950"><div class="flex items-center gap-2 font-bold mb-2 text-sm"><i data-lucide="{icon}" class="w-4 h-4"></i> {label}</div><div class="text-sm leading-relaxed callout-content">{inner}</div></div>\n'

    body = re.sub(r'<aside>(.*?)</aside>', aside_sub, body, flags=re.DOTALL)
    alert_pattern = re.compile(r'>\s*\[!(NOTE|TIP|WARNING|IMPORTANT)\]\s*\n((?:>.*(?:\n|$))+)', re.IGNORECASE)
    body = alert_pattern.sub(alert_sub, body)

    md = markdown.Markdown(extensions=[
        'extra',
        'tables',
        'fenced_code',
        'toc',
        'nl2br'
    ])
    html_out = md.convert(body)

    html_out = html_out.replace('<table>', '<div class="overflow-x-auto my-6"><table class="primer-table w-full text-left border-collapse">')
    html_out = html_out.replace('</table>', '</table></div>')

    headers = []
    def add_header_id(m):
        level = int(m.group(1))
        text = m.group(2)
        clean_text = re.sub(r'<[^>]+>', '', text)
        hid = re.sub(r'[^\w\s-]', '', clean_text.lower()).strip()
        hid = re.sub(r'[\s_]+', '-', hid)
        headers.append({'level': level, 'text': clean_text, 'id': hid})
        return f'<h{level} id="{hid}" class="scroll-mt-28 group flex items-center justify-between">{text} <a href="#{hid}" class="opacity-0 group-hover:opacity-40 text-sm font-normal ml-2">#</a></h{level}>'

    html_out = re.sub(r'<h([23])>(.*?)</h\1>', add_header_id, html_out)
    return html_out, headers

def generate_post_page(post, all_posts):
    slug = post['slug']
    html_content, headers = convert_markdown(post['raw_body'])
    badge_cls, badge_color, badge_style = get_badge_class(post.get('category_color', post.get('category', '')))

    # Sumário (Table of Contents)
    toc_html = ""
    toc_mobile_html = ""
    if headers:
        toc_items = []
        for h in headers:
            pl = "pl-0 font-semibold" if h['level'] == 2 else "pl-4 text-xs text-[#656d76]"
            toc_items.append(f'<li class="py-1"><a href="#{h["id"]}" class="toc-link hover:text-[#11376e] transition-colors block {pl}">{h["text"]}</a></li>')
        toc_items_str = "".join(toc_items)
        toc_html = f'''
        <nav class="toc-nav p-5 rounded-2xl glass border border-[#d0d7de] sticky top-28 mb-8" aria-label="Sumário do artigo">
          <div class="flex items-center gap-2 font-bold text-sm text-[#1f2328] mb-3 pb-2 border-b border-[#d0d7de]">
            <i data-lucide="list" class="w-4 h-4 text-[#11376e]"></i> Neste artigo
          </div>
          <ul class="text-sm space-y-1 max-h-[60vh] overflow-y-auto">
            {toc_items_str}
          </ul>
        </nav>
        '''
        toc_mobile_html = f'''
        <details class="lg:hidden mb-8 p-4 rounded-xl border border-[#d0d7de] bg-[#f6f8fa]">
          <summary class="font-bold text-sm text-[#1f2328] cursor-pointer flex items-center justify-between select-none">
            <span class="flex items-center gap-2"><i data-lucide="list" class="w-4 h-4 text-[#11376e]"></i> Neste artigo (Sumário)</span>
            <i data-lucide="chevron-down" class="w-4 h-4 text-[#656d76]"></i>
          </summary>
          <ul class="text-sm space-y-1.5 mt-3 pt-3 border-t border-[#d0d7de]/60">
            {toc_items_str}
          </ul>
        </details>
        '''

    # Artigos Relacionados
    related = [p for p in all_posts if p['slug'] != slug][:2]
    related_html = ""
    for r in related:
        r_badge, _, _ = get_badge_class(r.get('category_color', r.get('category', '')))
        related_html += f'''
        <a href="/blog/{r['slug']}" class="glass rounded-2xl p-5 border border-[#d0d7de] hover:border-[#11376e]/50 hover:shadow-md transition-all group flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-3">
              <span class="badge {r_badge} text-[11px]">{r.get('category', 'Artigo')}</span>
              <span class="text-xs text-[#656d76]">{r.get('read_time', '5 min')}</span>
            </div>
            <h4 class="text-base font-bold text-[#1f2328] group-hover:text-[#11376e] transition-colors line-clamp-2 mb-2 leading-snug">
              {html.escape(r.get('title', 'Artigo'), quote=True)}
            </h4>
            <p class="text-xs text-[#656d76] line-clamp-2 leading-relaxed">
              {html.escape(r.get('excerpt', ''), quote=False)}
            </p>
          </div>
          <span class="text-xs font-semibold text-[#11376e] inline-flex items-center gap-1 mt-4">
            Ler artigo <i data-lucide="arrow-right" class="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform"></i>
          </span>
        </a>
        '''

        tags_html = "".join(f'<span class="px-2.5 py-1 text-xs rounded-full bg-[#f6f8fa] border border-[#d0d7de] text-[#656d76]">#{html.escape(t, quote=True)}</span> ' for t in post.get('tags', []))

    cover_rel = html.escape(post.get('cover', 'assets/img/og-default.jpg').lstrip('/'), quote=True)
    cover_abs = f"https://marcosdataproduct.com/{cover_rel}"
    slug_safe = html.escape(slug, quote=True)
    post_url = f"https://marcosdataproduct.com/blog/{slug_safe}"
    title_text = html.escape(post.get('title', 'Artigo'), quote=True)
    raw_desc = (post.get('meta_description') or post.get('excerpt', '')).strip()
    if len(raw_desc) > 155:
        raw_desc = raw_desc[:152].rsplit(' ', 1)[0] + '...'
    meta_desc = html.escape(raw_desc, quote=True)
    category_text = html.escape(post.get('category', 'Artigo'), quote=True)
    author_text = html.escape(post.get('author', 'Marcos Aurélio'), quote=True)
    read_time_text = html.escape(post.get('read_time', '5 min'), quote=True)
    formatted_date_text = html.escape(str(post.get('formatted_date', '')), quote=True)
    excerpt_text = html.escape(post.get('excerpt', ''), quote=False)

    # Math check
    has_math = ('$$' in post.get('raw_body', '')) or post.get('math') is True
    katex_markup = ""
    if has_math:
        katex_markup = '''  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}]});"></script>'''

    # JSON-LD Schema (BlogPosting + BreadcrumbList)
    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "headline": title_text,
                "description": meta_desc,
                "url": post_url,
                "image": cover_abs,
                "datePublished": str(post.get('date', '2026-01-01')),
                "dateModified": str(post.get('updated_at', post.get('date', '2026-01-01'))),
                "author": {
                    "@type": "Person",
                    "name": "Marcos Aurélio",
                    "url": "https://marcosdataproduct.com/sobre",
                    "sameAs": [
                        "https://www.linkedin.com/in/marcos-a-m-m",
                        "https://github.com/marcos-a-m-91"
                    ]
                },
                "publisher": {
                    "@type": "Person",
                    "name": "Marcos Aurélio",
                    "url": "https://marcosdataproduct.com"
                },
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": post_url
                }
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://marcosdataproduct.com/"},
                    {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://marcosdataproduct.com/blog"},
                    {"@type": "ListItem", "position": 3, "name": title_text, "item": post_url}
                ]
            }
        ]
    }
    schema_json = json.dumps(schema_data, ensure_ascii=False, indent=2)

    page_html = f'''<!DOCTYPE html>
<html lang="pt-BR">

<head>
  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
  new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  }})(window,document,'script','dataLayer','GTM-KXNS2HLN');</script>
  <!-- End Google Tag Manager -->
  <meta charset="utf-8" />
  <meta content="width=device-width, initial-scale=1.0" name="viewport" />
  <title>{title_text} | Marcos Aurélio</title>
  <meta name="description" content="{meta_desc}" />
  <link rel="canonical" href="{post_url}" />

  <!-- OpenGraph / Social -->
  <meta property="og:site_name" content="Marcos Data Product" />
  <meta property="og:locale" content="pt_BR" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{post_url}" />
  <meta property="og:title" content="{title_text} | Marcos Aurélio" />
  <meta property="og:description" content="{meta_desc}" />
  <meta property="og:image" content="{cover_abs}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />

  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="/assets/img/favicon.svg" />
  <link rel="icon" type="image/x-icon" href="/favicon.ico" />
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32x32.png" />
  <link rel="icon" type="image/png" sizes="16x16" href="/assets/img/favicon-16x16.png" />
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/img/apple-touch-icon.png" />

  <!-- Stylesheets -->
  <link rel="stylesheet" href="/assets/css/tailwind.css">
  <link rel="stylesheet" href="/assets/css/main.css">
{katex_markup}

  <!-- Scripts -->
  <script defer src="/assets/vendor/lucide_latest_2eebd0ebe8c2.js"></script>
  <script defer src="/assets/js/main.js"></script>

  <!-- Dados Estruturados JSON-LD -->
  <script type="application/ld+json">
{schema_json}
  </script>

  <style>
    #reading-bar {{
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: linear-gradient(90deg, #11376e, #1f6feb);
      width: 0%;
      z-index: 9999;
      transition: width 0.1s ease-out;
    }}
    .nav-item-active {{
      color: #11376e !important;
      font-weight: 600;
      position: relative;
    }}
    .nav-item-active::after {{
      content: '';
      position: absolute;
      bottom: -6px;
      left: 0;
      width: 100%;
      height: 2px;
      background-color: #11376e;
      border-radius: 9999px;
    }}
    .article-prose {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #1f2328;
      font-size: 1.075rem;
      line-height: 1.8;
    }}
    .article-prose h2 {{
      font-size: 1.75rem;
      font-weight: 700;
      margin-top: 2.5rem;
      margin-bottom: 1rem;
      color: #1f2328;
      letter-spacing: -0.02em;
    }}
    .article-prose h3 {{
      font-size: 1.35rem;
      font-weight: 600;
      margin-top: 2rem;
      margin-bottom: 0.75rem;
      color: #1f2328;
      letter-spacing: -0.01em;
    }}
    .article-prose p {{
      margin-bottom: 1.4rem;
      color: #24292f;
    }}
    .article-prose ul, .article-prose ol {{
      margin-bottom: 1.4rem;
      padding-left: 1.5rem;
    }}
    .article-prose li {{
      margin-bottom: 0.5rem;
    }}
    .article-prose blockquote {{
      border-left: 4px solid #d0d7de;
      padding-left: 1rem;
      font-style: italic;
      color: #57606a;
      margin: 1.5rem 0;
    }}
    .primer-table th, .primer-table td {{
      padding: 10px 14px;
      border: 1px solid #d0d7de;
    }}
    .primer-table th {{
      background: #f6f8fa;
      font-weight: 600;
      color: #1f2328;
    }}
  </style>
</head>

<body class="bg-[#f8fafc] text-[#1f2328] antialiased selection:bg-[#11376e] selection:text-white">
  <!-- Google Tag Manager (noscript) -->
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-KXNS2HLN"
  height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
  <!-- End Google Tag Manager (noscript) -->
  <div id="reading-bar"></div>

  <!-- Header / Navbar -->
  <header id="navbar"
    class="sticky top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-[#d0d7de] px-5 sm:px-8 py-3.5 transition-all">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <a href="/" class="flex items-center group" aria-label="Marcos Data Product">
        <img src="/assets/img/logo-clara.webp" alt="Marcos Data Product Logo"
          class="h-8 sm:h-9 w-auto object-contain transition-opacity group-hover:opacity-90" width="180" height="40" />
      </a>
      <nav class="hidden md:flex items-center gap-8 text-sm text-[#656d76]" aria-label="Navegação Principal">
        <a href="/" class="hover:text-[#11376e] font-medium transition-colors">Home</a>
        <a href="/blog" class="nav-item-active">Blog</a>
        <a href="/projetos" class="hover:text-[#11376e] font-medium transition-colors">Projetos</a>
        <a href="/biblioteca" class="hover:text-[#11376e] font-medium transition-colors">Biblioteca</a>
        <a href="/sobre" class="hover:text-[#11376e] font-medium transition-colors">Sobre</a>
      </nav>
      <div class="flex items-center gap-3">
        <button id="search-modal-trigger"
          class="p-2 rounded-full text-[#656d76] hover:text-[#11376e] hover:bg-[#f6f8fa] transition-colors cursor-pointer"
          aria-label="Buscar no site" title="Buscar (Ctrl+K)">
          <i data-lucide="search" class="w-4 h-4 sm:w-4.5 sm:h-4.5"></i>
        </button>
        <button class="md:hidden p-2 rounded-lg text-[#656d76] hover:text-[#11376e] hover:bg-[#f6f8fa] cursor-pointer"
          id="mobile-btn" aria-label="Abrir Menu">
          <i data-lucide="menu" class="w-6 h-6"></i>
        </button>
      </div>
    </div>
  </header>

  <!-- Mobile Menu Drawer -->
  <div class="mobile-menu" id="mobile-menu">
    <button class="absolute top-5 right-5 p-2.5 rounded-xl bg-slate-100 text-[#656d76] hover:text-[#11376e]"
      id="mobile-close" aria-label="Fechar menu">
      <i data-lucide="x" class="w-5 h-5"></i>
    </button>
    <a href="/" class="flex items-center mb-8 px-2 py-1" aria-label="Marcos Data Product">
      <img src="/assets/img/logo-clara.webp" alt="Marcos Data Product" class="h-8 w-auto object-contain" width="180" height="40" />
    </a>
    <div class="flex flex-col gap-2">
      <a href="/" class="mobile-link">Home</a>
      <a href="/blog" class="mobile-link active font-semibold text-[#11376e]">Blog</a>
      <a href="/projetos" class="mobile-link">Projetos</a>
      <a href="/biblioteca" class="mobile-link">Biblioteca</a>
      <a href="/sobre" class="mobile-link">Sobre</a>
    </div>
  </div>

  <!-- Header do Post -->
  <main class="relative z-10 pt-8 sm:pt-12 pb-20 px-5 sm:px-8">
    <div class="max-w-4xl mx-auto">
      
      <!-- Breadcrumb -->
      <nav class="flex items-center gap-2 text-xs text-[#656d76] mb-8" aria-label="Breadcrumb">
        <a href="/" class="hover:text-[#11376e] transition-colors">Home</a>
        <span>/</span>
        <a href="/blog" class="hover:text-[#11376e] transition-colors">Blog</a>
        <span>/</span>
        <span class="text-[#1f2328] font-medium truncate max-w-xs">{category_text}</span>
      </nav>

      <!-- Category badge & Read info -->
      <div class="flex flex-wrap items-center gap-3 mb-5">
        <span class="badge {badge_cls} text-xs">{category_text}</span>
        <span class="text-xs text-[#656d76] flex items-center gap-1.5">
          <i data-lucide="calendar" class="w-3.5 h-3.5"></i> {formatted_date_text}
        </span>
        <span class="text-[#d0d7de]">•</span>
        <span class="text-xs text-[#656d76] flex items-center gap-1.5">
          <i data-lucide="clock" class="w-3.5 h-3.5"></i> {read_time_text} de leitura
        </span>
      </div>

      <!-- Main Title -->
      <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold text-[#1f2328] tracking-tight leading-[1.18] mb-6">
        {title_text}
      </h1>

      <!-- Excerpt -->
      <p class="text-lg sm:text-xl text-[#57606a] leading-relaxed mb-8">
        {excerpt_text}
      </p>

      <!-- Author Chip -->
      <div class="flex items-center justify-between py-4 border-y border-[#d0d7de] mb-10">
        <div class="flex items-center gap-3">
          <img src="/assets/img/minha-imagem-notion.webp" alt="Marcos Aurélio" class="w-12 h-12 rounded-full object-cover border border-[#d0d7de] bg-[#f6f8fa]" width="48" height="48" loading="lazy" decoding="async" />
          <div>
            <span class="font-bold text-sm text-[#1f2328] block">{author_text}</span>
            <span class="text-xs text-[#656d76]">Senior Business Analytics &bull; Autor</span>
          </div>
        </div>
      </div>

      {toc_mobile_html}

      <!-- Grid com Artigo e Sidebar -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-12">
        <article class="lg:col-span-8 article-prose">
          {html_content}

          <div class="mt-12 pt-6 border-t border-[#d0d7de] flex flex-wrap gap-2">
            {tags_html}
          </div>
        </article>

        <aside class="hidden lg:block lg:col-span-4">
          {toc_html}
          <div class="p-5 rounded-2xl bg-white border border-[#d0d7de] text-center shadow-xs">
            <h3 class="font-bold text-sm text-[#1f2328] mb-1">Marcos Aurélio</h3>
            <p class="text-xs text-[#656d76] mb-4 leading-relaxed">
              Compartilho análises e reflexões sobre dados, analytics, produtos e inteligência artificial.
            </p>
            <a href="https://www.linkedin.com/in/marcos-a-m-m" target="_blank" rel="noopener noreferrer" class="btn-tactile inline-flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-[#11376e] text-white text-xs font-semibold hover:bg-[#184a91] transition-all">
              <i data-lucide="linkedin" class="w-4 h-4"></i> Me acompanhe no LinkedIn
            </a>
          </div>
        </aside>
      </div>

      <!-- Artigos Relacionados -->
      {f'''
      <section class="mt-20 pt-12 border-t border-[#d0d7de]">
        <div class="flex items-center justify-between mb-8">
          <h2 class="text-xl font-bold text-[#1f2328]">Artigos Relacionados</h2>
          <a href="/blog" class="text-xs font-semibold text-[#11376e] hover:underline flex items-center gap-1">
            Ver todos <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
          </a>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          {related_html}
        </div>
      </section>
      ''' if related else ''}

    </div>
  </main>

  <!-- Footer Institucional -->
  <footer class="bg-[#0b1e3a] text-white py-12 px-5 sm:px-8 border-t border-[#1e293b]">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
      <a href="/" class="flex items-center group" aria-label="Marcos Data Product">
        <img src="/assets/img/logo-escura.webp" alt="Marcos Data Product" class="h-8 w-auto object-contain transition-opacity group-hover:opacity-90" width="180" height="40" />
      </a>
      <div class="flex items-center gap-6 text-sm text-[#94a3b8]">
        <a href="/" class="hover:text-white transition-colors">Home</a>
        <a href="/blog" class="hover:text-white transition-colors">Blog</a>
        <a href="/projetos" class="hover:text-white transition-colors">Projetos</a>
        <a href="/biblioteca" class="hover:text-white transition-colors">Biblioteca</a>
        <a href="/sobre" class="hover:text-white transition-colors">Sobre</a>
      </div>
      <div class="flex items-center gap-3 text-[#94a3b8]">
        <a href="https://www.linkedin.com/in/marcos-a-m-m" target="_blank" rel="noopener noreferrer" class="p-2 hover:text-white transition-colors" aria-label="LinkedIn">
          <i data-lucide="linkedin" class="w-5 h-5"></i>
        </a>
        <a href="https://www.instagram.com/marcos.dataproduct/" target="_blank" rel="noopener noreferrer" class="p-2 hover:text-white transition-colors" aria-label="Instagram">
          <i data-lucide="instagram" class="w-5 h-5"></i>
        </a>
        <a href="https://github.com/marcos-a-m-91" target="_blank" rel="noopener noreferrer" class="p-2 hover:text-white transition-colors" aria-label="GitHub">
          <i data-lucide="github" class="w-5 h-5"></i>
        </a>
        <a href="mailto:marcos.a.m@live.com" class="p-2 hover:text-white transition-colors" aria-label="E-mail">
          <i data-lucide="mail" class="w-5 h-5"></i>
        </a>
      </div>
    </div>
  </footer>

  <!-- Search Modal -->
  <div id="search-modal"
    class="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm hidden items-start justify-center p-4 sm:p-6 pt-20 transition-all opacity-0">
    <div
      class="bg-white rounded-2xl max-w-xl w-full border border-[#d0d7de] shadow-2xl overflow-hidden transform scale-95 transition-transform"
      id="search-modal-container">
      <div class="p-4 border-b border-[#d0d7de] flex items-center gap-3">
        <i data-lucide="search" class="w-5 h-5 text-[#11376e]"></i>
        <input type="text" id="site-search-input" placeholder="Buscar artigos, projetos, livros..."
          class="w-full text-sm outline-none text-[#1f2328] placeholder-[#8c959f]" autofocus />
        <button id="search-modal-close" class="p-1 rounded-lg text-[#656d76] hover:text-[#11376e] hover:bg-[#f6f8fa] cursor-pointer" aria-label="Fechar busca">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>
      <div class="p-4 max-h-[60vh] overflow-y-auto space-y-2" id="search-results">
        <div class="text-[11px] font-bold text-[#656d76] uppercase tracking-wider mb-2">Sugestões de navegação</div>
        <a href="/blog" class="flex items-center justify-between p-2.5 rounded-xl hover:bg-[#f6f8fa] transition-colors group">
          <div class="flex items-center gap-3">
            <span class="w-7 h-7 rounded-lg bg-[#11376e] text-white flex items-center justify-center text-xs"><i data-lucide="newspaper" class="w-3.5 h-3.5"></i></span>
            <div>
              <div class="text-xs font-semibold text-[#1f2328] group-hover:text-[#11376e]">Blog de Analytics e Dados</div>
              <div class="text-[10px] text-[#656d76]">Artigos e análises técnicas</div>
            </div>
          </div>
          <i data-lucide="chevron-right" class="w-4 h-4 text-[#8c959f] group-hover:translate-x-0.5 transition-transform"></i>
        </a>
        <a href="/projetos" class="flex items-center justify-between p-2.5 rounded-xl hover:bg-[#f6f8fa] transition-colors group">
          <div class="flex items-center gap-3">
            <span class="w-7 h-7 rounded-lg bg-[#11376e] text-white flex items-center justify-center text-xs"><i data-lucide="layers" class="w-3.5 h-3.5"></i></span>
            <div>
              <div class="text-xs font-semibold text-[#1f2328] group-hover:text-[#11376e]">Projetos e Casos Reais</div>
              <div class="text-[10px] text-[#656d76]">Portfólio prático de soluções</div>
            </div>
          </div>
          <i data-lucide="chevron-right" class="w-4 h-4 text-[#8c959f] group-hover:translate-x-0.5 transition-transform"></i>
        </a>
        <a href="/biblioteca" class="flex items-center justify-between p-2.5 rounded-xl hover:bg-[#f6f8fa] transition-colors group">
          <div class="flex items-center gap-3">
            <span class="w-7 h-7 rounded-lg bg-[#11376e] text-white flex items-center justify-center text-xs"><i data-lucide="book-open" class="w-3.5 h-3.5"></i></span>
            <div>
              <div class="text-xs font-semibold text-[#1f2328] group-hover:text-[#11376e]">Biblioteca Recomendada</div>
              <div class="text-[10px] text-[#656d76]">Curadoria de livros e referências</div>
            </div>
          </div>
          <i data-lucide="chevron-right" class="w-4 h-4 text-[#8c959f] group-hover:translate-x-0.5 transition-transform"></i>
        </a>
        <a href="/sobre" class="flex items-center justify-between p-2.5 rounded-xl hover:bg-[#f6f8fa] transition-colors group">
          <div class="flex items-center gap-3">
            <span class="w-7 h-7 rounded-lg bg-[#11376e] text-white flex items-center justify-center text-xs"><i data-lucide="user" class="w-3.5 h-3.5"></i></span>
            <div>
              <div class="text-xs font-semibold text-[#1f2328] group-hover:text-[#11376e]">Sobre Marcos Aurélio</div>
              <div class="text-[10px] text-[#656d76]">Trajetória, experiências e stack</div>
            </div>
          </div>
          <i data-lucide="chevron-right" class="w-4 h-4 text-[#8c959f] group-hover:translate-x-0.5 transition-transform"></i>
        </a>
      </div>
    </div>
  </div>
</body>
</html>'''

    out_file = os.path.join(BLOG_OUT_DIR, f"{slug}.html")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"[OK] Post compilado: {out_file}")

def get_filter_category(cat):
    c = str(cat).lower()
    if 'ia' in c or 'intelig' in c or 'rag' in c:
        return 'ia'
    if 'power' in c or 'bi' in c or 'viz' in c:
        return 'bi'
    if 'engenharia' in c or 'pipeline' in c or 'data' in c or 'dados' in c:
        return 'data'
    if 'anal' in c or 'analytics' in c:
        return 'analytics'
    if 'negoc' in c or 'business' in c:
        return 'business'
    if 'produt' in c or 'product' in c:
        return 'product'
    return 'data'

def get_theme_badge(cat):
    c = str(cat).lower()
    if 'ia' in c or 'intelig' in c or 'rag' in c:
        return 'badge-theme-ia', 'Inteligência Artificial'
    if 'power' in c or 'bi' in c or 'viz' in c:
        return 'badge-theme-powerbi', 'Power BI'
    if 'engenharia' in c or 'pipeline' in c:
        return 'badge-theme-data', 'Engenharia de Dados'
    if 'anal' in c or 'analytics' in c:
        return 'badge-theme-analytics', 'Analytics'
    if 'negoc' in c or 'business' in c:
        return 'badge-theme-business', 'Business'
    if 'produt' in c or 'product' in c:
        return 'badge-theme-product', 'Product'
    return 'badge-theme-data', 'Dados'

def sync_blog_posts_grid(posts):
    if not os.path.exists(BLOG_HUB_FILE):
        return

    with open(BLOG_HUB_FILE, 'r', encoding='utf-8') as f:
        hub_content = f.read()

    start_marker = "<!-- BLOG_POSTS_START -->"
    end_marker = "<!-- BLOG_POSTS_END -->"

    if start_marker not in hub_content or end_marker not in hub_content:
        return

    sorted_posts = sorted(posts, key=lambda x: str(x.get('date', '')), reverse=True)
    meses_abrv = {1:'jan', 2:'fev', 3:'mar', 4:'abr', 5:'mai', 6:'jun', 7:'jul', 8:'ago', 9:'set', 10:'out', 11:'nov', 12:'dez'}

    if not sorted_posts:
        new_inner = '''\n          <!-- Estado Vazio: Nenhum post -->
          <div class="col-span-1 md:col-span-2 bg-white rounded-2xl border border-[#d0d7de] p-8 sm:p-12 text-center my-4">
            <div class="w-12 h-12 rounded-xl bg-[#11376e]/10 text-[#11376e] flex items-center justify-center mx-auto mb-3">
              <i data-lucide="newspaper" class="w-6 h-6"></i>
            </div>
            <h3 class="text-base font-bold text-[#1f2328] mb-1">Novos artigos em breve</h3>
            <p class="text-xs sm:text-sm text-[#64748b] max-w-md mx-auto leading-relaxed">
              Estou redigindo novos artigos práticos sobre Business Analytics, Power BI, Engenharia de Dados e Inteligência Artificial. Volte em breve!
            </p>
          </div>\n          '''
    else:
        cards_html = []
        for p in sorted_posts:
            title = p.get('title', 'Sem título')
            slug = p.get('slug', '')
            read_time = p.get('read_time', '5 min')
            dt_str = str(p.get('date', '')).strip()
            try:
                dt = datetime.strptime(dt_str, '%Y-%m-%d')
                formatted_date = f"{dt.day:02d} {meses_abrv[dt.month]} {dt.year}"
            except Exception:
                formatted_date = dt_str

            cover = p.get('cover', 'assets/img/blog/cover-star-schema.svg')
            excerpt = p.get('excerpt', '')
            cat = p.get('category', 'Data')
            filter_cat = get_filter_category(cat)
            badge_cls, badge_label = get_theme_badge(cat)

            cards_html.append(f'''          <!-- Post: {title} ({formatted_date}) -->
          <article class="blog-post-card card-hover-clean bg-white rounded-2xl border border-[#d0d7de] overflow-hidden flex flex-col justify-between group transition-all h-full" data-category="{filter_cat}" data-date="{dt_str}">
            <a href="/blog/{slug}" class="block flex-1 flex flex-col">
              <div class="h-44 sm:h-48 bg-[#f8fafc] border-b border-[#d0d7de] overflow-hidden p-2 flex items-center justify-center">
                <img src="{cover}" alt="{title}" class="w-full h-full object-cover rounded-xl" width="400" height="240" loading="lazy" decoding="async" />
              </div>
              <div class="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <span class="{badge_cls} inline-block px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider mb-2.5">
                    {badge_label}
                  </span>
                  <h3 class="font-bold text-base text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug mb-2.5">
                    {title}
                  </h3>
                  <p class="text-xs text-[#656d76] leading-relaxed mb-4">
                    {excerpt}
                  </p>
                </div>
                <div class="flex items-center justify-between text-xs text-[#656d76] pt-3 border-t border-[#d0d7de]/50">
                  <span class="flex items-center gap-1.5">
                    <i data-lucide="clock" class="w-3.5 h-3.5 text-[#656d76]"></i>
                    <span class="text-[#656d76]">{read_time} de leitura</span>
                  </span>
                  <span>{formatted_date}</span>
                </div>
              </div>
            </a>
          </article>''')
        new_inner = '\n\n' + '\n\n'.join(cards_html) + '\n\n          '

    pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
    updated_content = pattern.sub(f"{start_marker}{new_inner}{end_marker}", hub_content)

    # Atualizar contadores
    updated_content = re.sub(r'<span\s+id=["\']displayed-count["\']>\d+</span>', f'<span id="displayed-count">{len(sorted_posts)}</span>', updated_content)
    updated_content = re.sub(r'<span\s+id=["\']total-count["\']>\d+</span>', f'<span id="total-count">{len(sorted_posts)}</span>', updated_content)

    with open(BLOG_HUB_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"[OK] Grid de posts em blog.html atualizado ({len(sorted_posts)} artigos).")

def sync_blog_featured_sidebar(posts):
    if not os.path.exists(BLOG_HUB_FILE):
        return

    with open(BLOG_HUB_FILE, 'r', encoding='utf-8') as f:
        hub_content = f.read()

    start_marker = "<!-- FEATURED_POSTS_START -->"
    end_marker = "<!-- FEATURED_POSTS_END -->"

    if start_marker not in hub_content or end_marker not in hub_content:
        return

    featured = [p for p in posts if p.get('featured') is True or str(p.get('featured')).lower() == 'true']
    featured.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    items_html = []
    meses_abrv = {1:'jan', 2:'fev', 3:'mar', 4:'abr', 5:'mai', 6:'jun', 7:'jul', 8:'ago', 9:'set', 10:'out', 11:'nov', 12:'dez'}

    for p in featured:
        title = p.get('title', 'Sem título')
        slug = p.get('slug', '')
        read_time = p.get('read_time', '5 min')
        dt_str = p.get('date', '')
        try:
            dt = datetime.strptime(str(dt_str).strip(), '%Y-%m-%d')
            formatted_date = f"{dt.day:02d} {meses_abrv[dt.month]} {dt.year}"
        except Exception:
            formatted_date = str(dt_str)
        cover = p.get('cover', 'assets/img/blog/cover-star-schema.svg')

        items_html.append(f'''            <!-- Item: {title} -->
            <a href="/blog/{slug}" class="flex items-center gap-3 group transition-all" data-date="{dt_str}">
              <img src="{cover}" alt="{title}" class="w-12 h-12 sm:w-14 sm:h-14 rounded-xl object-cover flex-shrink-0 shadow-2xs group-hover:scale-105 transition-transform duration-300" width="56" height="56" loading="lazy" decoding="async" />
              <div class="flex-1 min-w-0">
                <h4 class="font-bold text-xs sm:text-sm text-[#0b1e3a] group-hover:text-[#2563eb] transition-colors leading-snug line-clamp-2">
                  {title}
                </h4>
                <p class="text-[11px] text-[#64748b] mt-1 flex items-center gap-1 font-medium">
                  <span>{read_time}</span>
                  <span class="text-slate-300">•</span>
                  <span>{formatted_date}</span>
                </p>
              </div>
            </a>''')

    if not items_html:
        new_inner = '\n            <p class="text-xs text-[#64748b]">Nenhum artigo em destaque no momento.</p>\n            '
    else:
        new_inner = '\n' + '\n\n'.join(items_html) + '\n            '

    pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
    updated_content = pattern.sub(f"{start_marker}{new_inner}{end_marker}", hub_content)

    with open(BLOG_HUB_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)

def get_home_category_badge(post):
    cat = post.get('category', 'Analytics')
    color = post.get('category_color', '')
    c_cat = str(cat).lower()
    c_col = str(color).lower()

    if 'amber' in c_col or 'amarelo' in c_col or 'power' in c_col or 'analytics' in c_cat:
        return 'bg-[#9a6700]/10 text-[#9a6700]', cat
    if 'emerald' in c_col or 'green' in c_col or 'verde' in c_col or 'viz' in c_cat:
        return 'bg-[#1a7f37]/10 text-[#1a7f37]', cat
    if 'purple' in c_col or 'roxo' in c_col or 'ai' in c_cat or 'ia' in c_cat:
        return 'bg-[#8250df]/10 text-[#8250df]', cat
    return 'bg-[#11376e]/10 text-[#11376e]', cat

def sync_home_recent_posts(posts):
    if not os.path.exists(INDEX_FILE):
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index_content = f.read()

    start_marker = "<!-- HOME_RECENT_POSTS_START -->"
    end_marker = "<!-- HOME_RECENT_POSTS_END -->"

    if start_marker not in index_content or end_marker not in index_content:
        return

    sorted_posts = sorted(posts, key=lambda x: str(x.get('date', '')), reverse=True)
    recent_3 = sorted_posts[:3]
    meses_abrv = {1:'jan', 2:'fev', 3:'mar', 4:'abr', 5:'mai', 6:'jun', 7:'jul', 8:'ago', 9:'set', 10:'out', 11:'nov', 12:'dez'}

    if not recent_3:
        new_inner = '''\n          <div class="col-span-1 sm:col-span-3 bg-white rounded-2xl border border-[#d0d7de] p-8 text-center">
            <div class="w-12 h-12 rounded-xl bg-[#11376e]/10 text-[#11376e] flex items-center justify-center mx-auto mb-3">
              <i data-lucide="newspaper" class="w-6 h-6"></i>
            </div>
            <h3 class="text-sm font-bold text-[#1f2328] mb-1">Novos artigos em produção</h3>
            <p class="text-xs text-[#656d76] max-w-sm mx-auto leading-relaxed">
              Artigos práticos sobre Business Analytics, Power BI, Engenharia de Dados e IA estão sendo preparados. Em breve estarão disponíveis aqui e no blog.
            </p>
          </div>\n          '''
    else:
        cards_html = []
        for i, p in enumerate(recent_3, start=1):
            title = p.get('title', 'Sem título')
            title_attr = html.escape(title, quote=True)
            slug = p.get('slug', '')
            read_time = p.get('read_time', '5 min')
            dt_str = str(p.get('date', '')).strip()
            try:
                dt = datetime.strptime(dt_str, '%Y-%m-%d')
                formatted_date = f"{dt.day} {meses_abrv[dt.month]} {dt.year}"
            except Exception:
                formatted_date = dt_str

            cover = p.get('cover', 'assets/img/blog/cover-star-schema.svg')
            excerpt = p.get('excerpt', '')
            badge_style, badge_label = get_home_category_badge(p)

            cards_html.append(f'''          <!-- Post {i}: {title} -->
          <article class="card-hover-clean bg-white rounded-2xl border border-[#d0d7de] overflow-hidden flex flex-col justify-between group transition-all h-full">
            <a href="/blog/{slug}" class="block flex-1 flex flex-col">
              <div class="h-44 sm:h-48 bg-[#f6f8fa] border-b border-[#d0d7de] overflow-hidden p-2 flex items-center justify-center">
                <img src="{cover}" alt="{title_attr}" class="w-full h-full object-cover rounded-xl" width="400" height="240" loading="lazy" decoding="async" />
              </div>
              <div class="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <span class="inline-block px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-2.5 {badge_style}">
                    {badge_label}
                  </span>
                  <h3 class="font-bold text-base text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug mb-2.5">
                    {title}
                  </h3>
                  <p class="text-xs text-[#656d76] leading-relaxed mb-4">
                    {excerpt}
                  </p>
                </div>
                <div class="flex items-center justify-between text-[11px] text-[#8c959f] pt-3 border-t border-[#f1f5f9]">
                  <span class="flex items-center gap-1">
                    <i data-lucide="clock" class="w-3.5 h-3.5 text-[#656d76]"></i> {read_time} de leitura
                  </span>
                  <span>{formatted_date}</span>
                </div>
              </div>
            </a>
          </article>''')
        new_inner = '\n\n' + '\n\n'.join(cards_html) + '\n\n          '

    pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
    updated_content = pattern.sub(f"{start_marker}{new_inner}{end_marker}", index_content)

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"[OK] 3 artigos recentes sincronizados na HOME (index.html).")

def build_all():
    files = glob.glob(os.path.join(POSTS_DIR, '*.md'))
    today_str = datetime.now().strftime('%Y-%m-%d')
    posts = []

    for fp in files:
        post = parse_post(fp)
        # Filtros de publicação
        if post.get('draft') is True or post.get('noindex') is True:
            continue
        date_str = str(post.get('date', ''))[:10]
        if date_str and len(date_str) == 10 and date_str > today_str:
            continue
        posts.append(post)

    posts.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    print(f"Encontrados {len(posts)} artigos publicados. Gerando páginas...")
    for p in posts:
        generate_post_page(p, posts)

    sync_blog_posts_grid(posts)
    sync_blog_featured_sidebar(posts)
    sync_home_recent_posts(posts)
    
    # Atualizar sitemap
    build_sitemap()
    print("[OK] Blog compilado com sucesso!")

if __name__ == '__main__':
    build_all()
