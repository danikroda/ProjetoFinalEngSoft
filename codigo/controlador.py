from repository import GoogleSheetsRepository
from produto import Produto
from typing import List

class EstoqueController:
    def __init__(self):
        # O controlador instancia o repositório real
        self.__repo = GoogleSheetsRepository()

    def cadastrar_novo_produto(self, nome: str, preco: float, categoria: str, nivel_minimo: int) -> str:
        """Cria um novo produto, valida as regras e envia para a planilha."""
        # Cria a entidade (o construtor já roda as validações internas)
        novo_produto = Produto(
            nome=nome,
            preco=preco,
            categoria=categoria,
            nivel_minimo=nivel_minimo
        )
        # Salva na API do Google Sheets
        self.__repo.salvar_novo(novo_produto)
        # Retorna o SKU gerado para a View mostrar na tela
        return novo_produto.sku

    def listar_todos_produtos(self) -> List[Produto]:
        """Recupera a lista de todos os produtos cadastrados."""
        return self.__repo.listar_todos()

    def realizar_movimentacao(self, sku: str, quantidade: int) -> Produto:
        """Dá entrada (qtd positiva) ou saída (qtd negativa) no estoque de um produto."""
        produto = self.__repo.buscar_por_sku(sku)
        if not produto:
            raise ValueError(f"Erro: O SKU '{sku}' não foi encontrado no sistema.")
        
        # Altera o estado da entidade (dispara erro se tentar tirar mais do que tem)
        produto.atualizar_estoque(quantidade)
        
        # Se a regra de negócio aceitou, atualiza a linha correspondente na planilha
        self.__repo.atualizar(produto)
        return produto

    def alterar_ativacao_produto(self, sku: str) -> Produto:
        """Ativa ou desativa um produto do catálogo (Exclusão lógica)."""
        produto = self.__repo.buscar_por_sku(sku)
        if not produto:
            raise ValueError(f"Erro: O SKU '{sku}' não foi encontrado no sistema.")
        
        # Executa a regra interna do modelo
        produto.alternar_status()
        
        # Salva a alteração na planilha
        self.__repo.atualizar(produto)
        return produto