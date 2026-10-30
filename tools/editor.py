import os
import re
import sys
import glob
import json
import base64
import time
import threading
import webbrowser
import urllib.parse
import unicodedata
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
import yaml

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Localizar o diretório do site
possible_paths = [
    os.path.abspath(os.path.join(APP_DIR, '..', 'Site-Marcos-Data-Product')),
    os.path.abspath(os.path.join(APP_DIR, 'Site-Marcos-Data-Product')),
    os.path.abspath(os.path.join(APP_DIR, '..'))
]
SITE_DIR = next((p for p in possible_paths if os.path.exists(os.path.join(p, 'content', 'posts'))), possible_paths[0])

POSTS_DIR = os.path.join(SITE_DIR, 'content', 'posts')
IMAGES_DIR = os.path.join(SITE_DIR, 'assets', 'img', 'blog')
TOOLS_DIR = os.path.join(SITE_DIR, 'tools')

os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
sys.path.insert(0, APP_DIR)
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)
import build_blog
import build_biblioteca
import build_projetos
from build_sitemap import build_sitemap

BOOK_COVERS_DIR = os.path.join(SITE_DIR, 'assets', 'img', 'Biblioteca page')
os.makedirs(BOOK_COVERS_DIR, exist_ok=True)

app = Flask(__name__, template_folder=os.path.join(APP_DIR, 'templates'))
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB max upload
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.jinja_env.auto_reload = True

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower()).strip()
    return re.sub(r'[\s_]+', '-', text)

def sanitize_filename(name):
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[^\w\.\-\_]', '_', name.strip().lower())
    return re.sub(r'__+', '_', name)

def recompile_tailwind():
    build_tailwind_script = os.path.join(TOOLS_DIR, 'build_tailwind.js')
    if os.path.exists(build_tailwind_script):
        try:
            subprocess.run(['node', build_tailwind_script], cwd=SITE_DIR, check=False, capture_output=True)
        except Exception as e:
            print(f"[Aviso] Não foi possível executar build_tailwind.js: {e}")

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Servir arquivos estáticos do site
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(SITE_DIR, 'assets'), filename)

@app.route('/content/<path:filename>')
def serve_content(filename):
    return send_from_directory(os.path.join(SITE_DIR, 'content'), filename)

@app.route('/blog/<path:filename>')
def serve_blog(filename):
    if not filename.endswith('.html') and not '.' in filename:
        filename += '.html'
    return send_from_directory(os.path.join(SITE_DIR, 'blog'), filename)

# Rotas de páginas limpas e compatibilidade .html
@app.route('/index.html')
@app.route('/home')
def serve_home_hub():
    return send_from_directory(SITE_DIR, 'index.html')

@app.route('/projetos.html')
@app.route('/projetos')
def serve_projetos_hub():
    return send_from_directory(SITE_DIR, 'projetos.html')

@app.route('/sobre.html')
@app.route('/sobre')
def serve_sobre_hub():
    return send_from_directory(SITE_DIR, 'sobre.html')

@app.route('/blog.html')
@app.route('/blog')
def serve_blog_hub():
    return send_from_directory(SITE_DIR, 'blog.html')

@app.route('/biblioteca.html')
@app.route('/biblioteca')
def serve_biblioteca_hub():
    return send_from_directory(SITE_DIR, 'biblioteca.html')

@app.route('/')
def index():
    return render_template('editor.html')

@app.route('/api/posts', methods=['GET'])
def list_posts():
    files = glob.glob(os.path.join(POSTS_DIR, '*.md'))
    posts = []
    for fp in files:
        try:
            p = build_blog.parse_post(fp)
            posts.append({
                'title': p.get('title', 'Sem título'),
                'slug': p.get('slug', ''),
                'date': str(p.get('date', '')),
                'category': p.get('category', ''),
                'category_color': p.get('category_color', 'blue'),
                'read_time': p.get('read_time', '5 min'),
                'author': p.get('author', 'Marcos Aurélio'),
                'featured': p.get('featured', False),
                'filename': os.path.basename(fp)
            })
        except Exception as e:
            print(f'Erro ao ler post {fp}: {e}')
    posts.sort(key=lambda x: str(x['date']), reverse=True)
    return jsonify(posts)

@app.route('/api/post/<path:slug>', methods=['GET'])
def get_post(slug):
    slug_candidates = [
        slug,
        slug.lower(),
        urllib.parse.unquote(slug),
        urllib.parse.unquote(slug).lower()
    ]
    files = glob.glob(os.path.join(POSTS_DIR, '*.md'))
    for fp in files:
        try:
            p = build_blog.parse_post(fp)
            parsed_slug = str(p.get('slug', '')).strip()
            base_name = os.path.splitext(os.path.basename(fp))[0]
            if parsed_slug in slug_candidates or parsed_slug.lower() in slug_candidates or base_name in slug_candidates:
                return jsonify(p)
        except Exception as e:
            print(f'Erro ao ler {fp}: {e}')
    return jsonify({'error': 'Artigo não encontrado'}), 404

