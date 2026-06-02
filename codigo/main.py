import sys
from controlador import EstoqueController
from visao import EstoqueView

def main():
    try:
        print("⚡ Conectando ao Google Sheets... Aguarde.")
        # Instancia o motor (Controller + Repository)
        controlador = EstoqueController()
        
        # Instancia a interface passando o motor para ela (Injeção de dependência)
        interface = EstoqueView(controlador)
        print("✅ Conexão estabelecida com sucesso!")
        
        # Passa o controle total para a View
        interface.iniciar()
        
    except Exception as e:
        print(f"\n❌ [Erro Crítico de Inicialização]: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()