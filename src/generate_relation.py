import pandas as pd


def handle_gwas_association():
    df_gwas = pd.read_csv(
        "data/gwas/gwas_catalog_v1.0-associations_e105_r2021-12-21.tsv",
        sep="\t", dtype=str
    ).fillna("")

    print()


def handle_omim_map():
    df_omim_map = pd.read_csv("data/OMIM/genemap2.txt", sep="\t", dtype=str, skiprows=3).fillna("")

    print()


def handle_omim_chpo_rel():
    df_rel = pd.read_csv("data/omim_chn/omim_gene.txt", sep="\t", dtype=str).fillna("")

    df_omim = pd.read_csv("data/omim_chn/OMIM_disease.txt", sep="\t", dtype=str).fillna("")

    df_chpo = pd.read_csv("data/omim_chn/CHPO.txt", sep="\t", dtype=str).fillna("")

    print()


if __name__ == "__main__":
    handle_gwas_association()
    handle_omim_map()
    handle_omim_chpo_rel()