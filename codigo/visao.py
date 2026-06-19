import sys
from controlador import EstoqueController

# Importa os comandos isolados
from comandos import (
    ComandoCadastrar,
    ComandoListar,
    ComandoMovimentar,
    ComandoAlternarStatus,
    ComandoDeletar
)

class EstoqueView:
    def __init__(self, controlador: EstoqueController):
        self.__controlador = controlador
        
        # Mapeamento do Padrão Command: Dicionário de opções x Comandos
        self.__comandos = {
            "1": ComandoCadastrar(self.__controlador),
            "2": ComandoListar(self.__controlador),
            "3": ComandoMovimentar(self.__controlador),
            "4": ComandoAlternarStatus(self.__controlador),
            "5": ComandoDeletar(self.__controlador)
        }

    def __exibir_menu_principal(self):
        print("\n" + "="*45)
        print("    📦 STOCKFLOW - GERENCIAMENTO DE ESTOQUE 📦")
        print("="*45)
        print(" 1. ➕ Cadastrar Novo Produto")
        print(" 2. 📋 Listar Estoque Atual")
        print(" 3. 🔄 Dar Entrada / Saída no Estoque")
        print(" 4. 🚫 Alternar Status (Ativar/Desativar)")
        print(" 5. 🗑️  Deletar Produto")
        print(" 6. ❌ Sair")
        print("="*45)

    def iniciar(self):
        while True:
            self.__exibir_menu_principal()
            opcao = input("Escolha uma opção (1-6): ").strip()

            # Trata a saída do sistema separadamente, pois encerra o loop
            if opcao == "6":
                print("\nShutting down StockFlow... Fechando conexão com a API.")
                print("Até logo, Michel!")
                break

            # Execução do Padrão Command
            comando = self.__comandos.get(opcao)
            if comando:
                comando.executar()
            else:
                print("\n⚠️ Opção inválida! Digite um número de 1 a 6.")