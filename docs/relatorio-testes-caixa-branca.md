# Relatório — Testes de Técnica de Caixa Branca

**Disciplina:** Engenharia de Software III
**Atividade:** Testes de Técnica de Caixa Branca
**Versão do código analisado:** commit `216965b` (branch `main`) — `models.py` inalterado desde `c7ae92a`; `216965b` adicionou a implementação dos testes em `test_conta.py`.

## 1. Identificação da equipe e do projeto

- **Integrantes:** Nicolas Damasceno, Amanda Santos
- **Projeto:** Mini sistema bancário (Pessoa, Banco, Conta)
- **Linguagem:** Python 3.12
- **Arquivo analisado:** [`models.py`](../models.py)
- **Classe / método analisado:** `Conta.transferir` (linhas 39-66)
- **Arquivo de testes:** [`test_conta.py`](../test_conta.py)

## 2. Código selecionado e regra de negócio

`Conta.transferir(conta_destino, valor)` implementa a regra de transferência
entre contas do mini sistema bancário: valida o valor solicitado, impede
transferência para a própria conta, aplica as restrições específicas de
Conta Poupança (só pode enviar para Conta Corrente) e de Conta Corrente
(não pode enviar para outro banco), verifica saldo suficiente e, em caso
positivo, debita a origem e credita o destino.

```python
39: def transferir(self, conta_destino, valor):
40:     """Transfere `valor` desta conta para `conta_destino`. [...] """
47:     if valor <= 0:
48:         return False, "Valor de transferência inválido"
49:
50:     if conta_destino is self:
51:         return False, "Não é possível transferir para a própria conta"
52:
53:     if self.tipo_conta == Conta.TIPO_POUPANCA and conta_destino.tipo_conta != Conta.TIPO_CORRENTE:
54:         return False, "Conta Poupança só pode transferir para conta Corrente"
55:
56:     if self.tipo_conta == Conta.TIPO_CORRENTE and self.id_banco != conta_destino.id_banco:
57:         return False, "Conta Corrente não pode transferir para outro banco"
58:
59:     if self.saldo < valor:
60:         return False, "Saldo insuficiente"
61:
62:     self.saldo -= valor
63:     conta_destino.saldo += valor
64:     self.historico.append(f"Transferência de {valor:.2f} para conta {conta_destino.numero_conta}")
65:     conta_destino.historico.append(f"Recebimento de {valor:.2f} da conta {self.numero_conta}")
66:     return True, "Transferência realizada com sucesso"
```

**Entradas:** `conta_destino` (objeto `Conta`), `valor` (número).
**Saída:** tupla `(bool, str)` — sucesso/falha e mensagem.
**Retornos antecipados:** linhas 48, 51, 54, 57, 60 (todos os cenários de
rejeição). Não há exceções lançadas — cada bloqueio de regra de negócio é
comunicado via retorno, não via `raise`.

## 3. Grafo de Fluxo de Controle (GFC)

```mermaid
flowchart TD
    N1(["N1: início — transferir(conta_destino, valor)"]) --> N2{"N2 — D1: valor <= 0 ?"}
    N2 -- V --> N3["N3: return False, 'Valor de transferência inválido'"]
    N2 -- F --> N4{"N4 — D2: conta_destino is self ?"}
    N4 -- V --> N5["N5: return False, 'Não é possível transferir para a própria conta'"]
    N4 -- F --> N6{"N6 — D3: Poupança AND destino != Corrente ?"}
    N6 -- V --> N7["N7: return False, 'Poupança só pode transferir para Corrente'"]
    N6 -- F --> N8{"N8 — D4: Corrente AND banco != banco destino ?"}
    N8 -- V --> N9["N9: return False, 'Corrente não pode transferir para outro banco'"]
    N8 -- F --> N10{"N10 — D5: saldo < valor ?"}
    N10 -- V --> N11["N11: return False, 'Saldo insuficiente'"]
    N10 -- F --> N12["N12: debita origem / credita destino / registra histórico"]
    N12 --> N13["N13: return True, 'Transferência realizada com sucesso'"]
    N3 --> N14(["N14: fim"])
    N5 --> N14
    N7 --> N14
    N9 --> N14
    N11 --> N14
    N13 --> N14
```

