import os
import sys
import math
import pandas as pd
import threading
from tkinter import Tk, ttk

# Detecta o diretório de execução
if getattr(sys, 'frozen', False):
    pasta_entrada = os.path.dirname(sys.executable)
else:
    pasta_entrada = os.path.dirname(os.path.abspath(__file__))

arquivo_saida = 'planilhas_unificadas.csv'
extensoes = ['.xlsx', '.xls', '.csv', '.ods']

# --- GUI com Tkinter ---
root = Tk()
root.title("Unificando planilhas")
root.resizable(False, False)

# Tamanho da janela
largura_janela = 400
altura_janela = 50

# Calcula posição central
largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()
pos_x = (largura_tela // 2) - (largura_janela // 2)
pos_y = (altura_tela // 2) - (altura_janela // 2)

# Aplica tamanho e posição
root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

# Barra de progresso
progress = ttk.Progressbar(root, mode="determinate", length=380)
progress.pack(padx=10, pady=10)

def processar_arquivos():
    todas_linhas = []
    arquivos = [f for f in os.listdir(pasta_entrada) if os.path.splitext(f)[1].lower() in extensoes]

    # Fase 1: leitura dos arquivos
    for nome_arquivo in arquivos:
        caminho = os.path.join(pasta_entrada, nome_arquivo)
        _, ext = os.path.splitext(nome_arquivo)

        try:
            if ext.lower() == '.csv':
                df = pd.read_csv(caminho, sep=';')
                df.columns = [str(col).strip().lower() for col in df.columns]
                todas_linhas.append(df)
            else:
                xls = pd.read_excel(caminho, sheet_name=None, engine='odf' if ext == '.ods' else None)
                for _, df in xls.items():
                    df.columns = [str(col).strip().lower() for col in df.columns]
                    todas_linhas.append(df)
        except:
            pass  # silencioso, como solicitado

    # Fase 2: salvar com progresso
    if todas_linhas:
        df_final = pd.concat(todas_linhas, ignore_index=True)

        caminho_saida = os.path.join(pasta_entrada, arquivo_saida)
        chunk_size = 10000
        total_chunks = math.ceil(len(df_final) / chunk_size)
        progress["maximum"] = total_chunks

        with open(caminho_saida, 'w', encoding='utf-8', newline='') as f:
            for i in range(total_chunks):
                start = i * chunk_size
                end = min(start + chunk_size, len(df_final))
                chunk = df_final.iloc[start:end]
                chunk.to_csv(f, index=False, header=(i == 0), sep=';', mode='a')
                progress["value"] = i + 1
                root.update()

    root.after(300, root.destroy)  # fecha suavemente após 0.3s

# Executa a unificação numa thread para manter GUI ativa
threading.Thread(target=processar_arquivos, daemon=True).start()

# Inicia GUI
root.mainloop()
