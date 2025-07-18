import os
import sys
import math
import pandas as pd
from tqdm import tqdm

# Detecta diretório correto, seja no .py ou .exe compilado
if getattr(sys, 'frozen', False):
    pasta_entrada = os.path.dirname(sys.executable)
else:
    pasta_entrada = os.path.dirname(os.path.abspath(__file__))

arquivo_saida = 'planilhas_unificadas.csv'

# Extensões suportadas
extensoes = ['.xlsx', '.xls', '.csv', '.ods']

# Lista para armazenar todos os DataFrames
todas_linhas = []

# Lista de arquivos válidos na pasta
arquivos = [f for f in os.listdir(pasta_entrada) if os.path.splitext(f)[1].lower() in extensoes]

# Processa os arquivos com barra de progresso
for nome_arquivo in tqdm(arquivos, desc="Lendo arquivos"):
    caminho = os.path.join(pasta_entrada, nome_arquivo)
    nome, ext = os.path.splitext(nome_arquivo)

    try:
        if ext.lower() == '.csv':
            df = pd.read_csv(caminho, sep=';')
            df.columns = [str(col).strip().lower() for col in df.columns]  # Normalize colunas
            todas_linhas.append(df)
        else:
            xls = pd.read_excel(caminho, sheet_name=None, engine='odf' if ext == '.ods' else None)
            for _, df in xls.items():
                df.columns = [str(col).strip().lower() for col in df.columns]  # Normalize colunas
                todas_linhas.append(df)
    except Exception as e:
        print(f"Erro ao processar {nome_arquivo}: {e}")

# Salva o arquivo final
if todas_linhas:
    df_final = pd.concat(todas_linhas, ignore_index=True)

    caminho_saida = os.path.join(pasta_entrada, arquivo_saida)
    chunk_size = 10000
    total_chunks = math.ceil(len(df_final) / chunk_size)

    with open(caminho_saida, 'w', encoding='utf-8', newline='') as f:
        for i in tqdm(range(total_chunks), desc="Salvando CSV"):
            start = i * chunk_size
            end = min(start + chunk_size, len(df_final))
            chunk = df_final.iloc[start:end]
            chunk.to_csv(f, index=False, header=(i == 0), sep=';', mode='a')

    print(f"\n✅ Arquivo CSV consolidado salvo como: {arquivo_saida}")
else:
    print("⚠️ Nenhum dado encontrado para consolidar.")
