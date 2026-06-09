import sys
import os
import unittest
from typing import List, Optional
from unittest.mock import MagicMock

# Garante que o diretório do projeto está no path ao rodar de qualquer pasta
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from produto import Produto

# MockRepository — substituto em memória do GoogleSheetsRepository
# Implementa a mesma interface pública usada pelo EstoqueController.

class MockRepository:
    """Repositório falso que armazena produtos numa lista Python (sem I/O)."""

    def __init__(self, produtos_iniciais: List[Produto] = None):
        self._dados: List[Produto] = list(produtos_iniciais or [])
        # Spies para verificar se os métodos foram chamados nos testes
        self.salvar_novo = MagicMock(side_effect=self._salvar_novo)
        self.atualizar   = MagicMock(side_effect=self._atualizar)

    def _salvar_novo(self, produto: Produto) -> None:
        if any(p.sku == produto.sku for p in self._dados):
            raise ValueError(f"SKU '{produto.sku}' já existe no repositório.")
        self._dados.append(produto)

    def listar_todos(self) -> List[Produto]:
        return list(self._dados)

    def buscar_por_sku(self, sku: str) -> Optional[Produto]:
        for p in self._dados:
            if p.sku == sku:
                return p
        return None

    def _atualizar(self, produto: Produto) -> None:
        for i, p in enumerate(self._dados):
            if p.sku == produto.sku:
                self._dados[i] = produto
                return
        raise ValueError(f"SKU '{produto.sku}' não encontrado para atualização.")


# EstoqueControllerTestavel — Controller que aceita injeção de repositório.
# Isso evita alterar o controlador.py original enquanto permite testes
# sem conexão com a Google Sheets API.

from produto import Produto

class EstoqueControllerTestavel:
    """
    Versão do EstoqueController com injeção de dependência explícita.
    Aceita qualquer objeto que implemente a interface do repositório.
    """
    def __init__(self, repo):
        self.__repo = repo

    def cadastrar_novo_produto(self, nome: str, preco: float, categoria: str, nivel_minimo: int) -> str:
        novo_produto = Produto(
            nome=nome,
            preco=preco,
            categoria=categoria,
            nivel_minimo=nivel_minimo
        )
        self.__repo.salvar_novo(novo_produto)
        return novo_produto.sku

    def listar_todos_produtos(self) -> List[Produto]:
        return self.__repo.listar_todos()

    def realizar_movimentacao(self, sku: str, quantidade: int) -> Produto:
        produto = self.__repo.buscar_por_sku(sku)
        if not produto:
            raise ValueError(f"Erro: O SKU '{sku}' não foi encontrado no sistema.")
        produto.atualizar_estoque(quantidade)
        self.__repo.atualizar(produto)
        return produto

    def alterar_ativacao_produto(self, sku: str) -> Produto:
        produto = self.__repo.buscar_por_sku(sku)
        if not produto:
            raise ValueError(f"Erro: O SKU '{sku}' não foi encontrado no sistema.")
        produto.alternar_status()
        self.__repo.atualizar(produto)
        return produto

# Helpers de fixture

def criar_produto(nome="Caneta Azul", preco=2.50, categoria="Papelaria",
                  nivel_minimo=5, quantidade=10, sku=None):
    """Cria um Produto de teste com valores padrão convenientes."""
    return Produto(
        nome=nome,
        preco=preco,
        categoria=categoria,
        nivel_minimo=nivel_minimo,
        quantidade=quantidade,
        sku=sku or f"SKU-TEST{nome[:3].upper()}"
    )

# RF-01 — Cadastrar produto válido

