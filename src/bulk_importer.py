import json
import pandas as pd

with open("json/omim_node_dict.json", "r") as f:
    omim_node_dict = json.load(f)

with open("json/omim_edge_dict.json", "r") as f:
    omim_edge_dict = json.load(f)

with open("json/clinvar_node_dict.json", "r") as f:
    clinvar_node_dict = json.load(f)

with open("json/clinvar_edge_dict.json", "r") as f:
    clinvar_edge_dict = json.load(f)


def gen_omim_node_csv():
    # phenotype_OMIM node, from omim
    # header: OMIM_id:ID(phenotype_OMIM),display,phenotype,inheritance
    omim_str = "OMIM_id:ID(phenotype_OMIM),display,OMIM_name,OMIM_name_chn,phenotype,inheritance\n"
    for key, node in omim_node_dict.items():
        if "phenotype_OMIM" in node["label"]:
            row_str = ""
            for col in ["OMIM_id", "display", "OMIM_name", "OMIM_name_chn", "phenotype", "inheritance"]:
                cur_property = node["property"].get(col, "").replace("\"", "\'")
                cur_property = "\"{}\"".format(cur_property) if "," in cur_property else cur_property
                row_str += cur_property + ","

            # 移除最后一个逗号
            omim_str += row_str[:-1] + "\n"

    with open("output/pheno_omim.csv", "w", encoding="utf-8") as f:
        f.write(omim_str)

    # test csv availability
    pd.read_csv("output/pheno_omim.csv")


def gen_hpo_node_csv():
    # HPO node, from hpo
    # header: HPO_id:ID(HPO),display,HPO_name,HPO_name_chn,HPO_definition,HPO_definition_chn,HPO_classifications
    hpo_str = "HPO_id:ID(HPO),display,HPO_name,HPO_name_chn,HPO_definition,HPO_definition_chn,HPO_classifications\n"
    for key, node in omim_node_dict.items():
        if "HPO" in node["label"]:
            row_str = ""
            for col in ["HPO_id", "display", "HPO_name", "HPO_name_chn",
                        "HPO_definition", "HPO_definition_chn", "HPO_classifications"]:
                cur_property = node["property"].get(col, "").replace("\"", "\'")
                cur_property = "\"{}\"".format(cur_property) if "," in cur_property else cur_property
                row_str += cur_property + ","

            # 移除最后一个逗号
            hpo_str += row_str[:-1] + "\n"

    with open("output/hpo.csv", "w", encoding="utf-8") as f:
        f.write(hpo_str)

    # test csv availability
    pd.read_csv("output/hpo.csv")


def gen_location_node_csv():
    # variant_location node, from clinvar
    # header: location:ID(variant_location),display,variant_type,reference_allele,alternate_allele,nucleotide,
    # clinical_significance,phenotype,review_status,number_submitters,gene_name
    location_str = "location:ID(variant_location),display,variant_type,reference_allele,alternate_allele,nucleotide,clinical_significance,phenotype,review_status,number_submitters,gene_name\n"
    for key, node in clinvar_node_dict.items():
        if "variant_location" in node["label"]:
            row_str= ""
            for col in [
                "location", "display", "variant_type", "reference_allele", "alternate_allele", "nucleotide",
                "clinical_significance", "phenotype", "review_status", "number_submitters", "gene_name"
            ]:
                cur_property = node["property"].get(col, "").replace("\"", "'")
                cur_property = "\"{}\"".format(cur_property) if "," in cur_property else cur_property
                row_str += cur_property + ","

            # 移除最后一个逗号
            location_str += row_str[:-1] + "\n"

    with open("output/variant_location.csv", "w", encoding="utf-8") as f:
        f.write(location_str)

    # test csv availability
    df_location = pd.read_csv("output/variant_location.csv", dtype=str).fillna("")
    df_location = df_location[df_location["location:ID(variant_location)"].str.len() < 512]
    df_location.to_csv("output/variant_location.csv", index=False)


