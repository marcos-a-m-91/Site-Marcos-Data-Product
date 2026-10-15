# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
- **Público Primário:** Comunidade técnica de dados, estudantes, analistas e profissionais do ecossistema de dados buscando referências práticas, tutoriais aprofundados e playbooks de excelência.
- **Público Secundário:** Líderes técnicos, gestores de BI/Analytics e recrutadores avaliando senioridade, capacidade de entrega e visão de arquitetura orientada a produtos de dados.

## Product Purpose
Servir como o hub definitivo de autoridade e compartilhamento de conhecimento de Marcos Aurélio em Produtos de Dados. O site existe para democratizar técnicas avançadas de Analytics, IA aplicada e Data Visualization, apresentando estudos de caso reais, playbooks acionáveis e artigos técnicos que elevam o padrão de engenharia e produto na comunidade.

## Positioning
Posicionamento como especialista sênior em Produtos de Dados (*Data as a Product*), unindo rigor analítico e modelagem de alta performance (Star Schema, DAX, Governança), Inteligência Artificial prática (Sistemas Agênticos, Engenharia de Prompt e RAG) e UX Executivo / Data Storytelling de alto impacto visual.

## Operating Context
- Acesso prioritário via desktop e notebooks por profissionais durante estudos técnicos, trabalho ou benchmarking de arquiteturas.
- Acesso móvel para consumo rápido de artigos no Blog e consulta a playbooks.
- Ambientes de deploy estático (GitHub Pages / Vercel) com pipelines locais de compilação em Python (`tools/editor.py`, `tools/build_blog.py`).

## Capabilities and Constraints
- **Arquitetura Web:** Páginas estáticas em HTML5 semântico, estilização com Design Tokens inspirados no GitHub Primer e utilitários modernos, interatividade com JavaScript modular (GSAP, Three.js, Lucide).
- **Conteúdo Orientado a Markdown:** Gestão de artigos via arquivos `.md` com frontmatter YAML no diretório `content/posts/`, compilados automaticamente para HTML estático em `blog/`.
- **Restrições:** Performance de carregamento veloz, suporte estrito a acessibilidade semântica (a11y), preservação da consistência estética entre as seções (Home, Playbooks, Blog, Projetos, Biblioteca, Sobre).

## Brand Commitments
- **Nome e Marca:** Marcos Data Product / Marcos Aurélio — Senior Business Analytics & Data Product Specialist.
- **Voz e Tom:** Técnico, preciso, didático, pragmático e autoritativo sem arrogância; linguagem focada em valor de negócio, clareza arquitetural e excelência visual.
- **Identidade Visual Existente:** Interface refinada estilo "engineering craft", tons sóbrios e balanceados, contraste apurado, microinterações fluidas e tipografia limpa.

## Evidence on Hand
- Repositório ativo com portfólio de projetos estruturados em `projetos/` e `projetos.html`.
- Hub de playbooks especializados (`powerbi.html`, `ia.html`, `dataviz.html`).
- Feed ativo de blog em `blog.html` e artigos completos em `content/posts/`.
- Curadoria literária e referências técnicas em `biblioteca.html`.
- Ferramental de automação em Python (`tools/editor.py`, `tools/build_blog.py`).

## Product Principles
1. **Rigor e Substância Técnica Primeiro:** Nenhum conteúdo ou interface deve ser superficial; cada seção entrega utilidade prática imediata e fundamentação sólida.
2. **Data as a Product & Craft:** Tratar a informação e a interface com o mesmo cuidado de um produto de software de classe mundial — design limpo, legibilidade impecável e zero distrações desnecessárias.
3. **Didática e Reprodutibilidade:** Códigos, diagramas e tutoriais devem ser claros, reproduzíveis e estruturados com alto valor de consulta.
4. **Respeito aos Padrões Abertos da Web:** Estrutura semântica rápida, acessível e resiliente, sem dependências pesadas desnecessárias no runtime final.
