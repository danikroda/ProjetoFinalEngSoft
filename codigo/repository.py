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
            # Pega todas as linhas brutas da planilha
            todas_linhas = self.__tabela.get_all_values()
            
            print(f"\n🔍 [DIAGNÓSTICO] Total de linhas lidas (com cabeçalho): {len(todas_linhas)}")
            if todas_linhas:
                print(f"🔍 [DIAGNÓSTICO] Linha do Cabeçalho: {todas_linhas[0]}")
                if len(todas_linhas) > 1:
                    print(f"🔍 [DIAGNÓSTICO] Primeira linha de dados: {todas_linhas[1]}")
            
            # O [1:] pula a primeira linha (cabeçalho)
            linhas_dados = todas_linhas[1:]
            
            produtos = []
            for idx, linha in enumerate(linhas_dados):
                # Evita linhas completamente vazias na planilha
                if linha and any(linha):
                    try:
                        # Força o preenchimento de colunas faltantes com strings vazias para não quebrar o índice
                        while len(linha) < 7:
                            linha.append("")
                            
                        # Tenta transformar a linha em um Produto
                        prod = Produto.do_repositorio(linha)
                        produtos.append(prod)
                    except Exception as erro_linha:
                        print(f"⚠️ [Aviso] Erro ao converter a linha {idx + 2}: {linha}. Detalhe: {erro_linha}")
                        
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

    def deletar(self, sku: str) -> None:
        """Remove permanentemente a linha do produto na planilha pelo SKU."""
        try:
            todas_linhas = self.__tabela.get_all_values()
            for idx, linha in enumerate(todas_linhas):
                if linha and linha[0] == sku:
                    self.__tabela.delete_rows(idx + 1)  # gspread usa índice 1-based
                    return
            raise ValueError(f"SKU '{sku}' não encontrado para exclusão.")
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Erro ao deletar produto no Google Sheets: {e}")