def gen_rsid_node_csv():
    # rsID node, from clinvar
    # header: variant_name:ID(rsID),display,type
    rsid_str = "variant_name:ID(rsID),display,type\n"

    for key, node in clinvar_node_dict.items():
        if "rsID" in node["label"]:
            row_str = ""
            for col in ["variant_name", "display", "type"]:
                cur_property = node["property"].get(col, "").replace("\"", "'")
                cur_property = "\"{}\"".format(cur_property) if "," in cur_property else cur_property
                row_str += cur_property + ","

            # 移除最后一个逗号
            rsid_str += row_str[:-1] + "\n"

    for key, node in omim_node_dict.items():
        if "rsID" in node["label"]:
            row_str = ""
            for col in ["variant_name", "display", "type"]:
                cur_property = node["property"].get(col, "").replace("\"", "'")
                cur_property = "\"{}\"".format(cur_property) if "," in cur_property else cur_property
                row_str += cur_property + ","

            # 移除最后一个逗号
            rsid_str += row_str[:-1] + "\n"

    with open("output/rsID.csv", "w", encoding="utf-8") as f:
        f.write(rsid_str)

    # test csv availability
    df_rsid = pd.read_csv("output/rsID.csv", dtype=str).fillna("")
    df_rsid.drop_duplicates().to_csv("output/rsID.csv", index=False)


def gen_pubmed_node_csv():
    # pubmed node, from gwas
    # header: pubmed_id:ID(pubmed),display,pubmed_link,journal,sample_size,date
    pubmed_str = "pubmed_id:ID(pubmed),display,pubmed_link,journal,sample_size,date\n"
    for key, node in omim_node_dict.items():
        if "pubmed" in node["label"]:
            row_str = ""
            for col in ["pubmed_id", "display", "pubmed_link", "pubmed_study", "journal", "sample_size", "date"]:
                cur_property = node["property"].get(col, "").replace("\"", "'")
                cur_property = "\"{}\"".format(cur_property) if "," in cur_property else cur_property
                row_str += cur_property + ","

            # 移除最后一个逗号
            pubmed_str += row_str[:-1] + "\n"

    with open("output/pubmed.csv", "w", encoding="utf-8") as f:
        f.write(pubmed_str)

    # test csv availability
    pd.read_csv("output/pubmed.csv")


def gen_gene_node_csv():
    # gene node, from omim
    # header: gene_name:ID(gene),display,gene_name_detail,chromosome,position_start,position_end,cyto_location,OMIM_id
    gene_str = "gene_name:ID(gene),display,gene_name_detail,chromosome,position_start,position_end,cyto_location,OMIM_id\n"
    for key, node in omim_node_dict.items():
        if "gene" in node["label"]:
            row_str = ""
            for col in ["gene_name", "display", "gene_name_detail", "chromosome", "position_start",
                        "position_end", "cyto_location", "OMIM_id"]:
                cur_property = node["property"].get(col, "").replace("\"", "'")
                cur_property = "\"{}\"".format(cur_property) if "," in cur_property else cur_property
                row_str += cur_property + ","

            # 移除最后一个逗号
            gene_str += row_str[:-1] + "\n"

    with open("output/gene.csv", "w", encoding="utf-8") as f:
        f.write(gene_str)

    # test csv availability
    pd.read_csv("output/gene.csv")


def gen_omim_hpo_edge_csv():
    # (omim)-[has_phenotype]->(hpo), from omim
    # header: :START_ID(phenotype_OMIM),:END_ID(HPO)
    omim_hpo_str = ":START_ID(phenotype_OMIM),:END_ID(HPO)\n"
    for key, edge in omim_edge_dict.items():
        if "has_phenotype" in edge["edge"]["label"]:
            start_id = edge["start_node"]["property"]["OMIM_id"]
            end_id = edge["end_node"]["property"]["HPO_id"]
            # 节点存在再存储
            if "omim_{}".format(start_id) in omim_node_dict.keys() and \
                    "hpo_{}".format(end_id) in omim_node_dict.keys():
                row_str = "{},{}".format(start_id, end_id)
                omim_hpo_str += row_str + "\n"

    with open("output/omim_hpo_edge.csv", "w", encoding="utf-8") as f:
        f.write(omim_hpo_str)

    # test csv availability
    pd.read_csv("output/omim_hpo_edge.csv")


