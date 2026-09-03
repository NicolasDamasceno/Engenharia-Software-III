from models import Banco, Conta, Pessoa


def main():
    banco_a = Banco(id_banco=1, nome_banco="Banco A", cnpj="00.000.000/0001-00")
    banco_b = Banco(id_banco=2, nome_banco="Banco B", cnpj="11.111.111/0001-11")
    banco_a.criar_agencia({"numero": "0001", "cidade": "Recife"})
    banco_b.criar_agencia({"numero": "0002", "cidade": "Olinda"})

    joao = Pessoa(nome="João", cpf="111.111.111-11", telefone="81900000000")
    maria = Pessoa(nome="Maria", cpf="222.222.222-22", telefone="81911111111")

    conta_joao_corrente, msg = joao.solicitar_conta(banco_a, Conta.TIPO_CORRENTE)
    print(msg, conta_joao_corrente)

    conta_maria_poupanca, msg = maria.solicitar_conta(banco_a, Conta.TIPO_POUPANCA)
    print(msg, conta_maria_poupanca)

    conta_joao_corrente.depositar(500)
    print("Extrato João:", conta_joao_corrente.extrato())

    sucesso, msg = conta_maria_poupanca.transferir(conta_joao_corrente, 100)
    print(msg)

    sucesso, msg = conta_joao_corrente.transferir(conta_maria_poupanca, 50)
    print(msg)


if __name__ == "__main__":
    main()
