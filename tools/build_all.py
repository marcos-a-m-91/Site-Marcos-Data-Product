import os
import sys

# Garantir codificação UTF-8 no terminal Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

import build_blog
import build_biblioteca
import build_projetos

def build():
    print("=" * 60)
    print("Sincronizando todo o ecossistema Marcos Data Product...")
    print("=" * 60)

    print("\n[1/3] Sincronizando Blog & Artigos...")
    try:
        build_blog.build_all()
    except Exception as e:
        print(f"Erro no blog: {e}")

    print("\n[2/3] Sincronizando Biblioteca & Livros...")
    try:
        build_biblioteca.build_all()
    except Exception as e:
        print(f"Erro na biblioteca: {e}")

    print("\n[3/3] Sincronizando Projetos & Estudos de Caso...")
    try:
        build_projetos.build_all()
    except Exception as e:
        print(f"Erro nos projetos: {e}")

    print("\n" + "=" * 60)
    print("Sucesso: Todo o site foi sincronizado!")
    print("=" * 60)

if __name__ == '__main__':
    build()
