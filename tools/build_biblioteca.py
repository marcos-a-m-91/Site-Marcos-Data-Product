import os
import sys
import glob
import json
import re
import html
import time
from datetime import datetime
import yaml

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
possible_roots = [
    os.path.dirname(CURR_DIR),
    os.path.abspath(os.path.join(CURR_DIR, '..', 'Site-Marcos-Data-Product')),
    os.path.abspath(os.path.join(CURR_DIR, 'Site-Marcos-Data-Product')),
    CURR_DIR
]
ROOT_DIR = next((p for p in possible_roots if os.path.exists(os.path.join(p, 'biblioteca.html'))), possible_roots[0])
CONTENT_DIR = os.path.join(ROOT_DIR, 'content')
BOOKS_DIR = os.path.join(CONTENT_DIR, 'books')
BOOKS_JSON_PATH = os.path.join(CONTENT_DIR, 'books.json')
BIBLIOTECA_HTML_PATH = os.path.join(ROOT_DIR, 'biblioteca.html')
BIBLIOTECA_OUT_DIR = os.path.join(ROOT_DIR, 'biblioteca')
INDEX_HTML_PATH = os.path.join(ROOT_DIR, 'index.html')
SITE_URL = 'https://marcosdataproduct.com'

os.makedirs(BOOKS_DIR, exist_ok=True)
os.makedirs(BIBLIOTECA_OUT_DIR, exist_ok=True)

# Importar helper de sitemap e markdown parser
import markdown
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from build_sitemap import build_sitemap
except Exception:
    build_sitemap = lambda: None

try:
    from build_blog import convert_markdown
except Exception:
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
            cleaned = "\n".join(re.sub(r'^>\s?', '', l) for l in raw_lines.splitlines()).strip()
            inner = markdown.markdown(cleaned, extensions=['extra'])
            cls, icon, default_label, box_style = type_map.get(atype, type_map['NOTE'])
            return f'<div class="callout-box my-6 p-4 rounded-r-xl {box_style}"><div class="flex items-center gap-2 font-bold mb-2 text-sm"><i data-lucide="{icon}" class="w-4 h-4"></i> {default_label}</div><div class="text-sm leading-relaxed callout-content">{inner}</div></div>\n'
        
        parsed = re.sub(r'>\s*\[!(NOTE|TIP|WARNING|IMPORTANT)\]\s*\n((?:>.*(?:\n|$))+)', alert_sub, body or '', flags=re.IGNORECASE)
        md = markdown.Markdown(extensions=['extra', 'tables', 'fenced_code', 'nl2br'])
        return md.convert(parsed), []

CATEGORIES = ['dados', 'negocios', 'produto', 'tecnologia', 'carreira', 'mentalidade', 'sociedade']

CATEGORY_LABELS = {
    'dados': 'Dados & Analytics',
    'negocios': 'Negócios & Estratégia',
    'produto': 'Produto & UX',
    'tecnologia': 'Tecnologia & IA',
    'carreira': 'Carreira & Liderança',
    'mentalidade': 'Mentalidade & Hábitos',
    'sociedade': 'Sociedade & Filosofia'
}

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

