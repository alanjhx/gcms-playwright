import os
import pandas as pd
from gcms_scraper import executar_fluxo


def main():

    # URL base do GCMS / Unifier
    base_url = os.environ.get(
        "GCMS_URL",
        "https://unifier.oraclecloud.com/alcoa/bp/route/home/i-unifier"
    )

    # Caminho do CSV com a lista de projetos
    caminho_csv = os.environ.get("PROJETO_CSV", "Lista de Projetos.csv")

    print(f"Lendo lista de projetos em: {caminho_csv}")

    # Lê o CSV
    df = pd.read_csv(caminho_csv, header=None)  # sem cabeçalho
    projetos = df[0].astype(str).tolist()

    print("Projetos carregados:", projetos)

    # Executa o fluxo para cada projeto
    for numero in projetos:
        executar_fluxo(numero_projeto=numero, base_url=base_url)


if __name__ == "__main__":
    main()
