# Diretório: Livros da Biblioteca (Marcos Data Product)

Este diretório está reservado para a publicação de páginas individuais e aprofundadas de resenhas/fichamentos de livros recomendados no ecossistema **Marcos Data Product**.

---

## Como Funciona o Catálogo da Biblioteca

- **Catálogo Central**: Todas as obras e curadorias ativas são gerenciadas através do arquivo de dados `content/books.json` e exibidas dinamicamente na página [biblioteca.html](../biblioteca.html).
- **Sincronização**: O script `tools/build_biblioteca.py` garante a sincronização automática entre os dados em `content/books.json` e a exibição offline/online em `biblioteca.html`.
- **Capas Oficiais**: As capas dos livros ficam centralizadas no diretório `assets/img/books/`.
- **Páginas de Resenha Aprofundada**: Quando uma resenha ou fichamento completo for gerado para um livro, a página HTML correspondente deve ser criada nesta pasta (ex: `livros/inspired.html`), adotando os padrões visuais oficiais:
  - Fonte `Inter`
  - Sticky Navbar institucional
  - Rodapé Institucional Deep Navy (`#0B1E3A`)
