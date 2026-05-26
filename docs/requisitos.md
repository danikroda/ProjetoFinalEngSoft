StockFlow — Requisitos do Sistema
1. Elicitação de Requisitos
1.1 Contexto e Problema
Pequenas e médias empresas gerenciam estoque de forma manual ou semi-manual, gerando quatro classes de problema:
ProblemaImpacto operacionalRuptura de estoquePerda de venda; cliente busca concorrenteExcesso de estoqueCapital imobilizado; risco de vencimento/obsolescênciaErros de inventárioDivergência entre físico e registrado; retrabalho de contagemFalta de rastreabilidadeSem histórico confiável; impossibilidade de auditar movimentações
O StockFlow ataca todos os quatro usando regras de negócio encapsuladas e comportamento verificável via testes automatizados.

1.2 Stakeholders Identificados
StakeholderPapelInteresse principalGestor de comprasPrimárioVisualizar estoque atual, receber alertas de nível mínimo, gerar relatóriosLojista / OperadorPrimárioRegistrar entradas e saídas rapidamente via CLIEquipe de desenvolvimentoInternoCódigo de domínio isolado, testável sem dependência de API realAuditoria / ContabilidadeSecundárioHistórico de movimentações com data, tipo e responsávelGoogle (plataforma)ExternoConformidade com os limites de uso da Sheets API

1.3 Histórias de Usuário
As histórias estão organizadas por papel e prioridade (MoSCoW).
Como Gestor de Compras
IDHistóriaPrioridadeHU-01Quero visualizar a quantidade atual de cada produto para saber o que precisa ser reposto.MustHU-02Quero receber um alerta quando um produto atingir o nível mínimo para fazer o pedido antes de faltar.MustHU-03Quero consultar o histórico de movimentações de um produto específico para identificar padrões de consumo.ShouldHU-04Quero filtrar produtos por categoria para facilitar o planejamento de compras por seção.CouldHU-05Quero exportar um relatório de estoque atual para compartilhar com o fornecedor.Could
Como Operador / Lojista
IDHistóriaPrioridadeHU-06Quero registrar a entrada de um lote de produtos informando quantidade e data para manter o inventário atualizado.MustHU-07Quero registrar a saída de um produto ao realizar uma venda para que o estoque seja descontado automaticamente.MustHU-08Quero cadastrar um novo produto com nome, SKU, categoria e quantidade inicial para começar a controlá-lo.MustHU-09Quero editar os dados de um produto existente (nome, categoria, nível mínimo) sem apagar seu histórico.ShouldHU-10Quero remover (inativar) um produto descontinuado sem deletar seu histórico de movimentações.Should
Como Desenvolvedor / Testador
IDHistóriaPrioridadeHU-11Quero que a lógica de domínio seja independente do Google Sheets para poder testá-la com mocks.MustHU-12Quero que a interface de repositório seja abstraída para trocar o backend de persistência sem alterar o domínio.Must

2. Definição de Requisitos
2.1 Requisitos Funcionais (RF)
Gestão de Produtos
IDDescriçãoHistória(s)RF-01O sistema deve permitir cadastrar um produto com os campos: nome (obrigatório), SKU (único, obrigatório), categoria (opcional), quantidade inicial ≥ 0 e nível mínimo ≥ 0.HU-08RF-02O sistema deve impedir o cadastro de dois produtos com o mesmo SKU.HU-08RF-03O sistema deve permitir editar nome, categoria e nível mínimo de um produto existente, preservando seu histórico.HU-09RF-04O sistema deve permitir inativar um produto, impedindo novas movimentações sem deletar o histórico.HU-10RF-05O sistema deve listar todos os produtos ativos com SKU, nome, categoria, quantidade atual e nível mínimo.HU-01
Movimentações de Estoque
IDDescriçãoHistória(s)RF-06O sistema deve registrar uma entrada de estoque informando: SKU do produto, quantidade (inteiro > 0) e data (default = hoje).HU-06RF-07O sistema deve registrar uma saída de estoque informando: SKU do produto, quantidade (inteiro > 0) e data.HU-07RF-08O sistema deve rejeitar uma saída cujo quantidade solicitada exceda a quantidade disponível, exibindo mensagem de erro clara.HU-07RF-09O sistema deve exibir o histórico de movimentações de um produto com data, tipo (entrada/saída) e quantidade.HU-03
Alertas e Relatórios
IDDescriçãoHistória(s)RF-10O sistema deve exibir, ao listar produtos, um indicador visual (ex.: [ALERTA]) para produtos com quantidade atual ≤ nível mínimo.HU-02RF-11O sistema deve exibir um relatório de produtos abaixo do nível mínimo em qualquer momento via comando dedicado.HU-02RF-12O sistema deve permitir filtrar a listagem de produtos por categoria.HU-04

