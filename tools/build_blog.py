import os
import re
import glob
import yaml
import markdown
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
POSTS_DIR = os.path.join(ROOT_DIR, 'content', 'posts')
BLOG_OUT_DIR = os.path.join(ROOT_DIR, 'blog')
BLOG_HUB_FILE = os.path.join(ROOT_DIR, 'blog.html')

os.makedirs(BLOG_OUT_DIR, exist_ok=True)

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

    meta = {}
    body = content

    # YAML Frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()

    slug = meta.get('slug')
    if not slug:
        base = os.path.splitext(os.path.basename(file_path))[0]
        # Remover data no inicio se existir (YYYY-MM-DD-)
        slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', base)

    meta['slug'] = slug
    meta['raw_body'] = body
    meta['formatted_date'] = format_date_pt(meta.get('date', ''))
    return meta

def convert_markdown(body):
    # Processar GitHub style alerts: > [!NOTE], > [!TIP], > [!WARNING], > [!IMPORTANT]
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

    # Processar Notion style <aside> blocks
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

    # Converter com python-markdown
    md = markdown.Markdown(extensions=[
        'extra',
        'tables',
        'fenced_code',
        'toc',
        'nl2br'
    ])
    html = md.convert(body)

    # Ajustar tabelas para classe Primer
    html = html.replace('<table>', '<div class="overflow-x-auto my-6"><table class="primer-table w-full text-left border-collapse">')
    html = html.replace('</table>', '</table></div>')

    # Adicionar IDs e classes aos headers H2 e H3 para ancoragem e sumário
    headers = []
    def add_header_id(m):
        level = int(m.group(1))
        text = m.group(2)
        clean_text = re.sub(r'<[^>]+>', '', text)
        hid = re.sub(r'[^\w\s-]', '', clean_text.lower()).strip()
        hid = re.sub(r'[\s_]+', '-', hid)
        headers.append({'level': level, 'text': clean_text, 'id': hid})
        return f'<h{level} id="{hid}" class="scroll-mt-28 group flex items-center justify-between">{text} <a href="#{hid}" class="opacity-0 group-hover:opacity-40 text-sm font-normal ml-2">#</a></h{level}>'

    html = re.sub(r'<h([23])>(.*?)</h\1>', add_header_id, html)

    # Melhorar blocos de código com container e botão de copiar
    def wrap_code_block(m):
        raw_pre = m.group(0)
        code_match = re.search(r'<code(?:\s+class="([^"]*)")?>(.*?)</code>', raw_pre, flags=re.DOTALL)
        lang_class = (code_match.group(1) or "") if code_match else ""
        code_body = code_match.group(2) if code_match else ""
        lang_title = lang_class.replace('language-', '').upper() or 'CÓDIGO'
        return f'''<div class="code-wrapper relative my-6 rounded-xl overflow-hidden border border-[#d0d7de] bg-[#f6f8fa]">
  <div class="code-header flex items-center justify-between px-4 py-2 bg-[#eaeef2] border-b border-[#d0d7de] text-xs text-[#656d76] font-mono">
    <span>{lang_title}</span>
    <button onclick="copyCode(this)" class="copy-btn hover:text-[#1f2328] transition-colors flex items-center gap-1">
      <i data-lucide="copy" class="w-3.5 h-3.5"></i> Copiar
    </button>
  </div>
  <pre class="p-4 overflow-x-auto text-sm font-mono text-[#1f2328] leading-relaxed"><code>{code_body}</code></pre>
</div>'''

    html = re.sub(r'<pre><code.*?>.*?</code></pre>', wrap_code_block, html, flags=re.DOTALL)

    # Processar imagens do Markdown para ficarem elegantes e com caminhos relativos corretos em blog/
    def fix_image_tag(tag_str):
        if isinstance(tag_str, re.Match):
            tag_str = tag_str.group(0)
        src_m = re.search(r'src="([^"]+)"', tag_str)
        alt_m = re.search(r'alt="([^"]*)"', tag_str)
        src = src_m.group(1) if src_m else ""
        alt = alt_m.group(1) if alt_m else ""

        # Mapeamento inteligente de imagens locais
        if not src.startswith(('http://', 'https://', '//', '../', '/')):
            clean_name = os.path.basename(src)
            img_in_blog = os.path.join(ROOT_DIR, 'assets', 'img', 'blog', clean_name)
            if os.path.exists(img_in_blog):
                fixed_src = f'../assets/img/blog/{clean_name}'
            elif clean_name.lower() == 'imagem4.png':
                fixed_src = '../assets/img/blog/airbnb-comparacao.svg'
            elif clean_name.lower() == 'image.png':
                fixed_src = '../assets/img/blog/airbnb-distribuicao.svg'
            elif src.startswith('assets/'):
                fixed_src = '../' + src.lstrip('/')
            else:
                fixed_src = f'../assets/img/blog/{clean_name}'
        else:
            fixed_src = src

        caption_html = f'<figcaption class="text-xs text-[#656d76] text-center mt-2.5">{alt}</figcaption>' if alt and not alt.lower().endswith(('.png', '.jpg', '.webp', '.svg')) else ''
        return f'''<figure class="my-8 rounded-2xl overflow-hidden border border-[#d0d7de] bg-white p-2 sm:p-3 shadow-sm">
  <img src="{fixed_src}" alt="{alt}" class="w-full h-auto rounded-xl object-contain max-h-[600px] mx-auto" loading="lazy" />
  {caption_html}
</figure>'''

    html = re.sub(r'(?:<p>\s*)?<img[^>]+>(?:\s*</p>)?', fix_image_tag, html)

    return html, headers

