import os
from pathlib import Path
 
import pandas as pd
 
from gcms_scraper import executar_fluxo
 
 
def main() -> None:
    # URL base do Unifier / GCMS
    base_url = os.environ.get(
        "GCMS_URL",
        "https://unifier.oraclecloud.com/alcoa/bp/route/home/i-unifier",
    )
 
    # Caminho do CSV com a lista de projetos
    # Ex.: "Lista de Projetos.csv" com um projeto por linha, separados por ";"
    caminho_csv = os.environ.get("PROJETO_CSV", "Lista de Projetos.csv")
 
    caminho_csv = Path(caminho_csv)
    if not caminho_csv.exists():
        raise FileNotFoundError(
            f"Arquivo de projetos não encontrado: {caminho_csv.resolve()}"
        )
 
    print(f"Lendo lista de projetos em: {caminho_csv}")
 
    # Lê CSV sem cabeçalho, usando ";" como separador
    df = pd.read_csv(caminho_csv, header=None, sep=";", engine="python")
 
    # Primeira coluna
    projetos_brutos = df[0].astype(str).tolist()
 
    # Limpa espaços, remove ';' e linhas vazias
    projetos = []
    for p in projetos_brutos:
        p = p.strip().replace(";", "")
        if p:
            projetos.append(p)
 
    print("Projetos carregados:", projetos)
 
    for numero in projetos:
        print("=" * 60)
        print(f"Iniciando fluxo para o projeto: {numero}")
        print("=" * 60)
        try:
            executar_fluxo(numero_projeto=numero, base_url=base_url)
        except Exception as e:
            print(f"[ERRO GERAL] Falha ao processar o projeto {numero}: {e}")
 
 
if __name__ == "__main__":
    main()