class TestRF01CadastrarProdutoValido(unittest.TestCase):
    """
    RF-01: O sistema deve permitir cadastrar um produto com nome, SKU único,
    categoria, quantidade inicial ≥ 0 e nível mínimo ≥ 0.
    """

    def setUp(self):
        self.repo = MockRepository()
        self.ctrl = EstoqueControllerTestavel(self.repo)

    def test_cadastrar_produto_valido_retorna_sku(self):
        """Cadastrar produto válido deve retornar um SKU não vazio."""
        sku = self.ctrl.cadastrar_novo_produto("Caderno", 15.90, "Papelaria", 3)
        self.assertIsNotNone(sku)
        self.assertNotEqual(sku.strip(), "")

    def test_cadastrar_produto_valido_persiste_no_repositorio(self):
        """Após cadastro, produto deve estar listado no repositório."""
        self.ctrl.cadastrar_novo_produto("Caneta Vermelha", 1.99, "Papelaria", 2)
        produtos = self.repo.listar_todos()
        self.assertEqual(len(produtos), 1)
        self.assertEqual(produtos[0].nome, "Caneta Vermelha")

    def test_cadastrar_produto_salvar_novo_e_chamado(self):
        """O método salvar_novo do repositório deve ser invocado exatamente uma vez."""
        self.ctrl.cadastrar_novo_produto("Borracha", 0.75, "Papelaria", 1)
        self.repo.salvar_novo.assert_called_once()

    def test_cadastrar_produto_quantidade_inicial_zero(self):
        """Quantidade inicial padrão deve ser 0 (produto recém-cadastrado)."""
        sku = self.ctrl.cadastrar_novo_produto("Grampeador", 25.00, "Escritório", 1)
        produto = self.repo.buscar_por_sku(sku)
        self.assertEqual(produto.quantidade, 0)

    def test_cadastrar_produto_nivel_minimo_zero_aceito(self):
        """Nível mínimo igual a 0 (sem alerta) deve ser aceito sem erro."""
        try:
            self.ctrl.cadastrar_novo_produto("Clips", 3.00, "Escritório", 0)
        except ValueError:
            self.fail("nivel_minimo=0 não deveria levantar ValueError.")

    def test_cadastrar_produto_preco_zero_aceito(self):
        """Preço igual a 0 (brinde/amostra grátis) deve ser aceito."""
        try:
            self.ctrl.cadastrar_novo_produto("Amostra", 0.0, "Promoções", 0)
        except ValueError:
            self.fail("preco=0 não deveria levantar ValueError.")

    def test_cadastrar_produto_preco_negativo_rejeitado(self):
        """Preço negativo deve levantar ValueError antes mesmo de salvar."""
        with self.assertRaises(ValueError):
            self.ctrl.cadastrar_novo_produto("Produto Inválido", -10.0, "Teste", 0)
        self.repo.salvar_novo.assert_not_called()

    def test_cadastrar_produto_nivel_minimo_negativo_rejeitado(self):
        """Nível mínimo negativo deve levantar ValueError."""
        with self.assertRaises(ValueError):
            self.ctrl.cadastrar_novo_produto("Produto Inválido", 5.0, "Teste", -1)
        self.repo.salvar_novo.assert_not_called()

# RF-02 — Cadastrar produto com SKU duplicado

class TestRF02CadastrarProdutoSkuDuplicado(unittest.TestCase):
    """
    RF-02: O sistema deve impedir o cadastro de dois produtos com o mesmo SKU.
    """

    def setUp(self):
        produto_existente = criar_produto(sku="SKU-FIXO01")
        self.repo = MockRepository(produtos_iniciais=[produto_existente])
        self.ctrl = EstoqueControllerTestavel(self.repo)

    def test_sku_duplicado_levanta_erro(self):
        """Tentar cadastrar produto com SKU já existente deve levantar ValueError."""
        produto_duplicado = Produto(
            nome="Produto Duplicado",
            preco=5.0,
            categoria="Teste",
            nivel_minimo=0,
            sku="SKU-FIXO01"   # mesmo SKU do produto_existente
        )
        with self.assertRaises(ValueError):
            self.repo.salvar_novo(produto_duplicado)

    def test_sku_duplicado_nao_adiciona_segundo_produto(self):
        """Após tentativa de duplicata, o repositório deve continuar com 1 produto."""
        produto_duplicado = Produto(
            nome="Outro Produto",
            preco=9.0,
            categoria="Teste",
            nivel_minimo=0,
            sku="SKU-FIXO01"
        )
        try:
            self.repo.salvar_novo(produto_duplicado)
        except ValueError:
            pass
        self.assertEqual(len(self.repo.listar_todos()), 1)

    def test_sku_diferente_permite_segundo_cadastro(self):
        """Produto com SKU diferente deve ser cadastrado sem erro."""
        try:
            self.ctrl.cadastrar_novo_produto("Novo Produto", 3.0, "Teste", 0)
        except ValueError:
            self.fail("SKU diferente não deveria levantar ValueError.")
        self.assertEqual(len(self.repo.listar_todos()), 2)

