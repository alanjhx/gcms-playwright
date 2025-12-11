import os
import pandas as pd
from gcms_scraper import executar_fluxo

def main():
    base_url = os.environ.get("GCMS_URL")
    csv_path = os.environ.get("PROJETO_CSV", "Lista de Projetos.csv")

    df = pd.read_csv(csv_path, sep=";", header=None)
    projetos = [x.strip().replace(";", "") for x in df[0].astype(str).tolist() if x.strip()]

    print(projetos)

    for p in projetos:
        executar_fluxo(p, base_url)


if __name__ == "__main__":
    main()
