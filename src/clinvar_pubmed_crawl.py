import pandas as pd
import os

def print_pubmed():
    df_cit = pd.read_csv("data/clinvar/var_citations.txt", sep="\t", dtype=str).fillna("")

    df_cit = df_cit[df_cit["citation_source"] == "PubMed"]
    df_cit = df_cit[["VariationID", "citation_id"]]

    df_gwas = pd.read_csv("data/gwas/gwas_catalog_v1.0-associations_e105_r2021-12-21.tsv", sep="\t", dtype=str).fillna("")

    gwas_pubmed_list = set(df_gwas["PUBMEDID"].values)

    citation_id_list = set(df_cit["citation_id"].values)

    print(len(citation_id_list))

    crawl_list = list(citation_id_list - gwas_pubmed_list)

    batch_size = 2000

    for i in range(int(len(crawl_list) / batch_size) + 1):
        print(",".join(crawl_list[i * batch_size: (i + 1) * batch_size]))


def handle_pubmed():
    df_all = pd.DataFrame(columns=["PMID", "Title", "Journal/Book", "Create Date"])
    for p in os.listdir("data/pubmed"):
        _df = pd.read_csv(os.path.join("data/pubmed", p), dtype=str).fillna("")
        _df = _df[["PMID", "Title", "Journal/Book", "Create Date"]]
        df_all = pd.concat([_df, df_all], axis=0)

    df_all[":LABEL"] = ["pubmed"] * len(df_all)
    df_all[["pubmed_id:ID(pubmed)", "pubmed_study", "journal", "date"]] = \
        df_all[["PMID", "Title", "Journal/Book", "Create Date"]]
    df_all[["display"]] = df_all[["PMID"]]
    df_all["sample_size"] = [""] * len(df_all)
    df_all["pubmed_link"] = df_all.apply(lambda row: "www.ncbi.nlm.nih.gov/pubmed/{}".format(row["PMID"]), axis=1)
    df_all = df_all[["pubmed_id:ID(pubmed)", "display", "pubmed_link", "pubmed_study",
                     "journal", "sample_size", "date", ":LABEL"]]

    df_all = df_all[df_all["pubmed_id:ID(pubmed)"] != ""]

    df_all.to_csv("output/clinvar_pubmed.csv", index=False)


def gen_clinvar_pubmed_rel():
    df_cit = pd.read_csv("data/clinvar/var_citations.txt", sep="\t", dtype=str).fillna("")
    df_cit = df_cit[df_cit["citation_source"] == "PubMed"]
    df_cit = df_cit[["VariationID", "citation_id"]]

    df_location = pd.read_csv("output/variant_location.csv", dtype=str).fillna("")
    loc_vid_dict = dict(zip(
        [x.split("/")[-1] for x in df_location["variant_link"].values],
        df_location["display"].values
    ))

    df_cit[":START_ID(variant_location)"] = df_cit.apply(lambda row: loc_vid_dict.get(row["VariationID"], ""), axis=1)
    df_cit[[":END_ID(pubmed)"]] = df_cit[["citation_id"]]
    df_cit = df_cit[[":START_ID(variant_location)", ":END_ID(pubmed)"]]
    df_cit = df_cit[
        (df_cit[":START_ID(variant_location)"] != "") &
        (df_cit[":END_ID(pubmed)"] != "")
    ]
    df_cit[":TYPE"] = ["location_in_pubmed"] * len(df_cit)
    df_cit.to_csv("output/location_pubmed_edge.csv", index=False)


def gen_location_gene_rel():
    df_location = pd.read_csv("output/variant_location.csv", dtype=str).fillna("")
    df_location = df_location[["display", "gene_name"]].drop_duplicates()
    df_location[[":START_ID(variant_location)", ":END_ID(gene)"]] = df_location[["display", "gene_name"]]
    df_location = df_location[[":START_ID(variant_location)", ":END_ID(gene)"]]
    df_location = df_location[
        (df_location[":START_ID(variant_location)"] != "") &
        (df_location[":END_ID(gene)"] != "")
    ]
    df_location[":TYPE"] = ["location_in_gene"] * len(df_location)
    df_location.to_csv("output/location_gene_edge.csv", index=False)


if __name__ == "__main__":
    # print_pubmed()
    # handle_pubmed()
    gen_clinvar_pubmed_rel()
    gen_location_gene_rel()