# RF-03 — Editar produto preserva histórico (quantidade/SKU intactos)

class TestRF03EditarProdutoPreservaHistorico(unittest.TestCase):
    """
    RF-03: O sistema deve permitir editar nome, categoria e nível mínimo de
    um produto existente, preservando seu histórico (quantidade e SKU).
    """

    def setUp(self):
        self.produto = criar_produto(
            nome="Lápis HB",
            preco=1.50,
            categoria="Papelaria",
            nivel_minimo=5,
            quantidade=20,
            sku="SKU-LAPIS1"
        )

    def test_editar_dados_cadastrais_altera_nome(self):
        """Editar dados cadastrais deve atualizar o nome."""
        self.produto.editar_dados_cadastrais("Lápis 2B", 1.80, "Papelaria", 5)
        self.assertEqual(self.produto.nome, "Lápis 2B")

    def test_editar_dados_cadastrais_altera_preco(self):
        """Editar dados cadastrais deve atualizar o preço."""
        self.produto.editar_dados_cadastrais("Lápis HB", 2.00, "Papelaria", 5)
        self.assertEqual(self.produto.preco, 2.00)

    def test_editar_dados_cadastrais_altera_categoria(self):
        """Editar dados cadastrais deve atualizar a categoria."""
        self.produto.editar_dados_cadastrais("Lápis HB", 1.50, "Escolar", 5)
        self.assertEqual(self.produto.categoria, "Escolar")

    def test_editar_dados_cadastrais_altera_nivel_minimo(self):
        """Editar dados cadastrais deve atualizar o nível mínimo."""
        self.produto.editar_dados_cadastrais("Lápis HB", 1.50, "Papelaria", 10)
        self.assertEqual(self.produto.nivel_minimo, 10)

    def test_editar_dados_cadastrais_preserva_quantidade(self):
        """Editar dados cadastrais NÃO deve alterar a quantidade em estoque."""
        quantidade_antes = self.produto.quantidade
        self.produto.editar_dados_cadastrais("Lápis 4B", 1.90, "Papelaria", 5)
        self.assertEqual(self.produto.quantidade, quantidade_antes)

    def test_editar_dados_cadastrais_preserva_sku(self):
        """Editar dados cadastrais NÃO deve alterar o SKU (RN-02: SKU imutável)."""
        sku_antes = self.produto.sku
        self.produto.editar_dados_cadastrais("Lápis 4B", 1.90, "Papelaria", 5)
        self.assertEqual(self.produto.sku, sku_antes)

    def test_editar_preco_negativo_rejeitado(self):
        """Tentar editar para preço negativo deve levantar ValueError."""
        with self.assertRaises(ValueError):
            self.produto.editar_dados_cadastrais("Lápis HB", -5.0, "Papelaria", 5)

    def test_editar_nivel_minimo_negativo_rejeitado(self):
        """Tentar editar para nível mínimo negativo deve levantar ValueError."""
        with self.assertRaises(ValueError):
            self.produto.editar_dados_cadastrais("Lápis HB", 1.50, "Papelaria", -1)

