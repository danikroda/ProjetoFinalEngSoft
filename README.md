# StockFlow

Sistema de gerenciamento de estoque via linha de comando (CLI), com persistência no Google Sheets — desenvolvido para pequenas e médias empresas que hoje controlam o estoque manualmente em planilhas.

> 📄 Documentação completa: [`requisitos_stockflow.md`](./requisitos_stockflow.md) (requisitos, histórias de usuário, critérios de aceitação) e [`arquitetura.md`](./arquitetura.md) (camadas, diagramas e padrões de projeto).

---

## 📋 Visão Geral

O StockFlow centraliza o controle de estoque que hoje é feito de forma manual/semi-manual em planilhas, resolvendo quatro problemas recorrentes do varejo: **ruptura de estoque**, **excesso de estoque**, **erros de inventário** e **falta de rastreabilidade** (detalhes em `requisitos_stockflow.md`, seção 1.1).

**Funcionalidades principais:**

| Funcionalidade | Para quem |
|---|---|
| Cadastrar novo produto (nome, SKU, categoria, quantidade inicial, nível mínimo) | Operador |
| Listar produtos ativos, com indicador visual de alerta para estoque baixo | Gestor / Operador |
| Registrar entrada e saída de estoque (com rejeição de saída maior que o disponível) | Operador |
| Ativar/inativar um produto (toggle), preservando o histórico | Operador |
| Deletar um produto permanentemente | Operador |
| Notificação automática (tela + log em arquivo) quando o estoque cruza o nível mínimo | Gestor |

**Stack:** Python 3.10+, [`gspread`](https://docs.gspread.org/) (Google Sheets API), `google-auth`, `python-dotenv`.

---

## 🚀 Instruções de Uso

### Pré-requisitos

- Python 3.10 ou superior
- Uma planilha no Google Sheets e uma conta de serviço (*service account*) do Google Cloud com acesso a ela
- Pacotes: `gspread`, `google-auth`, `python-dotenv`

### Instalação

```bash
git clone <url-do-repositorio>
cd codigo
pip install -r requirements.txt
```

### Configuração

Crie um arquivo `.env` na raiz do projeto com as credenciais de acesso à planilha:

```env
GOOGLE_CREDENTIALS_PATH=credentials.json
SPREADSHEET_ID=<id_da_sua_planilha_google_sheets>
```

> O arquivo de credenciais (`credentials.json`) é o JSON gerado pela conta de serviço do Google Cloud. **Nunca** versione esse arquivo nem o `.env` — adicione ambos ao `.gitignore`.

### Executando o sistema

```bash
python main.py
```

O sistema abre um **menu interativo** no terminal. Cada opção corresponde a um comando independente (ver padrão *Command* em `arquitetura.md`, seção 3.4):

| Opção | Ação |
|---|---|
| 1 | Cadastrar novo produto |
| 2 | Listar estoque atual |
| 3 | Movimentar estoque (entrada/saída) |
| 4 | Alternar status (ativar/inativar produto) |
| 5 | Deletar produto |

Ao escolher uma opção, o sistema guia você com prompts (`input()`) para preencher os dados necessários (nome, SKU, quantidade etc.).

### Executando os testes

O framework de testes utilizado (`unittest`) é nativo do Python, portanto **não é necessário instalar nenhum pacote adicional via pip** para esta etapa. Além disso, os testes não fazem nenhuma chamada real à API do Google Sheets (o repositório é mockado, garantindo execução rápida e offline).

Para rodar a suíte de testes padrão, execute no terminal:

```bash
python -m unittest testes.py
```
Ou, se preferir uma saída mais detalhada (vendo o status de cada teste individualmente), execute:

```bash
python testes.py
```

---

### Executando o relatório

Para exportar a situação atual do seu estoque consolidado em um documento PDF, o projeto conta com um script gerador independente. Basta rodar o comando abaixo no terminal:

```bash
python relatorio.py
```
O arquivo será gerado e salvo automaticamente na pasta do projeto, pronto para ser impresso, arquivado ou enviado aos gestores e fornecedores.

---

## 🏗️ Decisões de Projeto

Resumo das principais decisões arquiteturais. O racional completo, com diagramas, está em [`arquitetura.md`](./arquitetura.md).

### Estrutura de módulos

| Módulo | Responsabilidade |
|---|---|
| `produto.py` | Modelo de domínio, validações e regras de negócio |
| `repository.py` | Comunicação com a Google Sheets API |
| `controlador.py` | Orquestração dos casos de uso |
| `visao.py` | Interface CLI e formatação de saída |
| `comando.py` | Cada ação do menu como um objeto `Comando` independente |
| `observador.py` | Notificações de estoque baixo (tela e arquivo de log) |
| `main.py` | Ponto de entrada e composição do sistema |
| `testes.py` | Testes unitários (domínio e controlador, com mock do repositório) |

### Principais trade-offs

| Decisão | Por quê | Custo assumido |
|---|---|---|
| Google Sheets como único armazenamento | A planilha já é a "verdade oficial" para os stakeholders; zero setup de banco de dados | Latência de rede a cada operação; sujeito à quota da API |
| CLI em vez de GUI/Web | Simplicidade de deploy (`python main.py`); foco nas regras de negócio | Menor usabilidade para usuários não técnicos |
| Repository acoplado ao Google Sheets, sem interface abstrata explícita | Reduz complexidade inicial; único backend previsto | Trocar de backend exige reescrever `repository.py` |
| SKU gerado por UUID (parcial) | Garante unicidade sem round-trip à API | SKU não é legível por humanos |
| `python-dotenv` para credenciais | Separa segredos do código-fonte | Exige `.gitignore` correto para não versionar `.env` |

### Padrões de projeto aplicados

| Padrão | Tipo | Onde |
|---|---|---|
| Repository | Arquitetural | `repository.py` ↔ `controlador.py` |
| MVC adaptado para CLI | Arquitetural | `visao.py`, `controlador.py`, `produto.py` |
| Factory Method | Projeto (Criacional) | `produto.py` (`do_repositorio`) |
| Command | Projeto (Comportamental) | `comando.py`, `visao.py` |
| Observer | Projeto (Comportamental) | `observador.py`, `controlador.py` |

A diferença entre padrão **arquitetural** (organiza a estrutura macro do sistema) e padrão de **projeto/GoF** (resolve um problema pontual entre algumas classes) está detalhada em `arquitetura.md`, seção 3.

---

## 👥 Equipe

- **Daniel Elder Kroda** — Especificação de requisitos
- **Michel Rochytor Lima Barbosa** — Arquitetura
- **João Pedro Gonçalves de Oliveira** — Testes