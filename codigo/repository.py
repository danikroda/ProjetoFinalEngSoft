import os
from typing import List, Optional
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from produto import Produto

# Carrega as variáveis de ambiente definidas no arquivo .env
load_dotenv()

class GoogleSheetsRepository:
    def __init__(self):
        # 1. Recupera as configurações do arquivo .env local
        cred_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        
        if not cred_path or not spreadsheet_id:
            raise ValueError(
                "Erro de Configuração: Variáveis GOOGLE_CREDENTIALS_PATH ou "
                "SPREADSHEET_ID não foram encontradas no arquivo .env!"
            )

        # 2. Define os escopos de acesso necessários para manipular o Drive e as Planilhas
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # 3. Autentica e conecta na API do Google
        try:
            credenciais = Credentials.from_service_account_file(cred_path, scopes=scopes)
            self.__client = gspread.authorize(credenciais)
            self.__planilha = self.__client.open_by_key(spreadsheet_id)
            # Conecta automaticamente na primeira aba (sheet1)
            self.__tabela = self.__planilha.sheet1
        except Exception as e:
            raise RuntimeError(f"Falha crítica ao conectar com a API do Google Sheets: {e}")

    def listar_todos(self) -> List[Produto]:
        """Lê todas as linhas da planilha e converte em objetos da classe Produto"""
        try:
            # Pega todas as linhas da planilha. O [1:] pula a primeira linha (cabeçalho)
            todas_linhas = self.__tabela.get_all_values()[1:]
            
            produtos = []
            for linha in todas_linhas:
                # Evita linhas completamente vazias na planilha
                if linha and any(linha):
                    # Uso do padrão Factory Method encapsulado no modelo
                    produtos.append(Produto.do_repositorio(linha))
            return produtos
        except Exception as e:
            raise RuntimeError(f"Erro ao ler dados da planilha: {e}")

    def buscar_por_sku(self, sku: str) -> Optional[Produto]:
        """Busca um produto específico na planilha utilizando o SKU"""
        produtos = self.listar_todos()
        for produto in produtos:
            if produto.sku == sku:
                return produto
        return None

    def salvar_novo(self, produto: Produto) -> None:
        """Adiciona uma nova linha com os dados do produto no final da planilha"""
        try:
            # Converte o modelo encapsulado para o formato de lista [SKU, Nome, Preço...]
            linha_dados = produto.para_linha_repositorio()
            self.__tabela.append_row(linha_dados)
        except Exception as e:
            raise RuntimeError(f"Erro ao salvar novo produto no Google Sheets: {e}")

    def atualizar(self, produto: Produto) -> None:
        """Localiza o produto pelo SKU na planilha e atualiza a linha correspondente por completo"""
        try:
            # Obtém todas as linhas atuais para descobrir o índice correto da linha
            todas_linhas = self.__tabela.get_all_values()
            
            for idx, linha in enumerate(todas_linhas):
                if linha and linha[0] == produto.sku:
                    # O gspread adota índice baseado em 1, logo a linha real é idx + 1
                    numero_linha = idx + 1
                    
                    # Define o intervalo da linha (Colunas de A até G)
                    intervalo = f"A{numero_linha}:G{numero_linha}"
                    
                    # Prepara a nova lista de dados atualizada da memória RAM
                    dados_atualizados = [produto.para_linha_repositorio()]
                    
                    # Executa a atualização na planilha por completo
                    self.__tabela.update(intervalo, dados_atualizados)
                    return
            
            raise ValueError(f"Não foi possível atualizar: SKU {produto.sku} não encontrado na planilha.")
        except Exception as e:
            raise RuntimeError(f"Erro ao atualizar dados na planilha: {e}")