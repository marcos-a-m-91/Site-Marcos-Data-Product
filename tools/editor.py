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
sys.path.insert(0, APP_DIR)
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)
import build_blog
import build_biblioteca

BOOK_COVERS_DIR = os.path.join(SITE_DIR, 'assets', 'img', 'Biblioteca page')
os.makedirs(BOOK_COVERS_DIR, exist_ok=True)

app = Flask(__name__, template_folder=os.path.join(APP_DIR, 'templates'))
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB max upload
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.jinja_env.auto_reload = True

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
    return send_from_directory(os.path.join(SITE_DIR, 'blog'), filename)

@app.route('/index.html')
@app.route('/home')
def serve_home_hub():
    return send_from_directory(SITE_DIR, 'index.html')

@app.route('/projetos.html')
def serve_projetos_hub():
    return send_from_directory(SITE_DIR, 'projetos.html')

@app.route('/sobre.html')
def serve_sobre_hub():
    return send_from_directory(SITE_DIR, 'sobre.html')

@app.route('/blog.html')
def serve_blog_hub():
    return send_from_directory(SITE_DIR, 'blog.html')

@app.route('/biblioteca.html')
def serve_biblioteca_hub():
    return send_from_directory(SITE_DIR, 'biblioteca.html')

@app.route('/')
def index():
    return render_template('editor.html')

@app.route('/biblioteca')
def biblioteca_manager():
    return render_template('biblioteca_manager.html')

@app.route('/api/posts', methods=['GET'])
def list_posts():
    files = glob.glob(os.path.join(POSTS_DIR, '*.md'))
    posts = []
    for fp in files:
        try:
            post = build_blog.parse_post(fp)
            posts.append({
                'title': post.get('title', 'Sem título'),
                'slug': post.get('slug', ''),
                'date': str(post.get('date', '')),
                'category': post.get('category', 'Artigo'),
                'category_color': post.get('category_color', 'blue'),
                'read_time': post.get('read_time', '5 min'),
                'cover': post.get('cover', ''),
                'excerpt': post.get('excerpt', ''),
                'featured': bool(post.get('featured', False)),
                'tags': post.get('tags', []),
                'filename': os.path.basename(fp)
            })
        except Exception as e:
            print(f'Erro ao ler {fp}: {e}')
    posts.sort(key=lambda x: str(x.get('date', '')), reverse=True)
    return jsonify(posts)

@app.route('/api/post/<slug>', methods=['GET'])
def get_post(slug):
    files = glob.glob(os.path.join(POSTS_DIR, '*.md'))
    for fp in files:
        post = build_blog.parse_post(fp)
        if post.get('slug') == slug or os.path.splitext(os.path.basename(fp))[0] == slug:
            return jsonify({
                'title': post.get('title', ''),
                'slug': post.get('slug', ''),
                'date': str(post.get('date', '')),
                'author': post.get('author', 'Marcos Aurélio'),
                'category': post.get('category', 'Power BI'),
                'category_color': post.get('category_color', 'amber'),
                'read_time': post.get('read_time', '5 min'),
                'excerpt': post.get('excerpt', ''),
                'cover': post.get('cover', ''),
                'featured': bool(post.get('featured', False)),
                'tags': post.get('tags', []),
                'body': post.get('raw_body', ''),
                'filename': os.path.basename(fp)
            })
    return jsonify({'error': 'Post não encontrado'}), 404

@app.route('/api/post/<slug>', methods=['DELETE'])
@app.route('/api/post/<slug>/delete', methods=['POST'])
def delete_post(slug):
    clean_slug = urllib.parse.unquote(slug).strip()
    slug_candidates = {slug, clean_slug, slug.lower(), clean_slug.lower()}
    
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
            
            matches = (
                parsed_slug in slug_candidates or
                parsed_slug.lower() in slug_candidates or
                base_name in slug_candidates or
                base_name.lower() in slug_candidates or
                os.path.basename(fp) in slug_candidates or
                parsed_title in slug_candidates or
                parsed_title.lower() in slug_candidates
            )
            if matches:
                target_md = fp
                target_slug = parsed_slug or base_name
                post_title = parsed_title or target_slug
                break
        except Exception as e:
            print(f'Erro ao ler {fp}: {e}')

    if not target_md or not os.path.exists(target_md):
        return jsonify({'error': f'Artigo com identificador "{slug}" não foi encontrado'}), 404

    # 1. Remover o arquivo Markdown da pasta de posts
    try:
        os.remove(target_md)
        print(f'Post Markdown removido com sucesso: {target_md}')
    except Exception as e:
        return jsonify({'error': f'Falha ao remover arquivo Markdown: {e}'}), 500

    # 2. Remover o HTML compilado da pasta do blog, se existir
    slugs_to_remove = set([slug, clean_slug, target_slug, target_slug.lower(), os.path.splitext(os.path.basename(target_md))[0]])
    for s in slugs_to_remove:
        if not s:
            continue
        html_file = os.path.join(SITE_DIR, 'blog', f'{s}.html')
        if os.path.exists(html_file):
            try:
                os.remove(html_file)
                print(f'HTML compilado removido do blog: {html_file}')
            except Exception as e:
                print(f'Aviso: Não foi possível remover {html_file}: {e}')

    # 3. Recompilar o blog (atualiza blog.html, listas e contadores)
    build_success = False
    try:
        build_blog.build_all()
        build_success = True
    except Exception as e:
        print(f'Erro ao recompilar blog após exclusão: {e}')

    return jsonify({
        'success': True,
        'slug': target_slug,
        'title': post_title,
        'build_success': build_success,
        'message': f'Artigo "{post_title}" excluído do blog com sucesso!'
    })

