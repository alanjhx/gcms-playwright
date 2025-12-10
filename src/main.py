import os
import pandas as pd
from gcms_scraper import executar_fluxo

def main():

    base_url = os.environ.get(
        "GCMS_URL",
        "https://unifier.oraclecloud.com/alcoa/bp/route/home/i-unifier"
    )

    caminho_csv = os.environ.get("PROJETO_CSV", "projetos.csv")

    print(f"Lendo lista de projetos em: {caminho_csv}")

    # Lê CSV sem cabeçalho, usando ";" como separador OU mantendo a coluna única
    df = pd.read_csv(caminho_csv, header=None, sep=";", engine="python")

    # Primeira coluna: coluna 0
    projetos_brutos = df[0].astype(str).tolist()

    # Limpa espaços, remove ponto-e-vírgula, remove vazios
    projetos = []
    for p in projetos_brutos:
        p = p.strip().replace(";", "")
        if p != "":
            projetos.append(p)

    print("Projetos carregados:", projetos)

    for numero in projetos:
        executar_fluxo(numero_projeto=numero, base_url=base_url)

if __name__ == "__main__":
    main()
