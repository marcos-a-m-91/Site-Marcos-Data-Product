import os
import re
import sys
import glob
import json
import base64
import time
import threading
import webbrowser
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
import yaml

# Adicionar pasta tools ao path para importar build_blog
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(TOOLS_DIR, '..'))
POSTS_DIR = os.path.join(ROOT_DIR, 'content', 'posts')
IMAGES_DIR = os.path.join(ROOT_DIR, 'assets', 'img', 'blog')

os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

sys.path.insert(0, TOOLS_DIR)
import build_blog

app = Flask(__name__, template_folder=os.path.join(TOOLS_DIR, 'templates'))
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB max upload

# Servir arquivos estáticos da pasta assets
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(ROOT_DIR, 'assets'), filename)

@app.route('/blog/<path:filename>')
def serve_blog(filename):
    return send_from_directory(os.path.join(ROOT_DIR, 'blog'), filename)

@app.route('/blog.html')
def serve_blog_hub():
    return send_from_directory(ROOT_DIR, 'blog.html')

@app.route('/')
def index():
    return render_template('editor.html')

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
            print(f"Erro ao ler {fp}: {e}")
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

def sanitize_filename(name):
    # Transforma nome em seguro para web
    name = re.sub(r'[^\w\.\-\_]', '_', name.strip().lower())
    return re.sub(r'__+', '_', name)

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    # 1. Upload via formulário multipart
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

        orig_name = sanitize_filename(file.filename)
        base, ext = os.path.splitext(orig_name)
        if not ext:
            ext = '.png'

        filename = f"{base}_{int(time.time())}{ext}"
        save_path = os.path.join(IMAGES_DIR, filename)
        file.save(save_path)

        relative_url = f"assets/img/blog/{filename}"
        return jsonify({
            'success': True,
            'url': relative_url,
            'filename': filename,
            'message': 'Imagem enviada com sucesso!'
        })

    # 2. Upload via Base64 (colado via clipboard Ctrl+V)
    data = request.get_json(silent=True) or {}
    if 'image_data' in data:
        img_data = data['image_data']
        # extrair formato data:image/png;base64,....
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
            filename = f"clipboard_{int(time.time())}{ext}"
            save_path = os.path.join(IMAGES_DIR, filename)
            with open(save_path, 'wb') as f:
                f.write(binary)

            relative_url = f"assets/img/blog/{filename}"
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

    # Montar o dicionário YAML Frontmatter ordenado
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
    file_content = f"---\n{yaml_header}---\n\n{raw_body}\n"

    # Verificar se já existe arquivo com esse slug
    existing_file = None
    for fp in glob.glob(os.path.join(POSTS_DIR, '*.md')):
        p = build_blog.parse_post(fp)
        if p.get('slug') == slug:
            existing_file = fp
            break

    if existing_file:
        target_path = existing_file
    else:
        # Se novo arquivo, prefixar com a data
        target_path = os.path.join(POSTS_DIR, f"{date_val}-{slug}.md")

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(file_content)

    print(f"Post salvo em: {target_path}")

    # Executar build do blog automaticamente
    try:
        build_blog.build_all()
        build_success = True
    except Exception as e:
        print(f"Erro ao compilar blog: {e}")
        build_success = False

    return jsonify({
        'success': True,
        'slug': slug,
        'target_file': os.path.basename(target_path),
        'post_url': f"blog/{slug}.html",
        'hub_url': "blog.html",
        'build_success': build_success,
        'message': f"Artigo '{title}' publicado e compilado com sucesso!"
    })

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://localhost:5000")

if __name__ == '__main__':
    if '--test' in sys.argv:
        print("Test mode: Flask app initialized successfully.")
        sys.exit(0)

    print("════════════════════════════════════════════════════════════")
    print(" 🚀 Marcos Data Product — Editor de Artigos para o Blog")
    print(" Servidor local iniciado em: http://localhost:5000")
    print(" Pressione Ctrl+C no terminal para encerrar.")
    print("════════════════════════════════════════════════════════════")
    
    # Abrir navegador automaticamente
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
