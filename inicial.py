import webview
import threading
import os
import time
import sys

# Função auxiliar para obter o caminho correto para recursos empacotados pelo PyInstaller
def resource_path(relative_path):
    """Obtém o caminho absoluto para o recurso, seja no ambiente de desenvolvimento ou no executável empacotado."""
    try:
        # PyInstaller cria um atributo _MEIPASS para acessar os arquivos temporários
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def iniciar_streamlit():
    app_path = resource_path("app.py")
    
    # Flags atualizadas do Streamlit para versões mais recentes
    command = f"streamlit run {app_path} --browser.gatherUsageStats false --server.headless true --server.port 8501 --server.enableCORS false --server.enableXsrfProtection false"
    
    os.system(command)

# Inicia o Streamlit em uma thread separada
threading.Thread(target=iniciar_streamlit, daemon=True).start()

# IMPORTANTE: Tempo de espera aumentado para permitir que o Streamlit e a configuração inicial do webview sejam concluídos.
# Ajuste este valor se ainda vir problemas. 20-30 segundos podem ser necessários para máquinas muito lentas.
time.sleep(15)

try:
    # Cria a janela do webview
    # Armazena o objeto da janela em uma variável
    window = webview.create_window("Meu Dashboard Financeiro", "http://localhost:8501", width=1280, height=800, min_size=(800, 600))
    
    # Inicia o loop do webview DEPOIS que a janela for confirmada como criada
    webview.start()

except Exception as e:
    # Captura quaisquer exceções durante a criação da janela ou o início do webview
    print(f"Ocorreu um erro durante a inicialização do webview: {e}")
    # Você pode querer registrar este erro ou exibir uma caixa de mensagem se estiver rodando como executável
    sys.exit(1) # Sai do script se o webview falhar ao iniciar