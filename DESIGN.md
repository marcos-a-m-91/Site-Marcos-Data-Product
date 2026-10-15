---
name: Marcos Data Product
description: The Engineering Craft Sanctuary — Elegância técnica, precisão analítica e estética clean de documentação de alto padrão.
colors:
  primary: "#11376e"
  primary-hover: "#184a91"
  primary-subtle: "rgba(17, 55, 110, 0.08)"
  neutral-bg: "#ffffff"
  canvas-subtle: "#f6f8fa"
  page-bg: "#f8fafc"
  border-default: "#d0d7de"
  border-subtle: "rgba(31, 35, 40, 0.08)"
  text-primary: "#1f2328"
  text-secondary: "#656d76"
  text-muted: "#8c959f"
  accent-blue: "#11376e"
  accent-amber: "#9a6700"
  accent-emerald: "#1a7f37"
  accent-purple: "#8250df"
  accent-pink: "#bf3989"
typography:
  display:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "clamp(2.25rem, 5vw, 3.5rem)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "clamp(1.5rem, 3vw, 2.25rem)"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  label:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.01em"
  handwriting:
    fontFamily: "Caveat, cursive"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "normal"
rounded:
  sm: "4px"
  md: "6px"
  lg: "12px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: "12px 28px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-secondary:
    backgroundColor: "{colors.canvas-subtle}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: "12px 28px"
  badge:
    backgroundColor: "{colors.primary-subtle}"
    textColor: "{colors.primary}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
  card:
    backgroundColor: "{colors.neutral-bg}"
    rounded: "{rounded.lg}"
    padding: "24px"
---

# Design System

## Overview
- **Creative North Star:** *"The Engineering Craft Sanctuary"* — Uma união entre o rigor funcional do GitHub Primer e a elegância moderna de interfaces de engenharia analítica. A estética transmite clareza absoluta, precisão matemática e sobriedade técnica, tratando a informação com a gravidade de um produto analítico de nível enterprise.
- **Propósito:** Oferecer uma experiência de leitura e navegação fluida, sem distrações, altamente convidativa para o consumo de tutoriais densos, playbooks estratégicos e documentações de arquitetura.
- **Tom Visual:** Autoritativo, minimalista, estruturado, limpo e refinado.

---

## Colors

### 1. Marca & Destaques Primários
- **Brand Blue (`--brand-blue`):** `#11376e` (`rgb(17, 55, 110)`). Azul profundo corporativo, utilizado como cor âncora para CTAs primários, títulos principais, estados ativos e bordas em foco.
- **Brand Blue Hover (`--brand-blue-hover`):** `#184a91`.
- **Brand Blue Subtle (`--brand-blue-subtle`):** `rgba(17, 55, 110, 0.08)`. Utilizado em badges, chips e fundos de destaque secundário.

### 2. Base Neutra & Superfícies (Primer Light)
- **Canvas / Superfície de Card (`--canvas-default`):** `#ffffff`. Superfície limpa com borda sólida e sombra sutil.
- **Superfície Secundária (`--canvas-subtle` / `--void`):** `#f6f8fa`. Fundo de botões secundários, inputs e seções de apoio.
- **Fundo da Página (`body`):** `#f8fafc`. Suave contraste off-white que reduz a fadiga visual em leitura prolongada.
- **Bordas Estruturais (`--border-default`):** `#d0d7de`. Delimitação física nítida sem ruído.
- **Bordas Suaves (`--border-subtle`):** `rgba(31, 35, 40, 0.08)`.

### 3. Tipografia & Contrastes
- **Texto Primário (`--text-primary`):** `#1f2328`. Preto grafite de alto contraste para leitura sem esforço (WCAG AAA).
- **Texto Secundário (`--text-secondary`):** `#656d76`. Cinza balanceado para descrições, metadados e subtítulos.
- **Texto Mudo / Legendas (`--text-muted`):** `#8c959f`. Datas, tags secundárias e placeholders.

### 4. Cores Semânticas de Apoio
- **Amber (Power BI / Alertas):** `#9a6700` (`rgba(154, 103, 0, 0.08)` em fundos).
- **Emerald (Sucesso / Métricas / Data Viz):** `#1a7f37` (`rgba(26, 127, 55, 0.08)` em fundos).
- **Purple (IA / Inovação / Agentes):** `#8250df` (`rgba(130, 80, 223, 0.08)` em fundos).
- **Pink (Destaques Especiais):** `#bf3989`.

---

## Typography

- **Família Tipográfica Principal:** `'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans", sans-serif`.
- **Monoespaçada (Códigos e Fórmulas DAX):** `'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, monospace`.

### Escala Tipográfica
- **Display (Hero Headline):** `clamp(2.25rem, 5vw, 3.5rem)`, peso `700`, line-height `1.15`, letter-spacing `-0.03em`.
- **Headline (H1/H2 de Seção):** `clamp(1.5rem, 3vw, 2.25rem)`, peso `600`, line-height `1.25`, letter-spacing `-0.02em`.
- **Title (H3 / Títulos de Card):** `1.125rem` a `1.25rem`, peso `600`, line-height `1.4`.
- **Body (Texto Principal):** `1rem` (`16px`), peso `400`, line-height `1.6` a `1.7` para máximo conforto de leitura.
- **Body Small / Captions:** `0.875rem` (`14px`), peso `400` / `500`, line-height `1.5`.
- **Labels / Badges:** `0.75rem` a `0.8125rem`, peso `500` / `600`, letter-spacing `0.02em`, uppercase ou titlecase consistente.

