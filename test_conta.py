"""Esqueleto de testes de caixa branca para Conta.transferir.

Unidade sob teste: models.Conta.transferir (models.py, linhas 39-66).
Ver docs/relatorio-testes-caixa-branca.md para o Grafo de Fluxo de Controle,
a memória de cálculo da complexidade ciclomática e os caminhos básicos que
cada caso de teste (CT-xx) abaixo deve exercitar.

Cada função de teste está marcada com `pass` (TODO) para que a dupla
implemente os asserts. Os fixtures já deixam o cenário base pronto.
"""

import pytest

from models import Banco, Conta, Pessoa


# ---------------------------------------------------------------------------
# Fixtures de apoio
# ---------------------------------------------------------------------------

@pytest.fixture
def banco():
    banco = Banco(id_banco=1, nome_banco="Banco A", cnpj="00.000.000/0001-00")
    banco.criar_agencia({"numero": "0001", "cidade": "Recife"})
    return banco


@pytest.fixture
def outro_banco():
    banco = Banco(id_banco=2, nome_banco="Banco B", cnpj="11.111.111/0001-11")
    banco.criar_agencia({"numero": "0002", "cidade": "Olinda"})
    return banco


@pytest.fixture
def conta_corrente(banco):
    pessoa = Pessoa(nome="João", cpf="111.111.111-11", telefone="81900000000")
    conta, _ = pessoa.solicitar_conta(banco, Conta.TIPO_CORRENTE)
    conta.depositar(500)
    return conta


@pytest.fixture
def conta_poupanca(banco):
    pessoa = Pessoa(nome="Maria", cpf="222.222.222-22", telefone="81911111111")
    conta, _ = pessoa.solicitar_conta(banco, Conta.TIPO_POUPANCA)
    conta.depositar(500)
    return conta


# ---------------------------------------------------------------------------
# Decisões do GFC de Conta.transferir (ver relatório):
#   D1: valor <= 0                                          (linha 47)
#   D2: conta_destino is self                                (linha 50)
#   D3: tipo_conta == Poupança AND destino.tipo != Corrente  (linha 53)
#   D4: tipo_conta == Corrente AND id_banco != destino.banco (linha 56)
#   D5: saldo < valor                                        (linha 59)
# ---------------------------------------------------------------------------

def test_ct01_valor_invalido(conta_corrente, conta_poupanca):
    """
    CT-01 | Caminho básico P1: N1-N2(V)-N3-N14
    Critério: cobertura de nós/arestas (D1 = Verdadeiro)
    Cenário: valor de transferência igual ou menor que zero.
    Esperado: (False, "Valor de transferência inválido"); nenhum saldo alterado.
    """
    saldo_origem_antes = conta_corrente.saldo
    saldo_destino_antes = conta_poupanca.saldo

    sucesso, msg = conta_corrente.transferir(conta_poupanca, 0)

    assert sucesso is False
    assert msg == "Valor de transferência inválido"
    assert conta_corrente.saldo == saldo_origem_antes
    assert conta_poupanca.saldo == saldo_destino_antes


def test_ct02_transferencia_para_a_propria_conta(conta_corrente):
    """
    CT-02 | Caminho básico P2: N1-N2(F)-N4(V)-N5-N14
    Critério: cobertura de nós/arestas (D1 = Falso, D2 = Verdadeiro)
    Cenário: conta_destino é a própria conta de origem.
    Esperado: (False, "Não é possível transferir para a própria conta").
    """
    saldo_antes = conta_corrente.saldo

    sucesso, msg = conta_corrente.transferir(conta_corrente, 100)

    assert sucesso is False
    assert msg == "Não é possível transferir para a própria conta"
    assert conta_corrente.saldo == saldo_antes


def test_ct03_poupanca_para_poupanca_bloqueada(conta_poupanca, banco):
    """
    CT-03 | Caminho básico P3: N1-N2(F)-N4(F)-N6(V)-N7-N14
    Critério: cobertura de nós/arestas (D3 = Verdadeiro, A=Verdadeiro e B=Verdadeiro)
    Cenário: conta Poupança tentando transferir para outra conta Poupança.
    Esperado: (False, "Conta Poupança só pode transferir para conta Corrente").
    """
    p3 = Pessoa(nome="Carlos", cpf="333.333.333-33", telefone="81922222222")
    destino_poupanca, _ = p3.solicitar_conta(banco, Conta.TIPO_POUPANCA)

    saldo_origem_antes = conta_poupanca.saldo
    saldo_destino_antes = destino_poupanca.saldo

    sucesso, msg = conta_poupanca.transferir(destino_poupanca, 100)

    assert sucesso is False
    assert msg == "Conta Poupança só pode transferir para conta Corrente"
    assert conta_poupanca.saldo == saldo_origem_antes
    assert destino_poupanca.saldo == saldo_destino_antes