def generate_post_page(post, all_posts):
    slug = post['slug']
    html_content, headers = convert_markdown(post['raw_body'])
    badge_cls, badge_color, badge_style = get_badge_class(post.get('category_color', post.get('category', '')))

    # Sumário (Table of Contents)
    toc_html = ""
    if headers:
        toc_items = []
        for h in headers:
            pl = "pl-0 font-semibold" if h['level'] == 2 else "pl-4 text-xs text-[#656d76]"
            toc_items.append(f'<li class="py-1"><a href="#{h["id"]}" class="toc-link hover:text-[#11376e] transition-colors block {pl}">{h["text"]}</a></li>')
        toc_html = f'''
        <nav class="toc-nav p-5 rounded-2xl glass border border-[#d0d7de] sticky top-28 mb-8">
          <div class="flex items-center gap-2 font-bold text-sm text-[#1f2328] mb-3 pb-2 border-b border-[#d0d7de]">
            <i data-lucide="list" class="w-4 h-4 text-[#11376e]"></i> Neste artigo
          </div>
          <ul class="text-sm space-y-1 max-h-[60vh] overflow-y-auto">
            {"".join(toc_items)}
          </ul>
        </nav>
        '''

    # Artigos Relacionados (outros posts)
    related = [p for p in all_posts if p['slug'] != slug][:2]
    related_html = ""
    for r in related:
        r_badge, _, _ = get_badge_class(r.get('category_color', r.get('category', '')))
        related_html += f'''
        <a href="{r['slug']}.html" class="glass rounded-2xl p-5 border border-[#d0d7de] hover:border-[#11376e]/50 hover:shadow-md transition-all group flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-3">
              <span class="badge {r_badge} text-[11px]">{r.get('category', 'Artigo')}</span>
              <span class="text-xs text-[#656d76]">{r.get('read_time', '5 min')}</span>
            </div>
            <h4 class="text-base font-bold text-[#1f2328] group-hover:text-[#11376e] transition-colors line-clamp-2 mb-2 leading-snug">
              {r.get('title')}
            </h4>
            <p class="text-xs text-[#656d76] line-clamp-2 leading-relaxed">
              {r.get('excerpt', '')}
            </p>
          </div>
          <span class="text-xs font-semibold text-[#11376e] inline-flex items-center gap-1 mt-4">
            Ler artigo <i data-lucide="arrow-right" class="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform"></i>
          </span>
        </a>
        '''

    # Tags
    tags_html = ""
    for tag in post.get('tags', []):
        tags_html += f'<span class="px-2.5 py-1 text-xs rounded-full bg-[#f6f8fa] border border-[#d0d7de] text-[#656d76]">#{tag}</span> '

    # Imagem de capa (ajustar caminho relativo pois está dentro de blog/)
    cover_path = post.get('cover', '')
    if cover_path:
        cover_path = '../' + cover_path.lstrip('/')

    page_html = f'''<!DOCTYPE html>
<html lang="pt-BR">

<head>
  <meta charset="utf-8" />
  <meta content="width=device-width, initial-scale=1.0" name="viewport" />
  <title>{post.get('title')} — Marcos Data Product</title>
  <meta name="description" content="{post.get('excerpt', '')}" />

  <!-- OpenGraph / Social -->
  <meta property="og:title" content="{post.get('title')} — Marcos Data Product" />
  <meta property="og:description" content="{post.get('excerpt', '')}" />
  <meta property="og:type" content="article" />
  <meta property="og:image" content="{cover_path}" />

  <!-- Vendor Libraries (Local) -->
  <script src="../assets/vendor/gsap_4a57399e4113.js"></script>
  <script src="../assets/vendor/ScrollTrigger_8669edfeb171.js"></script>
  <script src="../assets/vendor/resource_3fa48481346f.js"></script>
  <script src="../assets/vendor/lucide_latest_2eebd0ebe8c2.js"></script>

  <!-- Vendor Fonts (Local) -->
  <link href="../assets/vendor/css2_5f62d382f7c0.css" rel="stylesheet" />
  <link href="../assets/vendor/css2_9b8bf743d4a8.css" rel="stylesheet" />

  <!-- Main Styles -->
  <link rel="stylesheet" href="../assets/css/main.css">

  <!-- KaTeX for Math Formulas (LaTeX) -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}]}});"></script>

  <style>
    /* Estilos específicos de leitura tipográfica do Artigo */
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
    .article-prose {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
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
    .article-prose strong {{
      color: #0f172a;
      font-weight: 700;
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
    .callout-box .callout-content p {{
      margin-bottom: 0.5rem;
    }}
    .callout-box .callout-content p:last-child {{
      margin-bottom: 0;
    }}
    .callout-box .callout-content ul {{
      margin-bottom: 0.5rem;
      padding-left: 1.25rem;
      list-style-type: disc;
    }}
    .callout-box .callout-content li {{
      margin-bottom: 0.25rem;
    }}
  </style>
</head>

<body>
  <div id="reading-bar"></div>

  <!-- Three.js Canvas -->
  <canvas id="canvas"></canvas>

  <!-- ═══════════════════════════════════════════════════════
     NAVBAR
  ═══════════════════════════════════════════════════════ -->
  <header id="navbar" class="fixed top-0 left-0 right-0 z-50 px-5 sm:px-8 py-5 sm:py-7">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <a href="../index.html" class="flex items-center gap-3 group" aria-label="Home">
        <img src="../assets/img/Logo.png" alt="Marcos Data Product"
          class="w-10 h-10 sm:w-12 sm:h-12 object-contain opacity-90 group-hover:opacity-100 transition-opacity duration-300" />
        <span class="font-semibold text-base sm:text-lg tracking-tight text-[#1f2328] hidden sm:inline">Marcos Data Product</span>
      </a>

      <nav class="hidden md:flex items-center nav-pill-group" aria-label="Navegação principal">
        <a href="../index.html" class="nav-link">Home</a>
        <a href="../blog.html" class="nav-link active">Blog</a>
        <a href="../playbook.html" class="nav-link">Playbook</a>
        <a href="../projetos.html" class="nav-link">Projetos</a>
        <a href="../biblioteca.html" class="nav-link">Biblioteca</a>
        <a href="../sobre.html" class="nav-link">Sobre</a>
      </nav>

      <button class="md:hidden glass rounded-xl p-3 text-[#656d76] hover:text-[#1f2328] transition-colors" id="mobile-btn" aria-label="Menu">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="4" y1="6" x2="20" y2="6" />
          <line x1="4" y1="12" x2="20" y2="12" />
          <line x1="4" y1="18" x2="20" y2="18" />
        </svg>
      </button>
    </div>
  </header>

  <!-- Mobile menu -->
  <div class="mobile-menu" id="mobile-menu">
    <button class="absolute top-5 right-5 glass rounded-xl p-2.5 text-[#656d76] hover:text-[#1f2328]" id="mobile-close" aria-label="Fechar menu">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 6L6 18M6 6l12 12" />
      </svg>
    </button>
    <a href="../index.html" class="mobile-link">Home</a>
    <a href="../blog.html" class="mobile-link active">Blog</a>
    <a href="../playbook.html" class="mobile-link">Playbook</a>
    <a href="../projetos.html" class="mobile-link">Projetos</a>
    <a href="../biblioteca.html" class="mobile-link">Biblioteca</a>
    <a href="../sobre.html" class="mobile-link">Sobre</a>
  </div>

  <!-- ═══════════════════════════════════════════════════════
     HEADER DO POST
  ═══════════════════════════════════════════════════════ -->
  <main class="relative z-10 pt-36 sm:pt-40 pb-20 px-5 sm:px-8">
    <div class="max-w-4xl mx-auto">
      
      <!-- Breadcrumb -->
      <nav class="flex items-center gap-2 text-xs text-[#656d76] mb-8" aria-label="Breadcrumb">
        <a href="../index.html" class="hover:text-[#11376e] transition-colors">Home</a>
        <span>/</span>
        <a href="../blog.html" class="hover:text-[#11376e] transition-colors">Blog</a>
        <span>/</span>
        <span class="text-[#1f2328] font-medium truncate max-w-xs">{post.get('category', 'Artigo')}</span>
      </nav>

      <!-- Category badge & Read info -->
      <div class="flex flex-wrap items-center gap-3 mb-5">
        <span class="badge {badge_cls} text-xs">{post.get('category', 'Artigo')}</span>
        <span class="text-xs text-[#656d76] flex items-center gap-1.5">
          <i data-lucide="calendar" class="w-3.5 h-3.5"></i> {post.get('formatted_date')}
        </span>
        <span class="text-[#d0d7de]">•</span>
        <span class="text-xs text-[#656d76] flex items-center gap-1.5">
          <i data-lucide="clock" class="w-3.5 h-3.5"></i> {post.get('read_time', '5 min')} de leitura
        </span>
      </div>

      <!-- Main Title -->
      <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold text-[#1f2328] tracking-tight leading-[1.18] mb-6" style="font-family:'Space Grotesk',sans-serif">
        {post.get('title')}
      </h1>

      <!-- Excerpt -->
      <p class="text-lg sm:text-xl text-[#57606a] leading-relaxed mb-8" style="font-family:'Manrope',sans-serif">
        {post.get('excerpt', '')}
      </p>

      <!-- Author Chip -->
      <div class="flex items-center justify-between py-4 border-y border-[#d0d7de] mb-10">
        <div class="flex items-center gap-3">
          <img src="../assets/img/Foto Marcos Aurélio.webp" alt="Marcos Aurélio" class="w-12 h-12 rounded-full object-cover border border-[#d0d7de]" />
          <div>
            <span class="font-bold text-sm text-[#1f2328] block">{post.get('author', 'Marcos Aurélio')}</span>
            <span class="text-xs text-[#656d76]">Senior Business Analytics &bull; Autor</span>
          </div>
        </div>
        
        <!-- Social share quick links -->
        <div class="flex items-center gap-2">
          <button onclick="shareArticle('linkedin')" class="p-2 rounded-lg glass hover:text-[#0A66C2] transition-colors" title="Compartilhar no LinkedIn">
            <i data-lucide="linkedin" class="w-4 h-4"></i>
          </button>
          <button onclick="shareArticle('whatsapp')" class="p-2 rounded-lg glass hover:text-[#25D366] transition-colors" title="Compartilhar no WhatsApp">
            <i data-lucide="message-circle" class="w-4 h-4"></i>
          </button>
          <button onclick="copyCurrentUrl()" class="p-2 rounded-lg glass hover:text-[#11376e] transition-colors" title="Copiar link">
            <i data-lucide="link" class="w-4 h-4"></i>
          </button>
        </div>
      </div>

      <!-- Featured Image / Cover -->
      {f'<div class="rounded-2xl overflow-hidden border border-[#d0d7de] shadow-sm mb-12 bg-white max-h-[440px] flex items-center justify-center"><img src="{cover_path}" alt="{post.get("title")}" class="w-full h-full object-cover max-h-[440px]" /></div>' if cover_path else ''}

      <!-- ═══════════════════════════════════════════════════════
         CORPO DO ARTIGO + SIDEBAR
      ═══════════════════════════════════════════════════════ -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
        
        <!-- Main Content -->
        <article class="lg:col-span-8 article-prose">
          {html_content}

          <!-- Tags & Share Footer -->
          <div class="mt-12 pt-8 border-t border-[#d0d7de]">
            <div class="flex flex-wrap items-center justify-between gap-4">
              <div class="flex flex-wrap gap-1.5">
                {tags_html}
              </div>
              <div class="flex items-center gap-2 text-xs font-semibold text-[#656d76]">
                <span>Compartilhar:</span>
                <button onclick="shareArticle('linkedin')" class="p-2 rounded-lg glass hover:text-[#0A66C2]">
                  <i data-lucide="linkedin" class="w-4 h-4"></i>
                </button>
                <button onclick="shareArticle('whatsapp')" class="p-2 rounded-lg glass hover:text-[#25D366]">
                  <i data-lucide="message-circle" class="w-4 h-4"></i>
                </button>
                <button onclick="copyCurrentUrl()" class="p-2 rounded-lg glass hover:text-[#11376e]">
                  <i data-lucide="share-2" class="w-4 h-4"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Author Bio Card -->
          <div class="glass p-6 sm:p-8 rounded-2xl border border-[#d0d7de] mt-10 flex flex-col sm:flex-row items-center gap-6">
            <img src="../assets/img/Foto Marcos Aurélio.webp" alt="Marcos Aurélio" class="w-20 h-20 rounded-2xl object-cover border border-[#d0d7de] shadow-sm" />
            <div class="text-center sm:text-left">
              <span class="badge badge-blue text-[11px] mb-2">Sobre o Autor</span>
              <h3 class="text-lg font-bold text-[#1f2328] mb-1">Marcos Aurélio</h3>
              <p class="text-xs sm:text-sm text-[#656d76] leading-relaxed mb-4">
                Senior Business Analytics com passagens por Nubank, Google e Asimov Academy. Especialista em traduzir dados complexos em decisões estratégicas de produto, IA e governança.
              </p>
              <div class="flex items-center justify-center sm:justify-start gap-3 text-xs">
                <a href="https://www.linkedin.com/in/marcos-a-m-m" target="_blank" class="text-[#0A66C2] font-semibold flex items-center gap-1 hover:underline">
                  <i data-lucide="linkedin" class="w-3.5 h-3.5"></i> Conectar no LinkedIn
                </a>
                <span class="text-[#d0d7de]">&bull;</span>
                <a href="../sobre.html" class="text-[#11376e] font-semibold hover:underline">Ver Trajetória</a>
              </div>
            </div>
          </div>

          <!-- Back to blog button -->
          <div class="mt-10 text-center sm:text-left">
            <a href="../blog.html" class="btn-secondary inline-flex items-center gap-2">
              <i data-lucide="arrow-left" class="w-4 h-4"></i> Voltar para todos os artigos
            </a>
          </div>
        </article>

        <!-- Sidebar (Desktop TOC & Widget) -->
        <aside class="hidden lg:block lg:col-span-4">
          {toc_html}

          <!-- Newsletter / Connect Box -->
          <div class="glass p-6 rounded-2xl border border-[#d0d7de]">
            <div class="w-10 h-10 rounded-xl bg-[#11376e]/10 text-[#11376e] flex items-center justify-center mb-4">
              <i data-lucide="bell" class="w-5 h-5"></i>
            </div>
            <h4 class="font-bold text-sm text-[#1f2328] mb-1">Acompanhe novos insights</h4>
            <p class="text-xs text-[#656d76] leading-relaxed mb-4">
              Publico regularmente novos artigos práticos e casos reais de Power BI, IA e Analytics no meu perfil.
            </p>
            <a href="https://www.linkedin.com/in/marcos-a-m-m" target="_blank" class="btn-primary w-full justify-center text-xs py-2.5">
              <i data-lucide="linkedin" class="w-4 h-4 text-[#0A66C2]"></i> Seguir no LinkedIn
            </a>
          </div>
        </aside>

      </div>

      <!-- ═══════════════════════════════════════════════════════
         ARTIGOS RELACIONADOS
      ═══════════════════════════════════════════════════════ -->
      {f'''
      <section class="mt-20 pt-12 border-t border-[#d0d7de]">
        <div class="flex items-center justify-between mb-8">
          <h3 class="text-xl font-bold text-[#1f2328]" style="font-family:'Space Grotesk',sans-serif">Artigos Relacionados</h3>
          <a href="../blog.html" class="text-xs font-semibold text-[#11376e] hover:underline flex items-center gap-1">
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

  <!-- ═══════════════════════════════════════════════════════
     FOOTER
  ═══════════════════════════════════════════════════════ -->
  <footer class="relative z-10 border-t border-[#d0d7de] px-5 sm:px-8 py-8 mt-12 bg-white/50">
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#656d76]">
      <div class="flex items-center gap-3">
        <img src="../assets/img/Logo.png" alt="" class="w-5 h-5 object-contain opacity-60" />
        <span>&copy; 2026 Marcos Data Product</span>
      </div>
      <div class="flex items-center gap-4">
        <a href="../blog.html" class="hover:text-[#11376e]">Blog</a>
        <a href="../playbook.html" class="hover:text-[#11376e]">Playbook</a>
        <a href="../projetos.html" class="hover:text-[#11376e]">Projetos</a>
        <a href="../sobre.html" class="hover:text-[#11376e]">Sobre</a>
      </div>
    </div>
  </footer>

  <!-- Scripts -->
  <script src="../assets/js/main.js"></script>
  <script>
    // Reading Progress Bar
    window.addEventListener('scroll', () => {{
      const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (winScroll / height) * 100;
      const bar = document.getElementById('reading-bar');
      if (bar) bar.style.width = scrolled + '%';
    }});

    // Copy Code snippet
    function copyCode(btn) {{
      const wrapper = btn.closest('.code-wrapper');
      const code = wrapper.querySelector('code').innerText;
      navigator.clipboard.writeText(code).then(() => {{
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Copiado!';
        lucide.createIcons();
        setTimeout(() => {{
          btn.innerHTML = originalText;
          lucide.createIcons();
        }}, 2000);
      }});
    }}

    // Share Helpers
    function shareArticle(network) {{
      const url = encodeURIComponent(window.location.href);
      const title = encodeURIComponent(document.title);
      if (network === 'linkedin') {{
        window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${{url}}`, '_blank');
      }} else if (network === 'whatsapp') {{
        window.open(`https://api.whatsapp.com/send?text=${{title}}%20${{url}}`, '_blank');
      }}
    }}

    function copyCurrentUrl() {{
      navigator.clipboard.writeText(window.location.href).then(() => {{
        alert('Link copiado para a área de transferência!');
      }});
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      if (window.lucide) lucide.createIcons();
    }});
  </script>
