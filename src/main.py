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

    # Lê CSV sem cabeçalho, separado por ponto-e-vírgula
    df = pd.read_csv(caminho_csv, header=None, sep=";", engine="python")

    # Primeira coluna é a coluna 0
    projetos_brutos = df[0].astype(str).tolist()

    # Limpeza da lista
    projetos = []
    for p in projetos_brutos:
        p = p.strip().replace(";", "").strip()
        if p != "":
            projetos.append(p)

    print("Projetos carregados:", projetos)

    # Loop com tratamento de erro
    for numero in projetos:
        print("\n====================================================")
        print(f"Iniciando fluxo para o projeto: {numero}")
        print("====================================================\n")

        sucesso = executar_fluxo(numero_projeto=numero, base_url=base_url)

        if not sucesso:
            print(f"[AVISO] Projeto {numero} ignorado (não encontrado ou erro).")
        else:
            print(f"[OK] Projeto {numero} executado com sucesso.")

if __name__ == "__main__":
    main()
