"""Testes (pytest) para a funcionalidade de abertura de conta.

Unidade sob teste: Pessoa.solicitar_conta / Banco.criar_conta (models.py).
Escrito para a atividade de Testes Estáticos (revisão manual + Ruff):
os dois primeiros testes reproduzem, com evidência executável, os achados
A-01 e A-02 registrados no relatório da atividade. Executados contra a
versão original (models_antes.py) eles falham; contra a versão corrigida
(models.py) eles passam.
"""

import pytest

from models import Banco, Conta, Pessoa


@pytest.fixture
def banco():
    banco = Banco(id_banco=1, nome_banco="Banco A", cnpj="00.000.000/0001-00")
    banco.criar_agencia({"numero": "0001", "cidade": "Recife"})
    return banco


def test_solicitar_conta_com_dados_validos_cria_conta(banco):
    pessoa = Pessoa(nome="João", cpf="111.111.111-11", telefone="81900000000")

    conta, msg = pessoa.solicitar_conta(banco, Conta.TIPO_CORRENTE)

    assert conta is not None
    assert msg == "Conta criada com sucesso"
    assert conta.tipo_conta == Conta.TIPO_CORRENTE


def test_solicitar_conta_rejeita_tipo_de_conta_invalido(banco):
    """A-01: nada impede um tipo_conta fora de TIPO_CORRENTE/TIPO_POUPANCA."""
    pessoa = Pessoa(nome="João", cpf="111.111.111-11", telefone="81900000000")

    conta, msg = pessoa.solicitar_conta(banco, "Tipo-Que-Nao-Existe")

    assert conta is None
    assert msg == "Tipo de conta inválido"


def test_solicitar_conta_detecta_duplicidade_com_cpf_sem_pontuacao(banco):
    """A-02: o mesmo CPF, digitado sem pontuação, deve contar como duplicado."""
    pessoa = Pessoa(nome="João", cpf="111.111.111-11", telefone="81900000000")
    pessoa.solicitar_conta(banco, Conta.TIPO_CORRENTE)

    mesma_pessoa_cpf_sem_pontuacao = Pessoa(
        nome="João", cpf="11111111111", telefone="81900000000"
    )
    conta, msg = mesma_pessoa_cpf_sem_pontuacao.solicitar_conta(banco, Conta.TIPO_CORRENTE)

    assert conta is None
    assert msg == "Pessoa já possui uma conta desse tipo neste banco"
    assert len(banco.lista_contas) == 1


def test_solicitar_conta_permite_mesmo_cpf_em_banco_diferente(banco):
    """Regressão: a regra é por banco, não global (README, regras de negócio)."""
    outro_banco = Banco(id_banco=2, nome_banco="Banco B", cnpj="11.111.111/0001-11")
    outro_banco.criar_agencia({"numero": "0002", "cidade": "Olinda"})

    pessoa = Pessoa(nome="João", cpf="111.111.111-11", telefone="81900000000")
    pessoa.solicitar_conta(banco, Conta.TIPO_CORRENTE)
    conta, msg = pessoa.solicitar_conta(outro_banco, Conta.TIPO_CORRENTE)

    assert conta is not None
    assert msg == "Conta criada com sucesso"
