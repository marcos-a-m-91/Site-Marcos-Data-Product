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
SITE_DIR = next((p for p in possible_paths if os.path.exists(os.path.join(p, 'projetos.html'))), possible_paths[0])

CONTENT_DIR = os.path.join(SITE_DIR, 'content')
PROJECTS_JSON_PATH = os.path.join(CONTENT_DIR, 'projects.json')
PROJETOS_HTML_PATH = os.path.join(SITE_DIR, 'projetos.html')
INDEX_HTML_PATH = os.path.join(SITE_DIR, 'index.html')

os.makedirs(CONTENT_DIR, exist_ok=True)

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

CATEGORY_CONFIG = {
    'analytics': {
        'label': 'Analytics & Risco',
        'badge_class': 'badge-theme-analytics',
        'icon': 'trending-up',
        'tag_label': 'ANALYTICS'
    },
    'dataviz': {
        'label': 'Power BI & DataViz',
        'badge_class': 'badge-theme-dataviz',
        'icon': 'pie-chart',
        'tag_label': 'POWER BI'
    },
    'data': {
        'label': 'Engenharia de Dados',
        'badge_class': 'badge-theme-data',
        'icon': 'database',
        'tag_label': 'DATA ENGINEERING'
    },
    'ai': {
        'label': 'Inteligência Artificial',
        'badge_class': 'badge-theme-ai',
        'icon': 'cpu',
        'tag_label': 'INTELIGÊNCIA ARTIFICIAL'
    },
    'product': {
        'label': 'Product Analytics',
        'badge_class': 'badge-theme-product',
        'icon': 'package',
        'tag_label': 'PRODUCT ANALYTICS'
    },
    'business': {
        'label': 'Business Analytics',
        'badge_class': 'badge-theme-business',
        'icon': 'briefcase',
        'tag_label': 'BUSINESS ANALYTICS'
    }
}

