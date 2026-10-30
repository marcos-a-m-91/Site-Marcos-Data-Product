import os
import json
import re
import html
import time
from build_sitemap import build_sitemap

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(ROOT_DIR, 'content')
PROJECTS_JSON_PATH = os.path.join(CONTENT_DIR, 'projects.json')
PROJETOS_HTML_PATH = os.path.join(ROOT_DIR, 'projetos.html')
INDEX_HTML_PATH = os.path.join(ROOT_DIR, 'index.html')

os.makedirs(CONTENT_DIR, exist_ok=True)

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
    href = p.get('href', '/projetos')

    return f'''          <!-- Projeto: {title} -->
          <a href="{href}" class="card-hover-clean bg-white rounded-2xl border border-[#d0d7de] overflow-hidden flex flex-col group">
            <div class="h-32 bg-[#070f1e] overflow-hidden flex items-center justify-center p-1.5 border-b border-[#d0d7de]">
              <img src="{cover}" alt="{title}" class="w-full h-full object-cover rounded-lg" width="400" height="240" loading="lazy" decoding="async" />
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
    metric_label = html.escape(p.get('metric_label', 'Impacto'))
    href = p.get('href', '/projetos')

    stack = p.get('stack', [])
    stack_html = '\n'.join(
        f'              <span class="px-2 py-0.5 rounded bg-[#f6f8fa] border border-[#d0d7de] text-[#1f2328] text-[10px] font-semibold font-mono">{html.escape(s)}</span>'
        for s in stack[:4]
    )

    metric_markup = ""
    if metric:
        metric_markup = f'''            <div class="flex items-center gap-3 p-3 rounded-xl bg-[#f6f8fa] border border-[#d0d7de] mb-5">
              <span class="text-xs font-bold text-[#11376e] font-mono">{metric}</span>
              <span class="text-[11px] text-[#656d76]">{metric_label}</span>
            </div>'''

    return f'''      <!-- Projeto: {title} -->
      <article class="project-card bg-white rounded-2xl border border-[#d0d7de] overflow-hidden flex flex-col card-hover-clean group" data-category="{cat_key}">
        <div class="h-48 bg-[#0b1e3a] relative overflow-hidden flex items-center justify-center p-3 border-b border-[#d0d7de]">
          <img src="{cover}" alt="{title}" class="w-full h-full object-cover rounded-lg group-hover:scale-102 transition-transform duration-300" width="600" height="360" loading="lazy" decoding="async" />
        </div>
        <div class="p-6 flex-1 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between gap-2 mb-3">
              <span class="text-xs font-semibold px-2.5 py-1 rounded-md {badge_cls}">
                {cat_label}
              </span>
              <span class="text-[11px] text-[#656d76] font-medium">{sector}</span>
            </div>
            <h3 class="font-bold text-base sm:text-lg text-[#1f2328] group-hover:text-[#11376e] transition-colors leading-snug mb-2">
              {title}
            </h3>
            <p class="text-xs sm:text-sm text-[#656d76] leading-relaxed mb-5">
              {excerpt}
            </p>
{metric_markup}
          </div>
          <div>
            <div class="flex flex-wrap gap-1.5 mb-5">
{stack_html}
            </div>
            <a href="{href}" class="w-full px-4 py-2.5 rounded-xl bg-[#f6f8fa] hover:bg-[#11376e] border border-[#d0d7de] hover:border-[#11376e] text-[#1f2328] hover:text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer group/btn">
              <span>Ver Detalhes do Projeto</span>
              <i data-lucide="arrow-right" class="w-3.5 h-3.5 group-hover/btn:translate-x-1 transition-transform"></i>
            </a>
          </div>
        </div>
      </article>'''

def update_home_projects(projects):
    if not os.path.exists(INDEX_HTML_PATH):
        return False

    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    start_marker = "<!-- HOME_PROJECTS_START -->"
    end_marker = "<!-- HOME_PROJECTS_END -->"

    featured = [p for p in projects if p.get('featured_home', True)][:3]

    if not featured:
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
        target_re = re.compile(r'(<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">)(.*?)(</div>\s*</div>\s*<!-- ── BLOCO DIREITO)', re.DOTALL)
        if target_re.search(content):
            new_content = target_re.sub(f"\\1\n          {start_marker}\n\n{inner_html}\n\n          {end_marker}\n        \\3", content)
        else:
            return False

    atomic_write(INDEX_HTML_PATH, new_content)
    print(f"[OK] Home (index.html) sincronizada: {len(featured)} projetos refletidos.")
    return True

def update_projetos_html(projects):
    if not os.path.exists(PROJETOS_HTML_PATH):
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
        content = content.replace('id="empty-projects-state" class="hidden ', 'id="empty-projects-state" class="')
    else:
        grid_inner = '\n\n'.join(render_projetos_page_card(p) for p in projects)
        if 'id="empty-projects-state" class="' in content and 'hidden' not in content.split('id="empty-projects-state"')[1].split('>')[0]:
            content = content.replace('id="empty-projects-state" class="', 'id="empty-projects-state" class="hidden ')

    if start_marker in content and end_marker in content:
        pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
        content = pattern.sub(f"{start_marker}\n\n{grid_inner}\n\n      {end_marker}", content)
    else:
        grid_re = re.compile(r'(<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8" id="projects-grid">)(.*?)(</div>)', re.DOTALL)
        if grid_re.search(content):
            content = grid_re.sub(f"\\1\n      {start_marker}\n\n{grid_inner}\n\n      {end_marker}\n    \\3", content)

    atomic_write(PROJETOS_HTML_PATH, content)
    print(f"[OK] Página Projetos (projetos.html) sincronizada: {count} projetos atualizados.")
    return True

def build_all():
    projects = load_projects()
    update_projetos_html(projects)
    update_home_projects(projects)
    build_sitemap()

if __name__ == '__main__':
    build_all()