def test_ct04_corrente_para_outro_banco_bloqueada(conta_corrente, outro_banco):
    """
    CT-04 | Caminho básico P4: N1-N2(F)-N4(F)-N6(F)-N8(V)-N9-N14
    Critério: cobertura de nós/arestas (D4 = Verdadeiro)
    Cenário: conta Corrente tentando transferir para conta de outro banco.
    Esperado: (False, "Conta Corrente não pode transferir para outro banco").
    """
    p4 = Pessoa(nome="Ana", cpf="444.444.444-44", telefone="81933333333")
    destino_outro_banco, _ = p4.solicitar_conta(outro_banco, Conta.TIPO_CORRENTE)

    saldo_origem_antes = conta_corrente.saldo
    saldo_destino_antes = destino_outro_banco.saldo

    sucesso, msg = conta_corrente.transferir(destino_outro_banco, 100)

    assert sucesso is False
    assert msg == "Conta Corrente não pode transferir para outro banco"
    assert conta_corrente.saldo == saldo_origem_antes
    assert destino_outro_banco.saldo == saldo_destino_antes


def test_ct05_saldo_insuficiente(conta_corrente, banco):
    """
    CT-05 | Caminho básico P5: N1-N2(F)-N4(F)-N6(F)-N8(F)-N10(V)-N11-N14
    Critério: cobertura de nós/arestas (D5 = Verdadeiro)
    Cenário: valor de transferência maior que o saldo disponível.
    Esperado: (False, "Saldo insuficiente"); nenhum saldo alterado.
    """
    p5 = Pessoa(nome="Lucas", cpf="555.555.555-55", telefone="81944444444")
    destino_corrente, _ = p5.solicitar_conta(banco, Conta.TIPO_CORRENTE)

    saldo_origem_antes = conta_corrente.saldo
    saldo_destino_antes = destino_corrente.saldo

    sucesso, msg = conta_corrente.transferir(destino_corrente, 9999.00)

    assert sucesso is False
    assert msg == "Saldo insuficiente"
    assert conta_corrente.saldo == saldo_origem_antes
    assert destino_corrente.saldo == saldo_destino_antes
    

def test_ct06_transferencia_corrente_para_corrente_com_sucesso(conta_corrente, banco):
    """
    CT-06 | Caminho básico P6: N1-N2(F)-N4(F)-N6(F)-N8(F)-N10(F)-N12-N13-N14
    Critério: cobertura de nós/arestas + caminho básico (todas as decisões = Falso)
    Cenário: Corrente -> Corrente, mesmo banco, saldo suficiente.
    Esperado: (True, "Transferência realizada com sucesso"); saldo debitado na
    origem e creditado no destino; histórico atualizado nas duas contas.
    TODO: criar segunda conta Corrente no mesmo banco e implementar.
    """
    p6 = Pessoa(nome="Beatriz", cpf="666.666.666-66", telefone="81955555555")
    destino_corrente, _ = p6.solicitar_conta(banco, Conta.TIPO_CORRENTE)

    sucesso, msg = conta_corrente.transferir(destino_corrente, 200.0)

    assert sucesso is True
    assert msg == "Transferência realizada com sucesso"
    assert conta_corrente.saldo == 300.0
    assert destino_corrente.saldo == 200.0
    assert any("Transferência de 200.00 para conta" in h for h in conta_corrente.historico)
    assert any("Recebimento de 200.00 da conta" in h for h in destino_corrente.historico)


def test_ct07_poupanca_para_corrente_com_sucesso(conta_poupanca, conta_corrente):
    """
    CT-07 | Mesmo caminho de P6, exercitando D3 = Falso por outra combinação
    das condições atômicas (A = Verdadeiro, B = Falso, avaliadas sem
    curto-circuito adicional).
    Critério: condições compostas (cobertura das condições atômicas de D3)
    Cenário: Poupança -> Corrente, mesmo banco, saldo suficiente.
    Esperado: (True, "Transferência realizada com sucesso").
    """
    sucesso, msg = conta_poupanca.transferir(conta_corrente, 150.0)

    assert sucesso is True
    assert msg == "Transferência realizada com sucesso"
    assert conta_poupanca.saldo == 350.0
    assert conta_corrente.saldo == 650.0


def test_ct08_poupanca_para_corrente_banco_diferente_com_sucesso(conta_poupanca, outro_banco):
    """
    CT-08 (extra) | Critério: análise de requisito / ambiguidade
    Cenário: Poupança -> Corrente em outro banco. A regra de negócio não
    impõe restrição de banco para contas Poupança (apenas D4, que só se
    aplica a Corrente, verifica o banco). Confirmar com o professor se este
    comportamento é intencional ou se deveria haver a mesma restrição de
    banco também para Poupança.
    """
    p8 = Pessoa(nome="Eduardo", cpf="888.888.888-88", telefone="81977777777")
    destino_outro_banco, _ = p8.solicitar_conta(outro_banco, Conta.TIPO_CORRENTE)

    sucesso, msg = conta_poupanca.transferir(destino_outro_banco, 100.0)

    assert sucesso is True
    assert msg == "Transferência realizada com sucesso"
    assert conta_poupanca.saldo == 400.0
    assert destino_outro_banco.saldo == 100.0