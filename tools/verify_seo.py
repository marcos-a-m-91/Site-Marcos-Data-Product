"""
Script de verificação automática rigorosa de SEO e integridade técnica.
Verifica os 20 pontos de auditoria em todos os arquivos HTML e configurações.
"""
import os
import re
import json
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANONICAL_DOMAIN = "https://marcosdataproduct.com"
HTML_FILES = ["index.html", "sobre.html", "blog.html", "projetos.html", "biblioteca.html", "404.html"]

errors = []
warnings = []
passed = []

def check(condition, desc, error_msg):
    if condition:
        passed.append(desc)
    else:
        errors.append(f"[FALHA] {desc}: {error_msg}")

print("=== INICIANDO AUDITORIA E VERIFICAÇÃO AUTOMÁTICA ===")

# 1. Sitemap
sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
if os.path.exists(sitemap_path):
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        urls = [elem.text for elem in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        check(len(urls) == 5, "Sitemap tem 5 URLs públicas canônicas", f"Encontradas {len(urls)} URLs: {urls}")
        for u in urls:
            check(u.startswith(CANONICAL_DOMAIN), f"URL canônica no sitemap ({u})", f"Não começa com {CANONICAL_DOMAIN}")
            check(not u.endswith(".html"), f"URL limpa sem .html ({u})", "Termina com .html")
    except Exception as e:
        errors.append(f"Sitemap XML inválido: {e}")
else:
    errors.append("sitemap.xml não encontrado!")

# 2. Robots.txt
robots_path = os.path.join(BASE_DIR, "robots.txt")
if os.path.exists(robots_path):
    with open(robots_path, "r", encoding="utf-8") as f:
        robots_content = f.read()
    check("Sitemap: https://marcosdataproduct.com/sitemap.xml" in robots_content, "robots.txt contém sitemap correto", "Sitemap ausente ou incorreto")
    check("Allow: /" in robots_content, "robots.txt permite indexação pública", "Allow: / ausente")
    check("Disallow: /tools/" in robots_content, "robots.txt bloqueia /tools/", "Disallow: /tools/ ausente")
else:
    errors.append("robots.txt não encontrado!")

# 3. Vercel.json
vercel_path = os.path.join(BASE_DIR, "vercel.json")
if os.path.exists(vercel_path):
    try:
        with open(vercel_path, "r", encoding="utf-8") as f:
            v_conf = json.load(f)
        check(v_conf.get("cleanUrls") is True, "vercel.json cleanUrls ativado", "cleanUrls não é True")
        check(v_conf.get("trailingSlash") is False, "vercel.json trailingSlash desativado", "trailingSlash não é False")
        check(any(h.get("headers", [{}])[0].get("value") == "noindex, nofollow" for h in v_conf.get("headers", [])), "vercel.json aplica noindex em rotas privadas", "Header noindex não encontrado")
    except Exception as e:
        errors.append(f"vercel.json inválido: {e}")
else:
    errors.append("vercel.json não encontrado!")

# Checagem detalhada por arquivo HTML
page_titles = {}
page_descriptions = {}
page_h1s = {}

for html_file in HTML_FILES:
    file_path = os.path.join(BASE_DIR, html_file)
    if not os.path.exists(file_path):
        errors.append(f"Arquivo não existe: {html_file}")
        continue
    
    with open(file_path, "r", encoding="utf-8") as f:
        raw_html = f.read()

    # Separar HTML do corpo e scripts para verificações estáticas
    html_without_scripts = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', raw_html, flags=re.DOTALL)

    # Canonical
    can_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', raw_html)
    if html_file == "404.html":
        check(can_match is None, "[404.html] 404 sem canonical (correto por boas práticas)", "404 possui tag canonical indesejada")
    else:
        if can_match:
            can_url = can_match.group(1)
            check(can_url.startswith(CANONICAL_DOMAIN), f"[{html_file}] Canonical válida", f"Valor: {can_url}")
            check(not can_url.endswith(".html"), f"[{html_file}] Canonical sem .html", f"Valor: {can_url}")
        else:
            errors.append(f"[{html_file}] Tag canonical ausente!")

    # Title
    title_match = re.search(r'<title>([^<]+)</title>', raw_html)
    if title_match:
        title = title_match.group(1).strip()
        page_titles[html_file] = title
        check(len(title) <= 65, f"[{html_file}] Title dentro do limite ({len(title)} chars)", f"Title muito longo: '{title}' ({len(title)} chars)")
        check(len(title) >= 15, f"[{html_file}] Title tamanho mínimo", f"Title muito curto: '{title}'")
    else:
        errors.append(f"[{html_file}] Tag title ausente!")

    # Meta Description
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', raw_html)
    if html_file != "404.html":
        if desc_match:
            desc = desc_match.group(1).strip()
            page_descriptions[html_file] = desc
            check(len(desc) <= 165, f"[{html_file}] Meta description dentro do limite ({len(desc)} chars)", f"Desc muito longa: '{desc}' ({len(desc)} chars)")
            check(len(desc) >= 50, f"[{html_file}] Meta description com conteúdo relevante", f"Desc muito curta: '{desc}'")
        else:
            errors.append(f"[{html_file}] Meta description ausente!")

    # Robots tag na página
    robots_meta = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)["\']', raw_html)
    if html_file == "404.html":
        check(robots_meta and "noindex" in robots_meta.group(1), f"[{html_file}] 404 tem noindex", "404 sem noindex")
    else:
        if robots_meta:
            check("index" in robots_meta.group(1) and "noindex" not in robots_meta.group(1), f"[{html_file}] indexável", f"Robots meta incorreto: {robots_meta.group(1)}")

    # H1
    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html_without_scripts, re.DOTALL)
    clean_h1s = [re.sub(r'<[^>]+>', '', h).strip() for h in h1_matches]
    check(len(clean_h1s) == 1, f"[{html_file}] Exatamente um H1", f"Encontrados {len(clean_h1s)} H1s: {clean_h1s}")
    if clean_h1s:
        page_h1s[html_file] = clean_h1s[0]

    # Heading hierarchy check
    heading_tags = re.findall(r'<(h[1-6])[^>]*>', html_without_scripts)
    current_level = 0
    skipped_hierarchy = False
    for ht in heading_tags:
        level = int(ht[1])
        if level > current_level + 1 and current_level != 0:
            skipped_hierarchy = True
            errors.append(f"[{html_file}] Pulo de hierarquia de títulos: de H{current_level} para H{level}")
        current_level = level
    if not skipped_hierarchy:
        passed.append(f"[{html_file}] Hierarquia de cabeçalhos íntegra (H1->H2->H3)")

    # JSON-LD
    if html_file != "404.html":
        json_ld_matches = re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', raw_html, re.DOTALL)
        check(len(json_ld_matches) >= 1, f"[{html_file}] Possui JSON-LD estruturado", "JSON-LD ausente")
        for j_str in json_ld_matches:
            try:
                data = json.loads(j_str.strip())
                check(data.get("@context") in ["https://schema.org", "http://schema.org"], f"[{html_file}] JSON-LD Schema válido (@type: {data.get('@type') or '@graph'})", "Contexto inválido")
            except Exception as e:
                errors.append(f"[{html_file}] JSON-LD inválido: {e}")

    # Checagem de Imagens HTML
    img_tags = re.findall(r'<img\s+([^>]+)>', html_without_scripts)
    for img_attr in img_tags:
        src_match = re.search(r'src=["\']([^"\']+)["\']', img_attr)
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', img_attr)
        width_match = re.search(r'width=["\']([^"\']+)["\']', img_attr)
        height_match = re.search(r'height=["\']([^"\']+)["\']', img_attr)
        
        src = src_match.group(1) if src_match else "sem-src"
        check(alt_match is not None, f"[{html_file}] Imagem {src} tem atributo alt", f"Tag sem alt: {img_attr}")
        check(width_match is not None and height_match is not None, f"[{html_file}] Imagem {src} tem width e height definidos", f"Sem width/height: {img_attr}")
        
        # Verificar se arquivo local existe
        if not src.startswith("http") and not src.startswith("//") and not src.startswith("data:"):
            clean_src = src.split("?")[0].lstrip("/")
            local_img_path = os.path.join(BASE_DIR, clean_src)
            check(os.path.exists(local_img_path), f"[{html_file}] Imagem existe localmente ({clean_src})", f"Imagem não encontrada: {local_img_path}")

    # Checagem de Links Internos
    links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\']', raw_html)
    for l in links:
        if l.endswith(".html") and not l.startswith("http") and not l.startswith("//"):
            errors.append(f"[{html_file}] Link interno com extensão .html: {l}")
        # YouTube check
        if "youtube.com" in l or "youtu.be" in l:
            errors.append(f"[{html_file}] Link do YouTube visível: {l}")
        # Instagram check
        if "instagram.com" in l:
            check("marcos.dataproduct" in l, f"[{html_file}] Link do Instagram correto", f"Instagram incorreto: {l}")
        # GitHub check
        if "github.com" in l:
            check(l == "https://github.com/marcos-a-m-91" or l.startswith("https://github.com/marcos-a-m-91/"), f"[{html_file}] GitHub perfil pessoal", f"GitHub incorreto: {l}")

    # Checagem de tailwind.css compilado e ausência de script JIT
    check("assets/css/tailwind.css" in raw_html, f"[{html_file}] Referencia tailwind.css estático compilado", "tailwind.css ausente")
    check("resource_3fa48481346f.js" not in raw_html, f"[{html_file}] Sem script compilador JIT pesado de 400KB", "Script de 400KB ainda presente!")

# Unicidade de Titles e Descriptions (excluindo 404)
public_titles = {k: v for k, v in page_titles.items() if k != "404.html"}
public_descs = {k: v for k, v in page_descriptions.items() if k != "404.html"}
check(len(public_titles) == len(set(public_titles.values())), "Titles únicos em todas as páginas públicas", f"Duplicados: {public_titles}")
check(len(public_descs) == len(set(public_descs.values())), "Descriptions únicas em todas as páginas públicas", f"Duplicados: {public_descs}")

print("\n--- RESUMO DE TESTES ---")
print(f"Total de checagens aprovadas: {len(passed)}")
print(f"Total de falhas: {len(errors)}")

if errors:
    print("\nFALHAS ENCONTRADAS:")
    for err in errors:
        print("  - " + err)
else:
    print("\n[SUCESSO ABSOLUTO] TODOS OS PONTOS FORAM VALIDADOS COM 100% DE SUCESSO!")
