import pandas as pd


def handle_gwas_association():
    """
     pubmed node properties:
        pubmed_id
        pubmed_link
        pubmed_study
        pubmed_study_chn
        journal
        date
        sample_detail

    research_in_rsID edge properties:
        strongest_snp_risk_allele
        risk_allele_frequency
        p_value
        p_value_mlog


    (pubmed)-[research_in_gene]->(gene)
    (pubmed)-[research_in_rsID]->(rsID)
    """
    df_gwas = pd.read_csv(
        "data/gwas/gwas_catalog_v1.0-associations_e105_r2021-12-21.tsv",
        sep="\t", dtype=str
    ).fillna("")

    print()


def handle_omim_map():
    """
    gene node 补充 properties:
        gene_name_detail
        gene_name_detail_chn
        gene_phenotype
        gene_phenotype_chn
    """
    df_omim_map = pd.read_csv("data/OMIM/genemap2.txt", sep="\t", dtype=str, skiprows=3).fillna("")

    print()


def handle_omim_chpo_rel():
    """
    omim node properties:
        omim_id,
        omim_name,
        omim_name_chn

    hpo node properties:
        hpo_id,
        hpo_name,
        hpo_name_chn,
        hpo_definition,
        hpo_definition_chn,
        hpo_classification,
        hpo_classification_chn

    (omim)-[has-phenotype]->(hpo)
    (omim)-[omim_gene_influence]->(gene)
    (hpo)-[hpo_gene_influence]->(gene)
    """

    df_rel = pd.read_csv("data/omim_chn/omim_gene.txt", sep="\t", dtype=str).fillna("")

    df_omim = pd.read_csv("data/omim_chn/OMIM_disease.txt", sep="\t", dtype=str).fillna("")

    df_chpo = pd.read_csv("data/omim_chn/CHPO.txt", sep="\t", dtype=str).fillna("")

    print()


if __name__ == "__main__":
    handle_gwas_association()
    handle_omim_map()
    handle_omim_chpo_rel()
