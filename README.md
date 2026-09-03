# Engenharia-Software-III

Alocação de atividades feita em Engenharia de Software III.

## Atividade: Testes de Técnica de Caixa Branca

Mini sistema bancário em Python, criado para aplicar critérios de teste
estrutural (grafo de fluxo de controle, complexidade ciclomática, caminhos
independentes e cobertura) sobre uma unidade de código real.

### Estrutura

| Arquivo | Conteúdo |
|---|---|
| [`models.py`](models.py) | Classes `Pessoa`, `Banco` e `Conta` com as regras de negócio (criação de conta, depósito, saque, transferência) |
| [`main.py`](main.py) | Script de demonstração manual do fluxo (não é a suíte de testes) |
| [`tests.py`](tests.py) | Esqueleto dos testes unitários (`pytest`) do método `Conta.transferir` — unidade analisada na atividade |
| [`docs/relatorio-testes-caixa-branca.md`](docs/relatorio-testes-caixa-branca.md) | Relatório da atividade: GFC, complexidade ciclomática, caminhos independentes e casos de teste |

### Regras de negócio implementadas

- Uma `Pessoa` pode ter no máximo uma conta de cada tipo (Corrente ou
  Poupança) por banco, mas pode ter contas do mesmo tipo em bancos
  diferentes.
- Conta **Corrente**: transferência, saque, depósito e extrato. Não pode
  transferir para contas de outro banco.
- Conta **Poupança**: apenas extrato e transferência, e só pode transferir
  para contas do tipo Corrente.

### Requisitos

- Python 3.12+
- `pip install pytest pytest-cov radon` (para rodar os testes e as
  métricas de cobertura/complexidade da atividade)

### Como executar

```bash
python main.py
```

### Como rodar os testes (quando implementados)

```bash
pytest tests.py -v
pytest tests.py --cov=models --cov-branch --cov-report=html
```