def gen_omim_location_edge_csv():
    # (phenotype_OMIM)-[clinvar_variant_omim_relation]-(variant_location), from clinvar
    # header: :START_ID(phenotype_OMIM),:END_ID(variant_location)
    # omim_location_str = ":START_ID(phenotype_OMIM),:END_ID(variant_location)\n"
    # for key, edge in clinvar_edge_dict.items():
    #     if "clinvar_variant_omim_relation" in edge["edge"]["label"]:
    #         start_id = edge["start_node"]["property"]["OMIM_id"]
    #         end_id = edge["end_node"]["property"]["location"]
    #         # 节点存在再存储
    #         if "omim_{}".format(start_id) in omim_node_dict.keys() and \
    #                 "location_{}".format(end_id) in clinvar_node_dict.keys():
    #             row_str = "{},{}".format(start_id, end_id)
    #             omim_location_str += row_str + "\n"
    #
    # with open("output/omim_location_edge.csv", "w", encoding="utf-8") as f:
    #     f.write(omim_location_str)

    # test csv availability
    df_location = pd.read_csv("output/omim_location_edge.csv")
    df_location = df_location[df_location[":END_ID(variant_location)"].str.len() < 512]
    df_location.to_csv("output/omim_location_edge.csv", index=False)


def gen_hpo_location_edge_csv():
    # (HPO)-[clinvar_variant_hpo_relation]-(variant_location), from clinvar
    # header: :START_ID(HPO),:END_ID(variant_location)
    # hpo_location_str = ":START_ID(HPO),:END_ID(variant_location)\n"
    # for key, edge in clinvar_edge_dict.items():
    #     if "clinvar_variant_hpo_relation" in edge["edge"]["label"]:
    #         start_id = edge["start_node"]["property"]["HPO_id"]
    #         end_id = edge["end_node"]["property"]["location"]
    #         # 节点存在再存储
    #         if "hpo_{}".format(start_id) in omim_node_dict.keys() and \
    #                 "location_{}".format(end_id) in clinvar_node_dict.keys():
    #             row_str = "{},{}".format(start_id, end_id)
    #             hpo_location_str += row_str + "\n"
    #
    # with open("output/hpo_location_edge.csv", "w", encoding="utf-8") as f:
    #     f.write(hpo_location_str)

    # test csv availability
    df_location = pd.read_csv("output/hpo_location_edge.csv")
    df_location = df_location[df_location[":END_ID(variant_location)"].str.len() < 512]
    df_location.to_csv("output/hpo_location_edge.csv", index=False)


def gen_location_rsid_edge_csv():
    # (variant_location)-[rsID_location_mapping]-(rsID), from clinvar
    # header: :START_ID(variant_location),:END_ID(rsID)
    location_rsid_str = ":START_ID(variant_location),:END_ID(rsID)\n"
    for key, edge in clinvar_edge_dict.items():
        if "rsID_location_mapping" in edge["edge"]["label"]:
            start_id = edge["start_node"]["property"]["location"]
            end_id = edge["end_node"]["property"]["variant_name"]
            # 节点存在再存储
            if "location_{}".format(start_id) in clinvar_node_dict.keys() and \
                    "rsID_{}".format(end_id) in clinvar_node_dict.keys():
                row_str = "{},{}".format(start_id, end_id)
                location_rsid_str += row_str + "\n"

    with open("output/location_rsID_edge.csv", "w", encoding="utf-8") as f:
        f.write(location_rsid_str)

    # test csv availability
    pd.read_csv("output/location_rsID_edge.csv")


def gen_pubmed_gene_edge_csv():
    # (pubmed)-[research_in_gene]-(gene), from gwas
    # header: :START_ID(pubmed),:END_ID(gene)
    pubmed_gene_str = ":START_ID(pubmed),:END_ID(gene)\n"
    for key, edge in omim_edge_dict.items():
        if "research_in_gene" in edge["edge"]["label"]:
            start_id = edge["start_node"]["property"]["pubmed_id"]
            end_id = edge["end_node"]["property"]["gene_name"]
            # 节点存在再存储
            if "pubmed_{}".format(start_id) in omim_node_dict.keys() and \
                    "gene_{}".format(end_id) in omim_node_dict.keys():
                row_str = "{},\"{}\"".format(start_id, end_id)
                pubmed_gene_str += row_str + "\n"

    with open("output/pubmed_gene_edge.csv", "w", encoding="utf-8") as f:
        f.write(pubmed_gene_str)

    # test csv availability
    pd.read_csv("output/pubmed_gene_edge.csv")