### Correspondência nó ↔ linha(s) do código

| Nó | Linha(s) | Tipo | Descrição |
|----|----------|------|-----------|
| N1 | 39 | Início | Entrada do método |
| N2 | 47 | Decisão (D1) | `valor <= 0` |
| N3 | 48 | Bloco / retorno | Valor inválido |
| N4 | 50 | Decisão (D2) | `conta_destino is self` |
| N5 | 51 | Bloco / retorno | Transferência para a própria conta |
| N6 | 53 | Decisão (D3) | Poupança → destino diferente de Corrente |
| N7 | 54 | Bloco / retorno | Poupança bloqueada |
| N8 | 56 | Decisão (D4) | Corrente → banco diferente |
| N9 | 57 | Bloco / retorno | Corrente bloqueada (banco diferente) |
| N10 | 59 | Decisão (D5) | `saldo < valor` |
| N11 | 60 | Bloco / retorno | Saldo insuficiente |
| N12 | 62-65 | Bloco sequencial | Débito, crédito e histórico |
| N13 | 66 | Bloco / retorno | Sucesso |
| N14 | — | Fim | Saída única (unificação dos retornos) |

### Arestas

N1→N2, N2→N3 (V), N2→N4 (F), N3→N14, N4→N5 (V), N4→N6 (F), N5→N14,
N6→N7 (V), N6→N8 (F), N7→N14, N8→N9 (V), N8→N10 (F), N9→N14,
N10→N11 (V), N10→N12 (F), N11→N14, N12→N13, N13→N14.

## 4. Complexidade ciclomática

| N (nós) | E (arestas) | P (componentes) | D (decisões) |
|---|---|---|---|
| 14 | 18 | 1 | 5 (D1 a D5) |

- **V(G) = E - N + 2P = 18 - 14 + 2(1) = 6**
- **V(G) = D + 1 = 5 + 1 = 6**
- **Resultado de ferramenta (Radon):**

```
$ radon cc models.py -s
models.py
    M 39:4 Conta.transferir - B (8)
```

Radon aponta **complexidade 8** para `transferir`, e não 6 como no cálculo
manual. A diferença é explicada pela forma como cada ferramenta conta
decisões: no cálculo manual contamos **cada `if` como um ponto de
decisão** (5 ifs → D=5 → V(G)=6), enquanto Radon (assim como o McCabe
"estendido") conta **cada operador booleano (`and`/`or`) dentro de uma
condição como uma decisão adicional**. As linhas 53 e 56 têm um `and`
cada, então Radon soma +2 decisões (5 ifs + 2 `and` = 7 → V(G) = 7+1 = 8).
Essa divergência é esperada e documentada aqui — o código não foi alterado
para forçar os números a coincidirem, conforme orientado no enunciado.

**Conclusão:** são necessários **6 caminhos básicos** e, no mínimo,
**6 casos de teste** para satisfazer o critério de caminhos. Casos
adicionais são necessários para cobrir condições compostas (ver seção 6).

## 5. Caminhos linearmente independentes

| Caminho | Sequência de nós | Cenário |
|---|---|---|
| P1 | N1-N2(V)-N3-N14 | Valor inválido |
| P2 | N1-N2(F)-N4(V)-N5-N14 | Transferência para a própria conta |
| P3 | N1-N2(F)-N4(F)-N6(V)-N7-N14 | Poupança → Poupança (bloqueada) |
| P4 | N1-N2(F)-N4(F)-N6(F)-N8(V)-N9-N14 | Corrente → outro banco (bloqueada) |
| P5 | N1-N2(F)-N4(F)-N6(F)-N8(F)-N10(V)-N11-N14 | Saldo insuficiente |
| P6 | N1-N2(F)-N4(F)-N6(F)-N8(F)-N10(F)-N12-N13-N14 | Transferência com sucesso |