2.2 Requisitos Não Funcionais (RNF)
IDCategoriaDescriçãoRNF-01ArquiteturaO sistema deve ser organizado em camadas: domínio, repositório, serviço e interface CLI, com dependências unidirecionais.RNF-02TestabilidadeO domínio (domain/) e os serviços (service/) devem ser 100% testáveis sem conexão com a Google Sheets API, via interface RepositorioBase mockada.RNF-03PersistênciaToda leitura e escrita de dados deve passar pela Google Sheets API via gspread; nenhum dado deve ser armazenado localmente além das credenciais.RNF-04PortabilidadeO sistema deve funcionar em qualquer ambiente com Python ≥ 3.10 e as dependências gspread e google-auth instaladas.RNF-05Usabilidade CLICada operação deve ser executável com um único comando. O sistema deve exibir mensagens de erro legíveis por humanos, não stack traces.RNF-06ConfiabilidadeFalhas de conectividade com a API (timeout, quota exceeded) devem ser capturadas e exibidas como erro amigável sem encerrar o processo com código de saída não-zero inesperado.RNF-07RastreabilidadeToda movimentação registrada deve conter timestamp ISO 8601 gerado pelo sistema, não pelo usuário.RNF-08ManutenibilidadeA cobertura de testes automatizados das classes de domínio e serviço deve ser ≥ 80% (medida por coverage.py).

2.3 Regras de Negócio (RN)
IDRegraRequisito(s) relacionadosRN-01Uma saída de estoque só é permitida se quantidade_atual >= quantidade_solicitada. Caso contrário, o sistema recusa a operação com a mensagem: "Estoque insuficiente: disponível X, solicitado Y."RF-07, RF-08RN-02O SKU é imutável após o cadastro. Qualquer tentativa de alteração deve ser recusada com mensagem explicativa.RF-03RN-03Um produto inativo (RF-04) não pode receber novas entradas ou saídas. Qualquer tentativa gera erro: "Produto [SKU] está inativo."RF-04, RF-06, RF-07RN-04A quantidade de qualquer movimentação (entrada ou saída) deve ser um inteiro positivo (> 0). Valores zero, negativos ou fracionários são recusados.RF-06, RF-07RN-05O nível mínimo de um produto deve ser ≥ 0. O padrão, se não informado, é 0 (sem alerta).RF-01, RF-10RN-06O alerta de nível mínimo é disparado quando quantidade_atual <= nivel_minimo (operador ≤, não estritamente <).RF-10, RF-11

2.4 Estrutura de Dados (modelo de domínio)
Produto
├── sku: str (PK, imutável)
├── nome: str
├── categoria: str | None
├── quantidade_atual: int (≥ 0)
├── nivel_minimo: int (≥ 0, default 0)
└── ativo: bool (default True)

Movimentacao
├── id: str (UUID gerado pelo sistema)
├── produto_sku: str (FK → Produto.sku)
├── tipo: Literal["entrada", "saida"]
├── quantidade: int (> 0)
└── data: datetime (ISO 8601, gerado pelo sistema)

