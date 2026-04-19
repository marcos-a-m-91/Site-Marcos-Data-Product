# Marcos Data Product — Portfolio & Site

Este é o repositório do site profissional de **Marcos Aurélio**, Senior Business Analytics. O projeto foi reestruturado para ser profissional, escalável e pronto para deploy.

## 🚀 Estrutura do Projeto

```text
/
├── assets/
│   ├── css/          # Estilos centralizados (main.css)
│   ├── js/           # Scripts utilitários (main.js)
│   ├── img/          # Imagens, logotipos e frames de animação
│   └── vendor/       # Bibliotecas externas (GSAP, Tailwind, Lucide, Fonts)
├── tools/            # Scripts de automação (ex: build_sobre.py)
├── index.html        # Página principal
├── sobre.html        # Página "Sobre" (gerada automaticamente)
├── design_system.html # Referência visual e componentes
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
