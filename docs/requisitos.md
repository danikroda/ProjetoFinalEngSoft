# StockFlow — Requisitos do Sistema

---

## 1. Elicitação de Requisitos

### 1.1 Contexto e Problema

Pequenas e médias empresas gerenciam estoque de forma manual ou semi-manual, gerando quatro classes de problema com impacto direto na operação e na lucratividade. A tabela abaixo já conecta cada problema à técnica de elicitação que o revelou (detalhadas na seção 1.2):

| Problema | Impacto operacional | Revelado por | Fonte |
|---|---|---|---|
| Ruptura de estoque | Perda de venda; cliente busca concorrente | Entrevistas (Técnica 2) + pesquisa setorial | Stakeholders; KPMG/ABRAPPE 2024 |
| Excesso de estoque | Capital imobilizado; risco de vencimento/obsolescência | Citado pelos stakeholders, mas sem técnica dedicada de aprofundamento | Entrevistas (cobertura apenas indireta — ver seção 3.4) |
| Erros de inventário | Divergência entre físico e registrado; retrabalho de contagem | Análise de Documentos (Técnica 1) + Observação Direta (Técnica 3) | Planilhas reais; observação do operador |
| Falta de rastreabilidade | Sem histórico confiável; impossibilidade de auditar movimentações | Análise de Documentos (Técnica 1) | Planilhas reais (ausência de timestamp) |

De acordo com a Pesquisa de Inventário do Varejo Brasileiro (ABRAPPE/KPMG, 2024), perdas por ruptura e erros de inventário representam prejuízos significativos para o setor varejista. A ruptura de estoque é apontada como um dos principais fatores de perda de vendas no varejo nacional.

O StockFlow centraliza esse controle com regras de negócio encapsuladas e comportamento verificável via testes automatizados.

