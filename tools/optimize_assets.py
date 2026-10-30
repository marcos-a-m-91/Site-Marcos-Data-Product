import os
import shutil
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT_DIR, 'assets', 'img')

def run_asset_optimizations():
    print("=== OTIMIZAÇÃO DE ASSETS ===")
    
    # 1. Copiar favicon.ico para a raiz se não existir
    src_fav = os.path.join(IMG_DIR, 'favicon.ico')
    dst_fav = os.path.join(ROOT_DIR, 'favicon.ico')
    if os.path.exists(src_fav):
        shutil.copy2(src_fav, dst_fav)
        print(f"[OK] Favicon copiado para a raiz: {dst_fav}")

    # 2. Excluir artigo de teste analise2 (MD e HTML)
    test_md = os.path.join(ROOT_DIR, 'content', 'posts', '2026-10-22-vies-cognitivo---um-dos-maiores-sabotadores-da-sua-analise2.md')
    test_html = os.path.join(ROOT_DIR, 'blog', 'vies-cognitivo-um-dos-maiores-sabotadores-da-sua-analise2.html')
    for fpath in [test_md, test_html]:
        if os.path.exists(fpath):
            os.remove(fpath)
            print(f"[OK] Arquivo de teste removido: {fpath}")

    # Diretórios de destino organizados
    os.makedirs(os.path.join(IMG_DIR, 'companies'), exist_ok=True)
    os.makedirs(os.path.join(IMG_DIR, 'testimonials'), exist_ok=True)
    os.makedirs(os.path.join(IMG_DIR, 'books'), exist_ok=True)
    stacks_dir = os.path.join(IMG_DIR, 'icons-stacks')

    # Helper para converter e redimensionar imagens raster para WebP
    def convert_to_webp(src_path, dst_path, max_width=None, max_height=None, quality=82, lossless=False):
        if not os.path.exists(src_path):
            print(f"[WARN] Origem inexistente: {src_path}")
            return None
        with Image.open(src_path) as im:
            if im.mode in ("RGBA", "LA") and not lossless:
                pass
            elif im.mode != "RGB" and not lossless and im.mode != "RGBA":
                im = im.convert("RGB")
            
            w, h = im.size
            if max_width or max_height:
                im.thumbnail((max_width or w, max_height or h), Image.Resampling.LANCZOS)
            
            im.save(dst_path, 'WEBP', quality=quality, lossless=lossless, method=6)
            new_w, new_h = im.size
            orig_sz = os.path.getsize(src_path)
            new_sz = os.path.getsize(dst_path)
            saved_pct = ((orig_sz - new_sz) / orig_sz) * 100
            print(f"  [WEBP] {os.path.basename(dst_path)} ({new_w}x{new_h}) | {orig_sz//1024}KB -> {new_sz//1024}KB (-{saved_pct:.1f}%)")
            return new_w, new_h

    # 3. Converter Hero Sections
    print("\n--- Hero Images ---")
    convert_to_webp(os.path.join(IMG_DIR, 'hero_section_home.jpg'), os.path.join(IMG_DIR, 'hero-home.webp'), max_width=1920, quality=82)
    convert_to_webp(os.path.join(IMG_DIR, 'hero_section_sobre_v3.jpg'), os.path.join(IMG_DIR, 'hero-sobre.webp'), max_width=1920, quality=82)
    convert_to_webp(os.path.join(IMG_DIR, 'hero_section_blog_v2.jpg'), os.path.join(IMG_DIR, 'hero-blog.webp'), max_width=1920, quality=82)
    convert_to_webp(os.path.join(IMG_DIR, 'hero_section_projetos_v4.jpg'), os.path.join(IMG_DIR, 'hero-projetos.webp'), max_width=1920, quality=82)
    convert_to_webp(os.path.join(IMG_DIR, 'hero_section_biblioteca_v2.png'), os.path.join(IMG_DIR, 'hero-biblioteca.webp'), max_width=1920, quality=82)
    
    # Logos
    print("\n--- Logos ---")
    convert_to_webp(os.path.join(IMG_DIR, 'logo-clara.png'), os.path.join(IMG_DIR, 'logo-clara.webp'), lossless=True)
    convert_to_webp(os.path.join(IMG_DIR, 'logo-escura.png'), os.path.join(IMG_DIR, 'logo-escura.webp'), lossless=True)

    # 4. OpenGraph Social Share Card (1200x630)
    print("\n--- OpenGraph Default Card ---")
    og_path = os.path.join(IMG_DIR, 'og-default.jpg')
    if not os.path.exists(og_path):
        home_hero_src = os.path.join(IMG_DIR, 'hero_section_home.jpg')
        if os.path.exists(home_hero_src):
            with Image.open(home_hero_src) as im:
                im_rgb = im.convert('RGB')
                im_og = im_rgb.resize((1200, 630), Image.Resampling.LANCZOS)
                im_og.save(og_path, 'JPEG', quality=88, optimize=True)
                print(f"[OK] OG Default criado: {og_path} (1200x630)")

    # 5. Empresas (Companies) - 2x Retina para exibição 48x48
    print("\n--- Companies ---")
    companies = [
        ('bauminas.png', 'bauminas.webp'),
        ('Cogna.jpeg', 'cogna.webp'),
        ('Neoenergia.png', 'neoenergia.webp'),
        ('Alelo.png', 'alelo.webp'),
        ('Nubank.png', 'nubank.webp'),
        ('Ford.png', 'ford.webp'),
    ]
    for src_name, dst_name in companies:
        convert_to_webp(os.path.join(IMG_DIR, src_name), os.path.join(IMG_DIR, 'companies', dst_name), max_width=128, max_height=128, quality=85)

    # 6. Depoimentos (Testimonials) - 2x Retina para exibição 40x40
    print("\n--- Testimonials ---")
    testimonials = [
        ('Carolina Pazinato.jpeg', 'carolina-pazinato.webp'),
        ('Leidiana de Carli.jpeg', 'leidiana-de-carli.webp'),
        ('Lucas Sorreano.jpeg', 'lucas-sorreano.webp'),
        ('VIviane Vieira.jpeg', 'viviane-vieira.webp'),
    ]
    for src_name, dst_name in testimonials:
        convert_to_webp(os.path.join(IMG_DIR, src_name), os.path.join(IMG_DIR, 'testimonials', dst_name), max_width=100, max_height=100, quality=85)

    # 7. Livros (Books) - 2x Retina para exibição ~190px largura
    print("\n--- Books ---")
    bib_dir = os.path.join(IMG_DIR, 'Biblioteca page')
    book_covers = [
        (os.path.join(bib_dir, 'hábitos_atômicos_1792111870.jpg'), 'habitos-atomicos.webp'),
        (os.path.join(bib_dir, 'como_mentir_com_estatística_1792110793.jpg'), 'como-mentir-com-estatistica.webp'),
        (os.path.join(bib_dir, 'estatística_1792107395.jpg'), 'estatistica-o-que-e.webp'),
    ]
    for src_path, dst_name in book_covers:
        convert_to_webp(src_path, os.path.join(IMG_DIR, 'books', dst_name), max_width=380, quality=85)

    # 8. Normalizar nomes de ícones SVG de stacks para kebab-case lowercase
    print("\n--- Stack SVGs (kebab-case) ---")
    if os.path.exists(stacks_dir):
        svg_map = {
            'Big Query.svg': 'big-query.svg',
            'Data Studio.svg': 'data-studio.svg',
            'Power Apps.svg': 'power-apps.svg',
            'Power BI.svg': 'power-bi.svg',
            'Power Query.svg': 'power-query.svg',
            'VS Code.svg': 'vs-code.svg',
            'GA4.svg': 'ga4.svg',
            'Miro.svg': 'miro.svg',
            'PowerPoint.svg': 'powerpoint.svg',
            'Athena.svg': 'athena.svg',
            'Jira.svg': 'jira.svg',
            'Databricks.svg': 'databricks.svg',
            'Confluence.svg': 'confluence.svg',
            'Cursor.svg': 'cursor.svg',
            'GCP.svg': 'gcp.svg',
            'Sharepoint.svg': 'sharepoint.svg',
            'Copilot.svg': 'copilot.svg',
            'CopilotStudio.svg': 'copilot-studio.svg',
            'VBA.svg': 'vba.svg',
            'Totvs--Streamline-Simple-Icons.svg': 'totvs.svg',
            'Qlik.svg': 'qlik.svg',
            'Scala.svg': 'scala.svg',
            'Python.svg': 'python.svg',
            'Altair.svg': 'altair.svg',
        }
        for orig, clean in svg_map.items():
            orig_p = os.path.join(stacks_dir, orig)
            clean_p = os.path.join(stacks_dir, clean)
            if os.path.exists(orig_p) and not os.path.exists(clean_p):
                shutil.copy2(orig_p, clean_p)
                print(f"  [SVG] {orig} -> {clean}")

    print("\n[OK] Otimização de assets concluída!")

if __name__ == '__main__':
    run_asset_optimizations()

