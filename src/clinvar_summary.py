import pandas as pd
import json


def extract_hpo_id(id_str):
    return

def extract_omim_id(id_str):
    return


def handle_summary():
    df_variant = pd.read_csv("data/clinvar/variant_summary.txt", sep="\t", dtype=str).fillna("")

    df_variant = df_variant[df_variant["Assembly"] =="GRCh38"]

    for index, row in df_variant.iterrows():
        variant_type = row["Type"]
        nucleotide = row["Name"]
        gene_name = row["GeneSymbol"]
        clinical_significance = row["ClinicalSignificance"]
        rsID = row["RS# (dbSNP)"]
        phenotype_ids = row["phenotypeIDS"]
        other_ids = row["OtherIDs"]
        phenotype_list = row["PhenotypeList"]
        chromosome = row["Chromosome"]
        review_status = row["ReviewStatus"]
        number_submitters = row["NumberSubmitters"]


if __name__ == "__main__":
    handle_summary()