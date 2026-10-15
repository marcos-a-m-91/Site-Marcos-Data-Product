# Diretrizes de UI Craft & Microinterações (Emil Kowalski)

Estas regras codificam a filosofia de *Design Engineering* e acabamento de interface de **Emil Kowalski** (ex-Vercel, Linear, criador do Sonner, Vaul e animations.dev). Qualquer alteração de CSS, HTML ou componentes neste projeto deve seguir rigorosamente estes padrões:

---

## 1. Regras Absolutas de Performance (GPU-First)
- **Nunca use `transition: all`.** Sempre declare as propriedades exatas que serão animadas (ex: `transition: transform 160ms var(--ease-out), background-color 160ms var(--ease-out);`).
- **Anime exclusivamente propriedades aceleradas pela GPU:**
  - Permitido: `transform`, `opacity`.
  - Aceitável para microinterações de cor: `background-color`, `border-color`, `box-shadow`.
  - **PROIBIDO animar:** `width`, `height`, `margin`, `padding`, `top`, `left`, `right`, `bottom` (causam layout recalculation e perda de frames).

---

## 2. Tokens de Movimento & Curvas (Easings)
Use sempre as variáveis de curva definidas em `:root` no `main.css`:
- `--ease-out: cubic-bezier(0.23, 1, 0.32, 1);` — Para entradas, hovers e respostas instantâneas (começa rápido, desacelera suavemente).
- `--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);` — Para elementos já visíveis que se movimentam na tela.
- `--ease-spring: cubic-bezier(0.16, 1, 0.3, 1);` — Para transições suaves e expansões elásticas (estilo Linear / iOS).
- **PROIBIDO `ease-in` em UI:** Curvas `ease-in` iniciam devagar e transmitem sensação de lentidão e travamento.

---

## 3. Durações & Percepção de Velocidade
- **Teto de 300ms:** Qualquer animação de elemento de interface (dropdown, popover, badge, tooltip) deve durar menos de 300ms.
- **Tabela de durações de referência:**
  - Feedback tátil de clique / `:active`: `100ms – 160ms`
  - Tooltips e pequenos popovers: `125ms – 200ms`
  - Dropdowns e menus: `150ms – 250ms`
  - Modais e gavetas (drawers): `200ms – 300ms`
- **Ações frequentes (100+ vezes ao dia):** Não devem ter animação ou devem ser quase instantâneas.

---

## 4. Física, Escala & Origem
- **Nunca anime a partir de `scale(0)`:** Nada no mundo real surge de um ponto invisível do nada. Entradas de elementos devem partir de `scale(0.95)` combinado com `opacity: 0` até `scale(1)` e `opacity: 1`.
- **Feedback tátil obrigatório (`:active`):** Todo botão ou card clicável precisa confirmar o clique com:
  ```css
  .btn:active, .card-clickable:active {
    transform: scale(0.97);
  }
  ```
- **Origem de transformação (`transform-origin`):** Popovers e dropdowns devem expandir a partir do elemento disparador, nunca do centro (`center`), com exceção de modais centralizados na tela.

---

## 5. Acessibilidade e Proteção Mobile
- **Reduced Motion:** Respeite sempre `@media (prefers-reduced-motion: reduce)` substituindo transformações espaciais por transições sutis de opacidade ou cortes diretos.
- **Hover Gating:** Proteja interações com `@media (hover: hover) and (pointer: fine)` para evitar que dispositivos touch fiquem com efeitos de hover presos após o toque.