Quantidade de caminhos (6) igual à complexidade ciclomática adotada (6).
Todos os seis são viáveis com combinações simples de entrada — nenhum
precisou ser substituído por inviabilidade.

## 6. Casos de teste e critérios atendidos

| ID | Entrada/cenário | Resultado esperado | Caminho | Critério |
|----|------------------|---------------------|---------|----------|
| CT-01 | valor ≤ 0 | `(False, "Valor de transferência inválido")` | P1 | Nós / arestas / caminho |
| CT-02 | destino = própria conta | `(False, "Não é possível transferir para a própria conta")` | P2 | Nós / arestas / caminho |
| CT-03 | Poupança → Poupança | `(False, "Conta Poupança só pode transferir para conta Corrente")` | P3 | Nós / arestas / caminho |
| CT-04 | Corrente → Corrente de outro banco | `(False, "Conta Corrente não pode transferir para outro banco")` | P4 | Nós / arestas / caminho |
| CT-05 | valor > saldo disponível | `(False, "Saldo insuficiente")` | P5 | Nós / arestas / caminho |
| CT-06 | Corrente → Corrente, mesmo banco, saldo suficiente | `(True, "Transferência realizada com sucesso")` | P6 | Nós / arestas / caminho |
| CT-07 | Poupança → Corrente, mesmo banco, saldo suficiente | `(True, "Transferência realizada com sucesso")` | equivalente a P6 | Condições compostas (D3 falso via combinação A=V/B=F) |
| CT-08 | Poupança → Corrente em outro banco, saldo suficiente | `(True, "Transferência realizada com sucesso")` | equivalente a P6 | Análise de requisito (ver observação abaixo) |

Os casos CT-01 a CT-06 esgotam os 6 caminhos básicos e, como consequência,
também cobrem todos os nós e todas as arestas do GFC (não há laço, então
não se aplica o critério "zero/uma/mais de uma iteração"). CT-07 é
necessário porque D3 é uma condição composta (`A and B`) e os caminhos
básicos, sozinhos, não exercitam a combinação A=Verdadeiro/B=Falso — só
A=Verdadeiro/B=Verdadeiro (P3) e A=Falso (P4, P5, P6).

**Observação sobre CT-08 / possível ambiguidade de requisito:** a regra de
negócio informada restringe transferências entre bancos diferentes apenas
para Conta Corrente (D4). Não há restrição equivalente para Conta
Poupança, então uma Poupança pode transferir para uma Corrente em outro
banco. Vale confirmar com o professor/enunciado original se esse
comportamento é intencional.

## 7. Execução, cobertura e análise dos resultados

Comandos executados:

```bash
pytest test_conta.py -v
pytest test_conta.py --cov=models --cov-branch --cov-report=term-missing --cov-report=html
radon cc models.py -s
```

Resultado da execução dos 8 testes:

```
test_conta.py::test_ct01_valor_invalido PASSED
test_conta.py::test_ct02_transferencia_para_a_propria_conta PASSED
test_conta.py::test_ct03_poupanca_para_poupanca_bloqueada PASSED
test_conta.py::test_ct04_corrente_para_outro_banco_bloqueada PASSED
test_conta.py::test_ct05_saldo_insuficiente PASSED
test_conta.py::test_ct06_transferencia_corrente_para_corrente_com_sucesso PASSED
test_conta.py::test_ct07_poupanca_para_corrente_com_sucesso PASSED
test_conta.py::test_ct08_poupanca_para_corrente_banco_diferente_com_sucesso PASSED

8 passed in 0.09s
```

Cobertura obtida:

```
Name        Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------
models.py      78     16     24      3    75%   23, 29-37, 69, 72, 90, 98, 110, 115
-------------------------------------------------------
TOTAL          78     16     24      3    75%
```

Respostas às perguntas da atividade:

1. **Todos os testes passaram?** Sim, os 8 testes de `test_conta.py`
   passaram sem falhas.
