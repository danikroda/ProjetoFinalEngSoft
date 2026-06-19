from repository import GoogleSheetsRepository
from produto import Produto
from typing import List

# Importando os elementos do Padrão Observer
from observadores import ObservadorEstoque, AlertaTerminalObserver, LogArquivoObserver

class EstoqueController:
    def __init__(self, repo=None):
        # Suporta tanto injeção de dependência (testes) quanto instanciar o real
        self.__repo = repo if repo else GoogleSheetsRepository()
        
        # --- Configuração do Padrão Observer ---
        self.__observadores: List[ObservadorEstoque] = []
        
        # Já inscreve os dois observadores automaticamente ao iniciar o sistema
        self.inscrever_observador(AlertaTerminalObserver())
        self.inscrever_observador(LogArquivoObserver())

    # Método para registrar novos observadores
    def inscrever_observador(self, observador: ObservadorEstoque) -> None:
        self.__observadores.append(observador)

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
        """Recupera a lista de produtos (aplica filtro de ativos se o RF-05 exigir na view)."""
        todos = self.__repo.listar_todos()
        # Filtra apenas os ativos para atender ao RF-05
        return [p for p in todos if p.ativo]

    def realizar_movimentacao(self, sku: str, quantidade: int) -> Produto:
        """Dá entrada (qtd positiva) ou saída (qtd negativa) no estoque de um produto."""
        produto = self.__repo.buscar_por_sku(sku)
        if not produto:
            raise ValueError(f"Erro: O SKU '{sku}' não foi encontrado no sistema.")
        
        # Altera o estado da entidade e salva
        produto.atualizar_estoque(quantidade)
        self.__repo.atualizar(produto)
        
        # --- Execução do Padrão Observer ---
        # Se foi uma saída de estoque e o produto atingiu o nível crítico
        if quantidade < 0 and produto.verificar_estoque_baixo():
            for observador in self.__observadores:
                observador.notificar_estoque_baixo(produto)
                
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
        """Coordena a exclusão de um produto se ele cumprir as regras de negócio."""
        produto = self.__repo.buscar_por_sku(sku)
        if not produto:
            raise ValueError(f"Erro: O SKU '{sku}' não foi encontrado no sistema.")
        
        # Regra de negócio exigiria um método 'pode_ser_deletado' ou apenas checar a quantidade
        if produto.quantidade > 0:
            raise ValueError(
                f"Erro de Negócio: Não é possível deletar o produto '{produto.nome}'. "
                f"Ainda existem {produto.quantidade} unidades no estoque. Zere o estoque antes."
            )
        
        self.__repo.deletar(sku)
        return produto.nome