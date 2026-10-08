import json
import os
import re
from datetime import datetime


# ============================
# Classes de Domínio
# ============================

class Emprestimo:
    def __init__(self, valor, pendente=True):
        self.valor = float(valor)
        self.pendente = pendente

    def to_dict(self):
        return {"valor": self.valor, "pendente": self.pendente}

    @classmethod
    def from_dict(cls, data):
        return cls(data["valor"], data["pendente"])


class Cliente:
    def __init__(self, nome, idade, email, telefone, cpf, profissao, data_inicio_profissao, empregado_atualmente,
                 salario_atual, emprestimos=None):
        self.nome = nome
        self.idade = idade
        self.email = email
        self.telefone = telefone
        self.cpf = cpf
        self.profissao = profissao
        self.data_inicio_profissao = data_inicio_profissao
        self.empregado_atualmente = empregado_atualmente
        self.salario_atual = float(salario_atual)
        self.emprestimos = emprestimos if emprestimos is not None else []

    def calcular_limite_emprestimo(self):
        # 1. Validação de Regras Antigas (Máx 2 empréstimos e Dívida < 10.000)
        emprestimos_pendentes = [e for e in self.emprestimos if e.pendente]
        if len(emprestimos_pendentes) >= 2:
            return 0.0, "Possui 2 ou mais empréstimos pendentes."

        divida_total = sum(e.valor for e in emprestimos_pendentes)
        if divida_total >= 10000.00:
            return 0.0, "Dívida total atingiu o limite máximo do banco (R$ 10.000,00)."

        # 2. Validação de Emprego e Tempo de Trabalho
        if not self.empregado_atualmente:
            return 0.0, "Cliente não está empregado atualmente."

        try:
            inicio = datetime.strptime(self.data_inicio_profissao, "%d/%m/%Y")
            hoje = datetime.now()
            meses_trabalho = (hoje.year - inicio.year) * 12 + hoje.month - inicio.month
            if hoje.day < inicio.day:
                meses_trabalho -= 1
        except ValueError:
            return 0.0, "Erro ao calcular tempo de profissão."

        if meses_trabalho <= 6:
            return 0.0, "Tempo de trabalho insuficiente (mínimo de 6 meses exigido)."

        # 3. Regra dos 30% do Salário
        limite_total_teorico = self.salario_atual * 0.30

        # O limite disponível é o teto de 30% menos o que ele já deve
        limite_disponivel = limite_total_teorico - divida_total

        # Limita a R$ 10.000,00 caso os 30% do salário sejam astronômicos
        if limite_disponivel + divida_total > 10000.00:
            limite_disponivel = 10000.00 - divida_total

        if limite_disponivel <= 0:
            return 0.0, "Limite de crédito totalmente comprometido por dívidas ativas."

        return limite_disponivel, "Apto"

    def adicionar_emprestimo(self, valor):
        limite_disponivel, motivo = self.calcular_limite_emprestimo()

        if limite_disponivel == 0.0:
            print(f"❌ Empréstimo negado! Motivo: {motivo}")
            return False

        if valor > limite_disponivel:
            print(f"❌ Empréstimo negado! O valor solicitado excede o seu limite aprovado (R$ {limite_disponivel:.2f}).")
            return False

        novo_emprestimo = Emprestimo(valor)
        self.emprestimos.append(novo_emprestimo)
        print(f"✅ Empréstimo de R$ {valor:.2f} aprovado e registrado com sucesso!")
        return True

    def realizar_pagamento(self, valor_pagamento):
        if valor_pagamento <= 0:
            return False, "O valor do pagamento deve ser maior que zero."

        emprestimos_pendentes = [e for e in self.emprestimos if e.pendente]
        if not emprestimos_pendentes:
            return False, "O cliente não possui empréstimos pendentes."

        valor_restante = valor_pagamento

        # Paga os empréstimos abatendo do mais antigo para o mais novo
        for emp in emprestimos_pendentes:
            if valor_restante <= 0:
                break

            if valor_restante >= emp.valor:
                # Quita este empréstimo por completo
                valor_restante -= emp.valor
                emp.valor = 0.0
                emp.pendente = False
            else:
                # Abate apenas uma parte do empréstimo
                emp.valor -= valor_restante
                valor_restante = 0.0

        return True, valor_restante

    def to_dict(self):
        return {
            "nome": self.nome,
            "idade": self.idade,
            "email": self.email,
            "telefone": self.telefone,
            "cpf": self.cpf,
            "profissao": self.profissao,
            "data_inicio_profissao": self.data_inicio_profissao,
            "empregado_atualmente": self.empregado_atualmente,
            "salario_atual": self.salario_atual,
            "emprestimos": [e.to_dict() for e in self.emprestimos]
        }

    @classmethod
    def from_dict(cls, data):
        emprestimos = [Emprestimo.from_dict(e) for e in data.get("emprestimos", [])]
        return cls(
            data["nome"],
            data["idade"],
            data["email"],
            data["telefone"],
            data["cpf"],
            data.get("profissao", "Não informada"),
            data.get("data_inicio_profissao", datetime.now().strftime("%d/%m/%Y")),
            data.get("empregado_atualmente", False),
            data.get("salario_atual", 0.0),
            emprestimos
        )


