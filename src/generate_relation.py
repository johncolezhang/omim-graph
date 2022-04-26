import pandas as pd
import json

node_set = []
edge_set = []

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
        risk_allele
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

    node_list = []
    edge_list = []

    for index, row in df_gwas.iterrows():
        # for node
        pubmed_id = row["PUBMEDID"].replace("\"", "'").replace("?", "Unknown")
        pubmed_link = row["LINK"].replace("\"", "'").replace("?", "Unknown")
        journal = row["JOURNAL"].replace("\"", "'").replace("?", "Unknown")
        pubmed_study = row["STUDY"].replace("\"", "'").replace("?", "Unknown")
        sample_size = row["INITIAL SAMPLE SIZE"].replace("\"", "'").replace("?", "Unknown")
        date = row["DATE"].replace("\"", "'").replace("?", "Unknown")

        if "pubmed_{}".format(pubmed_id) not in node_set:
            node_set.append("pubmed_{}".format(pubmed_id))

            pubmed_node = {
                "label": ["pubmed"],
                "node_ID": "pubmed_id",
                "property": {
                    "pubmed_id": pubmed_id,
                    "display": pubmed_id,
                    "pubmed_link": pubmed_link,
                    "journal": journal,
                    "sample_size": sample_size,
                    "date": date
                }
            }
            node_list.append(pubmed_node)

        # for edge
        risk_allele = row["STRONGEST SNP-RISK ALLELE"]
        risk_allele_frequency = row["RISK ALLELE FREQUENCY"]
        rsID = row["SNPS"]
        p_value = row["P-VALUE"]
        p_value_mlog = row["PVALUE_MLOG"]
        gene_1 = row["REPORTED GENE(S)"]
        gene_2 = row["MAPPED_GENE"]

        # generate gene_name
        if gene_1 != "NR":
            gene_names = [x.strip() for x in gene_1.split(", ")]
            gene_names = list(filter(
                lambda x: x.lower() not in ["na", "", "nr", "intergenic"] and len(x) > 1,
                gene_names
            ))
        else:
            if "; " in gene_2:
                gene_2 = gene_2.replace("; ", " - ")

            if " - " in gene_2:
                gene_names = gene_2.split(" - ")
            else:
                gene_names = [gene_2]

            gene_names = list(set(filter(
                lambda x: x.lower() not in ["na", "", "nr", "n/a", "no mapped genes", "intergenic"] and len(x) > 1,
                gene_names
            )))

        if "rsID_{}".format(rsID) not in node_set:
            node_set.append("rsID_{}".format(rsID))

            rsID_node = {
                "label": ["rsID"],
                "node_ID": "variant_name",
                "property": {
                    "variant_name": rsID,
                    "display": rsID,
                    "type": "rsID"
                }
            }
            node_list.append(rsID_node)

        if "{}_{}".format(pubmed_id, rsID) not in edge_set:
            edge_set.append("{}_{}".format(pubmed_id, rsID))

            rsID_relation_edge = {
                "start_node": {
                    "label": ["pubmed"],
                    "node_ID": "pubmed_id",
                    "property": {
                        "pubmed_id": pubmed_id
                    }
                },
                "end_node": {
                    "label": ["rsID"],
                    "node_ID": "variant_name",
                    "property": {
                        "variant_name": rsID,
                        "type": "rsID"
                    }
                },
                "edge": {
                    "label": "research_in_rsID",
                    "property": {
                        "risk_allele": risk_allele,
                        "risk_allele_frequency": risk_allele_frequency,
                        "pubmed_study": pubmed_study,
                        "p_value": p_value,
                        "p_value_mlog": p_value_mlog
                    }
                }
            }
            edge_list.append(rsID_relation_edge)

        for gene_name in gene_names:
            if "gene_{}".format(gene_name) not in node_set:
                node_set.append("gene_{}".format(gene_name))

                gene_node = {
                    "label": ["gene"],
                    "node_ID": "gene_name",
                    "property": {
                        "gene_name": gene_name,
                        "display": gene_name
                    }
                }
                node_list.append(gene_node)

            if "{}_{}".format(pubmed_id, gene_name) not in edge_set:
                edge_set.append("{}_{}".format(pubmed_id, gene_name))

                gene_relation_edge = {
                    "start_node": {
                        "label": ["pubmed"],
                        "node_ID": "pubmed_id",
                        "property": {
                            "pubmed_id": pubmed_id
                        }
                    },
                    "end_node": {
                        "label": ["gene"],
                        "node_ID": "gene_name",
                        "property": {
                            "gene_name": gene_name,
                            "type": "gene"
                        }
                    },
                    "edge": {
                        "label": "research_in_gene",
                        "property": {}
                    }
                }
                edge_list.append(gene_relation_edge)

    with open("json/gwas_nodes.json", "w") as f:
        json.dump(node_list, f)

    with open("json/gwas_edges.json", "w") as f:
        json.dump(edge_list, f)


