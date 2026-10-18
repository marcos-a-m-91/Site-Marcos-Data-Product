import os
import json
import re
import html
import time

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Localizar o diretório do site
possible_paths = [
    os.path.abspath(os.path.join(APP_DIR, '..', 'Site-Marcos-Data-Product')),
    os.path.abspath(os.path.join(APP_DIR, 'Site-Marcos-Data-Product')),
    os.path.abspath(os.path.join(APP_DIR, '..'))
]
SITE_DIR = next((p for p in possible_paths if os.path.exists(os.path.join(p, 'biblioteca.html'))), possible_paths[0])

CONTENT_DIR = os.path.join(SITE_DIR, 'content')
BOOKS_JSON_PATH = os.path.join(CONTENT_DIR, 'books.json')
BIBLIOTECA_HTML_PATH = os.path.join(SITE_DIR, 'biblioteca.html')
INDEX_HTML_PATH = os.path.join(SITE_DIR, 'index.html')
COVERS_DIR = os.path.join(SITE_DIR, 'assets', 'img', 'Biblioteca page')

os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

def atomic_write(filepath, content, retries=5, delay=0.2):
    """
    Gravação atômica com arquivo temporário e substituição instantânea.
    Protege contra travamento de arquivo do Google Drive ou corrupção por escrita incompleta.
    """
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
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    return True
                except Exception as e:
                    print(f"Erro ao gravar {filepath}: {e}")
                    raise e
        except Exception as e:
            print(f"Erro inesperado ao gravar {filepath}: {e}")
            raise e

TAG_COLORS = {
    'dados': 'blue',
    'visualização': 'emerald',
    'visualizacao': 'emerald',
    'produto': 'purple',
    'tecnologia': 'pink',
    'negócios': 'amber',
    'negocios': 'amber',
    'comportamento': 'orange',
    'finanças': 'green',
    'financas': 'green',
    'ia': 'indigo',
    'inteligência artificial': 'indigo',
    'inteligencia artificial': 'indigo',
    'liderança': 'rose',
    'lideranca': 'rose',
    'estratégia': 'cyan',
    'estrategia': 'cyan',
    'estatística': 'cyan',
    'estatistica': 'cyan'
}

def get_tag_color(tag):
    tag_clean = tag.strip().lower()
    return TAG_COLORS.get(tag_clean, 'blue')

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

def normalize_books(books):
    for b in books:
        if not b.get('category'):
            tags_list = [t.lower() for t in b.get('tags', [])]
            title_lower = (b.get('title') or '').lower()
            text = ' ' + ' '.join(tags_list) + ' ' + title_lower + ' '

            if any(k in text for k in ['dado', 'estatistica', 'estatística', 'analise', 'análise', 'analytics', 'sql', 'bi ']):
                b['category'] = 'dados'
            elif any(k in text for k in ['produto', 'ux', 'discovery', 'design thinking']):
                b['category'] = 'produto'
            elif any(k in text for k in ['habito', 'hábito', 'mentalidade', 'comportamento', 'psicolog', 'mindset']):
                b['category'] = 'mentalidade'
            elif any(k in text for k in ['negocio', 'negócio', 'estrategia', 'estratégia', 'finan', 'gestao', 'gestão', 'economia']):
                b['category'] = 'negocios'
            elif any(k in text for k in ['tecno', 'python', 'inteligência artificial', 'inteligencia artificial', 'software', 'dev', 'computa']) or ' ia ' in text or ' ai ' in text:
                b['category'] = 'tecnologia'
            elif any(k in text for k in ['carreira', 'lideran', 'liderança', 'trabalho']):
                b['category'] = 'carreira'
            elif any(k in text for k in ['sociedade', 'filosofia', 'etica', 'ética', 'cultura']):
                b['category'] = 'sociedade'
            else:
                b['category'] = 'dados'
        if b.get('destaque') is None:
            b['destaque'] = True
        try:
            b['rating'] = float(b.get('rating', 4.8))
        except (ValueError, TypeError):
            b['rating'] = 4.8
    return books

def save_books(books):
    books = normalize_books(books)
    os.makedirs(CONTENT_DIR, exist_ok=True)
    books_json_str = json.dumps(books, ensure_ascii=False, indent=2)
    atomic_write(BOOKS_JSON_PATH, books_json_str)
    return build_all()

def render_book_card(book):
    title = html.escape(book.get('title', 'Sem título'), quote=True)
    author = html.escape(book.get('author', 'Autor desconhecido'), quote=True)
    amazon_link = html.escape(book.get('amazon_link', '#'), quote=True)
    cover_image = book.get('cover_image', 'assets/img/books/cover-estatistica-o-que-e.webp')
    short_desc = html.escape(book.get('short_desc', ''), quote=False)
    desc_full = html.escape(book.get('desc_full', ''), quote=True)
    
    tags = book.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    
    tags_str = ' '.join(t.lower() for t in tags)
    
    tag_spans = []
    for t in tags:
        c = get_tag_color(t)
        t_label = html.escape(t, quote=False)
        tag_spans.append(
            f'<span class="px-2.5 py-1 rounded-md border border-{c}-500/20 bg-{c}-500/10 text-{c}-400 text-[10px] font-semibold uppercase tracking-wider">{t_label}</span>'
        )
    tags_html = '\n            '.join(tag_spans)
    
    return f'''      <!-- Livro: {title} -->
      <div class="book-card reveal glass bg-black/50 backdrop-blur-2xl rounded-2xl overflow-hidden flex flex-col group hover:scale-[1.02] hover:border-white/20 transition-all duration-300 hover:shadow-[0_8px_32px_rgba(96,165,250,0.15)] cursor-pointer" 
        data-tags="{tags_str}"
        data-title="{title}"
        data-author="{author}"
        data-link="{amazon_link}"
        data-desc-full="{desc_full}">
        <div class="w-full aspect-[2/3] overflow-hidden bg-white/5 relative pointer-events-none">
          <img src="{cover_image}" alt="{title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
        </div>
        <div class="p-5 sm:p-6 flex flex-col flex-1 pointer-events-none">
          <h3 class="text-lg font-bold text-white mb-1 tracking-tight" style="font-family:'Space Grotesk',sans-serif">{title}</h3>
          <p class="text-sm text-white/50 mb-4" style="font-family:'Manrope',sans-serif">{author}</p>
          <p class="text-white/60 text-sm leading-relaxed mb-6 line-clamp-3" style="font-family:'Manrope',sans-serif">{short_desc}</p>
          
          <div class="flex flex-wrap gap-2 mb-6 mt-auto">
            {tags_html}
          </div>

          <div class="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl border border-white/10 text-white/80 text-sm font-medium group-hover:bg-white/10 group-hover:border-white/20 group-hover:text-white transition-all">
            Ver detalhes
            <i data-lucide="plus" class="w-4 h-4 text-white/50 group-hover:text-white"></i>
          </div>
        </div>
      </div>'''