def sanitize_filename(name):
    name = re.sub(r'[^\w\.\-\_]', '_', name.strip().lower())
    return re.sub(r'__+', '_', name)

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

        orig_name = sanitize_filename(file.filename)
        base, ext = os.path.splitext(orig_name)
        if not ext:
            ext = '.png'

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
            header, encoded = img_data.split(',', 1)
            ext = '.png'
            if 'jpeg' in header or 'jpg' in header:
                ext = '.jpg'
            elif 'webp' in header:
                ext = '.webp'
            elif 'svg' in header:
                ext = '.svg'
            
            binary = base64.b64decode(encoded)
            filename = f'clipboard_{int(time.time())}{ext}'
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
        slug = re.sub(r'[^\w\s-]', '', title.lower()).strip()
        slug = re.sub(r'[\s_]+', '-', slug)

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

    yaml_header = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
    file_content = f'---\n{yaml_header}---\n\n{raw_body}\n'

    existing_file = None
    for fp in glob.glob(os.path.join(POSTS_DIR, '*.md')):
        p = build_blog.parse_post(fp)
        if p.get('slug') == slug:
            existing_file = fp
            break

    if existing_file:
        target_path = existing_file
    else:
        target_path = os.path.join(POSTS_DIR, f'{date_val}-{slug}.md')

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(file_content)

    print(f'Post salvo em: {target_path}')

    try:
        build_blog.build_all()
        build_success = True
    except Exception as e:
        print(f'Erro ao compilar blog: {e}')
        build_success = False

    return jsonify({
        'success': True,
        'slug': slug,
        'target_file': os.path.basename(target_path),
        'post_url': f'blog/{slug}.html',
        'hub_url': 'blog.html',
        'build_success': build_success,
        'message': f'Artigo \'{title}\' publicado e compilado com sucesso!'
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
        text = ' ' + ' '.join(t.lower() for t in tags) + ' ' + title.lower() + ' '
        if any(k in text for k in ['dado', 'estatistica', 'estatística', 'analise', 'análise', 'analytics', 'sql', 'bi ']):
            category = 'dados'
        elif any(k in text for k in ['produto', 'ux', 'discovery', 'design thinking']):
            category = 'produto'
        elif any(k in text for k in ['habito', 'hábito', 'mentalidade', 'comportamento', 'psicolog', 'mindset']):
            category = 'mentalidade'
        elif any(k in text for k in ['negocio', 'negócio', 'estrategia', 'estratégia', 'finan', 'gestao', 'gestão', 'economia']):
            category = 'negocios'
        elif any(k in text for k in ['tecno', 'python', 'inteligência artificial', 'inteligencia artificial', 'software', 'dev', 'computa']) or ' ia ' in text or ' ai ' in text:
            category = 'tecnologia'
        elif any(k in text for k in ['carreira', 'lideran', 'liderança', 'trabalho']):
            category = 'carreira'
        elif any(k in text for k in ['sociedade', 'filosofia', 'etica', 'ética', 'cultura']):
            category = 'sociedade'
        else:
            category = 'dados'

    destaque = bool(data.get('destaque', True))
    try:
        rating = float(data.get('rating', 4.8))
    except (ValueError, TypeError):
        rating = 4.8

    book_id = data.get('id', '').strip()
    if not book_id:
        slug = re.sub(r'[^\w\s-]', '', title.lower()).strip()
        slug = re.sub(r'[\s_]+', '-', slug)
        book_id = f'{slug}-{int(time.time())}'

    books = build_biblioteca.load_books()
    existing_index = next((i for i, b in enumerate(books) if b.get('id') == book_id), None)

    book_obj = {
        'id': book_id,
        'title': title,
        'author': author,
        'rating': rating,
        'amazon_link': amazon_link,
        'cover_image': cover_image,
        'short_desc': short_desc,
        'desc_full': desc_full,
        'tags': tags,
        'category': category,
        'destaque': destaque,
        'created_at': data.get('created_at') or datetime.now().strftime('%Y-%m-%d')
    }

    if existing_index is not None:
        books[existing_index] = book_obj
        action = 'atualizado'
    else:
        books.insert(0, book_obj)
        action = 'adicionado'

    try:
        build_success = build_biblioteca.save_books(books)
    except Exception as e:
        print(f'Erro ao compilar biblioteca: {e}')
        build_success = False

    return jsonify({
        'success': True,
        'book': book_obj,
        'build_success': build_success,
        'message': f"Livro '{title}' {action} com sucesso e biblioteca sincronizada!"
    })

@app.route('/api/book/<book_id>', methods=['DELETE'])
@app.route('/api/book/<book_id>/delete', methods=['POST'])
def delete_book(book_id):
    books = build_biblioteca.load_books()
    target_book = next((b for b in books if b.get('id') == book_id), None)
    
    if not target_book:
        return jsonify({'error': 'Livro não encontrado'}), 404

    books = [b for b in books if b.get('id') != book_id]
    
    try:
        build_success = build_biblioteca.save_books(books)
    except Exception as e:
        print(f'Erro ao compilar biblioteca após exclusão: {e}')
        build_success = False

    return jsonify({
        'success': True,
        'deleted_id': book_id,
        'build_success': build_success,
        'message': f"Livro '{target_book.get('title')}' removido com sucesso da biblioteca!"
    })

@app.route('/api/sync-biblioteca', methods=['POST', 'GET'])
def sync_biblioteca_endpoint():
    try:
        books = build_biblioteca.load_books()
        books = build_biblioteca.normalize_books(books)
        build_success = build_biblioteca.save_books(books)
        return jsonify({
            'success': True,
            'count': len(books),
            'build_success': build_success,
            'message': f'Biblioteca sincronizada com sucesso! {len(books)} livros atualizados na Biblioteca e destaques sincronizados na Home.'
        })
    except Exception as e:
        print(f'Erro na sincronização manual da biblioteca: {e}')
        return jsonify({'success': False, 'error': f'Erro ao sincronizar biblioteca: {str(e)}'}), 500

@app.route('/api/upload-book-cover', methods=['POST'])
def upload_book_cover():
    file = request.files.get('cover')
    if file and file.filename:
        orig_name = sanitize_filename(file.filename)
        base, ext = os.path.splitext(orig_name)
        if not ext:
            ext = '.webp'
        filename = f'{base}_{int(time.time())}{ext}'
        save_path = os.path.join(BOOK_COVERS_DIR, filename)
        file.save(save_path)
        relative_url = f'assets/img/Biblioteca page/{filename}'
        return jsonify({
            'success': True,
            'url': relative_url,
            'filename': filename,
            'message': 'Capa do livro enviada com sucesso!'
        })

    data = request.get_json(silent=True) or {}
    if 'image_data' in data:
        img_data = data['image_data']
        if ',' in img_data:
            header, encoded = img_data.split(',', 1)
            ext = '.webp'
            if 'jpeg' in header or 'jpg' in header:
                ext = '.jpg'
            elif 'png' in header:
                ext = '.png'
            binary = base64.b64decode(encoded)
            filename = f'capa_{int(time.time())}{ext}'
            save_path = os.path.join(BOOK_COVERS_DIR, filename)
            with open(save_path, 'wb') as f:
                f.write(binary)
            relative_url = f'assets/img/Biblioteca page/{filename}'
            return jsonify({
                'success': True,
                'url': relative_url,
                'filename': filename,
                'message': 'Capa salva com sucesso!'
            })

    return jsonify({'error': 'Nenhuma imagem recebida'}), 400

@app.route('/api/book-covers', methods=['GET'])
def list_book_covers():
    images = []
    # Pasta Biblioteca page (uploads)
    if os.path.exists(BOOK_COVERS_DIR):
        for f in os.listdir(BOOK_COVERS_DIR):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg')):
                images.append({
                    'filename': f,
                    'url': f'assets/img/Biblioteca page/{f}'
                })
    # Pasta books (capas existentes do catálogo do site)
    books_dir = os.path.join(SITE_DIR, 'assets', 'img', 'books')
    if os.path.exists(books_dir):
        for f in os.listdir(books_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg')):
                images.append({
                    'filename': f,
                    'url': f'assets/img/books/{f}'
                })
    return jsonify(images)

def open_browser():
    time.sleep(1.2)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    if '--test' in sys.argv:
        print('Test mode: App-Editor-Blog Flask app initialized successfully.')
        sys.exit(0)

    print('════════════════════════════════════════════════════════════')
    print(' 🚀 Marcos Data Product — Editor de Artigos para o Blog')
    print(' Pasta do Site conectada:', SITE_DIR)
    print(' Servidor local iniciado em: http://localhost:5000')
    print(' Pressione Ctrl+C no terminal para encerrar.')
    print('════════════════════════════════════════════════════════════')
    
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
