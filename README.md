# Marcos Data Product — Portfolio & Site

Este é o repositório do site profissional de **Marcos Aurélio**, Senior Business Analytics. O projeto foi reestruturado para ser profissional, escalável e pronto para deploy.

## 🚀 Estrutura do Projeto

```text
/
├── content/
│   └── posts/        # Artigos em Markdown (.md) com frontmatter
├── blog/             # Páginas HTML dos artigos geradas automaticamente
├── blog.html         # Feed central do Blog com busca e filtros dinâmicos
├── assets/
│   ├── css/          # Estilos centralizados (main.css - GitHub Primer Light)
│   ├── js/           # Scripts utilitários compartilhados (main.js)
│   ├── img/          # Imagens, logotipos, capas do blog e ilustrações
│   └── vendor/       # Bibliotecas locais (GSAP, Tailwind, Lucide, Fonts)
├── references/       # Materiais de apoio, Brandbook e templates de referência
├── tools/            # Scripts de automação e utilitários Python
├── index.html        # Página principal (Home)
├── playbook.html     # Hub central do Playbook (portal com os 3 boxes pilares)
├── powerbi.html      # Playbook de Power BI (Modelagem Star Schema, DAX, templates .pbix)
├── ia.html           # Playbook de IA (Agentes, Engenharia de Prompt, RAG e Automação)
├── dataviz.html      # Playbook de Data Viz (Storytelling, Matriz de Gráficos e UX)
├── projetos.html     # Portfólio de projetos e estudos de caso
├── biblioteca.html   # Curadoria de livros, referências e leituras recomendadas
├── sobre.html        # Biografia profissional, trajetória e competências
├── design_system.html # Documentação viva de componentes e tokens visuais
└── README.md
```

## 🛠️ Tecnologias Utilizadas

- **HTML5/CSS3**: Estrutura e estilização moderna com Glassmorphism e Primer Design Tokens.
- **Tailwind CSS**: Utilitários para layout responsivo.
- **GSAP & ScrollTrigger**: Animações de alto nível e interações de scroll.
- **Three.js**: Fundo interativo com partículas e geometria 3D.
- **Lucide Icons**: Conjunto de ícones premium.
- **Python (Markdown + PyYAML)**: Compilação de posts estáticos e geração do feed do Blog.

## 🤖 Automações do Projeto

### 1. Publicar e Atualizar o Blog
Para compilar novos artigos escritos em Markdown (`content/posts/*.md`) para HTML e atualizar o feed:
```bash
python tools/build_blog.py
```

### 2. Sincronizar Página "Sobre"
Para manter a consistência do cabeçalho e navegação entre a Home e o `sobre.html`:
```bash
python tools/build_sobre.py
```

## 🌐 Deploy

O projeto está otimizado para deploy em plataformas como **GitHub Pages**, **Vercel** ou **Netlify**. Basta apontar para a raiz do repositório.
