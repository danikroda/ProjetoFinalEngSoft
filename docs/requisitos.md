# StockFlow — Requisitos do Sistema

---

## 1. Elicitação de Requisitos

### 1.1 Contexto e Problema

Pequenas e médias empresas gerenciam estoque de forma manual ou semi-manual, gerando quatro classes de problema:

| Problema | Impacto operacional |
|---|---|
| Ruptura de estoque | Perda de venda; cliente busca concorrente |
| Excesso de estoque | Capital imobilizado; risco de vencimento/obsolescência |
| Erros de inventário | Divergência entre físico e registrado; retrabalho de contagem |
| Falta de rastreabilidade | Sem histórico confiável; impossibilidade de auditar movimentações |

O StockFlow ataca todos os quatro usando regras de negócio encapsuladas e comportamento verificável via testes automatizados.

---

### 1.2 Stakeholders Identificados

| Stakeholder | Papel | Interesse principal |
|---|---|---|
| Gestor de compras | Primário | Visualizar estoque atual, receber alertas de nível mínimo, gerar relatórios |
| Lojista / Operador | Primário | Registrar entradas e saídas rapidamente via CLI |
| Equipe de desenvolvimento | Interno | Código de domínio isolado, testável sem dependência de API real |
| Auditoria / Contabilidade | Secundário | Histórico de movimentações com data, tipo e responsável |
| Google (plataforma) | Externo | Conformidade com os limites de uso da Sheets API |

---

### 1.3 Histórias de Usuário

As histórias estão organizadas por papel e prioridade (MoSCoW).

#### Como Gestor de Compras

| ID | História | Prioridade |
|---|---|---|
| HU-01 | Quero visualizar a quantidade atual de cada produto para saber o que precisa ser reposto. | Must |
| HU-02 | Quero receber um alerta quando um produto atingir o nível mínimo para fazer o pedido antes de faltar. | Must |
| HU-03 | Quero consultar o histórico de movimentações de um produto específico para identificar padrões de consumo. | Should |
| HU-04 | Quero filtrar produtos por categoria para facilitar o planejamento de compras por seção. | Could |
| HU-05 | Quero exportar um relatório de estoque atual para compartilhar com o fornecedor. | Could |

#### Como Operador / Lojista

| ID | História | Prioridade |
|---|---|---|
| HU-06 | Quero registrar a entrada de um lote de produtos informando quantidade e data para manter o inventário atualizado. | Must |
| HU-07 | Quero registrar a saída de um produto ao realizar uma venda para que o estoque seja descontado automaticamente. | Must |
| HU-08 | Quero cadastrar um novo produto com nome, SKU, categoria e quantidade inicial para começar a controlá-lo. | Must |
| HU-09 | Quero editar os dados de um produto existente (nome, categoria, nível mínimo) sem apagar seu histórico. | Should |
| HU-10 | Quero remover (inativar) um produto descontinuado sem deletar seu histórico de movimentações. | Should |

#### Como Desenvolvedor / Testador

| ID | História | Prioridade |
|---|---|---|
| HU-11 | Quero que a lógica de domínio seja independente do Google Sheets para poder testá-la com mocks. | Must |
| HU-12 | Quero que a interface de repositório seja abstraída para trocar o backend de persistência sem alterar o domínio. | Must |

---

## 2. Definição de Requisitos

### 2.1 Requisitos Funcionais (RF)

#### Gestão de Produtos

| ID | Descrição | História(s) |
|---|---|---|
| RF-01 | O sistema deve permitir cadastrar um produto com os campos: nome (obrigatório), SKU (único, obrigatório), categoria (opcional), quantidade inicial ≥ 0 e nível mínimo ≥ 0. | HU-08 |
| RF-02 | O sistema deve impedir o cadastro de dois produtos com o mesmo SKU. | HU-08 |
| RF-03 | O sistema deve permitir editar nome, categoria e nível mínimo de um produto existente, preservando seu histórico. | HU-09 |
| RF-04 | O sistema deve permitir inativar um produto, impedindo novas movimentações sem deletar o histórico. | HU-10 |
| RF-05 | O sistema deve listar todos os produtos ativos com SKU, nome, categoria, quantidade atual e nível mínimo. | HU-01 |

#### Movimentações de Estoque

| ID | Descrição | História(s) |
|---|---|---|
| RF-06 | O sistema deve registrar uma entrada de estoque informando: SKU do produto, quantidade (inteiro > 0) e data (default = hoje). | HU-06 |
| RF-07 | O sistema deve registrar uma saída de estoque informando: SKU do produto, quantidade (inteiro > 0) e data. | HU-07 |
| RF-08 | O sistema deve rejeitar uma saída cuja quantidade solicitada exceda a quantidade disponível, exibindo mensagem de erro clara. | HU-07 |
| RF-09 | O sistema deve exibir o histórico de movimentações de um produto com data, tipo (entrada/saída) e quantidade. | HU-03 |

#### Alertas e Relatórios

| ID | Descrição | História(s) |
|---|---|---|
| RF-10 | O sistema deve exibir, ao listar produtos, um indicador visual (ex.: `[ALERTA]`) para produtos com quantidade atual ≤ nível mínimo. | HU-02 |
| RF-11 | O sistema deve exibir um relatório de produtos abaixo do nível mínimo em qualquer momento via comando dedicado. | HU-02 |
| RF-12 | O sistema deve permitir filtrar a listagem de produtos por categoria. | HU-04 |

---

### 2.2 Requisitos Não Funcionais (RNF)