</body>
</html>'''

    out_path = os.path.join(BLOG_OUT_DIR, f"{slug}.html")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"Generated post: blog/{slug}.html")

def generate_blog_hub(all_posts):
    # Separar o post em destaque (featured ou o primeiro da lista)
    featured_post = next((p for p in all_posts if p.get('featured')), all_posts[0] if all_posts else None)
    regular_posts = [p for p in all_posts if p != featured_post] if featured_post else all_posts

    # Categorias únicas
    categories = sorted(list(set(p.get('category') for p in all_posts if p.get('category'))))

    # Hero card do post em destaque
    featured_html = ""
    if featured_post:
        f_badge, _, _ = get_badge_class(featured_post.get('category_color', featured_post.get('category', '')))
        f_cover = featured_post.get('cover', '')
        featured_html = f'''
        <div class="mb-14 reveal">
          <span class="text-xs font-bold text-[#11376e] tracking-wider uppercase mb-3 block flex items-center gap-1.5">
            <i data-lucide="sparkles" class="w-4 h-4 text-[#11376e]"></i> Artigo em Destaque
          </span>
          <div class="glass rounded-3xl border border-[#d0d7de] overflow-hidden hover:border-[#11376e]/50 hover:shadow-lg transition-all duration-500 group grid grid-cols-1 lg:grid-cols-12 gap-0">
            
            <!-- Imagem de Capa -->
            <div class="lg:col-span-6 bg-white overflow-hidden flex items-center justify-center p-4 sm:p-6 border-b lg:border-b-0 lg:border-r border-[#d0d7de]">
              <img src="{f_cover}" alt="{featured_post.get('title')}" class="w-full h-full object-cover max-h-[320px] rounded-2xl group-hover:scale-[1.02] transition-transform duration-500" />
            </div>

            <!-- Conteúdo -->
            <div class="lg:col-span-6 p-6 sm:p-10 flex flex-col justify-between">
              <div>
                <div class="flex items-center gap-3 mb-4">
                  <span class="badge {f_badge} text-xs">{featured_post.get('category', 'Artigo')}</span>
                  <span class="text-xs text-[#656d76] flex items-center gap-1">
                    <i data-lucide="calendar" class="w-3.5 h-3.5"></i> {featured_post.get('formatted_date')}
                  </span>
                  <span class="text-[#d0d7de]">&bull;</span>
                  <span class="text-xs text-[#656d76] flex items-center gap-1">
                    <i data-lucide="clock" class="w-3.5 h-3.5"></i> {featured_post.get('read_time', '5 min')}
                  </span>
                </div>

                <h2 class="text-2xl sm:text-3xl font-bold text-[#1f2328] group-hover:text-[#11376e] transition-colors tracking-tight leading-snug mb-4" style="font-family:'Space Grotesk',sans-serif">
                  <a href="blog/{featured_post['slug']}.html" class="hover:underline">
                    {featured_post.get('title')}
                  </a>
                </h2>

                <p class="text-sm sm:text-base text-[#57606a] leading-relaxed mb-6 line-clamp-3" style="font-family:'Manrope',sans-serif">
                  {featured_post.get('excerpt', '')}
                </p>
              </div>

              <div class="flex items-center justify-between pt-6 border-t border-[#d0d7de]">
                <div class="flex items-center gap-2.5">
                  <img src="assets/img/Foto Marcos Aurélio.webp" alt="Marcos Aurélio" class="w-8 h-8 rounded-full object-cover border border-[#d0d7de]" />
                  <span class="text-xs font-semibold text-[#1f2328]">Marcos Aurélio</span>
                </div>
                <a href="blog/{featured_post['slug']}.html" class="btn-primary text-xs py-2 px-4 inline-flex items-center gap-1.5">
                  Ler artigo completo <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                </a>
              </div>
            </div>

          </div>
        </div>
        '''

    # Grid de Posts
    posts_cards_html = ""
    for p in all_posts:
        badge_cls, _, _ = get_badge_class(p.get('category_color', p.get('category', '')))
        cover = p.get('cover', '')
        tags_str = " ".join(p.get('tags', []))

        posts_cards_html += f'''
        <article class="post-card glass rounded-2xl border border-[#d0d7de] overflow-hidden hover:border-[#11376e]/50 hover:shadow-md transition-all duration-300 flex flex-col justify-between group"
                 data-category="{p.get('category', '')}"
                 data-title="{p.get('title', '').lower()}"
                 data-excerpt="{p.get('excerpt', '').lower()}"
                 data-tags="{tags_str.lower()}">
          
          <div>
            <!-- Capa -->
            {f'<div class="h-48 overflow-hidden bg-white border-b border-[#d0d7de] p-3 flex items-center justify-center"><img src="{cover}" alt="{p.get("title")}" class="w-full h-full object-cover rounded-xl group-hover:scale-105 transition-transform duration-500" /></div>' if cover else ''}

            <!-- Body -->
            <div class="p-6">
              <div class="flex items-center justify-between gap-2 mb-3">
                <span class="badge {badge_cls} text-[11px]">{p.get('category', 'Artigo')}</span>
                <span class="text-xs text-[#656d76] flex items-center gap-1">
                  <i data-lucide="clock" class="w-3 h-3"></i> {p.get('read_time', '5 min')}
                </span>
              </div>

              <h3 class="text-lg font-bold text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug mb-3 tracking-tight">
                <a href="blog/{p['slug']}.html">
                  {p.get('title')}
                </a>
              </h3>

              <p class="text-xs sm:text-sm text-[#656d76] line-clamp-3 leading-relaxed mb-4">
                {p.get('excerpt', '')}
              </p>
            </div>
          </div>

          <!-- Card Footer -->
          <div class="px-6 py-4 border-t border-[#d0d7de]/60 bg-[#f6f8fa]/50 flex items-center justify-between text-xs">
            <span class="text-[#656d76]">{p.get('formatted_date')}</span>
            <a href="blog/{p['slug']}.html" class="font-semibold text-[#11376e] inline-flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
              Ler <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
            </a>
          </div>

        </article>
        '''

    # Botões de filtro de categoria
    cat_buttons_html = '<button class="cat-pill active px-4 py-1.5 rounded-full text-xs font-semibold border transition-all" data-filter="all">Todos (' + str(len(all_posts)) + ')</button>'
    for c in categories:
        count = sum(1 for p in all_posts if p.get('category') == c)
        cat_buttons_html += f'<button class="cat-pill px-4 py-1.5 rounded-full text-xs font-semibold border border-[#d0d7de] text-[#656d76] hover:text-[#1f2328] transition-all" data-filter="{c}">{c} ({count})</button>'

    hub_html = f'''<!DOCTYPE html>
