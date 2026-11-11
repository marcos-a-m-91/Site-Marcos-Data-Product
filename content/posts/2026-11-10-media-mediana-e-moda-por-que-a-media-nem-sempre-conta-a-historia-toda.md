---
title: 'Média, mediana e moda: por que a média nem sempre conta a história toda?'
slug: media-mediana-e-moda-por-que-a-media-nem-sempre-conta-a-historia-toda
date: '2026-11-10'
author: Marcos Aurélio
category: Business Analytics
category_color: blue
read_time: 8 min
excerpt: Uma nota 5,0 é sempre melhor que uma 4,8? Entenda como média, mediana e moda
  ajudam a interpretar dados e tomar decisões melhores.
cover: assets/img/blog/imagem1_1794352142.png
featured: true
tags:
- Estatística
- Estatística Descritiva
- Média
- Mediana
- Moda
- Análise de dados
- Tomada de Decisão
- Data 101
---

Imagine que você precisa viajar para São Paulo e está procurando um Airbnb para se hospedar. Depois de analisar localização, preço e comodidades, você chega a duas opções:

![Imagem4.png](/assets/img/blog/media-mediana-e-moda-por-que-a-media-nem-sempre-conta-a-historia-toda_imagem4_1794351968_1.png)

Qual delas você escolheria?

Se sua resposta imediata foi a opção 1, talvez valha a pena olhar os números com um pouco mais de atenção.

Esse exemplo aparentemente simples esconde algumas das ideias mais importantes da estatística descritiva. Entendê-las pode mudar a forma como interpretamos avaliações, indicadores de desempenho, pesquisas e praticamente qualquer conjunto de dados.

Inspirado no livro *Naked Statistics*, de Charles Wheelan, quero explorar três conceitos fundamentais da estatística descritiva: **média, mediana e moda**.

A proposta é entender não apenas como essas medidas funcionam, mas principalmente o que cada uma revela — e o que pode deixar de mostrar.

---

## O problema dos números que “mentem” sem mentir

A estatística descritiva tem um objetivo importante: transformar grandes volumes de dados em informações que possamos compreender e interpretar.

Para isso, utilizamos medidas de resumo, gráficos e outras ferramentas que ajudam a identificar padrões e características de uma distribuição.

O problema é que toda simplificação tem um custo: parte da informação original fica de fora.

Uma frase de Charles Wheelan, no livro, resume bem essa ideia:

> As estatísticas descritivas podem ser como perfis de namoro online: tecnicamente corretas e ainda assim bem enganosas
> 

O ponto central é que um número pode estar matematicamente correto e, mesmo assim, transmitir uma impressão incompleta da realidade.

É por isso que precisamos entender o que existe por trás das medidas que utilizamos.

---

## 1. Média: a ferramenta mais usada (e a mais mal usada)

A média aritmética é provavelmente a medida estatística mais conhecida. Seu cálculo é simples: somamos todos os valores e dividimos o resultado pela quantidade de observações.

Em outras palavras:

- Jeito que todo mundo entende

$$
\text{média} = \frac{\text{soma dos valores}}{\text{número de elementos}}
$$

- Jeito na linguagem matemática

$$
\bar{x} = \frac{\sum_{i=1}^{n} x_i}{n}
$$

Mas entender a fórmula não é suficiente. Precisamos observar como ela se comporta diante dos dados.

### Quando um único valor muda tudo

Imagine dez pessoas sentadas em um bar. Cada uma recebe R$ 5 mil por mês.

Nesse cenário, a renda média é de R$ 5 mil.

Agora imagine que Virginia Fonseca entra no estabelecimento, com uma renda hipotética de R$ 6 milhões mensais (um número ilustrativo, sem compromisso com a realidade).

A média de renda das onze pessoas passa a ser aproximadamente R$ 550 mil.

Perceba o que aconteceu: nenhuma das dez pessoas ficou mais rica, mas a média aumentou de R$ 5 mil para aproximadamente R$ 550 mil.

O responsável por essa distorção é um **outlier**, também chamado de valor atípico: uma observação muito distante das demais.

Esse fenômeno não acontece apenas em exemplos hipotéticos. Podemos encontrá-lo em diversas situações:

- **Renda:** a renda média de uma população pode aumentar significativamente porque uma pequena parcela ficou muito mais rica, mesmo que a renda da maioria permaneça estagnada.
- **Educação:** a média de uma turma pode ser elevada por alguns alunos com notas muito altas, mesmo que boa parte tenha dificuldades de aprendizagem.
- **Avaliações:** a nota média de um produto pode esconder uma distribuição bastante desigual entre clientes muito satisfeitos e muito insatisfeitos.

A média não está errada em nenhum desses casos. O problema é interpretá-la sem conhecer a distribuição dos dados.

---

## 2. Mediana: o antídoto para os outliers

A mediana é uma medida de tendência central que representa o valor localizado no meio de um conjunto de dados ordenados.

Para encontrá-la, organizamos os valores do menor para o maior e identificamos a posição central.

- Quando temos uma quantidade ímpar de observações, a mediana é o valor central.
- Quando temos uma quantidade par, calculamos a média dos dois valores centrais.

Voltando ao exemplo do bar: temos dez pessoas com renda de R$ 5 mil e a Virginia, com renda hipotética de R$ 6 milhões.

A renda mediana continua sendo R$ 5 mil.

Isso acontece porque a mediana depende da posição dos valores ordenados, e não da magnitude de todos eles.

