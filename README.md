#  StockFlow — Sistema de Gerenciamento de Estoque

## Descrição

O **StockFlow** é um sistema de gerenciamento de estoque desenvolvido inteiramente em Python, sem interface gráfica, operado via linha de comando. A persistência de dados é feita através da **Google Sheets API**, usando a planilha como banco de dados simples e acessível.

O foco do projeto não é a quantidade de funcionalidades, mas a **qualidade de engenharia**: requisitos bem definidos, arquitetura justificada, padrões de projeto aplicados intencionalmente e testes automatizados.

---

## Problema que Resolve

Pequenas empresas frequentemente controlam estoque em planilhas manuais ou de forma informal, o que gera:

- Ruptura de estoque — produto em falta no momento da venda
- Excesso de estoque — capital parado sem necessidade
- Erros de inventário — divergências entre o físico e o registrado
- Falta de rastreabilidade — sem histórico confiável de movimentações

O StockFlow centraliza esse controle com regras de negócio bem encapsuladas e comportamento verificável via testes.

---

## Público-Alvo

Pequenas e médias empresas, gestores de compras e lojistas que precisam de controle de estoque simples, auditável e sem custo de infraestrutura.

---

## Equipe

| Membro | Responsabilidade |
|---|---|
| [Daniel Elder Kroda] | Modelagem do domínio e especificação de requisitos |
| [Michel Rochytor Lima Barbosa] | Arquitetura, padrões de projeto e integração Google Sheets |
| [João Pedro Gonçalves de Oliveira] | Testes automatizados e documentação de qualidade |

---

## Estrutura do Repositório

```
stockflow/
├── README.md               # Visão geral, instruções de uso e decisões de projeto
│
├── docs/
│   ├── requisitos.md       # Síntese da elicitação, histórias de usuário e validação
│   ├── arquitetura.md      # Diagrama, componentes, padrões de projeto e trade-offs
│   └── testes.md           # Estratégia de testes, cobertura e lacunas
│
└── codigo/
    ├── *.py                # Código-fonte em Python
    └── tests/
        └── *.py            # Testes automatizados com unittest
```

---

## Instruções de Uso

### Pré-requisitos

```bash
pip install gspread google-auth
```

### Configuração da API do Google Sheets

1. Criar um projeto no [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar a **Google Sheets API** e a **Google Drive API**
3. Criar uma **conta de serviço** e baixar o `credentials.json`
4. Compartilhar a planilha com o e-mail da conta de serviço
5. Configurar as variáveis de ambiente:

```bash
export GOOGLE_CREDENTIALS_PATH=/caminho/para/credentials.json
export SPREADSHEET_ID=id_da_sua_planilha
```

### Executando o sistema

```bash
python codigo/main.py
```

### Executando os testes

```bash
python -m unittest discover codigo/tests
```

---

## Decisões de Projeto

| Decisão | Justificativa |
|---|---|
| Python puro, sem GUI | Foco em engenharia de software, não em frontend |
| Google Sheets como persistência | Simples, gratuito, auditável e sem necessidade de banco local |
| Arquitetura em camadas | Isola domínio da infraestrutura; domínio 100% testável sem API real |
| Interface abstrata para repositório | Permite mockar o Google Sheets nos testes unitários |
| unittest (stdlib) | Sem dependências externas para testes; padrão da linguagem |

Para detalhes de cada decisão, consulte [`docs/arquitetura.md`](docs/arquitetura.md).

---

*Projeto acadêmico — [UTFPR] — [2026]*
