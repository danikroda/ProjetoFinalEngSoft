from abc import ABC, abstractmethod
from produto import Produto

# 1. A Interface Base (O Contrato)
class ObservadorEstoque(ABC):
    """Interface que todo observador de estoque deve seguir."""
    
    @abstractmethod
    def notificar_estoque_baixo(self, produto: Produto) -> None:
        pass

# 2. Observador Concreto 1: Mensagem na Tela
class AlertaTerminalObserver(ObservadorEstoque):
    """Observador que imprime um alerta amarelo na tela do terminal."""
    
    def notificar_estoque_baixo(self, produto: Produto) -> None:
        print(f"\n⚠️  [SISTEMA DE ALERTAS]: Atenção! O estoque de '{produto.nome}' "
              f"caiu para {produto.quantidade} unidades. (Mínimo: {produto.nivel_minimo}). "
              f"Considere reabastecer em breve.")

# 3. Observador Concreto 2: Arquivo de Log
class LogArquivoObserver(ObservadorEstoque):
    """Observador que grava silenciosamente um registro em um arquivo de texto."""
    
    def notificar_estoque_baixo(self, produto: Produto) -> None:
        # Abre o arquivo em modo 'a' (append) para não apagar o que já existe
        with open("log_alertas_estoque.txt", "a", encoding="utf-8") as arquivo:
            arquivo.write(f"ALERTA GERADO: SKU {produto.sku} | Produto: {produto.nome} | "
                          f"Qtd Atual: {produto.quantidade} | Nivel Mínimo: {produto.nivel_minimo}\n")