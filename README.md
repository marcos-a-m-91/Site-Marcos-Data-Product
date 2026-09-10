# Marcos Data Product — Portfolio & Site

Este é o repositório do site profissional de **Marcos Aurélio**, Senior Business Analytics. O projeto foi reestruturado para ser profissional, escalável e pronto para deploy.

## 🚀 Estrutura do Projeto

```text
/
├── assets/
│   ├── css/          # Estilos centralizados (main.css - GitHub Primer Light)
│   ├── js/           # Scripts utilitários compartilhados (main.js)
│   ├── img/          # Imagens, logotipos e ilustrações
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

- **HTML5/CSS3**: Estrutura e estilização moderna com Glassmorphism.
- **Tailwind CSS**: Utilitários para layout responsivo.
- **GSAP & ScrollTrigger**: Animações de alto nível e interações de scroll.
- **Three.js**: Fundo interativo com partículas e geometria 3D.
- **Lucide Icons**: Conjunto de ícones premium.

## 🤖 Automação

Para manter a consistência entre a página inicial e a página "Sobre", utilize o script:
```bash
python tools/build_sobre.py
```
Este script sincroniza o `<head>` e o menu de navegação do `index.html` para o `sobre.html`.

## 🌐 Deploy

O projeto está otimizado para deploy em plataformas como **GitHub Pages**, **Vercel** ou **Netlify**. Basta apontar para a raiz do repositório.
