import csv
import os
import re


# Classe Pessoa
class Pessoa:
    def __init__(self, nome, idade, email, telefone, cpf):
        self.nome = nome
        self.idade = idade
        self.email = email
        self.telefone = telefone
        self.cpf = cpf

    def to_list(self):
        return [self.nome, self.idade, self.email, self.telefone, self.cpf]


# Classe CRUD
class CadastroPessoas:
    ARQUIVO = "pessoas.csv"

    def __init__(self):
        if not os.path.exists(self.ARQUIVO):
            with open(self.ARQUIVO, mode="w", newline="", encoding="utf-8") as f:
                escritor = csv.writer(f)
                escritor.writerow(["Nome", "Idade", "Email", "Telefone", "CPF"])

    def tem_registros(self):
        """Verifica se há algum registro além do cabeçalho."""
        with open(self.ARQUIVO, mode="r", encoding="utf-8") as f:
            leitor = csv.reader(f)
            linhas = list(leitor)
            return len(linhas) > 1

    def adicionar(self, pessoa: Pessoa):
        with open(self.ARQUIVO, mode="a", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(pessoa.to_list())
        print("✅ Pessoa cadastrada com sucesso!")

    def listar(self):
        with open(self.ARQUIVO, mode="r", encoding="utf-8") as f:
            leitor = csv.reader(f)
            registros_encontrados = False
            for i, linha in enumerate(leitor):
                if i == 0:
                    continue

                registros_encontrados = True
                nome = linha[0] if len(linha) > 0 else ""
                idade = linha[1] if len(linha) > 1 else ""
                email = linha[2] if len(linha) > 2 else ""
                telefone = linha[3] if len(linha) > 3 else ""
                cpf = linha[4] if len(linha) > 4 else ""

                print(f"Nome: {nome} | Idade: {idade} | Email: {email} | Telefone: {telefone} | CPF: {cpf}")

            if not registros_encontrados:
                print("Nenhum registro encontrado no momento.")

    def atualizar(self, email_busca, novo_nome, nova_idade, novo_telefone, novo_cpf):
        linhas = []
        atualizado = False
        with open(self.ARQUIVO, mode="r", encoding="utf-8") as f:
            leitor = csv.reader(f)
            for linha in leitor:
                if linha and len(linha) >= 3 and linha[2] == email_busca:
                    while len(linha) < 5:
                        linha.append("")

                    linha[0] = novo_nome
                    linha[1] = nova_idade
                    linha[3] = novo_telefone
                    linha[4] = novo_cpf

                    atualizado = True
                linhas.append(linha)

        with open(self.ARQUIVO, mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerows(linhas)

        if atualizado:
            print("✅ Cadastro atualizado com sucesso!")
        else:
            print("⚠️ Pessoa não encontrada.")

    def excluir(self, email):
        linhas = []
        excluido = False
        with open(self.ARQUIVO, mode="r", encoding="utf-8") as f:
            leitor = csv.reader(f)
            for linha in leitor:
                if linha and len(linha) >= 3 and linha[2] != email:
                    linhas.append(linha)
                elif linha and len(linha) >= 3 and linha[2] == email:
                    excluido = True

        with open(self.ARQUIVO, mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerows(linhas)

        if excluido:
            print("🗑️ Pessoa excluída com sucesso!")
        else:
            print("⚠️ Pessoa não encontrada.")

    def excluir_todos(self):
        with open(self.ARQUIVO, mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(["Nome", "Idade", "Email", "Telefone", "CPF"])
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


# ============================
# Menu
# ============================
def menu():
    cadastro = CadastroPessoas()

    while True:
        print("\n--- MENU ---")
        print("1 - Cadastrar Pessoa")
        print("2 - Listar Pessoas")
        print("3 - Atualizar Pessoa")
        print("4 - Excluir Pessoa")
        print("5 - Excluir TODA a Lista (Admin)")
        print("6 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = ler_nome("Nome: ")
            idade = ler_idade("Idade: ")
            email = ler_email("Email: ")
            telefone = ler_telefone("Telefone: ")
            cpf = ler_cpf("CPF: ")

            pessoa = Pessoa(nome, idade, email, telefone, cpf)
            cadastro.adicionar(pessoa)

        elif opcao == "2":
            print("\n--- Lista de Pessoas ---")
            cadastro.listar()

        elif opcao == "3":
            if not cadastro.tem_registros():
                print("❌ Não há registros cadastrados para atualizar.")
                continue

            email_busca = ler_email("Digite o email da pessoa que deseja atualizar: ")
            print("\nPreencha os novos dados da pessoa:")

            novo_nome = ler_nome("Novo nome: ")
            nova_idade = ler_idade("Nova idade: ")
            novo_telefone = ler_telefone("Novo telefone: ")
            novo_cpf = ler_cpf("Novo CPF: ")

            cadastro.atualizar(email_busca, novo_nome, nova_idade, novo_telefone, novo_cpf)

        elif opcao == "4":
            if not cadastro.tem_registros():
                print("❌ Não há registros cadastrados para excluir.")
                continue

            email = ler_email("Digite o email da pessoa que deseja excluir: ")

            while True:
                confirmacao = input(f"Tem certeza que deseja excluir o registro de {email}? (S/N): ").strip().upper()
                if confirmacao in ['S', 'N']:
                    break
                print("❌ Resposta inválida. Digite 'S' para sim ou 'N' para não.")

            if confirmacao == 'S':
                cadastro.excluir(email)
            else:
                print("❌ Operação de exclusão cancelada.")

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
                    print("❌ Operação de exclusão em massa cancelada.")
            else:
                print("❌ Senha incorreta! Acesso negado.")

        elif opcao == "6":
            print("👋 Saindo do sistema...")
            break
        else:
            print("❌ Opção inválida, tente novamente.")


if __name__ == "__main__":
    menu()
