import re
import pandas as pd
import json
from omim_disease_merge import translate_list

node_dict = {}
edge_dict = {}

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
    (pubmed)-[research_in_trait]->(trait)
    """
    df_gwas = pd.read_csv(
        "data/gwas/gwas_catalog_v1.0-associations_e105_r2021-12-21.tsv",
        sep="\t", dtype=str
    ).fillna("")

    node_list = []
    edge_list = []

    trait_list = set(df_gwas["DISEASE/TRAIT"].values)

    for index, row in df_gwas.iterrows():
        # for node
        pubmed_id = row["PUBMEDID"].replace("\"", "'").replace("?", "Unknown")
        pubmed_link = row["LINK"].replace("\"", "'").replace("?", "Unknown")
        journal = row["JOURNAL"].replace("\"", "'").replace("?", "Unknown")
        pubmed_study = row["STUDY"].replace("\"", "'").replace("?", "Unknown")
        sample_size = row["INITIAL SAMPLE SIZE"].replace("\"", "'").replace("?", "Unknown")
        date = row["DATE"].replace("\"", "'").replace("?", "Unknown")

        pubmed_node = {
            "label": ["pubmed"],
            "node_ID": "pubmed_id",
            "property": {
                "pubmed_id": pubmed_id,
                "display": pubmed_id,
                "pubmed_link": pubmed_link,
                "pubmed_study": pubmed_study,
                "journal": journal,
                "sample_size": sample_size,
                "date": date
            }
        }

        if "pubmed_{}".format(pubmed_id) not in node_dict.keys():
            node_list.append(pubmed_node)
            node_dict["pubmed_{}".format(pubmed_id)] = pubmed_node

        else:
            node_dict["pubmed_{}".format(pubmed_id)]["property"].update(pubmed_node["property"])

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

        if ";" in rsID:
            continue

        rsID_node = {
            "label": ["rsID"],
            "node_ID": "variant_name",
            "property": {
                "variant_name": rsID,
                "display": rsID,
                "type": "rsID"
            }
        }

        if "rsID_{}".format(rsID) not in node_dict.keys():
            node_list.append(rsID_node)
            node_dict["rsID_{}".format(rsID)] = rsID_node

        else:
            node_dict["rsID_{}".format(rsID)]["property"].update(rsID_node["property"])

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

        if "{}_{}".format(pubmed_id, rsID) not in edge_dict.keys():
            edge_list.append(rsID_relation_edge)
            edge_dict["{}_{}".format(pubmed_id, rsID)] = rsID_relation_edge
        else:
            edge_dict["{}_{}".format(pubmed_id, rsID)]["edge"]["property"].update(
                rsID_relation_edge["edge"]["property"])

        for gene_name in gene_names:
            gene_node = {
                "label": ["gene"],
                "node_ID": "gene_name",
                "property": {
                    "gene_name": gene_name,
                    "display": gene_name
                }
            }

            if "gene_{}".format(gene_name) not in node_dict.keys():
                node_list.append(gene_node)
                node_dict["gene_{}".format(gene_name)] = gene_node
            else:
                node_dict["gene_{}".format(gene_name)]["property"].update(gene_node["property"])

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

            if "{}_{}".format(pubmed_id, gene_name) not in edge_dict.keys():
                edge_list.append(gene_relation_edge)
                edge_dict["{}_{}".format(pubmed_id, gene_name)] = gene_relation_edge
            else:
                edge_dict["{}_{}".format(pubmed_id, gene_name)]["edge"]["property"].update(
                    gene_relation_edge["edge"]["property"])

    with open("json/gwas_nodes.json", "w") as f:
        json.dump(node_list, f)

    with open("json/gwas_edges.json", "w") as f:
        json.dump(edge_list, f)


pheno_omim_regex = re.compile("[\d]+ \([\d]+\)")
inheritance_regex = re.compile("(recessive|dominant|linked)")

def parse_pheno_omim(pheno_str):
    pheno_str = pheno_str.lower()
    pheno_omim_id = []
    inheritance = []
    for x in pheno_str.split(","):
        if pheno_omim_regex.findall(x):
            pheno_omim_id.append(x.strip())
        if inheritance_regex.findall(x.lower()):
            inheritance.append(x.strip())

    pheno_omim_id = list(set(pheno_omim_id))
    for poi in pheno_omim_id:
        pheno_str = pheno_str.replace(poi, "")

    inheritance = list(set(inheritance))
    for inh in inheritance:
        pheno_str = pheno_str.replace(inh, "")

    pheno_str = pheno_str.strip(" ,;?")
    return [", ".join(pheno_omim_id), ", ".join(inheritance), pheno_str]


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
        position_start = row["Genomic Position Start"]
        position_end = row["Genomic Position End"]
        cyto_location = row["Cyto Location"]
        gene_omim_id = "OMIM:{}".format(row["MIM Number"]) \
            if "OMIM:" not in row["MIM Number"] else row["MIM Number"] # gene omim
        phenotype_list = row["Phenotypes"].split(";")

        if "#" in chromosome:
            continue

        # 添加pheno_OMIM 节点
        for pheno in phenotype_list:
            pheno_result = parse_pheno_omim(pheno)
            p_omim_id = pheno_result[0]
            inheritance = pheno_result[1]

            if "(" in p_omim_id:
                p_omim_id = "OMIM:{}".format(p_omim_id.split("(")[0].strip())
            else:
                p_omim_id = ""

            if p_omim_id != "": # 最少一项不为空
                pheno_omim_node = {
                    "label": ["phenotype_OMIM"],
                    "node_ID": "OMIM_id",
                    "property": {
                        "OMIM_id": p_omim_id,
                        "display": p_omim_id,
                        "phenotype": pheno,
                        "inheritance": inheritance
                    }
                }

                if "omim_{}".format(p_omim_id) not in node_dict.keys():
                    node_list.append(pheno_omim_node)
                    node_dict["omim_{}".format(p_omim_id)] = pheno_omim_node
                else:
                    node_dict["omim_{}".format(p_omim_id)]["property"].update(pheno_omim_node["property"])

        # gene omim 和 gene 用同一节点
        gene_node = {
            "label": ["gene"],
            "node_ID": "gene_name",
            "property": {
                "gene_name": gene_name,
                "display": gene_name,
                "gene_name_detail": gene_name_detail,
                "chromosome": chromosome,
                "position_start": position_start,
                "position_end": position_end,
                "cyto_location": cyto_location,
                "OMIM_id": gene_omim_id
            }
        }

        if "gene_{}".format(gene_name) not in node_dict.keys():
            node_dict["gene_{}".format(gene_name)] = gene_node
            node_list.append(gene_node)
        else:
            node_dict["gene_{}".format(gene_name)]["property"].update(gene_node["property"])

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

        omim_node = {
            "label": ["phenotype_OMIM"],
            "node_ID": "OMIM_id",
            "property": {
                "OMIM_id": omim_id,
                "display": omim_id,
                "OMIM_name": omim_name,
                "OMIM_name_chn": omim_name_chn
            }
        }

        if "omim_{}".format(omim_id) not in node_dict.keys():
            node_dict["omim_{}".format(omim_id)] = omim_node
            node_list.append(omim_node)
        else:
            node_dict["omim_{}".format(omim_id)]["property"].update(omim_node["property"])

    df_chpo = pd.read_csv("data/omim_chn/CHPO.txt", sep="\t", dtype=str).fillna("")

    for index, row in df_chpo.iterrows():
        hpo_id = row["HPO编号"]
        hpo_name = row["名称(英文)"]
        hpo_name_chn = row["名称(中文)"]
        hpo_definition = row["定义(英文)"]
        hpo_definition_chn = row["定义(中文)"]
        classifications = row["主分类(中文)"]

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

        if "hpo_{}".format(hpo_id) not in node_dict.keys():
            node_dict["hpo_{}".format(hpo_id)] = hpo_node
            node_list.append(hpo_node)
        else:
            node_dict["hpo_{}".format(hpo_id)]["property"].update(hpo_node["property"])

    df_rel = pd.read_csv("data/omim_chn/OMIM_gene.txt", sep="\t", dtype=str).fillna("")

    for index, row in df_rel.iterrows():
        omim_id = row["diseaseId"]
        gene_name = row["gene-symbol"]
        hpo_id = row["HPO-ID"]

        omim_hpo_edge = {
            "start_node": {
                "label": ["phenotype_OMIM"],
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

        if "{}_{}".format(omim_id, hpo_id) not in edge_dict.keys():
            edge_dict["{}_{}".format(omim_id, hpo_id)] = omim_hpo_edge
            edge_list.append(omim_hpo_edge)
        else:
            edge_dict["{}_{}".format(omim_id, hpo_id)]["edge"]["property"].update(omim_hpo_edge["edge"]["property"])

        omim_gene_edge = {
            "start_node": {
                "label": ['phenotype_OMIM'],
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
                "label": "omim_gene_influence",
                "property": {}
            }
        }

        if "{}_{}".format(omim_id, gene_name) not in edge_dict.keys():
            edge_dict["{}_{}".format(omim_id, gene_name)] = omim_gene_edge
            edge_list.append(omim_gene_edge)
        else:
            edge_dict["{}_{}".format(omim_id, gene_name)]["edge"]["property"].update(omim_gene_edge["edge"]["property"])

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
                "label": "hpo_gene_influence",
                "property": {}
            }
        }
        if "{}_{}".format(hpo_id, gene_name) not in edge_dict.keys():
            edge_dict["{}_{}".format(hpo_id, gene_name)] = hpo_gene_edge
            edge_list.append(hpo_gene_edge)
        else:
            edge_dict["{}_{}".format(hpo_id, gene_name)]["edge"]["property"].update(hpo_gene_edge["edge"]["property"])

    with open("json/hpo_omim_nodes.json", "w") as f:
        json.dump(node_list, f)

    with open("json/hpo_omim_edges.json", "w") as f:
        json.dump(edge_list, f)


def dump_data():
    with open("json/omim_node_dict.json", "w") as f:
        json.dump(node_dict, f)

    with open("json/omim_edge_dict.json", "w") as f:
        json.dump(edge_dict, f)


def trait_translate():
    df_gwas = pd.read_csv(
        "data/gwas/gwas_catalog_v1.0-associations_e105_r2021-12-21.tsv",
        sep="\t", dtype=str
    ).fillna("")

    trait_list = sorted(set(df_gwas["DISEASE/TRAIT"].values))
    trait_clean_list = [re.sub(r"[&\'+-]", " ", x).strip() for x in trait_list]
    trait_mapping = dict(zip(trait_list, trait_clean_list))

    batch_size = 5

    translate_trait_list = []
    for i in range(int(len(trait_clean_list) / batch_size) + 1):
        translate_trait_list.append("\n".join(trait_clean_list[i * batch_size: (i + 1) * batch_size]))

    path1 = "translate/trait_translate_dict.json"
    path2 = "translate/trait_fail_review.tsv"
    fail_path = "translate/trait_fail_list.json"
    translate_list(translate_trait_list, path1, path2, fail_path)

    with open(path1, "r") as f:
        trans_dict = json.load(f)

    trait_chn_list = [trans_dict[trait_mapping[x]] for x in trait_list]

    df_trait = pd.DataFrame(zip(trait_list, trait_chn_list), columns=["trait_name:ID(trait)", "trait_name_chn"])
    df_trait = df_trait[df_trait["trait_name:ID(trait)"] != ""]
    df_trait[":LABEL"] = ["trait"] * len(df_trait)
    df_trait.to_csv("output/trait.csv", index=False)


    df_gwas = df_gwas[["PUBMEDID", "DISEASE/TRAIT"]]
    df_gwas[[":START_ID(pubmed)", ":END_ID(trait)"]] = df_gwas[["PUBMEDID", "DISEASE/TRAIT"]]
    df_gwas = df_gwas[[":START_ID(pubmed)", ":END_ID(trait)"]]

    df_gwas = df_gwas[
        (df_gwas[":START_ID(pubmed)"] != "") &
        (df_gwas[":END_ID(trait)"] != "")
        ]

    df_gwas = df_gwas.drop_duplicates()
    df_gwas[":TYPE"] = ["research_in_trait"] * len(df_gwas)
    df_gwas.to_csv("output/pubmed_trait_edge.csv", index=False)


if __name__ == "__main__":
    # handle_omim_map()
    # handle_omim_chpo_rel()
    # handle_gwas_association()
    # dump_data()
    trait_translate()
