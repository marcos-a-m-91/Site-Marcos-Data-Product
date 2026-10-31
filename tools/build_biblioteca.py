import os
import json
import re
import html
import time
from build_sitemap import build_sitemap

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(ROOT_DIR, 'content')
BOOKS_JSON_PATH = os.path.join(CONTENT_DIR, 'books.json')
BIBLIOTECA_HTML_PATH = os.path.join(ROOT_DIR, 'biblioteca.html')
INDEX_HTML_PATH = os.path.join(ROOT_DIR, 'index.html')

CATEGORIES = ['dados', 'negocios', 'produto', 'tecnologia', 'carreira', 'mentalidade', 'sociedade']

def atomic_write(filepath, content, retries=5, delay=0.2):
    dirname, basename = os.path.split(filepath)
    os.makedirs(dirname, exist_ok=True)
    temp_path = os.path.join(dirname, f".{basename}.tmp.{int(time.time() * 1000)}")
    
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(content)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass
        
    for attempt in range(retries):
        try:
            os.replace(temp_path, filepath)
            return True
        except PermissionError:
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return True
        except Exception as e:
            print(f"Erro ao gravar {filepath}: {e}")
            raise e

def load_books():
    if not os.path.exists(BOOKS_JSON_PATH):
        return []
    try:
        with open(BOOKS_JSON_PATH, 'r', encoding='utf-8') as f:
            books = json.load(f)
            return books if isinstance(books, list) else []
    except Exception as e:
        print(f'Erro ao carregar {BOOKS_JSON_PATH}: {e}')
        return []

def get_tag_badge_class(tag):
    t = (tag or '').strip().lower()
    if 'dado' in t or 'estatistica' in t or 'analise' in t or 'sql' in t:
        return 'bg-blue-50 text-blue-700 border border-blue-200/80'
    if 'produto' in t or 'ux' in t or 'discovery' in t:
        return 'bg-red-50 text-red-700 border border-red-200/80'
    if 'comportamento' in t or 'habito' in t or 'mentalidade' in t:
        return 'bg-amber-50 text-amber-700 border border-amber-200/80'
    if 'negocio' in t or 'estrategia' in t or 'gestao' in t:
        return 'bg-amber-50 text-amber-700 border border-amber-200/80'
    if 'tecno' in t or 'python' in t or 'ia' in t:
        return 'bg-purple-50 text-purple-700 border border-purple-200/80'
    if 'carreira' in t or 'lideran' in t:
        return 'bg-emerald-50 text-emerald-700 border border-emerald-200/80'
    if 'sociedade' in t or 'filosofia' in t or 'etica' in t:
        return 'bg-sky-50 text-sky-700 border border-sky-200/80'
    return 'bg-blue-50 text-blue-700 border border-blue-200/80'

def get_effective_category(b):
    if b.get('category'):
        return b['category']
    str_check = ' ' + ' '.join(b.get('tags', [])).lower() + ' ' + (b.get('title') or '').lower() + ' '
    if any(k in str_check for k in ['dado', 'estatistica', 'estatística', 'analise', 'análise', 'sql']):
        return 'dados'
    if any(k in str_check for k in ['produto', 'ux']):
        return 'produto'
    if any(k in str_check for k in ['habito', 'hábito', 'mentalidade', 'comportamento']):
        return 'mentalidade'
    if any(k in str_check for k in ['negocio', 'negócio', 'estrategia', 'gestao']):
        return 'negocios'
    if any(k in str_check for k in ['tecno', 'python', ' ia ', ' ai ']):
        return 'tecnologia'
    if any(k in str_check for k in ['carreira', 'lideran']):
        return 'carreira'
    if any(k in str_check for k in ['sociedade', 'filosofia']):
        return 'sociedade'
    return 'dados'