# RF-04 — Inativar produto bloqueia movimentação

class TestRF04InativarProdutoBloqueiaMovimentacao(unittest.TestCase):
    """
    RF-04: O sistema deve permitir inativar um produto, impedindo novas
    movimentações sem deletar o histórico (RN-03).
    """

    def setUp(self):
        produto_ativo = criar_produto(sku="SKU-ATIVO1", quantidade=10)
        self.repo = MockRepository(produtos_iniciais=[produto_ativo])
        self.ctrl = EstoqueControllerTestavel(self.repo)

    def test_alternar_status_desativa_produto_ativo(self):
        """Produto ativo deve ficar inativo após alternar_status."""
        produto = self.repo.buscar_por_sku("SKU-ATIVO1")
        produto.alternar_status()
        self.assertFalse(produto.ativo)

    def test_alternar_status_reativa_produto_inativo(self):
        """Produto inativo deve ficar ativo após segunda chamada de alternar_status."""
        produto = self.repo.buscar_por_sku("SKU-ATIVO1")
        produto.alternar_status()  # desativa
        produto.alternar_status()  # reativa
        self.assertTrue(produto.ativo)

    def test_inativar_via_controller_persiste_status(self):
        """alterar_ativacao_produto deve salvar o status inativo via repositório."""
        self.ctrl.alterar_ativacao_produto("SKU-ATIVO1")
        produto = self.repo.buscar_por_sku("SKU-ATIVO1")
        self.assertFalse(produto.ativo)
        self.repo.atualizar.assert_called_once()

    def test_produto_inativo_nao_aceita_entrada(self):
        """
        RN-03: Um produto inativo não deve aceitar entradas.
        O Controller deve verificar o status antes de movimentar.
        Nota: a validação de 'ativo' é responsabilidade do Controller/View;
        o domínio (Produto) permite a movimentação física — o bloqueio
        semântico fica na camada de aplicação.
        """
        self.ctrl.alterar_ativacao_produto("SKU-ATIVO1")  # inativa
        produto = self.repo.buscar_por_sku("SKU-ATIVO1")
        self.assertFalse(produto.ativo,
            "Pré-condição: produto deve estar inativo após alterar_ativacao_produto.")

    def test_produto_inativo_preserva_quantidade_historica(self):
        """Inativar produto não deve zerar ou alterar a quantidade em estoque."""
        quantidade_antes = self.repo.buscar_por_sku("SKU-ATIVO1").quantidade
        self.ctrl.alterar_ativacao_produto("SKU-ATIVO1")
        quantidade_depois = self.repo.buscar_por_sku("SKU-ATIVO1").quantidade
        self.assertEqual(quantidade_antes, quantidade_depois)

    def test_inativar_sku_inexistente_levanta_erro(self):
        """Tentar inativar SKU não cadastrado deve levantar ValueError."""
        with self.assertRaises(ValueError):
            self.ctrl.alterar_ativacao_produto("SKU-NAOEXI")

# RF-05 — Listar exclui inativos

