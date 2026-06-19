"""
Testes unitários do StockFlow.

Estes testes não fazem nenhuma chamada real à API do Google Sheets:
o GoogleSheetsRepository é substituído (mock) para que o EstoqueController
seja testado de forma isolada.s

Execução:
    python -m unittest testes.py
"""

import unittest
from unittest.mock import patch, MagicMock

from produto import Produto
from controlador import EstoqueController


def criar_produto(sku, nome="Produto Teste", categoria="Geral",
                   quantidade=10, nivel_minimo=2, ativo=True, preco=9.90):
    """Helper para criar um Produto já com SKU definido (sem depender do repositório)."""
    return Produto(
        sku=sku,
        nome=nome,
        preco=preco,
        categoria=categoria,
        nivel_minimo=nivel_minimo,
        quantidade=quantidade,
        ativo=ativo,
    )


class TestRF05ListarProdutosAtivos(unittest.TestCase):
    """
    RF-05: O sistema deve listar todos os produtos ativos com SKU, nome,
    categoria, quantidade atual e nível mínimo.
    """

    @patch("controlador.GoogleSheetsRepository")
    def test_listar_retorna_campos_obrigatorios(self, MockRepo):
        """[Sucesso] A listagem deve retornar os campos obrigatórios corretamente."""
        produto_ativo = criar_produto(
            sku="SKU-001", nome="Mouse Gamer", categoria="Periféricos",
            quantidade=15, nivel_minimo=5, ativo=True
        )

        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.listar_todos.return_value = [produto_ativo]

        controlador = EstoqueController()
        produtos = controlador.listar_todos_produtos()

        self.assertEqual(len(produtos), 1)
        produto_retornado = produtos[0]

        # Os 5 campos exigidos pelo RF-05 devem estar acessíveis no objeto retornado
        self.assertEqual(produto_retornado.sku, "SKU-001")
        self.assertEqual(produto_retornado.nome, "Mouse Gamer")
        self.assertEqual(produto_retornado.categoria, "Periféricos")
        self.assertEqual(produto_retornado.quantidade, 15)
        self.assertEqual(produto_retornado.nivel_minimo, 5)

    @patch("controlador.GoogleSheetsRepository")
    def test_listar_exclui_inativos(self, MockRepo):
        """[Sucesso/Regra] Produtos inativos não devem aparecer na listagem principal."""
        produto_ativo = criar_produto(sku="SKU-001", nome="Teclado", ativo=True)
        produto_inativo = criar_produto(sku="SKU-002", nome="Mousepad", ativo=False)

        # O repositório, no mundo real, devolve tudo; quem filtra os
        # produtos ativos é a camada de listagem do controlador.
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.listar_todos.return_value = [produto_ativo, produto_inativo]

        controlador = EstoqueController()
        produtos = controlador.listar_todos_produtos()

        skus_retornados = [p.sku for p in produtos]
        self.assertIn("SKU-001", skus_retornados)
        self.assertNotIn(
            "SKU-002",
            skus_retornados,
            "RF-05: produtos inativos não devem aparecer na listagem.",
        )

    @patch("controlador.GoogleSheetsRepository")
    def test_listar_sem_produtos_retorna_lista_vazia(self, MockRepo):
        """[Borda] Se não houver produtos, o sistema não deve quebrar, apenas retornar lista vazia."""
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.listar_todos.return_value = []

        controlador = EstoqueController()
        produtos = controlador.listar_todos_produtos()

        self.assertEqual(produtos, [])

    @patch("controlador.GoogleSheetsRepository")
    def test_listar_falha_conexao_repositorio(self, MockRepo):
        """
        [Falha] Simula erro na API do Google Sheets.
        O Controlador deve repassar a exceção para que a View possa tratar amigavelmente.
        """
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.listar_todos.side_effect = RuntimeError("Falha de conexão com a API do Google Sheets")

        controlador = EstoqueController()

        with self.assertRaises(RuntimeError) as contexto:
            controlador.listar_todos_produtos()

        self.assertIn("Falha de conexão", str(contexto.exception))


class TestRF08SaidaComEstoqueInsuficiente(unittest.TestCase):
    """
    RF-08: O sistema deve rejeitar uma saída cuja quantidade solicitada
    exceda a quantidade disponível, exibindo mensagem de erro clara.
    """

    def test_atualizar_estoque_aceita_saida_dentro_do_limite(self):
        """[Sucesso] Saída válida deve ser processada e alterar o saldo corretamente."""
        produto = criar_produto(sku="SKU-011", nome="Cabo USB-C", quantidade=10)
        produto.atualizar_estoque(-6)
        self.assertEqual(produto.quantidade, 4)

    def test_atualizar_estoque_rejeita_saida_maior_que_disponivel(self):
        """[Falha] Saída maior que o estoque deve levantar erro com mensagem clara."""
        produto = criar_produto(sku="SKU-010", nome="Cabo HDMI", quantidade=4)

        with self.assertRaises(ValueError) as contexto:
            produto.atualizar_estoque(-6)

        mensagem = str(contexto.exception)
        self.assertIn("Cabo HDMI", mensagem)
        self.assertTrue(len(mensagem) > 0, "A mensagem de erro deve ser clara e não vazia.")

    def test_atualizar_estoque_nao_altera_quantidade_em_caso_de_rejeicao(self):
        """[Falha/Atomicidade] Se a saída for rejeitada, o saldo original deve ser preservado."""
        produto = criar_produto(sku="SKU-010", nome="Cabo HDMI", quantidade=4)

        with self.assertRaises(ValueError):
            produto.atualizar_estoque(-6)

        # Operação deve ser atômica: rejeitada => quantidade inalterada
        self.assertEqual(produto.quantidade, 4)

    @patch("controlador.GoogleSheetsRepository")
    def test_controlador_rejeita_saida_e_nao_persiste_movimentacao(self, MockRepo):
        """[Integração/Falha] Se a saída falhar no modelo, o controlador não deve acionar o repositório."""
        produto = criar_produto(sku="SKU-010", nome="Cabo HDMI", quantidade=4)

        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.buscar_por_sku.return_value = produto

        controlador = EstoqueController()

        with self.assertRaises(ValueError):
            controlador.realizar_movimentacao("SKU-010", -6)

        # Nenhuma atualização deve ser enviada ao repositório quando a saída é rejeitada
        mock_repo_instance.atualizar.assert_not_called()
        self.assertEqual(produto.quantidade, 4)

    def test_atualizar_estoque_aceita_saida_exata_zerando_estoque(self):
        """
        [Borda] A quantidade solicitada é exatamente igual ao saldo disponível.
        O sistema deve aceitar e o saldo final deve cravar em 0.
        """
        produto = criar_produto(sku="SKU-012", nome="Fonte 500W", quantidade=5)
        produto.atualizar_estoque(-5)
        self.assertEqual(produto.quantidade, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)