def render_primer_book_card(book, is_carousel=False):
    book_id = html.escape(str(book.get('id', 'book-id')), quote=True)
    cat = html.escape(str(get_effective_category(book)), quote=True)
    title_safe = html.escape(book.get('title', 'Sem título'), quote=True)
    author_safe = html.escape(book.get('author', 'Autor desconhecido'), quote=True)
    cover_safe = html.escape(book.get('cover_image', 'assets/img/books/cover-estatistica-o-que-e.webp'), quote=True)
    desc_safe = html.escape(book.get('short_desc', ''), quote=False)
    amazon_url = html.escape(book.get('amazon_link', '#'), quote=True)

    tags = book.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    
    tags_html = ''.join(
        f'<span class="text-xs font-semibold px-2 py-0.5 rounded-md {get_tag_badge_class(t)}">{html.escape(t)}</span>'
        for t in tags[:2]
    )

    extra_classes = " w-[85%] sm:w-[calc(50%-12px)] md:w-[calc(33.333%-16px)] flex-shrink-0 snap-start" if is_carousel else ""

    return f'''            <div class="bg-white rounded-2xl border border-[#d0d7de] p-3.5 sm:p-4 flex flex-col h-full card-hover-clean relative group cursor-pointer book-card-item{extra_classes}" data-id="{book_id}" data-category="{cat}">
              <div class="aspect-[2/3] w-full max-w-[190px] mx-auto rounded-xl overflow-hidden mb-3.5 bg-[#f6f8fa] flex items-center justify-center p-2 shadow-xs group-hover:shadow-sm transition-shadow">
                <img src="{cover_safe}" alt="{title_safe}" class="object-contain max-h-full max-w-full rounded drop-shadow-[0_2px_4px_rgba(31,35,40,0.12)]" width="190" height="285" loading="lazy" decoding="async">
              </div>
              <h3 class="font-bold text-xs sm:text-sm text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug mb-1" title="{title_safe}">
                {title_safe}
              </h3>
              <p class="text-xs text-[#656d76] mb-2 font-medium">
                {author_safe}
              </p>
              <p class="text-xs text-[#656d76] line-clamp-5 leading-relaxed mb-3.5">
                {desc_safe}
              </p>
              <div class="flex flex-wrap gap-1 mb-3">
                {tags_html}
              </div>
              <div class="pt-3 border-t border-[#d0d7de]/60 flex items-center justify-between gap-2 mt-auto">
                <a href="{amazon_url}" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation();" class="btn-tactile inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-[#11376e] hover:bg-[#184a91] text-white text-[11px] font-semibold transition-all shadow-2xs" title="Comprar na Amazon">
                  <svg class="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M15.4 13.8V9.6c0-2.6-1.6-4.1-4.5-4.1-2.2 0-4 1-4.5 3l2.4.4c.3-.9 1-1.4 2-1.4 1.2 0 1.9.6 1.9 1.6v.4l-2.5.3c-2.8.3-4.4 1.5-4.4 3.6 0 2.1 1.6 3.4 3.7 3.4 1.6 0 2.8-.7 3.5-1.7.1.6.3 1.1.5 1.5h2.4c-.3-.5-.5-1.4-.5-2.8zm-2.6-.7c0 1.3-.9 2.2-2.2 2.2-1 0-1.6-.5-1.6-1.3 0-1 .8-1.5 2.2-1.7l1.6-.2v1z" fill="#ffffff"/>
                    <path d="M4.2 18.2c3.8 2.5 9.1 2.9 14.3.7" stroke="#FF9900" stroke-width="2.2" stroke-linecap="round"/>
                    <path d="M16.9 17.3c1.3-.2 2.4.1 2.6.4.2.3-.1 1.4-.9 2.4" stroke="#FF9900" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>Amazon</span>
                  <i data-lucide="external-link" class="w-2.5 h-2.5 opacity-85"></i>
                </a>
                <span class="text-xs text-[#11376e] group-hover:text-[#184a91] transition-colors flex items-center font-medium shrink-0">
                  Ver detalhes <i data-lucide="chevron-right" class="w-3 h-3 ml-0.5"></i>
                </span>
              </div>
            </div>'''

def render_home_book_card(book):
    title = html.escape(book.get('title', 'Sem título'), quote=True)
    author = html.escape(book.get('author', 'Autor desconhecido'), quote=True)
    cover_image = html.escape(book.get('cover_image', 'assets/img/books/cover-estatistica-o-que-e.webp'), quote=True)
    
    return f'''          <!-- Livro: {title} -->
          <a href="/biblioteca" class="flex flex-col group" title="{title}">
            <div class="w-full aspect-[2/3] rounded-lg overflow-hidden book-shadow mb-2.5 bg-[#ffffff] p-1 flex items-center justify-center border border-[#d0d7de]">
              <img src="{cover_image}" alt="{title} - {author}" class="w-full h-full object-contain" width="190" height="285" loading="lazy" decoding="async" />
            </div>
            <h3 class="font-bold text-xs text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug">
              {title}
            </h3>
            <span class="text-[10px] text-[#656d76] mt-1 block">{author}</span>
          </a>'''

def update_home_books(books):
    if not os.path.exists(INDEX_HTML_PATH):
        return False
        
    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    destaques = [b for b in books if b.get('destaque')]
    if len(destaques) < 3:
        for b in books:
            if b not in destaques:
                destaques.append(b)
            if len(destaques) >= 3:
                break
                
    featured_books = destaques[:3]
    cards_html = '\n\n'.join(render_home_book_card(b) for b in featured_books)
    
    start_marker = '<!-- HOME_BOOKS_START -->'
    end_marker = '<!-- HOME_BOOKS_END -->'
    
    if start_marker in content and end_marker in content:
        s_idx = content.find(start_marker)
        e_idx = content.find(end_marker) + len(end_marker)
        new_content = content[:s_idx] + f"{start_marker}\n\n{cards_html}\n\n          {end_marker}" + content[e_idx:]
        atomic_write(INDEX_HTML_PATH, new_content)
        print(f"[OK] Home (index.html) sincronizada com {len(featured_books)} destaques de livros.")
        return True
    return False