def handle_omim_map():
    """
    gene node 补充 properties:
        gene_name_detail
        gene_name_detail_chn
        chromosome
    """
    df_omim_map = pd.read_csv("data/OMIM/genemap2.txt", sep="\t", dtype=str, skiprows=3).fillna("")

    node_list = []
    for index, row in df_omim_map.iterrows():
        gene_name = row["Gene Symbols"]
        gene_name_detail = row["Gene Name"]
        chromosome = row["# Chromosome"]

        if "#" in chromosome:
            continue

    if "gene_{}".format(gene_name) not in node_set:
        node_set.append("gene_{}".format(gene_name))
        gene_node = {
            "label": ["gene"],
            "node_ID": "gene_name",
            "property": {
                "gene_name": gene_name,
                "display": gene_name,
                "gene_name_detail": gene_name_detail,
                "chromosome": chromosome
            }
        }
        node_list.append(gene_node)

    with open("json/omim_gene_nodes.json", "w") as f:
        json.dump(node_list, f)


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

    (omim)-[has_phenotype]->(hpo)
    (omim)-[omim_gene_influence]->(gene)
    (hpo)-[hpo_gene_influence]->(gene)
    """

    df_omim = pd.read_csv("data/omim_chn/OMIM_disease.txt", sep="\t", dtype=str).fillna("")

    node_list = []
    edge_list = []

    for index, row in df_omim.iterrows():
        omim_id = row["OMIM编码"]
        omim_name = row["英文名"]
        omim_name_chn = row["中文译名"]

        if "omim_{}".format(omim_id) not in node_set:
            node_set.append("omim_{}".format(omim_id))

            omim_node = {
                "label": ["OMIM"],
                "node_ID": "OMIM_id",
                "property": {
                    "OMIM_id": omim_id,
                    "display": omim_id,
                    "OMIM_name": omim_name,
                    "OMIM_name_chn": omim_name_chn
                }
            }
            node_list.append(omim_node)


    df_chpo = pd.read_csv("data/omim_chn/CHPO.txt", sep="\t", dtype=str).fillna("")

    for index, row in df_chpo.iterrows():
        hpo_id = row["HPO编号"]
        hpo_name = row["名称(英文)"]
        hpo_name_chn = row["名称(中文)"]
        hpo_definition = row["定义(英文)"]
        hpo_definition_chn = row["定义(中文)"]
        classifications = row["主分类(中文)"]

        if "hpo_{}".format(hpo_id) not in node_set:
            node_set.append("hpo_{}".format(hpo_id))

            hpo_node = {
                "label": ["HPO"],
                "node_ID": "HPO_id",
                "property": {
                    "HPO_id": hpo_id,
                    "display": hpo_id,
                    "HPO_name": hpo_name,
                    "HPO_name_chn": hpo_name_chn,
                    "HPO_definition": hpo_definition,
                    "HPO_definition_chn": hpo_definition_chn,
                    "HPO_classifications": classifications
                }
            }
            node_list.append(hpo_node)

    df_rel = pd.read_csv("data/omim_chn/omim_gene.txt", sep="\t", dtype=str).fillna("")

    for index, row in df_rel.iterrows():
        omim_id = row["diseaseId"]
        gene_name = row["gene-symbol"]
        hpo_id = row["HPO-ID"]

        if "{}_{}".format(omim_id, hpo_id) not in edge_set:
            edge_set.append("{}_{}".format(omim_id, hpo_id))
            omim_hpo_edge = {
                "start_node": {
                    "label": ["OMIM"],
                    "node_ID": "OMIM_id",
                    "property": {
                        "OMIM_id": omim_id
                    }
                },
                "end_node": {
                    "label": ["HPO"],
                    "node_ID": "HPO_id",
                    "property": {
                        "HPO_id": hpo_id,
                    }
                },
                "edge": {
                    "label": "has_phenotype",
                    "property": {}
                }
            }
            edge_list.append(omim_hpo_edge)

        if "{}_{}".format(omim_id, gene_name) not in edge_set:
            edge_set.append("{}_{}".format(omim_id, gene_name))
            omim_gene_edge = {
                "start_node": {
                    "label": ['OMIM'],
                    "node_ID": "OMIM_id",
                    "property": {
                        "OMIM_id": omim_id
                    }
                },
                "end_node": {
                    "label": ["gene"],
                    "node_ID": "gene_name",
                    "property": {
                        "gene_name": gene_name
                    }
                },
                "edge": {
                    "label": "omim_gene_influence"
                }
            }
            edge_list.append(omim_gene_edge)

        if "{}_{}".format(hpo_id, gene_name) not in edge_set:
            edge_set.append("{}_{}".format(hpo_id, gene_name))
            hpo_gene_edge = {
                "start_node": {
                    "label": ['HPO'],
                    "node_ID": "HPO_id",
                    "property": {
                        "HPO_id": hpo_id
                    }
                },
                "end_node": {
                    "label": ["gene"],
                    "node_ID": "gene_name",
                    "property": {
                        "gene_name": gene_name
                    }
                },
                "edge": {
                    "label": "hpo_gene_influence"
                }
            }
            edge_list.append(hpo_gene_edge)

    with open("json/hpo_omim_nodes.json", "w") as f:
        json.dump(node_list, f)

    with open("json/hpo_omim_edges.json", "w") as f:
        json.dump(edge_list, f)


if __name__ == "__main__":
    handle_omim_map()
    handle_gwas_association()
    handle_omim_chpo_rel()
