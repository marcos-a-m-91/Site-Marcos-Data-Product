"""
Script de atualização e padronização completa de SEO, acessibilidade,
Core Web Vitals e links em todas as páginas HTML do site.
"""
import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def update_all_pages():
    print("=== ATUALIZANDO PÁGINAS HTML (SEO & PERFORMANCE) ===")

    # Componentes padrão reutilizáveis
    standard_footer = '''<footer class="bg-[#0b1e3a] text-white py-12 px-5 sm:px-8 border-t border-[#1e293b]">
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
        <a href="https://github.com/marcos-a-m-91" target="_blank" rel="noopener noreferrer" class="p-2.5 rounded-lg hover:text-white hover:bg-white/5 transition-colors" aria-label="GitHub">
          <i data-lucide="github" class="w-5 h-5"></i>
        </a>
        <a href="mailto:marcos.a.m@live.com" class="p-2.5 rounded-lg hover:text-white hover:bg-white/5 transition-colors" aria-label="E-mail">
          <i data-lucide="mail" class="w-5 h-5"></i>
        </a>
      </div>
    </div>
  </footer>'''

    standard_search_modal = '''<div class="p-4 max-h-[60vh] overflow-y-auto space-y-2" id="search-results">
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
              <div class="text-[10px] text-[#656d76]">Portfólio de soluções práticas</div>
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
      </div>'''

    footer_re = re.compile(r'<footer class="bg-\[#0b1e3a\].*?</footer>', re.DOTALL)
    search_re = re.compile(r'<div class="p-4 max-h-\[60vh\] overflow-y-auto space-y-2" id="search-results">.*?</div>\s*</div>\s*</div>', re.DOTALL)

    def apply_clean_urls_and_assets(text):
        text = text.replace('href="index.html"', 'href="/"')
        text = text.replace('href="blog.html"', 'href="/blog"')
        text = text.replace('href="projetos.html"', 'href="/projetos"')
        text = text.replace('href="biblioteca.html"', 'href="/biblioteca"')
        text = text.replace('href="sobre.html"', 'href="/sobre"')
        text = text.replace('href="assets/img/favicon.svg"', 'href="/assets/img/favicon.svg"')
        text = text.replace('href="favicon.ico"', 'href="/favicon.ico"')
        text = text.replace('href="assets/img/favicon-32x32.png"', 'href="/assets/img/favicon-32x32.png"')
        text = text.replace('href="assets/img/favicon-16x16.png"', 'href="/assets/img/favicon-16x16.png"')
        text = text.replace('href="assets/img/apple-touch-icon.png"', 'href="/assets/img/apple-touch-icon.png"')
        text = text.replace('href="assets/css/main.css"', 'href="/assets/css/main.css"')
        text = text.replace('<script src="assets/vendor/resource_3fa48481346f.js"></script>', '<link rel="stylesheet" href="/assets/css/tailwind.css">')
        text = text.replace('<script src="assets/vendor/lucide_latest_2eebd0ebe8c2.js"></script>', '<script defer src="/assets/vendor/lucide_latest_2eebd0ebe8c2.js"></script>')
        text = text.replace('<script src="assets/js/main.js"></script>', '<script defer src="/assets/js/main.js"></script>')
        return text

    # ─────────────────────────────────────────────────────────────
    # 1. INDEX.HTML (HOME)
    # ─────────────────────────────────────────────────────────────
    home_path = os.path.join(ROOT_DIR, 'index.html')
    with open(home_path, 'r', encoding='utf-8') as f:
        home = f.read()

    home = re.sub(r'<title>.*?</title>', '<title>Marcos Aurélio | Business Analytics, Power BI e Dados</title>', home)
    home = re.sub(
        r'<meta\s+name=["\']description["\']\s+content=["\'].*?["\']\s*/?>',
        '<meta name="description" content="Economista e especialista em Business Analytics (+10 anos de experiência) transformando dados brutos em decisões estratégicas. Conheça o trabalho." />',
        home
    )

    head_home = '''  <link rel="canonical" href="https://marcosdataproduct.com/" />
  <meta property="og:site_name" content="Marcos Data Product" />
  <meta property="og:locale" content="pt_BR" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://marcosdataproduct.com/" />
  <meta property="og:title" content="Marcos Aurélio | Business Analytics, Power BI e Dados" />
  <meta property="og:description" content="Economista e especialista em Business Analytics (+10 anos de experiência) transformando dados brutos em decisões estratégicas. Conheça o trabalho." />
  <meta property="og:image" content="https://marcosdataproduct.com/assets/img/og-default.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />

  <!-- Dados Estruturados JSON-LD (Schema.org) -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebSite",
        "@id": "https://marcosdataproduct.com/#website",
        "url": "https://marcosdataproduct.com/",
        "name": "Marcos Data Product",
        "description": "Business Analytics, Power BI e Inteligência Artificial por Marcos Aurélio",
        "publisher": {
          "@type": "Person",
          "@id": "https://marcosdataproduct.com/#person"
        }
      },
      {
        "@type": "Person",
        "@id": "https://marcosdataproduct.com/#person",
        "name": "Marcos Aurélio",
        "jobTitle": "Senior Business Analytics",
        "url": "https://marcosdataproduct.com/sobre",
        "image": "https://marcosdataproduct.com/assets/img/foto-marcos-aurelio.webp",
        "description": "Economista e especialista em Business Analytics, Power BI, Databricks e Inteligência Artificial.",
        "sameAs": [
          "https://www.linkedin.com/in/marcos-a-m-m",
          "https://github.com/marcos-a-m-91",
          "https://www.instagram.com/marcos.dataproduct/"
        ]
      }
    ]
  }
  </script>'''

    if '<link rel="canonical"' not in home:
        home = home.replace('<!-- ═══════════════════════════════════════════════\n       DEPENDENCIES', head_home + '\n\n  <!-- ═══════════════════════════════════════════════\n       DEPENDENCIES')

    home = apply_clean_urls_and_assets(home)

    # Hero image preload & background
    home = home.replace('href="assets/img/hero_section_home.jpg"', 'href="/assets/img/hero-home.webp"')
    home = home.replace("url('assets/img/hero_section_home.jpg')", "url('/assets/img/hero-home.webp')")

    # Logos e Fotos com width/height
    home = home.replace('<img src="assets/img/logo-clara.png" alt="Marcos Data Product Logo" class="h-8 sm:h-9 w-auto object-contain transition-opacity group-hover:opacity-90" />',
                        '<img src="/assets/img/logo-clara.webp" alt="Marcos Data Product" class="h-8 sm:h-9 w-auto object-contain transition-opacity group-hover:opacity-90" width="180" height="40" />')
    home = home.replace('<img src="assets/img/logo-clara.png" alt="Marcos Data Product" class="h-8 w-auto object-contain" />',
                        '<img src="/assets/img/logo-clara.webp" alt="Marcos Data Product" class="h-8 w-auto object-contain" width="180" height="40" />')
    home = home.replace('<img src="assets/img/logo-escura.png" alt="Marcos Data Product" class="h-8 w-auto object-contain transition-opacity group-hover:opacity-90" />',
                        '<img src="/assets/img/logo-escura.webp" alt="Marcos Data Product" class="h-8 w-auto object-contain transition-opacity group-hover:opacity-90" width="180" height="40" />')
    home = home.replace('<img src="assets/img/foto-marcos-aurelio.webp" alt="Marcos Aurélio" class="w-full h-full object-cover object-top" />',
                        '<img src="/assets/img/foto-marcos-aurelio.webp" alt="Marcos Aurélio" class="w-full h-full object-cover object-top" width="230" height="288" loading="lazy" decoding="async" />')

    # Footer e Busca
    home = footer_re.sub(standard_footer, home)
    home = search_re.sub(standard_search_modal + '\n    </div>\n  </div>', home)

    # Fix placeholder script image tags in home JS to have width/height
    home = home.replace('class="w-full h-full object-cover rounded-lg" />', 'class="w-full h-full object-cover rounded-lg" width="380" height="128" />')

    with open(home_path, 'w', encoding='utf-8') as f:
        f.write(home)
    print("[OK] index.html atualizado!")

    # ─────────────────────────────────────────────────────────────
    # 2. SOBRE.HTML
    # ─────────────────────────────────────────────────────────────
    sobre_path = os.path.join(ROOT_DIR, 'sobre.html')
    with open(sobre_path, 'r', encoding='utf-8') as f:
        sobre = f.read()

    sobre = apply_clean_urls_and_assets(sobre)

    # Corrigir SVGs da timeline que ainda não têm width/height
    sobre = sobre.replace('src="assets/img/icons-stacks/sql.svg" alt="" class="w-3.5 h-3.5 object-contain" />',
                          'src="/assets/img/icons-stacks/sql.svg" alt="" class="w-3.5 h-3.5 object-contain" width="14" height="14" loading="lazy" decoding="async" />')
    sobre = sobre.replace('src="assets/img/icons-stacks/databricks.svg" alt=""\n                      class="w-3.5 h-3.5 object-contain" />',
                          'src="/assets/img/icons-stacks/databricks.svg" alt="" class="w-3.5 h-3.5 object-contain" width="14" height="14" loading="lazy" decoding="async" />')
    sobre = sobre.replace('src="assets/img/icons-stacks/github.svg" alt="" class="w-3.5 h-3.5 object-contain" />',
                          'src="/assets/img/icons-stacks/github.svg" alt="" class="w-3.5 h-3.5 object-contain" width="14" height="14" loading="lazy" decoding="async" />')

    sobre = footer_re.sub(standard_footer, sobre)
    sobre = search_re.sub(standard_search_modal + '\n    </div>\n  </div>', sobre)

    with open(sobre_path, 'w', encoding='utf-8') as f:
        f.write(sobre)
    print("[OK] sobre.html atualizado!")

    # ─────────────────────────────────────────────────────────────
    # 3. BLOG.HTML
    # ─────────────────────────────────────────────────────────────
    blog_path = os.path.join(ROOT_DIR, 'blog.html')
    with open(blog_path, 'r', encoding='utf-8') as f:
        blog = f.read()

    blog = apply_clean_urls_and_assets(blog)

    # Corrigir picos de hierarquia: h4 nos cards flutuantes do hero para p
    blog = blog.replace('<h4 class="text-[10px] font-bold text-white line-clamp-2 leading-snug">',
                        '<p class="text-[10px] font-bold text-white line-clamp-2 leading-snug">')
    blog = blog.replace('</h4>\n                    </div>\n                  </a>',
                        '</p>\n                    </div>\n                  </a>')

    # Remover links obsoletos com .html
    blog = blog.replace('href="blog/media-moda-e-mediana.html"', 'href="/blog"')
    blog = blog.replace('href="blog/modelagem-star-schema-powerbi.html"', 'href="/blog"')

    blog = footer_re.sub(standard_footer, blog)
    blog = search_re.sub(standard_search_modal + '\n    </div>\n  </div>', blog)

    with open(blog_path, 'w', encoding='utf-8') as f:
        f.write(blog)
    print("[OK] blog.html atualizado!")

    # ─────────────────────────────────────────────────────────────
    # 4. PROJETOS.HTML
    # ─────────────────────────────────────────────────────────────
    proj_path = os.path.join(ROOT_DIR, 'projetos.html')
    with open(proj_path, 'r', encoding='utf-8') as f:
        proj = f.read()

    proj = apply_clean_urls_and_assets(proj)
    proj = proj.replace('href="blog/media-moda-e-mediana.html"', 'href="/blog"')
    proj = proj.replace('href="blog/modelagem-star-schema-powerbi.html"', 'href="/blog"')
    proj = footer_re.sub(standard_footer, proj)
    proj = search_re.sub(standard_search_modal + '\n    </div>\n  </div>', proj)

    with open(proj_path, 'w', encoding='utf-8') as f:
        f.write(proj)
    print("[OK] projetos.html atualizado!")

    # ─────────────────────────────────────────────────────────────
    # 5. BIBLIOTECA.HTML
    # ─────────────────────────────────────────────────────────────
    bib_path = os.path.join(ROOT_DIR, 'biblioteca.html')
    with open(bib_path, 'r', encoding='utf-8') as f:
        bib = f.read()

    bib = apply_clean_urls_and_assets(bib)

    # Modal dummy img tags: adicionar width e height
    bib = bib.replace('id="modal-blur" src="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 1 1\'%3E%3C/svg%3E"',
                      'id="modal-blur" width="300" height="400" src="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 1 1\'%3E%3C/svg%3E"')
    bib = bib.replace('id="modal-cover" src="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 1 1\'%3E%3C/svg%3E"',
                      'id="modal-cover" width="185" height="275" src="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 1 1\'%3E%3C/svg%3E"')

    bib = footer_re.sub(standard_footer, bib)
    bib = search_re.sub(standard_search_modal + '\n    </div>\n  </div>', bib)

    with open(bib_path, 'w', encoding='utf-8') as f:
        f.write(bib)
    print("[OK] biblioteca.html atualizado!")

    # ─────────────────────────────────────────────────────────────
    # 6. 404.HTML
    # ─────────────────────────────────────────────────────────────
    p404_path = os.path.join(ROOT_DIR, '404.html')
    with open(p404_path, 'r', encoding='utf-8') as f:
        p404 = f.read()

    p404 = apply_clean_urls_and_assets(p404)
    p404 = p404.replace('href="blog/media-moda-e-mediana.html"', 'href="/blog"')
    p404 = footer_re.sub(standard_footer, p404)
    p404 = search_re.sub(standard_search_modal + '\n    </div>\n  </div>', p404)

    if '<meta name="robots" content="noindex, nofollow" />' not in p404:
        p404 = p404.replace('<title>', '<meta name="robots" content="noindex, nofollow" />\n  <title>')

    with open(p404_path, 'w', encoding='utf-8') as f:
        f.write(p404)
    print("[OK] 404.html atualizado!")

if __name__ == '__main__':
    update_all_pages()