2. **Cobertura de linhas/ramos:** o arquivo `models.py` como um todo tem
   75% de cobertura, mas as linhas e ramos **faltantes (23, 29-37, 69, 72,
   90, 98, 110, 115) pertencem a outros métodos** (`Conta.sacar`,
   `Conta.depositar`, `Conta.__repr__`, `Banco.criar_conta` sem agência,
   `Banco.__repr__`, `Pessoa.__repr__`), que estão fora do escopo desta
   atividade. Isolando só a unidade analisada: **`Conta.transferir`
   (linhas 39-66) tem 100% de cobertura de linhas e 100% de cobertura de
   ramos** — todas as 5 decisões foram exercitadas nos dois sentidos
   (Verdadeiro e Falso).
3. **Nós e arestas do GFC cobertos?** Sim. Cada teste cobre a sequência de
   nós indicada na coluna "Caminho" da tabela da seção 6; juntos, CT-01 a
   CT-08 passam por todos os 14 nós e todas as 18 arestas do grafo pelo
   menos uma vez, incluindo as saídas V e F de cada decisão.
4. **Os 6 caminhos básicos foram exercitados?** Sim — CT-01 a CT-06
   correspondem exatamente a P1-P6.
5. **Trecho inalcançável, caminho inviável, retorno antecipado ou exceção
   não coberta?** Não há trechos inalcançáveis nem exceções em
   `transferir` (todas as regras de negócio retornam `(False, msg)` em
   vez de lançar exceção). Os 5 retornos antecipados (linhas 48, 51, 54,
   57, 60) foram todos exercitados por algum teste.
6. **A ferramenta calculou a mesma complexidade manual?** Não — Radon
   retornou **8**, enquanto o cálculo manual (contando cada `if` como uma
   decisão) deu **6**. A diferença é a contagem dos operadores `and` das
   linhas 53 e 56 como decisões adicionais (ver seção 4). Isso não
   invalida os 6 caminhos básicos exercitados: eles continuam sendo os
   caminhos linearmente independentes pela definição de McCabe simples;
   a diferença está apenas em quantos *deveriam* existir teoricamente
   segundo cada convenção de contagem. Os testes CT-07 e CT-08 cobrem
   justamente as combinações extras de condições atômicas que a contagem
   "8" do Radon está enxergando.
7. **Defeito, ambiguidade de requisito ou oportunidade de refatoração?**
   Nenhum defeito foi encontrado — todos os testes passaram no primeiro
   commit da implementação. Uma **ambiguidade de requisito** foi
   identificada e documentada no CT-08: a regra de negócio não impõe
   restrição de banco para transferências originadas de Conta Poupança
   (só a Conta Corrente tem essa restrição), permitindo Poupança →
   Corrente entre bancos diferentes. Como **oportunidade de
   refatoração**, o método `transferir` poderia extrair a validação de
   tipo/banco de destino em funções auxiliares nomeadas (ex.:
   `_poupanca_pode_transferir_para` / `_corrente_pode_transferir_para`)
   para deixar cada regra de negócio testável isoladamente, mas isso não
   foi feito para não alterar o código já analisado nesta atividade.

## 8. Conclusão e referências

A unidade `Conta.transferir` foi validada com sucesso pelos 8 casos de
teste planejados: os 6 caminhos básicos exigidos pela complexidade
ciclomática (V(G)=6 pelo cálculo manual) foram todos exercitados, e mais
2 casos adicionais (CT-07 e CT-08) garantiram a cobertura das condições
compostas e revelaram uma ambiguidade de requisito no comportamento de
transferências entre bancos para contas Poupança. A cobertura de linhas e
ramos da unidade analisada chegou a 100%, mesmo com a cobertura total do
arquivo em 75% — a diferença fica em métodos fora do escopo da atividade
(`sacar`, `depositar`, `criar_conta`, `__repr__`), que podem ser
cobertos em uma iteração futura caso a disciplina peça a extensão da
análise a outras unidades. A divergência entre o cálculo manual (V(G)=6)
e o resultado do Radon (8) foi documentada e explicada pela forma como
cada abordagem conta condições compostas, sem necessidade de alterar o
código-fonte.

**Referências:** pytest, coverage.py / pytest-cov, Radon, Mermaid Live
Editor (usado para o GFC da seção 3).
