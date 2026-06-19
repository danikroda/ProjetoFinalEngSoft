from repository import GoogleSheetsRepository
from produto import Produto
from typing import List

class EstoqueController:
    def __init__(self):
        # O controlador instancia o repositório real
        self.__repo = GoogleSheetsRepository()

    def cadastrar_novo_produto(self, nome: str, preco: float, categoria: str, nivel_minimo: int) -> str:
        """Cria um novo produto, valida as regras e envia para a planilha."""
        novo_produto = Produto(
            nome=nome,
            preco=preco,
            categoria=categoria,
            nivel_minimo=nivel_minimo
        )
        self.__repo.salvar_novo(novo_produto)
        return novo_produto.sku

    def listar_todos_produtos(self) -> List[Produto]:
        """Recupera a lista de todos os produtos ativos cadastrados."""
        todos = self.__repo.listar_todos()
        return [produto for produto in todos if produto.ativo]

    def realizar_movimentacao(self, sku: str, quantidade: int) -> Produto:
        """Dá entrada (qtd positiva) ou saída (qtd negativa) no estoque de um produto."""
        produto = self.__repo.buscar_por_sku(sku)
        if not produto:
            raise ValueError(f"Erro: O SKU '{sku}' não foi encontrado no sistema.")
        
        produto.atualizar_estoque(quantidade)
        self.__repo.atualizar(produto)
        return produto

    def alterar_ativacao_produto(self, sku: str) -> Produto:
        """Ativa ou desativa um produto do catálogo (Exclusão lógica)."""
        produto = self.__repo.buscar_por_sku(sku)
        if not produto:
            raise ValueError(f"Erro: O SKU '{sku}' não foi encontrado no sistema.")
        
        produto.alternar_status()
        self.__repo.atualizar(produto)
        return produto

    def deletar_produto(self, sku: str) -> str:
        """Remove permanentemente um produto do sistema pelo SKU. Retorna o nome do produto deletado."""
        produto = self.__repo.buscar_por_sku(sku)
        if not produto:
            raise ValueError(f"Erro: O SKU '{sku}' não foi encontrado no sistema.")
        nome = produto.nome
        self.__repo.deletar(sku)
        return nome