3. Validação de Requisitos
3.1 Critérios de Aceitação por História de Usuário
HU-01 / RF-05 — Listar produtos ativos
Dado que existem produtos cadastrados e ativos,
Quando o operador executa python main.py listar,
Então o sistema exibe uma tabela com SKU, nome, categoria, quantidade atual e nível mínimo de cada produto ativo,
E produtos inativos não aparecem na listagem.

HU-02 / RF-10, RF-11 — Alerta de nível mínimo
Dado que um produto tem nivel_minimo = 5 e quantidade_atual = 3,
Quando o operador executa python main.py listar,
Então o sistema exibe [ALERTA] ao lado desse produto.
Dado que o operador executa python main.py alertas,
Então o sistema lista apenas os produtos com quantidade_atual <= nivel_minimo.

HU-06 / RF-06 — Registrar entrada
Dado um produto ativo com SKU "ABC-01" e quantidade atual 10,
Quando o operador executa python main.py entrada ABC-01 5,
Então a quantidade do produto passa a ser 15,
E uma movimentação do tipo "entrada" com quantidade 5 é registrada com timestamp automático.

HU-07, RF-07, RF-08, RN-01 — Registrar saída (incluindo falha)
Dado um produto ativo com quantidade atual 4,
Quando o operador tenta registrar saída de 6 unidades,
Então o sistema exibe: "Estoque insuficiente: disponível 4, solicitado 6."
E nenhuma movimentação é persistida.

HU-08 / RF-01, RF-02 — Cadastrar produto
Dado que não existe produto com SKU "XYZ-99",
Quando o operador executa python main.py cadastrar XYZ-99 "Caneta Azul" --categoria Papelaria --qtd 100 --min 20,
Então o produto é persistido com os dados informados e ativo = True.
Dado que já existe produto com SKU "XYZ-99",
Quando o operador tenta cadastrar outro produto com o mesmo SKU,
Então o sistema exibe: "SKU XYZ-99 já cadastrado."

HU-11, HU-12 / RNF-01, RNF-02 — Isolamento de domínio
Dado que a suite de testes é executada sem credenciais do Google,
Quando se executa python -m unittest discover codigo/tests,
Então todos os testes de domínio e serviço passam sem erros, usando o repositório mock em memória.

3.2 Rastreabilidade RF → Teste
RequisitoCaso de teste sugeridoTipoRF-01test_cadastrar_produto_validoUnitárioRF-02test_cadastrar_produto_sku_duplicadoUnitárioRF-03test_editar_produto_preserva_historicoUnitárioRF-04test_inativar_produto_bloqueia_movimentacaoUnitárioRF-06test_entrada_aumenta_quantidadeUnitárioRF-07test_saida_diminui_quantidadeUnitárioRF-08test_saida_estoque_insuficiente_rejeitadaUnitárioRF-10test_alerta_nivel_minimo_exibidoUnitárioRNF-02test_dominio_sem_api_realIntegração (mock)RNF-03test_persistencia_via_sheetsIntegração (API real)

3.3 Matriz de Cobertura (Problemas × Requisitos)
Problema de negócioRequisitos que cobremRuptura de estoqueRF-05, RF-10, RF-11, RN-06Excesso de estoqueRF-05, HU-04 (RF-12)Erros de inventárioRF-06, RF-07, RF-08, RN-01, RN-04Falta de rastreabilidadeRF-09, RNF-07

3.4 Requisitos Fora de Escopo (explicitamente excluídos)
Os itens abaixo foram identificados durante a elicitação mas não fazem parte do escopo deste projeto, por decisão da equipe, para manter foco na qualidade de engenharia:

Interface gráfica (GUI ou web)
Autenticação de usuários / controle de acesso
Múltiplos depósitos / localizações físicas
Integração com sistemas de PDV (ponto de venda)
Relatórios gráficos ou exportação para PDF
Gestão de fornecedores