# ============================
# Classe de Persistência (CRUD)
# ============================
class CadastroClientes:
    ARQUIVO = "clientes.json"

    def __init__(self):
        if not os.path.exists(self.ARQUIVO):
            with open(self.ARQUIVO, mode="w", encoding="utf-8") as f:
                json.dump([], f)

    def _ler_dados(self):
        try:
            with open(self.ARQUIVO, mode="r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _salvar_dados(self, dados):
        with open(self.ARQUIVO, mode="w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    def tem_registros(self):
        return len(self._ler_dados()) > 0

    def adicionar(self, cliente: Cliente):
        dados = self._ler_dados()
        if any(c["email"] == cliente.email for c in dados):
            print("⚠️ Já existe um cliente cadastrado com este e-mail.")
            return
        dados.append(cliente.to_dict())
        self._salvar_dados(dados)
        print("✅ Cliente cadastrado com sucesso!")

    def listar(self):
        dados = self._ler_dados()
        if not dados:
            print("Nenhum registro encontrado no momento.")
            return

        for data in dados:
            cliente = Cliente.from_dict(data)
            limite, motivo = cliente.calcular_limite_emprestimo()
            status_apto = f"Sim (Limite Disp: R$ {limite:.2f})" if limite > 0 else f"Não ({motivo})"
            divida = sum(e.valor for e in cliente.emprestimos if e.pendente)
            pendentes = len([e for e in cliente.emprestimos if e.pendente])

            print(
                f"Nome: {cliente.nome} | Email: {cliente.email} | Profissão: {cliente.profissao} | Salário: R$ {cliente.salario_atual:.2f}")
            print(f"   -> Empréstimos pendentes: {pendentes} | Dívida Total: R$ {divida:.2f}")
            print(f"   -> Apto para novo empréstimo? {status_apto}")
            print("-" * 70)

    def solicitar_emprestimo(self, email_busca, valor):
        dados = self._ler_dados()
        for i, data in enumerate(dados):
            if data["email"] == email_busca:
                cliente = Cliente.from_dict(data)
                if cliente.adicionar_emprestimo(valor):
                    dados[i] = cliente.to_dict()
                    self._salvar_dados(dados)
                return
        print("⚠️ Cliente não encontrado.")

    def pagar_emprestimo(self, email_busca, valor_pagamento):
        dados = self._ler_dados()
        for i, data in enumerate(dados):
            if data["email"] == email_busca:
                cliente = Cliente.from_dict(data)

                sucesso, retorno = cliente.realizar_pagamento(valor_pagamento)

                if sucesso:
                    dados[i] = cliente.to_dict()
                    self._salvar_dados(dados)
                    print(f"✅ Pagamento processado com sucesso!")
                    if retorno > 0:
                        print(f"⚠️ O valor pago foi maior que a dívida. Sobrou um troco de: R$ {retorno:.2f}")
                else:
                    print(f"❌ Não foi possível realizar o pagamento: {retorno}")
                return
        print("⚠️ Cliente não encontrado.")

    def excluir_todos(self):
        self._salvar_dados([])
        print("🚨 TODOS os registros foram apagados com sucesso!")


# ============================
# Funções de Validação de Dados
# ============================
def ler_nome(prompt):
    while True:
        valor = input(prompt).strip()
        if valor and not valor.isdigit():
            return valor
        print("❌ Nome inválido. O campo não pode ficar vazio ou conter apenas números.")


def ler_idade(prompt):
    while True:
        valor = input(prompt).strip()
        if valor.isdigit() and 0 <= int(valor) <= 100:
            return valor
        print("❌ Idade inválida. Digite apenas números entre 0 e 100.")


def ler_email(prompt):
    while True:
        valor = input(prompt).strip()
        padrao_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(padrao_email, valor):
            return valor
        print("❌ E-mail inválido. Use o formato: exemplo@dominio.com")


def ler_telefone(prompt):
    while True:
        valor = input(prompt).strip()
        valor_limpo = valor.replace(" ", "").replace("-", "")
        if valor_limpo.isdigit() and len(valor_limpo) >= 8:
            return valor_limpo
        print("❌ Telefone inválido. Digite apenas números (mínimo 8 dígitos).")


def ler_cpf(prompt):
    while True:
        valor = input(prompt).strip()
        if valor.isdigit() and len(valor) == 11 and " " not in valor:
            return valor
        print("❌ CPF inválido. Digite apenas números, sem espaços, com exatamente 11 dígitos.")


def ler_valor(prompt):
    while True:
        valor = input(prompt).strip().replace(",", ".")
        try:
            valor_float = float(valor)
            if valor_float > 0:
                return valor_float
            print("❌ O valor deve ser maior que zero.")
        except ValueError:
            print("❌ Valor inválido. Digite um número válido.")


def ler_data(prompt):
    while True:
        valor = input(prompt).strip()
        try:
            datetime.strptime(valor, "%d/%m/%Y")
            return valor
        except ValueError:
            print("❌ Data inválida. Use o formato: DD/MM/AAAA (ex: 15/04/2022)")


def ler_booleano(prompt):
    while True:
        valor = input(prompt).strip().upper()
        if valor in ['S', 'SIM']:
            return True
        elif valor in ['N', 'NAO', 'NÃO']:
            return False
        print("❌ Resposta inválida. Digite 'S' para Sim ou 'N' para Não.")


# ============================
# Menu Principal
# ============================
def menu():
    cadastro = CadastroClientes()

    while True:
        print("\n--- SISTEMA DE GESTÃO DE EMPRÉSTIMOS ---")
        print("1 - Cadastrar Cliente")
        print("2 - Listar Clientes e Status de Empréstimo")
        print("3 - Solicitar Novo Empréstimo")
        print("4 - Realizar Pagamento de Empréstimo (Quitar / Abater)")
        print("5 - Excluir TODA a Lista (Admin)")
        print("6 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = ler_nome("Nome: ")
            idade = ler_idade("Idade: ")
            email = ler_email("Email: ")
            telefone = ler_telefone("Telefone: ")
            cpf = ler_cpf("CPF: ")

            profissao = input("Profissão: ").strip()
            data_inicio = ler_data("Data de início na profissão (DD/MM/AAAA): ")
            empregado = ler_booleano("Está empregado atualmente? (S/N): ")
            salario = ler_valor("Salário atual: R$ ") if empregado else 0.0

            cliente = Cliente(nome, idade, email, telefone, cpf, profissao, data_inicio, empregado, salario)
            cadastro.adicionar(cliente)

        elif opcao == "2":
            print("\n--- Lista de Clientes ---")
            cadastro.listar()

        elif opcao == "3":
            if not cadastro.tem_registros():
                print("❌ Não há clientes cadastrados.")
                continue

            email_busca = ler_email("Digite o email do cliente: ")
            valor = ler_valor("Digite o valor do empréstimo (Ex: 1500.00): R$ ")
            cadastro.solicitar_emprestimo(email_busca, valor)

        elif opcao == "4":
            if not cadastro.tem_registros():
                print("❌ Não há clientes cadastrados.")
                continue

            email_busca = ler_email("Digite o email do cliente: ")
            valor_pagamento = ler_valor("Digite o valor que deseja pagar/abater da dívida: R$ ")
            cadastro.pagar_emprestimo(email_busca, valor_pagamento)

        elif opcao == "5":
            if not cadastro.tem_registros():
                print("❌ A lista já está vazia. Não há nada para excluir.")
                continue

            print("\n⚠️  ÁREA RESTRITA ⚠️")
            senha = input("Digite a senha de administrador: ")

            if senha == "1234":
                while True:
                    confirmacao = input(
                        "ATENÇÃO: Você está prestes a apagar TODOS os registros da base. Tem certeza? (S/N): ").strip().upper()
                    if confirmacao in ['S', 'N']:
                        break
                    print("❌ Resposta inválida. Digite 'S' para sim ou 'N' para não.")

                if confirmacao == 'S':
                    cadastro.excluir_todos()
                else:
                    print("❌ Operação cancelada.")
            else:
                print("❌ Senha incorreta! Acesso negado.")

        elif opcao == "6":
            print("👋 Saindo do sistema...")
            break
        else:
            print("❌ Opção inválida, tente novamente.")


if __name__ == "__main__":
    menu()