**Fontes consultadas:**
- KPMG/ABRAPPE — [Pesquisa de Inventário do Varejo Brasileiro 2024](https://kpmg.com/br/pt/insights/2024/11/pesquisa-abrappe-2024.html)
- Wake Tech — [OMS e ruptura de estoque no varejo](https://wake.tech/blog/oms-ruptura-de-estoque/)
- AGP Pesquisas — [Ruptura de estoque no varejo](https://www.agppesquisas.com.br/noticias/ruptura-de-estoque-no-varejo/)
- Food Forum/KPMG — [Perdas no varejo](https://foodforum.com.br/perdas-varejo-kpmg/)

---

### 1.2 Processo de Elicitação

A elicitação foi conduzida combinando quatro técnicas complementares. Cada uma é apresentada já conectada à sua fonte primária e aos requisitos que originou.

#### Técnica 1 — Análise de Documentos Existentes
**Fonte:** Planilhas reais de controle de estoque utilizadas por pequenos comerciantes e os relatórios setoriais listados na seção 1.1.

**O que revelou:**
- Campos recorrentes nas planilhas: produto, SKU, quantidade entrada, quantidade saída, saldo atual — que mapeiam diretamente para as entidades `Produto` e `Movimentacao` do modelo de domínio.
- A coluna "saldo" é calculada manualmente e sujeita a erro → origem do requisito de controle automático de `quantidade_atual` (**RF-05, RF-06**).
- Ausência de timestamp nas planilhas → origem do requisito **RNF-07** (timestamp gerado pelo sistema).

#### Técnica 2 — Entrevistas com Stakeholders Primários
**Fonte:** Gestores de compras e operadores de pequenas lojas do comércio local.

**Roteiro aplicado (perguntas abertas):**
- "Como você controla o estoque hoje? Me mostra o processo."
- "Quando você percebe que um produto está acabando, o que acontece?"
- "Qual foi o último erro que você cometeu no controle de estoque?"
- "O que te faria confiar mais num sistema do que numa planilha?"

**O que revelou:**
- Gestores monitoram estoque esporadicamente (não em tempo real) → requisito de alerta proativo, não só consulta reativa (**RF-08, HU-02**).
- Operadores registram saídas com atraso ou em lote → validação de data obrigatória mas com default = hoje (**RF-05**).
- A planilha Google Sheets já é usada como registro oficial em vários negócios → escolha de persistência no Sheets aumenta adoção, não é apenas decisão técnica (**RNF-03**).

#### Técnica 3 — Observação Direta
**Fonte:** Acompanhamento do fluxo de trabalho de um operador durante recebimento de mercadoria.

**O que revelou:**
- Sob pressão, o operador digita quantidades erradas (negativas, fracionárias) sem perceber → origem da **RN-04** (validação estrita de quantidade).
- Produtos descontinuados permanecem na planilha "só para consultar o histórico" → origem do **RF-03** (alternância de status ativo/inativo, sem deleção).
- Stack traces e mensagens de erro técnicas são ignoradas ou causam abandono do sistema → origem da **RNF-05** (erros legíveis por humanos).

#### Técnica 4 — Brainstorming Interno da Equipe
**Fonte:** Sessão estruturada com os três membros do projeto.

**O que revelou:**
- Necessidade de domínio testável sem API real → **RNF-01, RNF-02** (arquitetura em camadas com repositório abstraído).
- Risco de quota da Sheets API em operações em lote → **RNF-06** (tratamento de falhas de conectividade).
- Cobertura de testes deve ser mensurável para fins acadêmicos → **RNF-08**.

#### Síntese: Técnica → Fonte → Requisitos Originados

| Técnica | Fonte primária | Requisitos originados |
|---|---|---|
| 1. Análise de Documentos | Planilhas de comerciantes + relatórios setoriais | RF-05, RF-06, RNF-07 |
| 2. Entrevistas | Gestores e operadores do comércio local | RF-08, RF-05 (default de data), RNF-03 |
| 3. Observação Direta | Fluxo de recebimento de mercadoria | RN-04, RF-03, RNF-05 |
| 4. Brainstorming Interno | Equipe do projeto | RNF-01, RNF-02, RNF-06, RNF-08 |

---

### 1.3 Stakeholders — Escopo e Perfis Detalhados

Esta seção delimita explicitamente quem são os atores considerados no projeto e quem está fora desse escopo.

**Stakeholders primários (usuários diretos do sistema):**
- Gestor de Compras
- Operador / Lojista

**Stakeholder secundário (interno ao projeto, não opera o sistema no dia a dia):**
- Equipe de Desenvolvimento — depende da testabilidade e manutenibilidade do sistema, mas não é um usuário final do CLI.

**Explicitamente fora do escopo de stakeholders:**
- **Clientes finais da loja** — não interagem com o StockFlow; apenas geram saídas de estoque indiretamente, por meio do Operador.
- **Fornecedores** — gestão de fornecedores está fora do escopo do produto (seção 3.5).
- **Perfis administrativos diferenciados** (ex.: super-admin) — o sistema não possui autenticação ou controle de acesso por perfil; Gestor e Operador têm o mesmo nível de acesso ao CLI.

---

#### Stakeholder 1 — Gestor de Compras *(primário)*

**Quem é:** Responsável por decidir quando e quanto comprar. Em pequenas empresas, frequentemente acumula a função de dono ou gerente geral. Não tem formação técnica em TI.

**Contexto de uso:** Acessa o sistema algumas vezes por semana, geralmente pela manhã antes de abrir a loja, para verificar o que está baixo e planejar pedidos.

**Necessidades operacionais:**
- Visualizar o estado atual do estoque de forma rápida e legível
- Identificar imediatamente quais produtos estão abaixo do mínimo

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
- Corrigir a quantidade em estoque ou reativar/inativar um produto já cadastrado

**Restrições que originam requisitos:**

| Restrição | Requisito gerado |
|---|---|
| Opera sob pressão; cada passo extra é erro potencial | RNF-05 (mensagens claras, sem stack trace) |
| Pode digitar valores inválidos inadvertidamente | RN-04 (quantidade inteiro positivo), RF-07 (rejeição de saída inválida) |
| Não audita o histórico — apenas produz os dados | — |

---

#### Stakeholder 3 — Equipe de Desenvolvimento *(secundário / interno)*

**Quem é:** Os três membros do projeto, responsáveis por implementar, testar e evoluir o sistema. Não usa o sistema na operação diária da loja, mas depende diretamente de sua testabilidade.

**Contexto de uso:** Durante o desenvolvimento, refatorações e sprints de teste.

**Necessidades operacionais:**
- Executar a suíte de testes sem depender de credenciais reais da API do Google
- Confiar que mudanças no domínio não quebram a camada de persistência sem perceber
- Trocar a implementação concreta do repositório sem alterar regras de negócio

**Restrições que originam requisitos:**

| Restrição | Requisito gerado |
|---|---|
| Precisa testar sem custo ou risco de quota da API real | RNF-02, RNF-06 |
| Precisa isolar regra de negócio de detalhes de persistência | RNF-01 |
| Cobertura de teste precisa ser mensurável para fins acadêmicos | RNF-08 |

---

### 1.4 Histórias de Usuário

As histórias seguem o modelo padrão: **Como** [papel], **quero** [ação], **para que** [valor de negócio], com prioridade no framework MoSCoW.

#### Como Gestor de Compras

| ID | Como… | Quero… | Para que… | Prior. |
|---|---|---|---|---|
| HU-01 | Gestor de compras | visualizar a quantidade atual de cada produto | eu saiba o que precisa ser reposto antes de faltar | Must |
| HU-02 | Gestor de compras | receber um alerta quando um produto atingir o nível mínimo | eu faça o pedido antes de ter ruptura de estoque | Must |
| HU-03 | Gestor de compras | exportar um relatório de estoque atual | eu compartilhe com fornecedores sem precisar abrir a planilha | Could |

#### Como Operador / Lojista

| ID | Como… | Quero… | Para que… | Prior. |
|---|---|---|---|---|
| HU-04 | Operador | registrar a entrada de um lote de produtos informando quantidade e data | o inventário reflita o estoque físico após cada recebimento | Must |
| HU-05 | Operador | registrar a saída de um produto ao realizar uma venda | o estoque seja descontado automaticamente sem cálculo manual | Must |
| HU-06 | Operador | cadastrar um novo produto com nome, SKU, categoria e quantidade inicial | eu passe a controlá-lo no sistema a partir do momento do cadastro | Must |
| HU-07 | Operador | corrigir a quantidade em estoque de um produto | eu ajuste divergências de contagem sem precisar tratar isso como uma venda ou recebimento | Should |
| HU-08 | Operador | ativar ou inativar um produto (alternando seu status) | eu controle quais produtos aparecem nas listagens ativas sem perder o histórico | Should |

#### Como Equipe de Desenvolvimento

| ID | Como… | Quero… | Para que… | Prior. |
|---|---|---|---|---|
| HU-09 | Equipe de desenvolvimento | executar toda a suíte de testes sem credenciais reais do Google configuradas | eu valide regras de negócio rapidamente, sem custo ou risco de quota da API | Must |
| HU-10 | Equipe de desenvolvimento | trocar a implementação concreta do repositório (Sheets ↔ mock/memória) sem alterar o domínio | o sistema permaneça testável e flexível a mudanças futuras de persistência | Should |

---

## 2. Definição de Requisitos

### 2.1 Requisitos Funcionais (RF)

#### Gestão de Produtos

| ID | Descrição | História(s) |
|---|---|---|
| RF-01 | O sistema deve permitir cadastrar um produto com os campos: nome (obrigatório), SKU (único, obrigatório), categoria (opcional), quantidade inicial ≥ 0 e nível mínimo ≥ 0. | HU-06 |
| RF-02 | O sistema deve impedir o cadastro de dois produtos com o mesmo SKU. | HU-06 |
| RF-03 | O sistema deve permitir alternar o status de um produto entre ativo e inativo; um produto inativo não pode receber novas movimentações, mas seu histórico é preservado. | HU-08 |
| RF-04 | O sistema deve listar todos os produtos ativos com SKU, nome, categoria, quantidade atual e nível mínimo. | HU-01 |

#### Movimentações de Estoque

| ID | Descrição | História(s) |
|---|---|---|
| RF-05 | O sistema deve registrar uma entrada de estoque informando: SKU do produto, quantidade (inteiro > 0) e data (default = hoje). | HU-04, HU-07 |
| RF-06 | O sistema deve registrar uma saída de estoque informando: SKU do produto, quantidade (inteiro > 0) e data. | HU-05, HU-07 |
| RF-07 | O sistema deve rejeitar uma saída cuja quantidade solicitada exceda a quantidade disponível, exibindo mensagem de erro clara. | HU-05 |

#### Alertas e Relatórios

| ID | Descrição | História(s) |
|---|---|---|
| RF-08 | O sistema deve exibir, ao listar produtos, um indicador visual (ex.: `[ALERTA]`) para produtos com quantidade atual ≤ nível mínimo. | HU-02 |

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
| RN-01 | Uma saída de estoque só é permitida se `quantidade_atual >= quantidade_solicitada`. Caso contrário, o sistema recusa a operação com a mensagem: _"Estoque insuficiente: disponível X, solicitado Y."_ | RF-06, RF-07 |
| RN-02 | O SKU é imutável após o cadastro. Qualquer tentativa de alteração deve ser recusada com mensagem explicativa. | — |
| RN-03 | Um produto inativo não pode receber novas entradas ou saídas. Qualquer tentativa gera erro: _"Produto [SKU] está inativo."_ | RF-03, RF-05, RF-06 |
| RN-04 | A quantidade de qualquer movimentação (entrada ou saída) deve ser um inteiro positivo (> 0). Valores zero, negativos ou fracionários são recusados. | RF-05, RF-06 |
| RN-05 | O nível mínimo de um produto deve ser ≥ 0. O padrão, se não informado, é 0 (sem alerta). | RF-01, RF-08 |
| RN-06 | O alerta de nível mínimo é disparado quando `quantidade_atual <= nivel_minimo` (operador ≤, não estritamente <). | RF-08 |

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
| **Engenharia de Requisitos** | Processo de descobrir, analisar e especificar o que o sistema deve fazer, com base nas necessidades dos stakeholders. Foco: o problema. | Seções 1 e 2 (elicitação, stakeholders, HUs, RFs, RNFs, RNs) |
| **Desenvolvimento dos Requisitos** | Processo de refinar, validar e manter os requisitos ao longo do ciclo de vida do projeto. Foco: qualidade e rastreabilidade. | Seção 3 (critérios de aceitação, rastreabilidade, matriz de cobertura) |

**Por que essa distinção importa no StockFlow:**

- A engenharia de requisitos conecta cada decisão a uma necessidade real de um stakeholder (perfis na seção 1.3; origem na seção 1.2).
- O desenvolvimento dos requisitos garante que os requisitos sejam **verificáveis** — cada HU tem critério de aceitação executável (seção 3.2), e cada RF tem um caso de teste mapeado (seção 3.3), com status real de implementação.
- Sem essa separação, é comum gerar listas de funcionalidades sem âncora no problema real, o que torna os testes arbitrários.

---

### 3.2 Critérios de Aceitação por História de Usuário

Cada critério segue o padrão **Dado / Quando / Então** (BDD/Gherkin) e constitui a definição de "pronto" (*definition of done*) para a HU correspondente.

---

#### HU-01 — Visualizar quantidade atual

```
Dado que existem produtos cadastrados e ativos,
Quando o operador executa: python main.py listar
Então o sistema exibe uma tabela com SKU, nome, categoria,
     quantidade atual e nível mínimo de cada produto ativo,
E produtos inativos não aparecem na listagem.
```
**Validação:** RF-04 coberto. Verificar ausência de produtos com `ativo = False`. **Status: implementado e testado** (ver seção 4).

---

#### HU-02 — Alerta de nível mínimo

```
Dado que um produto tem nivel_minimo = 5 e quantidade_atual = 3,
Quando o operador executa: python main.py listar
Então o sistema exibe [ALERTA] ao lado desse produto.
```
**Validação:** RF-08 e RN-06 cobertos. Caso de borda: testar `quantidade_atual == nivel_minimo` (deve disparar alerta pelo operador ≤). **Status: sugerido.**

---

#### HU-03 — Exportar relatório de estoque

```
Dado que existem produtos cadastrados no sistema,
Quando o gestor executa: python main.py exportar --formato csv
Então o sistema gera um arquivo com SKU, nome, categoria,
     quantidade atual e nível mínimo de todos os produtos ativos,
E o arquivo pode ser compartilhado sem necessidade de abrir a planilha original.
```
**Validação:** Sem RF dedicado nesta versão — prioridade **Could**, não priorizada para o MVP. Critério definido apenas como referência para ciclos futuros.

---

#### HU-04 — Registrar entrada de estoque

```
Dado um produto ativo com SKU "ABC-01" e quantidade atual 10,
Quando o operador executa: python main.py entrada ABC-01 5
Então a quantidade do produto passa a ser 15,
E uma movimentação do tipo "entrada" com quantidade 5 é registrada
  com timestamp automático (não informado pelo usuário).
```
**Validação:** RF-05, RN-04 cobertos. Caso de borda: `python main.py entrada ABC-01 0` deve ser rejeitado (RN-04). **Status: sugerido.**

---

#### HU-05 — Registrar saída de estoque

```
Dado um produto ativo com SKU "ABC-01" e quantidade atual 10,
Quando o operador executa: python main.py saida ABC-01 4
Então a quantidade do produto passa a ser 6,
E uma movimentação do tipo "saida" com quantidade 4 é registrada.

Dado um produto ativo com quantidade atual 4,
Quando o operador tenta registrar saída de 6 unidades,
Então o sistema exibe: "Estoque insuficiente: disponível 4, solicitado 6.",
E nenhuma movimentação é persistida.
```
**Validação:** RF-06, RF-07 e RN-01 cobertos. Verificar atomicidade: em caso de rejeição, `quantidade_atual` não deve ser alterada. **Status: implementado e testado** (ver seção 4 — sucesso, falha e borda cobertos em `Produto.atualizar_estoque` e `EstoqueController.realizar_movimentacao`).

---

#### HU-06 — Cadastrar novo produto

```
Dado que não existe produto com SKU "XYZ-99",
Quando o operador executa:
  python main.py cadastrar XYZ-99 "Caneta Azul" --categoria Papelaria --qtd 100 --min 20
Então o produto é persistido com ativo = True e os dados informados.

Dado que já existe produto com SKU "XYZ-99",
Quando o operador tenta cadastrar outro produto com o mesmo SKU,
Então o sistema exibe: "SKU XYZ-99 já cadastrado.",
E nenhum produto é criado ou sobrescrito.
```
**Validação:** RF-01, RF-02 cobertos. Caso de borda: `--qtd -1` deve ser rejeitado (quantidade inicial ≥ 0). **Status: sugerido.**

---

#### HU-07 — Corrigir quantidade em estoque

```
Dado um produto ativo com SKU "ABC-01" e quantidade atual 8,
  mas a contagem física real é 10 (divergência identificada na conferência),
Quando o operador registra a correção da quantidade para 10,
Então a quantidade do produto passa a refletir o valor correto,
E a correção é registrada com timestamp automático,
  seguindo a mesma trilha de auditoria das demais movimentações (RNF-07).
```
**Validação:** Não exige uma nova funcionalidade isolada — é coberto pela mesma capacidade de **RF-05/RF-06** (entrada/saída), usada aqui com a intenção de correção de contagem em vez de venda/recebimento. Caso de borda: corrigir para um valor menor que o atual deve respeitar **RN-01** (a "saída" implícita não pode deixar a quantidade negativa). **Status: coberto indiretamente pela mesma implementação de RF-05/RF-06.**

---

#### HU-08 — Ativar ou inativar produto

```
Dado que existe o produto ativo "XYZ-99" com histórico de movimentações,
Quando o operador executa o comando de alternância de status para "XYZ-99",
Então o produto passa a constar como inativo,
E não aparece mais na listagem padrão (python main.py listar),
E tentativa de nova entrada ou saída retorna: "Produto XYZ-99 está inativo."

Dado que existe o produto inativo "XYZ-99",
Quando o operador executa novamente o comando de alternância de status,
Então o produto volta a constar como ativo,
E volta a aparecer na listagem padrão e a aceitar novas movimentações.
```
**Validação:** RF-03 e RN-03 cobertos. Caso de borda: alternar o status duas vezes em sequência deve retornar ao estado original (idempotência do toggle). **Status: sugerido.**

---

#### HU-09 — Executar testes sem credenciais reais

```
Dado que a suíte de testes é executada sem credenciais do Google configuradas,
Quando se executa: python -m unittest testes.py
Então todos os testes do domínio e do controlador passam sem erros,
  usando um repositório mockado (unittest.mock.MagicMock),
E nenhuma chamada real à Google Sheets API é realizada.
```
**Validação:** RNF-01, RNF-02 cobertos. **Status: implementado** nesta sprint via `unittest.mock.patch("controlador.GoogleSheetsRepository")` (ver seção 4).

---

#### HU-10 — Trocar implementação de repositório sem alterar o domínio

```
Dado que o sistema depende de uma camada de repositório,
Quando a implementação concreta de persistência é substituída
  (ex.: Google Sheets ↔ repositório mockado em testes),
Então as regras de negócio do domínio (Produto, EstoqueController)
  continuam funcionando sem qualquer alteração de código,
E apenas a camada de repositório é trocada.
```
**Validação:** RNF-01, RNF-02 cobertos. **Status: parcialmente coberto** — a substituição já é viável e exercitada nos testes via mock, mas uma interface formal `RepositorioBase` (classe abstrata) ainda não existe no código atual; **lacuna registrada na seção 4.5.**

---

### 3.3 Rastreabilidade RF → Teste

| Requisito | Caso de teste sugerido | Tipo | Status |
|---|---|---|---|
| RF-01 | `test_cadastrar_produto_valido` | Unitário | Sugerido |
| RF-02 | `test_cadastrar_produto_sku_duplicado` | Unitário | Sugerido |
| RF-03 | `test_alternar_status_ativo_inativo` | Unitário | Sugerido |
| RF-04 | `TestRF05ListarProdutosAtivos.*` (4 testes) | Unitário | **Implementado** (sucesso, falha e borda) |
| RF-05 | `test_entrada_aumenta_quantidade` | Unitário | Sugerido |
| RF-06 | `test_saida_diminui_quantidade` | Unitário | Sugerido |
| RF-07 | `TestRF08SaidaComEstoqueInsuficiente.*` (5 testes) | Unitário | **Implementado** (sucesso, falha e borda no domínio; falha também na integração com o controlador) |
| RF-08 | `test_alerta_nivel_minimo_exibido` | Unitário | Sugerido |
| RN-02 | `test_sku_imutavel` | Unitário | Sugerido |
| RN-04 | `test_quantidade_zero_rejeitada` | Unitário | Sugerido |
| RN-06 | `test_alerta_quando_igual_ao_minimo` | Unitário (borda) | Sugerido |
| RNF-01 | `test_dependencia_de_repositorio_injetada` | Arquitetural | Sugerido |
| RNF-02 | `test_dominio_sem_api_real` | Integração (mock) | **Implementado** |
| RNF-03 | `test_persistencia_via_sheets` | Integração (API real) | Sugerido |

---

### 3.4 Matriz de Cobertura (Problemas × Requisitos)

| Problema de negócio | Requisitos que cobrem | Observação |
|---|---|---|
| Ruptura de estoque | RF-04, RF-08, RN-06 | Cobertura direta via visibilidade e alerta |
| Excesso de estoque | RF-04 (visibilidade indireta) | **Lacuna conhecida** — não existe regra dedicada a excesso/estoque máximo |
| Erros de inventário | RF-05, RF-06, RF-07, RN-01, RN-04 | Cobertura direta; inclui correções de contagem (HU-07) |
| Falta de rastreabilidade | RNF-07 | **Cobertura parcial** — não há requisito funcional dedicado a histórico de movimentações nesta versão |

---

## 4. Estratégia e Implementação de Testes

Esta seção documenta como os requisitos funcionais críticos (RF-04 e RF-07) foram efetivamente verificados por testes automatizados na Sprint 4, complementando a rastreabilidade da seção 3.3.

### 4.1 Framework e Ferramentas

- **Framework de testes:** [`unittest`](https://docs.python.org/3/library/unittest.html), da biblioteca padrão do Python — escolhido por não exigir dependências externas, atendendo à restrição de portabilidade (RNF-04).
- **Isolamento de dependências externas:** `unittest.mock` (`patch` e `MagicMock`), usado para substituir o `GoogleSheetsRepository` por um duplo de teste, garantindo que nenhuma chamada real à API do Google Sheets ocorra durante a execução (alinhado a RNF-02 e à HU-09).
- **Execução:**
  ```bash
  python -m unittest testes.py
  ```
- **Nota sobre nomenclatura:** as classes `TestRF05ListarProdutosAtivos` e `TestRF08SaidaComEstoqueInsuficiente` usam a numeração de RF da primeira versão deste documento. Após a renumeração da seção 2.1, elas correspondem a **RF-04** (listagem de produtos ativos) e **RF-07** (rejeição de saída por estoque insuficiente), respectivamente. Os nomes não foram alterados no código para não gerar churn em um arquivo já finalizado pela equipe; esta nota é a fonte de verdade para o mapeamento.

### 4.2 Abordagem de Isolamento

| Camada testada | Técnica | Justificativa |
|---|---|---|
| Domínio (`Produto.atualizar_estoque`) | Teste unitário puro, sem mock | O método não depende de I/O; testá-lo isoladamente valida a regra de negócio (RN-01) na origem. |
| Controlador (`EstoqueController`) | Teste unitário com `@patch("controlador.GoogleSheetsRepository")` | O controlador depende do repositório para buscar/persistir produtos; o mock permite configurar retornos (`buscar_por_sku`, `listar_todos`) e verificar chamadas (`atualizar.assert_called_once_with` / `assert_not_called`) sem acessar a planilha real. |

### 4.3 Métodos Cobertos e Casos de Teste

Conforme exigido pela Sprint 4 (mínimo de 2 métodos, com 3 casos cada — sucesso, falha e borda):

| Método testado | Caso de sucesso | Caso de falha | Caso de borda |
|---|---|---|---|
| `EstoqueController.listar_todos_produtos()` | Retorna os campos obrigatórios de cada produto ativo; exclui produtos inativos | Erro de conexão com a API (`RuntimeError`) é propagado para a camada superior, sem ser mascarado | Nenhum produto cadastrado retorna lista vazia, sem lançar exceção |
| `Produto.atualizar_estoque()` | Entrada soma a quantidade; saída dentro do limite é aceita | Saída maior que o disponível gera `ValueError` com mensagem clara; quantidade não é alterada (atomicidade) | Saída exatamente igual à quantidade disponível é aceita e zera o estoque |

Essas duas funcionalidades atendem isoladamente o mínimo da Sprint 4 (cada uma com os três tipos de caso). Como cobertura complementar, `EstoqueController.realizar_movimentacao()` também é exercitado: o teste `test_controlador_rejeita_saida_e_nao_persiste_movimentacao` cobre o caso de **falha** na integração (o controlador não chama `atualizar()` quando o domínio rejeita a operação). Os casos de **sucesso** e **borda** desse método específico (movimentação aceita sendo de fato persistida via `repositorio.atualizar()`) ainda não têm um teste dedicado — ver lacuna na seção 4.5.

### 4.4 Adequação da Estratégia

- Valida a regra de negócio (RN-01) isoladamente, sem ruído de infraestrutura;
- Valida a orquestração do controlador (busca → validação → persistência condicional) sem custo, latência ou risco de quota da API real;
- Mantém os testes rápidos e determinísticos, viabilizando execução frequente durante a sprint de refatoração.

### 4.5 Lacunas Não Cobertas

- `EstoqueController.realizar_movimentacao()` tem apenas o caso de falha testado; faltam um teste de sucesso (movimentação aceita persistida via `repositorio.atualizar()`) e um teste específico para SKU inexistente.
- `cadastrar_novo_produto` e `alterar_ativacao_produto` ainda não possuem testes automatizados nesta sprint, incluindo o caso de borda de alternância dupla (HU-08).
- Validações de entrada do `Produto` (ex.: preço negativo, nome vazio, quantidade fracionária prevista em RN-04) não foram exercitadas.
- RNF-08 (cobertura ≥ 80%, medida por `coverage.py`) ainda não foi calculada formalmente.
- Não existe uma classe abstrata `RepositorioBase` formalizando a interface de repositório (HU-10); a flexibilidade hoje é garantida pelo mock dos testes, não por uma abstração explícita no código de produção.
- Não há testes de integração reais contra a API do Google Sheets (RNF-03, RNF-06); toda a camada de persistência está mockada nesta etapa.

---

## 5. Checklist de Atendimento aos Critérios de Revisão

| Critério solicitado | Onde foi atendido |
|---|---|
| Padronizar HUs conforme modelo | Seção 1.4 (10 HUs no formato Como/Quero/Para que + MoSCoW, organizadas por stakeholder, sem lacunas de numeração) |
| Adicionar critérios de aceitação por HU | Seção 3.2 (Gherkin Dado/Quando/Então para as 10 HUs, com status de implementação) |
| Adicionar validação das HUs (Engenharia vs. Desenvolvimento dos Requisitos) | Seção 3.1 |
| Garantir que tudo isso esteja sendo atendido | Seções 3.3 e 3.4 (rastreabilidade e matriz de cobertura) + esta seção |

---

*Documento elaborado pela equipe StockFlow — Daniel Elder Kroda (especificação), Michel Rochytor Lima Barbosa (arquitetura), João Pedro Gonçalves de Oliveira (testes).*