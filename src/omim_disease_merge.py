import pandas as pd
import os
import requests
from tqdm import tqdm
from random import randint
import hashlib
import time
import json
from collections import defaultdict
import re
import Levenshtein


app_id = "20220110001051924"
secret = "Lz82JXgvz2Sc5Xk61ou3"

def translate_list(trans_list, output_path1, output_path2, fail_path):
    base_url = """http://api.fanyi.baidu.com/api/trans/vip/translate?q={}&from=en&to=zh&appid={}&salt={}&sign={}"""

    try:
        with open(output_path1, "r", encoding="utf-8") as f:
            translate_dict = json.load(f)
    except:
        translate_dict = {}

    try:
        df_review = pd.read_csv(output_path2, sep="\t", dtype=str).fillna("")
        for index, row in df_review.iterrows():
            translate_dict[row["eng"]] = row["chn"]
    except Exception as e:
        print("skip: {}".format(e))

    fail_list = []
    for index, x in enumerate(tqdm(trans_list)):
        trans_l = []
        for tl in x.split("\n"):
            if tl not in translate_dict.keys():
                trans_l.append(tl)

        trans_l = list(filter(lambda x: x != "", trans_l))
        if len(trans_l) == 0:
            continue

        x = "\n".join(trans_l)

        status = 400
        count = 0 # retry 3 times
        while status != 200 and count < 2:
            count += 1
            rand_str = str(randint(1000, 9999))
            ori_translate_str = app_id + x + rand_str + secret
            hl = hashlib.md5()
            hl.update(ori_translate_str.encode(encoding='utf-8'))
            translate_str = hl.hexdigest()

            try:
                result = requests.get(base_url.format(x, app_id, rand_str, translate_str), timeout=10)
            except:
                fail_list.append(x)
                status = 400
                time.sleep(1)
                continue

            status = result.status_code
            if status == 200:
                try:
                    json_dict = json.loads(result.text)
                    for y in json_dict["trans_result"]:
                        translate_dict[y["src"]] = y["dst"]
                except:
                    fail_list.append(x)
                    status = 400
            time.sleep(1)

        if index != 0 and index % 20 == 0:
            with open(output_path1, "w", encoding="utf-8") as f:
                json.dump(translate_dict, f)

            with open(fail_path, "w", encoding="utf-8") as f:
                json.dump(list(set(fail_list)), f)

    with open(output_path1, "w", encoding="utf-8") as f:
        json.dump(translate_dict, f)

    with open(fail_path, "w", encoding="utf-8") as f:
        json.dump(list(set(fail_list)), f)



def omim_translate():
    # 给没有中文翻译的omim节点数据增加中文翻译，用于后面omim节点与disease节点的相似度匹配
    df_omim = pd.read_csv("output/pheno_omim.csv", dtype=str).fillna("")
    df_omim_trans = df_omim[(df_omim["OMIM_name_chn"] == "") & (df_omim["phenotype"] != "")]
    phenotype_list = [re.sub("[\{|\}|?]", "", x.split(",")[0]).strip() for x in df_omim_trans["phenotype"].values]
    pheno_mapping = dict(zip(df_omim_trans["phenotype"].values, phenotype_list))

    print(len(phenotype_list))
    path1 = "translate/omim_translate_dict.json"
    path2 = "translate/omim_fail_review.tsv"
    fail_path = "translate/omim_fail_list.json"
    translate_list(phenotype_list, path1, path2, fail_path)

    with open(path1, "r") as f:
        trans_dict = json.load(f)

    for index, row in df_omim.iterrows():
        if row["OMIM_name_chn"] == "" and row["phenotype"] != "":
            chn_str = trans_dict[pheno_mapping[row["phenotype"]]]
            row["OMIM_name_chn"] = chn_str
        else:
            continue

    df_omim.to_csv("output/pheno_omim_translate.csv", index=False)



def similarity(target_str, candidate_list):
    max_ratio = 0
    max_str = ""

    for cl in candidate_list:
        ratio = Levenshtein.ratio(target_str, cl)

        if target_str in cl or cl in target_str:
            ratio += 0.15

        if ratio > max_ratio:
            max_ratio = ratio
            max_str = cl
    return max_ratio, max_str



def od_merge():
    # 用于 omim节点以及disease节点之间的融合
    # 达到使用疾病名称-> omim id -> 研究位点的链路查找
    df_disease = pd.read_csv("D:/neo4j-community-4.3.1/csv_upload/clean_drug_graph.nodes.disease.csv", dtype=str).fillna("")
    df_omim = pd.read_csv("output/pheno_omim_translate.csv", dtype=str).fillna("")

    disease_name_list = list(df_disease["display"].values)
    omim_name_list = zip(
        list(df_omim["display"].values),
        list(df_omim["OMIM_name_chn"].values)
    )

    result_list = []
    # disease -> omim: 1 to multi
    for omim_id, om in omim_name_list:
        max_ratio, max_str = similarity(om, disease_name_list)
        if max_ratio >= 0.8:
            result_list.append([omim_id, om, max_str, max_ratio])

    df_rel = pd.DataFrame(
        result_list,
        columns=[":START_ID(phenotype_OMIM)", "OMIM_chn", ":END_ID(disease)", "max_ratio"]
    )
    df_rel[":TYPE"] = ["disease_OMIM_match"] * len(df_rel)

    df_rel = df_rel[[":START_ID(phenotype_OMIM)", ":END_ID(disease)", ":TYPE"]]
    df_rel.to_csv("output/disease_omim_edge.csv", index=False)


if __name__ == "__main__":
    # omim_translate()
    od_merge()

