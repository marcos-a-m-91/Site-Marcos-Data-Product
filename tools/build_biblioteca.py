import os
import json
import re

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

os.makedirs(CONTENT_DIR, exist_ok=True)

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

def build_all():
    books = load_books()
    if not os.path.exists(BIBLIOTECA_HTML_PATH):
        print(f'Arquivo {BIBLIOTECA_HTML_PATH} não encontrado.')
        return False
        
    with open(BIBLIOTECA_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    books_json_str = json.dumps(books, ensure_ascii=False, indent=2)
    
    # Atualizar o bloco de EMBEDDED_BOOKS em biblioteca.html
    pattern = re.compile(r'(const EMBEDDED_BOOKS\s*=\s*)\[.*?\];(\s*let allBooks\s*=)', re.DOTALL)
    if pattern.search(content):
        new_content = pattern.sub(f'\\1{books_json_str};\\2', content)
        with open(BIBLIOTECA_HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Biblioteca sincronizada com sucesso! {len(books)} livros atualizados em {BIBLIOTECA_HTML_PATH}')
        return True
    else:
        print('Aviso: Padrão EMBEDDED_BOOKS não encontrado em biblioteca.html')
        return False

if __name__ == '__main__':
    build_all()