| ID | Categoria | Descrição |
|---|---|---|
| RNF-01 | Arquitetura | O sistema deve ser organizado em camadas: domínio, repositório, serviço e interface CLI, com dependências unidirecionais. |
| RNF-02 | Testabilidade | O domínio (`domain/`) e os serviços (`service/`) devem ser 100% testáveis sem conexão com a Google Sheets API, via interface `RepositorioBase` mockada. |
| RNF-03 | Persistência | Toda leitura e escrita de dados deve passar pela Google Sheets API via `gspread`; nenhum dado deve ser armazenado localmente além das credenciais. |
| RNF-04 | Portabilidade | O sistema deve funcionar em qualquer ambiente com Python ≥ 3.10 e as dependências `gspread` e `google-auth` instaladas. |

---

### 2.3 Regras de Negócio (RN)

| ID | Regra | Requisito(s) relacionados |
|---|---|---|
| RN-01 | Uma saída de estoque só é permitida se `quantidade_atual >= quantidade_solicitada`. Caso contrário, o sistema recusa a operação com a mensagem: _"Estoque insuficiente: disponível X, solicitado Y."_ | RF-07, RF-08 |
| RN-02 | O SKU é imutável após o cadastro. Qualquer tentativa de alteração deve ser recusada com mensagem explicativa. | RF-03 |
| RN-03 | Um produto inativo (RF-04) não pode receber novas entradas ou saídas. Qualquer tentativa gera erro: _"Produto [SKU] está inativo."_ | RF-04, RF-06, RF-07 |
| RN-04 | A quantidade de qualquer movimentação (entrada ou saída) deve ser um inteiro positivo (> 0). Valores zero, negativos ou fracionários são recusados. | RF-06, RF-07 |
| RN-05 | O nível mínimo de um produto deve ser ≥ 0. O padrão, se não informado, é 0 (sem alerta). | RF-01, RF-10 |
| RN-06 | O alerta de nível mínimo é disparado quando `quantidade_atual <= nivel_minimo` (operador ≤, não estritamente <). | RF-10, RF-11 |

---

### 2.4 Estrutura de Dados (modelo de domínio)

```
Produto
├── sku: str            (PK, imutável)
├── nome: str
├── categoria: str | None
├── quantidade_atual: int  (≥ 0)
├── nivel_minimo: int      (≥ 0, default 0)
└── ativo: bool            (default True)

Movimentacao
├── id: str             (UUID gerado pelo sistema)
├── produto_sku: str    (FK → Produto.sku)
├── tipo: Literal["entrada", "saida"]
├── quantidade: int     (> 0)
└── data: datetime      (ISO 8601, gerado pelo sistema)
```

---

## 3. Validação de Requisitos

### 3.1 Critérios de Aceitação por História de Usuário

#### HU-01 / RF-05 — Listar produtos ativos

```gherkin
Dado que existem produtos cadastrados e ativos,
Quando o operador executa python main.py listar,
Então o sistema exibe uma tabela com SKU, nome, categoria, quantidade atual
     e nível mínimo de cada produto ativo,
E produtos inativos não aparecem na listagem.
```

#### HU-02 / RF-10, RF-11 — Alerta de nível mínimo

```gherkin
Dado que um produto tem nivel_minimo = 5 e quantidade_atual = 3,
Quando o operador executa python main.py listar,
Então o sistema exibe [ALERTA] ao lado desse produto.

Dado que o operador executa python main.py alertas,
Então o sistema lista apenas os produtos com quantidade_atual <= nivel_minimo.
```

#### HU-06 / RF-06 — Registrar entrada

```gherkin
Dado um produto ativo com SKU "ABC-01" e quantidade atual 10,
Quando o operador executa python main.py entrada ABC-01 5,
Então a quantidade do produto passa a ser 15,
E uma movimentação do tipo "entrada" com quantidade 5 é registrada
  com timestamp automático.
```

#### HU-07 / RF-07, RF-08, RN-01 — Registrar saída (incluindo falha)

```gherkin
Dado um produto ativo com quantidade atual 4,
Quando o operador tenta registrar saída de 6 unidades,
Então o sistema exibe: "Estoque insuficiente: disponível 4, solicitado 6."
E nenhuma movimentação é persistida.
```

#### HU-08 / RF-01, RF-02 — Cadastrar produto

```gherkin
Dado que não existe produto com SKU "XYZ-99",
Quando o operador executa:
  python main.py cadastrar XYZ-99 "Caneta Azul" --categoria Papelaria --qtd 100 --min 20,
Então o produto é persistido com os dados informados e ativo = True.

Dado que já existe produto com SKU "XYZ-99",
Quando o operador tenta cadastrar outro produto com o mesmo SKU,
Então o sistema exibe: "SKU XYZ-99 já cadastrado."
```

#### HU-11, HU-12 / RNF-01, RNF-02 — Isolamento de domínio

```gherkin
Dado que a suite de testes é executada sem credenciais do Google,
Quando se executa python -m unittest discover codigo/tests,
Então todos os testes de domínio e serviço passam sem erros,
  usando o repositório mock em memória.
```

### 3.2 Matriz de Cobertura (Problemas × Requisitos)

| Problema de negócio | Requisitos que cobrem |
|---|---|
| Ruptura de estoque | RF-05, RF-10, RF-11, RN-06 |
| Excesso de estoque | RF-05, RF-12 (HU-04) |
| Erros de inventário | RF-06, RF-07, RF-08, RN-01, RN-04 |
| Falta de rastreabilidade | RF-09, RNF-07 |

---
