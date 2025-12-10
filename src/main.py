import os
import pandas as pd
from pathlib import Path
 
from gcms_scraper import executar_fluxo
 
 
def main():
    base_url = os.environ.get(
        "GCMS_URL",
        "https://unifier.oraclecloud.com/alcoa/bp/route/home/i-unifier",
    )
 
    caminho_csv = os.environ.get("PROJETO_CSV", "Lista de Projetos.csv")
    caminho_csv = Path(caminho_csv)
 
    if not caminho_csv.exists():
        raise FileNotFoundError(f"CSV não encontrado: {caminho_csv}")
 
    print(f"Lendo arquivo: {caminho_csv}")
 
    df = pd.read_csv(caminho_csv, header=None, sep=";", engine="python")
 
    projetos = []
    for valor in df[0].astype(str).tolist():
        v = valor.strip().replace(";", "")
        if v:
            projetos.append(v)
 
    print(f"Projetos carregados: {len(projetos)}")
 
    for numero in projetos:
        try:
            executar_fluxo(numero, base_url)
        except Exception as e:
            print(f"[ERRO GERAL] Falha no projeto {numero}: {e}")
 
 
if __name__ == "__main__":
    main()
