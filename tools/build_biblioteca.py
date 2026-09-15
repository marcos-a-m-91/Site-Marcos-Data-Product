import os
import json
import re
import html

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
COVERS_DIR = os.path.join(SITE_DIR, 'assets', 'img', 'Biblioteca page')

os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

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
    'estrategia': 'cyan'
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

def save_books(books):
    os.makedirs(CONTENT_DIR, exist_ok=True)
    with open(BOOKS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    return build_all()

def render_book_card(book):
    title = html.escape(book.get('title', 'Sem título'), quote=True)
    author = html.escape(book.get('author', 'Autor desconhecido'), quote=True)
    amazon_link = html.escape(book.get('amazon_link', '#'), quote=True)
    cover_image = book.get('cover_image', 'assets/img/Biblioteca page/Estatística O que é, para que serve, como funciona.webp')
    short_desc = html.escape(book.get('short_desc', ''), quote=False)
    desc_full = html.escape(book.get('desc_full', ''), quote=True)
    
    tags = book.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    
    tags_str = ' '.join(t.lower() for t in tags)
    
    tag_spans = []
    for t in tags:
        c = get_tag_color(t)
        t_label = html.escape(t.title(), quote=False)
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

def build_all():
    books = load_books()
    if not os.path.exists(BIBLIOTECA_HTML_PATH):
        print(f'Arquivo {BIBLIOTECA_HTML_PATH} não encontrado.')
        return False
        
    with open(BIBLIOTECA_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    cards_html = '\n\n'.join(render_book_card(b) for b in books)
    
    start_marker = '<!-- BOOKS_GRID_START -->'
    end_marker = '<!-- BOOKS_GRID_END -->'
    
    if start_marker in content and end_marker in content:
        pattern = re.compile(f'{re.escape(start_marker)}.*?{re.escape(end_marker)}', re.DOTALL)
        new_content = pattern.sub(f'{start_marker}\n\n{cards_html}\n\n      {end_marker}', content)
    else:
        pattern = re.compile(r'(<div[^>]*id=["\']books-grid["\'][^>]*>)(.*?)(</div>\s*</section>\s*<!-- MODAL)', re.DOTALL)
        if not pattern.search(content):
            print('Aviso: Estrutura de books-grid não encontrada em biblioteca.html')
            return False
        new_content = pattern.sub(f'\\1\n\n      {start_marker}\n\n{cards_html}\n\n      {end_marker}\n    \\3', content)
        
    with open(BIBLIOTECA_HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f'Biblioteca compilada com sucesso! {len(books)} livros atualizados em {BIBLIOTECA_HTML_PATH}')
    return True

if __name__ == '__main__':
    build_all()