def gen_pubmed_rsid_edge_csv():
    # (pubmed)-[research_in_rsID]-(rsID), from gwas
    # header: :START_ID(pubmed),risk_allele,risk_allele_frequency,pubmed_study,p_value,p_value_mlog,:END_ID(rsID)
    pubmed_rsid_str = ":START_ID(pubmed),risk_allele,risk_allele_frequency,pubmed_study,p_value,p_value_mlog,:END_ID(rsID)\n"
    for key, edge in omim_edge_dict.items():
        if "research_in_rsID" in edge["edge"]["label"]:
            start_id = edge["start_node"]["property"]["pubmed_id"]
            end_id = edge["end_node"]["property"]["variant_name"]

            if ";" in end_id or "," in end_id:
                continue

            # 节点存在再存储
            if "pubmed_{}".format(start_id) in omim_node_dict.keys() and \
                    "rsID_{}".format(end_id) in omim_node_dict.keys():
                row_str = ""
                for col in ["risk_allele", "risk_allele_frequency",
                            "pubmed_study", "p_value", "p_value_mlog"]:
                    cur_property = edge["edge"]["property"].get(col, "").replace("\"", "'")
                    cur_property = "\"{}\"".format(cur_property) if "," in cur_property else cur_property
                    row_str += cur_property + ","

                # 移除row_str的最后一个逗号
                new_row_str = "{},{},\"{}\"".format(start_id, row_str[:-1], end_id)
                pubmed_rsid_str += new_row_str + "\n"

    with open("output/pubmed_rsid_edge.csv", "w", encoding="utf-8") as f:
        f.write(pubmed_rsid_str)

    # test csv availability
    pd.read_csv("output/pubmed_rsid_edge.csv")


def gen_omim_gene_edge_csv():
    # (phenotype_OMIM)-[omim_gene_influence]-(gene), from omim
    # header: :START_ID(phenotype_OMIM),:END_ID(gene)
    omim_gene_str = ":START_ID(phenotype_OMIM),:END_ID(gene)\n"
    for key, edge in omim_edge_dict.items():
        if "omim_gene_influence" in edge["edge"]["label"]:
            start_id = edge["start_node"]["property"]["OMIM_id"]
            end_id = edge["end_node"]["property"]["gene_name"]
            # 节点存在再存储
            if "omim_{}".format(start_id) in omim_node_dict.keys() and \
                    "gene_{}".format(end_id) in omim_node_dict.keys():
                row_str = "{},\"{}\"".format(start_id, end_id)
                omim_gene_str += row_str + "\n"

    with open("output/omim_gene_edge.csv", "w", encoding="utf-8") as f:
        f.write(omim_gene_str)

    # test csv availability
    pd.read_csv("output/omim_gene_edge.csv")


def gene_hpo_gene_edge_csv():
    # (HPO)-[hpo_gene_influence]-(gene), from omim
    # header: :START_ID(HPO),:END_ID(gene)
    hpo_gene_str = ":START_ID(HPO),:END_ID(gene)\n"
    for key, edge in omim_edge_dict.items():
        if "hpo_gene_influence" in edge["edge"]["label"]:
            start_id = edge["start_node"]["property"]["HPO_id"]
            end_id = edge["end_node"]["property"]["gene_name"]
            # 节点存在再存储
            if "hpo_{}".format(start_id) in omim_node_dict.keys() and \
                    "gene_{}".format(end_id) in omim_node_dict.keys():
                row_str = "{},\"{}\"".format(start_id, end_id)
                hpo_gene_str += row_str + "\n"

    with open("output/hpo_gene_edge.csv", "w", encoding="utf-8") as f:
        f.write(hpo_gene_str)

    # test csv availability
    pd.read_csv("output/hpo_gene_edge.csv")


if __name__ == "__main__":
    # gen_omim_node_csv()
    # gen_hpo_node_csv()
    # gen_location_node_csv()
    # gen_rsid_node_csv()
    # gen_pubmed_node_csv()
    # gen_gene_node_csv()

    # gen_omim_hpo_edge_csv()
    gen_omim_location_edge_csv()
    gen_hpo_location_edge_csv()
    # gen_location_rsid_edge_csv()
    # gen_pubmed_gene_edge_csv()
    # gen_pubmed_rsid_edge_csv()
    # gen_omim_gene_edge_csv()
    # gene_hpo_gene_edge_csv()