def load_projects():
    if not os.path.exists(PROJECTS_JSON_PATH):
        return []
    try:
        with open(PROJECTS_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Erro ao ler {PROJECTS_JSON_PATH}: {e}")
        return []

def render_home_project_card(p):
    cat_key = p.get('category', 'analytics').lower()
    cat_info = CATEGORY_CONFIG.get(cat_key, CATEGORY_CONFIG['analytics'])
    tag_label = p.get('tag_label') or cat_info['tag_label']
    title = html.escape(p.get('title', 'Sem título'))
    excerpt = html.escape(p.get('short_desc', p.get('excerpt', '')))
    cover = p.get('image', p.get('cover', 'assets/img/projects/project-sales-dashboard.svg'))
    href = p.get('href', 'projetos.html')

    return f'''          <!-- Projeto: {title} -->
          <a href="{href}" class="card-hover-clean bg-white rounded-2xl border border-[#d0d7de] overflow-hidden flex flex-col group">
            <div class="h-32 bg-[#070f1e] overflow-hidden flex items-center justify-center p-1.5 border-b border-[#d0d7de]">
              <img src="{cover}" alt="{title}" class="w-full h-full object-cover rounded-lg" />
            </div>
            <div class="p-4 flex-1 flex flex-col justify-between">
              <div>
                <span class="inline-block px-2 py-0.5 rounded bg-[#11376e] text-white text-[10px] font-semibold uppercase tracking-wider mb-2">
                  {tag_label}
                </span>
                <h3 class="font-bold text-xs sm:text-sm text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug mb-1">
                  {title}
                </h3>
                <p class="text-[11px] text-[#656d76] line-clamp-2 leading-relaxed">
                  {excerpt}
                </p>
              </div>
            </div>
          </a>'''

def render_projetos_page_card(p):
    cat_key = p.get('category', 'analytics').lower()
    cat_info = CATEGORY_CONFIG.get(cat_key, CATEGORY_CONFIG['analytics'])
    cat_label = p.get('category_label') or cat_info['label']
    badge_cls = cat_info['badge_class']
    title = html.escape(p.get('title', 'Sem título'))
    excerpt = html.escape(p.get('description', p.get('excerpt', '')))
    cover = p.get('image', p.get('cover', 'assets/img/projects/project-sales-dashboard.svg'))
    sector = html.escape(p.get('sector', 'Analytics'))
    metric = html.escape(p.get('metric', ''))
    metric_label = html.escape(p.get('metric_label', 'Impacto mensurável'))
    href = p.get('href', '#')
    stack = p.get('stack', [])
    stack_tags = ' '.join(str(s).lower() for s in stack)
    tech_attr = f"{title.lower()} {cat_key} {sector.lower()} {stack_tags}"

    stack_html = '\n'.join(f'              <span class="px-2 py-0.5 bg-[#f6f8fa] border border-[#d0d7de] text-[#656d76] rounded text-xs font-medium">{html.escape(s)}</span>' for s in stack[:4])

    metric_markup = ''
    if metric:
        metric_markup = f'''            <!-- Callout de Métrica -->
            <div class="bg-[#f6f8fa] rounded-xl p-3 mb-5 flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-[#11376e]/10 text-[#11376e] flex items-center justify-center shrink-0">
                <i data-lucide="zap" class="w-4 h-4"></i>
              </div>
              <div class="text-xs text-[#1f2328] font-medium leading-tight">
                <strong class="text-[#11376e]">{metric}</strong> {metric_label}
              </div>
            </div>'''

    return f'''      <!-- PROJETO: {title} -->
      <article
        class="project-card bg-white rounded-2xl border border-[#d0d7de] overflow-hidden flex flex-col card-hover-clean group cursor-pointer"
        data-category="{cat_key}"
        data-href="{href}"
        data-tech="{tech_attr}">
        <!-- Visual Header -->
        <div class="aspect-[16/10] bg-[#07101e] relative overflow-hidden flex items-center justify-center border-b border-[#d0d7de]">
          <img src="{cover}" alt="{title}" class="w-full h-full object-cover" />
          <div class="absolute top-3.5 left-3.5 z-10 flex items-center gap-2">
            <span class="px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider bg-[#0b1e3a]/90 text-white backdrop-blur-md border border-white/10 shadow-sm flex items-center gap-1.5">
              <i data-lucide="building-2" class="w-3 h-3 text-[#38bdf8]"></i>
              {sector}
            </span>
          </div>
        </div>

        <!-- Body -->
        <div class="p-6 flex-1 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between gap-2 mb-2.5">
              <span class="{badge_cls} inline-block px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider">
                {cat_label}
              </span>
            </div>

            <h3 class="font-bold text-lg text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug mb-2.5">
              {title}
            </h3>

            <p class="text-xs sm:text-sm text-[#656d76] leading-relaxed mb-5">
              {excerpt}
            </p>

{metric_markup}
          </div>

          <!-- Bottom Footer -->
          <div>
            <div class="flex flex-wrap gap-1.5 mb-5">
{stack_html}
            </div>

            <a href="{href}"
              class="w-full px-4 py-2.5 rounded-xl bg-[#f6f8fa] hover:bg-[#11376e] border border-[#d0d7de] hover:border-[#11376e] text-[#1f2328] hover:text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer group/btn">
              <span>Ver Detalhes do Projeto</span>
              <i data-lucide="arrow-right" class="w-3.5 h-3.5 group-hover/btn:translate-x-1 transition-transform"></i>
            </a>
          </div>
        </div>
      </article>'''

def update_home_projects(projects):
    if not os.path.exists(INDEX_HTML_PATH):
        print(f"Arquivo {INDEX_HTML_PATH} não encontrado.")
        return False

    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    start_marker = "<!-- HOME_PROJECTS_START -->"
    end_marker = "<!-- HOME_PROJECTS_END -->"

    featured = [p for p in projects if p.get('featured_home', True)][:3]

    if not featured:
        # Estado Vazio elegante sincronizado na Home
        inner_html = '''          <div class="col-span-1 sm:col-span-3 bg-white rounded-2xl border border-[#d0d7de] p-8 text-center">
            <div class="w-12 h-12 rounded-xl bg-[#11376e]/10 text-[#11376e] flex items-center justify-center mx-auto mb-3">
              <i data-lucide="folder-kanban" class="w-6 h-6"></i>
            </div>
            <h3 class="text-sm font-bold text-[#1f2328] mb-1">Novos projetos em desenvolvimento</h3>
            <p class="text-xs text-[#656d76] max-w-sm mx-auto leading-relaxed">
              Casos de estudo práticos em Power BI, Databricks e Analytics estão sendo preparados. Em breve estarão disponíveis aqui e na página de projetos.
            </p>
          </div>'''
    else:
        inner_html = '\n\n'.join(render_home_project_card(p) for p in featured)

    if start_marker in content and end_marker in content:
        pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
        new_content = pattern.sub(f"{start_marker}\n\n{inner_html}\n\n          {end_marker}", content)
    else:
        # Localizar bloco de projetos na Home
        target_re = re.compile(r'(<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">)(.*?)(</div>\s*</div>\s*<!-- ── BLOCO DIREITO)', re.DOTALL)
        if target_re.search(content):
            new_content = target_re.sub(f"\\1\n          {start_marker}\n\n{inner_html}\n\n          {end_marker}\n        \\3", content)
        else:
            print("Não foi possível localizar o container de projetos em index.html")
            return False

    atomic_write(INDEX_HTML_PATH, new_content)
    print(f"Home (index.html) sincronizada: {len(featured)} projetos refletidos.")
    return True

def update_projetos_html(projects):
    if not os.path.exists(PROJETOS_HTML_PATH):
        print(f"Arquivo {PROJETOS_HTML_PATH} não encontrado.")
        return False

    with open(PROJETOS_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    start_marker = "<!-- PROJECTS_GRID_START -->"
    end_marker = "<!-- PROJECTS_GRID_END -->"

    count = len(projects)
    counter_text = f"{count} {'projeto' if count == 1 else 'projetos'}"

    # 1. Atualizar contadores
    content = re.sub(
        r'<span class="text-xs opacity-80 font-mono font-semibold" id="pill-count-all">.*?</span>',
        f'<span class="text-xs opacity-80 font-mono font-semibold" id="pill-count-all">({count})</span>',
        content
    )
    content = re.sub(
        r'<span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-\[#656d76\]"\s+id="project-counter">.*?</span>',
        f'<span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-[#656d76]"\n          id="project-counter">{counter_text}</span>',
        content
    )

    # 2. Atualizar cards no grid
    if not projects:
        grid_inner = '      <!-- Nenhum projeto publicado no momento -->'
        # Garantir que o empty-projects-state fique visível
        content = content.replace('id="empty-projects-state" class="hidden ', 'id="empty-projects-state" class="')
    else:
        grid_inner = '\n\n'.join(render_projetos_page_card(p) for p in projects)
        # Ocultar o empty-projects-state se houver projetos
        if 'id="empty-projects-state" class="' in content and 'hidden' not in content.split('id="empty-projects-state"')[1].split('>')[0]:
            content = content.replace('id="empty-projects-state" class="', 'id="empty-projects-state" class="hidden ')

    if start_marker in content and end_marker in content:
        pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
        content = pattern.sub(f"{start_marker}\n\n{grid_inner}\n\n    {end_marker}", content)
    else:
        # Inserir marcadores no container #projects-grid
        grid_re = re.compile(r'(<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8" id="projects-grid">)(.*?)(</div>)', re.DOTALL)
        if grid_re.search(content):
            content = grid_re.sub(f"\\1\n      {start_marker}\n\n{grid_inner}\n\n      {end_marker}\n    \\3", content)

    atomic_write(PROJETOS_HTML_PATH, content)
    print(f"Página Projetos (projetos.html) sincronizada: {count} projetos atualizados.")
    return True

def build_all():
    projects = load_projects()
    update_projetos_html(projects)
    update_home_projects(projects)

if __name__ == '__main__':
    build_all()