Por essa característica, ela é menos sensível a valores extremos do que a média.

Se outra pessoa com renda muito elevada entrar no bar, por exemplo, a mediana continuará em R$ 5 mil.

### Quando utilizar a mediana?

A mediana é especialmente útil quando trabalhamos com distribuições assimétricas ou que apresentam valores extremos.

Alguns exemplos:

- **Renda:** a renda mediana costuma representar melhor a condição econômica de uma pessoa típica do que a renda média.
- **Imóveis:** o preço mediano de venda pode ser mais representativo quando existem imóveis de luxo com valores muito superiores aos demais.
- **Tempo de atendimento:** a mediana pode representar melhor o tempo de espera habitual quando alguns atendimentos excepcionalmente longos distorcem a média.

Uma boa prática é analisar média e mediana em conjunto.

Quando existe uma diferença expressiva entre elas, vale investigar a distribuição dos dados, a presença de valores extremos e possíveis assimetrias.

Essa diferença não prova, sozinha, que existem outliers, mas é um sinal de que precisamos olhar mais de perto.

---

## 3. Moda: o valor mais frequente

A moda é a medida de tendência central mais simples de identificar: representa o valor que aparece com maior frequência em um conjunto de dados.

Diferentemente da média e da mediana, a moda também pode ser utilizada em dados categóricos, nos quais não existe uma operação matemática de soma ou ordenação.

| Nota | Qnt. Avaliações |
| --- | --- |
| 1 | 5 |
| 2 | 10 |
| 3 | 15 |
| 4 | 70 |
| 5 | 30 |

Nesse exemplo, a moda é 4, pois essa é a nota que aparece com maior frequência.

Isso nos permite identificar a avaliação mais comum entre os usuários.

Mas existe uma diferença importante: a moda não representa necessariamente a maioria absoluta. Ela representa apenas a categoria ou o valor mais frequente.

Em análises de produtos digitais, por exemplo, essa informação pode ajudar a compreender padrões de satisfação, comportamento e percepção dos usuários.

A média nos ajuda a entender o resultado agregado. A moda mostra qual avaliação aparece mais frequentemente. Cada medida responde a uma pergunta diferente.

---

## Voltando ao casa do Airbnb

Agora que entendemos os três conceitos, podemos voltar à situação inicial.

Imagine que as duas opções apresentam os seguintes indicadores:

| Indicador | Opção 1 | Opção 2 |
| --- | --- | --- |
| Nota Média | 5 | 4,8 |
| Avaliações | 10 | 120 |

A opção 1 possui apenas dez avaliações. A opção 2 possui 120.

Isso não significa que a segunda opção seja necessariamente melhor, mas indica que temos uma base maior de experiências para avaliar sua reputação.

Uma média de 5,0 construída sobre dez avaliações pode ser mais sensível a novas observações do que uma média de 4,8 construída sobre 120 avaliações.

Em outras palavras, a primeira nota possui menos observações sustentando o resultado e, portanto, pode apresentar maior instabilidade.

### O que eu analiso antes de escolher?

Além da média, existem outras informações que ajudam a construir uma decisão mais consistente:

**1. Quantidade de avaliações**

Além da média, existem outras informações que ajudam a construir uma decisão mais consistente:

**2. Quantidade de avaliações**

Não olharia apenas para a média. Verificaria como as avaliações estão distribuídas entre as notas 1 e 5.

**3. Moda**

Identificaria qual nota aparece com maior frequência. Se a moda for 5, por exemplo, significa que essa é a avaliação mais comum, mesmo que a média seja inferior a 5.

**4. Comentários recentes**

Esse é um ponto especialmente importante para hospedagens.

Em São Paulo, por exemplo, a existência de obras nas proximidades pode afetar a experiência dos hóspedes. Por isso, procuraria comentários recentes sobre barulho, limpeza, conservação e localização.

Afinal, uma avaliação de dois anos atrás pode não representar as condições atuais do imóvel.

A decisão, portanto, não deveria ser baseada exclusivamente na maior média.

O ideal é combinar diferentes informações para construir uma visão mais completa do cenário.

---

## O que esses três conceitos nos ensinam?

Média, mediana e moda são medidas simples, mas respondem a perguntas diferentes:

| Medida | Pergunta que responde? |
| --- | --- |
| Média | Qual é o resultado médio considerando todos os valores? |
| Mediana | Qual é o valor que ocupa a posição central? |
| Moda | Qual é o valor mais frequente? |

Nenhuma delas é universalmente melhor.

A escolha depende da pergunta que queremos responder, da distribuição dos dados e do contexto em que estamos trabalhando.

Esse é um dos princípios mais importantes da análise de dados: **antes de escolher uma métrica, precisamos entender o problema que queremos investigar.**

Conhecer uma fórmula é importante. Saber quando utilizá-la, interpretar seus resultados e reconhecer suas limitações é o que realmente faz diferença.

---

<aside>
⚠️

Leitura recomendada

Se você quer desenvolver sua compreensão sobre estatística sem começar por fórmulas complexas, recomendo *Naked Statistics: Stripping the Dread from the Data*, de Charles Wheelan.

O livro apresenta conceitos estatísticos por meio de situações cotidianas, exemplos bem-humorados e explicações acessíveis.

Uma boa leitura para perceber que estatística não é apenas sobre calcular números. É sobre entender o que eles representam, questionar o que estão mostrando e identificar o que podem estar escondendo.

</aside>