<html lang="pt-BR">

<head>
  <meta charset="utf-8" />
  <meta content="width=device-width, initial-scale=1.0" name="viewport" />
  <title>Blog — Marcos Data Product | Insights, Power BI & IA</title>
  <meta name="description" content="Artigos práticos, guias e análises técnicas sobre Power BI, Inteligência Artificial, Modelagem Dimensional e Data Visualization." />

  <!-- Vendor Libraries (Local) -->
  <script src="assets/vendor/gsap_4a57399e4113.js"></script>
  <script src="assets/vendor/ScrollTrigger_8669edfeb171.js"></script>
  <script src="assets/vendor/resource_3fa48481346f.js"></script>
  <script src="assets/vendor/lucide_latest_2eebd0ebe8c2.js"></script>

  <!-- Vendor Fonts (Local) -->
  <link href="assets/vendor/css2_5f62d382f7c0.css" rel="stylesheet" />
  <link href="assets/vendor/css2_9b8bf743d4a8.css" rel="stylesheet" />

  <!-- Main Styles -->
  <link rel="stylesheet" href="assets/css/main.css">

  <style>
    .cat-pill.active {{
      background: #11376e;
      color: #ffffff;
      border-color: #11376e;
      box-shadow: 0 2px 4px rgba(17, 55, 110, 0.2);
    }}
  </style>
