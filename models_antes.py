"""Mini sistema bancário orientado a objetos.

Classes: Pessoa, Banco, Conta.
Sem dependências de banco de dados, rede ou interface gráfica.
"""


class Conta:
    TIPO_CORRENTE = "Corrente"
    TIPO_POUPANCA = "Poupança"

    def __init__(self, numero_conta, agencia, id_banco, cpf_pessoa, tipo_conta, saldo_inicial=0.0):
        self.numero_conta = numero_conta
        self.agencia = agencia
        self.id_banco = id_banco
        self.cpf_pessoa = cpf_pessoa
        self.tipo_conta = tipo_conta
        self.saldo = saldo_inicial
        self.historico = []

    def depositar(self, valor):
        if valor <= 0:
            return False, "Valor de depósito inválido"
        self.saldo += valor
        self.historico.append(f"Depósito de {valor:.2f}")
        return True, "Depósito realizado com sucesso"

    def sacar(self, valor):
        if self.tipo_conta != Conta.TIPO_CORRENTE:
            return False, "Apenas contas Correntes podem realizar saque"
        if valor <= 0:
            return False, "Valor de saque inválido"
        if valor > self.saldo:
            return False, "Saldo insuficiente"
        self.saldo -= valor
        self.historico.append(f"Saque de {valor:.2f}")
        return True, "Saque realizado com sucesso"

    def transferir(self, conta_destino, valor):
        """Transfere `valor` desta conta para `conta_destino`.

        Unidade-alvo da análise de Testes de Caixa Branca (ver PARTE 3 do
        relatório): concentra as regras de negócio de transferência entre
        Contas Correntes e Poupanças, incluindo validação de valor, saldo
        e restrições de tipo/banco de destino.
        """
        if valor <= 0:
            return False, "Valor de transferência inválido"

        if conta_destino is self:
            return False, "Não é possível transferir para a própria conta"

        if self.tipo_conta == Conta.TIPO_POUPANCA and conta_destino.tipo_conta != Conta.TIPO_CORRENTE:
            return False, "Conta Poupança só pode transferir para conta Corrente"

        if self.tipo_conta == Conta.TIPO_CORRENTE and self.id_banco != conta_destino.id_banco:
            return False, "Conta Corrente não pode transferir para outro banco"

        if self.saldo < valor:
            return False, "Saldo insuficiente"

        self.saldo -= valor
        conta_destino.saldo += valor
        self.historico.append(f"Transferência de {valor:.2f} para conta {conta_destino.numero_conta}")
        conta_destino.historico.append(f"Recebimento de {valor:.2f} da conta {self.numero_conta}")
        return True, "Transferência realizada com sucesso"

    def extrato(self):
        return list(self.historico)

    def __repr__(self):
        return (f"Conta(numero={self.numero_conta}, tipo={self.tipo_conta}, "
                f"banco={self.id_banco}, saldo={self.saldo:.2f})")


class Banco:
    def __init__(self, id_banco, nome_banco, cnpj):
        self.id_banco = id_banco
        self.nome_banco = nome_banco
        self.cnpj = cnpj
        self.lista_agencias = []
        self.lista_contas = []

    def criar_agencia(self, detalhes):
        self.lista_agencias.append(detalhes)
        return detalhes

    def criar_conta(self, pessoa, tipo_conta):
        if not self.lista_agencias:
            return None, "Banco não possui agências cadastradas"

        numero_conta = len(self.lista_contas) + 1
        conta = Conta(numero_conta, self.lista_agencias[0], self.id_banco, pessoa.cpf, tipo_conta)
        self.lista_contas.append(conta)
        return conta, "Conta criada com sucesso"

    def __repr__(self):
        return f"Banco(id={self.id_banco}, nome={self.nome_banco})"


class Pessoa:
    def __init__(self, nome, cpf, telefone):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone

    def solicitar_conta(self, banco, tipo_conta):
        for conta in banco.lista_contas:
            if conta.cpf_pessoa == self.cpf and conta.tipo_conta == tipo_conta:
                return None, "Pessoa já possui uma conta desse tipo neste banco"

        return banco.criar_conta(self, tipo_conta)

    def __repr__(self):
        return f"Pessoa(nome={self.nome}, cpf={self.cpf})"
