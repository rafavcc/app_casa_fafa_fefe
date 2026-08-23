# Mansão Fefael

Aplicação web simples para acompanhar as despesas da casa, separando gastos
variáveis e fixos e calculando a divisão mensal entre Fafa e Fefe.

## Recursos

- Registro e exclusão de gastos variáveis
- Registro de gastos fixos recorrentes
- Categorias para cada tipo de gasto
- Ajuste da proporção mensal de pagamento
- Balanço mensal de quanto cada pessoa pagou e deve pagar
- Tema claro e escuro
- API REST para as operações principais

## Tecnologias

- Python 3.10 ou superior
- FastAPI
- NiceGUI
- SQLAlchemy
- SQLite

## Como executar

Clone o repositório e entre na pasta do projeto:

```bash
git clone https://github.com/rafavcc/app_casa_fafa_fefe.git
cd app_casa_fafa_fefe
```

Crie e ative um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

No Windows (PowerShell), use:

```powershell
venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie as categorias iniciais. Este comando também cria o banco de dados local
(`casa.db`) se ele ainda não existir:

```bash
python -m app.seed
```

Inicie a aplicação:

```bash
uvicorn app.main:app --reload
```

Abra [http://localhost:8080](http://localhost:8080) no navegador.

## Banco de dados e privacidade

Os dados são armazenados localmente no arquivo `casa.db`, na raiz do projeto.
Esse arquivo contém despesas pessoais e é ignorado pelo Git; não o envie para um repositório público.

Para recomeçar com um banco vazio, feche a aplicação, remova `casa.db` e rode
novamente:

```bash
python -m app.seed
```

## Rotas principais

| Rota | Descrição |
| --- | --- |
| `/` | Visão geral das despesas |
| `/variable` | Gastos variáveis |
| `/regular` | Gastos fixos |
| `/balance` | Balanço mensal |
| `/api/health` | Verificação de saúde da API |

## Estrutura do projeto

```text
app/
├── main.py          # Aplicação FastAPI e interface NiceGUI
├── database.py      # Configuração do SQLite e sessões
├── models.py        # Modelos do banco de dados
├── schemas.py       # Esquemas de validação da API
├── crud.py          # Operações no banco de dados
├── balance.py       # Cálculo do balanço mensal
├── seed.py          # Categorias iniciais
├── theme.py         # Tema visual da interface
└── pages/           # Telas da aplicação
```

## Desenvolvimento

Com o ambiente virtual ativado, execute o mesmo comando de inicialização após alterar o código. O banco de dados local e o diretório `venv/` não devem ser versionados.