</head>

<body>

  <!-- Three.js Canvas -->
  <canvas id="canvas"></canvas>

  <!-- ═══════════════════════════════════════════════════════
     NAVBAR
  ═══════════════════════════════════════════════════════ -->
  <header id="navbar" class="fixed top-0 left-0 right-0 z-50 px-5 sm:px-8 py-5 sm:py-7">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <a href="index.html" class="flex items-center gap-3 group" aria-label="Home">
        <img src="assets/img/Logo.png" alt="Marcos Data Product"
          class="w-10 h-10 sm:w-12 sm:h-12 object-contain opacity-90 group-hover:opacity-100 transition-opacity duration-300" />
        <span class="font-semibold text-base sm:text-lg tracking-tight text-[#1f2328] hidden sm:inline">Marcos Data Product</span>
      </a>

      <nav class="hidden md:flex items-center nav-pill-group" aria-label="Navegação principal">
        <a href="index.html" class="nav-link">Home</a>
        <a href="blog.html" class="nav-link active">Blog</a>
        <a href="playbook.html" class="nav-link">Playbook</a>
        <a href="projetos.html" class="nav-link">Projetos</a>
        <a href="biblioteca.html" class="nav-link">Biblioteca</a>
        <a href="sobre.html" class="nav-link">Sobre</a>
      </nav>

      <button class="md:hidden glass rounded-xl p-3 text-[#656d76] hover:text-[#1f2328] transition-colors" id="mobile-btn" aria-label="Menu">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="4" y1="6" x2="20" y2="6" />
          <line x1="4" y1="12" x2="20" y2="12" />
          <line x1="4" y1="18" x2="20" y2="18" />
        </svg>
      </button>
    </div>
  </header>

  <!-- Mobile menu -->
  <div class="mobile-menu" id="mobile-menu">
    <button class="absolute top-5 right-5 glass rounded-xl p-2.5 text-[#656d76] hover:text-[#1f2328]" id="mobile-close" aria-label="Fechar menu">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 6L6 18M6 6l12 12" />
      </svg>
    </button>
    <a href="index.html" class="mobile-link">Home</a>
    <a href="blog.html" class="mobile-link active">Blog</a>
    <a href="playbook.html" class="mobile-link">Playbook</a>
    <a href="projetos.html" class="mobile-link">Projetos</a>
    <a href="biblioteca.html" class="mobile-link">Biblioteca</a>
    <a href="sobre.html" class="mobile-link">Sobre</a>
  </div>

  <!-- ═══════════════════════════════════════════════════════
     HERO SECTION
  ═══════════════════════════════════════════════════════ -->
  <section class="min-h-[45vh] flex flex-col items-center justify-center px-5 sm:px-8 pt-36 sm:pt-40 pb-12 relative overflow-hidden text-center z-10">
    <div class="max-w-4xl mx-auto flex flex-col items-center">
      
      <span class="reveal inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#11376e]/30 bg-[#11376e]/10 text-[#11376e] text-xs sm:text-sm font-semibold mb-6 uppercase tracking-wider backdrop-blur-md shadow-sm">
        <i data-lucide="newspaper" class="w-4 h-4 text-[#11376e]"></i>
        Insights & Engenharia de Dados
      </span>

      <h1 class="reveal text-4xl sm:text-5xl md:text-6xl font-bold leading-[1.08] tracking-tight mb-6 text-[#1f2328]" style="font-family:'Space Grotesk',sans-serif">
        Artigos, Metodologias &amp;<br />
        <span class="gradient-text">Visão Prática de Negócio</span>
      </h1>

      <p class="reveal text-base sm:text-lg text-[#656d76] max-w-2xl mx-auto leading-relaxed mb-6" style="font-family:'Manrope',sans-serif">
        Conteúdo técnico aprofundado sobre arquitetura no Power BI, automações com IA generativa, governança e boas práticas de visualização de dados para tomada de decisão.
      </p>

    </div>
  </section>

  <div class="section-divider"></div>

  <!-- ═══════════════════════════════════════════════════════
     FEED DE ARTIGOS
  ═══════════════════════════════════════════════════════ -->
  <main class="relative z-10 px-5 sm:px-8 py-12 pb-28">
    <div class="max-w-7xl mx-auto">
      
      <!-- Featured Post (Destaque) -->
      {featured_html}

      <!-- Toolbar: Busca e Filtros -->
      <div class="flex flex-col md:flex-row items-center justify-between gap-4 mb-10 pb-6 border-b border-[#d0d7de]">
        
        <!-- Categorias (Pílulas) -->
        <div class="flex flex-wrap items-center gap-2 w-full md:w-auto" id="cat-filters">
          {cat_buttons_html}
        </div>

        <!-- Input de Busca -->
        <div class="relative w-full md:w-80">
          <i data-lucide="search" class="w-4 h-4 text-[#656d76] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none"></i>
          <input type="text" id="search-input" placeholder="Buscar por tema, DAX, IA..."
                 class="w-full pl-10 pr-4 py-2 text-xs rounded-xl bg-white border border-[#d0d7de] text-[#1f2328] focus:outline-none focus:border-[#11376e] focus:ring-2 focus:ring-[#11376e]/10 shadow-sm" />
        </div>

      </div>

      <!-- Grid de Artigos -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8" id="posts-grid">
        {posts_cards_html}
      </div>

      <!-- Empty State se nada for encontrado na busca -->
      <div id="empty-state" class="hidden text-center py-20">
        <div class="w-16 h-16 rounded-2xl bg-[#f6f8fa] border border-[#d0d7de] flex items-center justify-center mx-auto mb-4 text-[#656d76]">
          <i data-lucide="search-x" class="w-8 h-8"></i>
        </div>
        <h3 class="text-lg font-bold text-[#1f2328] mb-2">Nenhum artigo encontrado</h3>
        <p class="text-xs text-[#656d76] max-w-sm mx-auto mb-6">Tente pesquisar por outros termos como "Power BI", "IA" ou limpe o filtro de busca.</p>
        <button onclick="resetFilters()" class="btn-secondary text-xs">Limpar filtros</button>
      </div>

      <!-- ═══════════════════════════════════════════════════════
         BANNER LINKEDIN / NEWSLETTER
      ═══════════════════════════════════════════════════════ -->
      <div class="mt-20 glass rounded-3xl p-8 sm:p-12 border border-[#d0d7de] relative overflow-hidden text-center sm:text-left flex flex-col sm:flex-row items-center justify-between gap-8">
        <div class="max-w-xl">
          <span class="badge badge-blue text-xs mb-3">Rede Profissional</span>
          <h3 class="text-2xl sm:text-3xl font-bold text-[#1f2328] tracking-tight mb-2" style="font-family:'Space Grotesk',sans-serif">
            Gostou dos artigos? Conecte-se comigo
          </h3>
          <p class="text-sm text-[#656d76] leading-relaxed">
            Compartilho análises semanais, novidades em IA aplicada a produtos de dados e discussões sobre o ecossistema moderno de Analytics.
          </p>
        </div>
        <div class="flex-shrink-0">
          <a href="https://www.linkedin.com/in/marcos-a-m-m" target="_blank" class="btn-primary py-3 px-6 text-sm">
            <i data-lucide="linkedin" class="w-4 h-4 text-[#0A66C2]"></i> Conectar no LinkedIn
          </a>
        </div>
      </div>

    </div>
  </main>

  <!-- ═══════════════════════════════════════════════════════
     FOOTER
  ═══════════════════════════════════════════════════════ -->
  <footer class="relative z-10 border-t border-[#d0d7de] px-5 sm:px-8 py-8 mt-12 bg-white/50">
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#656d76]">
      <div class="flex items-center gap-3">
        <img src="assets/img/Logo.png" alt="" class="w-5 h-5 object-contain opacity-60" />
        <span>&copy; 2026 Marcos Data Product</span>
      </div>
      <div class="flex items-center gap-4">
        <a href="blog.html" class="hover:text-[#11376e]">Blog</a>
        <a href="playbook.html" class="hover:text-[#11376e]">Playbook</a>
        <a href="projetos.html" class="hover:text-[#11376e]">Projetos</a>
        <a href="sobre.html" class="hover:text-[#11376e]">Sobre</a>
      </div>
    </div>
  </footer>

  <!-- Scripts -->
  <script src="assets/js/main.js"></script>
  <script>
    // Live Search & Category Filter Logic
    let currentCategory = 'all';
    let searchQuery = '';

    const catPills = document.querySelectorAll('.cat-pill');
    const searchInput = document.getElementById('search-input');
    const postCards = document.querySelectorAll('.post-card');
    const emptyState = document.getElementById('empty-state');

    function filterPosts() {{
      let visibleCount = 0;

      postCards.forEach(card => {{
        const category = card.getAttribute('data-category') || '';
        const title = card.getAttribute('data-title') || '';
        const excerpt = card.getAttribute('data-excerpt') || '';
        const tags = card.getAttribute('data-tags') || '';

        const matchesCat = (currentCategory === 'all' || category === currentCategory);
        const matchesSearch = (!searchQuery || title.includes(searchQuery) || excerpt.includes(searchQuery) || tags.includes(searchQuery));

        if (matchesCat && matchesSearch) {{
          card.style.display = 'flex';
          visibleCount++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      if (emptyState) {{
        emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
      }}
    }}

    catPills.forEach(pill => {{
      pill.addEventListener('click', () => {{
        catPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        currentCategory = pill.getAttribute('data-filter');
        filterPosts();
      }});
    }});

    if (searchInput) {{
      searchInput.addEventListener('input', (e) => {{
        searchQuery = e.target.value.toLowerCase().trim();
        filterPosts();
      }});
    }}

    function resetFilters() {{
      if (searchInput) searchInput.value = '';
      searchQuery = '';
      currentCategory = 'all';
      catPills.forEach(p => {{
        if (p.getAttribute('data-filter') === 'all') p.classList.add('active');
        else p.classList.remove('active');
      }});
      filterPosts();
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      if (window.lucide) lucide.createIcons();
    }});
  </script>
</body>
</html>'''

    with open(BLOG_HUB_FILE, 'w', encoding='utf-8') as f:
        f.write(hub_html)
    print("Generated hub: blog.html")

def build_all():
    files = glob.glob(os.path.join(POSTS_DIR, '*.md'))
    if not files:
        print(f"No markdown posts found in {POSTS_DIR}")
        return

    posts = []
    for fp in files:
        post = parse_post(fp)
        posts.append(post)

    # Ordenar por data decrescente
    posts.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    print(f"Found {len(posts)} posts. Generating pages...")
    for p in posts:
        generate_post_page(p, posts)

    generate_blog_hub(posts)
    print("All blog pages generated successfully!")

if __name__ == '__main__':
    build_all()