---

## Layout

- **Container Central Padrão:** `max-w-6xl` (`72rem` / `1152px`) ou `max-w-7xl` (`80rem` / `1280px`) com preenchimento lateral responsivo (`px-4 sm:px-6 lg:px-8`).
- **Ritmo Vertical:** Seções com respiro generoso (`py-16` a `py-24`).
- **Sistema de Grid:**
  - Cards e Playbooks: 3 colunas em desktop (`grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6` ou `gap-8`).
  - Feeds de Artigos / Projetos: 2 colunas com destaque para cards horizontais em telas médias/grandes.
- **Overlay Técnico de Fundo:** Padrão sutil de grade radial de 32px (`background-image: radial-gradient(#d0d7de 1px, transparent 1px)`) com opacidade de 35%, ancorando a temática de engenharia.

---

## Elevation & Depth

- **Nível 0 (Flat):** Fundo de página `#f8fafc` com elementos integrados sem sombra.
- **Nível 1 (Superfície Base - `.glass` / Cards):**
  - Fundo: `#ffffff`.
  - Borda: `1px solid var(--border-default)`.
  - Sombra: `0 1px 3px rgba(31, 35, 40, 0.08), 0 1px 2px rgba(31, 35, 40, 0.04)`.
- **Nível 2 (Cards em Hover & Dropdowns - `.glass-strong`):**
  - Sombra: `0 8px 24px rgba(17, 55, 110, 0.12), 0 2px 6px rgba(31, 35, 40, 0.04)`.
  - Elevação física com microinteração: `transform: translateY(-2px)` a `translateY(-4px)`.
- **Glows de Iluminação Sutil:** `section-glow` pontuais com `filter: blur(120px)` e opacidade controlada (`0.05` a `0.08`) em azul da marca, sem saturar a visão.

---

## Shapes

- **Controle de Cantos (Border Radius):**
  - **Inputs & Botões:** `6px` (`rounded-md` estilo Primer clássico) ou `8px`.
  - **Cards & Banners:** `12px` (`rounded-xl`), proporcionando modernidade sem infantilizar a interface.
  - **Segmented Controls & Pills de Navegação:** `9999px` (`rounded-full`), garantindo affordance tátil de cápsula.
  - **Badges e Tags:** `9999px` (`rounded-full`) ou `6px`.
- **Bordas Físicas:** Todo container elevado possui uma borda sólida explícita de `1px` (`#d0d7de`), eliminando qualquer sensação de indefinição ou elemento flutuando sem peso.

---

## Components

### 1. Botões
- **Primário (`.btn-primary`):** Fundo `#11376e`, texto `#ffffff`, padding `0.75rem 1.75rem`, raio `6px`, sombra de precisão, efeito sutil de ripple e microinteração de escala (`transform: scale(0.97)` no clique).
- **Secundário (`.btn-secondary`):** Fundo `#f6f8fa`, texto `#1f2328`, borda `1px solid #d0d7de`, hover com destaque em azul.

### 2. Segmented Pill Nav (`#navbar`)
- Barra de navegação com grupo de links em cápsula flutuante (`.nav-pill-group`).
- Ao scrollar: ativa `backdrop-filter: blur(16px)` com fundo branco translúcido (`rgba(255, 255, 255, 0.92)`).

### 3. Cards de Projetos & Playbooks
- Cabeçalho com ícone vetorial temático (Lucide Icons) em container circular ou quadrado com cantos suaves.
- Título nítido, resumo objetivo, tags de tecnologia e link acionável com seta animada.

### 4. Badges & Tags
- Cores de fundo diluídas (`rgba(..., 0.08)`) com texto na cor âncora pura.
- Padding compacto (`0.25rem 0.75rem`), peso semibold e tipografia nítida.

---

## Do's and Don'ts

### ✅ O que FAZER (Do's)
- **Priorizar Legibilidade:** Garantir que blocos de texto longo tenham largura máxima controlada (`max-w-prose` ou `65ch`) e espaçamento confortável.
- **Manter Consistência de Tokens:** Sempre utilizar as variáveis CSS de cor e espaçamento (`var(--brand-blue)`, `var(--border-default)`, etc.).
- **Microinterações com Propósito:** Utilizar as curvas de animação de Emil Kowalski (`--ease-out: cubic-bezier(0.23, 1, 0.32, 1)`, durabilidade de `160ms` a `250ms`).
- **Contraste Rígido:** Todo texto interativo deve atender aos critérios de contraste WCAG AA/AAA.

### ❌ O que NÃO FAZER (Don'ts)
- **Sem "AI Slop":** Nunca utilizar gradientes roxos genéricos no fundo ou sombras difusas desproporcionais sem borda de contenção.
- **Não aninhar Cards dentro de Cards:** Se um card precisa de agrupamento interno, use divisores sutis (`1px border-subtle`) ou variação de fundo tonal (`--canvas-subtle`), não outro card com sombra.
- **Não usar preto puro (#000000):** Use sempre o grafite primário `#1f2328` para textos e fundos.
- **Não usar cinza de baixo contraste:** Evitar textos abaixo de `#656d76` sobre fundos brancos.
- **Não exagerar em animações:** Não usar saltos elásticos ou rotações lentas que atrasem o uso da ferramenta ou causem distração durante o estudo técnico.