def parse_book_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    meta = {}
    body = raw
    if raw.startswith('---'):
        parts = raw.split('---', 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
            except Exception as e:
                print(f"Aviso: yaml.safe_load falhou ({e}) em {file_path}. Usando parser de recuperação...")
                meta = {}
                current_k = None
                for line in parts[1].splitlines():
                    s = line.strip()
                    if not s or s.startswith('#'):
                        continue
                    if s.startswith('- ') and current_k:
                        val = s[2:].strip().strip("'\"")
                        if not isinstance(meta.get(current_k), list):
                            meta[current_k] = []
                        meta[current_k].append(val)
                    elif ':' in line:
                        kv = line.split(':', 1)
                        k = kv[0].strip()
                        v = kv[1].strip().strip("'\"")
                        current_k = k
                        meta[k] = v
            body = parts[2].strip()

    slug = meta.get('slug') or meta.get('id') or os.path.splitext(os.path.basename(file_path))[0]
    meta.pop('rating', None)
    meta['slug'] = slug
    meta['id'] = slug
    meta['body'] = body
    if not meta.get('desc_full'):
        meta['desc_full'] = body
    return meta

def load_books():
    books_dict = {}

    # 1. Carregar de content/books/*.md
    if os.path.exists(BOOKS_DIR):
        for md_file in glob.glob(os.path.join(BOOKS_DIR, '*.md')):
            try:
                b = parse_book_md(md_file)
                if b.get('id'):
                    books_dict[b['id']] = b
            except Exception as e:
                print(f"Erro ao carregar livro {md_file}: {e}")

    # 2. Carregar de content/books.json (para livros que ainda não viraram .md)
    if os.path.exists(BOOKS_JSON_PATH):
        try:
            with open(BOOKS_JSON_PATH, 'r', encoding='utf-8') as f:
                json_books = json.load(f)
                if isinstance(json_books, list):
                    for b in json_books:
                        b_id = b.get('id') or b.get('slug')
                        if b_id and b_id not in books_dict:
                            if not b.get('body'):
                                b['body'] = b.get('desc_full', '')
                            b['slug'] = b_id
                            books_dict[b_id] = b
                            # Salvar como .md para persistir
                            save_book_md(b)
        except Exception as e:
            print(f"Erro ao carregar {BOOKS_JSON_PATH}: {e}")

    books = list(books_dict.values())
    
    # Ordenar por data ou destaque
    books.sort(key=lambda x: (not x.get('destaque', False), str(x.get('created_at', ''))), reverse=False)
    return books

def save_book_md(book):
    slug = book.get('slug') or book.get('id')
    if not slug:
        return None
    
    os.makedirs(BOOKS_DIR, exist_ok=True)
    file_path = os.path.join(BOOKS_DIR, f"{slug}.md")

    body = book.get('body') or book.get('desc_full', '')
    meta = {
        'title': book.get('title', 'Sem título'),
        'id': slug,
        'slug': slug,
        'author': book.get('author', 'Autor desconhecido'),
        'amazon_link': book.get('amazon_link', '#'),
        'cover_image': book.get('cover_image', 'assets/img/books/cover-estatistica-o-que-e.webp'),
        'category': book.get('category', 'dados'),
        'category_color': book.get('category_color', 'blue'),
        'tags': book.get('tags', []),
        'destaque': bool(book.get('destaque', False)),
        'created_at': str(book.get('created_at', datetime.now().strftime('%Y-%m-%d'))),
        'short_desc': book.get('short_desc', ''),
        'read_time': book.get('read_time', '4 min')
    }

    yaml_header = yaml.dump(meta, allow_unicode=True, sort_keys=False)
    content = f"---\n{yaml_header}---\n\n{body}\n"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path

def normalize_books(books):
    normalized = []
    for b in books:
        b.pop('rating', None)
        slug = b.get('slug') or b.get('id')
        if not slug:
            clean_title = re.sub(r'[^\w\s-]', '', (b.get('title') or '').lower()).strip()
            slug = re.sub(r'[\s_]+', '-', clean_title) or f"livro-{int(time.time())}"
        b['slug'] = slug
        b['id'] = slug
        if not b.get('created_at'):
            b['created_at'] = datetime.now().strftime('%Y-%m-%d')
        if not b.get('category'):
            b['category'] = get_effective_category(b)
        normalized.append(b)
    return normalized

def save_books(books):
    books = normalize_books(books)
    for b in books:
        save_book_md(b)
    try:
        clean_json_books = []
        for b in books:
            b_copy = dict(b)
            clean_json_books.append(b_copy)
        with open(BOOKS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(clean_json_books, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao atualizar {BOOKS_JSON_PATH}: {e}")
    return build_all()

def delete_book_by_id(book_id):
    slug = str(book_id).strip()
    md_file = os.path.join(BOOKS_DIR, f"{slug}.md")
    html_file = os.path.join(BIBLIOTECA_OUT_DIR, f"{slug}.html")
    
    import gc
    gc.collect()
    
    for attempt in range(5):
        if os.path.exists(md_file):
            try:
                os.remove(md_file)
                print(f"[OK] Removido {md_file}")
                break
            except Exception as e:
                time.sleep(0.15 * (attempt + 1))
                if attempt == 4:
                    print(f"Erro ao remover {md_file}: {e}")
        else:
            break

    for attempt in range(6):
        if os.path.exists(html_file):
            try:
                gc.collect()
                os.remove(html_file)
                print(f"[OK] Removido {html_file}")
                break
            except Exception as e:
                time.sleep(0.2 * (attempt + 1))
                if attempt == 5:
                    print(f"Erro ao remover {html_file}: {e}")
                    try:
                        temp_del = html_file + f".del_{int(time.time())}"
                        os.replace(html_file, temp_del)
                        try:
                            os.remove(temp_del)
                        except Exception:
                            pass
                    except Exception:
                        pass
        else:
            break

    # Atualizar books.json se existir
    if os.path.exists(BOOKS_JSON_PATH):
        try:
            with open(BOOKS_JSON_PATH, 'r', encoding='utf-8') as f:
                json_books = json.load(f)
            json_books = [b for b in json_books if (b.get('id') != slug and b.get('slug') != slug)]
            with open(BOOKS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(json_books, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao atualizar {BOOKS_JSON_PATH}: {e}")

    build_all()
    return True

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
        return b['category'].lower().strip()
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

# ── Renderizadores de Cards na Biblioteca Principal ──
def render_destaque_book_card(book):
    slug = html.escape(str(book.get('slug') or book.get('id', 'book-id')), quote=True)
    cat = html.escape(str(get_effective_category(book)), quote=True)
    title_safe = html.escape(book.get('title', 'Sem título'), quote=True)
    author_safe = html.escape(book.get('author', 'Autor desconhecido'), quote=True)
    cover_safe = html.escape(book.get('cover_image', 'assets/img/books/cover-estatistica-o-que-e.webp'), quote=True)
    amazon_url = html.escape(book.get('amazon_link', '#'), quote=True)

    tags = book.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    first_tag = html.escape(tags[0]) if tags else 'Recomendado'
    badge_cls = get_tag_badge_class(first_tag)

    return f'''            <a href="/biblioteca/{slug}" class="bg-white rounded-xl border border-[#d0d7de] p-3 flex items-start gap-3 sm:gap-3.5 card-hover-clean relative group cursor-pointer book-card-item w-[300px] sm:w-[340px] md:w-[360px] shrink-0 snap-start shadow-2xs hover:border-[#11376e] transition-all block" data-id="{slug}" data-category="{cat}">
              <div class="w-[72px] sm:w-[78px] aspect-[2/3] shrink-0 rounded-lg overflow-hidden bg-[#f6f8fa] flex items-center justify-center p-1 border border-[#d0d7de]/50 shadow-2xs group-hover:shadow-xs transition-shadow">
                <img src="/{cover_safe.lstrip('/')}" alt="{title_safe}" class="object-contain max-h-full max-w-full rounded drop-shadow-[0_2px_4px_rgba(31,35,40,0.12)]" width="78" height="117" loading="lazy" decoding="async">
              </div>
              <div class="flex-1 min-w-0 flex flex-col justify-between h-full py-0.5">
                <div>
                  <div class="flex items-center gap-1.5 mb-1">
                    <span class="text-[10px] font-semibold px-2 py-0.5 rounded-md {badge_cls}">{first_tag}</span>
                  </div>
                  <h3 class="font-bold text-xs sm:text-[13px] text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug mb-1.5 line-clamp-2" title="{title_safe}">
                    {title_safe}
                  </h3>
                  <p class="text-[11px] text-[#656d76] font-medium mb-2">
                    {author_safe}
                  </p>
                </div>
                <div class="pt-2 border-t border-[#d0d7de]/50 flex items-center justify-between gap-2 mt-auto">
                  <span onclick="event.stopPropagation(); window.open('{amazon_url}', '_blank');" class="btn-tactile inline-flex items-center gap-1 px-2 py-1 rounded-md bg-[#11376e] hover:bg-[#184a91] text-white text-[10px] font-semibold transition-all shadow-2xs cursor-pointer" title="Comprar na Amazon">
                    <svg class="w-3 h-3 shrink-0" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                      <path d="M15.4 13.8V9.6c0-2.6-1.6-4.1-4.5-4.1-2.2 0-4 1-4.5 3l2.4.4c.3-.9 1-1.4 2-1.4 1.2 0 1.9.6 1.9 1.6v.4l-2.5.3c-2.8.3-4.4 1.5-4.4 3.6 0 2.1 1.6 3.4 3.7 3.4 1.6 0 2.8-.7 3.5-1.7.1.6.3 1.1.5 1.5h2.4c-.3-.5-.5-1.4-.5-2.8zm-2.6-.7c0 1.3-.9 2.2-2.2 2.2-1 0-1.6-.5-1.6-1.3 0-1 .8-1.5 2.2-1.7l1.6-.2v1z" fill="#ffffff"/>
                      <path d="M4.2 18.2c3.8 2.5 9.1 2.9 14.3.7" stroke="#FF9900" stroke-width="2.2" stroke-linecap="round"/>
                      <path d="M16.9 17.3c1.3-.2 2.4.1 2.6.4.2.3-.1 1.4-.9 2.4" stroke="#FF9900" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span>Amazon</span>
                  </span>
                  <span class="text-[10px] sm:text-[11px] text-[#11376e] group-hover:text-[#184a91] font-medium flex items-center shrink-0">
                    Ler resenha <i data-lucide="arrow-right" class="w-3 h-3 ml-0.5 group-hover:translate-x-0.5 transition-transform"></i>
                  </span>
                </div>
              </div>
            </a>'''

def render_primer_book_card(book, is_carousel=False):
    slug = html.escape(str(book.get('slug') or book.get('id', 'book-id')), quote=True)
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
        f'<span class="text-[10px] sm:text-[11px] font-semibold px-2 py-0.5 rounded-md {get_tag_badge_class(t)}">{html.escape(t)}</span>'
        for t in tags[:2]
    )

    extra_classes = " w-[78%] sm:w-[calc(50%-10px)] md:w-[calc(33.333%-14px)] lg:w-[calc(25%-15px)] shrink-0 snap-start" if is_carousel else ""

    return f'''            <a href="/biblioteca/{slug}" class="bg-white rounded-2xl border border-[#d0d7de] p-3 sm:p-3.5 flex flex-col h-full card-hover-clean relative group cursor-pointer book-card-item{extra_classes} block" data-id="{slug}" data-category="{cat}">
              <div class="aspect-[2/3] w-full max-w-[135px] mx-auto rounded-lg overflow-hidden mb-2.5 bg-[#f6f8fa] flex items-center justify-center p-1.5 shadow-2xs group-hover:shadow-xs transition-shadow">
                <img src="/{cover_safe.lstrip('/')}" alt="{title_safe}" class="object-contain max-h-full max-w-full rounded drop-shadow-[0_2px_4px_rgba(31,35,40,0.10)]" width="135" height="202" loading="lazy" decoding="async">
              </div>
              <h3 class="font-bold text-xs sm:text-sm text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug mb-1 line-clamp-2" title="{title_safe}">
                {title_safe}
              </h3>
              <p class="text-[11px] sm:text-xs text-[#656d76] mb-1.5 font-medium line-clamp-1">
                {author_safe}
              </p>
              <p class="text-[11px] sm:text-xs text-[#656d76] line-clamp-2 sm:line-clamp-3 leading-relaxed mb-2.5">
                {desc_safe}
              </p>
              <div class="flex flex-wrap gap-1 mb-2.5">
                {tags_html}
              </div>
              <div class="pt-2.5 border-t border-[#d0d7de]/60 flex items-center justify-between gap-2 mt-auto">
                <span onclick="event.stopPropagation(); window.open('{amazon_url}', '_blank');" class="btn-tactile inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#11376e] hover:bg-[#184a91] text-white text-[11px] font-semibold transition-all shadow-2xs cursor-pointer" title="Comprar na Amazon">
                  <svg class="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M15.4 13.8V9.6c0-2.6-1.6-4.1-4.5-4.1-2.2 0-4 1-4.5 3l2.4.4c.3-.9 1-1.4 2-1.4 1.2 0 1.9.6 1.9 1.6v.4l-2.5.3c-2.8.3-4.4 1.5-4.4 3.6 0 2.1 1.6 3.4 3.7 3.4 1.6 0 2.8-.7 3.5-1.7.1.6.3 1.1.5 1.5h2.4c-.3-.5-.5-1.4-.5-2.8zm-2.6-.7c0 1.3-.9 2.2-2.2 2.2-1 0-1.6-.5-1.6-1.3 0-1 .8-1.5 2.2-1.7l1.6-.2v1z" fill="#ffffff"/>
                    <path d="M4.2 18.2c3.8 2.5 9.1 2.9 14.3.7" stroke="#FF9900" stroke-width="2.2" stroke-linecap="round"/>
                    <path d="M16.9 17.3c1.3-.2 2.4.1 2.6.4.2.3-.1 1.4-.9 2.4" stroke="#FF9900" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>Amazon</span>
                  <i data-lucide="external-link" class="w-2.5 h-2.5 opacity-85"></i>
                </span>
                <span class="text-[11px] sm:text-xs text-[#11376e] group-hover:text-[#184a91] transition-colors flex items-center font-medium shrink-0">
                  Ler resenha <i data-lucide="arrow-right" class="w-3 h-3 ml-0.5 group-hover:translate-x-0.5 transition-transform"></i>
                </span>
              </div>
            </a>'''

def render_home_book_card(book):
    slug = html.escape(str(book.get('slug') or book.get('id', 'book-id')), quote=True)
    title = html.escape(book.get('title', 'Sem título'), quote=True)
    author = html.escape(book.get('author', 'Autor desconhecido'), quote=True)
    cover_image = html.escape(book.get('cover_image', 'assets/img/books/cover-estatistica-o-que-e.webp'), quote=True)
    
    return f'''          <!-- Livro: {title} -->
          <a href="/biblioteca/{slug}" class="flex flex-col group" title="{title}">
            <div class="w-full aspect-[2/3] rounded-lg overflow-hidden book-shadow mb-2.5 bg-[#ffffff] p-1 flex items-center justify-center border border-[#d0d7de]">
              <img src="/{cover_image.lstrip('/')}" alt="{title} - {author}" class="w-full h-full object-contain" width="190" height="285" loading="lazy" decoding="async" />
            </div>
            <h3 class="font-bold text-xs text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug line-clamp-2">
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

# ── Gerador de Páginas Individuais de Livros (/biblioteca/{slug}.html) ──
def generate_book_page(book, all_books):
    slug = book.get('slug') or book.get('id')
    title = book.get('title', 'Sem título')
    author = book.get('author', 'Autor desconhecido')
    cat = get_effective_category(book)
    cat_label = CATEGORY_LABELS.get(cat, 'Leituras & Curadoria')
    amazon_link = book.get('amazon_link', '#')
    cover_image = (book.get('cover_image') or 'assets/img/books/cover-estatistica-o-que-e.webp').lstrip('/')
    short_desc = book.get('short_desc', '')
    read_time = book.get('read_time', '4 min')
    raw_body = book.get('body') or book.get('desc_full', '')

    body_clean = re.sub(r'(:\s*)\n(-|\*|\d+\.)', r'\1\n\n\2', raw_body or '')
    html_content, headers = convert_markdown(body_clean)

    title_safe = html.escape(title, quote=True)
    author_safe = html.escape(author, quote=True)
    cat_label_safe = html.escape(cat_label, quote=True)
    short_desc_safe = html.escape(short_desc, quote=True)
    amazon_link_safe = html.escape(amazon_link, quote=True)
    cover_abs = f"{SITE_URL}/{cover_image}"
    book_url = f"{SITE_URL}/biblioteca/{slug}"

    tags = book.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    tags_html = ''.join(
        f'<span class="text-xs font-semibold px-2.5 py-1 rounded-md {get_tag_badge_class(t)}">{html.escape(t)}</span>'
        for t in tags
    )

    # Livros relacionados da biblioteca (mesma categoria ou outros)
    related = [b for b in all_books if (b.get('slug') or b.get('id')) != slug][:3]
    related_cards_html = ""
    for r in related:
        r_slug = html.escape(r.get('slug') or r.get('id'), quote=True)
        r_title = html.escape(r.get('title', 'Livro'), quote=True)
        r_author = html.escape(r.get('author', 'Autor'), quote=True)
        r_cover = html.escape((r.get('cover_image') or 'assets/img/books/cover-estatistica-o-que-e.webp').lstrip('/'), quote=True)
        r_cat = CATEGORY_LABELS.get(get_effective_category(r), 'Leituras')
        related_cards_html += f'''
        <a href="/biblioteca/{r_slug}" class="bg-white rounded-2xl border border-[#d0d7de] p-4 flex gap-4 card-hover-clean group hover:border-[#11376e] transition-all">
          <div class="w-16 aspect-[2/3] shrink-0 rounded-lg overflow-hidden bg-[#f6f8fa] p-1 border border-[#d0d7de]/60 shadow-2xs">
            <img src="/{r_cover}" alt="{r_title}" class="w-full h-full object-contain" loading="lazy">
          </div>
          <div class="flex-1 min-w-0 flex flex-col justify-between py-0.5">
            <div>
              <span class="text-[10px] font-semibold text-[#11376e] bg-blue-50 px-2 py-0.5 rounded mb-1 inline-block">{r_cat}</span>
              <h4 class="text-xs sm:text-sm font-bold text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug line-clamp-2">{r_title}</h4>
              <p class="text-[11px] text-[#656d76] mt-0.5">{r_author}</p>
            </div>
            <span class="text-[11px] font-semibold text-[#11376e] inline-flex items-center gap-1 mt-2">
              Ver livro <i data-lucide="arrow-right" class="w-3 h-3 group-hover:translate-x-0.5 transition-transform"></i>
            </span>
          </div>
        </a>
        '''

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
  <title>{title_safe} | Notas de Leitura &amp; Resenha | Marcos Aurélio</title>
  <meta name="description" content="{short_desc_safe}" />
  <link rel="canonical" href="{book_url}" />

  <!-- OpenGraph / Social -->
  <meta property="og:site_name" content="Marcos Data Product" />
  <meta property="og:locale" content="pt_BR" />
  <meta property="og:type" content="book" />
  <meta property="og:url" content="{book_url}" />
  <meta property="og:title" content="{title_safe} | Curadoria &amp; Resenha" />
  <meta property="og:description" content="{short_desc_safe}" />
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
  <!-- KaTeX Math Rendering -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
  <script defer src="/assets/vendor/lucide_latest_2eebd0ebe8c2.js"></script>
  <script defer src="/assets/js/main.js"></script>

  <!-- Google Font: Inter -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

  <style>
    body, h1, h2, h3, h4, h5, h6, p, a, button, input, span, blockquote, label {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }}
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
    .book-cover-3d {{
      box-shadow: 0 16px 36px -4px rgba(17, 55, 110, 0.22), 0 6px 12px -2px rgba(0, 0, 0, 0.08);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .book-cover-3d:hover {{
      transform: translateY(-4px) scale(1.02);
      box-shadow: 0 24px 48px -6px rgba(17, 55, 110, 0.28), 0 10px 16px -3px rgba(0, 0, 0, 0.12);
    }}
    /* Hero layout resiliente independente de compilação CSS externa */
    .book-hero-layout {{
      display: flex;
      flex-direction: column;
      gap: 2rem;
      align-items: flex-start;
    }}
    @media (min-width: 768px) {{
      .book-hero-layout {{
        flex-direction: row;
        gap: 2.5rem;
      }}
    }}
    .book-hero-sidebar {{
      width: 100%;
      max-width: 220px;
      margin-left: auto;
      margin-right: auto;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }}
    @media (min-width: 768px) {{
      .book-hero-sidebar {{
        margin-left: 0;
        margin-right: 0;
        width: 220px;
        max-width: 220px;
      }}
    }}
    .book-amazon-btn {{
      width: 100%;
      max-width: 220px;
    }}
    .book-hero-content {{
      flex: 1;
      min-width: 0;
      width: 100%;
    }}
    /* Prose styling editorial */
    .article-prose, .prose-editorial {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #1f2328;
      font-size: 1.075rem;
      line-height: 1.8;
    }}
    .article-prose h2, .prose-editorial h2 {{
      font-size: 1.65rem;
      font-weight: 700;
      color: #1f2328;
      letter-spacing: -0.02em;
      margin-top: 2.25rem;
      margin-bottom: 0.85rem;
      padding-bottom: 0.4rem;
      border-bottom: 1px solid #e2e8f0;
    }}
    .article-prose h3, .prose-editorial h3 {{
      font-size: 1.25rem;
      font-weight: 700;
      color: #1f2328;
      letter-spacing: -0.015em;
      margin-top: 1.75rem;
      margin-bottom: 0.75rem;
    }}
    .article-prose p, .prose-editorial p {{
      margin-bottom: 1.35rem;
      line-height: 1.85;
      color: #334155;
      font-size: 1.05rem;
    }}
    .article-prose ul, .article-prose ol, .prose-editorial ul, .prose-editorial ol {{
      margin-bottom: 1.35rem;
      padding-left: 1.5rem;
      color: #334155;
      line-height: 1.8;
      font-size: 1.05rem;
    }}
    .article-prose ul, .prose-editorial ul {{
      list-style-type: disc;
    }}
    .article-prose ol, .prose-editorial ol {{
      list-style-type: decimal;
    }}
    .article-prose li, .prose-editorial li {{
      margin-bottom: 0.5rem;
    }}
    .article-prose blockquote, .prose-editorial blockquote {{
      border-left: 4px solid #11376e;
      background: #f8fafc;
      padding: 1rem 1.25rem;
      border-radius: 0 0.75rem 0.75rem 0;
      font-style: italic;
      color: #1f2328;
      margin: 1.5rem 0;
    }}
    .article-prose hr, .prose-editorial hr {{
      border: none;
      border-top: 1px solid #e2e8f0;
      margin: 2.5rem 0;
    }}
    .article-prose strong, .prose-editorial strong {{
      font-weight: 700;
      color: #0f172a;
    }}
    .callout-box {{
      border-radius: 0 0.75rem 0.75rem 0;
      margin: 1.5rem 0;
      padding: 1rem 1.25rem;
    }}
    .callout-content p {{
      margin-bottom: 0.5rem;
    }}
    .callout-content p:last-child {{
      margin-bottom: 0;
    }}
  </style>

  <!-- Dados Estruturados JSON-LD -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "Book",
        "@id": "{book_url}#book",
        "name": "{title_safe}",
        "author": {{
          "@type": "Person",
          "name": "{author_safe}"
        }},
        "image": "{cover_abs}",
        "url": "{book_url}",
        "description": "{short_desc_safe}"
      }},
      {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://marcosdataproduct.com/"}},
          {{"@type": "ListItem", "position": 2, "name": "Biblioteca", "item": "https://marcosdataproduct.com/biblioteca"}},
          {{"@type": "ListItem", "position": 3, "name": "{title_safe}", "item": "{book_url}"}}
        ]
      }}
    ]
  }}
  </script>
</head>

<body class="bg-[#f8fafc] text-[#1f2328] font-sans antialiased min-h-screen flex flex-col selection:bg-[#11376e] selection:text-white">
  <div id="reading-bar"></div>

  <!-- NAVBAR INSTITUCIONAL -->
  <header class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-[#d0d7de] transition-all">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <a href="/" class="flex items-center gap-2 group" aria-label="Marcos Data Product">
        <img src="/assets/img/logo-clara.webp" alt="Marcos Data Product" class="h-8 w-auto object-contain transition-transform group-hover:scale-95" width="180" height="40" />
      </a>
      <nav class="hidden md:flex items-center gap-8 text-sm font-medium text-[#656d76]" aria-label="Navegação Principal">
        <a href="/" class="hover:text-[#11376e] transition-colors py-2">Home</a>
        <a href="/blog" class="hover:text-[#11376e] transition-colors py-2">Blog</a>
        <a href="/projetos" class="hover:text-[#11376e] transition-colors py-2">Projetos</a>
        <a href="/biblioteca" class="text-[#11376e] font-semibold border-b-2 border-[#11376e] py-2">Biblioteca</a>
        <a href="/sobre" class="hover:text-[#11376e] transition-colors py-2">Sobre</a>
      </nav>
      <div class="flex items-center gap-3">
        <a href="/biblioteca" class="btn-tactile inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg border border-[#d0d7de] bg-white hover:bg-slate-50 text-xs font-semibold text-[#11376e] shadow-2xs">
          <i data-lucide="arrow-left" class="w-3.5 h-3.5"></i>
          <span>Voltar à Estante</span>
        </a>
      </div>
    </div>
  </header>

  <!-- CONTEÚDO PRINCIPAL -->
  <main class="flex-1 py-8 sm:py-12">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">

      <!-- Breadcrumb -->
      <nav class="flex items-center gap-2 text-xs text-[#656d76] mb-6 sm:mb-8" aria-label="Breadcrumb">
        <a href="/" class="hover:text-[#11376e] transition-colors">Home</a>
        <span>/</span>
        <a href="/biblioteca" class="hover:text-[#11376e] transition-colors">Biblioteca</a>
        <span>/</span>
        <span class="text-[#1f2328] font-medium truncate max-w-[280px] sm:max-w-md">{title_safe}</span>
      </nav>

      <!-- HERO DO LIVRO -->
      <section class="bg-white rounded-3xl border border-[#d0d7de] p-6 sm:p-10 mb-10 shadow-sm relative overflow-hidden">
        <div class="book-hero-layout flex flex-col md:flex-row gap-8 lg:gap-10 items-start">
          
          <!-- Capa do Livro em Destaque 3D -->
          <div class="book-hero-sidebar w-full sm:w-[200px] md:w-[220px] shrink-0 mx-auto md:mx-0 flex flex-col items-center gap-4">
            <div class="w-[170px] sm:w-[200px] aspect-[2/3] rounded-2xl overflow-hidden bg-[#f6f8fa] p-2 border border-[#d0d7de] book-cover-3d">
              <img src="/{cover_image}" alt="{title_safe}" class="w-full h-full object-contain rounded" width="200" height="300" priority>
            </div>
            
            <!-- Botão da Amazon -->
            <a href="{amazon_link_safe}" target="_blank" rel="noopener noreferrer" class="book-amazon-btn btn-tactile inline-flex items-center justify-center gap-2 w-full px-4 py-2.5 rounded-xl bg-[#11376e] hover:bg-[#184a91] text-white font-semibold text-xs sm:text-sm transition-all shadow-md">
              <span class="inline-flex items-center justify-center w-5 h-5 rounded-md bg-white/10 shrink-0">
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M15.4 13.8V9.6c0-2.6-1.6-4.1-4.5-4.1-2.2 0-4 1-4.5 3l2.4.4c.3-.9 1-1.4 2-1.4 1.2 0 1.9.6 1.9 1.6v.4l-2.5.3c-2.8.3-4.4 1.5-4.4 3.6 0 2.1 1.6 3.4 3.7 3.4 1.6 0 2.8-.7 3.5-1.7.1.6.3 1.1.5 1.5h2.4c-.3-.5-.5-1.4-.5-2.8zm-2.6-.7c0 1.3-.9 2.2-2.2 2.2-1 0-1.6-.5-1.6-1.3 0-1 .8-1.5 2.2-1.7l1.6-.2v1z" fill="#ffffff"/>
                  <path d="M4.2 18.2c3.8 2.5 9.1 2.9 14.3.7" stroke="#FF9900" stroke-width="2" stroke-linecap="round"/>
                  <path d="M16.9 17.3c1.3-.2 2.4.1 2.6.4.2.3-.1 1.4-.9 2.4" stroke="#FF9900" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
              <span>Comprar na Amazon</span>
              <i data-lucide="external-link" class="w-3.5 h-3.5 opacity-80 shrink-0"></i>
            </a>
          </div>

          <!-- Metadados & Apresentação -->
          <div class="book-hero-content flex-1 min-w-0 flex flex-col justify-between">
            <div>
              <div class="flex flex-wrap items-center gap-2 mb-3">
                <span class="text-xs font-semibold px-2.5 py-1 rounded-md bg-blue-50 text-[#11376e] border border-blue-200/80">
                  {cat_label_safe}
                </span>
                {tags_html}
              </div>

              <h1 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-[#1f2328] tracking-tight leading-tight mb-2">
                {title_safe}
              </h1>

              <p class="text-sm sm:text-base font-medium text-[#475569] mb-4">
                Obra por <span class="font-bold text-[#1f2328]">{author_safe}</span>
              </p>

              <!-- Leitura e Contexto -->
              <div class="flex flex-wrap items-center gap-4 text-xs sm:text-sm text-[#656d76] pb-5 mb-5 border-b border-[#e2e8f0]">
                <div class="inline-flex items-center gap-1.5 font-medium">
                  <i data-lucide="clock" class="w-3.5 h-3.5 text-[#656d76]"></i>
                  <span>{read_time} de leitura das notas</span>
                </div>
              </div>

              <!-- Tese Central / Resumo -->
              <div class="p-4 sm:p-5 rounded-2xl bg-[#f8fafc] border-l-4 border-[#11376e] shadow-2xs mb-2">
                <div class="text-[11px] font-bold uppercase tracking-wider text-[#11376e] mb-1.5 flex items-center gap-1.5">
                  <i data-lucide="quote" class="w-3.5 h-3.5 text-[#11376e]"></i>
                  <span>Por que vale a leitura</span>
                </div>
                <p class="text-sm sm:text-[15px] text-[#334155] leading-relaxed italic">
                  "{short_desc_safe}"
                </p>
              </div>

            </div>
          </div>

        </div>
      </section>

      <!-- ARTIGO / NOTAS COMPLETAS DO MARCOS -->
      <section class="bg-white rounded-3xl border border-[#d0d7de] p-6 sm:p-10 mb-12 shadow-sm">
        <div class="flex items-center gap-2 text-[#11376e] font-bold text-xs uppercase tracking-wider mb-6 pb-3 border-b border-[#e2e8f0]">
          <i data-lucide="book-open-check" class="w-4 h-4 text-[#11376e]"></i>
          <span>Curadoria Comentada &amp; Notas de Leitura do Marcos</span>
        </div>

        <article class="article-prose prose-editorial">
          {html_content}
        </article>

        <!-- Caixa de Ação / Compartilhamento -->
        <div class="p-6 rounded-2xl bg-[#f8fafc] border border-[#d0d7de] flex flex-col sm:flex-row items-center justify-between gap-4 mt-10">
          <div>
            <h4 class="text-sm font-bold text-[#1f2328] mb-0.5">Gostou das reflexões desta obra?</h4>
            <p class="text-xs text-[#656d76]">Compartilhe este link com alguém do seu time de dados ou produto.</p>
          </div>
          <button onclick="navigator.clipboard.writeText(window.location.href); this.textContent='Link Copiado!'; setTimeout(() => this.textContent='Copiar Link', 2000);" class="btn-tactile inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-[#d0d7de] bg-white hover:bg-slate-50 text-xs font-semibold text-[#11376e] shadow-2xs cursor-pointer shrink-0">
            <i data-lucide="copy" class="w-3.5 h-3.5"></i>
            <span>Copiar Link</span>
          </button>
        </div>
      </section>

      <!-- OUTRAS LEITURAS RECOMENDADAS -->
      <section class="mb-10">
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-base sm:text-lg font-bold text-[#1f2328] tracking-tight">Outras leituras recomendadas na biblioteca</h3>
          <a href="/biblioteca" class="text-xs font-semibold text-[#11376e] hover:underline flex items-center gap-1">
            Ver todas <i data-lucide="arrow-right" class="w-3 h-3"></i>
          </a>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {related_cards_html}
        </div>
      </section>

    </div>
  </main>

  <!-- FOOTER INSTITUCIONAL -->
  <footer class="bg-[#0b1e3a] text-white py-12 px-5 sm:px-8 border-t border-[#1e293b]">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
      <a href="/" class="flex items-center group" aria-label="Marcos Data Product">
        <img src="/assets/img/logo-escura.webp" alt="Marcos Data Product" class="h-8 w-auto object-contain transition-opacity group-hover:opacity-90" width="180" height="40" />
      </a>
      <div class="flex flex-wrap items-center justify-center gap-6 text-sm text-[#94a3b8]">
        <a href="/" class="hover:text-white transition-colors">Home</a>
        <a href="/blog" class="hover:text-white transition-colors">Blog</a>
        <a href="/projetos" class="hover:text-white transition-colors">Projetos</a>
        <a href="/biblioteca" class="hover:text-white transition-colors">Biblioteca</a>
        <a href="/sobre" class="hover:text-white transition-colors">Sobre</a>
      </div>
      <div class="flex items-center gap-2 text-[#94a3b8]">
        <a href="https://www.linkedin.com/in/marcos-a-m-m" target="_blank" rel="noopener noreferrer" class="p-2.5 rounded-lg hover:text-white hover:bg-white/5 transition-colors" aria-label="LinkedIn">
          <i data-lucide="linkedin" class="w-5 h-5"></i>
        </a>
        <a href="https://www.instagram.com/marcos.dataproduct/" target="_blank" rel="noopener noreferrer" class="p-2.5 rounded-lg hover:text-white hover:bg-white/5 transition-colors" aria-label="Instagram">
          <i data-lucide="instagram" class="w-5 h-5"></i>
        </a>
      </div>
    </div>
    <div class="max-w-7xl mx-auto mt-8 pt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#64748b]">
      <p>&copy; 2026 Marcos Data Product. Todos os direitos reservados.</p>
      <div class="flex items-center gap-4">
        <span>Curadoria por Marcos Aurélio</span>
      </div>
    </div>
  </footer>

  <script>
    document.addEventListener("DOMContentLoaded", function() {{
      if (window.lucide && typeof lucide.createIcons === 'function') {{
        lucide.createIcons();
      }}
    }});
  </script>
</body>
</html>'''

    out_file = os.path.join(BIBLIOTECA_OUT_DIR, f"{slug}.html")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"[OK] Página de livro gerada: {out_file}")
    return out_file

def build_all():
    books = load_books()
    if not os.path.exists(BIBLIOTECA_HTML_PATH):
        return False
        
    with open(BIBLIOTECA_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Gerar página individual para CADA livro
    for b in books:
        generate_book_page(b, books)

    # 2. Atualizar EMBEDDED_BOOKS no JS de biblioteca.html
    books_json_str = json.dumps(books, ensure_ascii=False, indent=2).replace('</script>', '<\\/script>')
    m = re.search(r'const EMBEDDED_BOOKS\s*=\s*\[.*?\];\s*(?=let allBooks)', content, re.DOTALL)
    if not m:
        m = re.search(r'const EMBEDDED_BOOKS\s*=\s*\[.*?\];', content, re.DOTALL)
    if m:
        content = content[:m.start()] + f'const EMBEDDED_BOOKS = {books_json_str};\n      ' + content[m.end():]

    # 3. Pré-renderizar Grid de Destaques
    destaques = [b for b in books if b.get('destaque')]
    destaques_cards = '\n'.join(render_destaque_book_card(b) for b in destaques)
    pattern_destaques = re.compile(r'(<div\s+id=["\']destaques-grid["\'][^>]*>).*?(</div>\s*</div>\s*</section>)', re.DOTALL)
    content = pattern_destaques.sub(f'\\1\n{destaques_cards}\n        \\2', content)

    # 4. Pré-renderizar Cada Categoria e Atualizar Seções
    for cat in CATEGORIES:
        cat_books = [b for b in books if get_effective_category(b) == cat]
        cat_cards = '\n'.join(render_primer_book_card(b) for b in cat_books)
        
        pattern_grid = re.compile(rf'(<div\s+id=["\']{cat}-grid["\'][^>]*>).*?(</div>\s*</section>)', re.DOTALL)
        content = pattern_grid.sub(f'\\1\n{cat_cards}\n            \\2', content)

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

    # 5. Atualizar contadores estáticos
    total_books = len(books)
    destaques_count = len(destaques)
    content = re.sub(r'<span\s+id=["\']results-count["\']>\d+</span>', f'<span id="results-count">{total_books}</span>', content)
    content = re.sub(r'<span\s+id=["\']destaques-badge-count["\']>\d+</span>', f'<span id="destaques-badge-count">{destaques_count}</span>', content)
    content = re.sub(r'<span\s+class=["\']text-slate-400 font-mono["\']\s+id=["\']filter-count-cat-all["\']>\d+</span>', f'<span class="text-slate-400 font-mono" id="filter-count-cat-all">{total_books}</span>', content)

    for cat in CATEGORIES:
        cnt = len([b for b in books if get_effective_category(b) == cat])
        content = re.sub(rf'<span\s+class=["\']text-slate-400 font-mono["\']\s+id=["\']filter-count-cat-{cat}["\']>\d+</span>', f'<span class="text-slate-400 font-mono" id="filter-count-cat-{cat}">{cnt}</span>', content)
        content = re.sub(rf'<span\s+id=["\']pill-count-{cat}["\']>\d+</span>', f'<span id="pill-count-{cat}">{cnt}</span>', content)

    # 6. Gerar JSON-LD ItemList
    itemlist_elements = []
    for idx, b in enumerate(books, start=1):
        b_slug = b.get('slug') or b.get('id')
        itemlist_elements.append({
            "@type": "ListItem",
            "position": idx,
            "item": {
                "@type": "Book",
                "name": b.get("title", ""),
                "author": {"@type": "Person", "name": b.get("author", "")},
                "image": f"https://marcosdataproduct.com/{b.get('cover_image', '').lstrip('/')}",
                "description": b.get("short_desc", ""),
                "url": f"https://marcosdataproduct.com/biblioteca/{b_slug}"
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

    if 'id="schema-itemlist"' in content:
        content = re.sub(r'<script\s+type=["\']application/ld\+json["\']\s+id=["\']schema-itemlist["\']>.*?</script>', f'<script type="application/ld+json" id="schema-itemlist">\n{jsonld_str}\n  </script>', content, flags=re.DOTALL)
    else:
        content = content.replace('</head>', f'  <script type="application/ld+json" id="schema-itemlist">\n{jsonld_str}\n  </script>\n</head>')

    atomic_write(BIBLIOTECA_HTML_PATH, content)
    print(f"[OK] biblioteca.html compilada com {total_books} livros e páginas individuais geradas.")

    update_home_books(books)
    build_sitemap()
    return True

if __name__ == '__main__':
    build_all()