def render_home_book_card(book):
    title = html.escape(book.get('title', 'Sem título'), quote=True)
    author = html.escape(book.get('author', 'Autor desconhecido'), quote=True)
    cover_image = book.get('cover_image', 'assets/img/books/cover-estatistica-o-que-e.webp')
    
    return f'''          <!-- Livro: {title} -->
          <a href="biblioteca.html" class="flex flex-col group" title="{title}">
            <div class="w-full aspect-[2/3] rounded-lg overflow-hidden book-shadow mb-2.5 bg-[#ffffff] p-1 flex items-center justify-center border border-[#d0d7de]">
              <img src="{cover_image}" alt="{title} - {author}" class="w-full h-full object-contain" onerror="this.onerror=null; this.src='assets/img/books/cover-estatistica-o-que-e.webp';" />
            </div>
            <h3 class="font-bold text-xs text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-tight line-clamp-2">
              {title}
            </h3>
            <span class="text-[10px] text-[#656d76] mt-0.5 line-clamp-1">{author}</span>
          </a>'''

def update_home_books(books):
    if not os.path.exists(INDEX_HTML_PATH):
        print(f'Arquivo {INDEX_HTML_PATH} não encontrado.')
        return False
        
    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Priorizar livros marcados como destaque (ou os mais recentes)
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
    else:
        leituras_idx = content.find('Leituras & Repertório')
        if leituras_idx == -1:
            leituras_idx = content.find('3 Capas de Livros')
        if leituras_idx == -1:
            print("Seção de Leituras não encontrada em index.html")
            return False
            
        grid_start_tag = '<div class="grid grid-cols-3 gap-3.5">'
        g_start = content.find(grid_start_tag, leituras_idx)
        if g_start == -1:
            print("Grid de livros não encontrado em index.html")
            return False
            
        g_end = content.find('</div>', g_start)
        new_grid = f'{grid_start_tag}\n\n          {start_marker}\n\n{cards_html}\n\n          {end_marker}\n        '
        new_content = content[:g_start] + new_grid + content[g_end:]

    atomic_write(INDEX_HTML_PATH, new_content)
    print(f'Home (index.html) atualizada com sucesso! {len(featured_books)} destaques sincronizados.')
    return True

def build_all():
    books = normalize_books(load_books())
    if not os.path.exists(BIBLIOTECA_HTML_PATH):
        print(f'Arquivo {BIBLIOTECA_HTML_PATH} não encontrado.')
        return False
        
    with open(BIBLIOTECA_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content
    books_json_str = json.dumps(books, ensure_ascii=False, indent=2).replace('</script>', '<\\/script>')

    # 1. Atualizar EMBEDDED_BOOKS em biblioteca.html com fatiamento direto (evita re.sub corromper escapes como \n)
    m = re.search(r'const EMBEDDED_BOOKS\s*=\s*\[.*?\];\s*(?=let allBooks)', new_content, re.DOTALL)
    if not m:
        m = re.search(r'const EMBEDDED_BOOKS\s*=\s*\[.*?\];', new_content, re.DOTALL)
    if m:
        new_content = new_content[:m.start()] + f'const EMBEDDED_BOOKS = {books_json_str};\n      ' + new_content[m.end():]

    # 2. Atualizar marcação estática se existir
    cards_html = '\n\n'.join(render_book_card(b) for b in books)
    start_marker = '<!-- BOOKS_GRID_START -->'
    end_marker = '<!-- BOOKS_GRID_END -->'
    
    if start_marker in new_content and end_marker in new_content:
        pattern = re.compile(f'{re.escape(start_marker)}.*?{re.escape(end_marker)}', re.DOTALL)
        new_content = pattern.sub(f'{start_marker}\n\n{cards_html}\n\n      {end_marker}', new_content)
    else:
        pattern = re.compile(r'(<div[^>]*id=["\']books-grid["\'][^>]*>)(.*?)(</div>\s*</section>\s*<!-- MODAL)', re.DOTALL)
        if pattern.search(new_content):
            new_content = pattern.sub(f'\\1\n\n      {start_marker}\n\n{cards_html}\n\n      {end_marker}\n    \\3', new_content)
        
    atomic_write(BIBLIOTECA_HTML_PATH, new_content)
    print(f'Biblioteca compilada com sucesso! {len(books)} livros atualizados em {BIBLIOTECA_HTML_PATH}')
    
    # 3. Atualizar destaques da biblioteca na Home (index.html)
    update_home_books(books)
    return True

if __name__ == '__main__':
    build_all()
