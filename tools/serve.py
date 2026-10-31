import http.server
import socketserver
import os
import sys
import webbrowser

PORT = 8000
DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Tratar URL limpa (Clean URLs estilo Vercel)
        raw_path = self.path.split('?')[0].split('#')[0].rstrip('/')
        if raw_path == '':
            raw_path = '/index.html'

        clean_relative = raw_path.lstrip('/')
        disk_path = os.path.join(DIRECTORY, clean_relative)

        # 1. Se existe arquivo direto (ex: index.html, sobre.html, imagem, css)
        if os.path.exists(disk_path) and os.path.isfile(disk_path):
            return super().do_GET()

        # 2. Se não existe direto, mas existe .html correspondente (ex: /sobre -> sobre.html)
        if os.path.exists(disk_path + '.html') and os.path.isfile(disk_path + '.html'):
            query = self.path[len(raw_path):] if len(self.path) > len(raw_path) else ''
            self.path = raw_path + '.html' + query
            return super().do_GET()

        # 3. Rota não encontrada: exibir a sua página 404.html personalizada
        self.send_error(404)

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            custom_404 = os.path.join(DIRECTORY, '404.html')
            if os.path.exists(custom_404):
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache')
                with open(custom_404, 'rb') as f:
                    content = f.read()
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
        super().send_error(code, message, explain)

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), CleanURLHandler) as httpd:
        print("════════════════════════════════════════════════════════════")
        print(" 🚀 Marcos Data Product — Servidor Local")
        print(f" Pasta do Site: {DIRECTORY}")
        print(f" Servidor rodando em: http://localhost:{PORT}")
        print(" Suporte a Clean URLs e página 404.html personalizada ativo!")
        print(" Pressione Ctrl+C para encerrar.")
        print("════════════════════════════════════════════════════════════")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")
            sys.exit(0)