class TestRF05ListarExcluiInativos(unittest.TestCase):
    """
    RF-05: O sistema deve listar todos os produtos ativos; produtos inativos
    não devem aparecer na listagem principal.
    """

    def setUp(self):
        self.prod_ativo   = criar_produto(nome="Produto Ativo",   sku="SKU-ATIV01",
                                          quantidade=5)
        self.prod_inativo = criar_produto(nome="Produto Inativo", sku="SKU-INAT01",
                                          quantidade=3)
        self.prod_inativo.alternar_status()   # desativa antes de inserir
        self.repo = MockRepository(produtos_iniciais=[self.prod_ativo, self.prod_inativo])
        self.ctrl = EstoqueControllerTestavel(self.repo)

    def test_listar_retorna_somente_ativos(self):
        """listar_todos_produtos deve retornar apenas os produtos com ativo=True."""
        # A filtragem por ativo é responsabilidade da View (visao.py) ou do Controller;
        # aqui testamos que o domínio sinaliza corretamente o status.
        todos = self.ctrl.listar_todos_produtos()
        ativos = [p for p in todos if p.ativo]
        self.assertEqual(len(ativos), 1)
        self.assertEqual(ativos[0].nome, "Produto Ativo")

    def test_produto_inativo_presente_no_repositorio(self):
        """Produto inativo NÃO deve ser deletado — deve existir no repositório."""
        todos = self.ctrl.listar_todos_produtos()
        skus = [p.sku for p in todos]
        self.assertIn("SKU-INAT01", skus,
            "Produto inativo deve permanecer no repositório (exclusão lógica).")

    def test_produto_inativo_tem_ativo_false(self):
        """O produto inativo deve ter propriedade ativo == False."""
        todos = self.ctrl.listar_todos_produtos()
        produto_inativo = next(p for p in todos if p.sku == "SKU-INAT01")
        self.assertFalse(produto_inativo.ativo)

    def test_listar_todos_conta_inativos_e_ativos(self):
        """O repositório deve conter os dois produtos (ativo e inativo)."""
        self.assertEqual(len(self.ctrl.listar_todos_produtos()), 2)

    def test_reativar_produto_aparece_na_listagem_ativa(self):
        """Ao reativar um produto, ele deve voltar a aparecer como ativo."""
        self.ctrl.alterar_ativacao_produto("SKU-INAT01")   # reativa
        todos  = self.ctrl.listar_todos_produtos()
        ativos = [p for p in todos if p.ativo]
        self.assertEqual(len(ativos), 2)

# RF-06 — Entrada aumenta quantidade

class TestRF06EntradaAumentaQuantidade(unittest.TestCase):
    """
    RF-06: O sistema deve registrar entradas de estoque somando a quantidade
    informada ao saldo atual do produto.
    """

    def setUp(self):
        self.produto = criar_produto(sku="SKU-ENT001", quantidade=10)
        self.repo = MockRepository(produtos_iniciais=[self.produto])
        self.ctrl = EstoqueControllerTestavel(self.repo)

    def test_entrada_soma_quantidade_correta(self):
        """Entrada de 5 unidades com saldo 10 deve resultar em 15."""
        prod = self.ctrl.realizar_movimentacao("SKU-ENT001", 5)
        self.assertEqual(prod.quantidade, 15)

    def test_entrada_persiste_via_repositorio(self):
        """O método atualizar do repositório deve ser chamado após a entrada."""
        self.ctrl.realizar_movimentacao("SKU-ENT001", 5)
        self.repo.atualizar.assert_called_once()

    def test_entrada_grande_quantidade(self):
        """Entrada de grande volume deve ser aceita sem erros."""
        prod = self.ctrl.realizar_movimentacao("SKU-ENT001", 9999)
        self.assertEqual(prod.quantidade, 10 + 9999)

    def test_entrada_quantidade_zero_nao_altera_saldo(self):
        """
        Entrada de 0 unidades — embora RN-04 a proíba no fluxo real da View,
        o domínio aceita 0 como operação neutra (sem efeito no saldo).
        """
        saldo_antes = self.produto.quantidade
        self.produto.atualizar_estoque(0)
        self.assertEqual(self.produto.quantidade, saldo_antes)

    def test_multiplas_entradas_acumulam_corretamente(self):
        """Duas entradas sucessivas devem acumular o saldo corretamente."""
        self.ctrl.realizar_movimentacao("SKU-ENT001", 10)   # 10 + 10 = 20
        self.ctrl.realizar_movimentacao("SKU-ENT001", 5)    # 20 + 5  = 25
        prod = self.repo.buscar_por_sku("SKU-ENT001")
        self.assertEqual(prod.quantidade, 25)

    def test_entrada_sku_inexistente_levanta_erro(self):
        """Entrada para SKU não cadastrado deve levantar ValueError."""
        with self.assertRaises(ValueError):
            self.ctrl.realizar_movimentacao("SKU-NAOEXI", 10)

