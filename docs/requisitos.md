# StockFlow — Requisitos do Sistema

---

## 1. Elicitação de Requisitos

### 1.1 Contexto e Problema

Pequenas e médias empresas gerenciam estoque de forma manual ou semi-manual, gerando quatro classes de problema com impacto direto na operação e na lucratividade:

| Problema | Impacto operacional |
|---|---|
| Ruptura de estoque | Perda de venda; cliente busca concorrente |
| Excesso de estoque | Capital imobilizado; risco de vencimento/obsolescência |
| Erros de inventário | Divergência entre físico e registrado; retrabalho de contagem |
| Falta de rastreabilidade | Sem histórico confiável; impossibilidade de auditar movimentações |

De acordo com a Pesquisa de Inventário do Varejo Brasileiro (ABRAPPE/KPMG, 2024), perdas por ruptura e erros de inventário representam prejuízos significativos para o setor varejista. A ruptura de estoque é apontada como um dos principais fatores de perda de vendas no varejo nacional.

O StockFlow centraliza esse controle com regras de negócio encapsuladas e comportamento verificável via testes automatizados.

**Fontes consultadas:**
- KPMG/ABRAPPE — [Pesquisa de Inventário do Varejo Brasileiro 2024](https://kpmg.com/br/pt/insights/2024/11/pesquisa-abrappe-2024.html)
- Wake Tech — [OMS e ruptura de estoque no varejo](https://wake.tech/blog/oms-ruptura-de-estoque/)
- AGP Pesquisas — [Ruptura de estoque no varejo](https://www.agppesquisas.com.br/noticias/ruptura-de-estoque-no-varejo/)
- Food Forum/KPMG — [Perdas no varejo](https://foodforum.com.br/perdas-varejo-kpmg/)

---

### 1.2 Processo de Elicitação

A elicitação foi conduzida combinando quatro técnicas complementares, conectando cada uma às fontes primárias de conhecimento:

#### Técnica 1 — Análise de Documentos Existentes
**Fonte:** Planilhas reais de controle de estoque utilizadas por pequenos comerciantes e os relatórios setoriais listados na seção 1.1.

**O que revelou:**
- Campos recorrentes nas planilhas: produto, SKU, quantidade entrada, quantidade saída, saldo atual — que mapeiam diretamente para as entidades `Produto` e `Movimentacao` do modelo de domínio.
- A coluna "saldo" é calculada manualmente e sujeita a erro → origem do requisito de controle automático de `quantidade_atual` (RF-06, RF-07).
- Ausência de timestamp nas planilhas → origem do requisito RNF-07 (timestamp gerado pelo sistema).

#### Técnica 2 — Entrevistas com Stakeholders Primários
**Fonte:** Gestores de compras e operadores de pequenas lojas do comércio local.

**Roteiro aplicado (perguntas abertas):**
- "Como você controla o estoque hoje? Me mostra o processo."
- "Quando você percebe que um produto está acabando, o que acontece?"
- "Qual foi o último erro que você cometeu no controle de estoque?"
- "O que te faria confiar mais num sistema do que numa planilha?"

**O que revelou:**
- Gestores monitoram estoque esporadicamente (não em tempo real) → requisito de alerta proativo, não só consulta reativa (RF-10, RF-11, HU-02).
- Operadores registram saídas com atraso ou em lote → validação de data obrigatória mas com default = hoje (RF-06).
- A planilha Google Sheets já é usada como registro oficial em vários negócios → escolha de persistência no Sheets aumenta adoção, não é apenas decisão técnica (RNF-03).

#### Técnica 3 — Observação Direta
**Fonte:** Acompanhamento do fluxo de trabalho de um operador durante recebimento de mercadoria.

**O que revelou:**
- Sob pressão, o operador digita quantidades erradas (negativas, fracionárias) sem perceber → origem da RN-04 (validação estrita de quantidade).
- Produtos descontinuados permanecem na planilha "só para consultar o histórico" → origem do RF-04 (inativação sem deleção).
- Stack traces e mensagens de erro técnicas são ignoradas ou causam abandono do sistema → origem do RNF-05 (erros legíveis por humanos).

#### Técnica 4 — Brainstorming Interno da Equipe
**Fonte:** Sessão estruturada com os três membros do projeto.

**O que revelou:**
- Necessidade de domínio testável sem API real → RNF-01, RNF-02 (arquitetura em camadas com repositório abstraído).
- Risco de quota da Sheets API em operações em lote → RNF-06 (tratamento de falhas de conectividade).
- Cobertura de testes deve ser mensurável para fins acadêmicos → RNF-08.

---

### 1.3 Stakeholders — Perfis Detalhados

#### Stakeholder 1 — Gestor de Compras *(primário)*

**Quem é:** Responsável por decidir quando e quanto comprar. Em pequenas empresas, frequentemente acumula a função de dono ou gerente geral. Não tem formação técnica em TI.

**Contexto de uso:** Acessa o sistema algumas vezes por semana, geralmente pela manhã antes de abrir a loja, para verificar o que está baixo e planejar pedidos.

**Necessidades operacionais:**
- Visualizar o estado atual do estoque de forma rápida e legível
- Identificar imediatamente quais produtos estão abaixo do mínimo
- Consultar histórico de um produto para estimar demanda futura
- Filtrar produtos por categoria para planejar compras por seção

**Restrições que originam requisitos:**

| Restrição | Requisito gerado |
|---|---|
| Não instala dependências; setup deve ser mínimo | RNF-04 (Python ≥ 3.10 + 2 pacotes) |
| Confia na planilha como "verdade oficial" do negócio | RNF-03 (persistência exclusiva no Sheets) |
| Não tolera inconsistência de dados — volta para a planilha | RN-01, RN-04 (validações rígidas) |

---

#### Stakeholder 2 — Operador / Lojista *(primário)*

**Quem é:** Funcionário responsável pela operação diária — recebe mercadoria, registra vendas, faz contagens. Pode ser o próprio dono em negócios menores.

**Contexto de uso:** Usa o sistema várias vezes ao dia, em momentos de alta pressão (recebendo entrega, atendendo cliente). Velocidade é prioridade.

**Necessidades operacionais:**
- Registrar entradas de lote ao receber mercadoria
- Registrar saídas ao realizar vendas ou baixas
- Cadastrar produtos novos ocasionalmente
- Editar dados de produtos sem perder histórico

**Restrições que originam requisitos:**

| Restrição | Requisito gerado |
|---|---|
| Opera sob pressão; cada passo extra é erro potencial | RNF-05 (mensagens claras, sem stack trace) |
| Pode digitar valores inválidos inadvertidamente | RN-04 (quantidade inteiro positivo), RF-08 (rejeição de saída inválida) |
| Não audita o histórico — apenas produz os dados | RF-09 existe para o Gestor, não para o Operador |

---

### 1.4 Histórias de Usuário

As histórias seguem o modelo padrão: **Como** [papel], **quero** [ação], **para que** [valor de negócio]. A prioridade segue o framework MoSCoW.

#### Como Gestor de Compras

| ID | Como… | Quero… | Para que… | Prior. |
|---|---|---|---|---|
| HU-01 | Gestor de compras | visualizar a quantidade atual de cada produto | eu saiba o que precisa ser reposto antes de faltar | Must |
| HU-02 | Gestor de compras | receber um alerta quando um produto atingir o nível mínimo | eu faça o pedido antes de ter ruptura de estoque | Must |
| HU-03 | Gestor de compras | consultar o histórico de movimentações de um produto específico | eu identifique padrões de consumo e planeje melhor as compras | Should |
| HU-04 | Gestor de compras | filtrar produtos por categoria | eu planeje compras por seção sem ver itens irrelevantes | Could |
| HU-05 | Gestor de compras | exportar um relatório de estoque atual | eu compartilhe com fornecedores sem precisar abrir a planilha | Could |

#### Como Operador / Lojista

| ID | Como… | Quero… | Para que… | Prior. |
|---|---|---|---|---|
| HU-06 | Operador | registrar a entrada de um lote de produtos informando quantidade e data | o inventário reflita o estoque físico após cada recebimento | Must |
| HU-07 | Operador | registrar a saída de um produto ao realizar uma venda | o estoque seja descontado automaticamente sem cálculo manual | Must |
| HU-08 | Operador | cadastrar um novo produto com nome, SKU, categoria e quantidade inicial | eu passe a controlá-lo no sistema a partir do momento do cadastro | Must |
| HU-09 | Operador | editar os dados de um produto existente (nome, categoria, nível mínimo) | eu corrija informações sem perder o histórico de movimentações | Should |
| HU-10 | Operador | inativar um produto descontinuado | ele não apareça nas listagens ativas mas seu histórico seja preservado | Should |

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
| RNF-05 | Usabilidade CLI | Cada operação deve ser executável com um único comando. O sistema deve exibir mensagens de erro legíveis por humanos, não stack traces. |
| RNF-06 | Confiabilidade | Falhas de conectividade com a API (timeout, quota exceeded) devem ser capturadas e exibidas como erro amigável sem encerrar o processo com código de saída não-zero inesperado. |
| RNF-07 | Rastreabilidade | Toda movimentação registrada deve conter timestamp ISO 8601 gerado pelo sistema, não pelo usuário. |
| RNF-08 | Manutenibilidade | A cobertura de testes automatizados das classes de domínio e serviço deve ser ≥ 80% (medida por `coverage.py`). |

---

### 2.3 Regras de Negócio (RN)

| ID | Regra | Requisito(s) relacionados |
|---|---|---|
| RN-01 | Uma saída de estoque só é permitida se `quantidade_atual >= quantidade_solicitada`. Caso contrário, o sistema recusa a operação com a mensagem: _"Estoque insuficiente: disponível X, solicitado Y."_ | RF-07, RF-08 |
| RN-02 | O SKU é imutável após o cadastro. Qualquer tentativa de alteração deve ser recusada com mensagem explicativa. | RF-03 |
| RN-03 | Um produto inativo não pode receber novas entradas ou saídas. Qualquer tentativa gera erro: _"Produto [SKU] está inativo."_ | RF-04, RF-06, RF-07 |
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

### 3.1 Engenharia de Requisitos vs. Desenvolvimento dos Requisitos

É importante distinguir duas atividades que compõem este documento:

| Atividade | O que é | Produto gerado |
|---|---|---|
| **Engenharia de Requisitos** | Processo de descobrir, analisar e especificar o que o sistema deve fazer, com base nas necessidades dos stakeholders. Foco: *problema*. | Seções 1 e 2 deste documento (elicitação, stakeholders, HUs, RFs, RNFs, RNs) |
| **Desenvolvimento dos Requisitos** | Processo de refinar, validar e manter os requisitos ao longo do ciclo de vida do projeto. Foco: *qualidade e rastreabilidade*. | Seção 3 deste documento (critérios de aceitação, rastreabilidade, matriz de cobertura) |

**Por que essa distinção importa no StockFlow:**
- A engenharia de requisitos conecta cada decisão a uma necessidade real de um stakeholder (ver perfis na seção 1.3 e origem dos requisitos na seção 1.2).
- O desenvolvimento dos requisitos garante que os requisitos sejam *verificáveis* — cada HU tem critério de aceitação executável, e cada RF tem um caso de teste mapeado.
- Sem essa separação, é comum gerar listas de funcionalidades sem âncora no problema real, o que torna os testes arbitrários.

---

### 3.2 Critérios de Aceitação por História de Usuário

Cada critério segue o padrão **Dado / Quando / Então** (BDD/Gherkin) e constitui a definição de "pronto" (*definition of done*) para a HU correspondente.

---

#### HU-01 — Visualizar quantidade atual

```gherkin
Dado que existem produtos cadastrados e ativos,
Quando o operador executa: python main.py listar
Então o sistema exibe uma tabela com SKU, nome, categoria,
     quantidade atual e nível mínimo de cada produto ativo,
E produtos inativos não aparecem na listagem.
```

**Validação:** RF-05 coberto. Verificar ausência de produtos com `ativo = False`.

---

#### HU-02 — Alerta de nível mínimo

```gherkin
Dado que um produto tem nivel_minimo = 5 e quantidade_atual = 3,
Quando o operador executa: python main.py listar
Então o sistema exibe [ALERTA] ao lado desse produto.

Dado que o operador executa: python main.py alertas
Então o sistema lista apenas os produtos com quantidade_atual <= nivel_minimo.
```

**Validação:** RF-10, RF-11 e RN-06 cobertos. Caso de borda: testar `quantidade_atual == nivel_minimo` (deve disparar alerta pelo operador ≤).

---

#### HU-03 — Consultar histórico de movimentações

```gherkin
Dado que o produto "ABC-01" possui 3 movimentações registradas,
Quando o operador executa: python main.py historico ABC-01
Então o sistema exibe as 3 movimentações com data, tipo e quantidade,
E as movimentações estão ordenadas por data decrescente.
```

**Validação:** RF-09 coberto. Verificar presença de timestamp em todas as linhas.

---

#### HU-04 — Filtrar por categoria

```gherkin
Dado que existem produtos das categorias "Papelaria" e "Limpeza",
Quando o operador executa: python main.py listar --categoria Papelaria
Então o sistema exibe apenas os produtos da categoria "Papelaria",
E nenhum produto de "Limpeza" aparece no resultado.
```

**Validação:** RF-12 coberto. Caso de borda: categoria inexistente deve retornar lista vazia com mensagem informativa.

---

#### HU-06 — Registrar entrada de estoque

```gherkin
Dado um produto ativo com SKU "ABC-01" e quantidade atual 10,
Quando o operador executa: python main.py entrada ABC-01 5
Então a quantidade do produto passa a ser 15,
E uma movimentação do tipo "entrada" com quantidade 5 é registrada
  com timestamp automático (não informado pelo usuário).
```

**Validação:** RF-06, RN-04 cobertos. Caso de borda: `python main.py entrada ABC-01 0` deve ser rejeitado (RN-04).

---

#### HU-07 — Registrar saída de estoque

```gherkin
Dado um produto ativo com SKU "ABC-01" e quantidade atual 10,
Quando o operador executa: python main.py saida ABC-01 4
Então a quantidade do produto passa a ser 6,
E uma movimentação do tipo "saida" com quantidade 4 é registrada.

Dado um produto ativo com quantidade atual 4,
Quando o operador tenta registrar saída de 6 unidades,
Então o sistema exibe: "Estoque insuficiente: disponível 4, solicitado 6.",
E nenhuma movimentação é persistida.
```

**Validação:** RF-07, RF-08 e RN-01 cobertos. Verificar atomicidade: em caso de rejeição, `quantidade_atual` não deve ser alterada.

---

#### HU-08 — Cadastrar novo produto

```gherkin
Dado que não existe produto com SKU "XYZ-99",
Quando o operador executa:
  python main.py cadastrar XYZ-99 "Caneta Azul" --categoria Papelaria --qtd 100 --min 20
Então o produto é persistido com ativo = True e os dados informados.

Dado que já existe produto com SKU "XYZ-99",
Quando o operador tenta cadastrar outro produto com o mesmo SKU,
Então o sistema exibe: "SKU XYZ-99 já cadastrado.",
E nenhum produto é criado ou sobrescrito.
```

**Validação:** RF-01, RF-02 cobertos. Caso de borda: `--qtd -1` deve ser rejeitado (quantidade inicial ≥ 0).

---

#### HU-09 — Editar dados de produto

```gherkin
Dado que existe o produto "XYZ-99" com 5 movimentações registradas,
Quando o operador executa: python main.py editar XYZ-99 --nome "Caneta Azul BIC"
Então o nome do produto é atualizado,
E as 5 movimentações anteriores permanecem inalteradas,
E o SKU "XYZ-99" não pode ser alterado.
```

**Validação:** RF-03, RN-02 cobertos. Verificar que tentativa de editar o SKU retorna erro explicativo.

---

#### HU-10 — Inativar produto

```gherkin
Dado que existe o produto ativo "XYZ-99" com histórico de movimentações,
Quando o operador executa: python main.py inativar XYZ-99
Então o produto não aparece mais na listagem padrão (python main.py listar),
E suas movimentações históricas permanecem acessíveis via python main.py historico XYZ-99,
E tentativa de nova entrada ou saída retorna: "Produto XYZ-99 está inativo."
```

**Validação:** RF-04, RN-03 cobertos.

---

#### HU-11 e HU-12 — Isolamento de domínio e abstração do repositório

```gherkin
Dado que a suite de testes é executada sem credenciais do Google configuradas,
Quando se executa: python -m unittest discover codigo/tests
Então todos os testes de domínio e serviço passam sem erros,
  usando o repositório mock em memória (RepositorioEmMemoria),
E nenhum teste faz chamada real à Google Sheets API.
```

**Validação:** RNF-01, RNF-02 cobertos. Verificar que `RepositorioBase` é uma classe abstrata com interface definida e que `RepositorioSheets` e `RepositorioEmMemoria` a implementam.

---

### 3.3 Rastreabilidade RF → Teste

| Requisito | Caso de teste sugerido | Tipo |
|---|---|---|
| RF-01 | `test_cadastrar_produto_valido` | Unitário |
| RF-02 | `test_cadastrar_produto_sku_duplicado` | Unitário |
| RF-03 | `test_editar_produto_preserva_historico` | Unitário |
| RF-04 | `test_inativar_produto_bloqueia_movimentacao` | Unitário |
| RF-05 | `test_listar_exclui_inativos` | Unitário |
| RF-06 | `test_entrada_aumenta_quantidade` | Unitário |
| RF-07 | `test_saida_diminui_quantidade` | Unitário |
| RF-08 | `test_saida_estoque_insuficiente_rejeitada` | Unitário |
| RF-09 | `test_historico_ordenado_por_data` | Unitário |
| RF-10 | `test_alerta_nivel_minimo_exibido` | Unitário |
| RF-11 | `test_comando_alertas_lista_apenas_criticos` | Unitário |
| RF-12 | `test_filtro_por_categoria` | Unitário |
| RN-02 | `test_sku_imutavel` | Unitário |
| RN-04 | `test_quantidade_zero_rejeitada` | Unitário |
| RN-06 | `test_alerta_quando_igual_ao_minimo` | Unitário (borda) |
| RNF-02 | `test_dominio_sem_api_real` | Integração (mock) |
| RNF-03 | `test_persistencia_via_sheets` | Integração (API real) |

---

### 3.4 Matriz de Cobertura (Problemas × Requisitos)

| Problema de negócio | Requisitos que cobrem |
|---|---|
| Ruptura de estoque | RF-05, RF-10, RF-11, RN-06 |
| Excesso de estoque | RF-05, RF-12 (HU-04) |
| Erros de inventário | RF-06, RF-07, RF-08, RN-01, RN-04 |
| Falta de rastreabilidade | RF-09, RNF-07 |

---

### 3.5 Escopo Excluído (Out of Scope)

Os itens abaixo foram identificados durante a elicitação mas **não fazem parte do escopo** deste projeto, por decisão da equipe, para manter foco na qualidade de engenharia:

- Interface gráfica (GUI ou web)
- Autenticação de usuários / controle de acesso por perfil
- Múltiplos depósitos ou localizações físicas
- Integração com sistemas de PDV (ponto de venda)
- Relatórios gráficos ou exportação para PDF
- Gestão de fornecedores

---