import pandas as pd
import json
import re

omim_regex = re.compile("OMIM:[\d]+")
hpo_regex = re.compile("Human Phenotype Ontology:HP:[\d]+")

def extract_hpo_id(id_str):
    hpo_list = hpo_regex.findall(id_str)
    hpo_list = [x.split(":")[-1] for x in hpo_list]
    return hpo_list

def extract_omim_id(id_str):
    omim_list = omim_regex.findall(id_str)
    omim_list = [x.split(":")[-1] for x in omim_list]
    return omim_list


node_dict = {}
edge_dict = {}

def handle_summary():
    df_variant = pd.read_csv("data/clinvar/variant_summary.txt", sep="\t", dtype=str).fillna("")
    df_variant = df_variant[df_variant["Assembly"] =="GRCh38"]

    node_list = []
    edge_list = []

    for index, row in df_variant.iterrows():
        variant_type = row["Type"]
        nucleotide = row["Name"]
        gene_name = row["GeneSymbol"]
        clinical_significance_list = row["ClinicalSignificance"].split("/")
        rsID = "rs{}".format(row["RS# (dbSNP)"]) if row["RS# (dbSNP)"] not in ["", "-1"] else ""
        phenotype_ids = row["PhenotypeIDS"]
        phenotype_list = row["PhenotypeList"].split("|")
        chromosome = row["Chromosome"]
        review_status = row["ReviewStatus"]
        number_submitters = row["NumberSubmitters"]
        position = row["PositionVCF"]
        reference = row["ReferenceAlleleVCF"]
        alternate = row["AlternateAlleleVCF"]

        pheno_omim_list = extract_omim_id(phenotype_ids)
        hpo_list = extract_hpo_id(phenotype_ids)
        if position != "-1":
            location = "chr{}:{}:{}>{}".format(chromosome, position, reference, alternate)
        else:
            continue

        location_node = {
            "label": ["variant_location"],
            "node_ID": "location",
            "property": {
                "location": location,
                "display": location,
                "variant_type": variant_type,
                "reference_allele": reference,
                "alternate_allele": alternate,
                "nucleotide": nucleotide,
                "clinical_significance": ", ".join(clinical_significance_list),
                "phenotype": ", ".join(phenotype_list),
                "review_status": review_status,
                "number_submitters": number_submitters,
                "gene_name": gene_name
            }
        }
        if "location_{}".format(location) not in node_dict.keys():
            node_list.append(location_node)
            node_dict["location_{}".format(location)] = location_node
        else:
            node_dict["location_{}".format(location)]["property"].update(location_node["property"])

        if rsID != "":
            rsID_node = {
                "label": ["variant", "rsID"],
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


        # add edge HPO -> variant location
        for hpo in hpo_list:
            if hpo != "":
                hpo_location_edge = {
                    "start_node": {
                        "label": ["HPO"],
                        "node_ID": "HPO_id",
                        "property": {
                            "HPO_id": hpo
                        }
                    },
                    "end_node": {
                        "label": ["variant_location"],
                        "node_ID": "location",
                        "property": {
                            "location": location,
                        }
                    },
                    "edge": {
                        "label": "clinvar_variant_hpo_relation",
                        "property": {}
                    }
                }
                if "{}_{}".format(hpo, location) not in edge_dict.keys():
                    edge_dict["{}_{}".format(hpo, location)] = hpo_location_edge
                    edge_list.append(hpo_location_edge)
                else:
                    edge_dict["{}_{}".format(hpo, location)]["edge"]["property"].update(
                        hpo_location_edge["edge"]["property"])

        # add edge phenotype OMIM -> variant location
        for p_omim in pheno_omim_list:
            if p_omim != "":
                omim_location_edge = {
                    "start_node": {
                        "label": ["phenotype_OMIM"],
                        "node_ID": "OMIM_id",
                        "property": {
                            "OMIM_id": p_omim
                        }
                    },
                    "end_node": {
                        "label": ["variant_location"],
                        "node_ID": "location",
                        "property": {
                            "location": location,
                        }
                    },
                    "edge": {
                        "label": "clinvar_variant_omim_relation",
                        "property": {}
                    }
                }
                if "{}_{}".format(p_omim, location) not in edge_dict.keys():
                    edge_list.append(omim_location_edge)
                    edge_dict["{}_{}".format(p_omim, location)] = omim_location_edge
                else:
                    edge_dict["{}_{}".format(p_omim, location)]["edge"]["property"].update(
                        omim_location_edge["edge"]["property"])

        # add edge variant location -> rsID
        if rsID != "" and location != "":
            location_rsID_edge = {
                "start_node": {
                    "label": ["variant_location"],
                    "node_ID": "location",
                    "property": {
                        "location": location,
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
                    "label": "rsID_location_mapping",
                    "property": {}
                }
            }

            if "{}_{}".format(location, rsID) not in edge_dict.keys():
                edge_dict["{}_{}".format(location, rsID)] = location_rsID_edge
                edge_list.append(location_rsID_edge)
            else:
                edge_dict["{}_{}".format(location, rsID)]["edge"]["property"].update(
                    location_rsID_edge["edge"]["property"])

    with open("json/clinvar_nodes.json", "w") as f:
        json.dump(node_list, f)

    with open("json/clinvar_edges.json", "w") as f:
        json.dump(edge_list, f)


def dump_data():
    with open("json/clinvar_node_dict.json", "w") as f:
        json.dump(node_dict, f)

    with open("json/clinvar_edge_dict.json", "w") as f:
        json.dump(edge_dict, f)


if __name__ == "__main__":
    handle_summary()
    dump_data()