@app.route('/api/delete-post/<path:slug>', methods=['DELETE', 'POST'])
def delete_post(slug):
    clean_slug = urllib.parse.unquote(slug).strip()
    slug_candidates = set([
        slug,
        slug.lower(),
        clean_slug,
        clean_slug.lower()
    ])
    files = glob.glob(os.path.join(POSTS_DIR, '*.md'))
    target_md = None
    target_slug = clean_slug
    post_title = clean_slug

    for fp in files:
        try:
            p = build_blog.parse_post(fp)
            base_name = os.path.splitext(os.path.basename(fp))[0]
            parsed_slug = str(p.get('slug', '')).strip()
            parsed_title = str(p.get('title', '')).strip()
            if (parsed_slug in slug_candidates or
                parsed_slug.lower() in slug_candidates or
                base_name in slug_candidates or
                base_name.lower() in slug_candidates):
                target_md = fp
                target_slug = parsed_slug or base_name
                post_title = parsed_title or target_slug
                break
        except Exception as e:
            print(f'Erro ao ler {fp}: {e}')

    if not target_md or not os.path.exists(target_md):
        return jsonify({'error': f'Artigo "{slug}" não encontrado'}), 404

    try:
        os.remove(target_md)
    except Exception as e:
        return jsonify({'error': f'Falha ao remover Markdown: {e}'}), 500

    html_file = os.path.join(SITE_DIR, 'blog', f'{target_slug}.html')
    if os.path.exists(html_file):
        try:
            os.remove(html_file)
        except Exception:
            pass

    build_blog.build_all()
    build_sitemap()
    recompile_tailwind()

    return jsonify({
        'success': True,
        'slug': target_slug,
        'title': post_title,
        'message': f'Artigo "{post_title}" excluído com sucesso!'
    })

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

        orig_name = sanitize_filename(file.filename)
        base, ext = os.path.splitext(orig_name)
        
        # Tentar salvar como WebP diretamente se Pillow estiver disponível
        try:
            from PIL import Image
            im = Image.open(file.stream)
            filename = f'{base}_{int(time.time())}.webp'
            save_path = os.path.join(IMAGES_DIR, filename)
            im.save(save_path, 'WEBP', quality=85)
        except Exception:
            if not ext: ext = '.png'
            filename = f'{base}_{int(time.time())}{ext}'
            save_path = os.path.join(IMAGES_DIR, filename)
            file.save(save_path)

        relative_url = f'assets/img/blog/{filename}'
        return jsonify({
            'success': True,
            'url': relative_url,
            'filename': filename,
            'message': 'Imagem enviada com sucesso!'
        })

    data = request.get_json(silent=True) or {}
    if 'image_data' in data:
        img_data = data['image_data']
        if ',' in img_data:
            _, encoded = img_data.split(',', 1)
            binary = base64.b64decode(encoded)
            filename = f'clipboard_{int(time.time())}.webp'
            save_path = os.path.join(IMAGES_DIR, filename)
            try:
                import io
                from PIL import Image
                im = Image.open(io.BytesIO(binary))
                im.save(save_path, 'WEBP', quality=85)
            except Exception:
                filename = f'clipboard_{int(time.time())}.png'
                save_path = os.path.join(IMAGES_DIR, filename)
                with open(save_path, 'wb') as f:
                    f.write(binary)

            relative_url = f'assets/img/blog/{filename}'
            return jsonify({
                'success': True,
                'url': relative_url,
                'filename': filename,
                'message': 'Imagem colada e salva com sucesso!'
            })

    return jsonify({'error': 'Nenhuma imagem recebida'}), 400

