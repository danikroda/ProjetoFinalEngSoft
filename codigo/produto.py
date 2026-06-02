import uuid
from datetime import datetime

class Produto:
    def __init__(
        self, 
        nome: str, 
        preco: float, 
        categoria: str, 
        nivel_minimo: int, 
        quantidade: int = 0, 
        ativo: bool = True, 
        sku: str = None
    ):
        # O SKU só é gerado se for um produto totalmente novo no sistema
        self.__sku = sku if sku else f"SKU-{str(uuid.uuid4()).split('-')[0].upper()}"
        self.__nome = nome
        self.__preco = self.__validar_preco(preco)
        self.__categoria = categoria
        self.__ativo = ativo
        self.__quantidade = self.__validar_quantidade_inicial(quantidade)
        self.__nivel_minimo = self.__validar_nivel_minimo(nivel_minimo)

    # === MÉTODOS DE FÁBRICA (FACTORY METHODS) ===

    @classmethod
    def do_repositorio(cls, linha: list) -> 'Produto':
        """Reconstrói um objeto Produto a partir dos dados textuais do Google Sheets."""
        if not linha or len(linha) < 7:
            raise ValueError("Dados do repositório incompletos para instanciar Produto.")
            
        return cls(
            sku=linha[0],
            nome=linha[1],
            preco=float(linha[2]),
            categoria=linha[3],
            ativo=linha[4].lower() == 'true',
            nivel_minimo=int(linha[5]),
            quantidade=int(linha[6])
        )

    def para_linha_repositorio(self) -> list:
        """Exporta os dados do produto formatados para salvar na linha do Sheets."""
        return [
            self.sku, 
            self.nome, 
            self.preco, 
            self.categoria, 
            str(self.ativo), 
            self.nivel_minimo, 
            self.quantidade
        ]

    # === GETTERS (PROPERTIES) — Acesso controlado de leitura externa ===

    @property
    def sku(self) -> str:
        return self.__sku

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def preco(self) -> float:
        return self.__preco

    @property
    def categoria(self) -> str:
        return self.__categoria

    @property
    def ativo(self) -> bool:
        return self.__ativo

    @property
    def quantidade(self) -> int:
        return self.__quantidade

    @property
    def nivel_minimo(self) -> int:
        return self.__nivel_minimo

    # === REGRAS DE NEGÓCIO ENCAPSULADAS (MUTAÇÕES DE ESTADO) ===

    def atualizar_estoque(self, qtd: int) -> None:
        """Modifica a quantidade em estoque. Números positivos para Entrada, negativos para Saída."""
        if self.__quantidade + qtd < 0:
            raise ValueError(f"Operação negada. Saldo insuficiente para o produto '{self.__nome}' (Ruptura de Estoque).")
        self.__quantidade += qtd

    def alternar_status(self) -> None:
        """Ativa ou desativa o produto (Exclusão lógica do catálogo)."""
        self.__ativo = not self.__ativo

    def editar_dados_cadastrais(self, nome: str, preco: float, categoria: str, nivel_minimo: int) -> None:
        """Atualiza as informações básicas do produto aplicando as validações necessárias."""
        self.__nome = nome
        self.__preco = self.__validar_preco(preco)
        self.__categoria = categoria
        self.__nivel_minimo = self.__validar_nivel_minimo(nivel_minimo)

    def verificar_estoque_baixo(self) -> bool:
        """Indica se o produto atingiu ou operou abaixo do nível de segurança de estoque."""
        return self.__quantidade <= self.__nivel_minimo

    # === VALIDAÇÕES INTERNAS (MÉTODOS PRIVADOS `__`) ===

    def __validar_preco(self, preco: float) -> float:
        if preco < 0:
            raise ValueError("O preço do produto não pode ser valores negativos.")
        return preco

    def __validar_quantidade_inicial(self, qtd: int) -> int:
        if qtd < 0:
            raise ValueError("O estoque inicial não pode ser negativo.")
        return qtd

    def __validar_nivel_minimo(self, nivel: int) -> int:
        if nivel < 0:
            raise ValueError("O nível mínimo de estoque de segurança não pode ser negativo.")
        return nivel