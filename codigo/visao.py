import sys
from controlador import EstoqueController

class EstoqueView:
    def __init__(self, controlador: EstoqueController):
        self.__controlador = controlador

    def __exibir_menu_principal(self):
        print("\n" + "="*45)
        print("     📦 STOCKFLOW - GERENCIAMENTO DE ESTOQUE 📦")
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

            if opcao == "1":
                self.__menu_cadastrar()
            elif opcao == "2":
                self.__menu_listar()
            elif opcao == "3":
                self.__menu_movimentar()
            elif opcao == "4":
                self.__menu_alternar_status()
            elif opcao == "5":
                self.__menu_deletar()
            elif opcao == "6":
                print("\nShutting down StockFlow... Fechando conexão com a API.")
                print("Até logo, Michel!")
                break
            else:
                print("\n⚠️ Opção inválida! Digite um número de 1 a 6.")

    def __menu_cadastrar(self):
        print("\n--- 📝 CADASTRAR NOVO PRODUTO ---")
        try:
            nome = input("Nome do produto: ").strip()
            preco = float(input("Preço unitário: R$ "))
            categoria = input("Categoria do produto: ").strip()
            minimo = int(input("Nível mínimo de segurança: "))
            
            sku = self.__controlador.cadastrar_novo_produto(nome, preco, categoria, minimo)
            print(f"\n🎉 [Sucesso] Produto cadastrado! SKU gerado: {sku}")
        except ValueError as e:
            print(f"\n⚠️ [Erro de Validação]: {e}")
        except Exception as e:
            print(f"\n❌ [Erro de Sistema]: {e}")

    def __menu_listar(self):
        print("\n--- 📋 ESTOQUE ATUAL DO GOOGLE SHEETS ---")
        try:
            produtos = self.__controlador.listar_todos_produtos()
            if not produtos:
                print("Nenhum produto encontrado na planilha.")
                return
            
            print(f"{'SKU':<15} | {'Nome':<20} | {'Qtd':<6} | {'Mín':<5} | {'Preço':<10} | Status")
            print("-" * 75)
            for p in produtos:
                status_ativo = "Ativo" if p.ativo else "Inativo"
                alerta = "⚠️ [ESTOQUE BAIXO]" if p.verificar_estoque_baixo() and p.ativo else ""
                print(f"{p.sku:<15} | {p.nome:<20} | {p.quantidade:<6} | {p.nivel_minimo:<5} | R${p.preco:<8.2f} | {status_ativo} {alerta}")
        except Exception as e:
            print(f"\n❌ [Erro ao listar]: {e}")

    def __menu_movimentar(self):
        print("\n--- 🔄 MOVIMENTAR ESTOQUE ---")
        sku = input("Digite o SKU do produto: ").strip().upper()
        print("💡 Dica: Use números positivos para ENTRADA (ex: 10) e negativos para SAÍDA (ex: -5)")
        try:
            qtd = int(input("Quantidade da movimentação: "))
            prod_atualizado = self.__controlador.realizar_movimentacao(sku, qtd)
            print(f"\n✅ [Sucesso] {prod_atualizado.nome} atualizado! Novo saldo: {prod_atualizado.quantidade}")
        except ValueError as e:
            print(f"\n⚠️ [Regra de Negócio Violada]: {e}")
        except Exception as e:
            print(f"\n❌ [Erro]: {e}")

    def __menu_alternar_status(self):
        print("\n--- 🚫 ALTERNAR STATUS DO PRODUTO ---")
        sku = input("Digite o SKU do produto para ativar/desativar: ").strip().upper()
        try:
            prod_atualizado = self.__controlador.alterar_ativacao_produto(sku)
            status_final = "ATIVADO" if prod_atualizado.ativo else "DESATIVADO"
            print(f"\n✅ [Sucesso] O produto {prod_atualizado.nome} agora está {status_final}!")
        except Exception as e:
            print(f"\n❌ [Erro]: {e}")

    def __menu_deletar(self):
        print("\n--- 🗑️  DELETAR PRODUTO ---")
        print("⚠️  Atenção: esta ação é permanente e não pode ser desfeita.")
        print("    Para desativar sem perder histórico, use a opção 4.")
        sku = input("Digite o SKU do produto a deletar (ou Enter para cancelar): ").strip().upper()
        if not sku:
            print("Operação cancelada.")
            return
        confirmacao = input(f"Confirma a exclusão do produto '{sku}'? (s/N): ").strip().lower()
        if confirmacao != "s":
            print("Operação cancelada.")
            return
        try:
            nome = self.__controlador.deletar_produto(sku)
            print(f"\n✅ [Sucesso] Produto '{nome}' ({sku}) removido permanentemente.")
        except ValueError as e:
            print(f"\n⚠️ [Erro]: {e}")
        except Exception as e:
            print(f"\n❌ [Erro de Sistema]: {e}")