@app.route('/api/publish', methods=['POST'])
def publish_post():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'O título é obrigatório'}), 400

    slug = data.get('slug', '').strip()
    if not slug:
        slug = slugify(title)
    else:
        slug = slugify(slug)

    date_val = data.get('date', '').strip() or datetime.now().strftime('%Y-%m-%d')
    author = data.get('author', '').strip() or 'Marcos Aurélio'
    category = data.get('category', '').strip() or 'Business Analytics'
    category_color = data.get('category_color', '').strip() or 'blue'
    read_time = data.get('read_time', '').strip() or '5 min'
    excerpt = data.get('excerpt', '').strip()
    cover = data.get('cover', '').strip()
    featured = bool(data.get('featured', False))
    tags = data.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]

    raw_body = data.get('body', '').strip()

    frontmatter = {
        'title': title,
        'slug': slug,
        'date': date_val,
        'author': author,
        'category': category,
        'category_color': category_color,
        'read_time': read_time,
        'excerpt': excerpt,
        'cover': cover,
        'featured': featured,
        'tags': tags
    }

    yaml_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)
    file_content = f"---\n{yaml_str}---\n\n{raw_body}\n"

    filename = f"{date_val}-{slug}.md"
    target_path = os.path.join(POSTS_DIR, filename)

    existing_files = glob.glob(os.path.join(POSTS_DIR, '*.md'))
    for ef in existing_files:
        try:
            p = build_blog.parse_post(ef)
            if str(p.get('slug', '')).strip().lower() == slug.lower() and ef != target_path:
                os.remove(ef)
                break
        except Exception:
            pass

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(file_content)

    build_blog.build_all()
    build_sitemap()
    recompile_tailwind()

    return jsonify({
        'success': True,
        'slug': slug,
        'target_file': os.path.basename(target_path),
        'post_url': f'/blog/{slug}',
        'hub_url': '/blog',
        'build_success': True,
        'message': f'Artigo "{title}" publicado com sucesso!'
    })

# -------------------------------------------------------------
# Rotas e APIs para Gestão da Biblioteca
# -------------------------------------------------------------

@app.route('/api/books', methods=['GET'])
def list_books():
    try:
        books = build_biblioteca.load_books()
        return jsonify(books)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/book/<book_id>', methods=['GET'])
def get_book(book_id):
    books = build_biblioteca.load_books()
    book = next((b for b in books if b.get('id') == book_id), None)
    if not book:
        return jsonify({'error': 'Livro não encontrado'}), 404
    return jsonify(book)

@app.route('/api/book', methods=['POST'])
def save_book():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'O nome do livro é obrigatório'}), 400

    author = data.get('author', '').strip() or 'Autor desconhecido'
    amazon_link = data.get('amazon_link', '').strip() or '#'
    cover_image = data.get('cover_image', '').strip() or 'assets/img/books/cover-estatistica-o-que-e.webp'
    short_desc = data.get('short_desc', '').strip()
    desc_full = data.get('desc_full', '').strip() or short_desc

    tags = data.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]

    category = data.get('category', '').strip().lower()
    if not category:
        category = 'dados'

    destaque = bool(data.get('destaque', True))
    try:
        rating = float(data.get('rating', 4.8))
    except (ValueError, TypeError):
        rating = 4.8

    book_id = data.get('id', '').strip()
    if not book_id:
        clean_name = slugify(title)
        book_id = f"{clean_name}-{int(time.time())}"

    books = build_biblioteca.load_books()
    existing_index = next((i for i, b in enumerate(books) if b.get('id') == book_id), None)

    book_entry = {
        'id': book_id,
        'title': title,
        'author': author,
        'category': category,
        'rating': rating,
        'amazon_link': amazon_link,
        'cover_image': cover_image,
        'short_desc': short_desc,
        'desc_full': desc_full,
        'tags': tags,
        'destaque': destaque,
        'created_at': data.get('created_at') or datetime.now().strftime('%Y-%m-%d')
    }

    if existing_index is not None:
        books[existing_index] = book_entry
    else:
        books.insert(0, book_entry)

    with open(build_biblioteca.BOOKS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    build_biblioteca.build_all()
    build_sitemap()
    recompile_tailwind()

    return jsonify({
        'success': True,
        'book': book_entry,
        'message': f'Livro "{title}" salvo com sucesso!'
    })

@app.route('/api/book/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    books = build_biblioteca.load_books()
    filtered = [b for b in books if b.get('id') != book_id]
    if len(filtered) == len(books):
        return jsonify({'error': 'Livro não encontrado'}), 404

    with open(build_biblioteca.BOOKS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    build_biblioteca.build_all()
    build_sitemap()
    recompile_tailwind()

    return jsonify({'success': True, 'message': 'Livro removido com sucesso!'})

@app.route('/api/sync-biblioteca', methods=['POST'])
def sync_biblioteca():
    try:
        build_biblioteca.build_all()
        build_sitemap()
        recompile_tailwind()
        return jsonify({'success': True, 'message': 'Biblioteca sincronizada!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def open_browser():
    time.sleep(1.2)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    if '--test' in sys.argv:
        print('Test mode: editor.py Flask app initialized successfully.')
        sys.exit(0)

    print('════════════════════════════════════════════════════════════')
    print(' 🚀 Marcos Data Product — Editor')
    print(' Pasta do Site conectada:', SITE_DIR)
    print(' Servidor local iniciado em: http://localhost:5000')
    print(' Pressione Ctrl+C no terminal para encerrar.')
    print('════════════════════════════════════════════════════════════')
    
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
