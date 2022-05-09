import os
import pandas as pd
import json

def graph_merge_clean():
    file_folder = "D:/neo4j-community-4.3.1/import/"
    file_list = os.listdir(file_folder)

    node_file_list = list(filter(lambda x: ".nodes." in x, file_list))
    edge_file_list = list(filter(lambda x: ".relationships." in x, file_list))

    id_name_mapping = {
        ".chemical.": ["chemical_name", "chemical"],
        ".gene.": ["gene_name", "gene"],
        ".diplotype.": ["diplotype_name", "diplotype"],
        ".disease.": ["disease_name", "disease"],
        ".drug.": ["drug_name", "drug"],
        ".nmpa_drug.": ["drug_code", "nmpa_drug"],
        ".symptom.": ["symptom_name", "symptom"],
        ".haplotype.": ["variant_name", "haplotype"],
        ".rsID.": ["variant_name", "rsID"]
    }

    node_id_mapping = {}
    node_type_mapping = {}

    output_folder = "D:/neo4j-community-4.3.1/csv_upload/"
    for nf in node_file_list:
        id_column = id_name_mapping[list(filter(lambda x: x in nf, id_name_mapping.keys()))[0]]
        node_type = id_column[1]
        id_column = id_column[0]
        df_nf = pd.read_csv(os.path.join(file_folder, nf), dtype=str).fillna("")
        node_id_mapping.update(dict(zip(df_nf[":ID"].values, df_nf[id_column].values)))
        node_type_mapping.update(dict(zip(df_nf[":ID"].values, [node_type] * len(df_nf))))
        df_nf = df_nf.drop(':ID', axis=1)
        df_nf[["{}:ID({})".format(id_column, node_type)]] = df_nf[[id_column]]
        df_nf = df_nf.drop(id_column, axis=1)
        df_nf.to_csv(os.path.join(output_folder, "clean_{}".format(nf)), index=False)

    for ef in edge_file_list:
        df_ef = pd.read_csv(os.path.join(file_folder, ef), dtype=str).fillna("")
        start_list = [node_id_mapping.get(x, "") for x in df_ef[":START_ID"].values]
        start_type_list = [node_type_mapping.get(x, "") for x in df_ef[":START_ID"].values]
        df_ef[":START_ID"] = start_list
        df_ef["start_type"] = start_type_list
        end_list = [node_id_mapping.get(x, "") for x in df_ef[":END_ID"].values]
        end_type_list = [node_type_mapping.get(x, "") for x in df_ef[":END_ID"].values]
        df_ef[":END_ID"] = end_list
        df_ef["end_type"] = end_type_list

        df_ef = df_ef[
            (df_ef[":START_ID"] != "") & (df_ef[":END_ID"] != "") &
            (df_ef["start_type"] != "") & (df_ef["end_type"] != "")
        ]

        # 解决多节点关系匹配问题
        for i, contents in enumerate(df_ef.groupby(["start_type", "end_type"])):
            start_type, end_type = contents[0]
            _df = contents[1]
            _df[":START_ID({})".format(start_type)] = _df[":START_ID"]
            _df[":END_ID({})".format(end_type)] = _df[":END_ID"]
            _df = _df.drop([":START_ID", ":END_ID", "start_type", "end_type"], axis=1)
            _df.to_csv(os.path.join(output_folder, "clean_{}_{}".format(i, ef)), index=False)


def gene_merge():
    path1 = "output/gene.csv"
    path2 = "D:/neo4j-community-4.3.1/csv_upload/clean_drug_graph.nodes.gene.csv"
    df_1 = pd.read_csv(path1, dtype=str).fillna("")
    df_2 = pd.read_csv(path2, dtype=str).fillna("")
    cols = set(df_1.columns).intersection(set(df_2.columns))
    df_gene = pd.merge(df_1, df_2, on=list(cols), how='outer').fillna("")
    df_gene.to_csv("D:/neo4j-community-4.3.1/csv_upload/gene_merge.csv", index=False)


def rsid_merge():
    path1 = "output/rsID.csv"
    path2 = "D:/neo4j-community-4.3.1/csv_upload/clean_drug_graph.nodes.variant.rsID.csv"
    df_1 = pd.read_csv(path1, dtype=str).fillna("")
    df_2 = pd.read_csv(path2, dtype=str).fillna("")
    cols = set(df_1.columns).intersection(set(df_2.columns))
    df_rsID = pd.merge(df_1, df_2, on=list(cols), how='outer').fillna("")
    df_rsID.to_csv("D:/neo4j-community-4.3.1/csv_upload/rsID_merge.csv", index=False)


if __name__ == "__main__":
    graph_merge_clean()
    # gene_merge()
    # rsid_merge()
    pass
