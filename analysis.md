# 个体特征遗传疾病知识图谱分析方法

目录：

[comment]: <> ([TOC])

- [个体特征遗传疾病知识图谱分析方法](#----------------)
  * [基于链路查询的分析方法](#-----------)
    + [查询与个体特征相关的前五个rsID及其详情](#-------------rsid----)
    + [查询与基因相关的遗传疾病，按照审核分数筛选变异位点](#-------------------------)
    + [查询与疾病相关的变异位点及表型](#---------------)
  * [基于图嵌入的分析方式](#----------)

## 基于链路查询的分析方法

### 查询与个体特征相关的前五个rsID及其详情

这里通过**个体特征<->pubmed<->rsID**的这条关系链路，找出影响个体特征的rsID，
并且通过研究得到的p_value_mlog值做降序排序筛选得到相关性最高的rsID

注：trait_name属性为个体特征节点原有属性，trait_name_chn是数据清洗过程中调用百度翻译API机翻获得的，可能存在释义偏差。

```
// 高原适应
// ".*<word>.*" 表示为模糊搜索
match (t:trait)-[:research_in_trait]-(pm:pubmed)
where t.trait_name_chn =~ ".*高原适应.*"
with t, pm
match (pm)-[rs_research:research_in_rsID]->(rs:rsID)
return properties(t), properties(pm), properties(rs_research), properties(rs)
order by rs_research.p_value_mlog desc limit 5
```

```
// 脱发
match (t:trait)-[:research_in_trait]-(pm:pubmed)
where t.trait_name_chn =~ ".*脱发.*"
with t, pm
match (pm)-[rs_research:research_in_rsID]->(rs:rsID)
return properties(t), properties(pm), properties(rs_research), properties(rs)
order by rs_research.p_value_mlog desc limit 5
```

```
// 与肥胖相关的rsID
match (t:trait)-[:research_in_trait]-(pm:pubmed)
where t.trait_name =~ "Obesity"
with t, pm
match (pm)-[rs_research:research_in_rsID]->(rs:rsID)
return properties(t), properties(pm), properties(rs_research), properties(rs)
order by rs_research.p_value_mlog desc limit 5
```

### 查询与基因相关的遗传疾病，按照审核分数筛选变异位点

通过 **gene<->变异位点<->rsID<->OMIM疾病<->PubMed**链路查询与基因相关得遗传疾病
筛选具有致病性的位点，以及审查评分为3，4的位点进行显示。

```
// 与CFTR相关得遗传疾病信息获取
match (ge:gene {display: "CFTR"})<-[:location_in_gene]-(loc:variant_location)
where loc.review_score in ["3", "4"] and loc.clinical_significance =~ "Pathogenic"
with ge, loc 
match (loc)<-[:clinvar_variant_omim_relation]-(om:OMIM_disease)
with ge, loc, om
match (loc)-[:rsID_location_mapping]-(rs:rsID)
with ge, loc, om, rs
match (loc)-[:location_in_pubmed]->(pub:pubmed)
return properties(ge), properties(loc), properties(om), properties(rs), properties(pub)
order by loc.review_score desc
```

### 查询与疾病相关的变异位点及表型

通过 **变异位点<->OMIM疾病<->HPO表型**链路进行查询

注：OMIM_disease节点中的OMIM_name为英文标准疾病名称，OMIM_name_chn为数据清洗过程中使用百度翻译API机翻获得，可能存在释义偏差。

```
// 鱼鳞病
match (omim:OMIM_disease)-[r:has_phenotype]->(hp:HPO)
where omim.OMIM_name_chn =~ ".*鱼鳞病.*"
with omim, hp
match (omim)-[:clinvar_variant_omim_relation]->(loc:variant_location)
where loc.review_score in ["3", "4"] and loc.clinical_significance =~ "Pathogenic"
with omim, loc, hp
match (loc)-[:rsID_location_mapping]->(rsID)
RETURN properties(omim), properties(loc), properties(rsID), properties(hp)
```

```
match (omim:OMIM_disease)-[r:has_phenotype]->(hp:HPO)
where omim.OMIM_name_chn =~ ".*黄斑变性.*"
with omim, hp
match (omim)-[:clinvar_variant_omim_relation]->(loc:variant_location)
where loc.review_score in ["1", "2", "3", "4"] and loc.clinical_significance =~ "Pathogenic"


with omim, loc, hp
match (loc)-[:rsID_location_mapping]->(rsID)
RETURN properties(omim), properties(loc), properties(rsID), properties(hp)
```

## 基于图嵌入的分析方式

知识图谱图嵌入分析是一种主流的图谱分析方法，通过对节点及边的向量化训练，给每个节点与边赋予自己的向量，
并且在几何空间中，距离相近的向量，意味这两个向量的相似度越高，也就意味者两个节点的相似度越高。

求向量化的主流做法是使用[DGL-KE](https://github.com/awslabs/dgl-ke) （Deep Graph Library for Knowledge Embedding）工具来训练图嵌入。

在生命科学知识图谱邻域中，目前已有一些基于图嵌入的研究成果，比如说：
- [DRKG](https://github.com/gnn4dr/DRKG) ，药物重定向知识图谱，
在建图之后，尝试了在药物<->适应症之间的相关性分析。固定covid-19作为适应症，遍历所有的药物向量计算相似度，查找最符合治疗covid-19的药物。
- 在浙大[药物与靶点相互作用的预测](https://www.nature.com/articles/s41467-021-27137-3) 知识图谱当中，同样以HetioNet作为源知识图谱，
固定药物，遍历所有的靶点向量与药物向量求相似度，找到最匹配的药物<->靶点关系对。

在我们的个体特征遗传疾病知识图谱当中，后续也可以基于图谱的关系对，
分析 **OMIM疾病<->基因变异**、**个体特征<->基因变异**、以及
**跨组学、跨图谱链路的（药物、基因变异、OMIM疾病、个体特征）** 的关联分析。