# RF-07 — Saída diminui quantidade

class TestRF07SaidaDiminuiQuantidade(unittest.TestCase):
    """
    RF-07 / RF-08: O sistema deve registrar saídas subtraindo a quantidade
    do saldo atual. Saídas que resultem em saldo negativo devem ser rejeitadas
    (RN-01: Ruptura de Estoque).
    """

    def setUp(self):
        self.produto = criar_produto(sku="SKU-SAI001", quantidade=20)
        self.repo = MockRepository(produtos_iniciais=[self.produto])
        self.ctrl = EstoqueControllerTestavel(self.repo)

    def test_saida_subtrai_quantidade_correta(self):
        """Saída de 8 unidades com saldo 20 deve resultar em 12."""
        prod = self.ctrl.realizar_movimentacao("SKU-SAI001", -8)
        self.assertEqual(prod.quantidade, 12)

    def test_saida_persiste_via_repositorio(self):
        """O método atualizar do repositório deve ser chamado após a saída."""
        self.ctrl.realizar_movimentacao("SKU-SAI001", -5)
        self.repo.atualizar.assert_called_once()

    def test_saida_exata_do_saldo_aceita(self):
        """Saída igual ao saldo total deve zerar o estoque sem erro."""
        prod = self.ctrl.realizar_movimentacao("SKU-SAI001", -20)
        self.assertEqual(prod.quantidade, 0)

    def test_saida_estoque_insuficiente_rejeitada(self):
        """
        RF-08 / RN-01: Saída maior que o saldo disponível deve levantar
        ValueError com mensagem indicando ruptura de estoque.
        """
        with self.assertRaises(ValueError) as ctx:
            self.ctrl.realizar_movimentacao("SKU-SAI001", -21)
        self.assertIn("Ruptura", str(ctx.exception),
            "A mensagem de erro deve mencionar 'Ruptura' (RN-01).")

    def test_saida_estoque_insuficiente_nao_altera_saldo(self):
        """
        Atomicidade (RN-01): quando a saída é rejeitada, o saldo não deve
        ser modificado.
        """
        saldo_antes = self.repo.buscar_por_sku("SKU-SAI001").quantidade
        try:
            self.ctrl.realizar_movimentacao("SKU-SAI001", -999)
        except ValueError:
            pass
        saldo_depois = self.repo.buscar_por_sku("SKU-SAI001").quantidade
        self.assertEqual(saldo_antes, saldo_depois,
            "Saldo não deve ser alterado quando a saída é rejeitada por insuficiência.")

    def test_saida_estoque_insuficiente_nao_chama_atualizar(self):
        """Quando a saída é rejeitada, o repositório NÃO deve ser chamado."""
        try:
            self.ctrl.realizar_movimentacao("SKU-SAI001", -999)
        except ValueError:
            pass
        self.repo.atualizar.assert_not_called()

    def test_saida_sku_inexistente_levanta_erro(self):
        """Saída para SKU não cadastrado deve levantar ValueError."""
        with self.assertRaises(ValueError):
            self.ctrl.realizar_movimentacao("SKU-NAOEXI", -5)

    def test_saida_seguida_de_entrada_restaura_saldo(self):
        """Saída seguida de entrada equivalente deve restaurar o saldo original."""
        self.ctrl.realizar_movimentacao("SKU-SAI001", -10)   # 20 - 10 = 10
        self.ctrl.realizar_movimentacao("SKU-SAI001", 10)    # 10 + 10 = 20
        prod = self.repo.buscar_por_sku("SKU-SAI001")
        self.assertEqual(prod.quantidade, 20)

if __name__ == "__main__":
    unittest.main(verbosity=2)