def build_all():
    books = load_books()
    if not os.path.exists(BIBLIOTECA_HTML_PATH):
        return False
        
    with open(BIBLIOTECA_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Atualizar EMBEDDED_BOOKS no JS
    books_json_str = json.dumps(books, ensure_ascii=False, indent=2).replace('</script>', '<\\/script>')
    m = re.search(r'const EMBEDDED_BOOKS\s*=\s*\[.*?\];\s*(?=let allBooks)', content, re.DOTALL)
    if not m:
        m = re.search(r'const EMBEDDED_BOOKS\s*=\s*\[.*?\];', content, re.DOTALL)
    if m:
        content = content[:m.start()] + f'const EMBEDDED_BOOKS = {books_json_str};\n      ' + content[m.end():]

    # 2. Pré-renderizar Grid de Destaques
    destaques = [b for b in books if b.get('destaque')]
    destaques_cards = '\n'.join(render_primer_book_card(b, is_carousel=True) for b in destaques)
    content = re.sub(
        r'(<div\s+id=["\']destaques-grid["\'][^>]*>).*?(</div>\s*<!-- Controles de Navegação)',
        f'\\1\n{destaques_cards}\n            \\2',
        content,
        flags=re.DOTALL
    )

    # 3. Pré-renderizar Cada Categoria e Atualizar Seções
    for cat in CATEGORIES:
        cat_books = [b for b in books if get_effective_category(b) == cat]
        cat_cards = '\n'.join(render_primer_book_card(b) for b in cat_books)
        
        # Injetar cards no grid da categoria
        pattern_grid = re.compile(rf'(<div\s+id=["\']{cat}-grid["\'][^>]*>).*?(</div>\s*</section>)', re.DOTALL)
        content = pattern_grid.sub(f'\\1\n{cat_cards}\n            \\2', content)

        # Se tiver 0 livros, adiciona 'hidden' à section da categoria
        pattern_sec = re.compile(rf'<section\s+id=["\']section-{cat}["\']\s+class=["\']([^"\']*)["\']')
        def replace_sec(m_sec):
            cls = m_sec.group(1).split()
            if len(cat_books) == 0:
                if 'hidden' not in cls:
                    cls.append('hidden')
            else:
                cls = [c for c in cls if c != 'hidden']
            return f'<section id="section-{cat}" class="{" ".join(cls)}"'
        content = pattern_sec.sub(replace_sec, content)

    # 4. Atualizar contadores estáticos
    total_books = len(books)
    destaques_count = len(destaques)
    content = re.sub(r'<span\s+id=["\']results-count["\']>\d+</span>', f'<span id="results-count">{total_books}</span>', content)
    content = re.sub(r'<span\s+id=["\']destaques-badge-count["\']>\d+</span>', f'<span id="destaques-badge-count">{destaques_count}</span>', content)
    content = re.sub(r'<span\s+class=["\']text-slate-400 font-mono["\']\s+id=["\']filter-count-cat-all["\']>\d+</span>', f'<span class="text-slate-400 font-mono" id="filter-count-cat-all">{total_books}</span>', content)

    for cat in CATEGORIES:
        cnt = len([b for b in books if get_effective_category(b) == cat])
        content = re.sub(rf'<span\s+class=["\']text-slate-400 font-mono["\']\s+id=["\']filter-count-cat-{cat}["\']>\d+</span>', f'<span class="text-slate-400 font-mono" id="filter-count-cat-{cat}">{cnt}</span>', content)
        content = re.sub(rf'<span\s+id=["\']pill-count-{cat}["\']>\d+</span>', f'<span id="pill-count-{cat}">{cnt}</span>', content)

    # 5. Gerar JSON-LD ItemList
    itemlist_elements = []
    for idx, b in enumerate(books, start=1):
        itemlist_elements.append({
            "@type": "ListItem",
            "position": idx,
            "item": {
                "@type": "Book",
                "name": b.get("title", ""),
                "author": {"@type": "Person", "name": b.get("author", "")},
                "image": f"https://marcosdataproduct.com/{b.get('cover_image', '')}",
                "description": b.get("short_desc", ""),
                "url": b.get("amazon_link", "https://marcosdataproduct.com/biblioteca")
            }
        })
    jsonld_itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Livros Recomendados de Business Analytics, Estatística e Negócios",
        "description": "Curadoria de leituras essenciais recomendadas por Marcos Aurélio.",
        "itemListElement": itemlist_elements
    }
    jsonld_str = json.dumps(jsonld_itemlist, ensure_ascii=False, indent=2)

    # Injetar ou substituir script ld+json ItemList
    if 'id="schema-itemlist"' in content:
        content = re.sub(r'<script\s+type=["\']application/ld\+json["\']\s+id=["\']schema-itemlist["\']>.*?</script>', f'<script type="application/ld+json" id="schema-itemlist">\n{jsonld_str}\n  </script>', content, flags=re.DOTALL)
    else:
        content = content.replace('</head>', f'  <script type="application/ld+json" id="schema-itemlist">\n{jsonld_str}\n  </script>\n</head>')

    atomic_write(BIBLIOTECA_HTML_PATH, content)
    print(f"[OK] biblioteca.html compilada com {total_books} livros e HTML estático pré-renderizado.")

    update_home_books(books)
    build_sitemap()
    return True

if __name__ == '__main__':
    build_all()
