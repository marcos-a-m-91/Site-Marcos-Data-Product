import os
import subprocess
import build_blog
import build_biblioteca
import build_projetos
from build_sitemap import build_sitemap

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(ROOT_DIR, 'tools')

def build():
    print("=== EXECUTANDO BUILD COMPLETO DO SITE ===")
    
    # 1. Compilar Blog
    print("\n1. Compilando Blog...")
    build_blog.build_all()

    # 2. Compilar Biblioteca
    print("\n2. Compilando Biblioteca...")
    build_biblioteca.build_all()

    # 3. Compilar Projetos
    print("\n3. Compilando Projetos...")
    build_projetos.build_all()

    # 4. Gerar Sitemap
    print("\n4. Gerando Sitemap...")
    total_urls = build_sitemap()
    print(f"Sitemap finalizado com {total_urls} URLs.")

    # 5. Recompilar Tailwind CSS
    print("\n5. Compilando Tailwind CSS estático...")
    js_script = os.path.join(TOOLS_DIR, 'build_tailwind.js')
    res = subprocess.run(['node', js_script], cwd=ROOT_DIR, capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("Erro Tailwind:", res.stderr)

    print("\n[OK] Build completo concluído com sucesso!")

if __name__ == '__main__':
    build()

